import argparse
import copy
import os.path

from maiconverter.converter import sdt_to_ma2
from maiconverter.maima2 import MaiMa2, HoldNote, SlideNote, TouchHoldNote
from maiconverter.maisxt import MaiSxt
from maiconverter.tool import quantise


# noinspection PyShadowingNames
def main():
    parser = argparse.ArgumentParser("sxt to ma2 with bpm changes")
    parser.add_argument("input", type=str)
    parser.add_argument("conform", type=str)
    parser.add_argument("bpm", type=float)
    parser.add_argument("--offset", type=str)
    parser.add_argument("--resolution", type=int, default=384)
    parser.add_argument("--quantise", type=int, default=16)

    args = parser.parse_args()

    sdt = MaiSxt.open(args.input, args.bpm)
    ma2 = sdt_to_ma2(sdt, args.bpm)
    ma2.notes.sort(key=lambda note: note.measure)

    conform_ma2 = MaiMa2.open(args.conform)

    new_notes = []
    offset = 0.0 - conform_ma2.second_to_measure(
        ma2.measure_to_second(0.0, decrement=False), increment=False
    )
    for note in ma2.notes:
        current_measure = note.measure
        current_time = ma2.measure_to_second(current_measure, decrement=False)
        current_conform_measure = conform_ma2.second_to_measure(
            current_time, increment=False
        )

        scale = conform_ma2.get_bpm(
            current_conform_measure, decrement=False
        ) / ma2.get_bpm(current_measure, decrement=False)

        note = copy.deepcopy(note)
        note.measure = quantise(current_conform_measure + offset, args.quantise)
        if isinstance(note, (HoldNote, TouchHoldNote)):
            note.duration = quantise(scale * note.duration, args.quantise)
        elif isinstance(note, SlideNote):
            note.duration = quantise(scale * note.duration, args.quantise)
            note.delay = quantise(scale * note.delay, args.quantise)

        new_notes.append(note)

    ma2.notes = new_notes
    ma2.bpms = conform_ma2.bpms

    if args.offset is not None:
        ma2.offset(args.offset)

    filename, _ = os.path.splitext(args.input)
    with open(filename + "_conformed.ma2", "w", newline="\r\n") as out:
        out.write(ma2.export(resolution=args.resolution))

    print("saved to: " + filename + "_conformed.ma2")


if __name__ == "__main__":
    main()
