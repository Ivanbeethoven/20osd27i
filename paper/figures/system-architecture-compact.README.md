# Compact mechanism diagram

Active paper figure: `system-architecture-compact.pdf`.
Editable source: `system-architecture-compact.svg`, with live Arial text and
stable component/edge IDs. All shapes and arrows are vector objects; PNG is a
preview. Final dimensions are 504 x 230 pt with 8 pt minimum labels.

Regenerate from the repository root:

```powershell
python tools/draw_architecture_compact.py
```

Dependencies: reportlab, svglib, PyMuPDF, and Windows Arial/Arial Bold fonts.
Use the labels in `planning/terminology.zh.md` and preserve claim boundaries.
`LowerRange`, `Data`, and `Hole` are the implementation's explicit span kinds.
The middle panel depicts one
name-based access route, and the inherited data edge does not imply a new name
lookup. The right panel's two data/two parity shards with two q cells are a
schematic eligible geometry; neither this drawing nor a hint header establishes
that the integrated runtime has persisted that treatment.

`B` is the erasure-coding block size; `q` is the physical verification/read
quantum. The `B hint` requests a block size; the backend chooses compatible
`q`. A Packed frame is a separate snapshot-format unit.

The brief, primary-paper references and source mappings are in
`planning/architecture-compact-brief.md`; audits are in
`validation/compact-figures/`. Older architecture/v2 assets remain historical.
