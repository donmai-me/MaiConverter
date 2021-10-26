import copy
from typing import Union, Callable, List

from ..event import SimaiNote, NoteType
from ..maisxt import (
    MaiSxt,
    HoldNote as SDTHoldNote,
    SlideStartNote as SDTSlideStartNote,
)
from ..simai import (
    SimaiChart,
    pattern_to_int,
    TapNote,
    HoldNote,
    SlideNote,
    TouchHoldNote,
    TouchTapNote,
)


def _default_touch_converter(
    sxt: MaiSxt, touch_note: Union[TouchTapNote, TouchHoldNote]
) -> None:
    if isinstance(touch_note, TouchTapNote) and touch_note.region == "C":
        sxt.add_tap(measure=touch_note.measure, position=0)
    elif isinstance(touch_note, TouchTapNote):
        sxt.add_tap(
            measure=touch_note.measure,
            position=touch_note.position,
        )
    elif isinstance(touch_note, TouchHoldNote) and touch_note.region == "C":
        sxt.add_hold(
            measure=touch_note.measure,
            position=0,
            duration=touch_note.duration,
        )


def simai_to_sdt(
    simai: SimaiChart,
    touch_converter: Callable[
        [MaiSxt, Union[TouchHoldNote, TouchTapNote]], None
    ] = _default_touch_converter,
    convert_touch: bool = False,
) -> MaiSxt:
    initial_bpm = simai.get_bpm(1.0)
    sdt = MaiSxt(initial_bpm)
    convert_notes(sdt, simai.notes, touch_converter, convert_touch)
    sdt.notes.sort()

    equivalent_notes = []
    for note in sdt.notes:
        current_measure = note.measure
        current_time = simai.measure_to_second(current_measure)
        scale = sdt.bpm / simai.get_bpm(current_measure)

        note = copy.deepcopy(note)
        note.measure = sdt.second_to_measure(current_time)

        if isinstance(note, SDTHoldNote):
            note.duration = note.duration * scale
        elif isinstance(note, SDTSlideStartNote):
            note.duration = note.duration * scale
            note.delay = note.delay * scale

        equivalent_notes.append(note)

    sdt.notes = equivalent_notes
    return sdt


def convert_notes(
    sxt: MaiSxt,
    simai_notes: List[SimaiNote],
    touch_converter: Callable[[MaiSxt, Union[TouchHoldNote, TouchTapNote]], None],
    convert_touch: bool,
) -> None:
    skipped_notes = 0
    for simai_note in simai_notes:
        note_type = simai_note.note_type
        if isinstance(simai_note, TapNote):
            is_break = note_type in [NoteType.break_tap, NoteType.break_star]
            is_star = note_type in [NoteType.star, NoteType.break_star]
            sxt.add_tap(
                measure=simai_note.measure,
                position=simai_note.position,
                is_break=is_break,
                is_star=is_star,
            )
        elif isinstance(simai_note, HoldNote):
            sxt.add_hold(
                measure=simai_note.measure,
                position=simai_note.position,
                duration=simai_note.duration,
            )
        elif isinstance(simai_note, SlideNote):
            # SDT slide duration include the delay
            # unlike in simai
            pattern = pattern_to_int(simai_note)
            sxt.add_slide(
                measure=simai_note.measure,
                start_position=simai_note.position,
                end_position=simai_note.end_position,
                duration=simai_note.duration + simai_note.delay,
                pattern=pattern,
                delay=simai_note.delay,
            )
        elif isinstance(simai_note, (TouchTapNote, TouchHoldNote)):
            # Touch tap and touch hold
            if convert_touch:
                touch_converter(sxt, simai_note)
            else:
                skipped_notes += 1
        else:
            print(f"Warning: Unknown note type {note_type}")

    if skipped_notes > 0:
        print(f"Skipped {skipped_notes} touch note(s)")
