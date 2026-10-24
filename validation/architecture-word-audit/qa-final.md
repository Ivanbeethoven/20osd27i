# Final export and manuscript QA

2026-10-23. This record applies to the final word-audited SVG/PDF/PNG and the root manuscript builds.

- Canvas remains **240 × 258 pt**, with the same single-column inclusion. No enlargement of the figure was used to accommodate revised wording.
- **56 logical labels, 73 live SVG text nodes.** Subscripts use separate, editable text runs. The PDF contains **zero raster-image objects**.
- Main labels remain 6.2–7.4 pt, mechanism headings 8.5 pt, and subscripts at least 5.2 pt. Font audit reports zero text below 5 pt.
- Rendered collision audit: **0 failures, 3 warnings**. Each warning combines a numbered badge and heading into one text bounding box; inspection confirms the intentional white numeral inside its dark circle and the separate heading do not collide.
- The SVG width warning concerns Nature-specific 89/183 mm presets. This manuscript deliberately uses 84.67 mm, matching the current USENIX single-column target.
- The final diagram and page 5 were inspected visually for labels, subscript glyphs, connector attachments, final-size readability, object/frame distinction, quantum annotation, and equal raw-data extent under the two fixed g choices.
- **Both main and anonymous manuscripts compiled successfully, each with 16 pages.** The updated system diagram is on page 5. Final logs contain no overfull boxes, missing characters, or undefined references. LaTeX's page-5 floats-only warning refers to the figure-heavy column; the rendered page has normal body text in the other column and no clipping.
- The semantic review found no remaining material label/connection error. This is a figure and source audit; no new system experiments or performance claims were introduced.

Evidence: `svg-audit.json`, `font-audit.json`, `collision.json`, `build-summary.json`, `main-page-05.png`, `anonymous-preview-page-05.png`, and `final-semantic-review.md`. Before assets are retained as `before.svg/.pdf/.png` and `before-scene.json`.
