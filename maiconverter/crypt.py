import os
from Crypto.Cipher import AES
from binascii import hexlify, unhexlify
import gzip


class MaiFinaleCrypt:
    def __init__(self, key):
        self.key = unhexlify(key.replace(" ", ""))
        if len(self.key) != 0x10:
            raise ValueError("Invalid key length.")
        self.cipher = None

    def generate(self, iv):
        self.cipher = AES.new(self.key, AES.MODE_CBC, iv)

    def convert_to_text(self, file_path):
        with open(file_path, "rb") as encrypted_file:
            iv = encrypted_file.read(0x10)
            ciphertext = encrypted_file.read()
            if len(ciphertext) % 0x10 != 0:
                raise Exception("Ciphertext is not a multiple of 16.")

            self.generate(iv)

            gzipdata = self.cipher.decrypt(ciphertext)
            padding = gzipdata[-1]
            gzipdata = gzipdata[:-padding]

            data = gzip.decompress(gzipdata)
            data = data[16:]

            return data

    def convert_to_bin(self, file_path):
        with open(file_path, "rb") as text_file:
            plaintext = text_file.read()
            plaintext = unhexlify("4b67ca1eebc78fb9964f781019bc4903") + plaintext
            gzipdata = gzip.compress(plaintext)

            padding = b""
            if len(gzipdata) % 16 != 0:
                amount = 16 - (len(gzipdata) % 16)
                padding = bytes([amount]) * amount
            gzipdata += padding

            iv = os.urandom(16)
            self.generate(iv)
            ciphertext = self.cipher.encrypt(gzipdata)

            return iv + ciphertext
