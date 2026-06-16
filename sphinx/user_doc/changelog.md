# Changelog

## [6.0.16] 2026-06-16

### Added

- database_qc_table reimplemented for Capsul (parsing filesystem) with a few viewer processes

### Changed

- VipSplitBrain: fixed normalized coordinates in tyemplate in one of the functions (not sure it is actually used)


## [6.0.15] 2026-05-21

### Added

- Stratified normative stats for Morphologist, separated by age/sex.

### Changed

- Fixed and improved FOMs (File Organization Model) for Morphologist/Capsul.
- the two versions of brainvisa-1.0 FOMs ("auto" and "nonoverlap") have been merged, based on the non-overlapping one, and are now the same ("overlap" loads the regular one and adds nothing to it, its name has been left for backward compatibility).

## [6.0.14] 2026-04-07

### Changed

- morphologist-cli fixed subject ID which got quotes for single subject

## [6.0.10] 2026-02-27

### Changed

- morpho-deepsulci: fixed models installation issue (spam model graphs 2019 were not installed)

## [6.0.9] 2026-02-27

### Changed

- morphologist-ui: fixed sulci session name in BIDS mode to match regular morphologist attributes
- morpho_report process: fix in text location (was sometimes overlapping)


## [6.0.8] 2026-02-06

### Changed

- insert new model graphs (for visualization) in the shared database.
- hide read-only databases as output
- improved a bit more switch_manual_labels to include output database

### Added

- added a changelog (was formerly in the web site only)
