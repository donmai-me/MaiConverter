import math
from typing import Tuple

from maiconverter.event import MaiNote, NoteType, Event, EventType
from maiconverter.tool import slide_distance

# Dictionary for a note type's representation in ma2
# Does not cover slide notes, BPM, and meter events.
# Use slide_dict for slides instead.
note_dict = {
    "TAP": 1,
    "HLD": 2,
    "BRK": 3,
    "STR": 4,
    "BST": 5,
    "XTP": 6,
    "XST": 7,
    "XHO": 8,
    "TTP": 9,
    "THO": 10,
    # "SLD": 11
}

# Dictionary for a slide note's representation in ma2 by pattern.
slide_dict = {
    "SI_": 1,
    "SCL": 2,
    "SCR": 3,
    "SUL": 4,
    "SUR": 5,
    "SSL": 6,
    "SSR": 7,
    "SV_": 8,
    "SXL": 9,
    "SXR": 10,
    "SLL": 11,
    "SLR": 12,
    "SF_": 13,
}


class SlideNote(MaiNote):
    def __init__(
        self,
        measure: float,
        start_position: int,
        end_position: int,
        pattern: int,
        duration: float,
        delay: float = 0.25,
    ) -> None:
        """Produces a ma2 slide note.

        Note:
            Please use MaiMa2 class' add_slide method for adding slides.

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
        Raises:
            ValueError: When pattern or duration is not a positive integer,
                        and when delay, or end_position are negative.
        """
        if pattern <= 0:
            raise ValueError(f"Slide pattern is not positive {pattern}")
        if duration <= 0:
            raise ValueError(f"Slide duration is not positive {duration}")
        if delay < 0:
            raise ValueError(f"Slide delay is negative {delay}")
        if end_position < 0:
            raise ValueError(f"Slide end position is negative {end_position}")

        super().__init__(measure, start_position, NoteType.complete_slide)
        self.end_position = end_position
        self.pattern = pattern
        self.delay = delay
        self.duration = duration

    def to_str(self, resolution: int = 384) -> str:
        measure = measure_to_ma2_time(self.measure, resolution)
        template = "{}\t{}\t{}\t{}\t{}\t{}\t{}"
        inv_slide_dict = {v: k for k, v in slide_dict.items()}
        if self.pattern not in inv_slide_dict:
            raise ValueError(f"Unknown slide pattern {self.pattern}")

        pattern = inv_slide_dict[self.pattern]
        delay = round(self.delay * resolution)
        duration = round(self.duration * resolution)
        return template.format(
            pattern,
            measure[0],
            measure[1],
            self.position,
            delay,
            duration,
            self.end_position,
        )


class HoldNote(MaiNote):
    def __init__(
        self,
        measure: float,
        position: int,
        duration: float,
        is_ex: bool = False,
    ) -> None:
        """Produces a ma2 hold note.

        Note:
            Please use MaiMa2 class' add_hold method for adding holds.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the hold note happens.
            duration: Total time duration of the hold note.
            is_ex: Whether a hold note is an ex note.

        Raises:
            ValueError: When duration is not positive.
        """
        if duration < 0:
            raise ValueError(f"Hold duration is negative: {duration}")

        if is_ex:
            super().__init__(measure, position, NoteType.ex_hold)
        else:
            super().__init__(measure, position, NoteType.hold)

        self.duration = duration

    def to_str(self, resolution: int) -> str:
        measure = measure_to_ma2_time(self.measure, resolution)
        template = "HLD\t{}\t{}\t{}\t{}"
        duration = round(self.duration * resolution)
        return template.format(measure[0], measure[1], self.position, duration)


class TapNote(MaiNote):
    def __init__(
        self,
        measure: float,
        position: int,
        is_star: bool = False,
        is_break: bool = False,
        is_ex: bool = False,
    ) -> None:
        """Produces a ma2 tap note.

        Note:
            Please use MaiMa2 class' add_tap method for adding taps.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Button where the tap note happens.
            is_star: Whether a tap note is a star note.
            is_break: Whether a tap note is a break note.
            is_ex: Whether a tap note is an ex note.
        """

        if is_ex and is_star:
            super().__init__(measure, position, NoteType.ex_star)
        elif is_ex and not is_star:
            super().__init__(measure, position, NoteType.ex_tap)
        elif is_star and is_break:
            super().__init__(measure, position, NoteType.break_star)
        elif is_star and not is_break:
            super().__init__(measure, position, NoteType.star)
        elif not is_star and is_break:
            super().__init__(measure, position, NoteType.break_tap)
        elif not is_star and not is_break:
            super().__init__(measure, position, NoteType.tap)

    def to_str(self, resolution: int) -> str:
        measure = measure_to_ma2_time(self.measure, resolution)
        template = "{}\t{}\t{}\t{}"
        inv_note_dict = {v: k for k, v in note_dict.items()}
        if self.note_type.value not in inv_note_dict:
            raise ValueError(f"Unknown tap note {self.note_type.value}")

        name = inv_note_dict[self.note_type.value]
        return template.format(name, measure[0], measure[1], self.position)


