from __future__ import annotations

import math
import re
from typing import Union, List, Dict

from .sxtnote import (
    TapNote,
    HoldNote,
    SlideStartNote,
    SlideEndNote,
    is_slide_valid,
)
from ..event import NoteType
from ..tool import measure_to_second, second_to_measure


class MaiSxt:
    """A class that represents an sxt (and predecessors) chart.
    Only contains notes, and does not include information
    such as song name, chart difficulty, composer, chart maker, etc.
    It only contains enough information to build a working sxt
    chart file.

    Attributes:
        bpm: Singular BPM in which the chart is written in.
        notes: Contains notes of the chart.
    """

    def __init__(self, bpm: float) -> None:
        if bpm <= 0:
            raise ValueError(f"BPM is not positive {bpm}")

        self.bpm = bpm
        self.notes: List[Union[TapNote, HoldNote, SlideStartNote, SlideEndNote]] = []
        self.start_slide_notes: Dict[int, Dict[str, Union[int, float]]] = {}
        self.slide_count = 1

    @classmethod
    def open(cls, path: str, bpm: float, encoding: str = "utf-8") -> MaiSxt:
        sdt = cls(bpm=bpm)
        with open(path, "r", encoding=encoding) as file:
            for line in file:
                if line in ["\n", "\r\n"]:
                    continue

                if re.search(r"\.srt", path) is None:
                    sdt.parse_line(line)
                else:
                    sdt.parse_srt_line(line)

        return sdt

    def parse_line(self, line: str) -> None:
        """Parse a non-SRT comma-separated line.

        Args:
            line: A non-SRT comma-separated line.

        Raises:
            ValueError: When the number of columns are not between 7 and 9.
                When an end slide is declared before an beginning slide.
                When an unknown note type is given.
        """
        values = line.rstrip().rstrip(",").replace(" ", "").split(",")
        if not (7 <= len(values) <= 9):
            raise ValueError(f"Line has invalid number of columns {len(values)}")

        measure = float(values[0]) + float(values[1])
        position = int(values[3])
        note_type = int(values[4])

        if note_type in [1, 3, 4, 5]:
            # Regular tap note, break tap note, star note, break star note
            is_star = note_type in [4, 5]
            is_break = note_type in [3, 5]
            self.add_tap(
                measure=measure, position=position, is_break=is_break, is_star=is_star
            )
        elif note_type == 2:
            # Hold note
            duration = float(values[2])
            self.add_hold(measure, position, duration)
        elif note_type == 0:  # Start slide
            if len(values) == 9:
                # SDT includes delay
                delay = float(values[8])
            else:
                delay = 0.25

            duration = float(values[2])
            slide_id = int(values[5])
            pattern = int(values[6])
            start_slide = {
                "position": position,
                "measure": measure,
                "duration": duration,
                "delay": delay,
                "pattern": pattern,
            }
            self.start_slide_notes[slide_id] = start_slide
        elif note_type == 128:  # End slide
            slide_id = int(values[5])

            # Get information about corresponding start slide
            if slide_id not in self.start_slide_notes:
                raise ValueError("End slide is declared before slide start!")

            start_slide = self.start_slide_notes[slide_id]
            start_measure = start_slide["measure"]
            start_position = start_slide["position"]
            duration = start_slide["duration"]
            delay = start_slide["delay"]
            slide_pattern = start_slide["pattern"]
            self.add_slide(
                start_measure,
                int(start_position),
                position,
                duration,
                int(slide_pattern),
                delay,
            )
        else:
            raise ValueError("Unknown note type {}".format(note_type))

    def parse_srt_line(self, line: str) -> None:
        """Parse an SRT comma-separated line.

        Args:
            line: An SRT comma-separated line.

        Raises:
            ValueError: When the number of columns are not between 7 and 9.
                When an end slide is declared before an beginning slide.
                When an unknown note type is given.
        """
        srt_slide_to_later_dict = {
            0: 1,
            1: 3,
            2: 2,
        }
        values = line.rstrip().rstrip(",").replace(" ", "").split(",")
        if len(values) != 7:
            raise ValueError(f"SRT should have 7 columns. Given: {len(values)}")

        measure = float(values[0]) + float(values[1])
        position = int(values[3])
        note_type = int(values[4])

        if note_type in [0, 4]:
            # 0: Regular tap note or star and start slide note
            # 4: Break tap note
            slide_id = int(values[5])
            if slide_id != 0:
                # Tap notes with a non-zero slide id are stars and start slide
                self.add_tap(measure=measure, position=position, is_star=True)
                duration = float(values[2])
                # Slide patterns in SZT, and later, starts at 1
                pattern = srt_slide_to_later_dict[int(values[6])]
                start_slide: Dict[str, Union[float, int]] = {
                    "position": position,
                    "measure": measure,
                    "duration": duration,
                    "pattern": pattern,
                }
                self.start_slide_notes[slide_id] = start_slide
            else:
                is_break = note_type == 4
                self.add_tap(measure=measure, position=position, is_break=is_break)
        elif note_type == 2:  # Hold note
            duration = float(values[2])
            self.add_hold(measure, position, duration)
        elif note_type == 128:
            slide_id = int(values[5])
            # Get information about corresponding start slide
            if slide_id not in self.start_slide_notes:
                raise RuntimeError("End slide is declared before slide start!")

            start: Dict[str, Union[float, int]] = self.start_slide_notes[slide_id]
            start_measure = start["measure"]
            start_position = start["position"]
            duration = start["duration"]
            slide_pattern = start["pattern"]
            self.add_slide(
                start_measure,
                int(start_position),
                position,
                duration,
                int(slide_pattern),
            )
        else:
            raise ValueError(f"Unknown note type {note_type}")

    def add_tap(
        self,
        measure: float,
        position: int,
        is_break: bool = False,
        is_star: bool = False,
        decrement: bool = True,
    ) -> None:
        """Adds a tap note to the list of notes.

        Args:
            measure: Time when the tap happens, in terms of measures.
            position: Button where the tap note happens.
            is_break: Whether a tap note is a break note.
            is_star: Whether a tap note is a star note.
            decrement: When set to true, measure is subtracted by 1. Defaults to true.

        Examples:
            Add a regular tap note at measure 1 at button 2,
            and a break tap note at measure 2 at button 7.

            >>> sxt = MaiSxt()
            >>> sxt.add_tap(1, 2)
            >>> sxt.add_tap(2, 7, is_break=True)
        """
        if decrement:
            measure = max(0.0, measure - 1.0)

        tap_note = TapNote(
            measure=measure, position=position, is_break=is_break, is_star=is_star
        )
        self.notes.append(tap_note)

    def del_tap(self, measure: float, position: int, decrement: bool = True) -> None:
        """Deletes a tap note from the list of notes.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the tap note happens.
            decrement: When set to true, measure is subtracted by 1. Defaults to true.

        Examples:
            Create a break tap note at measure 26.75 at button 4. Then delete it.

            >>> sxt = MaiSxt()
            >>> sxt.add_tap(26.75, 4, is_break=True)
            >>> sxt.del_tap(26.75, 4)
        """
        if decrement:
            measure = max(0.0, measure - 1.0)

        tap_notes = [
            x
            for x in self.notes
            if isinstance(x, TapNote)
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == position
        ]
        for note in tap_notes:
            self.notes.remove(note)

    def add_hold(
        self,
        measure: float,
        position: int,
        duration: float,
        decrement: bool = True,
    ) -> None:
        """Adds a hold note to the list of notes.

        Args:
            measure: Time when the hold starts, in terms of measures.
            position: Button where the hold happens.
            duration: Total duration of the hold, in terms of measures.
            decrement: When set to true, measure is subtracted by 1. Defaults to true.

        Examples:
            Add a regular hold note at button 5 at measure 1.5, with
            duration of 2.75 measures.

            >>> sxt = MaiSxt()
            >>> sxt.add_hold(1.5, 5, 2.75)
        """
        if decrement:
            measure = max(0.0, measure - 1.0)

        hold_note = HoldNote(measure=measure, position=position, duration=duration)
        self.notes.append(hold_note)

    def del_hold(self, measure: float, position: int, decrement: bool = True) -> None:
        """Deletes the matching hold note in the list of notes. If there are multiple
        matches, all matching notes are deleted. If there are no match, nothing happens.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the hold note happens.
            decrement: When set to true, measure is subtracted by 1. Defaults to true.

        Examples:
            Add a regular hold note at button 0 at measure 3.25 with duration of 2 measures
            and delete it.

            >>> sxt = MaiSxt()
            >>> sxt.add_hold(3.25, 0, 2)
            >>> sxt.del_hold(3.25, 0)
        """
        if decrement:
            measure = max(0.0, measure - 1.0)

        hold_notes = [
            x
            for x in self.notes
            if isinstance(x, HoldNote)
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == position
        ]
        for note in hold_notes:
            self.notes.remove(note)

    # Note: SDT slide duration includes delay
    def add_slide(
        self,
        measure: float,
        start_position: int,
        end_position: int,
        duration: float,
        pattern: int,
        delay: float = 0.25,
        check_slide: bool = True,
        fail_on_undefined: bool = False,
        decrement: bool = True,
    ) -> None:
        """Adds both a start slide and end slide note to the list of notes.

        Args:
            measure: Time when the slide starts, in
                terms of measures.
            start_position: Button where the slide starts.
            end_position: Button where the slide ends.
            duration: Total duration of the slide, in terms of
                measures. Includes slide delay.
            pattern: Numerical representation of the slide pattern.
            delay: Duration from when the slide appears and when it
                starts to move, in terms of measures. Defaults to 0.25.
            check_slide: When set to true, will check validity of slides.
            fail_on_undefined: Optional bool defaults to False. When True, slides with undefined
                behaviour will raise a ValueError instead.
            decrement: When set to true, measure is subtracted by 1. Defaults to true.

        Raises:
            ValueError: When a slide is invalid and crashes the game (Can be disabled by setting check_slide to False.)
                When fail_on_undefined is True and given a slide with undefined behaviour.

        Examples:
            Add a slide at measure 2 from button 6 to button 3 with
            duration of 1.75 measures, delay of 0.25 measures,
            pattern of 1.

            >>> sxt = MaiSxt()
            >>> sxt.add_slide(2, 6, 3, 1.75, 1)
        """
        if check_slide and not is_slide_valid(
            pattern, start_position, end_position, fail_on_undefined
        ):
            print(f"Warning: Adding slide with undefined behaviour.")

        if decrement:
            measure = max(0.0, measure - 1.0)

        slide_id = self.slide_count
        start_slide = SlideStartNote(
            measure=measure,
            position=start_position,
            pattern=pattern,
            duration=duration,
            slide_id=slide_id,
            delay=delay,
        )
        end_measure = measure + duration
        end_slide = SlideEndNote(
            measure=end_measure,
            position=end_position,
            pattern=pattern,
            slide_id=slide_id,
        )
        self.notes.append(start_slide)
        self.notes.append(end_slide)
        self.slide_count += 1

        star_notes = [
            x
            for x in self.notes
            if isinstance(x, TapNote)
            and x.note_type in [NoteType.star, NoteType.break_star]
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == start_position
        ]
        for star_note in star_notes:
            star_note.amount += 1

    def del_slide(
        self,
        measure: float,
        start_position: int,
        end_position: int,
        decrement: bool = True,
    ) -> None:
        if decrement:
            measure = max(0.0, measure - 1.0)

        start_slides = [
            x
            for x in self.notes
            if isinstance(x, SlideStartNote)
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == start_position
        ]
        end_slides: List[SlideEndNote] = []
        for note in start_slides:
            slides = [
                x
                for x in self.notes
                if isinstance(x, SlideEndNote)
                and x.slide_id == note.slide_id
                and x.position == end_position
            ]
            end_slides += slides

        correct_start_slides = []
        for note in end_slides:
            slides = [
                x
                for x in self.notes
                if isinstance(x, SlideStartNote) and x.slide_id == note.slide_id
            ]
            correct_start_slides += slides

        star_notes = [
            x
            for x in self.notes
            if isinstance(x, TapNote)
            and x.note_type in [NoteType.star, NoteType.break_star]
            and math.isclose(x.measure, measure, abs_tol=0.0001)
            and x.position == start_position
        ]

        for note in correct_start_slides:
            self.notes.remove(note)

        for note in end_slides:
            self.notes.remove(note)

        for star_note in star_notes:
            star_note.amount -= 1

    def offset(self, offset: Union[float, str]) -> None:
        if isinstance(offset, float):
            offset = offset
        elif isinstance(offset, str) and offset[-1].lower() == "s":
            offset = self.second_to_measure(float(offset[:-1]))
        elif isinstance(offset, str) and "/" in offset:
            fraction = offset.split("/")
            if len(fraction) != 2:
                raise ValueError(f"Invalid fraction: {offset}")

            offset = int(fraction[0]) / int(fraction[1])
        else:
            offset = float(offset)

        for note in self.notes:
            note.measure = round((note.measure + offset) * 10000.0) / 10000.0

    def measure_to_second(self, measure: float, decrement: bool = True) -> float:
        if decrement:
            measure = max(0.0, measure - 1.0)

        return measure_to_second(measure, [(0.0, self.bpm)])

    def second_to_measure(self, seconds: float, increment: bool = True) -> float:
        measure = second_to_measure(seconds, [(0.0, self.bpm)])
        if increment:
            measure += 1.0

        return measure

    def export(self) -> str:
        """Generates an sxt text from all the notes defined.

        Returns:
            A multiline string. The returned
            string is a complete and functioning sxt text and should
            be stored as-is in a text file with an sxt file extension.
        """
        self.notes.sort()
        return "\n".join([str(note) for note in self.notes]) + "\n"
