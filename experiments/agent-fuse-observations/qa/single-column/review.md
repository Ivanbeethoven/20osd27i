# Single-column rendering QA

- Final PDF: 237.6 x 208.8 pt (3.3 x 2.9 in).
- Final editable PDF/SVG text: 8.5-9 pt; font audit minimum 8.5 pt, zero
  text runs below the requested threshold.
- Alignment: PASS, three physical comparisons, zero exceptions. Left plot
  areas share x = 51..111 pt. Right spanning area shares the top of a and
  the bottom of b. The narrower temporal area uses the same 0-100% scale.
- Collision audit: PASS, zero failures and zero warnings across 35 text
  boxes and 80 stroke paths. Re-export followed the initial clipping fixes.
- Visual inspection: all four classes and their error overlays, all four
  size bars with three intervals, and eight individually labelled task
  markers remain visible. Right-axis 100 and the multiline temporal label
  have page margins; the full Metadata label is retained.
- Complete plotted-data JSON equality with the prior compact rendering
  confirms unchanged totals, bin boundaries/counts, and all task bursts.
  There is no sampling, exclusion, pooling of task markers, or synthetic data.
- Source preflight: zero FAILs. Three generic warnings are intentional:
  no TIFF is needed for a vector manuscript plot; PNG is a 300-dpi preview;
  83.8 mm is the requested systems-paper column width rather than the
  Nature-style 89 mm default.
- Statistical limits remain as documented: one capture per task, no
  independent replicates or confidence intervals, and group differences
  confound repositories, prompts, and time budgets.
- Main-manuscript compilation and page placement are delegated to the
  coordinating task, so this report does not claim a page-placement check.

Reproduce with Python and the dependency versions in the experiment
requirements, then run `plot_single_column.py`. The `--qa-scripts` option
selects the nature-figure alignment validator. The final manuscript uses
`figure` and `width=\columnwidth` rather than the wide figure float.
