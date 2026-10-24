# Embedded figure review

Date: 2026-10-23.

- Canonical manuscript: repository-root `main.tex`, following the current repository layout.
- Updated system schematic: `figures/system-architecture-rewritten.png`, included by `figures/architecture.tex` at 7 inches wide. Native image is 1774 × 887 pixels; placed size is 504 × 252 points.
- Combined workload figure: `figures/agent-fuse/fuse-combined-compact.pdf`, 7 × 2.75 inches, vector text at 9.5–10.5 pt. Source observations and detailed legacy figures are retained.
- Main PDF: 16 pages. Figure 1 is on page 3; Figure 2 is on page 5. Captions and references match the revised assets.
- Both `main.tex` and `anonymous-preview.tex` compiled with latexmk/XeLaTeX, exit status 0. Final main log has no undefined references or overfull boxes. Existing underfull-box notices remain outside the scope of this figure revision.
- Inspected the rendered main-document pages 3 and 5 at 108 dpi: no clipped figures, overlapping captions, or figure/page-boundary overflow. The workload grouping, error segments, size-bin legend, task names and burst metric remain legible. The accepted system schematic has no central File interface bar.
- Generation prompts and provenance are retained under `output/imagegen/architecture-rewritten-v3/`; the system figure remains an AI-generated internal design schematic, with no quantitative results drawn by imagegen.
