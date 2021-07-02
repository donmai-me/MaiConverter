import os
import argparse
import re
import sys

from maiconverter.maisdt import MaiSDT
from maiconverter.converter import sdt_to_ma2


def main():
    parser = argparse.ArgumentParser(
        description="Converts sdt to ma2", allow_abbrev=False
    )
    parser.add_argument(
        "path", metavar="Path", type=file_path, help="Path to score file or directory"
    )
    parser.add_argument(
        "--bpm",
        metavar="Song BPM",
        type=float,
        help="BPM of the chart or group of chart's song",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="Output directory",
        type=dir_path,
        help="Path to output. Defaults to " + "/path/to/input/output",
    )
    parser.add_argument(
        "-d",
        "--delay",
        metavar="Delay",
        type=float,
        help="Offset a chart by set measures (can be negative)",
    )

    args = parser.parse_args()

    if args.bpm is None:
        print("Error: BPM is required")
        parser.print_help()
        sys.exit(1)

    if args.output is None and os.path.isdir(args.path):
        output_dir = os.path.join(args.path, "output")
    elif args.output is None and not os.path.isdir(args.path):
        output_dir = os.path.join(os.path.dirname(args.path), "output")
    else:
        output_dir = args.output

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    elif os.path.exists(output_dir) and not os.path.isdir(output_dir):
        raise NotADirectoryError(output_dir)

    if os.path.isdir(args.path):
        files = os.listdir(args.path)
        files = [
            file for file in files if os.path.isfile(os.path.join(args.path, file))
        ]

        files = [file for file in files if not re.search(r"\.s..", file) is None]

        for file in files:
            convert_sdt_file(
                os.path.join(args.path, file), output_dir, args.bpm, args.delay
            )
    elif not re.search(r"\.s..", args.path) is None:
        convert_sdt_file(args.path, output_dir, args.bpm, args.delay)
    else:
        print("Error: Not an sdt file")
        sys.exit(1)

    sys.exit(0)


def convert_sdt_file(input_path, output_dir, initial_bpm, delay):
    sdt = MaiSDT()

    file_name = os.path.splitext(os.path.basename(input_path))[0]
    file_ext = ".ma2"

    if os.path.exists(os.path.join(output_dir, file_name + file_ext)):
        print("File {} exists! Skipping".format(file_name + file_ext))
        return

    with open(input_path, "r") as in_f:
        for line in in_f:
            if line in ["\n", "\r\n"]:
                continue

            if re.search(r"\.sr.", input_path) is None:
                sdt.parse_line(line)
            else:
                sdt.parse_srt_line(line)

    ma2 = sdt_to_ma2(sdt, initial_bpm)
    ma2.set_meter(0, 4, 4)
    if delay is not None:
        ma2.offset(delay)

    with open(os.path.join(output_dir, file_name + file_ext), "x") as out_f:
        out_f.write(ma2.export())


# Accepts both file and directory paths
def file_path(string):
    if os.path.exists(string):
        return string.rstrip("/\\")

    raise FileNotFoundError(string)


# Only accepts directory paths
def dir_path(string):
    if os.path.isdir(string):
        return string.rstrip("/\\")

    raise NotADirectoryError(string)


if __name__ == "__main__":
    main()
