from __future__ import annotations

import math
from typing import Optional, Tuple, List, Union
from lark import Lark

from .tools import (
    get_measure_divisor,
    convert_to_fragment,
    get_rest,
    parallel_parse_fragments,
)
from ..event import NoteType
from .simainote import TapNote, HoldNote, SlideNote, TouchTapNote, TouchHoldNote, BPM
from .simai_parser import SimaiTransformer

# I hate the simai format can we use bmson or stepmania chart format for
# community-made charts instead
from ..tool import measure_to_second, second_to_measure, offset_arg_to_measure


class SimaiChart:
    """A class that represents a simai chart. Contains notes and bpm
    information. Does not include information such as
    song name, chart difficulty, composer, chart maker, etc.
    It only contains enough information to build a working simai
    chart.

    Attributes:
        bpms: Contains bpm events of the chart.
        notes: Contains notes of the chart.
    """

    def __init__(self):
        self.notes: List[
            Union[TapNote, HoldNote, SlideNote, TouchTapNote, TouchHoldNote]
        ] = []
        self.bpms: List[BPM] = []
        self._divisor: Optional[float] = None
        self._measure = 1.0

    @classmethod
    def from_str(cls, chart_text: str, message: Optional[str] = None) -> SimaiChart:
        # TODO: Rewrite this
        if message is None:
            print("Parsing simai chart...", end="", flush=True)
        else:
            print(message, end="", flush=True)

        simai_chart = cls()
        chart_text = "".join(chart_text.split())
        try:
            events_list = parallel_parse_fragments(chart_text.split(","))
        except:
            print("ERROR")
            raise
        else:
            print("Done")

        for events in events_list:
            star_positions = []
            offset = 0
            for event in events:
                event_type = event["type"]
                if event_type == "bpm":
                    simai_chart.set_bpm(simai_chart._measure, event["value"])
                elif event_type == "divisor":
                    simai_chart._divisor = event["value"]
                elif event_type == "tap":
                    is_break, is_ex, is_star = False, False, False
                    modifier = event["modifier"]
                    if "b" in modifier:
                        is_break = True
                    if "x" in modifier:
                        is_ex = True
                    if "$" in modifier:
                        is_star = True

                    if "`" in modifier:
                        # Equivalent to one tick in ma2 with resolution of 384
                        offset += 0.0027
                    else:
                        offset = 0

                    simai_chart.add_tap(
                        measure=simai_chart._measure + offset,
                        position=event["button"],
                        is_break=is_break,
                        is_star=is_star,
                        is_ex=is_ex,
                    )
                elif event_type == "hold":
                    is_ex = False
                    modifier = event["modifier"]
                    if "x" in modifier:
                        is_ex = True

                    if "`" in modifier:
                        # Equivalent to one tick in ma2 with resolution of 384
                        offset += 0.0027
                    else:
                        offset = 0

                    simai_chart.add_hold(
                        measure=simai_chart._measure + offset,
                        position=event["button"],
                        duration=event["duration"],
                        is_ex=is_ex,
                    )
                elif event_type == "slide":
                    is_break, is_ex, is_tapless = False, False, False
                    modifier = event["modifier"]
                    if "b" in modifier:
                        is_break = True
                    if "x" in modifier:
                        is_ex = True
                    if any([a in modifier for a in "?!$"]):
                        # Tapless slides
                        # ? means the slide has no tap
                        # ! produces a tapless slide with no path, just a moving star
                        # $ is a remnant of 2simai, it is equivalent to ?
                        is_tapless = True

                    if "*" in modifier:
                        # Chained slides should have the same offset
                        pass
                    elif "`" in modifier:
                        # Equivalent to one tick in ma2 with resolution of 384
                        offset += 0.0027
                    else:
                        offset = 0

                    if not (is_tapless or event["start_button"] in star_positions):
                        simai_chart.add_tap(
                            measure=simai_chart._measure + offset,
                            position=event["start_button"],
                            is_break=is_break,
                            is_star=True,
                            is_ex=is_ex,
                        )
                        star_positions.append(event["start_button"])

                    equivalent_bpm = event["equivalent_bpm"]
                    duration = event["duration"]
                    delay = 0.25
                    if equivalent_bpm is not None:
                        multiplier = (
                            simai_chart.get_bpm(simai_chart._measure) / equivalent_bpm
                        )
                        duration = multiplier * duration
                        delay = multiplier * delay

                    simai_chart.add_slide(
                        measure=simai_chart._measure + offset,
                        start_position=event["start_button"],
                        end_position=event["end_button"],
                        duration=duration,
                        pattern=event["pattern"],
                        delay=delay,
                        reflect_position=event["reflect_position"],
                    )
                elif event_type == "touch_tap":
                    is_firework = False
                    modifier = event["modifier"]
                    if "f" in modifier:
                        is_firework = True

                    if "`" in modifier:
                        # Equivalent to one tick in ma2 with resolution of 384
                        offset += 0.0027
                    else:
                        offset = 0

                    simai_chart.add_touch_tap(
                        measure=simai_chart._measure + offset,
                        position=event["location"],
                        region=event["region"],
                        is_firework=is_firework,
                    )

                elif event_type == "touch_hold":
                    is_firework = False
                    modifier = event["modifier"]
                    if "f" in modifier:
                        is_firework = True

                    if "`" in modifier:
                        # Equivalent to one tick in ma2 with resolution of 384
                        offset += 0.0027
                    else:
                        offset = 0

                    simai_chart.add_touch_hold(
                        measure=simai_chart._measure + offset,
                        position=event["location"],
                        region=event["region"],
                        duration=event["duration"],
                        is_firework=is_firework,
                    )
                else:
                    raise Exception(f"Unknown event type: {event_type}")

            simai_chart._measure += 1 / simai_chart._divisor

        return simai_chart

    @classmethod
    def open(cls, file: str) -> SimaiChart:
        """Opens a text file containing only a Simai chart. Does NOT accept a regular Simai file which contains
        metadata and multiple charts. Use `parse_file` to parse a normal Simai file.

        Args:
              file: The path of the Simai chart file.

        Examples:
            Open a Simai chart file named "example.txt" at current directory.

            >>> simai = SimaiChart.open("./example.txt")
        """
        with open(file, "r") as f:
            chart = f.read()

        return cls.from_str(chart)

    def add_tap(
        self,
        measure: float,
        position: int,
        is_break: bool = False,
        is_star: bool = False,
        is_ex: bool = False,
    ) -> SimaiChart:
        """Adds a tap note to the list of notes.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the tap note happens.
            is_break: Whether a tap note is a break note.
            is_star: Whether a tap note is a star note.
            is_ex: Whether a tap note is an ex note.

        Examples:
            Add a regular tap note at measure 1, break tap note at
            measure 2, ex tap note at measure 2.5, star note at
            measure 3, and a break star note at measure 5. All at
            position 7.

            >>> simai = SimaiChart()
            >>> simai.add_tap(1, 7)
            >>> simai.add_tap(2, 7, is_break=True)
            >>> simai.add_tap(2.5, 7, is_ex=True)
            >>> simai.add_tap(3, 7, is_star=True)
            >>> simai.add_tap(5, 7, is_break=True, is_star=True)
        """
        tap_note = TapNote(
            measure=measure,
            position=position,
            is_break=is_break,
            is_star=is_star,
            is_ex=is_ex,
        )
        self.notes.append(tap_note)

        return self

    def del_tap(self, measure: float, position: int) -> SimaiChart:
        """Deletes a tap note from the list of notes.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the tap note happens.

        Examples:
            Remove tap note at measure 26.75 at button 4.
            >>> simai = SimaiChart()
            >>> simai.add_tap(26.5, 4)
            >>> simai.del_tap(26.75, 4)
        """
        tap_notes = [
            x
            for x in self.notes
            if isinstance(x, TapNote)
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == position
        ]
        for note in tap_notes:
            self.notes.remove(note)

        return self

    def add_hold(
        self,
        measure: float,
        position: int,
        duration: float,
        is_ex: bool = False,
    ) -> SimaiChart:
        """Adds a hold note to the list of notes.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the hold note happens.
            duration: Total time duration of the hold note.
            is_ex: Whether a hold note is an ex note.

        Examples:
            Add a regular hold note at button 2 at measure 1, with
            duration of 5 measures. And an ex hold note at button
            6 at measure 3, with duration of 0.5 measures.

            >>> simai = SimaiChart()
            >>> simai.add_hold(1, 2, 5)
            >>> simai.add_hold(3, 6, 0.5, is_ex=True)
        """
        hold_note = HoldNote(measure, position, duration, is_ex)
        self.notes.append(hold_note)

        return self

    def del_hold(self, measure: float, position: int) -> SimaiChart:
        """Deletes the matching hold note in the list of notes. If there are multiple
        matches, all matching notes are deleted. If there are no match, nothing happens.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the hold note happens.

        Examples:
            Add a regular hold note at button 0 at measure 3.25 with duration of 2 measures
            and delete it.

            >>> simai = SimaiChart()
            >>> simai.add_hold(3.25, 0, 2)
            >>> simai.del_hold(3.25, 0)
        """
        hold_notes = [
            x
            for x in self.notes
            if isinstance(x, HoldNote)
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == position
        ]
        for note in hold_notes:
            self.notes.remove(note)

        return self

    def add_slide(
        self,
        measure: float,
        start_position: int,
        end_position: int,
        duration: float,
        pattern: str,
        delay: float = 0.25,
        reflect_position: Optional[int] = None,
    ) -> SimaiChart:
        """Adds both a slide note to the list of notes.

        Args:
            measure: Time when the slide starts, in
                terms of measures.
            start_position: Button where the slide starts.
            end_position: Button where the slide ends.
            duration: Total duration of the slide, in terms of
                measures. Includes slide delay.
            pattern: The one or two character slide pattern used.
            delay: Duration from when the slide appears and when it
                starts to move, in terms of measures. Defaults to 0.25.
            reflect_position: The button where the 'V' slide will first go to.
                Optional, defaults to None.

        Examples:
            Add a '-' slide at measure 2.25 from button 1 to button 5 with
            duration of 1.5 measures

            >>> simai = SimaiChart()
            >>> simai.add_slide(2.25, 1, 5, 1.5, "-")
            >>> simai.add_slide(3, 2, 7, 0.5, "V", reflect_position=4)
        """
        slide_note = SlideNote(
            measure,
            start_position,
            end_position,
            duration,
            pattern,
            delay,
            reflect_position,
        )
        self.notes.append(slide_note)

        return self

    def del_slide(
        self,
        measure: float,
        start_position: int,
        end_position: int,
    ) -> SimaiChart:
        slide_notes = [
            x
            for x in self.notes
            if isinstance(x, SlideNote)
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == start_position
            and x.end_position == end_position
        ]
        for note in slide_notes:
            self.notes.remove(note)

        return self

    def add_touch_tap(
        self,
        measure: float,
        position: int,
        region: str,
        is_firework: bool = False,
    ) -> SimaiChart:
        touch_tap_note = TouchTapNote(measure, position, region, is_firework)
        self.notes.append(touch_tap_note)

        return self

    def del_touch_tap(
        self,
        measure: float,
        position: int,
        region: str,
    ) -> SimaiChart:
        touch_taps = [
            x
            for x in self.notes
            if isinstance(x, TouchTapNote)
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == position
            and x.region == region
        ]
        for note in touch_taps:
            self.notes.remove(note)

        return self

    def add_touch_hold(
        self,
        measure: float,
        position: int,
        region: str,
        duration: float,
        is_firework: bool = False,
    ) -> SimaiChart:
        touch_hold_note = TouchHoldNote(
            measure, position, region, duration, is_firework
        )
        self.notes.append(touch_hold_note)

        return self

    def del_touch_hold(
        self,
        measure: float,
        position: int,
        region: str,
    ) -> SimaiChart:
        touch_holds = [
            x
            for x in self.notes
            if isinstance(x, TouchHoldNote)
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == position
            and x.region == region
        ]
        for note in touch_holds:
            self.notes.remove(note)

        return self

    def set_bpm(self, measure: float, bpm: float) -> SimaiChart:
        """Sets the bpm at given measure.

        Note:
            If BPM event is already defined at given measure,
            the method will overwrite it.

        Args:
            measure: Time, in measures, where the bpm is defined.
            bpm: The tempo in beat per minutes.

        Examples:
            In a chart, the initial bpm is 180 then changes
            to 250 in measure 12.

            >>> simai = SimaiChart()
            >>> simai.set_bpm(0, 180)
            >>> simai.set_bpm(12, 250)
        """
        self.del_bpm(measure)

        bpm_event = BPM(measure, bpm)
        self.bpms.append(bpm_event)

        return self

    def get_bpm(self, measure: float) -> float:
        """Gets the bpm at given measure.

        Args:
            measure: Time, in measures.

        Returns:
            Returns the bpm defined at given measure or None.

        Raises:
            ValueError: When measure is negative, there are no BPMs
                defined, or there are no starting BPM defined.

        Examples:
            In a chart, the initial bpm is 180 then changes
            to 250 in measure 12.

            >>> simai = SimaiChart()
            >>> simai.get_bpm(0)
            180.0
            >>> simai.get_bpm(11.99)
            180.0
            >>> simai.get_bpm(12)
            250.0
        """
        if len(self.bpms) == 0:
            raise ValueError("No BPMs defined")
        if not any([0.0 <= x.measure <= 1.0 for x in self.bpms]):
            raise ValueError("No starting BPM defined")

        self.bpms.sort(key=lambda x: x.measure)
        previous_bpm = self.bpms[0].bpm
        for bpm in self.bpms:
            if math.isclose(measure, bpm.measure, abs_tol=0.0001):
                return bpm.bpm
            if bpm.measure > measure:
                break

            previous_bpm = bpm.bpm

        return previous_bpm

    def del_bpm(self, measure: float) -> SimaiChart:
        """Deletes the bpm at given measure.

        Note:
            If there are no BPM defined for that measure, nothing happens.

        Args:
            measure: Time, in measures, where the bpm is defined.

        Examples:
            Delete the BPM change defined at measure 24.

            >>> simai = SimaiChart()
            >>> simai.del_bpm(24)
        """
        bpms = [
            x for x in self.bpms if math.isclose(x.measure, measure, abs_tol=0.0001)
        ]
        for x in bpms:
            self.bpms.remove(x)

        return self

    def offset(self, offset: Union[float, str]) -> SimaiChart:
        offset = offset_arg_to_measure(offset, self.second_to_measure)

        for note in self.notes:
            note.measure = round(note.measure + offset, 4)

        for bpm in self.bpms:
            if 0 <= bpm.measure <= 1:
                continue

            bpm.measure = round(bpm.measure + offset, 4)

        return self

    def measure_to_second(self, measure: float) -> float:
        bpms = [(bpm.measure, bpm.bpm) for bpm in self.bpms]

        return measure_to_second(measure, bpms)

    def second_to_measure(self, seconds: float) -> float:
        bpms = [(bpm.measure, bpm.bpm) for bpm in self.bpms]
        measure = second_to_measure(seconds, bpms)

        return measure

    def export(self, max_den: int = 1000) -> str:
        # TODO: Rewrite this
        measures = [event.measure for event in self.notes + self.bpms]

        measures += [int(i) for i in measures]
        measures.append(0.0)

        measures = list(set(measures))
        last_whole_measure = max([int(measure) for measure in measures])
        measures.sort()

        # whole_divisors contains divisors that fit perfectly all notes in one measure.
        # It either contains an integer or None.
        whole_divisors: List[Union[int, None]] = []
        for whole_measure in range(last_whole_measure + 1):
            note_measures = [
                note_measure
                for note_measure in measures
                if int(note_measure) == whole_measure
            ]
            whole_divisors.append(get_measure_divisor(note_measures))

        # last_measure takes into account slide and hold notes' end measure
        last_measure = 0.0
        # measure_tick is our time-tracking variable. Used to know what measure
        # are we in-between rests ","
        measure_tick = 0.0
        # previous_divisor is used for comparing to current_divisor
        # to know if we should add a "{}" indicator
        previous_divisor: Optional[int] = None
        # previous_measure_int is used for comparing to current measure.
        # If we are in a new whole measure, add a new line and add the divisor.
        previous_measure_int = 0
        # Our resulting chart in text form. Assuming that string fits in memory
        result = ""
        for (i, current_measure) in enumerate(measures):
            bpm = [bpm for bpm in self.bpms if bpm.measure == current_measure]
            notes = [note for note in self.notes if note.measure == current_measure]

            hold_slides = [
                note
                for note in notes
                if note.note_type
                in [
                    NoteType.hold,
                    NoteType.ex_hold,
                    NoteType.touch_hold,
                    NoteType.complete_slide,
                ]
            ]
            for hold_slide in hold_slides:
                # Get hold and slide end measure and compare with last_measure
                if hold_slide.note_type == NoteType.complete_slide:
                    last_measure = max(
                        current_measure + hold_slide.delay + hold_slide.duration,
                        last_measure,
                    )
                else:
                    last_measure = max(
                        current_measure + hold_slide.duration, last_measure
                    )

            whole_divisor = whole_divisors[int(current_measure)]

            if i == len(measures) - 1:
                # We are at the end so let's check if there are any
                # active holds or slides
                if last_measure > current_measure:
                    (whole, current_divisor, rest_amount) = get_rest(
                        current_measure,
                        last_measure,
                        current_divisor=(
                            previous_divisor if whole_divisor is None else whole_divisor
                        ),
                        max_den=max_den,
                    )

                else:
                    # Nothing to do
                    current_divisor = (
                        previous_divisor if whole_divisor is None else whole_divisor
                    )
                    whole, rest_amount = 0, 0
            else:
                # Why doesn't Python have a safe list 'get' method
                next_measure: Optional[float] = (
                    measures[i + 1] if i + 1 < len(measures) else None
                )
                after_next_measure: Optional[float] = (
                    measures[i + 2] if i + 2 < len(measures) else None
                )
                (whole, current_divisor, rest_amount) = get_rest(
                    current_measure,
                    next_measure,
                    after_next_measure=after_next_measure,
                    current_divisor=(
                        previous_divisor if whole_divisor is None else whole_divisor
                    ),
                    max_den=max_den,
                )

            if (
                previous_divisor != current_divisor
                or int(measure_tick) > previous_measure_int
            ):
                result += "\n"
                result += convert_to_fragment(
                    notes + bpm,
                    self.get_bpm(current_measure + 1),
                    current_divisor,
                    max_den=max_den,
                )
                previous_divisor = current_divisor
                previous_measure_int = int(measure_tick)
            else:
                result += convert_to_fragment(
                    notes + bpm, self.get_bpm(current_measure + 1), max_den=max_den
                )

            measure_tick = current_measure

            for _ in range(rest_amount):
                result += ","
                measure_tick += 1 / current_divisor

            if whole > 0:
                if current_divisor != 1:
                    result += "{1}"
                    previous_divisor = 1

                for _ in range(whole):
                    result += ","
                    measure_tick += 1

            measure_tick = round(measure_tick * 10000) / 10000

        result += ",\nE\n"
        return result


def parse_file_str(
    file: str, lark_file: str = "simai.lark"
) -> Tuple[str, List[Tuple[int, SimaiChart]]]:
    parser = Lark.open(lark_file, rel_to=__file__, parser="lalr")

    dicts: List[dict] = SimaiTransformer().transform(parser.parse(file))

    title = ""
    charts: List[Tuple[int, SimaiChart]] = []
    for element in dicts:
        if element["type"] == "title":
            title: str = element["value"]
        elif element["type"] == "chart":
            num, chart = element["value"]
            simai_chart = SimaiChart.from_str(chart, message=f"Parsing chart #{num}...")
            charts.append((num, simai_chart))

    return title, charts


def parse_file(
    path: str,
    encoding: str = "UTF-8",
    lark_file: str = "simai.lark",
) -> Tuple[str, List[Tuple[int, SimaiChart]]]:
    with open(path, encoding=encoding) as f:
        simai = f.read()

    print(f"Parsing Simai file at {path}")
    try:
        result = parse_file_str(simai, lark_file=lark_file)
    except:
        print(f"Error parsing Simai file at {path}")
        raise
    else:
        print(f"Done parsing Simai file at {path}")
        return result
