import os
import gzip
from typing import Union
from binascii import unhexlify
from Crypto.Cipher import AES


def finale_db_decrypt(
    key: str,
    path: str,
    encoding: str = "utf-16-le",
    ignore_errors: bool = True,
) -> str:
    if os.path.getsize(path) % 0x10 != 0:
        raise ValueError("Ciphertext is not a multiple of 16")

    with open(path, "rb") as encrypted_file:
        iv = encrypted_file.read(0x10)
        ciphertext = encrypted_file.read()

    return finale_decrypt(
        mode="db",
        key=key,
        iv=iv,
        ciphertext=ciphertext,
        encoding=encoding,
        ignore_errors=ignore_errors,
    )


def finale_db_encrypt(
    key: str,
    path: str,
    encoding: str = "utf-16-le",
) -> bytes:
    with open(path, "r", encoding="utf-8") as f:
        rawtext = f.read()

    return finale_encrypt(mode="db", key=key, plaintext=rawtext, encoding=encoding)


def finale_chart_decrypt(key: str, path: str, encoding: str = "utf-8") -> str:
    if os.path.getsize(path) % 0x10 != 0:
        raise ValueError("Ciphertext is not a multiple of 16")

    with open(path, "rb") as encrypted_file:
        iv = encrypted_file.read(0x10)
        ciphertext = encrypted_file.read()

    key_bin = int(key, 0).to_bytes(0x10, "big")

    return finale_decrypt(
        mode="chart",
        key=key_bin,
        iv=iv,
        ciphertext=ciphertext,
        encoding=encoding,
    )


def finale_chart_encrypt(key: str, path: str, encoding: str = "utf-8") -> bytes:
    key_bin = int(key, 0).to_bytes(0x10, "big")

    with open(path, "r", encoding="utf-8") as f:
        rawtext = f.read()

    return finale_encrypt(
        mode="chart", key=key_bin, plaintext=rawtext, encoding=encoding
    )


def finale_decrypt(
    mode: str,
    key: Union[str, bytes],
    iv: bytes,
    ciphertext: bytes,
    encoding: str,
    ignore_errors: bool = True,
) -> str:
    if not isinstance(key, bytes):
        key = int(key, 0).to_bytes(0x10, "big")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    gzipdata = cipher.decrypt(ciphertext)

    num_padding = gzipdata[-1]
    if num_padding > 0:
        gzipdata = gzipdata[:-num_padding]
    if gzipdata[:2] != b"\x1f\x8b":
        gzipdata = b"\x1f\x8b" + gzipdata

    if mode == "db":
        # 0x10 bytes for random data and 2 bytes for the UTF-16 BOM
        data = gzip.decompress(gzipdata)[0x12:]
    elif mode == "chart":
        data = gzip.decompress(gzipdata)[0x10:]
    else:
        raise ValueError(f"Unknown mode: {mode}")

    if ignore_errors:
        return data.decode(encoding, errors="ignore")

    return data.decode(encoding)


def finale_encrypt(
    mode: str,
    key: Union[str, bytes],
    plaintext: str,
    encoding: str,
) -> bytes:
    if not isinstance(key, bytes):
        key = unhexlify(key.replace(" ", ""))
    if len(key) != 0x10:
        raise ValueError("Invalid key length")

    JUNK = unhexlify("4b67ca1eebc78fb9964f781019bc4903")
    if mode == "db":
        # FEFF is UTF-16 BOM
        encoded = JUNK + b"\xfe\xff" + plaintext.encode(encoding=encoding)
    else:
        encoded = JUNK + plaintext.encode(encoding=encoding)

    gzipdata = gzip.compress(encoded)
    if len(gzipdata) % 0x10 != 0:
        amount = 0x10 - (len(gzipdata) % 0x10)
        padding = amount.to_bytes(1, "big") * amount
        gzipdata += padding

    iv = os.urandom(0x10)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    return iv + cipher.encrypt(gzipdata)
