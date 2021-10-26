import math
from typing import List, Tuple, Union, Callable


def _check_bpms(bpms: List[Tuple[float, float]]):
    if len(bpms) == 0:
        raise ValueError("No BPMs given.")
    if not any([0.0 <= x[0] <= 1.0 for x in bpms]):
        raise ValueError("No starting BPM defined.")


def measure_to_second(
    measure: float,
    bpms: List[Tuple[float, float]],
    include_metronome_ticks: bool = True,
) -> float:
    _check_bpms(bpms)
    bpms.sort(key=lambda x: x[0])

    if measure < 0.0:
        return 60 * 4 * measure / bpms[0][1]

    previous_bpm = bpms[0][1]
    previous_measure = 1.0
    if include_metronome_ticks:
        previous_time = 60 * 4 * 1 / previous_bpm
    else:
        previous_time = 0.0

    for current_measure, current_bpm in bpms:
        if 0.0 <= current_measure < 1.0:
            continue

        gap_measure = current_measure - previous_measure
        gap_time = 60 * 4 * gap_measure / previous_bpm

        current_time = previous_time + gap_time
        if math.isclose(current_measure, measure, abs_tol=0.0005):
            return current_time
        if current_measure > measure:
            break

        previous_measure = current_measure
        previous_bpm = current_bpm
        previous_time = current_time

    gap_measure = measure - previous_measure
    gap_time = 60 * 4 * gap_measure / previous_bpm

    return previous_time + gap_time


def second_to_measure(
    seconds: float,
    bpms: List[Tuple[float, float]],
    include_metronome_ticks: bool = True,
) -> float:
    _check_bpms(bpms)
    bpms.sort(key=lambda x: x[0])

    if seconds < 0.0:
        return seconds * bpms[0][1] / (60 * 4)

    previous_bpm = bpms[0][1]
    previous_measure = 1.0
    if include_metronome_ticks:
        metronome_ticks_duration = 60 * 4 * 1 / previous_bpm

        if seconds < metronome_ticks_duration or math.isclose(
            seconds, metronome_ticks_duration, abs_tol=0.0001
        ):
            return seconds / metronome_ticks_duration

        previous_time = metronome_ticks_duration
    else:
        previous_time = 0.0

    for current_measure, current_bpm in bpms:
        if 0.0 <= current_measure < 1.0:
            continue

        gap_measure = current_measure - previous_measure
        # Time (in seconds) = 60 seconds per minute * measure * beats per measure / BPM
        gap_time = 60 * gap_measure * 4 / previous_bpm
        current_time = previous_time + gap_time

        if math.isclose(current_time, seconds, abs_tol=0.0005):
            return current_measure
        if current_time > seconds:
            break

        previous_measure = current_measure
        previous_time = current_time
        previous_bpm = current_bpm

    gap_time = seconds - previous_time
    gap_measure = gap_time * previous_bpm / (60 * 4)

    return previous_measure + gap_measure


def offset_arg_to_measure(
    offset: Union[float, str], sec_to_measure: Callable[[float], float]
) -> float:
    if isinstance(offset, float):
        offset = offset
    elif isinstance(offset, str) and offset[-1].lower() == "s":
        offset = sec_to_measure(float(offset[:-1]))
    elif isinstance(offset, str) and "/" in offset:
        fraction = offset.split("/")
        if len(fraction) != 2:
            raise ValueError(f"Invalid fraction: {offset}")

        offset = int(fraction[0]) / int(fraction[1])
    else:
        offset = float(offset)

    return offset


def quantise(measure: float, grid: int) -> float:
    if grid <= 0:
        raise ValueError(f"Quantisation is not positive: {grid}")

    return round(grid * measure) / grid
