# Architecture v2: image concept to editable figure

The active Figure 4 uses `system-architecture-v2.pdf`. Its source is
`system-architecture-v2.svg`; text, pages, folders, storage objects, brackets
and arrows remain separate editable elements with stable group IDs.
The original `system-architecture.*` files are retained for comparison.

## Visual development

The user requested image generation before further refinement. Two real calls
to the configured OpenAI-compatible relay used the requested model identifier
`gpt-image-2.5-flare`: one generation, then one image edit. Both used the
unmodified imagegen skill CLI, 1536 × 1024, high quality, opaque PNG output.

- `output/imagegen/architecture-concept-v2.png`: first generated concept.
- `output/imagegen/architecture-concept-v3.png`: edited concept with a white
  background and corrected service boundary.
- `planning/architecture-imagegen-v2-prompt.txt`: generation prompt.
- `planning/architecture-imagegen-v3-edit.txt`: edit prompt.
- `output/imagegen/provenance.json`: request settings and asset hashes.

The generated concepts are internal design drafts, not evidence or
submission-cleared artwork. Their remaining technical errors are documented
in the review. They are not embedded in the paper. The vector reconstruction
retains the folder/page/stack vocabulary and semantic colors while correcting
the topology and labels against the existing architecture brief and source
ledger. Final venue-specific AI disclosure and submission eligibility must
be checked by the authors before submission.

## Rebuild and edit

```powershell
python tools/draw_architecture_v2.py
latexmk -xelatex '-outdir=.' '-auxdir=.' -interaction=nonstopmode -halt-on-error main.tex
latexmk -xelatex '-outdir=.' '-auxdir=.' -interaction=nonstopmode -halt-on-error anonymous-preview.tex
```

The generator needs reportlab, svglib and pymupdf. It uses Arial and Arial Bold
from Windows, or accepts `--font` and `--bold-font` paths. The drawing is
504 × 422 pt (7 inches wide); label sizes are 8.2, 9.2 and 11 pt. Its PDF is
vector-only with embedded fonts; the PNG is rendered from that PDF at 216 dpi.
Open the SVG in Inkscape or Illustrator for manual editing. Changes made in
the generator are reproducible; preserve a sibling copy when editing the SVG
directly because regeneration overwrites it.

The drawing intentionally shows three clients instead of one repeated box to
make private state visible. Blue means shared immutable state or its local
reader; amber means private state and its upload-related path. Pale slanted
faces illustrate pages and objects without gradients or image-model pixels.
These are deliberate style exceptions to the generic figure skill's flat,
single-accent default, following the user's request for a more vivid figure.
Multi-bend connectors keep labels clear. Colors also have text and shape cues.

## Scientific scope

- A private upper permits lower inheritance only where visible; deletion does
  not cause fallback. The illustrative cross on an upper page denotes deletion.
- Each workspace has its own Packed reader. Shared snapshot objects do not
  imply a shared reader daemon or a shared writable upper.
- Upper metadata and control remain in a mutable service. Private payload
  objects are separate. The producer and mutable service are outside the
  logical object-store boundary.
- Upper/control and payload edges are shown once for clarity; every client
  has both. Request arrows omit response paths.
- Finalized-object hints remain integration work; smaller-q writes are gated.
  The effective B/q layout is persisted by the backend. The cells and ellipses
  do not specify numeric sizes or a fixed B/q ratio.
- Whole-object upper reads, incomplete runtime qualification and the absence
  of performance evidence remain explicit in the caption and manuscript.

Validation is recorded in `validation/architecture-v2/`.
