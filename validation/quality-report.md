# Current artifact quality report

Date: 2026-10-23. This revision promotes the BrewFS manuscript to the repository root. The canonical entry is `main.tex`; `anonymous-preview.tex`, `sections/`, `figures/`, `references.bib`, styles, and reviewed PDFs are alongside it. `paper/Makefile` only forwards legacy make commands. The original starter is preserved under `templates/usenix-starter/`, and the official example under `templates/usenix-official/`.

## Preservation and scope

All eleven manuscript section files, all figure assets, the bibliography, official style, and derived workload observations are byte-identical to the local pre-move snapshot. The existing uncommitted combined workload figure and its observation-section references were retained and included in the root build. This revision changes paths, build entry points, documentation, and validation; it does not add system measurements or rewrite the scientific claims.

The previous root starter files are preserved exactly. Editable source and regeneration scripts now target `figures/`. Historical evidence and QA records retain paths as recorded at the time. The previous quality report is archived at `validation/root-layout/quality-before.md`.

## Validation

- Both documents build from the root with bare `latexmk` (XeLaTeX is selected in `.latexmkrc`). Output is `main.pdf` and `anonymous-preview.pdf` in the root.
- Both PDFs have 16 pages; the last numbered body section ends on page 14. The prior local combined-figure edit accounts for the difference from the older 17-page PDF.
- Both final logs have zero undefined references/citations, overfull boxes, and missing glyphs. All fonts are embedded, no Type 3 fonts occur, and extracted text stays within page boundaries.
- Both PDFs were rendered in full and visually inspected in contact sheets; the combined observation figure and caption were inspected at full-page scale. No clipping, overlap, or broken glyphs were found.
- Package validation passes: 29 BibTeX entries, 27 cited, RQ1–RQ7, and E00–E16 still planned. The official style hash remains unchanged.
- Root Makefile, legacy forwarding Makefile, README, script output paths, GitHub Actions, and PDF artifact paths agree with the new layout. Windows validation used latexmk directly; make forwarding was inspected rather than executed because make is not installed in this shell.

Details are in `validation/root-layout/preservation-and-pdf-checks.json` and `package-validation.json`. The PDFs remain author working drafts; the neutral-name preview is not a certification of submission anonymity or venue compliance. No BrewFS runtime, fault, or performance experiments were executed.
