# Figure 1 coordination pass

The previous PNG and complete plotted-data manifest were saved before editing
as `before.png` and `before-plotted-data.json`. The figure retains its single
column dimensions, 3.3 by 2.9 inches (237.6 by 208.8 pt).

Changes are visual only:

- Shared Core/Exploratory legend; a/c title baseline aligned, a/b title left
  edges aligned, all three titles use the same 9 pt bold style.
- Local Error key sits on its own row under Call mix. Finite diagonal strokes
  distinguish errors from the unhatched white >64 KiB size interval in b.
  The error share is included in each bar's total, as before.
- The size key is directly under Request sizes and carries the KiB unit.
  Axes explicitly distinguish All calls, R/W calls, and Task calls (%).
- Uniform muted gray spines, ticks, vertical grids, and leader lines.
- Left plot areas retain an equal 60 pt width. The right plot grows from
  49 to 101 pt by placing task names inside its otherwise unoccupied low
  percentage region. Its scale remains 0–100%, and all eight points remain.
- No zero-origin bars are implied by c's leader lines: each leader begins
  three points after its task label and terminates at the measured marker.

All eight observed burst fractions are at least 47.4%. Label clearances were
measured after rendering, using marker edge rather than center. Requests is
the closest case at 5.155 pt; the script requires at least 3 pt for every
task. Labels do not cover observations or crop away the low percentage
region. `task-label-clearances.json` records every clearance.

QA on the final PDF:

- Plotted-data equality: PASS. Before/after JSONs are identical, including
  all 1,138,884 events, eight class records, twelve size-bin records, all
  eight tasks, denominators, intervals, and the empty exclusion list.
- Rendered panel alignment: PASS, 3 comparisons, zero exceptions. Left
  areas share their x bounds; c shares a's top and b's bottom.
- PDF font audit: PASS, minimum 8.5 pt, no smaller text runs.
- PDF collision audit: PASS, 36 visible text boxes, 81 stroke paths,
  zero failures and zero warnings.
- Source preflight: no failures. Generic warnings concern the intentional
  vector-first/no-TIFF export, 300-dpi preview, and requested 83.8-mm width
  instead of the validator's Nature-oriented width default.
- Inspected the complete 300-dpi PNG and a separate 100-dpi screen-size QA
  image. The latter is only a viewing proof, not a manuscript raster export.

The original statistics, derived files, task order, colors, marker types,
and reference data are unchanged. No section, caption, or manuscript build
was edited or run in this subtask. Captions should describe hatched errors,
not white-only error segments.
