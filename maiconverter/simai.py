from fractions import Fraction
import math
from typing import Optional, Tuple, List

from .note import SimaiNote, NoteType
from .event import Event, EventType
from .simai_lark_parser import simai_parse_fragment

# I hate the simai format can we use bmson for
# community-made charts instead

# For straightforward slide pattern conversion from simai to sdt/ma2.
# Use simai_pattern_to_int to cover all simai slide patterns.
simai_slide_dict = {
    "-": 1,
    "p": 4,
    "q": 5,
    "s": 6,
    "z": 7,
    "v": 8,
    "pp": 9,
    "qq": 10,
    "w": 13,
}

simai_slide_patterns = [
    "-",
    "^",
    ">",
    "<",
    "p",
    "q",
    "s",
    "z",
    "v",
    "pp",
    "qq",
    "V",
    "w",
]


class SimaiHoldNote(SimaiNote):
    def __init__(
        self, measure: float, position: int, duration: float, is_ex: bool = False
    ) -> None:
        if is_ex:
            super().__init__(measure, position, NoteType.ex_hold)
        else:
            super().__init__(measure, position, NoteType.hold)

        self.duration = duration


class SimaiTapNote(SimaiNote):
    def __init__(
        self,
        measure: float,
        position: int,
        is_break: bool = False,
        is_star: bool = False,
        is_ex: bool = False,
    ) -> None:
        if is_ex and is_star:
            super().__init__(measure, position, NoteType.ex_star)
        elif is_ex and not is_star:
            super().__init__(measure, position, NoteType.ex_tap)
        elif is_star and is_break:
            super().__init__(measure, position, NoteType.break_star)
        elif is_star and not is_break:
            super().__init__(measure, position, NoteType.star)
        elif is_break:
            super().__init__(measure, position, NoteType.break_tap)
        else:
            super().__init__(measure, position, NoteType.tap)


class SimaiSlideNote(SimaiNote):
    def __init__(
        self,
        measure: float,
        start_position: int,
        end_position: int,
        duration: float,
        pattern: str,
        delay: float = 0.25,
        reflect_position: Optional[int] = None,
    ) -> None:
        """Produces a simai slide note.

        Note: Simai slide durations does not include slide delay.

        Args:
            measure (float): Measure where the slide note begins.
            start_position (int): Button where slide begins. [0, 7]
            end_position (int): Button where slide ends. [0, 7]
            duration (float): Total duration, in measures, of
                the slide, including delay.
            pattern (str): Simai slide pattern. If 'V', then
                reflect_position should not be None.
            delay (float, optional): Time duration, in measures,
                from where slide appears and when it starts to move.
                Defaults to 0.25.
            reflect_position (Optional[int], optional): For 'V'
                patterns. Defaults to None.

        Raises:
            ValueError: When duration is not positive
                or when delay is negative
        """
        if duration <= 0:
            raise ValueError("Duration is not positive " + str(duration))
        elif delay < 0:
            raise ValueError("Delay is negative " + str(duration))
        elif not pattern in simai_slide_patterns:
            raise ValueError("Unknown slide pattern " + str(pattern))
        elif pattern == "V" and reflect_position is None:
            raise Exception("Slide pattern 'V' is given " + "without reflection point")

        super().__init__(measure, start_position, NoteType.complete_slide)
        self.duration = duration
        self.end_position = end_position
        self.pattern = pattern
        self.delay = delay
        self.reflect_position = reflect_position


class SimaiTouchTapNote(SimaiNote):
    def __init__(
        self, measure: float, position: int, zone: str, is_firework: bool = False
    ) -> None:
        measure_rounded = round(measure * 10000.0) / 10000.0

        super().__init__(measure_rounded, position, NoteType.touch_tap)
        self.is_firework = is_firework
        self.zone = zone


class SimaiTouchHoldNote(SimaiNote):
    def __init__(
        self,
        measure: float,
        position: int,
        zone: str,
        duration: float,
        is_firework: bool = False,
    ) -> None:
        measure_rounded = round(measure * 10000.0) / 10000.0
        duration_rounded = round(duration * 10000.0) / 10000.0

        super().__init__(measure_rounded, position, NoteType.touch_hold)
        self.is_firework = is_firework
        self.zone = zone
        self.duration = duration_rounded


