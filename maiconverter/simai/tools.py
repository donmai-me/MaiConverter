import math
from typing import List, Union, Optional, Tuple
from fractions import Fraction
from multiprocessing import Pool, Event
import os

from ..event import NoteType
from .simainote import (
    TapNote,
    HoldNote,
    SlideNote,
    TouchTapNote,
    TouchHoldNote,
    BPM,
    slide_to_pattern_str,
)
from .simai_parser import parse_fragment

ABORT = None


def _lcm(a: int, b: int) -> int:
    return a * b // math.gcd(a, b)


def get_rest(
    current_measure: float,
    next_measure: float,
    after_next_measure: Optional[float] = None,
    current_divisor: Optional[int] = None,
    max_den: int = 1000,
) -> Tuple[int, int, int]:
    # Finds the amount of rest needed to get to the next measure
    # Returns a tuple (whole, divisor, amount)
    if next_measure < current_measure:
        raise ValueError("Current measure is greater than next.")
    if next_measure == current_measure:
        if current_divisor is None:
            return 0, 4, 0

        return 0, current_divisor, 0

    difference = math.modf(next_measure - current_measure)
    difference_frac = Fraction(difference[0]).limit_denominator(max_den)

    if current_divisor is not None:
        _lcm_divisor = _lcm(current_divisor, difference_frac.denominator)
        if _lcm_divisor == current_divisor and next_measure - current_measure < 1:
            divisor = current_divisor
            whole = 0
            amount = int(
                difference[1] * divisor
                + difference_frac.numerator * (divisor / difference_frac.denominator)
            )
            return whole, divisor, amount

    if after_next_measure is not None:
        if next_measure > after_next_measure:
            raise ValueError("After next measure is greater than next measure")

        difference_after = math.modf(after_next_measure - next_measure)
        difference_after_frac = Fraction(difference_after[0]).limit_denominator(max_den)
        _lcm_divisor_after = _lcm(
            difference_frac.denominator, difference_after_frac.denominator
        )
        if _lcm_divisor_after <= 64 and next_measure - current_measure < 1:
            divisor = _lcm_divisor_after
            whole = 0
            amount = int(
                difference[1] * divisor
                + difference_frac.numerator * (divisor / difference_frac.denominator)
            )
            return whole, divisor, amount

    whole = int(difference[1])
    amount = difference_frac.numerator
    divisor = difference_frac.denominator
    return whole, divisor, amount


def get_measure_divisor(measures: List[float], max_den: int = 1000) -> Optional[int]:
    """Accepts a list of measures that all belong to the same whole measure.
    Example: [1.23, 1.5, 1.67, 1.89]
    Returns a divisor that would fit the list upto an upper bound.
    Otherwise, returns None.

    Args:
        measures: List of measure that has the same whole measure.
        max_den: The maximum denominator when making a fraction.

    Returns:
        Returns the smallest divisor that would fit all the measure in the list.
        Or None, if no divisor found."""
    if len(measures) == 0:
        return None

    differences = []
    previous_measure = int(measures[0])
    measures.sort()
    for measure in measures:
        differences.append(math.modf(measure - previous_measure)[0])
        previous_measure = measure

    current__lcm = 1
    for difference in differences:
        divisor = Fraction(difference).limit_denominator(max_den).denominator
        current__lcm = _lcm(current__lcm, divisor)
        if current__lcm > 64:
            return None

    return current__lcm


def handle_tap(tap: TapNote, slides: List[SlideNote], counter: int) -> Tuple[str, int]:
    result = ""
    note_type = tap.note_type
    if note_type in [NoteType.tap, NoteType.break_tap, NoteType.ex_tap]:
        # Regular, break, and ex tap note
        if note_type == NoteType.break_tap:
            modifier_string = "b"
        elif note_type == NoteType.ex_tap:
            modifier_string = "x"
        else:
            modifier_string = ""

        if counter > 0:
            result += "/"

        result += "{}{}".format(tap.position + 1, modifier_string)
    elif note_type in [NoteType.star, NoteType.break_star, NoteType.ex_star]:
        produced_slides = [slide for slide in slides if slide.position == tap.position]
        if len(produced_slides) > 0:
            return "", counter

        # Adding $ would make a star note with no slides
        if note_type == NoteType.break_star:
            modifier_string = "b$"
        elif note_type == NoteType.ex_star:
            modifier_string = "x$"
        else:
            modifier_string = "$"

        if counter > 0:
            result += "/"
        result += "{}{}".format(tap.position + 1, modifier_string)

    counter += 1
    return result, counter


def handle_hold(hold: HoldNote, counter: int, max_den: int = 1000) -> Tuple[str, int]:
    result = ""
    frac = Fraction(hold.duration).limit_denominator(max_den * 2)
    if hold.note_type == NoteType.ex_hold:
        modifier_string = "hx"
    else:
        modifier_string = "h"

    if counter > 0:
        result += "/"

    result += "{}{}[{}:{}]".format(
        hold.position + 1, modifier_string, frac.denominator, frac.numerator
    )

    counter += 1
    return result, counter


def handle_touch_tap(touch: TouchTapNote, counter: int) -> Tuple[str, int]:
    result = ""
    if touch.is_firework:
        modifier_string = "f"
    else:
        modifier_string = ""

    if counter > 0:
        result += "/"

    result += "{}{}{}".format(touch.region, touch.position + 1, modifier_string)

    counter += 1
    return result, counter


