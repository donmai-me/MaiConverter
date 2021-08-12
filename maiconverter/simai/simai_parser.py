from typing import List
from lark import Lark, Transformer


class SimaiTransformer(Transformer):
    def title(self, n):
        n = n[0]
        return {"type": "title", "value": n.rstrip()}

    def artist(self, n):
        n = n[0]
        return {"type": "artist", "value": n.rstrip()}

    def smsg(self, n):
        pass

    def des(self, n):
        pass

    def freemsg(self, n):
        pass

    def first(self, n):
        pass

    def pvstart(self, n):
        pass

    def pvend(self, n):
        pass

    def wholebpm(self, n):
        pass

    def level(self, n):
        num, level = n
        return {"type": "level", "value": (int(num), level.rstrip())}

    def chart(self, n):
        num, raw_chart = n
        chart = ""
        for x in raw_chart.splitlines():
            if "||" not in x:
                chart += x

        chart = "".join(chart.split())
        return {"type": "chart", "value": (int(num), chart)}

    def amsg_first(self, n):
        pass

    def amsg_time(self, n):
        pass

    def amsg_content(self, n):
        pass

    def demo_seek(self, n):
        pass

    def demo_len(self, n):
        pass

    def chain(self, values):
        result = []
        for value in values:
            if isinstance(value, dict):
                result.append(value)

        return result


