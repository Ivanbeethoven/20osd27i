# Architecture draft review (2026-10-23)

Only the new shared-base draft, generator, caption, brief and this audit directory
were authored in the target repository. Existing manuscript edits were retained.
No main/anonymous manuscript was rebuilt because this turn produces a reviewable
figure design rather than replacing the active paper figure.

Canvas: 504 × 230 PDF points, equal to the previous compact figure. Live Arial
text: 8–9 pt. Main area and inset intentionally have unequal widths because they
serve different explanatory roles; statistical-panel alignment is not applicable.
Repeated workspace rectangles and A/B/C cells share dimensions and y coordinates.

The final PNG was visually checked at full composition scale. The PDF collision
audit found zero failures and zero warnings. Its contained text/fill overlays are
intentional labels inside nodes and cells. The SVG audit uses an 8–9 pt contract;
the remaining 177.8 mm width warning is a Nature-preset mismatch, not a clipping
or OSDI size error. Text remains live in SVG and embedded in PDF.

Independent review prompted explicit mutable metadata labels, private payloads
outside the workspace view boxes, an aligned A/B/C overwrite example, and a
default-off label for smaller q. The caption states object-storage placement,
the upper whole-object read policy, other Packed access routes, and integration
limits. The illustration is not a measured workload or performance result.

Canonical source: tools/draw_architecture_shared.py. Geometry ledger: scene.json.
Automated reports: svg-audit.json, font-audit.json, collision.json.
