from typing import Union, Callable, Sequence
import copy

from ..event import MaiNote, NoteType
from ..maisxt import (
    MaiSxt,
    HoldNote as SDTHoldNote,
    SlideStartNote as SDTSlideStartNote,
)
from ..maima2 import MaiMa2, TapNote, HoldNote, SlideNote, TouchTapNote, TouchHoldNote

ma2_slide_dict = {
    "SI_": 1,
    "SCL": 2,
    "SCR": 3,
    "SUL": 4,
    "SUR": 5,
    "SSL": 6,
    "SSR": 7,
    "SV_": 8,
    "SXL": 9,
    "SXR": 10,
    "SLL": 11,
    "SLR": 12,
    "SF_": 13,
}


def _default_touch_converter(
    sdt: MaiSxt, touch_note: Union[TouchTapNote, TouchHoldNote]
) -> None:
    if isinstance(touch_note, TouchTapNote) and touch_note.region == "C":
        sdt.add_tap(measure=touch_note.measure, position=0)
    elif isinstance(touch_note, TouchTapNote):
        sdt.add_tap(
            measure=touch_note.measure, position=touch_note.position
        )
    elif isinstance(touch_note, TouchHoldNote) and touch_note.region == "C":
        sdt.add_hold(
            measure=touch_note.measure,
            position=0,
            duration=touch_note.duration,
        )


def ma2_to_sdt(
    ma2: MaiMa2,
    touch_converter: Callable[
        [MaiSxt, Union[TouchTapNote, TouchHoldNote]], None
    ] = _default_touch_converter,
    convert_touch: bool = False,
) -> MaiSxt:
    initial_bpm = ma2.get_bpm(0)
    sdt = MaiSxt(bpm=initial_bpm)
    convert_notes(sdt, ma2.notes, touch_converter, convert_touch)
    sdt.notes.sort()

    equivalent_notes = []
    for note in sdt.notes:
        current_measure = note.measure
        current_time = ma2.measure_to_second(current_measure)
        scale = sdt.bpm / ma2.get_bpm(current_measure)

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
    sdt: MaiSxt,
    ma2_notes: Sequence[MaiNote],
    touch_converter: Callable[[MaiSxt, Union[TouchTapNote, TouchHoldNote]], None],
    convert_touch: bool,
) -> None:
    skipped_notes = 0
    for ma2_note in ma2_notes:
        note_type = ma2_note.note_type
        if isinstance(ma2_note, TapNote):
            is_break = note_type in [NoteType.break_tap, NoteType.break_tap]
            is_star = note_type in [NoteType.star, NoteType.break_star]
            sdt.add_tap(
                measure=ma2_note.measure,
                position=ma2_note.position,
                is_break=is_break,
                is_star=is_star,
            )
        elif isinstance(ma2_note, HoldNote):
            # Hold, and ex hold
            sdt.add_hold(
                measure=ma2_note.measure,
                position=ma2_note.position,
                duration=ma2_note.duration,
            )
        elif isinstance(ma2_note, SlideNote):
            # Complete slide
            # SDT slide durations include the delay unlike in ma2
            sdt.add_slide(
                measure=ma2_note.measure,
                start_position=ma2_note.position,
                end_position=ma2_note.end_position,
                duration=ma2_note.duration + ma2_note.delay,
                pattern=ma2_note.pattern,
                delay=ma2_note.delay,
            )
        elif isinstance(ma2_note, (TouchTapNote, TouchHoldNote)):
            # Touch tap, and touch hold
            if convert_touch:
                touch_converter(sdt, ma2_note)
            else:
                skipped_notes += 1
        else:
            print("Warning: Unknown note type {}".format(note_type))

    if skipped_notes > 0:
        print("Skipped {} touch note(s)".format(skipped_notes))
