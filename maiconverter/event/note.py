import enum

from .event import Event, EventType

# Note types
# 0: Start slide (For SDT)
# 1: Regular Tap
# 2: Hold
# 3: Break tap
# 4: Star
# 5: Break star
# 6: Ex tap
# 7: Ex star
# 8: Ex hold
# 9: Touch tap
# 10: Touch hold
# 11: Complete slide (Both start and end slide. For ma2 and simai)
# 128: End slide (For SDT)


class NoteType(enum.Enum):
    start_slide = 0
    tap = 1
    hold = 2
    break_tap = 3
    star = 4
    break_star = 5
    ex_tap = 6
    ex_star = 7
    ex_hold = 8
    touch_tap = 9
    touch_hold = 10
    complete_slide = 11
    end_slide = 128


class Note(Event):
    def __init__(self, measure: float, position: int, note_type: NoteType) -> None:
        if position < 0:
            raise ValueError("Note position is negative " + str(position))

        super().__init__(measure, EventType.note)
        self.position = position
        self.note_type = note_type

    def __key(self):
        return (self.measure, self.event_type, self.position, self.note_type)


class MaiNote(Note):
    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        if (
            (self.note_type == 4)
            and (other.note_type == 0)
            and (self.measure == other.measure)
        ):
            return True
        elif self.measure == other.measure:
            return self.position < other.position
        else:
            return self.measure < other.measure

    def __gt__(self, other):
        if (
            (self.note_type == 4)
            and (other.note_type == 0)
            and (self.measure == other.measure)
        ):
            return False
        elif self.measure == other.measure:
            return self.position > other.position
        else:
            return self.measure > other.measure

    def __le__(self, other):
        if (
            (self.note_type == 4)
            and (other.note_type == 0)
            and (self.measure == other.measure)
        ):
            return True
        elif self.measure == other.measure:
            return self.position <= other.position
        else:
            return self.measure <= other.measure

    def __ge__(self, other):
        if (
            (self.note_type == 4)
            and (other.note_type == 0)
            and (self.measure == other.measure)
        ):
            return False
        elif self.measure == other.measure:
            return self.position >= other.position
        else:
            return self.measure >= other.measure

    def __eq__(self, other):
        if (
            (self.note_type == 4)
            and (other.note_type == 0)
            and (self.measure == other.measure)
        ):
            return False
        elif self.measure == other.measure:
            return self.position == other.position
        else:
            return self.measure == other.measure

    def __ne__(self, other):
        if (
            (self.note_type == 4)
            and (other.note_type == 0)
            and (self.measure == other.measure)
        ):
            return True
        elif self.measure == other.measure:
            return self.position != other.position
        else:
            return self.measure != other.measure


class SimaiNote(Note):
    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        if self.measure == other.measure:
            if self.note_type == other.note_type:
                return self.position < other.position
            else:
                return self.note_type < other.note_type
        else:
            return self.measure < other.measure

    def __gt__(self, other):
        if self.measure == other.measure:
            if self.note_type == other.note_type:
                return self.position > other.position
            else:
                return self.note_type > other.note_type
        else:
            return self.measure > other.measure

    def __le__(self, other):
        if self.measure == other.measure:
            if self.note_type == other.note_type:
                return self.position <= other.position
            else:
                return self.note_type <= other.note_type
        else:
            return self.measure <= other.measure

    def __ge__(self, other):
        if self.measure == other.measure:
            if self.note_type == other.note_type:
                return self.position >= other.position
            else:
                return self.note_type >= other.note_type
        else:
            return self.measure >= other.measure

    def __ne__(self, other):
        return (
            (self.measure != other.measure)
            and (self.note_type != other.note_type)
            and (self.position != other.position)
        )

    def __eq__(self, other):
        return (
            (self.measure == other.measure)
            and (self.note_type == other.note_type)
            and (self.position == other.position)
        )
