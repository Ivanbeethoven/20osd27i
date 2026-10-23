# Compact figure revision — 2026-10-23

The author requested substantially smaller data figures and a compact technical
methods diagram informed by published OSDI papers. Actual reference pages were
downloaded and visually inspected: Oxbow (OSDI 2026) Figures 3/5/6, DeLFS
(OSDI 2026) Figure 3, WOLVES (OSDI 2025) Figures 3/5, and SquirrelFS (OSDI 2024)
Figure 2. URLs, design lessons and source mappings are in
`planning/architecture-compact-brief.md`. Reference artwork was not copied.

## Dimensions and evidence

All dimensions are at the final 7-inch manuscript width; typography is not
downscaled by LaTeX.

| Figure | Before height | Final height | Height reduction |
|---|---:|---:|---:|
| Method/size profile | 5.05 in | 2.45 in | 51.5% |
| Per-task cumulative calls | 2.95 in | 2.00 in | 32.2% |
| System/methods diagram | 422 pt | 230 pt | 45.5% |

The profile has one row of four panels. Its method panels share label order and
have equal widths; its wider ECDF panels also have equal widths. All share top
and bottom bounds. Explicit comparable-pair groups make the unequal width
intentional and auditable; the alignment tolerance remains 1.5 pt. Errors,
metadata stars, both denominators, exact request sample counts, byte-labelled
write ticks and all observations remain. Temporal legends use repository names;
exact task IDs remain in the companion table and data files. No data, bins,
events or time windows were removed or recomputed.

The architecture exposes Present/hidden/fallback name resolution and explicit
LowerRange/Data/Hole byte mappings. A LowerRange edge enters the frame path
without forcing a new name lookup. The representative directory-name route
shows manifest roots, a paged index, GroupMeta fields and a data locator.
The backend panel distinguishes finalized object length, an unintegrated hint
edge, admission, persisted B/q/d/p and read/repair geometry. Its 2+2, s=2q sketch
matches an eligible selector case, not every object. Whole-object upper
verification and smaller-q write gates remain visible. Repeated clients,
decorative folders and producer internals are omitted rather than miniaturized.

## Validation

- Final PDF font audits pass: minimum 8.0 pt for all three changed figures.
  Minimum Arial text measured after manuscript inclusion is 8.00016 pt.
- Profile/time alignment audits pass with no warnings. All three PDF collision
  audits pass with zero failures and zero warnings. Pale box fills containing
  text are intentional, not obstructing overlays.
- SVG audit passes with the single expected width warning: the skill recognizes
  Nature's 89/183 mm presets; this USENIX figure correctly uses 177.8 mm (7 in).
- Plot-source preflight: 18 pass, 3 warnings, 0 failures. Warnings concern
  PNG/TIFF, 300/600 dpi preview defaults, and static recognition of the explicit
  positive-size assertion. The paper uses vector PDFs; no zeros were dropped.
- All final pages of both PDFs were rendered and reviewed as contact sheets;
  the changed figure pages were also inspected at page scale. No clipping,
  overlapping labels or missing glyphs remain in the changed figures.
- Windows XeLaTeX/latexmk builds pass for main and anonymous-preview. Both are
  15 pages with body ending on page 13 (previously 16/14). Figures 1 and 2 share
  page 3, Figure 3 is on page 5, and the unchanged lower-path figure is on page 7.
  Local `[!t]` permits compact placement; no global typography/margins changed.
- All fonts are embedded, with no Type 3 fonts. Logs have zero unresolved
  references/citations, overfull boxes or missing characters. Underfull notices
  remain: 55 main, 56 anonymous-preview. Some vertical spacing is still uneven.
- `preservation-check.json` confirms the analyzer, every derived file, abstract
  and draft status, and evaluation plan match the starting bytes. No experiments
  were run and no performance or novelty claims were added.

The body still exceeds the recorded 12-page initial-submission budget by one
page. The neutral-name preview retains one existing BrewFS occurrence and one
source identity in implementation-audit prose; it is not fully anonymized.
This revision improves presentation and does not certify submission readiness.

## Active outputs

- `paper/figures/agent-fuse/fuse-profile.{pdf,svg,png}`
- `paper/figures/agent-fuse/fuse-time.{pdf,svg,png}`
- `paper/figures/system-architecture-compact.{pdf,svg,png}`
- `experiments/agent-fuse-observations/plot.py`
- `tools/draw_architecture_compact.py`
- `paper/sections/02-agent-observations.tex`
- `paper/sections/03-overview.tex`, `paper/figures/architecture.tex`
- `paper/main.pdf`, `paper/anonymous-preview.pdf`

`before.json` preserves the starting working-tree hashes and figure dimensions;
`pdf-inspection.json`, font/collision JSONs and build logs preserve final checks.
Earlier directories are historical audit snapshots, not current geometry.
