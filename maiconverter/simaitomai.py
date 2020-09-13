import re

from .maisdt import MaiSDT
from .maisdt import MaiSDTSlideTapNote as SlideTapNote
from .maisdt import MaiSDTSlideStartNote as SlideStartNote
from .maisdt import MaiSDTSlideEndNote as SlideEndNote
from .note import Note, HoldNote


class SimaiToMaiSDT(MaiSDT):
    
    slide_dictionary = {
        # Converts simai slide pattern to corresponding SDT slide
        # pattern value. Additional steps need to be taken for
        # '^' and 'V' as they don't immediately report direction
        # Note: We ignore the second point in 'V'. Room for improvement?

        "-": 1,
        # "^" is either 2 or 3
        ">": 2,
        "<": 3,
        "p": 4,
        "q": 5,
        "s": 6,
        "z": 7,
        "v": 8,
        "pp": 9,
        "qq": 10,
        # 'V' is either 11 or 12
        "w": 13,
    }

    def __init__(self, initial_bpm = 120, divisor = 4, rest_time = 0.2500):
        super().__init__(initial_bpm)
        self.current_bpm = initial_bpm
        self.current_measure = 1.0000
        self.divisor = divisor
        self.rest_time = rest_time
        self.slide_counter = 1

    def change_bpm(self, new_bpm):
        # SDT doesn't support BPM changes so let's do some math
        # Quarter note rest_time are converted to equivalent length
        if new_bpm <= 0:
            raise ValueError("BPM must be positive.")
        self.current_bpm = new_bpm
        self.rest_time = 0.25*self.initial_bpm/self.current_bpm
        print("Changed bpm to " + str(new_bpm) + " rest time is now: " \
              + str(self.rest_time))

    def change_divisor(self, new_divisor):
        self.divisor = new_divisor

    def add_tap(self, taps):
        # Accepts list of strings from parse_tap
        for tap in taps:
            note_type = 3 if tap.find("b") != -1 else 1
            note_position = int(tap[0]) - 1
            tap_note = Note(self.current_measure, note_position, note_type)
            self.notes.append(tap_note)

    def add_hold(self, holds):
        # Accepts list of strings from parse_hold
        for hold in holds:
            note_position = int(hold[0]) - 1
            scale = self.initial_bpm/self.current_bpm
            hold_divisor = int(re.search("\[(\d+):", hold).group()[1:-1])
            hold_amount = int(re.search(":(\d+)\]", hold).group()[1:-1])
            hold_duration = scale*hold_amount/hold_divisor
            hold_note = HoldNote(self.current_measure, note_position,
                                hold_duration)
            self.notes.append(hold_note)

    def add_slide(self, slides):
        # Accepts list of strings from parse_slide
        for slide in slides:
            start_position = int(slide[0]) - 1
            start_amount = slide.count("*") + 1
            is_break = True if slide.find("b") != -1 else False

            slide_tap_note = SlideTapNote(self.current_measure,
                                          start_position,
                                          start_amount,
                                          is_break)
            self.notes.append(slide_tap_note)

            ends = slide.split("*")
            for end in ends:
                end_position = int(re.search("\d\[", end).group()[0]) - 1
                pattern_string = re.search("[-^<>vVpqszw][pq]?", slide) \
                                    .group()

                if pattern_string == "^":
                    is_CW = SimaiToMaiSDT.handle_ambiguous_slide( \
                                                start_position, end_position)
                    pattern = 3 if is_CW else 2
                elif pattern_string == "V":
                    relection_point = int(re.search("V[1-8]{2}", end)\
                                            .group()[1]) - 1
                    is_CW = SimaiToMaiSDT.handle_ambiguous_slide( \
                                                start_position, \
                                                relection_point)
                    pattern = 12 if is_CW else 11
                else:
                    pattern = self.slide_dictionary.get(pattern_string,\
                                                            None)

                scale = self.initial_bpm/self.current_bpm
                slide_divisor = int(re.search("\[(\d+):", end).group()[1:-1])
                slide_amount = int(re.search(":(\d+)\]", end).group()[1:-1])
                slide_duration = scale*slide_amount/slide_divisor

                if slide_duration*0.75 < self.rest_time:
                    rest_time = slide_duration*0.75
                else:
                    rest_time = self.rest_time

                slide_start_note = SlideStartNote(self.current_measure,
                                             start_position,
                                             self.slide_counter,
                                             pattern, slide_duration,
                                             rest_time)
                slide_end_note = SlideEndNote(self.current_measure
                                              + slide_duration, end_position,
                                              self.slide_counter,
                                              pattern)
                self.slide_counter += 1
            
                self.notes.append(slide_start_note)
                self.notes.append(slide_end_note)

    
    def next(self, amount = 1):
        # Move to the next event separated by ","
        # Provides a way to keep track of where we are in the chart
        # regardless of BPM and divisor changes
        # as .sdt files are incapable of that
        scale = self.initial_bpm/self.current_bpm
        self.current_measure += amount*scale/self.divisor

    @staticmethod
    def handle_ambiguous_slide(start_position, end_position):
        # Handles slide cases where the direction is not specified
        # Returns True for clockwise and False for counterclockwise
        diff = abs(end_position - start_position)
        other_diff = abs(8 - diff)
        if diff == 4:
            raise ValueError("Can't choose direction for a 180 degree angle.")

        if ((end_position > start_position) and (diff > other_diff)) \
            or ((end_position < start_position) and (diff < other_diff)):
            return False
        else:
            return True


    @staticmethod
    def parse_bpm(bpm_string):
        # Parse BPM change
        # Accepts strings of the form '(b)' where b is a positive number
        # greater than 0
        # Returns a float or None
        bpm = re.search("\(([0-9]+?(?:\.[0-9]+?)?)\)", bpm_string)

        if bpm is None:
            return None
        else:
            result = float(bpm.group()[1:-1])
            if not result > 0:
                raise ValueError("BPM is not a number greater than 0. "
                                + str(bpm_string))

            return result

    @staticmethod
    def parse_divisor(divisor_string):
        # Accepts strings of the form '{x}' where x is a positive number
        # greater than 0
        # Returns a float or None
        divisor = re.search("\{([0-9]+?(?:\.[0-9]+?)?)\}", divisor_string)

        if divisor is None:
            return None
        else:
            result = float(divisor.group()[1:-1])
            if not result > 0:
                raise ValueError("Divisor is not a number greater than 0. "
                                + str(divisor_string))

            return result

    @staticmethod
    def parse_tap(tap_string):
        # Accepts strings of the form 'x', 'xy', 'x/y', 'xb', 'xbyb',
        # or 'xb/yb' where x and y are integers from 1 to 8.
        # Returns list of string, or None.
        tap = re.findall("(?<!V)([1-8]b?)(?!h|-|b-|\^|b\^|<|b<|>|b>|v|bv|p"
                        + "|bp|q|bq|s|bs|z|bz|pp|bpp|qq|bqq|V\d|bV\d|w|bw"
                        + "|\[|[^({[]*[\)}\]])", tap_string)

        if (tap is None) or (len(tap) == 0):
            return None
        else:
            return tap

    @staticmethod
    def parse_hold(hold_string):
        # Accepts strings of the form 'Bh[x:y]' where B is an integer 
        # from 1 to 8, and x and y are positive non-zero integers
        # Returns list of string, or None.
        hold = re.findall("([1-8]h\[\d+:\d+\])", hold_string)

        if (hold is None) or (len(hold) == 0):
            return None
        else:
            return hold

    @staticmethod
    def parse_slide(slide_string):
        # Accepts strings of the form 'aBc[x:y]' where a and c 
        # are integers from 1 to 8, B is the slide pattern, 
        # and x and y are positive non-zero integers
        # Returns list of string, or None.
        slide = re.findall("([1-8]b?[-^<>vVpqszw][pq]?[1-8]{1,2}\[\d+:\d+\]"
                        + "(?:\*[-^<>vVpqszw][pq]?[1-8]{1,2}\[\d+:\d+\])*)",
                            slide_string)

        if (slide is None) or (len(slide) == 0):
            return None
        else:
            return slide