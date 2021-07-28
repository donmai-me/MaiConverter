import enum


class EventType(enum.Enum):
    note = 0
    bpm = 1
    meter = 2


class Event:
    def __init__(self, measure: float, event_type: EventType) -> None:
        if measure < 0:
            raise ValueError("Measure is negative " + str(measure))

        self.measure = round(measure * 10000) / 10000
        self.event_type = event_type
