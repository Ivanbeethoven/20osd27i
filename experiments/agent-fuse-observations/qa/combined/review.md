# Combined workload figure review

## Scope

Only the workload figure, its reproduction documentation, and corresponding
manuscript figure references/caption were revised. The original method, size,
profile, and time exports are unchanged. No source or derived observation was
changed. This is a new evidence composition with style-only reuse of the
existing Python workflow and group palette.

## Verification

- All 1,138,884 calls and all eight tasks retained; Core 217,129, Exploratory
  921,755. Binning is explicit in the contract and caption. Every drawn aggregate
  is in `plotted-data.json` and checked against validated source summaries.
- Burst fractions recomputed from complete 1-s series, including zero windows
  and the final partial window; all eight agree with the task table.
- Figure: 504 x 198 pt. Equal plot areas: 102 x 112 pt. Repeated gutters: 65 pt.
  Render-time alignment passes at the unchanged 1.5-pt tolerance.
- Actual PDF text: minimum 9.5 pt, no smaller glyphs.
- Final PDF collision audit: zero failures and zero warnings.
- Source preflight: 19 pass, zero fail. Its two raster warnings are intentional:
  vector PDF is included in the manuscript; PNG is a 300-dpi preview, and TIFF
  is not an intended output.

## Visual review at manuscript width

The 7-inch placement proof was inspected as a whole and panel by panel. Names
and axes are readable, titles and axes align, legends do not intersect marks,
and no text is clipped. Groups have consistent hue and fixed bar order; panel c
adds distinct shapes. Size fills are monotonic and distinguishable in grayscale;
the caption states bar order if group hues cannot be distinguished. White means
error in a and >64 KiB in b; separate keys and the caption state the distinction.

Panel a includes every status and does not equate error with agent-task failure.
Panel b compares within-method request distributions, not object sizes. Panel c
keeps one marker per measured task. No uncertainty bars are appropriate for
complete descriptive captures with one observation per task.

Companion ECDFs and time curves retain detail and ordering that the main figure
explicitly aggregates. The figure does not imply lossless reconstruction of
those curves, cross-task sharing, sparse mutation, or any performance gain.
