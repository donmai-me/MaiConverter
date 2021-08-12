import argparse
import copy
import os.path

from maiconverter.maisxt import MaiSxt, HoldNote, SlideStartNote


def main():
    parser = argparse.ArgumentParser("sxt to ma2 with bpm changes")
    parser.add_argument("input", type=str)
    parser.add_argument("original_bpm", type=float)
    parser.add_argument("new_bpm", type=float)

    args = parser.parse_args()
    sdt = MaiSxt.open(args.input, bpm=args.new_bpm)
    sdt.notes.sort(key=lambda x: x.measure)

    scale = args.new_bpm / args.original_bpm

    new_notes = []
    previous_measure = 0.0
    equivalent_current_measure = 0.0
    for note in sdt.notes:
        current_measure = note.measure
        equivalent_current_measure += scale * (current_measure - previous_measure)
        previous_measure = current_measure

        note = copy.deepcopy(note)
        note.measure = equivalent_current_measure

        if isinstance(note, HoldNote):
            note.duration *= scale
        elif isinstance(note, SlideStartNote):
            note.duration *= scale
            note.delay *= scale

        new_notes.append(note)

    new_notes.sort()
    sdt.notes = new_notes

    filename, _ = os.path.splitext(args.input)
    with open(filename + f"_bpm{args.new_bpm}.sxt", "w", newline="\r\n") as out:
        out.write(sdt.export())


if __name__ == "__main__":
    main()
