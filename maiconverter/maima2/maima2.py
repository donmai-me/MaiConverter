from __future__ import annotations

import math
from collections import defaultdict
from typing import Tuple, List, Union

from .ma2note import (
    TapNote,
    HoldNote,
    SlideNote,
    TouchTapNote,
    TouchHoldNote,
    BPM,
    Meter,
    check_slide,
)
from .tools import parse_v1
from maiconverter.event import NoteType
from maiconverter.tool import (
    second_to_measure,
    measure_to_second,
    offset_arg_to_measure,
)

# Latest chart version
MA2_VERSION = "1.03.00"


class MaiMa2:
    """A class that represents a ma2 chart. Contains notes, bpm,
    and meter information. Does not include information such as
    song name, chart difficulty, composer, chart maker, etc.
    It only contains enough information to build a working ma2
    chart file.

    Attributes:
        fes_mode (bool): Whether a chart is an utage.
        bpms (list[BPM]): Contains bpm events of the chart.
        meters (dict[float, Meter]): Contains meter events
            of the chart
        notes (list[MaiNote]): Contains notes of the chart.
        version (str): Required for ma2's header.Copied from
            official ma2 chart files.
        notes_stat (dict[str, int]): Tracks total number of
            notes used by note type.
    """

    def __init__(
        self,
        fes_mode: bool = False,
        version: str = MA2_VERSION,
    ):
        """Produces a MaiMa2 object.

        Args:
            fes_mode: Whether a chart is an utage.
            version: Chart version.


        Examples:
            Create a regular ma2 object.

            >>> ma2 = MaiMa2()

            Create an utage ma2.

            >>> ma2 = MaiMa2(fes_mode=True)
        """
        self.fes_mode = fes_mode
        self.bpms: List[BPM] = []
        self.meters: List[Meter] = []
        self.notes: List[
            Union[TapNote, HoldNote, SlideNote, TouchTapNote, TouchHoldNote]
        ] = []
        self.notes_stat = {
            "TAP": 0,
            "BRK": 0,
            "XTP": 0,
            "HLD": 0,
            "XHO": 0,
            "STR": 0,
            "BST": 0,
            "XST": 0,
            "TTP": 0,
            "THO": 0,
            "SLD": 0,
        }

        # TODO: Remove these when the new Ma2 parser is finished
        self.version = ("0.00.00", version)
        self.resolution = 384

    @classmethod
    def open(cls, path: str, encoding: str = "utf-8") -> MaiMa2:
        ma2 = cls()
        with open(path, "r", encoding=encoding) as in_f:
            for line in in_f:
                if line in ["\n", "\r\n"]:
                    continue

                ma2.parse_line(line)

        return ma2

    def parse_line(self, line: str) -> MaiMa2:
        # Ma2 notes are tab-separated so we make a list called values that contains all the info
        values = line.rstrip().split("\t")
        line_type = values[0]
        if line_type == "VERSION":
            self.version = (values[1], values[2])
        elif line_type == "FES_MODE":
            self.fes_mode = values[1] == "1"
        elif self.version[1] in ["1.02.00", "1.03.00"]:
            parse_v1(self, values)
        else:
            raise ValueError(f"Unknown Ma2 version: {self.version}")

        return self

    def set_bpm(self, measure: float, bpm: float) -> MaiMa2:
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

            >>> ma2 = MaiMa2()
            >>> ma2.set_bpm(0, 180)
            >>> ma2.set_bpm(12, 250)
        """
        self.del_bpm(measure)
        self.bpms.append(BPM(measure, bpm))

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

            >>> ma2 = MaiMa2()
            >>> ma2.set_bpm(0.0, 180.0).set_bpm(12, 250)
            >>> ma2.get_bpm(0)
            180.0
            >>> ma2.get_bpm(11.99)
            180.0
            >>> ma2.get_bpm(12)
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

    def del_bpm(self, measure: float) -> MaiMa2:
        """Deletes the bpm at given measure.

        Note:
            If there are no BPM defined for that measure, nothing happens.

        Args:
            measure: Time, in measures, where the bpm is defined.

        Examples:
            Delete the BPM change defined at measure 24.

            >>> ma2 = MaiMa2()
            >>> ma2.del_bpm(24)
        """
        bpms = [
            x for x in self.bpms if math.isclose(x.measure, measure, abs_tol=0.0001)
        ]
        for x in bpms:
            self.bpms.remove(x)

        return self

    def set_meter(
        self,
        measure: float,
        meter_numerator: int,
        meter_denominator: int,
    ) -> MaiMa2:
        """Sets the meter signature at given measure.

        Note:
            If meter signature event is already defined
            at given measure, the method will overwrite it.

        Args:
            measure: Time, in measures, where the bpm is defined.
            meter_numerator: The upper numeral in a meter signature.
            meter_denominator: The lower numeral in a meter signature.

        Examples:
            In a chart, the initial meter is 4/4 then changes
            to 6/8 in measure 5.

            >>> ma2 = MaiMa2()
            >>> ma2.set_meter(0, 4, 4)
            >>> ma2.set_meter(5, 6, 8)
        """
        self.del_meter(measure)
        self.meters.append(Meter(measure, meter_numerator, meter_denominator))

        return self

    def get_meter(self, measure: float) -> Tuple[int, int]:
        """Gets the bpm at given measure.

        Args:
            measure: Time, in measures.

        Returns:
            Returns a tuple (numerator, denominator) defined at
            given measure or None.

        Examples:
            In a chart, the initial meter is 4/4 then changes
            to 6/8 in measure 12.

            >>> ma2.get_meter(0)
            (4, 4)
            >>> ma2.get_meter(11.99)
            (4, 4)
            >>> ma2.get_meter(12)
            (6, 8)
        """
        if len(self.meters) == 0:
            raise ValueError("No meters defined")

        self.meters.sort(key=lambda x: x.measure)
        previous_meter = self.meters[0]
        for meter in self.meters:
            if math.isclose(measure, meter.measure, abs_tol=0.0001):
                return meter.numerator, meter.denominator
            if meter.measure > measure:
                break

            previous_meter = meter

        return previous_meter.numerator, previous_meter.numerator

    def del_meter(self, measure: float) -> MaiMa2:
        meters = [
            x for x in self.meters if math.isclose(x.measure, measure, abs_tol=0.0001)
        ]
        for x in meters:
            self.meters.remove(x)

        return self

    def add_tap(
        self,
        measure: float,
        position: int,
        is_break: bool = False,
        is_star: bool = False,
        is_ex: bool = False,
    ) -> MaiMa2:
        """Adds a tap note to the list of notes.

        Used to add TAP, XTP, BRK, STR, or BST to the list of notes. Increments
        the total note type produced by 1.

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

            >>> ma2 = MaiMa2()
            >>> ma2.add_tap(1, 7)
            >>> ma2.add_tap(2, 7, is_break=True)
            >>> ma2.add_tap(2.5, 7, is_ex=True)
            >>> ma2.add_tap(3, 7, is_star=True)
            >>> ma2.add_tap(5, 7, is_break=True, is_star=True)
        """
        tap_note = TapNote(
            measure=measure,
            position=position,
            is_star=is_star,
            is_break=is_break,
            is_ex=is_ex,
        )

        if is_ex and is_star:
            self.notes_stat["XST"] += 1
        elif is_ex and not is_star:
            self.notes_stat["XTP"] += 1
        elif is_break and is_star and not is_ex:
            self.notes_stat["BST"] += 1
        elif is_break and not is_star and not is_ex:
            self.notes_stat["BRK"] += 1
        elif not is_break and is_star and not is_ex:
            self.notes_stat["STR"] += 1
        elif not is_break and not is_star and not is_ex:
            self.notes_stat["TAP"] += 1

        self.notes.append(tap_note)

        return self

    def del_tap(self, measure: float, position: int) -> MaiMa2:
        """Deletes a tap note from the list of notes.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the tap note happens.

        Examples:
            Create a break tap note at measure 26.75 at button 4. Then delete it.

            >>> ma2 = MaiMa2()
            >>> ma2.add_tap(26.75, 4, is_break=True)
            >>> ma2.del_tap(26.75, 4)
        """
        tap_notes = [
            x
            for x in self.notes
            if isinstance(x, TapNote)
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == position
        ]
        for note in tap_notes:
            is_ex = note.note_type in [NoteType.ex_tap, NoteType.ex_star]
            is_break = note.note_type in [NoteType.break_tap, NoteType.break_star]
            is_star = note.note_type in [
                NoteType.star,
                NoteType.ex_star,
                NoteType.break_star,
            ]
            self.notes.remove(note)
            if is_ex and is_star:
                self.notes_stat["XST"] -= 1
            elif is_ex and not is_star:
                self.notes_stat["XTP"] -= 1
            elif is_break and is_star and not is_ex:
                self.notes_stat["BST"] -= 1
            elif is_break and not is_star and not is_ex:
                self.notes_stat["BRK"] -= 1
            elif not is_break and is_star and not is_ex:
                self.notes_stat["STR"] -= 1
            elif not is_break and not is_star and not is_ex:
                self.notes_stat["TAP"] -= 1

        return self

    def add_hold(
        self,
        measure: float,
        position: int,
        duration: float,
        is_ex: bool = False,
    ) -> MaiMa2:
        """Adds a hold note to the list of notes.

        Used to add HLD or XHO to the list of notes. Increments the total
        note type produced by 1.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the hold note happens.
            duration: Total time duration of the hold note.
            is_ex: Whether a hold note is an ex note.

        Examples:
            Add a regular hold note at button 2 at measure 1, with
            duration of 5 measures. And an ex hold note at button
            6 at measure 3, with duration of 0.5 measures.

            >>> ma2 = MaiMa2()
            >>> ma2.add_hold(1, 2, 5)
            >>> ma2.add_hold(3, 6, 0.5, is_ex=True)
        """
        hold_note = HoldNote(measure, position, duration, is_ex)

        if is_ex:
            self.notes_stat["XHO"] += 1
        else:
            self.notes_stat["HLD"] += 1

        self.notes.append(hold_note)

        return self

    def del_hold(self, measure: float, position: int) -> MaiMa2:
        """Deletes the matching hold note in the list of notes. If there are multiple
        matches, all matching notes are deleted. If there are no match, nothing happens.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the hold note happens.

        Examples:
            Add a regular hold note at button 0 at measure 3.25 with duration of 2 measures
            and delete it.

            >>> ma2 = MaiMa2()
            >>> ma2.add_hold(3.25, 0, 2)
            >>> ma2.del_hold(3.25, 0)
        """
        hold_notes = [
            x
            for x in self.notes
            if isinstance(x, HoldNote)
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == position
        ]
        for note in hold_notes:
            is_ex = note.note_type == NoteType.ex_hold
            self.notes.remove(note)
            if is_ex:
                self.notes_stat["XHO"] -= 1
            else:
                self.notes_stat["HLD"] -= 1

        return self

    def add_slide(
        self,
        measure: float,
        start_position: int,
        end_position: int,
        duration: float,
        pattern: int,
        delay: float = 0.25,
        slide_check: bool = True,
    ) -> MaiMa2:
        """Adds a slide note to the list of notes.

        Used to add SI_, SCL, SCR, SUL, SUR, SSL, SSR, SV_, SXL, SXR,
        SLL, SLR, or SF_ to the list of notes. Increments the total
        slides produced by 1.

        Args:
            measure: Time when the note starts, in terms of measures.
            start_position: Starting button.
            end_position: Ending button.
            pattern: Numerical representation of the slide pattern.
            duration: Time duration of when the slide starts moving and
                      when it ends (delay is not included.) in terms of
                      measures.
            delay: Time duration of when the slide appears and when it
                   starts to move, in terms of measures.
            slide_check: When set to true, will check validity of slides.

        Examples:
            Add an SUL at measure 2.5 from button 1 to 5, with a duration
            of 0.5 measures and default delay.

            >>> ma2 = MaiMa2()
            >>> ma2.add_slide(2.5, 1, 5, 0.5, 5)
        """
        if slide_check:
            check_slide(pattern, start_position, end_position)

        slide_note = SlideNote(
            measure,
            start_position,
            end_position,
            pattern,
            duration,
            delay,
        )
        self.notes_stat["SLD"] += 1
        self.notes.append(slide_note)

        return self

    def del_slide(
        self,
        measure: float,
        start_position: int,
        end_position: int,
    ) -> MaiMa2:
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
            self.notes_stat["SLD"] -= 1

        return self

    def add_touch_tap(
        self,
        measure: float,
        position: int,
        region: str,
        is_firework: bool = False,
        size: str = "M1",
    ) -> MaiMa2:
        """Adds a touch tap note to the list of notes.

        Used to add TTP to the list of notes. Increments the total touch taps
        produced by 1.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Position in the region where the note happens.
            region: Touch region where the note happens.
            is_firework: Whether a touch tap note will produce
                         fireworks. Optional bool, defaults to False.
            size: Optional str. Defaults to "M1"

        Examples:
            Add a touch tap at measure 0.75 at B1 with fireworks.

            >>> ma2 = MaiMa2()
            >>> ma2.add_touch_tap(0.75, 1, "B", is_firework=True)
        """
        touch_tap = TouchTapNote(measure, position, region, is_firework, size)
        self.notes_stat["TTP"] += 1
        self.notes.append(touch_tap)

        return self

    def del_touch_tap(self, measure: float, position: int, region: str) -> MaiMa2:
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
            self.notes_stat["TTP"] -= 1

        return self

    def add_touch_hold(
        self,
        measure: float,
        position: int,
        region: str,
        duration: float,
        is_firework: bool = False,
        size: str = "M1",
    ) -> MaiMa2:
        """Adds a touch hold note to the list of notes.

        Used to add THO to the list of notes. Increments the total touch holds
        produced by 1.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Position in the region where the note happens.
            region: Touch region where the note happens.
            duration: Total time duration of the touch hold note.
            is_firework: Whether a touch hold note will produce
                         fireworks. Optional bool, defaults to False.
            size: Optional str. Defaults to "M1"

        Examples:
            Add a touch hold at measure 2 at C0 with duration of
            2 measures and produces fireworks.

            >>> ma2 = MaiMa2()
            >>> ma2.add_touch_hold(2, 0, "C", 2, is_firework=True)
        """
        touch_tap = TouchHoldNote(
            measure, position, region, duration, is_firework, size
        )
        self.notes_stat["THO"] += 1
        self.notes.append(touch_tap)

        return self

    def del_touch_hold(
        self,
        measure: float,
        position: int,
        region: str,
    ) -> MaiMa2:
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
            self.notes_stat["THO"] -= 1

        return self

    def offset(self, offset: Union[float, str]) -> MaiMa2:
        offset = offset_arg_to_measure(offset, self.second_to_measure)

        for note in self.notes:
            note.measure = round(note.measure + offset, 4)

        for bpm in self.bpms:
            if 0 <= bpm.measure <= 1:
                continue

            bpm.measure = round(bpm.measure + offset, 4)

        for meter in self.meters:
            if 0 <= meter.measure <= 1:
                continue

            meter.measure = round(meter.measure + offset, 4)

        return self

    def measure_to_second(self, measure: float) -> float:
        bpms = [(bpm.measure, bpm.bpm) for bpm in self.bpms]

        return measure_to_second(measure, bpms)

    def second_to_measure(self, seconds: float) -> float:
        bpms = [(bpm.measure, bpm.bpm) for bpm in self.bpms]

        return second_to_measure(seconds, bpms)

    def get_bpm_statistic(self) -> Tuple[float, float, float, float]:
        """Reads all the BPM defined and provides statistics.

        Returns:
            A tuple of floats representing BPMs:
             (STARTING, MODE, HIGHEST, LOWEST)

        Raises:
            Exception: If there are no BPM events defined.
        """
        if len(self.bpms) == 0:
            raise ValueError("No BPMs defined.")

        self.bpms.sort(key=lambda x: x.measure)
        bpm_list = [bpm.bpm for bpm in self.bpms]

        starting_bpm = self.get_bpm(0.0)
        mode_bpm = starting_bpm
        highest_bpm = max(bpm_list)
        lowest_bpm = min(bpm_list)

        bpm_duration = defaultdict(lambda: 0.0)

        last_measure = max([note.measure for note in self.notes])
        for i, bpm in enumerate(self.bpms):
            current_measure = bpm.measure
            bpm_value = bpm.bpm
            if i == len(self.bpms) - 1:
                bpm_duration[bpm_value] += last_measure - current_measure
            else:
                bpm_duration[bpm_value] += self.bpms[i + 1].measure - current_measure

            if bpm_duration[bpm_value] > bpm_duration[mode_bpm]:
                mode_bpm = bpm_value

        return starting_bpm, mode_bpm, highest_bpm, lowest_bpm

    def get_header(self, resolution: int) -> str:
        """Generates a 7 line header required in ma2 formats.

        If there are no defined meter events, it is assumed that the
        meter is 4/4.

        Returns:
            A multiline string.
        """
        bpms = self.get_bpm_statistic()
        try:
            starting_meter = self.get_meter(0.0)
            meter_num = starting_meter[0]
            meter_den = starting_meter[1]
        except ValueError:
            print("Warning: No starting meter defined. Assuming 4 4")
            meter_num = 4
            meter_den = 4

        result = f"VERSION\t0.00.00\t{MA2_VERSION}\n"
        result += f"FES_MODE\t{1 if self.fes_mode else 0}\n"
        result += (
            f"BPM_DEF\t{bpms[0]:.3f}\t{bpms[1]:.3f}\t{bpms[2]:.3f}\t{bpms[3]:.3f}\n"
        )
        result += f"MET_DEF\t{meter_num}\t{meter_den}\n"
        result += f"RESOLUTION\t{resolution}\n"
        result += f"CLK_DEF\t{resolution}\n"
        result += "COMPATIBLE_CODE\tMA2\n"

        return result

    def get_epilog(self) -> str:
        """Prints summary of all notes and score information.

        Returns:
            A multiline string.
            First part gives the total number of notes are in
            the chart. Second part is about score related information.

        """
        result = ""
        total_notes = 0
        for note_type in self.notes_stat:
            total_notes += self.notes_stat[note_type]
            result += "T_REC_{}\t{}\n".format(note_type, self.notes_stat[note_type])
        result += "T_REC_ALL\t{}\n".format(total_notes)

        num_taps = sum(
            [self.notes_stat[i] for i in ["TAP", "XTP", "STR", "XST", "TTP"]]
        )
        num_breaks = self.notes_stat["BRK"] + self.notes_stat["BST"]
        num_holds = sum([self.notes_stat[i] for i in ["HLD", "XHO", "THO"]])
        num_slides = self.notes_stat["SLD"]

        result += "T_NUM_TAP\t{}\n".format(num_taps)
        result += "T_NUM_BRK\t{}\n".format(num_breaks)
        result += "T_NUM_HLD\t{}\n".format(num_holds)
        result += "T_NUM_SLD\t{}\n".format(num_slides)
        result += "T_NUM_ALL\t{}\n".format(total_notes)

        judge_taps = num_taps + num_breaks
        judge_holds = round(num_holds * 1.75)
        judge_all = judge_taps + judge_holds + num_slides
        result += "T_JUDGE_TAP\t{}\n".format(judge_taps)
        result += "T_JUDGE_HLD\t{}\n".format(judge_holds)
        result += "T_JUDGE_SLD\t{}\n".format(num_slides)
        result += "T_JUDGE_ALL\t{}\n".format(judge_all)

        taps = [
            note.measure
            for note in self.notes
            if isinstance(note, (TapNote, HoldNote, TouchTapNote, TouchHoldNote))
        ]
        measures = set(taps)
        num_eachpairs = 0

        for measure in measures:
            if taps.count(measure) > 1:
                num_eachpairs += 1

        result += "TTM_EACHPAIRS\t{}\n".format(num_eachpairs)

        # From https://docs.google.com/document/d/1gQlxtxOj-E3H2SClJH5PNxLnG6eBufDFrw2yLsffbp0
        total_max_score_tap = 500 * num_taps
        total_max_score_break = 2600 * num_breaks
        total_max_score_hold = 1000 * num_holds
        total_max_score_slide = 1500 * num_slides
        total_max_score = (
            total_max_score_tap
            + total_max_score_break
            + total_max_score_hold
            + total_max_score_slide
        )
        result += "TTM_SCR_TAP\t{}\n".format(total_max_score_tap)
        result += "TTM_SCR_BRK\t{}\n".format(total_max_score_break)
        result += "TTM_SCR_HLD\t{}\n".format(total_max_score_hold)
        result += "TTM_SCR_SLD\t{}\n".format(total_max_score_slide)
        result += "TTM_SCR_ALL\t{}\n".format(total_max_score)
        total_base_score = (
            total_max_score_tap
            + total_max_score_hold
            + total_max_score_slide
            + 2500 * num_breaks
        )
        max_finale_achievement = int(10000 * total_max_score / total_base_score)
        total_max_score_s = round(0.97 * total_base_score / 100) * 100
        total_max_score_ss = total_base_score
        result += "TTM_SCR_S\t{}\n".format(total_max_score_s)
        result += "TTM_SCR_SS\t{}\n".format(total_max_score_ss)
        result += "TTM_RAT_ACV\t{}\n".format(max_finale_achievement)
        return result

    def export(self, resolution: int = 384) -> str:
        """Generates a ma2 text from all the notes and events defined.

        Returns:
            A multiline string. The returned
            string is a complete and functioning ma2 text and should
            be stored as-is in a text file with a .ma2 file extension.
        """
        # Header
        result = self.get_header(resolution=resolution)
        result += "\n"

        # BPM and meters
        self.bpms.sort(key=lambda x: x.measure)
        result += "\n".join([bpm.to_str(resolution) for bpm in self.bpms])
        self.meters.sort(key=lambda x: x.measure)
        result += "\n".join([meter.to_str(resolution) for meter in self.meters])
        result += "\n"

        self.notes.sort()
        result += "\n".join([note.to_str(resolution=resolution) for note in self.notes])

        result += "\n"
        result += self.get_epilog()
        result += "\n"
        return result
