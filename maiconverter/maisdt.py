import math
from .note import Note

#Implementing additional note types
class MaiSDTSlideTapNote(Note):
    def __init__(self, measure, position, amount, break_note = False):
        if (not type(amount) is int) or (amount < 0):
            raise TypeError("Slide tap note amount is not an int or \
                            is negative. " + str(amount))

        if (not type(break_note) is bool):
            raise TypeError("Slide tap note break_note is not a bool. "
                            + str(break_note))

        if break_note:
            super().__init__(measure, position, 5)
        else:
            super().__init__(measure, position, 4)
        self.amount = amount


class MaiSDTSlideStartNote(Note):
    def __init__(self, measure, position, slide_id, pattern, \
                 duration, rest_time = 0.25):
        if (not type(slide_id) is int) or (slide_id < 0):
            raise TypeError("Slide start note slide_id is not an int"
                            + " or is negative. " + str(slide_id))

        if (not type(pattern) is int) or (pattern < 0):
            raise TypeError("Slide start note pattern is not an int"
                            + " or is negative. " + str(pattern))

        if ((not type(duration) is int) \
                and (not type(duration) is float)) \
                or (duration < 0):
            raise TypeError("Slide start note duration is not a number"
                            + " or is negative. " + str(duration))

        if ((not type(rest_time) is int) and (not type(rest_time) is float)) \
                or (rest_time < 0):
            raise TypeError("Slide start note rest_time is not a number"
                            + " or is negative. " + str(rest_time))

        super().__init__(measure, position, 0)
        self.slide_id = slide_id
        self.pattern = pattern
        self.rest_time = rest_time
        self.duration = duration


class MaiSDTSlideEndNote(Note):
    def __init__(self, measure, position, slide_id, pattern):
        if (not type(slide_id) is int) or (slide_id < 0):
            raise TypeError("Slide end note slide_id is not an int"
                            + " or is negative. " + str(slide_id))

        if (not type(pattern) is int) or (pattern < 0):
            raise TypeError("Slide end note pattern is not an int"
                            + " or is negative. " + str(pattern))

        super().__init__(measure, position, 128)
        self.slide_id = slide_id
        self.pattern = pattern

class MaiSDT():
    def __init__(self, initial_bpm = 120):
        self.initial_bpm = initial_bpm
        self.notes = []

    @staticmethod
    def convert_to_line(note):
        measure = math.modf(note.measure)

        if (note.note_type == 2 or note.note_type == 0):
            note_duration = note.duration
        elif note.note_type == 128:
            note_duration = 0
        else: 
            note_duration = 0.062500

        if (note.note_type == 0 or note.note_type == 128):
            slide_id = note.slide_id
            pattern = note.pattern
        else:
            slide_id = 0
            pattern = 0
        
        if (note.note_type == 4 or note.note_type == 5):
            slide_amount = note.amount
        else:
            slide_amount = 0

        rest_time = 0 if note.note_type != 0 else note.rest_time

        line_template = "{:.4f}, {:.4f}, {:.4f}, {:2d}, {:3d}, {:3d}," \
                        + " {:2d}, {:2d}, {:.4f},\n"
        result = line_template.format(measure[1], measure[0], note_duration,
                                     note.position, note.note_type, slide_id,
                                     pattern, slide_amount, rest_time)
        return result

    def export(self):
        self.notes.sort()
        result = ""
        for note in self.notes:
            result += MaiSDT.convert_to_line(note)

        return result