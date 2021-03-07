from typing import Union, Callable, List
import copy

from .note import SimaiNote, MaiNote, NoteType
from .maisdt import MaiSDTSlideStartNote as SlideStartNote
from .maisdt import MaiSDTHoldNote as HoldNote
from .simai import simai_pattern_to_int, SimaiChart
from .simai import SimaiTouchTapNote as TouchTapNote
from .simai import SimaiTouchHoldNote as TouchHoldNote
from .maisdt import MaiSDT


def default_touch_converter(
    sdt: MaiSDT, touch_note: Union[TouchTapNote, TouchHoldNote]
) -> None:
    if touch_note.note_type == NoteType.touch_tap and touch_note.zone == "C":
        sdt.add_tap(touch_note.measure, 0, False)
    elif touch_note.note_type == NoteType.touch_tap:
        sdt.add_tap(touch_note.measure, touch_note.position, False)
    elif touch_note.note_type == NoteType.touch_hold and touch_note.zone == "C":
        sdt.add_hold(touch_note.measure, 0, touch_note.duration)


def simai_to_sdt(
    simai: SimaiChart,
    touch_converter: Callable[
        [MaiSDT, Union[TouchHoldNote, TouchTapNote]], None
    ] = default_touch_converter,
    convert_touch: bool = False,
) -> MaiSDT:
    sdt = MaiSDT()
    convert_notes(sdt, simai.notes, touch_converter, convert_touch)
    sdt.notes.sort()

    event_list = [note for note in sdt.notes]
    for bpm in simai.bpms:
        event_list.append(bpm)

    event_list.sort(key=lambda event: event.measure)
    previous_measure = 1
    equivalent_current_measure = 1
    equivalent_notes = []
    initial_bpm = simai.get_bpm(1)
    for event in event_list:
        current_measure = event.measure
        current_bpm = simai.get_bpm(current_measure)
        gap = current_measure - previous_measure
        scale = initial_bpm / current_bpm
        equivalent_gap = gap * scale
        equivalent_current_measure += equivalent_gap

        previous_measure = current_measure
        if not isinstance(event, MaiNote):
            continue

        note = copy.deepcopy(event)
        note.measure = equivalent_current_measure

        if isinstance(note, HoldNote):
            note.duration = note.duration * scale
        elif isinstance(note, SlideStartNote):
            note.duration = note.duration * scale
            note.delay = note.delay * scale

        equivalent_notes.append(note)

    sdt.notes = equivalent_notes
    return sdt


def convert_notes(
    sdt: MaiSDT,
    simai_notes: List[SimaiNote],
    touch_converter: Callable[[MaiSDT, Union[TouchHoldNote, TouchTapNote]], None],
    convert_touch: bool,
) -> None:
    slide_counter = 1
    skipped_notes = 0
    for simai_note in simai_notes:
        note_type = simai_note.note_type
        if note_type in [NoteType.tap, NoteType.break_tap, NoteType.ex_tap]:
            is_break = True if note_type == NoteType.break_tap else False
            sdt.add_tap(simai_note.measure, simai_note.position, is_break)
        elif note_type in [NoteType.hold, NoteType.ex_hold]:
            sdt.add_hold(simai_note.measure, simai_note.position, simai_note.duration)
        elif note_type in [NoteType.star, NoteType.break_star, NoteType.ex_star]:
            is_break = True if note_type == NoteType.break_star else False
            slides = [
                slide
                for slide in simai_notes
                if slide.note_type == NoteType.complete_slide
                and slide.measure == simai_note.measure
                and slide.position == simai_note.position
            ]
            sdt.add_star(simai_note.measure, simai_note.position, len(slides), is_break)
        elif note_type == NoteType.complete_slide:
            # SDT slide duration include the delay
            # unlike in simai
            pattern = simai_pattern_to_int(simai_note)
            sdt.add_slide(
                simai_note.measure,
                simai_note.position,
                simai_note.end_position,
                pattern,
                simai_note.duration + simai_note.delay,
                slide_counter,
                simai_note.delay,
            )
            slide_counter += 1
        elif note_type in [NoteType.touch_tap, NoteType.touch_hold]:
            # Touch tap and touch hold
            if convert_touch:
                touch_converter(sdt, simai_note)
            else:
                skipped_notes += 1
        else:
            print("Warning: Unknown note type {}".format(note_type))

    if skipped_notes > 0:
        print("Skipped {} touch note(s)".format(skipped_notes))
