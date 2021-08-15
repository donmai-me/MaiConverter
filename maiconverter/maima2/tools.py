from typing import List

from .ma2note import note_dict, slide_dict

_ignored_v1 = [
    "VERSION",
    "FES_MODE",
    "BPM_DEF",
    "MET_DEF",
    "CLK_DEF",
    "CLK",
    "COMPATIBLE_CODE",
    "T_REC_TAP",
    "T_REC_BRK",
    "T_REC_XTP",
    "T_REC_HLD",
    "T_REC_XHO",
    "T_REC_STR",
    "T_REC_BST",
    "T_REC_XST",
    "T_REC_TTP",
    "T_REC_THO",
    "T_REC_SLD",
    "T_REC_ALL",
    "T_NUM_TAP",
    "T_NUM_BRK",
    "T_NUM_HLD",
    "T_NUM_SLD",
    "T_NUM_ALL",
    "T_JUDGE_TAP",
    "T_JUDGE_HLD",
    "T_JUDGE_SLD",
    "T_JUDGE_ALL",
    "TTM_EACHPAIRS",
    "TTM_SCR_TAP",
    "TTM_SCR_BRK",
    "TTM_SCR_HLD",
    "TTM_SCR_SLD",
    "TTM_SCR_ALL",
    "TTM_SCR_S",
    "TTM_SCR_SS",
    "TTM_RAT_ACV",
]


def parse_v1(ma2, values: List[str]) -> None:
    """Ma2 line parser for versions 1.02.00 and 1.03.00 currently."""
    # For notes and events, the first value is a 3-character text
    line_type = values[0]
    # Create a list of all valid ma2 note and slide types
    if line_type in _ignored_v1:
        # Ignore some parts of the header and all summary statistics lines
        return
    if line_type == "RESOLUTION":
        # Set the max number of ticks in a measure
        ma2._resolution = int(values[1])
    elif line_type == "BPM":
        # Set the BPM for a measure
        measure = float(values[1]) + float(values[2]) / ma2.resolution
        bpm = float(values[3])
        ma2.set_bpm(measure, bpm)
    elif line_type == "MET":
        # Set MET event
        measure = float(values[1]) + float(values[2]) / ma2.resolution
        ma2.set_meter(measure, int(values[3]), int(values[4]))
    elif line_type in list(note_dict.keys()):
        _handle_notes_v1(ma2, values)
    elif line_type in list(slide_dict.keys()):
        _handle_slides_v1(ma2, values)
    else:
        print(f"Warning: Ignoring unknown line type {line_type}")


def _handle_notes_v1(ma2, values: List[str]) -> None:
    line_type = values[0]
    measure = float(values[1]) + float(values[2]) / ma2.resolution
    position = int(values[3])
    if line_type in ["TAP", "BRK", "XTP", "STR", "BST", "XST"]:
        is_break = line_type in ["BRK", "BST"]
        is_ex = line_type in ["XTP", "XST"]
        is_star = line_type in ["STR", "BST", "XST"]
        ma2.add_tap(measure, position, is_break, is_star, is_ex)
    elif line_type in ["XHO", "HLD"]:
        is_ex = line_type == "XHO"
        duration = float(values[4]) / ma2.resolution
        ma2.add_hold(measure, position, duration, is_ex)
    elif line_type == "TTP":
        region = values[4]
        is_firework = values[5] == "1"
        size = values[6] if len(values) > 6 else "M1"
        ma2.add_touch_tap(measure, position, region, is_firework, size)
    elif line_type == "THO":
        duration = float(values[4]) / ma2.resolution
        region = values[5]
        is_firework = values[6] == "1"
        size = values[7] if len(values) > 7 else "M1"
        ma2.add_touch_hold(measure, position, region, duration, is_firework, size)


def _handle_slides_v1(ma2, values: List[str]) -> None:
    line_type = values[0]
    pattern = slide_dict[line_type]
    measure = float(values[1]) + float(values[2]) / ma2.resolution
    start_position = int(values[3])
    delay = int(values[4]) / ma2.resolution
    duration = int(values[5]) / ma2.resolution
    end_position = int(values[6])
    ma2.add_slide(measure, start_position, end_position, duration, pattern, delay)
