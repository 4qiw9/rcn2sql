# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Detect suspected duplicate GML files (same size, different name)
- Support multiple GML files import with glob patterns (e.g. `rcn_*.gml`)

## [0.1.0] - 2026-02-21

### Added
- Initial release
- CLI with `parse`, `build-wide`, and `pipeline` commands
- GML parsers for 7 feature types:
  - RCN_Transakcja
  - RCN_Dokument
  - RCN_Nieruchomosc
  - RCN_Dzialka
  - RCN_Budynek
  - RCN_Lokal
  - RCN_Adres
- Wide table builder with denormalized data
- Streaming GML/XML parser for large files
- SQLite output with indexes
- Logging to console and file
- Unit tests for parsers and build_wide

