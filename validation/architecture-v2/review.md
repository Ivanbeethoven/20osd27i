# Architecture v2 validation

Date: 2026-10-23. Technical review and image-generation provenance are in
`planning/architecture-imagegen-review.md` and `output/imagegen/provenance.json`.
The unchanged source-level architecture brief and manuscript Sections 3–7
govern the scientific content.

- Actual image API generation and edit completed successfully using the
  configured relay model identifier `gpt-image-2.5-flare`. Generated candidates
  remain distinct from the corrected editable vector asset used in Figure 4.
- SVG audit: 0 failures. The only warning is the generic Nature-width heuristic;
  this USENIX figure uses the actual 7-inch (177.8 mm) text block.
- Final PDF font audit: minimum 8.2 pt. Arial and Arial Bold are embedded;
  no Type 3 fonts, outlined labels or raster images in the architecture PDF.
- Final collision audit: 0 failures, 0 warnings. Its 35 contained fill overlays
  are intentional labels in folders, storage groups and contribution badges.
- Scene measurements verify text bounds. The three clients use equal folder
  dimensions and aligned labels. This is one logical schematic, not comparable
  statistical panels; statistical alignment/uncertainty tests do not apply.
- Manual review checked arrow endpoints and the separation of private state,
  client-local readers, shared objects, metadata service and producer. A plain
  blue/amber line crossing has no connection dot and denotes separate requests.
  The geometric bracket spans one block; the q bracket spans one cell, with
  ellipses and a schematic note avoiding a numeric size or fixed-ratio claim.
- Caption explicitly states representative upper/control and payload edges,
  pending hint wiring, smaller-q gating, and whole-object upper integrity reads.
- Windows XeLaTeX/latexmk successfully rebuilt the named and neutral-name PDFs.
  Both remain 16 pages with Figure 4 on page 6. Final logs contain no unresolved
  citations/references, overfull boxes, missing glyphs or LaTeX errors. All
  manuscript fonts are embedded. See `pdf-inspection.json` for output hashes.
- Final page 6 and its surrounding pages were rendered for visual inspection;
  the diagram and caption fit without clipping. Earlier full-document review
  remains applicable to unchanged sections. Existing submission-length and
  anonymous-preview limitations are unchanged and recorded in the main report.

No new workload data, performance measurements, causal results or runtime
qualification claims were added during this visual revision.
