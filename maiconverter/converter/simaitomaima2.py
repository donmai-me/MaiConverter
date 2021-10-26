from typing import List

from ..maima2 import MaiMa2
from ..simai import (
    SimaiChart,
    pattern_to_int,
    TapNote,
    HoldNote,
    SlideNote,
    TouchHoldNote,
    TouchTapNote,
)
from ..event import SimaiNote, NoteType


def simai_to_ma2(simai: SimaiChart, fes_mode: bool = False) -> MaiMa2:
    ma2 = MaiMa2(fes_mode=fes_mode)

    for bpm in simai.bpms:
        ma2.set_bpm(bpm.measure, bpm.bpm)

    ma2.set_meter(0.0, 4, 4)
    convert_notes(ma2, simai.notes)
    return ma2


def convert_notes(ma2: MaiMa2, simai_notes: List[SimaiNote]) -> None:
    for simai_note in simai_notes:
        note_type = simai_note.note_type
        if isinstance(simai_note, TapNote):
            is_break = note_type in [NoteType.break_tap, NoteType.break_star]
            is_ex = note_type in [NoteType.ex_tap, NoteType.ex_star]
            is_star = note_type in [
                NoteType.star,
                NoteType.break_star,
                NoteType.ex_star,
            ]
            ma2.add_tap(
                measure=simai_note.measure,
                position=simai_note.position,
                is_break=is_break,
                is_star=is_star,
                is_ex=is_ex,
            )
        elif isinstance(simai_note, HoldNote):
            is_ex = note_type == NoteType.ex_hold
            ma2.add_hold(
                measure=simai_note.measure,
                position=simai_note.position,
                duration=simai_note.duration,
                is_ex=is_ex,
            )
        elif isinstance(simai_note, SlideNote):
            # Ma2 slide durations does not include the delay
            # like in simai
            pattern = pattern_to_int(simai_note)
            ma2.add_slide(
                measure=simai_note.measure,
                start_position=simai_note.position,
                end_position=simai_note.end_position,
                duration=simai_note.duration,
                pattern=pattern,
                delay=simai_note.delay,
            )
        elif isinstance(simai_note, TouchTapNote):
            ma2.add_touch_tap(
                measure=simai_note.measure,
                position=simai_note.position,
                region=simai_note.region,
                is_firework=simai_note.is_firework,
            )
        elif isinstance(simai_note, TouchHoldNote):
            ma2.add_touch_hold(
                measure=simai_note.measure,
                position=simai_note.position,
                region=simai_note.region,
                duration=simai_note.duration,
                is_firework=simai_note.is_firework,
            )
        else:
            print(f"Warning: Unknown note type {note_type}")
