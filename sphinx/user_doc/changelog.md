# Changelog

## [6.0.19] 2026-08-06

### Added

- added an optional parameter in morpho_report allowing to specify complex covariables files
- added min_vertex_size parameter to corticalfoldgraph process
- Capsul implementation of morphologist_qc_table, with optional use of a sqlite database to speed parsing up, and all needed viewers (editors are not ready yet).
- Capsul process for database FOM indexing (used in the database_qc_table process)
- doc for `morphologist-cli`
- doc for QC tables and Morphologist report

### Changed

- error handling change in concatenatefiles process (CSV concat) to avoid failures on missing data
- wider support for differing versions of pandas in global morphometry
- database_qc_table / Capsul: some parameters become optional when specified via engine settings (data paths, FOMs) or database indexing
- database_qc_table / Capsul: allow to sort by status colomns
- database_qc_table / Capsul: optimizations in parsing / building time
- improvements in some FOM definitions (in order to have all attributes)
- Fixes in Morphologist UI: several crashes fixed in importation
- Fixes in Morphologist UI: spurious "missing input files" error fixed
- Fixes in Morphologist UI: crash when the current workflow is deleted from outside (from `soma_workflow_gui` for instance)
- Fixes in Morphologist UI: fixed help browser which was broken


## [6.0.17] 2026-06-26

### Added

- QC table GUI ported from Axon to Capsul
- QC measurements comparing segmentations and folds to the MNI template
- morphologist report includes the new QC measurements

### Changed

- Fixes in FOMs and Axon hierarchies
- fix in stratified morphometric stats recordiong for small datasets


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
