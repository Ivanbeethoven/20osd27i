# Architecture figure review — 2026-10-23

Scientific scope: logical Entity workspace design, reviewed against Sections
3–7 and the fixed source ledger. Current BrewFS checkout entry points were
rechecked for upper spans, full-object integrity and the omitted Entity hint
configuration. The diagram does not merge the ordinary VFS and Entity paths.

The numbered mechanisms are Delta-based workspace resolution, the per-client
Packed lower reader, and backend-persisted object layout. Independent private
state and reusable snapshot objects are explicit. The mutable service remains
visible. The two hint edges retain the implementation gate, and the caption
states that smaller-q writes are gated and upper reads still verify complete
objects. B/q are not application request sizes or a claimed optimal policy.

## Artifact checks

- SVG: live text and stable groups, no raster images, no external assets,
  no outlined labels, no forbidden effects; no off-canvas text. The only SVG
  audit warning is its generic Nature-width heuristic (89/183 mm). This
  figure intentionally uses the actual USENIX width, 177.8 mm = 7 inches.
- PDF: exported from that SVG, no embedded images, all fonts embedded, no
  Type 3 fonts. Minimum audited text is 8.2 pt; glyph-floor audit passes.
- Collision audit: 0 FAIL, 0 WARN. The 29 contained fill overlays are intended
  labels inside boxes and numbered badges. No line crosses a label.
- Geometry: source measures label widths before export and checks canvas
  bounds. This is a single logical diagram, not a quantitative multipanel
  grid; statistical panel alignment and uncertainty bars are inapplicable.
- Preview inspected at full figure size and in paper page 6. The final PDFs
  were rendered in contact sheets to check surrounding pagination.
- Main and neutral-name manuscripts compile with Windows XeLaTeX / latexmk
  4.88. Both remain 16 pages, body ending on page 14. No undefined references,
  overfull boxes or missing glyphs appear in either final build log.

The SVG's declared Arial bold style is editable; exported font resources are
recorded separately by the PDF inspection. The diagram is an author-review
draft: source-supported architecture does not establish runtime qualification,
publication/recovery correctness or measured performance benefits.