def handle_touch_hold(
    touch: TouchHoldNote, counter: int, max_den: int = 1000
) -> Tuple[str, int]:
    result = ""
    frac = Fraction(touch.duration).limit_denominator(max_den * 2)
    if touch.is_firework:
        modifier_string = "hf"
    else:
        modifier_string = "h"

    if counter > 0:
        result += "/"

    result += "{}{}[{}:{}]".format(
        touch.region, modifier_string, frac.denominator, frac.numerator
    )

    counter += 1
    return result, counter


def handle_slide(
    slide: SlideNote,
    taps: List[TapNote],
    positions: List[int],
    bpm: float,
    counter: int,
    max_den: int = 1000,
) -> Tuple[str, int]:
    result = ""
    stars = [star for star in taps if star.position == slide.position]
    if counter > 0 and slide.position not in positions:
        result += "/"

    if slide.position not in positions:
        if len(stars) == 0:
            # No star
            modifier_string = "?"
        elif stars[0].note_type == NoteType.break_star:
            modifier_string = "b"
        elif stars[0].note_type == NoteType.ex_star:
            # Ex star
            modifier_string = "x"
        else:
            modifier_string = ""
    else:
        # Regular star
        modifier_string = ""

    if slide.position in positions:
        start_position = "*"
    else:
        start_position = str(slide.position + 1)

    pattern = slide_to_pattern_str(slide)
    if slide.delay != 0.25:
        if slide.delay > 0.0025:
            scale = 0.25 / slide.delay
        else:
            # There are no instant slides in Simai due to its
            # "unique" way of representing slide delays
            # So we just make a very fast slide
            scale = 100

        equivalent_bpm = round(bpm * scale * 10000.0) / 10000.0
        equivalent_duration = slide.duration * scale
        frac = Fraction(equivalent_duration).limit_denominator(max_den * 10)
        result += "{}{}{}{}[{:.2f}#{}:{}]".format(
            start_position,
            modifier_string,
            pattern,
            slide.end_position + 1,
            equivalent_bpm,
            frac.denominator,
            frac.numerator,
        )
    else:
        frac = Fraction(slide.duration).limit_denominator(max_den * 10)
        result += "{}{}{}{}[{}:{}]".format(
            start_position,
            modifier_string,
            pattern,
            slide.end_position + 1,
            frac.denominator,
            frac.numerator,
        )

    if slide.position not in positions:
        positions.append(slide.position)

    counter += 1
    return result, counter


def convert_to_fragment(
    events: List[Union[TapNote, HoldNote, SlideNote, TouchTapNote, TouchHoldNote, BPM]],
    current_bpm: float,
    divisor: Optional[int] = None,
    max_den: int = 1000,
) -> str:
    # Accepts a list of events that starts at the same measure
    bpms = [bpm for bpm in events if isinstance(bpm, BPM)]
    tap_notes = [note for note in events if isinstance(note, TapNote)]
    hold_notes = [note for note in events if isinstance(note, HoldNote)]
    touch_tap_notes = [note for note in events if isinstance(note, TouchTapNote)]
    touch_hold_notes = [note for note in events if isinstance(note, TouchHoldNote)]
    slide_notes = [note for note in events if isinstance(note, SlideNote)]
    slide_notes.sort(
        key=lambda sn: (
            sn.position,
            sn.end_position,
            sn.pattern,
        )
    )

    fragment = ""
    counter = 0
    if len(bpms) != 0:
        fragment += "({})".format(bpms[0].bpm)

    if divisor is not None:
        fragment += f"{{{divisor}}}"

    for tap_note in tap_notes:
        result = handle_tap(tap_note, slide_notes, counter)
        fragment += result[0]
        counter = result[1]

    for hold_note in hold_notes:
        result = handle_hold(hold_note, counter, max_den=max_den)
        fragment += result[0]
        counter = result[1]

    for touch_tap_note in touch_tap_notes:
        result = handle_touch_tap(touch_tap_note, counter)
        fragment += result[0]
        counter = result[1]

    for touch_hold_note in touch_hold_notes:
        result = handle_touch_hold(touch_hold_note, counter, max_den=max_den)
        fragment += result[0]
        counter = result[1]

    positions: List[int] = []
    for slide_note in slide_notes:
        result = handle_slide(
            slide_note, tap_notes, positions, current_bpm, counter, max_den=max_den
        )
        fragment += result[0]
        counter = result[1]

    return fragment


def _parse_init(event):
    global ABORT
    ABORT = event


def _parse_helper(fragment: str) -> List:
    global ABORT
    # Return an empty list when ABORT is set or the fragments is empty or "E"
    if ABORT.is_set() or len(fragment) == 0 or fragment == "E":
        return []

    try:
        parsed = parse_fragment(fragment)
    except Exception as e:
        # Abort all jobs
        ABORT.set()
        raise RuntimeError(f"Error parsing fragment {fragment}") from e

    return parsed


def parallel_parse_fragments(fragments: List[str]) -> list:
    _abort = Event()

    cpu_count = os.cpu_count()
    if cpu_count is None:
        cpu_count = 1

    chunksize = 1 + len(fragments) // cpu_count

    # Stop jobs when abort is set
    def fragment_iter():
        for fragment in fragments:
            if not _abort.is_set():
                yield fragment

    with Pool(processes=cpu_count, initializer=_parse_init, initargs=(_abort,)) as pool:
        result = pool.map(_parse_helper, fragment_iter(), chunksize)

    return result
