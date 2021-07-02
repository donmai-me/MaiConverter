import os
import argparse
import re
import sys

from maiconverter.maima2 import MaiMa2
from maiconverter.converter import ma2_to_simai


def main():
    parser = argparse.ArgumentParser(
        description="Converts ma2 to simai", allow_abbrev=False
    )
    parser.add_argument(
        "path", metavar="Path", type=file_path, help="Path to score file or directory"
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

        files = [file for file in files if not re.search(r".ma2", file) is None]

        for file in files:
            convert_ma2_file(os.path.join(args.path, file), output_dir, args.delay)
    elif not re.search(r".ma2", args.path) is None:
        convert_ma2_file(args.path, output_dir, args.delay)
    else:
        print("Error: Not a ma2 file")
        sys.exit(1)

    sys.exit(0)


def convert_ma2_file(input_path, output_dir, delay):
    ma2 = MaiMa2()
    file_name = os.path.splitext(os.path.basename(input_path))[0]
    file_ext = ".txt"

    if os.path.exists(os.path.join(output_dir, file_name + file_ext)):
        print("File {} exists! Skipping".format(file_name + file_ext))
        return

    with open(input_path, "r") as in_f:
        for line in in_f:
            if line in ["\n", "\r\n"]:
                continue

            ma2.parse_line(line)

    simai_chart = ma2_to_simai(ma2)
    if delay is not None:
        simai_chart.offset(delay)

    with open(os.path.join(output_dir, file_name + file_ext), "x") as out_f:
        out_f.write(simai_chart.export())


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
