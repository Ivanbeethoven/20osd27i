# Editable architecture validation — 2026-11-04

Current source: `tools/draw_architecture_editable.py`; exports: `figures/system-architecture-editable.{svg,pdf,png}`. This revision connects the boxed FUSE entry to the view-choice junction and places matching numbered badges in the dashed upper-right legend. The accepted architecture and BrewFS–RustFS optimization region retain their layout.

- Canvas: 240 × 280 pt, rendered at manuscript column width. SVG has 49 editable labels; all labels are 7–8.5 pt. PDF has zero raster objects. The first mechanism heading is a single 8.5 pt line; the RustFS region explicitly names the backend optimizations and per-object block sizing.
- Collision audit: 0 failures, 3 warnings. Each warning combines a white number and its adjacent heading into one bounding box crossing the number badge. Visual inspection confirms that the three badges and headings are distinct and legible.
- SVG width warning: 84.67 mm targets the USENIX column rather than the audit tool's Nature presets of 89/183 mm.
- Semantics checked: ordinary-volume bypass, standalone read-only entry, native/packed alternatives, metadata references to existing bytes, fixed client g, solid object upload, optional dashed B hint, backend-selected q, and retained layout for reads and repair.
- Figure 2 appears on page 4 of the 12-page manuscript; body ends on page 10. Local XeLaTeX build has no undefined references, missing characters, or overfull boxes. Inspected the complete page contact sheet and full-size pages containing the opening, architecture, backend mechanism, and related work.

`scene.json`, `collision.json`, `font-audit.json`, and `svg-audit.json` describe the current export. `formula-review.md` and adjacent historical audit directories describe older revisions; their dimensions and page locations do not describe the current manuscript.
