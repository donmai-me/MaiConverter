import math

from .note import MaiNote, NoteType


class MaiSDTStarNote(MaiNote):
    def __init__(
        self, measure: float, position: int, amount: int, is_break: bool = False
    ) -> None:
        """Produces an sdt star note.

        Note:
            Please use MaiSDT class' add_tap method for adding taps.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the star note happens.
            amount: Amount of slides a star notes produces.
            is_break: Whether a star note is a break note.

        Raises:
            ValueError: When amount is negative
        """
        if amount < 0:
            raise ValueError("Star note amount is negative " + str(amount))

        measure = round(10000.0 * measure) / 10000.0

        if is_break:
            super().__init__(measure, position, NoteType.break_star)
        else:
            super().__init__(measure, position, NoteType.star)

        self.amount = amount

    def __str__(self) -> str:
        return sdt_note_to_str(self)


class MaiSDTSlideStartNote(MaiNote):
    def __init__(
        self,
        measure: float,
        position: int,
        slide_id: int,
        pattern: int,
        duration: float,
        delay: float = 0.25,
    ) -> None:
        """Produces an sdt slide start note.

        Note:
            Please use MaiSDT class' add_slide method for adding
            slide start and slide end.

        Args:
            measure: Time when the slide starts, in terms of measures.
            position: Button where the slide starts.
            slide_id: Unique non-zero integer for slide start
                and end pair.
            pattern: Numerical representation of the slide pattern.
            duration: Total duration of the slide, in terms of
                measures. Includes slide delay.
            delay: Duration from when the slide appears and when it
                starts to move, in terms of measures.
        """
        if slide_id <= 0:
            raise ValueError("Slide id is not positive " + str(slide_id))
        elif pattern <= 0:
            raise ValueError("Slide pattern is not positive " + str(pattern))
        elif duration <= 0:
            raise ValueError("Slide duration is not positive " + str(duration))
        elif delay < 0:
            raise ValueError("Slide delay is negative " + str(delay))

        measure = round(10000.0 * measure) / 10000.0
        duration = round(10000.0 * duration) / 10000.0
        delay = round(10000.0 * delay) / 10000.0
        super().__init__(measure, position, NoteType.start_slide)
        self.slide_id = slide_id
        self.pattern = pattern
        self.delay = delay
        self.duration = duration

    def __str__(self) -> str:
        return sdt_note_to_str(self)


class MaiSDTSlideEndNote(MaiNote):
    def __init__(
        self, measure: float, position: int, slide_id: int, pattern: int
    ) -> None:
        """Produces an sdt slide end note.

        Note:
            Please use MaiSDT class' add_slide method for adding
            slide start and slide end.

        Args:
            measure: Time when the slide ends, in terms of measures.
            position: Button where the slide ends.
            slide_id: Unique non-zero integer for slide start
                and end pair.
            pattern: Numerical representation of the slide pattern.
        """
        if slide_id <= 0:
            raise ValueError("Slide id is not positive " + str(slide_id))
        elif pattern <= 0:
            raise ValueError("Slide pattern is not positive " + str(pattern))

        measure = round(10000 * measure) / 10000
        super().__init__(measure, position, NoteType.end_slide)
        self.slide_id = slide_id
        self.pattern = pattern

    def __str__(self) -> str:
        return sdt_note_to_str(self)


class MaiSDTHoldNote(MaiNote):
    def __init__(self, measure: float, position: int, duration: float) -> None:
        """Produces an sdt hold note.

        Note:
            Please use MaiSDT class' add_hold method for adding
            hold notes.

        Args:
            measure: Time when the hold starts, in terms of measures.
            position: Button where the hold happens.
            duration: Total duration of the hold, in terms of measures.
        """
        if duration <= 0:
            raise ValueError("Slide duration is not positive " + str(duration))

        measure = round(10000.0 * measure) / 10000.0
        duration = round(10000.0 * duration) / 10000.0
        super().__init__(measure, position, NoteType.hold)
        self.duration = duration

    def __str__(self) -> str:
        return sdt_note_to_str(self)


class MaiSDTTapNote(MaiNote):
    def __init__(self, measure: float, position: int, is_break: bool = False) -> None:
        """Produces an sdt tap note.

        Note:
            Please use MaiSDT class' add_tap method for adding
            tap notes.

        Args:
            measure: Time when the tap happens, in terms of measures.
            position: Button where the tap note happens.
            is_break: Whether a tap note is a break note.
        """
        measure = round(10000.0 * measure) / 10000.0
        if is_break:
            super().__init__(measure, position, NoteType.break_tap)
        else:
            super().__init__(measure, position, NoteType.tap)

    def __str__(self) -> str:
        return sdt_note_to_str(self)


