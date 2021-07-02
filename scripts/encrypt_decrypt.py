import argparse
import os
import re

from maiconverter.maicrypt import MaiFinaleCrypt


def main():
    parser = argparse.ArgumentParser(
        description="Encrypts or decrypts a score file or "
        + "a directory containing score files.",
        allow_abbrev=False,
    )

    # python encrypt_decrypt.py encrypt 'KEY HERE IN HEX' /path/to/input
    parser.add_argument(
        "command",
        metavar="Command",
        type=str,
        choices=["encrypt", "decrypt"],
        help="Specify whether to encrypt or decrypt",
    )
    parser.add_argument(
        "key", metavar="Key", type=str, help="16 byte AES key used (whitespace allowed)"
    )
    parser.add_argument(
        "path", metavar="Path", type=file_path, help="Path to score file or directory"
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="Output directory",
        type=dir_path,
        help="Path to output. Defaults to /path/to/input/output",
    )
    parser.add_argument(
        "--database",
        "-db",
        metavar="Process database/s toggle",
        action="store_const",
        default=False,
        const=True,
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

        if args.command == "encrypt":
            if args.database:
                files = [file for file in files if not re.search(r".tbl", file) is None]
            else:
                # Only accept ".sdt" ".sct" ".szt" ".srt" files
                files = [file for file in files if not re.search(r".s.t", file) is None]
        else:  # decrypt
            if args.database:
                files = [file for file in files if not re.search(r".bin", file) is None]
            else:
                # Only accept ".sdb" ".scb" ".szb" ".srb" files
                files = [file for file in files if not re.search(r".s.b", file) is None]

        for file in files:
            if args.database:
                handle_db(
                    os.path.join(args.path, file), output_dir, args.command, args.key
                )
            else:
                handle_file(
                    os.path.join(args.path, file), output_dir, args.command, args.key
                )
    else:
        if args.database:
            handle_db(args.path, output_dir, args.command, args.key)
        else:
            handle_file(args.path, output_dir, args.command, args.key)


# input_path is a path to afile not a directory
def handle_file(input_path, output_dir, command, key):
    crypt = MaiFinaleCrypt(key)

    if command == "encrypt":
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        file_ext = os.path.splitext(input_path)[1].replace("t", "b")
        if os.path.exists(os.path.join(output_dir, file_name + file_ext)):
            print("File {} exists! Skipping".format(file_name + file_ext))
            return

        cipher_text = crypt.convert_to_bin(input_path)
        f = open(os.path.join(output_dir, file_name + file_ext), "xb")
        f.write(cipher_text)
        f.close()
    else:
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        file_ext = os.path.splitext(input_path)[1].replace("b", "t")
        if os.path.exists(os.path.join(output_dir, file_name + file_ext)):
            print("File {} exists! Skipping".format(file_name + file_ext))
            return

        plain_text = crypt.convert_to_text(input_path)
        f = open(os.path.join(output_dir, file_name + file_ext), "xb")
        f.write(plain_text)
        f.close()


def handle_db(input_path, output_dir, command, key):
    crypt = MaiFinaleCrypt(key)

    if command == "encrypt":
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        file_ext = ".bin"
        if os.path.exists(os.path.join(output_dir, file_name + file_ext)):
            print("File {} exists! Skipping".format(file_name + file_ext))
            return

        cipher_text = crypt.convert_to_bin(input_path)
        f = open(os.path.join(output_dir, file_name + file_ext), "xb")
        f.write(cipher_text)
        f.close()
    else:
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        file_ext = ".tbl"
        if os.path.exists(os.path.join(output_dir, file_name + file_ext)):
            print("File {} exists! Skipping".format(file_name + file_ext))
            return

        plain_text = crypt.convert_to_text(input_path)
        f = open(os.path.join(output_dir, file_name + file_ext), "xb")
        f.write(plain_text)
        f.close()


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