class TouchTapNote(MaiNote):
    def __init__(
        self,
        measure: float,
        position: int,
        region: str,
        is_firework: bool = False,
        size: str = "M1",
    ) -> None:
        """Produces a ma2 touch tap note.

        Note:
            Please use MaiMa2 class' add_touch_tap method
            for adding touch taps.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Position in the region where the note happens.
            region: Touch region where the note happens.
            is_firework: Whether a touch tap note will produce
                         fireworks. Optional bool, defaults to False.
            size: Optional str. Specifies the size of touch note defaults to "M1"

        Examples:
            A touch tap note at E0 at measure 2.25, produces no
            fireworks.

            >>> touch_tap = TouchTapNote(2.25, 0, "E")

            A touch tap note at B5 at measure 5.00, produces fireworks.

            >>> touch_tap = TouchTapNote(5.00, 5, "B", True)
        """
        if size not in ["M1", "L1"]:
            raise ValueError(f"Invalid size given: {size}")

        super().__init__(measure, position, NoteType.touch_tap)
        self.is_firework = is_firework
        self.region = region
        self.size = size

    def to_str(self, resolution: int) -> str:
        measure = measure_to_ma2_time(self.measure, resolution)
        template = "TTP\t{}\t{}\t{}\t{}\t{}\t{}"
        fireworks = 1 if self.is_firework else 0
        return template.format(
            measure[0],
            measure[1],
            self.position,
            self.region,
            fireworks,
            self.size,
        )


class TouchHoldNote(MaiNote):
    def __init__(
        self,
        measure: float,
        position: int,
        region: str,
        duration: float,
        is_firework: bool = False,
        size: str = "M1",
    ) -> None:
        """Produces a ma2 touch hold note.

        Note:
            Please use MaiMa2 class' add_touch_hold method
            for adding touch holds.

        Args:
            measure: Time when the note starts, in terms of measures.
            position: Position in the region where the note happens.
            region: Touch region where the note happens.
            duration: Total time duration of the touch hold note.
            is_firework: Whether a touch hold note will produce
                         fireworks. Optional bool, defaults to False.
            size: Optional str. Specifies the size of touch note defaults to "M1"

        Examples:
            A touch hold note at C0 at measure 1 with duration of
            1.5 measures, produces no fireworks.

            >>> touch_tap = TouchHoldNote(1, 0, "C", 1.5)
        """
        if duration < 0:
            raise ValueError(f"Hold duration is negative: {duration} ")
        if size not in ["M1", "L1"]:
            raise ValueError(f"Invalid size given: {size}")

        duration = round(duration * 10000.0) / 10000.0

        super().__init__(measure, position, NoteType.touch_hold)
        self.duration = duration
        self.is_firework = is_firework
        self.region = region
        self.size = size

    def to_str(self, resolution: int) -> str:
        measure = measure_to_ma2_time(self.measure, resolution)
        template = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}"
        name = "THO"
        duration = round(self.duration * resolution)
        fireworks = 1 if self.is_firework else 0
        return template.format(
            name,
            measure[0],
            measure[1],
            self.position,
            duration,
            self.region,
            fireworks,
            self.size,
        )


class BPM(Event):
    def __init__(self, measure: float, bpm: float) -> None:
        """Produces a ma2 BPM event.

        Note:
            Please use MaiMa2 class' set_bpm method
            for adding BPM events.

        Args:
            measure: Time when the BPM change happens,
                     in terms of measures.
            bpm: The tempo in beats per minute.

        Raises:
            ValueError: When bpm is not positive.

        Examples:
            A bpm of 220 at measure 3.

            >>> ma2_bpm = BPM(3, 220)
        """
        if bpm <= 0:
            raise ValueError(f"BPM is not positive: {bpm}")

        super().__init__(measure, EventType.bpm)
        self.bpm = bpm

    def to_str(self, resolution: int) -> str:
        if self.measure == 0.0:
            measure = (0, 0)
        else:
            measure = measure_to_ma2_time(self.measure, resolution)

        template = "BPM\t{}\t{}\t{:.3f}"
        return template.format(measure[0], measure[1], self.bpm)


