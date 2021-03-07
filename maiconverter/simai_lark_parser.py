from lark import Lark, Transformer


class SimaiTransformer(Transformer):
    def bpm(self, n):
        (n,) = n
        event_dict = {
            "event_type": "bpm",
            "value": float(n),
        }
        return event_dict

    def divisor(self, n):
        (n,) = n
        event_dict = {
            "event_type": "divisor",
            "value": int(n),
        }
        return event_dict

    def button(self, n):
        (n,) = n
        # We start at 0
        return int(n) - 1

    def equivalent_bpm(self, n):
        if len(n) == 0:
            return None
        else:
            (n,) = n
            return float(n)

    def duration(self, items):
        (
            equivalent_bpm,
            den,
            num,
        ) = items

        return (float(num) / float(den), equivalent_bpm)

    def slide_modifier(self, item):
        if len(item) == 0:
            return None
        else:
            (item,) = item
            (item,) = item
            return item

    def tap_modifier(self, items):
        if len(items) == 0:
            return None
        else:
            result = ""
            for item in items:
                result += item
            return result

    def slide_pattern_literal(self, s):
        (s,) = s
        return (s, None)

    def slide_pattern_v(self, items):
        (
            s,
            reflect_position,
        ) = items
        (s,) = s
        return (s, int(reflect_position))

    def slide_pattern(self, items):
        (items,) = items
        (
            pattern_string,
            reflect_position,
        ) = items
        return (pattern_string, reflect_position)

    def chained_slides(self, items):
        if len(items) == 0:
            return None
        else:
            return list(items)

    def touch_location(self, s):
        (s,) = s
        s = s[0]
        return s

    def slide_note(self, items):
        start_button = items[0]
        slide_modifier = items[1]
        if not items[5] is None:
            slides = process_chained_slides(start_button, slide_modifier, items[5])
        else:
            slides = []

        note_dict = {
            "event_type": "slide",
            "start_button": start_button,
            "modifier": slide_modifier,
            "pattern": items[2][0],
            "reflect_position": items[2][1],
            "end_button": items[3],
            "duration": items[4][0],
            "equivalent_bpm": items[4][1],
        }

        slides.append(note_dict)
        return slides

    def tap_note(self, items):
        note_dict = {
            "event_type": "tap",
            "button": items[0],
            "modifier": items[1],
        }
        return note_dict

    def hold_note(self, items):
        note_dict = {
            "event_type": "hold",
            "button": items[0],
            "modifier": items[1],
            "duration": items[2][0],
        }
        return note_dict

    def touch_tap_note(self, items):
        note_dict = {
            "event_type": "touch_tap",
            "location": items[0],
            "modifier": items[1],
        }
        return note_dict

    def touch_hold_note(self, items):
        note_dict = {
            "event_type": "touch_hold",
            "location": items[0],
            "modifier": items[1],
            "duration": items[2][0],
        }
        return note_dict

    def chain(self, items):
        result = []
        # Flatten list of slides
        for item in items:
            if isinstance(item, list):
                for subitem in item:
                    result.append(subitem)
            elif isinstance(item, dict):
                result.append(item)
            else:
                raise Exception("Not a dict: " + str(item))
        return result

    chained_slide_note = chained_slides
    hold_modifier = slide_modifier
    touch_modifier = slide_modifier


def process_chained_slides(start_button, slide_modifier, chained_slides):
    complete_slides = []
    for chained_slide in chained_slides:
        (slide_pattern, slide_reflect_position) = chained_slide[0]
        note_dict = {
            "event_type": "slide",
            "start_button": start_button,
            "modifier": slide_modifier,
            "pattern": slide_pattern,
            "reflect_position": slide_reflect_position,
            "end_button": chained_slide[1],
            "duration": chained_slide[2][0],
            "equivalent_bpm": chained_slide[2][1],
        }
        complete_slides.append(note_dict)

    return complete_slides


def simai_parse_fragment(fragment: str, lark_file: str = "simai_fragment.lark"):
    parser = Lark.open(lark_file, rel_to=__file__)
    return SimaiTransformer().transform(parser.parse(fragment))
