from maiconverter import SimaiToMaiSDT

import argparse
import os
import re

def main():
    parser = argparse.ArgumentParser(description='Converts a simai file ' \
                                    + ' to SDT', allow_abbrev=False)
    parser.add_argument('file_path', metavar='Path', type=str,\
                        help='Path to chart file')
    args = parser.parse_args()

    if not os.path.isfile(args.file_path):
        print('File does not exist')
        sys.exit()

    simai_text = ""

    with open(args.file_path, 'r') as f:
        for line in f:
            if line[0] != "&":
                simai_text += line

    simai_text = "".join(simai_text.split())
    simai_fragments = simai_text.split(",")

    initial_bpm = SimaiToMaiSDT.parse_bpm(simai_fragments[0])
    initial_divisor = SimaiToMaiSDT.parse_divisor(simai_fragments[0])
    converter = SimaiToMaiSDT(initial_bpm, initial_divisor)
    print("Initial BPM: " + str(initial_bpm) + " Initial divisor: " \
          + str(initial_divisor))
    for fragment in simai_fragments:
        dx_notes = re.search("(E[1-8]|C[12]?|B[1-8])", fragment)
        if not dx_notes is None:
            raise Exception("Only standard charts are allowed.")

        if fragment.find("E") != -1:
            break

        new_bpm = SimaiToMaiSDT.parse_bpm(fragment)
        if not new_bpm is None:
            converter.change_bpm(new_bpm)

        new_divisor = SimaiToMaiSDT.parse_divisor(fragment)
        if not new_divisor is None:
            converter.change_divisor(new_divisor)

        tap_notes = SimaiToMaiSDT.parse_tap(fragment)
        if not tap_notes is None:
            converter.add_tap(tap_notes)

        hold_notes = SimaiToMaiSDT.parse_hold(fragment)
        if not hold_notes is None:
            converter.add_hold(hold_notes)

        slide_notes = SimaiToMaiSDT.parse_slide(fragment)
        if not slide_notes is None:
            converter.add_slide(slide_notes)

        converter.next()

    maisdt = converter.export()
    file_name = os.path.splitext(args.file_path)[0]
    f = open(file_name + ".sdt", "w")
    f.write(maisdt)
    f.close()


if __name__ == "__main__":
    main()