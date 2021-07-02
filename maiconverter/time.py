def second_to_measure(seconds: float, bpm: float, beats_per_bar: int = 4) -> float:
    beats = bpm * seconds / 60
    return beats / beats_per_bar


def measure_to_second(measure: float, bpm: float, beats_per_bar: int = 4) -> float:
    beats = measure * beats_per_bar
    return 60 * beats / bpm