class FragmentTransformer(Transformer):
    def bpm(self, n) -> dict:
        (n,) = n
        event_dict = {
            "type": "bpm",
            "value": float(n),
        }
        return event_dict

    def divisor(self, n) -> dict:
        (n,) = n
        if float(n) == 0:
            raise ValueError("Divisor is 0.")

        event_dict = {
            "type": "divisor",
            "value": float(n),
        }
        return event_dict

    def equivalent_bpm(self, n) -> dict:
        if len(n) == 0:
            return {"type": "equivalent_bpm", "value": None}

        (n,) = n
        return {"type": "equivalent_bpm", "value": float(n)}

    def duration(self, items) -> dict:
        # Set defaults
        equivalent_bpm = None
        den = None
        num = None

        for item in items:
            if isinstance(item, str) and item.type == "INT" and den is None:
                den = int(item)
                if den <= 0:
                    return {
                        "type": "duration",
                        "equivalent_bpm": equivalent_bpm,
                        "duration": 0,
                    }
            elif isinstance(item, str) and item.type == "INT" and num is None:
                num = int(item)
            elif isinstance(item, str) and item[-1] == "#":
                equivalent_bpm = float(item[:-1])

        if den is None or num is None:
            raise ValueError("No denominator or numerator given")

        return {
            "type": "duration",
            "equivalent_bpm": equivalent_bpm,
            "duration": num / den,
        }

    def slide_beg(self, items) -> dict:
        text = items[0]
        start = int(text[0]) - 1
        text = text[1:]

        modifier = ""
        for i, char in enumerate(text):
            if char in "b@x?$!":
                modifier += char
            else:
                text = text[i:]
                break

        reflect = None

        if text[0] not in "-^<>szvwpqV":
            raise ValueError(f"Unknown slide pattern {text[0]}")

        pattern = text[0]
        if text[0] in "-^<>szvw":
            text = text[1:]
        elif text[0] in "pq" and text[1] in "pq":
            pattern += text[1]
            text = text[2:]
        elif text[0] in "pq" and text[1] not in "pq":
            text = text[1:]
        else:  # V slide
            reflect = int(text[1]) - 1
            text = text[2:]

        end = int(text[0]) - 1

        return {
            "type": "slide_beg",
            "start": start,
            "modifier": modifier,
            "pattern": pattern,
            "reflect": reflect,
            "end": end,
        }

    def chained_slide_note(self, items) -> dict:
        (
            text,
            duration_dict,
        ) = items

        # Skip the modifiers in a chained slide
        for i, char in enumerate(text):
            if char not in "b@x?$!":
                text = text[i:]
                break

        pattern = text[0]
        reflect = None
        if text[0] in "-^<>szvw":
            text = text[1:]
        elif text[0] in "pq" and text[1] in "pq":
            pattern += text[1]
            text = text[2:]
        elif text[0] in "pq" and text[1] not in "pq":
            text = text[1:]
        else:  # V slide
            reflect = int(text[1]) - 1
            text = text[2:]

        end = int(text[0]) - 1

        if not isinstance(duration_dict, dict):
            raise ValueError(f"Not a dict: {duration_dict}")

        duration = duration_dict["duration"]
        equivalent_bpm = duration_dict["equivalent_bpm"]

        return {
            "type": "chained_slide_note",
            "pattern": pattern,
            "reflect": reflect,
            "end": end,
            "equivalent_bpm": equivalent_bpm,
            "duration": duration,
        }

    def slide_note(self, items):
        start = None
        end = None
        modifier = ""
        pattern = None
        reflect = None
        equivalent_bpm = None
        duration = None
        chained_slides = []

        for item in items:
            if isinstance(item, dict) and item["type"] == "slide_beg":
                if item["start"] == -1 or item["reflect"] == -1 or item["end"] == -1:
                    return

                start = item["start"]
                modifier = item["modifier"]
                pattern = item["pattern"]
                end = item["end"]
                reflect = item["reflect"]
            elif isinstance(item, dict) and item["type"] == "duration":
                equivalent_bpm = item["equivalent_bpm"]
                duration = item["duration"]
            elif isinstance(item, dict) and item["type"] == "chained_slide_note":
                chained_slides.append(item)
            else:
                raise ValueError(f"Unknown value: {item}")

        if any((c is None) for c in [start, end, pattern, duration]):
            raise ValueError("Incomplete data")

        slides = []
        if start != -1 and end != -1 and reflect != -1:
            note_dict = {
                "type": "slide",
                "start_button": start,
                "modifier": modifier,
                "pattern": pattern,
                "reflect_position": reflect,
                "end_button": end,
                "duration": duration,
                "equivalent_bpm": equivalent_bpm,
            }
            slides.append(note_dict)

        if len(chained_slides) != 0:
            slides += process_chained_slides(start, modifier + "*", chained_slides)

        if len(slides) > 0:
            return slides

    def tap_hold_note(self, items):
        if len(items) == 2:
            (
                text,
                duration_dict,
            ) = items
        else:
            (text,) = items
            duration_dict = None

        button = int(text[0]) - 1
        text = text[1:]
        if button == -1:
            # Ignore simai notes that has button position 0
            return

        is_tap = True
        if "h" in text:
            is_tap = False

        modifier = ""
        for char in text:
            if char == "h":
                continue

            if is_tap and char in "bx$":
                modifier += char
            elif not is_tap and char in "x":
                modifier += char

        if not is_tap:
            if duration_dict is None:
                duration = 0
            else:
                duration = duration_dict["duration"]

            return {
                "type": "hold",
                "button": button,
                "modifier": modifier,
                "duration": duration,
            }

        return {
            "type": "tap",
            "button": button,
            "modifier": modifier,
        }

    def touch_tap_hold_note(self, items):
        if len(items) == 2:
            (
                text,
                duration_dict,
            ) = items
        else:
            (text,) = items
            duration_dict = None

        region = text[0]
        if len(text) > 1 and text[1] in "012345678":
            position = int(text[1]) - 1
            text = text[2:]
        else:
            position = 0
            text = text[1:]

        if region not in "CBE" or position == -1:
            return

        is_tap = True
        if "h" in text:
            is_tap = False

        modifier = ""
        for char in text:
            if char == "h":
                continue

            if char in "f":
                modifier += char

        if not is_tap:
            if duration_dict is None:
                duration = 0
            else:
                duration = duration_dict["duration"]

            return {
                "type": "touch_hold",
                "region": region,
                "location": position,
                "modifier": modifier,
                "duration": duration,
            }

        return {
            "type": "touch_tap",
            "region": region,
            "location": position,
            "modifier": modifier,
        }

    def pseudo_each(self, items):
        (item,) = items
        if isinstance(item, list):
            notes = item
        elif isinstance(item, dict):
            notes = [item]
        else:
            raise TypeError(f"Invalid type: {type(item)}")

        for note in notes:
            note["modifier"] += "`"

        return notes

    def chain(self, items) -> list:
        result = []
        # Flatten list
        for item in items:
            if isinstance(item, list):
                for subitem in item:
                    result.append(subitem)
            elif isinstance(item, dict):
                result.append(item)
        return result


def process_chained_slides(start_button, slide_modifier, chained_slides):
    complete_slides = []
    for slide in chained_slides:
        if start_button == -1 or slide["reflect"] == -1 or slide["end"] == -1:
            continue

        note_dict = {
            "type": "slide",
            "start_button": start_button,
            "modifier": slide_modifier,
            "pattern": slide["pattern"],
            "reflect_position": slide["reflect"],
            "end_button": slide["end"],
            "duration": slide["duration"],
            "equivalent_bpm": slide["equivalent_bpm"],
        }
        complete_slides.append(note_dict)

    return complete_slides


def parse_fragment(fragment: str, lark_file: str = "simai_fragment.lark") -> List[dict]:
    parser = Lark.open(lark_file, rel_to=__file__, parser="lalr")
    try:
        return FragmentTransformer().transform(parser.parse(fragment))
    except Exception:
        print(f"Error parsing {fragment}")
        raise