def sdt_note_to_str(note: MaiNote) -> str:
    """Prints note into sdt-compatible lines.

    Args:
        note: A MaiNote to be converted to a sdt string.

    Returns:
        A single line string.
    """
    measure = math.modf(note.measure)
    note_type = note.note_type
    if isinstance(note, (MaiSDTHoldNote, MaiSDTSlideStartNote)):
        note_duration = note.duration
    elif isinstance(note, MaiSDTSlideEndNote):
        note_duration = 0
    else:
        note_duration = 0.0625

    if isinstance(note, (MaiSDTSlideStartNote, MaiSDTSlideEndNote)):
        slide_id = note.slide_id
        pattern = note.pattern
    else:
        slide_id = 0
        pattern = 0

    if isinstance(note, MaiSDTStarNote):
        slide_amount = note.amount
    else:
        slide_amount = 0

    delay = 0 if note_type != NoteType.start_slide else note.delay
    line_template = (
        "{:.4f}, {:.4f}, {:.4f}, {:2d}, {:3d}, {:3d}, {:2d}, {:2d}, {:.4f},\n"
    )
    result = line_template.format(
        measure[1],
        measure[0],
        note_duration,
        note.position,
        note_type.value,
        slide_id,
        pattern,
        slide_amount,
        delay,
    )
    return result


