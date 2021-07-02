import math
from typing import Union

from ..event import MaiNote, NoteType


class TapNote(MaiNote):
    def __init__(
        self,
        measure: float,
        position: int,
        is_break: bool = False,
        is_star: bool = False,
    ) -> None:
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
        if is_break and is_star:
            super().__init__(measure, position, NoteType.break_star)
            self.amount = 0
        elif is_break:
            super().__init__(measure, position, NoteType.break_tap)
        elif is_star:
            super().__init__(measure, position, NoteType.star)
            self.amount = 0
        else:
            super().__init__(measure, position, NoteType.tap)

    def __str__(self) -> str:
        return sdt_note_to_str(self)


class SlideStartNote(MaiNote):
    def __init__(
        self,
        measure: float,
        position: int,
        pattern: int,
        duration: float,
        slide_id: int,
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
        if pattern <= 0:
            raise ValueError("Slide pattern is not positive " + str(pattern))
        if duration <= 0:
            raise ValueError("Slide duration is not positive " + str(duration))
        if delay < 0:
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


class SlideEndNote(MaiNote):
    def __init__(
        self, measure: float, position: int, pattern: int, slide_id: int
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
        if pattern <= 0:
            raise ValueError("Slide pattern is not positive " + str(pattern))

        measure = round(10000 * measure) / 10000
        super().__init__(measure, position, NoteType.end_slide)
        self.slide_id = slide_id
        self.pattern = pattern

    def __str__(self) -> str:
        return sdt_note_to_str(self)


class HoldNote(MaiNote):
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
        if duration < 0:
            raise ValueError(f"Hold duration is negative: {duration}")

        measure = round(10000.0 * measure) / 10000.0
        duration = round(10000.0 * duration) / 10000.0
        super().__init__(measure, position, NoteType.hold)
        self.duration = duration

    def __str__(self) -> str:
        return sdt_note_to_str(self)


def sdt_note_to_str(
    note: Union[TapNote, HoldNote, SlideEndNote, SlideStartNote]
) -> str:
    """Prints note into sdt-compatible lines.

    Args:
        note: A MaiNote to be converted to a sdt string.

    Returns:
        A single line string.
    """
    measure = math.modf(note.measure)
    note_type = note.note_type
    if isinstance(note, (HoldNote, SlideStartNote)):
        note_duration = note.duration
    elif isinstance(note, SlideEndNote):
        note_duration = 0
    else:
        note_duration = 0.0625

    if isinstance(note, (SlideStartNote, SlideEndNote)):
        slide_id = note.slide_id
        pattern = note.pattern
    else:
        slide_id = 0
        pattern = 0

    if isinstance(note, TapNote) and note.note_type in [
        NoteType.star,
        NoteType.break_star,
    ]:
        slide_amount = note.amount
    else:
        slide_amount = 0

    delay = 0.0 if not isinstance(note, SlideStartNote) else note.delay
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
