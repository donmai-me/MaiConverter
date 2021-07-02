Old scripts. Consider using the included command-line tool when you install the package.

# Usage
## ma2_to_sdt.py
Converts a ma2 file or a directory containing ma2 files to sdt.

All output files are stored in 'output' folder in the same directory as the input. Unless output directory is specified by using the --output or -o parameter

```python ma2_to_sdt.py /path/to/file/or/directory```

To convert ma2 touch tap and touch hold notes into approximate regular tap and hold notes, add the --convert-touch or -ct argument.

## ma2_to_simai.py
Converts a ma2 file or a directory containing ma2 files to simai. 

**NOTE**: This is a proof of concept and does **not** produce a complete simai file. The output file only contains the chart for one difficulty with no "&inote_=" or any simai fields.

Usage is just like ma2_to_sdt.py but there are no touch note conversion.

## ma2_to_sdt.py
Converts a ma2 file or a directory containing ma2 files to sdt. 

All output files are stored in 'output' folder in the same directory as the input. Unless output directory is specified by using the --output or -o parameter

```python ma2_to_sdt.py /path/to/file/or/directory```

To convert ma2 touch tap and touch hold notes into approximate regular tap and hold notes, add the --convert-touch or -ct argument.

## sxt_to_ma2.py
Converts an s\*t file or a directory containing s\*t files to ma2.

Usage is just like ma2_to_sdt.py but you need to manually specify the bpm of the chart or group of charts because s\*t doesn't include that data. And there are no touch note conversion.

## sxt_to_simai.py
Converts an s\*t file or a directory containing s\*t files to simai.

**NOTE**: This is a proof of concept and does **not** produce a complete simai file. The output file only contains the chart for one difficulty with no "&inote_=" or any simai fields.

Usage is just like sxt_to_ma2.py

## simai_to_sdt.py
Converts a simai file or a directory containing simai files to sdt.

**NOTE**: This is a proof of concept and does **not** accept a complete simai file. The input file should only contain the chart for one difficulty with no "&inote_=" or any simai fields.

Usage is just like ma2_to_sdt.py

## simai_to_ma2.py
Converts a simai file or a directory containing simai files to ma2.

**NOTE**: This is a proof of concept and does **not** accept a complete simai file. The input file should only contain the chart for one difficulty with no "&inote_=" or any simai fields.

Usage is just like ma2_to_simai.py

## encrypt_decrypt.py
Encrypts and decrypts finale files. S\*T files are converted to S\*B files and vice versa. Database files can be encrypted and decrypted by using the --database or -db parameter.

All output files are stored in 'output' folder in the same directory as the input. Unless output directory is specified by using the --output or -o parameter

### Encrypting
```python encrypt_decrypt.py encrypt 'AES KEY HERE IN HEX' /path/to/file/or/directory```

### Decrypting
```python encrypt_decrypt.py decrypt 'AES KEY HERE IN HEX' /path/to/file/or/directory```