class MaiSDT:
    """A class that represents one sdt chart. Only contains notes,
    and does not include information such as bpm, song name,
    chart difficulty, composer, chart maker, etc.
    It only contains enough information to build a working sdt
    chart file.

    Attributes:
        notes (list[MaiNote]): Contains notes of the chart.
    """

    def __init__(self) -> None:
        self.notes = []
        self.start_slide_notes = {}
        self.slide_count = 1

    def parse_line(self, line: str) -> None:
        values = line.rstrip().rstrip(",").replace(" ", "").split(",")
        if not (len(values) >= 7 and len(values) <= 9):
            raise Exception("Line has invalid number of columns! {}".format(len(line)))
        measure = float(values[0]) + float(values[1])
        position = int(values[3])
        note_type = int(values[4])

        if note_type == 1:  # Regular tap note
            self.add_tap(measure, position)
        elif note_type == 2:  # Hold note
            duration = float(values[2])
            self.add_hold(measure, position, duration)
        elif note_type == 3:  # Break tap note
            self.add_tap(measure, position, is_break=True)
        elif note_type in [4, 5]:  # Regular star note
            if len(values) > 7:
                # SCT and later
                amount = int(values[7])
            else:
                amount = 1

            is_break = True if note_type == 5 else False
            self.add_star(measure, position, amount, is_break)
        elif note_type == 0:  # Start slide
            if len(values) == 9:  # SDT includes delay
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
            start_slide = self.start_slide_notes.get(slide_id)
            if start_slide is None:
                raise Exception("End slide is declared before slide start!")

            start_measure = start_slide.get("measure")
            start_position = start_slide.get("position")
            duration = start_slide.get("duration")
            delay = start_slide.get("delay")
            pattern = start_slide.get("pattern")
            self.add_slide(
                start_measure,
                start_position,
                position,
                pattern,
                duration,
                self.slide_count,
                delay,
            )
            self.slide_count += 1
        else:
            raise TypeError("Unknown note type {}".format(note_type))

    def parse_srt_line(self, line: str) -> None:
        srt_slide_to_later_dict = {
            0: 1,
            1: 3,
            2: 2,
        }
        values = line.rstrip().rstrip(",").replace(" ", "").split(",")
        if len(values) != 7:
            raise Exception("SRT should have 7 columns. Given: {}".format(line))

        measure = float(values[0]) + float(values[1])
        position = int(values[3])
        note_type = int(values[4])

        if note_type == 0:  # Regular tap note, or star and start slide note
            slide_id = int(values[5])
            # Tap notes with a non-zero slide id are stars and start slide
            if slide_id != 0:
                self.add_star(measure, position, 1)
                delay = 0.25
                duration = float(values[2])
                # Slide patterns in SZT, and later, starts at 1
                pattern = srt_slide_to_later_dict.get(int(values[6]))
                start_slide = {
                    "position": position,
                    "measure": measure,
                    "duration": duration,
                    "delay": delay,
                    "pattern": pattern,
                }
                self.start_slide_notes[slide_id] = start_slide
            else:
                self.add_tap(measure, position)
        elif note_type == 2:  # Hold note
            duration = float(values[2])
            self.add_hold(measure, position, duration)
        elif note_type == 4:  # Break tap note
            self.add_tap(measure, position, is_break=True)
        elif note_type == 128:
            slide_id = int(values[5])
            # Get information about corresponding start slide
            start_slide = self.start_slide_notes.get(slide_id)
            if start_slide is None:
                raise Exception("End slide is declared before slide start!")

            start_measure = start_slide.get("measure")
            start_position = start_slide.get("position")
            duration = start_slide.get("duration")
            delay = start_slide.get("delay")
            pattern = start_slide.get("pattern")
            self.add_slide(
                start_measure,
                start_position,
                position,
                pattern,
                duration,
                self.slide_count,
                delay,
            )
            self.slide_count += 1
        else:
            raise TypeError("Unknown note type {}".format(note_type))

    def add_tap(self, measure: float, position: int, is_break: bool = False) -> None:
        """Adds a tap note to the object.

        Args:
            measure: Time when the tap happens, in terms of measures.
            position: Button where the tap note happens.
            is_break: Whether a tap note is a break note.

        Examples:
            Add a regular tap note at measure 1 at button 2,
            and a break tap note at measure 2 at button 7.

            >>> sdt = MaiSDT()
            >>> sdt.add_tap(1, 2)
            >>> sdt.add_tap(2, 7, is_break=True)
        """
        tap_note = MaiSDTTapNote(measure, position, is_break)
        self.notes.append(tap_note)

    def add_hold(self, measure: float, position: int, duration: float) -> None:
        """Adds a hold note to the object.

        Args:
            measure: Time when the hold starts, in terms of measures.
            position: Button where the hold happens.
            duration: Total duration of the hold, in terms of measures.

        Examples:
            Add a regular hold note at button 5 at measure 1.5, with
            duration of 2.75 measures.

            >>> sdt = MaiSDT()
            >>> sdt.add_hold(1.5, 5, 2.75)
        """
        hold_note = MaiSDTHoldNote(measure, position, duration)
        self.notes.append(hold_note)

    def add_star(
        self, measure: float, position: int, amount: int, is_break: bool = False
    ) -> None:
        """Adds a star note to the object.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the star note happens.
            amount: Amount of slides a star notes produces.
            is_break: Whether a star note is a break note.

        Examples:
            Add a regular star note at button 3 at measure 1, which
            produces 1 slide. And a break star note at button 1 at
            measure 2.5, which produces no slides.

            >>> sdt = MaiSDT()
            >>> sdt.add_star(1, 3, 1)
            >>> sdt.add_star(2.5, 1, 0, is_break=True)
        """
        star_note = MaiSDTStarNote(measure, position, amount, is_break)
        self.notes.append(star_note)

    # Note: SDT slide duration includes delay
    def add_slide(
        self,
        start_measure: float,
        start_position: int,
        end_position: int,
        pattern: int,
        duration: float,
        slide_id: int,
        delay: float = 0.25,
    ) -> None:
        """Adds a star note to the object.

        Note:
            Having two pairs of slides with the same slide id will
            produce undefined behavior.

        Args:
            start_measure: Time when the slide starts, in
                terms of measures.
            start_position: Button where the slide starts.
            end_position: Button where the slide ends.
            pattern: Numerical representation of the slide pattern.
            duration: Total duration of the slide, in terms of
                measures. Includes slide delay.
            slide_id: Unique non-zero integer for slide start
                and end pair.
            delay: Duration from when the slide appears and when it
                starts to move, in terms of measures.

        Examples:
            Add a slide at measure 2 from button 6 to button 3 with
            duration of 1.75 measures, delay of 0.25 measures,
            pattern of 1, and slide id of 7.

            >>> sdt = MaiSDT()
            >>> sdt.add_slide(2, 6, 3, 1, 1.75, 7)
        """
        start_slide = MaiSDTSlideStartNote(
            start_measure, start_position, slide_id, pattern, duration, delay
        )
        end_measure = start_measure + duration
        end_slide = MaiSDTSlideEndNote(end_measure, end_position, slide_id, pattern)
        self.notes.append(start_slide)
        self.notes.append(end_slide)

    def export(self) -> str:
        """Generates an sdt text from all the notes defined.

        Returns:
            A multiline string. The returned
            string is a complete and functioning sdt text and should
            be stored as-is in a text file with an sdt file extension.
        """
        self.notes.sort()
        result = ""
        for note in self.notes:
            result += str(note)

        return result
