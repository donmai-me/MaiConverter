from dataclasses import dataclass
from typing import List

from .simai import SimaiChart, simai_pattern_from_int
from .maisdt import MaiSDT
from .note import MaiNote, NoteType


@dataclass
class StartSlide:
    measure: float
    position: int
    duration: float
    delay: float
    slide_id: int


def sdt_to_simai(sdt: MaiSDT, initial_bpm: float) -> SimaiChart:
    simai_chart = SimaiChart()
    simai_chart.set_bpm(1.0, initial_bpm)
    convert_notes(simai_chart, sdt.notes)
    return simai_chart


def convert_notes(simai_chart: SimaiChart, sdt_notes: List[MaiNote]) -> None:
    start_slides = []
    for sdt_note in sdt_notes:
        note_type = sdt_note.note_type
        if note_type in [
            NoteType.tap,
            NoteType.break_tap,
            NoteType.star,
            NoteType.break_star,
        ]:
            is_break = (
                True
                if note_type in [NoteType.break_tap, NoteType.break_star]
                else False
            )
            is_star = (
                True if note_type in [NoteType.star, NoteType.break_star] else False
            )
            simai_chart.add_tap(sdt_note.measure, sdt_note.position, is_break, is_star)
        elif note_type == NoteType.hold:
            simai_chart.add_hold(sdt_note.measure, sdt_note.position, sdt_note.duration)
        elif note_type == NoteType.start_slide:
            # simai slide durations does not include the delay
            # unlike in sdt
            start_slide = StartSlide(
                sdt_note.measure,
                sdt_note.position,
                sdt_note.duration - sdt_note.delay,
                sdt_note.delay,
                sdt_note.slide_id,
            )
            start_slides.append(start_slide)
        elif note_type == NoteType.end_slide:
            start_slide = [
                slide for slide in start_slides if slide.slide_id == sdt_note.slide_id
            ]
            if len(start_slide) == 0:
                raise Exception("No corresponding start slide")
            elif len(start_slide) > 1:
                raise Exception("Multiple start slides with same slide id")
            else:
                start_slide = start_slide[0]
                pattern = simai_pattern_from_int(
                    sdt_note.pattern, start_slide.position, sdt_note.position
                )
                simai_chart.add_slide(
                    start_slide.measure,
                    start_slide.position,
                    sdt_note.position,
                    start_slide.duration,
                    pattern[0],
                    start_slide.delay,
                    pattern[1],
                )
        else:
            print("Warning: Unknown note type {}".format(note_type))