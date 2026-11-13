# Changelog

All notable changes are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-11-13

### Added
- Phase 0: package skeleton; the poster spec (page size, resolution, margin, gap,
  cells holding a plain text blob or an image); the `poster version` and `shapes`
  commands; strict typing, lint, tests and CI on Python 3.11 to 3.13.
- Phase 1: rectangles, equally spaced. The grid engine picks the rows and columns that
  make the shapes largest (or uses `columns`), keeps every gap equal and centers a short
  last row. Text is wrapped and set at the largest size that fits; images are scaled
  without distortion. `poster render` writes a PNG at the page's resolution;
  `poster layout` prints each shape's box. Two example specs.
