class Note():
    def __init__(self, measure, position, note_type):
        if ((not type(measure) is int) and (not type(measure) is float)) \
            or (measure < 0):
            raise TypeError("Note measure is not a number or is negative. "
                            + str(measure))

        if (not type(position) is int) or (position < 0):
            raise TypeError("Note position is not an int or is negative. "
                            + str(position))

        if (not type(note_type) is int) or (note_type < 0):
            raise TypeError("Note type is not an int or is negative. "
                            + str(note_type))

        self.measure = measure
        self.position = position
        self.note_type = note_type

    # For sorting notes. Only ever used in SDT files
    def __lt__(self, other):
        if (self.note_type == 4) and (other.note_type == 0) \
                and (self.measure == other.measure):
            return True
        elif self.measure == other.measure:
            return self.position < other.position
        else: 
            return self.measure < other.measure

    def __gt__(self, other):
        if (self.note_type == 4) and (other.note_type == 0) \
                and (self.measure == other.measure):
            return False
        elif self.measure == other.measure:
            return self.position > other.position
        else: 
            return self.measure > other.measure

    def __le__(self, other):
        if (self.note_type == 4) and (other.note_type == 0) \
                and (self.measure == other.measure):
            return True
        elif self.measure == other.measure:
            return self.position <= other.position
        else: 
            return self.measure <= other.measure

    def __ge__(self, other):
        if (self.note_type == 4) and (other.note_type == 0) \
                and (self.measure == other.measure):
            return False
        elif self.measure == other.measure:
            return self.position >= other.position
        else: 
            return self.measure >= other.measure

    def __eq__(self, other):
        if (self.note_type == 4) and (other.note_type == 0) \
                and (self.measure == other.measure):
            return False
        elif self.measure == other.measure:
            return self.position == other.position
        else: 
            return self.measure == other.measure

    def __ne__(self, other):
        if (self.note_type == 4) and (other.note_type == 0) \
                and (self.measure == other.measure):
            return True
        elif self.measure == other.measure:
            return self.position != other.position
        else: 
            return self.measure != other.measure


class HoldNote(Note):
    def __init__(self, measure, position, duration):
        super().__init__(measure, position, 2)
        self.duration = duration

# Implement the rest since it's mostly format dependent