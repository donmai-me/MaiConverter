from typing import Sequence

from ..simai import (
    SimaiChart,
    pattern_from_int,
)
from ..maima2 import MaiMa2, TapNote, HoldNote, SlideNote, TouchTapNote, TouchHoldNote
from ..event import MaiNote, NoteType


def ma2_to_simai(ma2: MaiMa2) -> SimaiChart:
    simai_chart = SimaiChart()

    for bpm in ma2.bpms:
        simai_chart.set_bpm(bpm.measure, bpm.bpm)

    convert_notes(simai_chart, ma2.notes)

    return simai_chart


def convert_notes(simai_chart: SimaiChart, ma2_notes: Sequence[MaiNote]) -> None:
    for ma2_note in ma2_notes:
        note_type = ma2_note.note_type
        if isinstance(ma2_note, TapNote):
            is_break = note_type in [NoteType.break_tap, NoteType.break_star]
            is_ex = note_type in [NoteType.ex_tap, NoteType.ex_star]
            is_star = note_type in [
                NoteType.star,
                NoteType.break_star,
                NoteType.ex_star,
            ]
            simai_chart.add_tap(
                measure=ma2_note.measure,
                position=ma2_note.position,
                is_break=is_break,
                is_star=is_star,
                is_ex=is_ex,
            )
        elif isinstance(ma2_note, HoldNote):
            is_ex = note_type == NoteType.ex_hold
            simai_chart.add_hold(
                measure=ma2_note.measure,
                position=ma2_note.position,
                duration=ma2_note.duration,
                is_ex=is_ex,
            )
        elif isinstance(ma2_note, SlideNote):
            # Ma2 slide durations does not include the delay
            # like in simai
            pattern = pattern_from_int(
                ma2_note.pattern, ma2_note.position, ma2_note.end_position
            )
            simai_chart.add_slide(
                measure=ma2_note.measure,
                start_position=ma2_note.position,
                end_position=ma2_note.end_position,
                duration=ma2_note.duration,
                pattern=pattern[0],
                delay=ma2_note.delay,
                reflect_position=pattern[1],
            )
        elif isinstance(ma2_note, TouchTapNote):
            simai_chart.add_touch_tap(
                measure=ma2_note.measure,
                position=ma2_note.position,
                region=ma2_note.region,
                is_firework=ma2_note.is_firework,
            )
        elif isinstance(ma2_note, TouchHoldNote):
            simai_chart.add_touch_hold(
                measure=ma2_note.measure,
                position=ma2_note.position,
                region=ma2_note.region,
                duration=ma2_note.duration,
                is_firework=ma2_note.is_firework,
            )
        else:
            print("Warning: Unknown note type {}".format(note_type))