class Meter(Event):
    def __init__(
        self,
        measure: float,
        meter_numerator: int,
        meter_denominator: int,
    ) -> None:
        """Produces a ma2 meter signature event.

        Note:
            Please use MaiMa2 class' set_meter method
            for adding meter signature events.

        Args:
            measure: Time when the meter change happens,
                     in terms of measures.
            meter_numerator: The upper numeral in a meter/time
                             signature.
            meter_denominator: The lower numeral in a meter/time
                             signature.

        Raises:
            ValueError: When meter_numerator or
                        meter_denominator is not positive.
        """
        if meter_numerator <= 0:
            raise ValueError("Meter numerator is not positive: {meter_numerator}")
        if meter_denominator <= 0:
            raise ValueError(f"Meter denominator is not positive {meter_denominator}")

        super().__init__(measure, EventType.meter)
        self.numerator = meter_numerator
        self.denominator = meter_denominator

    def to_str(self, resolution: int) -> str:
        if self.measure == 0.0:
            measure = (0, 0)
        else:
            measure = measure_to_ma2_time(self.measure, resolution)

        template = "MET\t{}\t{}\t{}\t{}"
        return template.format(measure[0], measure[1], self.numerator, self.denominator)


def measure_to_ma2_time(measure: float, resolution: int) -> Tuple[int, int]:
    """Convert measure in decimal form to ma2's format.

    Ma2 uses integer timing for its measures. It does so by taking
    the fractional part and multiplying it to the chart's
    resolution, then rounding it up. For durations like holds
    and slides, both the whole and fractional part are
    multiplied by the charts resolution.

    Args:
        measure: The time a note happened or duration.
        resolution: The number of ticks equal to one measure.

    Returns:
        A tuple (WHOLE_PART, FRACTIONAL_PART).

    Raises:
        ValueError: When measure is negative.

    Examples:
        Convert a note that happens in measure 2.5 in ma2 time
        with resolution of 384.

        >>> print(measure_to_ma2_time(2.5))
        (2, 192)

        Convert a duration of 3.75 measures in ma2 time with
        resolution of 500.

        >>> my_resolution = 500
        >>> (whole, dec) = measure_to_ma2_time(3.75, my_resolution)
        >>> whole*my_resolution + dec
        1875.0
    """
    if measure < 0:
        raise ValueError("Measure is negative. " + str(measure))

    (decimal_part, whole_part) = math.modf(measure)
    decimal_part = round(decimal_part * resolution)

    return int(whole_part), decimal_part


def check_slide(pattern: int, start_position: int, end_position: int):
    """Function that checks a slide if it's valid. Will raise a ValueError if given
    a slide that will crash the game or has undefined behaviour.

    Args:
        pattern: The slide pattern of a slide.
        start_position: The button where a slide begins.
        end_position: The button where a slide ends.

    Raises:
        ValueError: When given a slide that will crash the game or has undefined
            behaviour.
    """
    if not (0 < pattern < 14):
        raise ValueError(f"Invalid slide pattern {pattern}")
    if not (0 <= start_position <= 7):
        raise ValueError(f"Invalid start position {start_position}")
    if not (0 <= end_position <= 7):
        raise ValueError(f"Invalid end position {end_position}")

    distance_cw = slide_distance(start_position, end_position, is_cw=True)
    distance_ccw = slide_distance(start_position, end_position, is_cw=False)

    if pattern == 1:
        if not (distance_cw > 1 and distance_ccw > 1):
            raise ValueError(
                "Distance between start and end position must be greater than 1 in SI_."
            )
    elif pattern in [6, 7, 13]:
        if distance_cw != 4:
            raise ValueError(
                "Start and end position must be opposite of each other in SSL, SSR, or SF_."
            )
    elif pattern == 8:
        if start_position == end_position:
            raise ValueError(
                "Start and end position must not be equal to each other in SV_."
            )
    elif pattern == 11:
        if not 0 < distance_cw < 5:
            raise ValueError("Clockwise distance must be between 0 and 5 in SLL.")
    elif pattern == 12:
        if not 0 < distance_ccw < 5:
            raise ValueError(
                "Counter-clockwise distance must be between 0 and 5 in SLR."
            )