class SimaiBPM(Event):
    def __init__(self, measure: float, bpm: float) -> None:
        if bpm <= 0:
            raise ValueError("BPM is not positive " + str(bpm))

        measure_rounded = round(measure * 10000.0) / 10000.0

        super().__init__(measure_rounded, EventType.bpm)
        self.bpm = bpm


def slide_distance(start_position: int, end_position: int, is_cw: bool) -> int:
    end = end_position
    start = start_position
    if is_cw:
        if start >= end:
            end += 8

        return end - start
    else:
        if start <= end:
            start += 8

        return start - end


def slide_is_cw(start_position: int, end_position: int) -> bool:
    # Handles slide cases where the direction is not specified
    # Returns True for clockwise and False for counterclockwise
    diff = abs(end_position - start_position)
    other_diff = abs(8 - diff)
    if diff == 4:
        raise ValueError("Can't choose direction for a 180 degree angle.")

    if (end_position > start_position and diff > other_diff) or (
        end_position < start_position and diff < other_diff
    ):
        return False
    else:
        return True


def simai_slide_to_pattern_str(slide_note: SimaiSlideNote) -> str:
    pattern = slide_note.pattern
    if pattern != "V":
        return pattern
    elif pattern == "V" and slide_note.reflect_position is None:
        raise Exception("Slide has 'V' pattern but no reflect position")
    else:
        return "V{}".format(slide_note.reflect_position + 1)


def simai_pattern_from_int(
    pattern: int, start_position: int, end_position: int
) -> (str, Optional[int]):
    top_list = [0, 1, 6, 7]
    inv_slide_dict = {v: k for k, v in simai_slide_dict.items()}
    dict_result = inv_slide_dict.get(pattern)
    if not dict_result is None:
        return (dict_result, None)
    elif pattern in [2, 3]:
        # Have I told you how much I hate the simai format?
        is_cw = True if pattern == 3 else False
        distance = slide_distance(start_position, end_position, is_cw)
        if distance <= 3:
            return ("^", None)
        elif (start_position in top_list and is_cw) or not (
            start_position in top_list or is_cw
        ):
            return (">", None)
        else:
            return ("<", None)
    elif pattern in [11, 12]:
        if pattern == 11:
            reflect_position = start_position - 2
            if reflect_position < 0:
                reflect_position += 8
        else:
            reflect_position = start_position + 2
            if reflect_position > 7:
                reflect_position -= 8

        return ("V", reflect_position)
    else:
        raise ValueError("Unknown pattern: " + str(pattern))


def simai_pattern_to_int(slide_note: SimaiSlideNote) -> Optional[int]:
    pattern = slide_note.pattern
    top_list = [0, 1, 6, 7]
    if not pattern in simai_slide_patterns:
        return None

    dict_result = simai_slide_dict.get(pattern)
    if not dict_result is None:
        return dict_result
    elif pattern == "^":
        is_cw = slide_is_cw(slide_note.position, slide_note.end_position)
        if is_cw:
            return 3
        else:
            return 2
    elif pattern == ">":
        is_top = True if slide_note.position in top_list else False
        if is_top:
            return 3
        else:
            return 2
    elif pattern == "<":
        is_top = True if slide_note.position in top_list else False
        if is_top:
            return 2
        else:
            return 3
    elif pattern == "V":
        is_cw = slide_is_cw(slide_note.position, slide_note.reflect_position)
        if is_cw:
            return 12
        else:
            return 11


def simai_get_rest(
    current_measure: float, next_measure: float
) -> Optional[Tuple[int, int, int]]:
    # Finds the amount of rest needed to get to the next measure
    # Returns a tuple (whole, divisor, amount)
    if next_measure < current_measure:
        raise ValueError("Current measure is greater than next.")
    elif next_measure == current_measure:
        return None
    else:
        difference = math.modf(next_measure - current_measure)
        whole = difference[1]
        decimal_fraction = Fraction(difference[0]).limit_denominator(1000)
        amount = decimal_fraction.numerator
        divisor = decimal_fraction.denominator
        return (int(whole), divisor, amount)


