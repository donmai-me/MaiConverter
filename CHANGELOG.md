# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.14.3] - 2021-12-20
### Fixed
- Fixed exceptions raised when ma2 TouchHoldNote has a 0 length

### Changed
- Batch conversions will no longer continue when one fails.
- Program should no longer return exit code 0 for failed conversions.

## [0.14.2] - 2021-12-17
### Fixed
- Fixes ma2 export being offset by one measure
- Fixes 360 degree slide conversion from ma2 to simai. [GitHub Issue](https://github.com/donmai-me/MaiConverter/issues/9)

### Added
- Initial PyTest folder

## [0.14.1] - 2021-11-14
### Fixed
- Fixed bugs in finale charts encrypt/decrypt.

## [0.14.0] - 2021-11-14
### Added
- New time tracking functions: measure_to_second, second_to_measure, and quantise.
- Time functions measure_to_second and second_to_measure has an optional parameter `include_metronome_ticks`, set to True by default, that takes into account the first few metronome ticks at the start.
- New script (sxt_change_bpm.py) that converts an MaiSxt chart written in one BPM to another.
- New script (sxt_to_ma2_with_bpms.py) that converts an MaiSxt chart to a MaiMa2 chart that copies the BPM skeleton of another MaiMa2 chart.

### Changed
- Renamed MaiSDT to MaiSxt.
- Renamed maisdt package to maisxt.
- Renamed all conversion functions that mentions sdt to sxt.
- MaiSxt constructor now requires BPM.
- Conversion functions that converts from MaiSxt no longer accepts initial_bpm parameter.
- All chart class methods that returns None, now returns itself instead. For easy chaining.
- MaiSxt and MaiMa2 add_slide now checks for validity of slide with an optional toggle to disable checks.
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

[Unreleased]: https://github.com/donmai-me/MaiConverter/compare/0.14.3...HEAD
[0.14.3]: https://github.com/donmai-me/MaiConverter/compare/0.14.2...0.14.3
[0.14.2]: https://github.com/donmai-me/MaiConverter/compare/0.14.1...0.14.2
[0.14.1]: https://github.com/donmai-me/MaiConverter/compare/0.14.0...0.14.1
[0.14.0]: https://github.com/donmai-me/MaiConverter/compare/0.13.0...0.14.0
[0.13.0]: https://github.com/donmai-me/MaiConverter/compare/0.12.0...0.13.0
