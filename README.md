# MaiConverter
Converts standard 3simai files to sdt files so you can play custom charts in your favorite touchlaundry machine. Python done quick and dirty.

Rewrite now includes a proper lark parser for simai and should handle more 3simai quirks. Conversion logic has also been completely rewritten to be more accurate and maintainable. As such a new s\*t to simai converter has been added.

If you're not familiar with these file formats, then you can read about sdt files [here](https://listed.to/@donmai/18173/the-four-chart-formats-of-maimai-classic) and simai files [here](https://w.atwiki.jp/simai/pages/25.html). You can read about my blog post about this [here](https://listed.to/@donmai/18284/newly-released-simai-to-sdt-converter)

# Dependencies 
* [Pycryptodome](https://pypi.org/project/pycryptodome)
* [Lark](https://pypi.org/project/lark-parser)

# Usage
## simai_to_sdt.py
Converts a simai file or a directory containing simai files to sdt.

**NOTE**: This is a proof of concept and does **not** accept a complete simai file. The input file should only contain the chart for one difficulty with no "&inote_=" or any simai fields.

All output files are stored in 'output' folder in the same directory as the input. Unless output directory is specified by using the --output or -o parameter.

```python simai_to_sdt.py /path/to/file/or/directory```

## sxt_to_simai.py
Converts an s\*t file or a directory containing s\*t files to simai.

**NOTE**: This is a proof of concept and does **not** produce a complete simai file. The output file only contains the chart for one difficulty with no "&inote_=" or any simai fields.

All output files are stored in 'output' folder in the same directory as the input. Unless output directory is specified by using the --output or -o parameter. You need to specify the bpm of the song by using the `--bpm` parameter

```python sxt_to_simai.py --bpm 120 /path/to/file/or/directory```

## encrypt_decrypt.py
Encrypts and decrypts finale files. S\*T files are converted to S\*B files and vice versa. Database files can be encrypted and decrypted by using the --database or -db parameter.

All output files are stored in 'output' folder in the same directory as the input. Unless output directory is specified by using the --output or -o parameter

### Encrypting
```python encrypt_decrypt.py encrypt 'AES KEY HERE IN HEX' /path/to/file/or/directory```

### Decrypting
```python encrypt_decrypt.py decrypt 'AES KEY HERE IN HEX' /path/to/file/or/directory```

# License
This is an open-sourced application licensed under the [MIT License](https://github.com/donmai-me/MaiConverter/blob/master/LICENSE)
