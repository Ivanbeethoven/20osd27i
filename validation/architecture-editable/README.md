# Editable architecture validation — 2026-11-04

Current source: `tools/draw_architecture_editable.py`; exports: `figures/system-architecture-editable.{svg,pdf,png}`. The 11 pt gap leaves 5 pt to the junction and 6 pt from it to either lower panel. A 4× raster comparison with `c58ea70` confirms that the upper workspace/legend region and the right RustFS panel are pixel-identical. The direct FUSE bypass remains connected to both paths.

- Canvas: 240 × 268 pt, rendered at manuscript column width. SVG has 45 editable labels; all labels are 7–8.5 pt. PDF has zero raster objects. The first mechanism heading remains a single 8.5 pt line.
- Collision audit: 0 failures, 3 warnings. Each warning combines a white number and its adjacent heading into one bounding box crossing the number badge. Visual inspection confirms that the three badges and headings are distinct and legible.
- SVG width warning: 84.67 mm targets the USENIX column rather than the audit tool's Nature presets of 89/183 mm.
- Panel ② has 13 labels below its heading (previously 19), including the two rows of example data. Its query, selected interval, and matching row align; the caption explains publication and page verification. Figure 3 retains the explicit non-inline read condition. Each box label and the edge label fit on one line in the manuscript.
- In the compiled manuscript, Figure 2 is on page 4, Figure 3 on page 5, and the backup comparison on page 9. The body ends on page 10 of 12. The two figures were inspected at column width. The local XeLaTeX build has no undefined references, missing characters, or overfull boxes.

`scene.json`, `collision.json`, `font-audit.json`, and `svg-audit.json` describe the current export. `formula-review.md` and adjacent historical audit directories describe older revisions; their dimensions and page locations do not describe the current manuscript.
