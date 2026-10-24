# Single-column figure review

Date: 2026-10-23.

- Both main figures now use `figure` and `columnwidth`, replacing double-column placement.
- Workload figure: `figures/agent-fuse/fuse-single-column.pdf`; native size 3.3 × 2.9 inches, vector text 8.5–9 pt. Panel a/b are stacked left, panel c spans the right. New and previous plotted-data JSON are identical; all categories, errors, size bins, and eight tasks are retained. Source-level alignment, font, and collision reports are under `experiments/agent-fuse-observations/qa/single-column/`.
- Architecture: `figures/system-architecture-single-column.png`; 1254 × 1254 pixels, placed at approximately 240.12 × 240.12 points. Figure area is about 55% lower than the previous 504 × 252 point double-column version. The architecture image is raster; its text does not have auditable PDF font operators. Do not apply the workload figure's 8.5–9 pt claim to the architecture.
- Architecture information retained: two views, private states, S, range mapping kinds, private payload, Native/Packed alternative, direct read-only use, joint metadata fields and locator/frame relation, g choices and tails, object formation and L_o, distinct producer paths, default/hinted backend, stored B and shard q. Repeated labels/sample records were condensed. Two U1 labels identify the same payload, as stated in the caption.
- Both named and name-switching manuscripts compiled successfully with latexmk/XeLaTeX; 16 pages each. Final logs contain no undefined-reference, overfull-box, or missing-character findings. Existing underfull notices remain.
- Rendered actual main-document pages 2 and 5 at 108 dpi and visually checked placement. Figure 1 is on page 2 and Figure 2 on page 5. No clipped figures or caption/text overlap. Architecture is materially denser at single-column scale; its generated label text remains raster, while the workload figure remains vector.
- All imagegen prompts and provenance are retained under `output/imagegen/architecture-single-column-v4/`. Built-in imagegen reference-edit mode was used; underlying model version is not exposed by the tool.
