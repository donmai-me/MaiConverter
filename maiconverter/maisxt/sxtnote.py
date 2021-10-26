import math
from typing import Union, Optional

from .sxtchart import SxtChartType
from ..event import MaiNote, NoteType
from ..tool import slide_distance

srt_note_to_later_note = {
    # 0 (tap notes) can be star, break star, start slide, or tap note
    2: 2,
    4: 3,
    128: 128,
}

srt_szt_template = "{:.6f}, {:.6f}, {:.6f}, {:2d}, {:3d}, {:3d}, {:2d},\n"
sct_template = "{:.4f}, {:.4f}, {:.4f}, {:2d}, {:3d}, {:3d}, {:2d}, {:2d},\n"
sdt_template = "{:.4f}, {:.4f}, {:.4f}, {:2d}, {:3d}, {:3d}, {:2d}, {:2d}, {:.4f},\n"


class TapNote(MaiNote):
    def __init__(
        self,
        measure: float,
        position: int,
        is_break: bool = False,
        is_star: bool = False,
    ) -> None:
        """Produces an sxt tap note.

        Note:
            Please use MaiSxt class' add_tap method for adding
            tap notes.

        Args:
            measure: Time when the tap happens, in terms of measures.
            position: Button where the tap note happens.
            is_break: Whether a tap note is a break note.
        """
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
        # return self.to_str(SxtChartType.SDT)

    def to_str(
        self,
        chart_type: SxtChartType,
        srt_slide_duration: Optional[float] = None,
        srt_slide_id: Optional[int] = None,
        srt_slide_pattern: Optional[int] = None,
    ) -> str:
        raise NotImplementedError

        measure = math.modf(self.measure)
        is_star = self.note_type in [NoteType.break_star, NoteType.star]

        if chart_type is SxtChartType.SRT:
            if self.note_type is NoteType.break_star:
                print(
                    "Warning: Converting break star to regular star. Report an issue if SRT supports break stars."
                )

            if is_star and (
                srt_slide_duration is None
                or srt_slide_id is None
                or srt_slide_pattern is None
            ):
                raise ValueError(
                    "Slide duration, id, or pattern is not given for SRT star note."
                )

            return srt_szt_template.format(
                measure[1],
                measure[0],
                0.0 if not is_star else srt_slide_duration,
                self.position,
                4 if self.note_type is NoteType.break_tap else 0,
                0 if srt_slide_id is None else srt_slide_id,
                0 if srt_slide_pattern is None else srt_slide_pattern,
            )
        elif chart_type is SxtChartType.SZT:
            return srt_szt_template.format(
                measure[1],
                measure[0],
                0.0625,
                self.position,
                self.note_type.value,
                0,
                0,
            )
        elif chart_type is SxtChartType.SCT:
            return sct_template.format(
                measure[1],
                measure[0],
                0.0625,
                self.position,
                self.note_type.value,
                0,
                0,
                0 if not is_star else self.amount,
            )
        else:
            return sdt_template.format(
                measure[1],
                measure[0],
                0.0625,
                self.position,
                self.note_type.value,
                0,
                0,
                0 if not is_star else self.amount,
                0.0,
            )


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
        """Produces an sxt slide start note.

        Note:
            Please use MaiSxt class' add_slide method for adding
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

        duration = round(10000.0 * duration) / 10000.0
        delay = round(10000.0 * delay) / 10000.0
        super().__init__(measure, position, NoteType.start_slide)
        self.slide_id = slide_id
        self.pattern = pattern
        self.delay = delay
        self.duration = duration

    def __str__(self) -> str:
        return sdt_note_to_str(self)

    # def to_str(self, slide_delay: float):


class SlideEndNote(MaiNote):
    def __init__(
        self, measure: float, position: int, pattern: int, slide_id: int
    ) -> None:
        """Produces an sxt slide end note.

        Note:
            Please use MaiSxt class' add_slide method for adding
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
        """Produces an sxt hold note.

        Note:
            Please use MaiSxt class' add_hold method for adding
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
    """Prints note into sxt-compatible lines.

    Args:
        note: A MaiNote to be converted to a sxt string.

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
    line_template = "{:.4f}, {:.4f}, {:.4f}, {:2d}, {:3d}, {:3d}, {:2d}, {:2d}, {:.4f},"
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


def check_slide(
    pattern: int,
    start_position: int,
    end_position: int,
    chart_type: SxtChartType = SxtChartType.SDT,
):
    """Function that checks a slide if it's valid. Will raise a ValueError if given
    a slide that will crash the game or has undefined behaviour.

    Args:
        pattern: The slide pattern of a slide. Should be ints corresponding to slides from SZT and later.
        start_position: The button where a slide begins.
        end_position: The button where a slide ends.
        chart_type: Optional chart type. Used only for checking SRT slides.

    Raises:
        ValueError: When given a slide that will crash the game or has undefined
            behaviour.
    """
    if not (0 <= start_position <= 7):
        raise ValueError(f"Invalid start position {start_position}")
    if not (0 <= end_position <= 7):
        raise ValueError(f"Invalid end position {end_position}")
    if chart_type is SxtChartType.SRT and not (1 <= pattern <= 3):
        raise ValueError(f"Invalid pattern for SRT chart {pattern}")
    if chart_type is not SxtChartType.SRT and not (1 <= pattern <= 13):
        raise ValueError(f"Invalid pattern for non-SRT chart {pattern}")

    # Helper variables
    distance_cw = slide_distance(start_position, end_position, is_cw=True)
    distance_ccw = slide_distance(start_position, end_position, is_cw=False)

    if pattern == 1:
        # Straight slide's end position should at least be two places away
        if not 2 <= distance_cw <= 6:
            raise ValueError(
                "Distance between start and end position should be greater than 1 in pattern 1"
            )
    elif pattern == 2 and chart_type is SxtChartType.SRT:
        # CCW around the judgement ring in SRT can only do 3 places max
        if not distance_ccw <= 3:
            raise ValueError("SRT can only do distances of 3 places max in pattern 2")
    elif pattern == 3 and chart_type is SxtChartType.SRT:
        # CW around the judgement ring in SRT can only do 3 places max
        if not distance_cw <= 3:
            raise ValueError("SRT can only do distances of 3 places max in pattern 3")
    elif pattern in [6, 7] and distance_cw != 4:
        # Zigzags end_position should be opposite of start_position
        raise ValueError(
            "End position is not opposite of start position in pattern 6 or 7"
        )
    elif pattern == 11:
        if not distance_ccw >= 4:
            raise ValueError(f"CCW distance is less than 4 in pattern 11")
    elif pattern == 12:
        if not distance_cw >= 4:
            raise ValueError(f"CW distance is less than 4 in pattern 12")
    elif pattern == 13 and distance_cw != 4:
        raise ValueError("End position is not opposite of start position in pattern 13")
