# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- New time tracking functions: measure_to_second, second_to_measure, and quantise.
- New script (sxt_change_bpm.py) that converts an MaiSxt chart written in one BPM to another.
- New script (sxt_to_ma2_with_bpms.py) that converts an MaiSxt chart to a MaiMa2 chart that copies the BPM skeleton of another MaiMa2 chart.

### Changed
- All chart formats now internally start at measure 0 instead of 1.
- All set, add, and del events on all chart formats have an optional boolean switch to disable measure decrement.
- Renamed MaiSDT to MaiSxt.
- Renamed maisdt package to maisxt.
- Renamed all conversion functions that mentions sdt to sxt.
- MaiSxt constructor now requires BPM.
- Conversion functions that converts from MaiSxt no longer accepts initial_bpm parameter.
- MaiSxt add_slide now checks for validity of slide with an optional toggle to disable checks and a toggle to raise errors on slides with undefined behaviour.
- Encryption and decryption methods now only accept raw bytes.
- MaiMa2 resolution moved from being an attribute to a parameter in export method.
- Migrated changelog format to keep a changelog and remove entries from unreleased versions.
- MaiMa2 and MaiSxt notes no longer have a newline character at the end when converted to string.
- slide_distance and is_slide_cw moved from simai package to tool package. 

### Removed
- Old scripts in the scripts folder.

## [0.13.0] - 2021-07-07
### Added
- Support for Simai fields: freemsg, PVStart, and PVEnd.
- Support for Simai divisors with float values.
- Encoding parameter for open method in chart classes.

## [0.12.0] - 2021-07-03
### Added
- Ma2 chart parsing.
- Simai with touch notes parsing.
- Ma2 to Simai conversion and vice versa.
- Ma2 to Sdt conversion and vice versa.
- Simai to Sdt conversion and vice versa.

[Unreleased]: https://github.com/donmai-me/MaiConverter/compare/0.13.0...HEAD
[0.13.0]: https://github.com/donmai-me/MaiConverter/compare/0.12.0...0.13.0