def simai_convert_to_fragment(
    events: List[Event], current_bpm: float, divisor: Optional[int] = None
) -> str:
    # Accepts a list of events that starts at the same measure

    if len(events) == 0:
        return ""

    bpms = [bpm for bpm in events if isinstance(bpm, SimaiBPM)]
    tap_notes = [note for note in events if isinstance(note, SimaiTapNote)]
    hold_notes = [note for note in events if isinstance(note, SimaiHoldNote)]
    touch_tap_notes = [note for note in events if isinstance(note, SimaiTouchTapNote)]
    touch_hold_notes = [note for note in events if isinstance(note, SimaiTouchHoldNote)]
    slide_notes = [note for note in events if isinstance(note, SimaiSlideNote)]
    slide_notes.sort(
        key=lambda slide_note: (
            slide_note.position,
            slide_note.end_position,
            slide_note.pattern,
        )
    )

    fragment = ""
    counter = 0
    if len(bpms) > 1:
        raise Exception("Multiple BPM defined at same measure " + str(bpms))
    elif len(bpms) == 1:
        fragment += "({})".format(bpms[0].bpm)

    if not divisor is None:
        fragment += "{" + str(divisor) + "}"

    for tap_note in tap_notes:
        note_type = tap_note.note_type
        if note_type in [NoteType.tap, NoteType.break_tap, NoteType.ex_tap]:
            # Regular, break, and ex tap note
            if note_type == NoteType.break_tap:
                modifier_string = "b"
            elif note_type == NoteType.ex_tap:
                modifier_string = "x"
            else:
                modifier_string = ""

            if counter > 0:
                fragment += "/"

            fragment += "{}{}".format(tap_note.position + 1, modifier_string)
        elif note_type in [NoteType.star, NoteType.break_star, NoteType.ex_star]:
            produced_slides = [
                slide for slide in slide_notes if slide.position == tap_note.position
            ]
            if len(produced_slides) > 0:
                continue
            else:
                # Adding $ would make a star note with no slides
                if note_type == NoteType.break_star:
                    modifier_string = "b$"
                elif note_type == NoteType.ex_star:
                    modifier_string = "x$"
                else:
                    modifier_string = "$"

                if counter > 0:
                    fragment += "/"
                fragment += "{}{}".format(tap_note.position + 1, modifier_string)

        counter += 1

    for hold_note in hold_notes:
        frac = Fraction(hold_note.duration).limit_denominator(1000)
        if hold_note.note_type == NoteType.ex_hold:
            modifier_string = "hx"
        else:
            modifier_string = "h"

        if counter > 0:
            fragment += "/"

        fragment += "{}{}[{}:{}]".format(
            hold_note.position + 1, modifier_string, frac.denominator, frac.numerator
        )

        counter += 1

    for touch_tap_note in touch_tap_notes:
        if touch_tap_note.is_firework:
            modifier_string = "f"
        else:
            modifier_string = ""

        if counter > 0:
            fragment += "/"

        fragment += "{}{}{}".format(
            touch_tap_note.zone, touch_tap_note.position + 1, modifier_string
        )

        counter += 1

    for touch_hold_note in touch_hold_notes:
        frac = Fraction(touch_hold_note.duration).limit_denominator(1000)
        if touch_hold_note.is_firework:
            modifier_string = "hf"
        else:
            modifier_string = "h"

        if counter > 0:
            fragment += "/"

        fragment += "{}{}[{}:{}]".format(
            touch_hold_note.zone, modifier_string, frac.denominator, frac.numerator
        )

        counter += 1

    positions = []
    for slide_note in slide_notes:
        star = [star for star in tap_notes if star.position == slide_note.position]
        if counter > 0 and not slide_note.position in positions:
            fragment += "/"

        if len(star) == 0 and not slide_note.position in positions:
            # No star
            modifier_string = "?"
        elif (
            star[0].note_type == NoteType.break_star
            and not slide_note.position in positions
        ):
            modifier_string = "b"
        elif (
            star[0].note_type == NoteType.ex_star
            and not slide_note.position in positions
        ):
            # Ex star
            modifier_string = "x"
        else:
            # Regular star
            modifier_string = ""

        if slide_note.position in positions:
            start_position = "*"
        else:
            start_position = str(slide_note.position + 1)

        pattern = simai_slide_to_pattern_str(slide_note)
        if slide_note.delay != 0.25:
            scale = 0.25 / slide_note.delay
            equivalent_bpm = round(current_bpm * scale * 10000.0) / 10000.0
            equivalent_duration = slide_note.duration * scale
            frac = Fraction(equivalent_duration).limit_denominator(1000)
            fragment += "{}{}{}{}[{}#{}:{}]".format(
                start_position,
                modifier_string,
                pattern,
                slide_note.end_position + 1,
                equivalent_bpm,
                frac.denominator,
                frac.numerator,
            )
        else:
            frac = Fraction(slide_note.duration).limit_denominator(1000)
            fragment += "{}{}{}{}[{}:{}]".format(
                start_position,
                modifier_string,
                pattern,
                slide_note.end_position + 1,
                frac.denominator,
                frac.numerator,
            )

        if not slide_note.position in positions:
            positions.append(slide_note.position)

        counter += 1

    return fragment


