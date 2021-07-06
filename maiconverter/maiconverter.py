import os
import argparse
import re
import traceback

import maiconverter
from maiconverter.maicrypt import (
    finale_db_encrypt,
    finale_db_decrypt,
    finale_chart_encrypt,
    finale_chart_decrypt,
)
from maiconverter.maima2 import MaiMa2
from maiconverter.maisdt import MaiSDT
from maiconverter.simai import parse_file, SimaiChart
from maiconverter.converter import (
    ma2_to_sdt,
    ma2_to_simai,
    sdt_to_ma2,
    sdt_to_simai,
    simai_to_ma2,
    simai_to_sdt,
)

COMMANDS = [
    "encrypt",
    "decrypt",
    "ma2tosdt",
    "ma2tosimai",
    "sdttoma2",
    "sdttosimai",
    "simaifiletoma2",
    "simaifiletosdt",
    "simaitoma2",
    "simaitosdt",
]


def file_path(string):
    if os.path.exists(string):
        return string.rstrip("/\\")

    raise FileNotFoundError(string)


# Only accepts directory paths
def dir_path(string):
    if os.path.isdir(string):
        return string.rstrip("/\\")

    raise NotADirectoryError(string)


def crypto(args, output):
    if args.key is None:
        raise RuntimeError("Key not supplied")

    if os.path.isdir(args.path):
        files = os.listdir(args.path)
        files = [
            os.path.join(args.path, file)
            for file in files
            if os.path.isfile(os.path.join(args.path, file))
        ]

        if args.command == "encrypt":
            if args.database:
                files = [
                    file for file in files if not re.search(r"\.tbl", file) is None
                ]
            else:
                # Only accept ".sdt" ".sct" ".szt" ".srt" files
                files = [
                    file for file in files if not re.search(r"\.s.t", file) is None
                ]
        else:  # decrypt
            if args.database:
                files = [
                    file for file in files if not re.search(r"\.bin", file) is None
                ]
            else:
                # Only accept ".sdb" ".scb" ".szb" ".srb" files
                files = [
                    file for file in files if not re.search(r"\.s.b", file) is None
                ]
    else:
        files = [args.path]

    for file in files:
        if args.database:
            handle_db(file, output, args.command, args.key)
        else:
            handle_file(file, output, args.command, args.key)


def chart_convert(args, output):
    if args.command in ["ma2tosdt", "ma2tosimai"]:
        file_regex = r"\.ma2"
    elif args.command in ["sdttoma2", "sdttosimai"]:
        if args.bpm is None:
            raise RuntimeError("BPM required for SDT file")

        file_regex = r"\.s.t"
    else:
        file_regex = r"\.txt"

    if os.path.isdir(args.path):
        files = os.listdir(args.path)
        files = [
            os.path.join(args.path, file)
            for file in files
            if os.path.isfile(os.path.join(args.path, file))
            and re.search(file_regex, file) is not None
        ]
    else:
        files = [args.path]

    for file in files:
        name = os.path.splitext(os.path.basename(file))[0]

        try:
            if args.command in ["ma2tosdt", "ma2tosimai"]:
                handle_ma2(file, name, output, args)
            elif args.command in ["sdttoma2", "sdttosimai"]:
                handle_sdt(file, name, output, args)
            elif args.command in ["simaifiletoma2", "simaifiletosdt"]:
                handle_simai_file(file, name, output, args)
            else:
                handle_simai_chart(file, name, output, args)

        except Exception as e:
            print(f"Error occured processing {file}. {e}")
            traceback.print_exc()


def handle_ma2(file, name, output_path, args):
    ma2 = MaiMa2.open(file, encoding=args.encoding)
    if len(args.delay) != 0:
        ma2.offset(args.delay)

    if args.command == "ma2tosdt":
        sdt = ma2_to_sdt(ma2, convert_touch=args.convert_touch)
        ext = ".sdt"
    else:
        simai = ma2_to_simai(ma2)
        ext = ".txt"

    with open(
        os.path.join(output_path, name + ext), "w+", newline="\r\n", encoding="utf-8"
    ) as out:
        if args.command == "ma2tosimai":
            out.write(simai.export(max_den=args.max_divisor))
        else:
            out.write(sdt.export())


def handle_sdt(file, name, output_path, args):
    sdt = MaiSDT.open(file, encoding=args.encoding)
    if len(args.delay) != 0:
        sdt.offset(args.delay)

    if args.command == "sdttoma2":
        ma2 = sdt_to_ma2(sdt, initial_bpm=args.bpm, res=args.resolution)
        ext = ".ma2"
    else:
        simai = sdt_to_simai(sdt, initial_bpm=args.bpm)
        ext = ".txt"

    with open(
        os.path.join(output_path, name + ext), "w+", newline="\r\n", encoding="utf-8"
    ) as out:
        if args.command == "sdttosimai":
            out.write(simai.export(max_den=args.max_divisor))
        else:
            out.write(ma2.export())


