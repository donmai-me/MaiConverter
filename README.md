# MaiConverter
A Python program for parsing and converting Maimai charts. Made up of two parts: 
* An importable package for parsing, creating, exporting, and converting SDT, Ma2, and 3Simai charts. And
* a commandline script for parsing and converting the 3 formats.

If you're not familiar with these file formats, then you can read about sdt files [here](https://listed.to/@donmai/18173/the-four-chart-formats-of-maimai-classic) and simai files [here](https://w.atwiki.jp/simai/pages/25.html). You can read about my blog post about this [here](https://listed.to/@donmai/18284/newly-released-simai-to-sdt-converter)

If you're interested in anything MaiMai modding related, then go join [MaiMai TEA](https://discord.gg/82UR3e2akE) in Discord.

# Dependencies 
* [Pycryptodome](https://pypi.org/project/pycryptodome)
* [Lark](https://pypi.org/project/lark-parser)

# Commandline
The command-line script, installed as part of the package, can parse, convert, encrypt, or decrypt MaiMai chart formats. The general form is:

```maiconverter COMMAND /path/to/file/or/directory```

`COMMAND` can be the following, with descriptions later:
* encrypt
* decrypt
* ma2tosdt
* ma2tosimai
* sdttoma2
* sdttosimai
* simaifiletoma2
* simaifiletosdt
* simaitoma2
* simaitosdt

The second positional argument is the path to a chart file or directory. If given a directory, it will convert all relevant files found in the directory.

The program will save all converted file in the "output" folder in the input file's parent directory or the input directory. It will make an "output" folder if there is no existing folder.

## encrypt, decrypt

These commands will either encrypt an S\*T chart file to their equivalent S\*B file or vice versa.
**Requires**: -k or --key parameter followed by a hexadecimal AES key. The program can encrypt or decrypt a **table** by adding a -db or --database toggle parameter.

### Example
Convert an SDT to SDB:

```maiconverter encrypt --key 0xFEDCBA9876543210 100_songname_02.sdt```

Convert an SCB to SCT:

```maiconverter decrypt --key 0xFEDCBA9876543210 252_donmaime_05.scb```

Decrypts an encrypted table:

```maiconverter decrypt --key 0xFEDCBA9876543210 mmtablename.bin```

## sdttoma2, sdttosimai

These commands will either convert an S\*T file to ma2 or Simai, respectively. **Requires** -b or --bpm parameter followed by the song's BPM as either an int or float. 
**Note**: For sdttosimai, it does not produce a complete Simai file. sdttosimai only generates a Simai chart.

### Example
Convert a 200 bpm SRT file to Simai:

```maiconverter sdttosimai --bpm 200 300_segapls.srt```

Convert a 130 bpm SDT file to Ma2:

```maiconverter sdttoma2 --bpm 130 301_dontsue.sdt```

## ma2tosdt, ma2tosimai

These commands will either convert a Ma2 file to SDT or Simai, respectively.
**Note**: For ma2tosimai, it does not produce a complete Simai file. ma2tosimai only generates a Simai chart.

### Example
Convert a Ma2 file to SDT:

```maiconverter ma2tosdt 000404_02.ma2```

Convert a Ma2 file to Simai:

```maiconverter ma2tosimai 001401_04.ma2```

## simaitoma2, simaitosdt

These commands convert a text file containing only a Simai chart file to either a Ma2 or SDT, respectively.

## simaifiletoma2, simaifiletosdt

These commands differ from the previous by parsing an entire maidata.txt. All charts are individually converted to a Ma2 or SDT, respectively.

# Misc commandline arguments
## -o, --output
Specify an output directory, or it defaults to the input directory.

## -d, --delay
If you want to apply an offset to every converted chart's notes, you can do so using this argument. It accepts both negative and positive offsets in terms of measures.

## -ct, --convert_touch
If converting from Ma2 or Simai to SDT, you can add this toggle to (naively) convert touch notes to regular tap and hold notes. Useful when you want to manually convert touch notes to tap and hold notes. You just need to modify the note's button, no need to figure out the timing.

## -md, --max-divisor
Sets the max Simai divisor ("{}") that is allowed when exporting a Simai chart. Set it to a low number like 128, should you want a more readable output. Defaults to 1000. 

# Python package
If you installed the wheel file, you could import the program like a standard Python package. If you want to make a chart maker or GUI frontend for this converter, please use it. See `how_to_make_charts.md` for an introductory guide on using MaiConverter for chart making. There is also (incomplete) documentation for classes and functions in the package. See licensing below.

# TODOS
* Documentation
* Do all the `TODO`s scattered in the package
* Reduce jank

# Contact
If you have questions or bug reports and for some reason you don't want to make an issue at GitHub, send me a DM or ping me at MaiTea Discord server.

* Discord: donmai#1493
* Twitter: @donmai_me
* GitHub: donmai-me
* Listed.to: @donmai

# License
This is an open-sourced application licensed under the MIT License