class SimaiChart:
    def __init__(self):
        self.notes = []
        self.bpms = []

    def add_tap(
        self,
        measure: float,
        position: int,
        is_break: bool = False,
        is_star: bool = False,
        is_ex: bool = False,
    ) -> None:
        tap_note = SimaiTapNote(measure, position, is_break, is_star, is_ex)
        self.notes.append(tap_note)

    def add_hold(
        self, measure: float, position: int, duration: float, is_ex: bool = False
    ) -> None:
        hold_note = SimaiHoldNote(measure, position, duration, is_ex)
        self.notes.append(hold_note)

    def add_slide(
        self,
        measure: float,
        start_position: int,
        end_position: int,
        duration: float,
        pattern: str,
        delay: float = 0.25,
        reflect_position: Optional[int] = None,
    ) -> None:
        slide_note = SimaiSlideNote(
            measure,
            start_position,
            end_position,
            duration,
            pattern,
            delay,
            reflect_position,
        )
        self.notes.append(slide_note)

    def add_touch_tap(
        self, measure: float, position: int, zone: str, is_firework: bool = False
    ) -> None:
        touch_tap_note = SimaiTouchTapNote(measure, position, zone, is_firework)
        self.notes.append(touch_tap_note)

    def add_touch_hold(
        self,
        measure: float,
        position: int,
        zone: str,
        duration: float,
        is_firework: bool = False,
    ) -> None:
        touch_hold_note = SimaiTouchHoldNote(
            measure, position, zone, duration, is_firework
        )
        self.notes.append(touch_hold_note)

    def set_bpm(self, measure: float, bpm: float) -> None:
        bpm_event = SimaiBPM(measure, bpm)
        self.bpms.append(bpm_event)

    def get_bpm(self, measure) -> float:
        bpm_measures = [bpm.measure for bpm in self.bpms]
        bpm_measures = list(set(bpm_measures))
        bpm_measures.sort()

        previous_measure = 0
        for bpm_measure in bpm_measures:
            if bpm_measure <= measure:
                previous_measure = bpm_measure
            else:
                break

        bpm_result = [bpm.bpm for bpm in self.bpms if bpm.measure == previous_measure]
        return bpm_result[0]

    def export(self) -> str:
        measures = [note.measure for note in self.notes]
        for bpm_event in self.bpms:
            measures.append(bpm_event.measure)

        measures = list(set(measures))
        measures.sort()

        previous_divisor = 4
        result = ""
        for (i, current_measure) in enumerate(measures):
            # Why doesn't Python have a safe list 'get' method
            next_measure = measures[i + 1] if i + 1 < len(measures) else None
            if next_measure is None:
                # We are at end so do nothing
                current_divisor = previous_divisor
                is_move_whole = False
                whole, post_div, post_amount = None, None, None
            else:
                # Determine if we'll move by whole notes or not
                (whole, post_div, post_amount) = simai_get_rest(
                    current_measure, next_measure
                )
                if whole > 0:
                    current_divisor = 1
                    is_move_whole = True
                else:
                    current_divisor = post_div
                    is_move_whole = False

            bpm = [bpm for bpm in self.bpms if bpm.measure == current_measure]
            notes = [note for note in self.notes if note.measure == current_measure]
            divisor = current_divisor if current_divisor != previous_divisor else None

            result += simai_convert_to_fragment(
                notes + bpm, self.get_bpm(current_measure), divisor
            )
            if is_move_whole:
                result += "," * whole

            if not post_div is None and post_div != current_divisor:
                result += "{" + str(post_div) + "}"
                result += "," * post_amount
                current_divisor = post_div
            elif not post_div is None and post_div == current_divisor:
                result += "," * post_amount

            previous_divisor = current_divisor

        result += ",E"
        return result


