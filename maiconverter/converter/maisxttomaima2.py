from dataclasses import dataclass
from typing import List, Union

from ..maima2 import MaiMa2
from ..maisxt import MaiSxt, TapNote, HoldNote, SlideStartNote, SlideEndNote
from ..event import NoteType


@dataclass
class StartSlide:
    measure: float
    position: int
    duration: float
    delay: float
    slide_id: int


def sdt_to_ma2(
    sdt: MaiSxt,
    fes_mode: bool = False,
) -> MaiMa2:
    ma2 = MaiMa2(fes_mode=fes_mode)
    ma2.set_bpm(0.0, sdt.bpm)
    ma2.set_meter(0.0, 4, 4)
    convert_notes(ma2, sdt.notes)
    return ma2


def convert_notes(
    ma2: MaiMa2,
    sdt_notes: List[Union[TapNote, HoldNote, SlideStartNote, SlideEndNote]],
) -> None:
    start_slides = []
    for sdt_note in sdt_notes:
        note_type = sdt_note.note_type
        if isinstance(sdt_note, TapNote):
            is_break = note_type in [NoteType.break_tap, NoteType.break_star]
            is_star = note_type in [NoteType.star, NoteType.break_star]
            ma2.add_tap(
                measure=sdt_note.measure,
                position=sdt_note.position,
                is_break=is_break,
                is_star=is_star,
            )
        elif isinstance(sdt_note, HoldNote):
            ma2.add_hold(
                measure=sdt_note.measure,
                position=sdt_note.position,
                duration=sdt_note.duration,
            )
        elif isinstance(sdt_note, SlideStartNote):
            # ma2 slide durations does not include the delay unlike in sxt
            start_slide = StartSlide(
                measure=sdt_note.measure,
                position=sdt_note.position,
                duration=sdt_note.duration - sdt_note.delay,
                delay=sdt_note.delay,
                slide_id=sdt_note.slide_id,
            )
            start_slides.append(start_slide)
        elif isinstance(sdt_note, SlideEndNote):
            starts = [
                slide for slide in start_slides if slide.slide_id == sdt_note.slide_id
            ]
            if len(starts) == 0:
                raise Exception("No corresponding start slide")
            if len(starts) > 1:
                raise Exception("Multiple start slides with same slide id")

            start_slide = starts[0]
            ma2.add_slide(
                measure=start_slide.measure,
                start_position=start_slide.position,
                end_position=sdt_note.position,
                duration=start_slide.duration,
                pattern=sdt_note.pattern,
                delay=start_slide.delay,
            )
        else:
            print("Warning: Unknown note type {}".format(note_type))
