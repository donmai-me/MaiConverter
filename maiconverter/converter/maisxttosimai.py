from dataclasses import dataclass
from typing import List, Union

from ..simai import SimaiChart, pattern_from_int
from ..maisxt import MaiSxt, TapNote, HoldNote, SlideStartNote, SlideEndNote
from ..event import NoteType


@dataclass
class StartSlide:
    measure: float
    position: int
    duration: float
    delay: float
    slide_id: int


def sdt_to_simai(sdt: MaiSxt) -> SimaiChart:
    simai_chart = SimaiChart()
    simai_chart.set_bpm(0.0, sdt.bpm)
    convert_notes(simai_chart, sdt.notes)
    return simai_chart


def convert_notes(
    simai_chart: SimaiChart,
    sdt_notes: List[Union[TapNote, HoldNote, SlideStartNote, SlideEndNote]],
) -> None:
    start_slides = []
    for sdt_note in sdt_notes:
        note_type = sdt_note.note_type
        if isinstance(sdt_note, TapNote):
            is_break = note_type in [NoteType.break_tap, NoteType.break_star]
            is_star = note_type in [NoteType.star, NoteType.break_star]
            simai_chart.add_tap(
                measure=sdt_note.measure,
                position=sdt_note.position,
                is_break=is_break,
                is_star=is_star,
            )
        elif isinstance(sdt_note, HoldNote):
            simai_chart.add_hold(
                measure=sdt_note.measure,
                position=sdt_note.position,
                duration=sdt_note.duration,
            )
        elif isinstance(sdt_note, SlideStartNote):
            # Simai slide durations does not include the delay
            # unlike in sxt
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
            pattern = pattern_from_int(
                sdt_note.pattern, start_slide.position, sdt_note.position
            )
            simai_chart.add_slide(
                measure=start_slide.measure,
                start_position=start_slide.position,
                end_position=sdt_note.position,
                duration=start_slide.duration,
                pattern=pattern[0],
                delay=start_slide.delay,
                reflect_position=pattern[1],
            )
        else:
            print(f"Warning: Unknown note type {note_type}")