def simai_parse_chart(chart: str) -> SimaiChart:
    print("Parsing simai chart...")
    simai_chart = SimaiChart()
    current_bpm = 120
    current_divisor = 4
    current_measure = 1.0
    chart = "".join(chart.split())
    fragments = chart.split(",")
    for fragment in fragments:
        if fragment == "E":
            break
        elif fragment == "":
            pass
        else:
            star_positions = []
            events = simai_parse_fragment(fragment)
            for event in events:
                event_type = event["event_type"]
                if event_type == "bpm":
                    current_bpm = event["value"]
                    simai_chart.set_bpm(current_measure, current_bpm)
                elif event_type == "divisor":
                    current_divisor = event["value"]
                elif event_type == "tap":
                    is_break, is_ex, is_star = False, False, False
                    modifier = event["modifier"]
                    if not modifier is None:
                        if "b" in modifier:
                            is_break = True
                        elif "x" in modifier:
                            is_ex = True

                        if "$" in modifier:
                            is_star = True

                    simai_chart.add_tap(
                        current_measure, event["button"], is_break, is_star, is_ex
                    )
                elif event_type == "hold":
                    is_ex = False
                    modifier = event["modifier"]
                    if modifier == "x":
                        is_ex = True

                    simai_chart.add_hold(
                        current_measure, event["button"], event["duration"], is_ex
                    )
                elif event_type == "slide":
                    is_break, is_ex, is_tapless = False, False, False
                    modifier = event["modifier"]
                    if modifier == "b":
                        is_break = True
                    elif modifier == "x":
                        is_ex = True
                    elif modifier in ["?", "!", "$"]:
                        # Tapless slides
                        # ? means the slide has delay
                        # ! produces a slide with no path, just a moving star
                        # $ is a remnant of 2simai, it is equivalent to ?
                        is_tapless = True
                    elif not modifier is None:
                        raise ValueError("Unknown slide modifier" + str(modifier))

                    if not (is_tapless or event["start_button"] in star_positions):
                        simai_chart.add_tap(
                            current_measure,
                            event["start_button"],
                            is_break,
                            True,
                            is_ex,
                        )
                        star_positions.append(event["start_button"])

                    equivalent_bpm = event["equivalent_bpm"]
                    duration = event["duration"]
                    delay = 0.25
                    if not equivalent_bpm is None:
                        multiplier = current_bpm / equivalent_bpm
                        duration = multiplier * duration
                        delay = multiplier * delay

                    simai_chart.add_slide(
                        current_measure,
                        event["start_button"],
                        event["end_button"],
                        duration,
                        event["pattern"],
                        delay,
                        event["reflect_position"],
                    )
                elif event_type == "touch_tap":
                    is_firework = False
                    modifier = event["modifier"]
                    if modifier == "f":
                        is_firework = True
                    elif not modifier is None:
                        raise ValueError("Unknown touch modifier" + str(modifier))

                    zone = event["location"][0]
                    if len(event["location"]) > 1:
                        location = int(event["location"][1]) - 1
                    else:
                        location = 0

                    simai_chart.add_touch_tap(
                        current_measure, location, zone, is_firework
                    )

                elif event_type == "touch_hold":
                    is_firework = False
                    modifier = event["modifier"]
                    if modifier == "f":
                        is_firework = True
                    elif not modifier is None:
                        raise ValueError("Unknown touch modifier" + str(modifier))

                    zone = event["location"][0]
                    if len(event["location"]) > 1:
                        location = int(event["location"][1]) - 1
                    else:
                        location = 0

                    simai_chart.add_touch_hold(
                        current_measure, location, zone, event["duration"], is_firework
                    )
                else:
                    raise Exception("Unknown event type: " + str(event_type))

        current_measure += 1 / current_divisor

    print("Done!")
    return simai_chart
