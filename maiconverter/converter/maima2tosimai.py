from typing import Sequence, List

from ..simai import (
    SimaiChart,
    pattern_from_int,
    HoldNote as SimaiHoldNote,
    TouchHoldNote as SimaiTouchHoldNote,
    SlideNote as SimaiSlideNote,
)
from ..maima2 import (
    MaiMa2,
    TapNote,
    HoldNote,
    SlideNote,
    TouchTapNote,
    TouchHoldNote,
    BPM,
)
from ..event import MaiNote, NoteType


def ma2_to_simai(ma2: MaiMa2) -> SimaiChart:
    simai_chart = SimaiChart()

    for bpm in ma2.bpms:
        measure = 1.0 if bpm.measure <= 1.0 else bpm.measure

        simai_chart.set_bpm(measure, bpm.bpm)

    convert_notes(simai_chart, ma2.notes)

    if len(simai_chart.bpms) != 1:
        fix_durations(simai_chart)

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


def fix_durations(simai: SimaiChart):
    """Simai note durations (slide delay, slide duration, hold note duration)
    disregards bpm changes midway, unlike ma2. So we'll have to compensate for those.
    """

    def bpm_changes(start: float, duration: float) -> List[BPM]:
        result: List[BPM] = []
        for bpm in simai.bpms:
            if start < bpm.measure < start + duration:
                result.append(bpm)

        return result

    def compensate_duration(
        start: float, duration: float, base_bpm: float, changes: List[BPM]
    ) -> float:
        new_duration = 0

        note_start = start
        for bpm in changes:
            new_duration += (
                base_bpm
                * (bpm.measure - note_start)
                / simai.get_bpm(bpm.measure - 0.0001)
            )

            note_start = bpm.measure

        if note_start < start + duration:
            new_duration += (
                base_bpm
                * (start + duration - note_start)
                / simai.get_bpm(note_start + 0.0001)
            )

        return new_duration

    for note in simai.notes:
        if isinstance(note, (SimaiHoldNote, SimaiTouchHoldNote, SimaiSlideNote)):
            bpms = bpm_changes(note.measure, note.duration)
            if len(bpms) != 0:
                note.duration = compensate_duration(
                    note.measure, note.duration, simai.get_bpm(note.measure), bpms
                )
        if isinstance(note, SimaiSlideNote):
            bpms = bpm_changes(note.measure, note.delay)
            if len(bpms) != 0:
                note.delay = compensate_duration(
                    note.measure, note.delay, simai.get_bpm(note.measure), bpms
                )
