import math
from typing import Tuple, Union

from ..event import MaiNote, NoteType, Event, EventType

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
            resolution: Ma2 time resolution used. Optional, defaults to
                        384.
        Raises:
            ValueError: When pattern or duration is not a positive integer,
                        and when delay, or end_position are negative.
        """
        if pattern <= 0:
            raise ValueError("Slide pattern is not positive " + str(pattern))
        if duration <= 0:
            raise ValueError("Slide duration is not positive " + str(duration))
        if delay < 0:
            raise ValueError("Slide delay is negative " + str(delay))
        if end_position < 0:
            raise ValueError("Slide end position is negative " + str(end_position))

        measure = round(10000.0 * measure) / 10000.0
        super().__init__(measure, start_position, NoteType.complete_slide)
        self.end_position = end_position
        self.pattern = pattern
        self.delay = delay
        self.duration = duration


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
            resolution: Ma2 time resolution used. Optional, defaults to
                        384.

        Raises:
            ValueError: When duration is not positive.
        """
        if duration < 0:
            raise ValueError(f"Hold duration is negative: {duration}")

        measure = round(measure * 10000.0) / 10000.0
        duration = round(duration * 10000.0) / 10000.0

        if is_ex:
            super().__init__(measure, position, NoteType.ex_hold)
        else:
            super().__init__(measure, position, NoteType.hold)

        self.duration = duration


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
            resolution: Ma2 time resolution used. Optional, defaults to
                        384.
        """
        measure = round(measure * 10000.0) / 10000.0

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

            >>> touch_tap = MaiMa2TouchTapNote(2.25, 0, "E")

            A touch tap note at B5 at measure 5.00, produces fireworks.

            >>> touch_tap = MaiMa2TouchTapNote(5.00, 5, "B", True)
        """
        if size not in ["M1", "L1"]:
            raise ValueError(f"Invalid size given: {size}")

        measure = round(measure * 10000.0) / 10000.0

        super().__init__(measure, position, NoteType.touch_tap)
        self.is_firework = is_firework
        self.region = region
        self.size = size


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

            >>> touch_tap = MaiMa2TouchHoldNote(1, 0, "C", 1.5)
        """
        if duration <= 0:
            raise ValueError(f"Hold duration is not positive: {duration} ")
        if size not in ["M1", "L1"]:
            raise ValueError(f"Invalid size given: {size}")

        measure = round(measure * 10000.0) / 10000.0
        duration = round(duration * 10000.0) / 10000.0

        super().__init__(measure, position, NoteType.touch_hold)
        self.duration = duration
        self.is_firework = is_firework
        self.region = region
        self.size = size


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
            resolution: Ma2 time resolution used. Optional, defaults to
                        384.

        Raises:
            ValueError: When bpm is not positive.

        Examples:
            A bpm of 220 at measure 3.

            >>> ma2_bpm = MaiMa2BPM(3, 220)
        """
        if bpm <= 0:
            raise ValueError(f"BPM is not positive: {bpm}")

        measure = round(measure * 10000.0) / 10000.0

        super().__init__(measure, EventType.bpm)
        self.bpm = bpm


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
            resolution: Ma2 time resolution used. Optional, defaults to
                        384.

        Raises:
            ValueError: When meter_numerator or
                        meter_denominator is not positive.
        """
        if meter_numerator <= 0:
            raise ValueError("Meter numerator is not positive: {meter_numerator}")
        if meter_denominator <= 0:
            raise ValueError(f"Meter denominator is not positive {meter_denominator}")

        measure = round(measure * 10000.0) / 10000.0

        super().__init__(measure, EventType.meter)
        self.numerator = meter_numerator
        self.denominator = meter_denominator


def measure_to_ma2_time(measure: float, resolution: int = 384) -> Tuple[int, int]:
    """Convert measure in decimal form to ma2's format.

    Ma2 uses integer timing for its measures. It does so by taking
    the fractional part and multiplying it to the chart's
    resolution, then rounding it up. For durations like holds
    and slides, both the whole and fractional part are
    multiplied by the charts resolution.

    Args:
        measure: The time a note happened or duration.

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

    return (int(whole_part), decimal_part)


def event_to_str(
    event: Union[TapNote, HoldNote, SlideNote, TouchTapNote, TouchHoldNote, BPM, Meter],
    resolution: int = 384,
) -> str:
    """Converts ma2 note and events into ma2-compatible lines.

    Args:
        event: A bpm, meter, or note event.

    Returns:
        A single line string with a line ending.

    Raises:
        TypeError: If a note or event is unknown.
        ValueError: If a slide note has unknown pattern.
    """
    if not isinstance(event, Event):
        raise TypeError("{} is not an Event type".format(event))

    inv_note_dict = {v: k for k, v in note_dict.items()}
    measure = measure_to_ma2_time(event.measure, resolution)

    if isinstance(event, BPM):  # BPM
        template = "BPM\t{}\t{}\t{:.3f}\n"
        result = template.format(measure[0], measure[1], event.bpm)
    elif isinstance(event, Meter):  # Meter
        template = "MET\t{}\t{}\t{}\t{}\n"
        result = template.format(
            measure[0], measure[1], event.numerator, event.denominator
        )
    elif isinstance(event, TapNote):
        template = "{}\t{}\t{}\t{}\n"
        name = inv_note_dict[event.note_type.value]
        result = template.format(name, measure[0], measure[1], event.position)
    elif isinstance(event, HoldNote):
        template = "{}\t{}\t{}\t{}\t{}\n"
        name = inv_note_dict[event.note_type.value]
        duration = round(event.duration * resolution)
        result = template.format(name, measure[0], measure[1], event.position, duration)
    elif isinstance(event, SlideNote):
        template = "{}\t{}\t{}\t{}\t{}\t{}\t{}\n"
        inv_slide_dict = {v: k for k, v in slide_dict.items()}
        if event.pattern not in inv_slide_dict:
            raise ValueError("Unknown slide pattern {}".format(event.pattern))

        pattern = inv_slide_dict[event.pattern]
        delay = round(event.delay * resolution)
        duration = round(event.duration * resolution)
        result = template.format(
            pattern,
            measure[0],
            measure[1],
            event.position,
            delay,
            duration,
            event.end_position,
        )
    elif isinstance(event, TouchTapNote):
        template = "{}\t{}\t{}\t{}\t{}\t{}\t{}\n"
        name = inv_note_dict[event.note_type.value]
        fireworks = 1 if event.is_firework else 0
        result = template.format(
            name,
            measure[0],
            measure[1],
            event.position,
            event.region,
            fireworks,
            event.size,
        )
    elif isinstance(event, TouchHoldNote):
        template = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n"
        name = inv_note_dict[event.note_type.value]
        duration = round(event.duration * resolution)
        fireworks = 1 if event.is_firework else 0
        result = template.format(
            name,
            measure[0],
            measure[1],
            event.position,
            duration,
            event.region,
            fireworks,
            event.size,
        )
    else:
        raise TypeError("Unknown note type {}".format(event.note_type.value))

    return result
