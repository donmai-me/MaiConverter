# MaiConverter
Converts standard 3simai files to sdt files so you can play custom charts in your favorite touchlaundry machine. Python done quick and dirty.

If you're not familiar with these file formats, then you can read about sdt files [here](https://listed.to/@donmai/18173/the-four-chart-formats-of-maimai-classic) and simai files [here](https://w.atwiki.jp/simai/pages/25.html). You can read about my blog post about this [here](https://listed.to/@donmai/18284/newly-released-simai-to-sdt-converter)

# Usage
## main.py
Converts standard Simai files to SDT.
Just point the program to your `maidata.txt` and it will convert it to an sdt file.
```python3 main.py maidata.txt```

## encrypt_decrypt.py
Encrypts and decrypts finale files. S\*T files are converted to S\*B files and vice versa. Database files can be encrypted and decrypted by using the --database or -db parameter.

All output files are stored in 'output' folder in the same directory as the input. Unless output directory is specified by using the --output or -o parameter

### Encrypting
```python encrypt_decrypt.py encrypt 'AES KEY HERE IN HEX' /path/to/file/or/directory```

### Decrypting
```python encrypt_decrypt.py decrypt 'AES KEY HERE IN HEX' /path/to/file/or/directory```

# License
This is an open-sourced application licensed under the [MIT License](https://github.com/donmai-me/MaiConverter/blob/master/LICENSE)
