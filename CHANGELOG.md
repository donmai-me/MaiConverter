# 0.12.0
* Add support for Simai ex notes written as "ex" instead of just "x". [Reported]
* Force CRLF for Sdt and Ma2 export.
* Fixed bug when a note and bpm change happens at the same time causing gap to be incorrectly computed. [Report: Kyan-pasu]
* Handle division by zero in Simai chart duration parsing. [Reported]
* Refactored Simai chart export solving the following bugs:
  * Simai divisors ("{}") sometimes don't appear at the beginning after the initial bpm declaration. [Report: Kyan-pasu]
  * Incorrect computation in `get_measure_computation` function. [Report: Kyan-pasu]
  * Better handling of float arithmetic.
* Fix bug that causes a slide note to ignore pseudo each modifier. [Reported]
* Fix error in prepending the first 0x10 bytes in chart and db encryption.
* Handle case when decrypted chart or database doesn't have gzip magic number.
* Fix bug in decryption when padding is 0.
* Added more tests and documentation.

# 0.11.0
* Rewritten lark grammar to utilize LALR parser for around 50% speed improvement.
* Tweaked how debug information is presented.

# 0.10.1
* Added debug information when parsing Simai charts and files.
* Minor changes to Simai class.

# 0.10.0
* Added support for simai pseudo each \`. Current implementation is to offset the succeeding note by 1/384 (384 is ma2's default resolution.) [Reported]
* Added support for simai notes with 0 positions (e.g. 3/0, 0>0[4:1]). Current implementation is to ignore such notes. [Reported]
* Added support for simai touch notes with regions A and D. Current implementation is to ignore such notes. [Reported]
* Added support for hold notes where the modifier is first (e.g. 3xh, Cfh). [Reported]
* Ma2 parsing no longer ignores MET events.
* Replaced the word zone with region in touch notes. I used to refer to DX's C, B, and E touch regions as zones. I have since changed them.

# 0.9.0
* Rewritten offset functions to accept inputs in terms of seconds and fractions of measures: "0.5s", "2s", or "1/64"
* Fixed offset not taking into account BPM changes [Report: Kyan-pasu]
* Fixed erroneous check in after_next_measure duration check in `get_rest` in simai module [Reported]
* Add suppport for integer values for simai `&first` fields [Reported]
* Fix simai touch notes parsing. [Reported]
* Removed deprecated MaiFinaleCrypt class.

# 0.8.0
* Rewritten Ma2 parsing to be more flexible for future versions of the format.
* Added support for Ma2 version 1.02.00 [Report: StonerSto].
* Fixed `add_touch_hold` and `del_touch_hold` not using `THO` key for updating note statistics.
* Added ma2 parsing tests.
* Added \_\_main\_\_.py to allow `python -m maiconverter arguments here`

# 0.7.1
* Fixed ma2 parsing of ex star notes [Report: StonerSto].

# 0.7.0
* Added error handling in parallel Simai chart parsing for Windows [Report: Kurimu Pantsu].
* Added support for simai hold notes that don't have duration [Report: Kurimu Pantsu].
* More tests are added for Simai file parsing.
* Added `parse_file_str` for Simai module to parse Simai files in string format rather than opening a file.
* Added `finale_encrypt` and `finale_decrypt` to reduce repetition in code and provide users a way to encrypt/decrypt strings by themselves.

# 0.6.5
* Added two more fields specific to Maipad plus: `demo_seek` and `demo_len` [Report: Kurimu Pantsu]. Current implementation is to ignore these fields.

# 0.6.2 - 0.6.4
* Various bug fixes in Simai file parsing and Simai chart exporting [Report: Kurimu Pantsu].
* Command-line tool now uses the new finale crypt functions instead of the soon-to-be removed `MaiFinaleCrypt`.
* Updated neglected tests module with more tests coming.

# 0.6.1
* Added the old scripts back in the new `scripts` folder.

# 0.6.0
Added four functions in MaiCrypt package: `finale_db_encrypt`, `finale_db_decrypt`, `finale_chart_encrypt`, and `finale_chart_decrypt`. The chart functions are simply the old `MaiFinaleCrypt` class turned into functions. While the db functions are more suited for encrypting and decrypting Finale's database files. Included in the new db functions are easy handling of UTF-16. In accordance with this, the `MaiFinaleCrypt` class is now pending deprecation and will be removed in 0.9.0.

`del_slide` methods in all three chart classes now require a third parameter, `end_position`, to prevent deleting multiple slides that start at the same button and measure.

# 0.5.0
Most of the changes were made to make making charts for the three formats easier and consistent across all the formats.

Added del methods for deleting notes for all three chart classes. Breaking changes are made to Ma2 and SDT classes to unify the method signatures for all three classes. 

In SDT, the StarNote class and add_star method were removed and moved to the TapNote class and add_tap method. Both of them now accept an `is_star` parameter. For the TapNote class an `amount` attribute is added for star notes. A star note's `amount` is now automatically incremented when an `add_slide` method is called that has the same button position and measure.

The `add_slide` method for SDTs no longer need a `slide_id` parameter and has since been removed. The method now automatically assigns a unique `slide_id` when creating a `SlideStart` and `SlideEnd` class.

For Ma2 and SDT classes, the position of `pattern` and `duration` for the `add_slide` method was moved to make it more consistent with other add methods. To avoid code from being broken please use keyword arguments for your programs.

For Simai parallel processing, chunksizes are now based on the number of fragments divided by the amount of available CPU.

# 0.4.0
Added parrellism in Simai fragments parsing for (small) speed improvements. Ongoing debloat of the SimaiChart class and fix PyLint and MyPy warnings and errors.

# 0.3.3
First semi-public release of MaiConverter-Private. Has encrypt/decrypt, S\*T, Ma2, and 3Simai support.