def handle_simai_chart(file, name, output_path, args):
    with open(file, "r", encoding=args.encoding) as f:
        chart_text = f.read()

    simai = SimaiChart.from_str(chart_text, message=f"Parsing Simai chart at {file}...")
    if len(args.delay) != 0:
        simai.offset(args.delay)

    if args.command == "simaitosdt":
        ext = ".sdt"
        converted = simai_to_sdt(simai, convert_touch=args.convert_touch)
    else:
        ext = ".ma2"
        converted = simai_to_ma2(simai, res=args.resolution)

    with open(
        os.path.join(output_path, name + ext), "w+", newline="\r\n", encoding="utf-8"
    ) as out:
        out.write(converted.export())


def handle_simai_file(file, name, output_path, args):
    title, charts = parse_file(file, encoding=args.encoding)
    for i, chart in enumerate(charts):
        diff, simai_chart = chart
        if len(args.delay) != 0:
            simai_chart.offset(args.delay)

        try:
            if args.command == "simaifiletosdt":
                ext = ".sdt"
                converted = simai_to_sdt(simai_chart, convert_touch=args.convert_touch)
            else:
                ext = ".ma2"
                converted = simai_to_ma2(simai_chart, res=args.resolution)

            name = title + f"_{diff}"
            with open(
                os.path.join(output_path, name + ext),
                "w+",
                newline="\r\n",
                encoding="utf-8",
            ) as out:
                out.write(converted.export())
        except Exception as e:
            print(f"Error processing {i + 1} chart of file. {e}")
            traceback.print_exc()


def handle_file(input_path, output_dir, command, key):
    file_name = os.path.splitext(os.path.basename(input_path))[0]
    if command == "encrypt":

        file_ext = os.path.splitext(input_path)[1].replace("t", "b")
        if os.path.exists(os.path.join(output_dir, file_name + file_ext)):
            print("File {} exists! Skipping".format(file_name + file_ext))
            return

        cipher_text = finale_chart_encrypt(key, input_path)
        with open(os.path.join(output_dir, file_name + file_ext), "xb") as f:
            f.write(cipher_text)
    else:
        file_ext = os.path.splitext(input_path)[1].replace("b", "t")
        if os.path.exists(os.path.join(output_dir, file_name + file_ext)):
            print("File {} exists! Skipping".format(file_name + file_ext))
            return

        plain_text = finale_chart_decrypt(key, input_path)
        with open(
            os.path.join(output_dir, file_name + file_ext),
            "x",
            newline="\r\n",
            encoding="utf-8",
        ) as f:
            f.write(plain_text)


def handle_db(input_path, output_dir, command, key):
    if command == "encrypt":
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        file_ext = ".bin"
        if os.path.exists(os.path.join(output_dir, file_name + file_ext)):
            print("File {} exists! Skipping".format(file_name + file_ext))
            return

        cipher_text = finale_db_encrypt(key, input_path)
        with open(os.path.join(output_dir, file_name + file_ext), "xb") as f:
            f.write(cipher_text)
    else:
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        file_ext = ".tbl"
        if os.path.exists(os.path.join(output_dir, file_name + file_ext)):
            print("File {} exists! Skipping".format(file_name + file_ext))
            return

        plain_text = finale_db_decrypt(key, input_path)
        with open(
            os.path.join(output_dir, file_name + file_ext),
            "x",
            newline="\r\n",
            encoding="utf-8",
        ) as f:
            f.write(plain_text)


def main():
    parser = argparse.ArgumentParser(
        description="Tool for converting Maimai chart formats",
        allow_abbrev=False,
    )
    parser.add_argument(
        "command",
        metavar="command",
        type=str,
        choices=COMMANDS,
        help="Specify whether to encrypt or decrypt",
    )
    parser.add_argument("path", metavar="input", type=file_path, help="")
    parser.add_argument(
        "-k",
        "--key",
        type=str,
        help="16 byte AES key for encrypt/decrypt (whitespace allowed)",
    )
    parser.add_argument(
        "--database",
        "-db",
        action="store_const",
        default=False,
        const=True,
        help="Database/s toggle for encrypt/decrypt",
    )
    parser.add_argument(
        "-b",
        "--bpm",
        metavar="Song BPM",
        type=float,
        help="Song BPM for sdttoma2/sdttosimai",
    )
    parser.add_argument(
        "-d",
        "--delay",
        metavar="Delay",
        type=str,
        default="",
        help="Offset a chart by set measures (can be negative)",
    )
    parser.add_argument(
        "-ct",
        "--convert_touch",
        action="store_const",
        default=False,
        const=True,
        help="Toggle to convert touch notes for chart conversion to SDT",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        default=384,
        help="Output chart resolution for ma2 charts",
    )
    parser.add_argument(
        "-md",
        "--max_divisor",
        type=int,
        default=1000,
        help="Max divisor used in Simai export",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="Output directory",
        type=dir_path,
        help="Path to output. Defaults to /path/to/input/output",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        type=str,
        default="utf-8",
        help="Specify encoding of source file. Defaults to utf-8",
    )

    args = parser.parse_args()
    print(f"MaiConverter {maiconverter.__version__} by donmai")

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

    if args.command in ["encrypt", "decrypt"]:
        crypto(args, output_dir)
    else:
        chart_convert(args, output_dir)

    print(
        "Finished. Join MaiMai Tea Discord server for more info and tools about MaiMai modding!"
    )
    print("https://discord.gg/WxEMM9dnwR")
