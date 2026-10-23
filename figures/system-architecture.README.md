# Editable system architecture

This is the retained first version. The active paper figure uses
`system-architecture-compact.pdf`; see `system-architecture-compact.README.md`
for its editable source and current build instructions.

This replaces the previous overview as Figure 4 in Section 3. It presents the
logical Entity workspace architecture, not a physical deployment topology.
The same name-neutral drawing is used in both manuscript variants.

- `system-architecture.svg`: editable text, rectangles, circles and routed
  arrows, grouped by stable component/edge IDs. Open with Inkscape or Adobe
  Illustrator. Arial and Arial Bold are the intended fonts; labels are not
  converted to outlines. No embedded bitmap is used.
- `system-architecture.pdf`: vector export consumed by `architecture.tex`;
  its fonts are embedded.
- `system-architecture.png`: 216 dpi preview of the exported PDF.
- `tools/draw_architecture.py` (from the repository root): labels and
  coordinates for regenerating all three formats.

The physical size is 7 × 5.833 inches (504 × 420 pt), matching the USENIX
two-column text width. Text sizes are 8.2, 9 and 10.5 pt. One accent identifies
the three paper mechanisms; solid arrows are logical requests/dependencies,
while dashed arrows have only the hint-integration meaning.

## Edit and rebuild

From the repository root, with the Python environment recorded in
`validation/architecture/environment.json`:

```powershell
python tools/draw_architecture.py
latexmk -xelatex '-outdir=.' '-auxdir=.' -interaction=nonstopmode -halt-on-error main.tex
latexmk -xelatex '-outdir=.' '-auxdir=.' -interaction=nonstopmode -halt-on-error anonymous-preview.tex
```

The generator requires reportlab, svglib, cssselect2, tinycss2 and pymupdf.
On another platform use `--font` and `--bold-font` with the installed TrueType
font files. SVG is exported through svglib/reportlab, and the preview is
rendered from that exact PDF. ReportLab ASCII85 encoding is disabled so the
PDF font auditor can inspect the text streams directly.

For reproducible edits, change generator labels/coordinates and regenerate.
For manual SVG editing, retain an edited copy and export its PDF directly;
running the generator again replaces the generated SVG. Component IDs start
with `n:`, containers with `c:`, and edges with `e:`.

The scientific scope, node/edge source map and excluded claims are in
`planning/architecture-figure-brief.md`. The final caption is maintained in
`sections/03-overview.tex`. The figure intentionally retains the mutable
metadata service, the upper whole-object integrity boundary in its caption,
and the incomplete hint connections. It does not depict evaluated speedups,
general crash recovery, or automatic merging between agents.
