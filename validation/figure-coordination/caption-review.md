# Figure caption compression review

Initial compression: 2026-10-23. Synchronized on 2026-10-24 with the redesigned
Figure 2 and its latest caption. The original compression revised the three
active figure captions and immediately corresponding observation prose.
This synchronization changes only this review document, not TeX or figures.
Historical captions, table captions, and data remain outside this task's scope.

## Word counts

| Active figure | Source | Before | After | Target |
|---|---|---:|---:|---:|
| 1: measured FUSE observations | `sections/02-agent-observations.tex` | 103 | 41 | 40–55 |
| 2: system overview | `sections/03-overview.tex` | 131 | 45 | 40–60 |
| 3: packed lookup/read path | `sections/05-packed.tex` | 51 | 26 | 20–35 |
| **Total caption text** | | **285** | **112** | |

The current captions lose 173 words (about 61%) against the initial 285-word
baseline. Figure 2 was initially compressed to 54 words and now has 45 words;
Figures 1 and 3 remain unchanged. Baseline counts refer to the actual captions
read at the start of compression, rather than earlier longer versions. Counts use
whitespace-separated visible words/tokens after removing TeX command wrappers;
hyphenated/slash compounds and standalone mathematical symbols count as one
token, and a section reference counts as its displayed number. Figure labels
added by LaTeX are excluded. Line wrapping does not change the count.

## Figure 1

The 41-word caption retains a/b/c meanings, within-method/group size
normalization, each task's busiest 10% of one-second windows, and bar order.
**Error segments are described as hatched**, matching the concurrent plot edit;
the old white-error wording was removed so it cannot conflict with white >64 KiB
segments in panel b. No metric or denominator changed.

Already present in the adjacent text and therefore removed from the caption:

- Five Core/three Exploratory runs; 1,138,884 events; group totals; all statuses;
  setup/canary/teardown; request weighting: Capture and scope.
- At-most-4-KiB and (4,64]-KiB boundaries and observed fractions: request sizes.
  The plotted interval key retains the complete partition, including >64 KiB.
- FUSE request lengths are not object sizes: the existing measurement-boundary
  sentence in request sizes.
- Per-task rounding-up rule, all eight tasks, and confounded group contrasts:
  task and temporal heterogeneity.

Necessary information that had existed only in the caption was moved into the
existing relevant paragraphs, without creating a new explanatory paragraph:

1. The six metadata methods and the complement defining Other now appear in
   Metadata traffic and read dominance.
2. Read/write sample counts, their all-ok status, and KiB=1024 bytes now open
   A mixture of request sizes. Counts remain 22,142/98,292 reads and
   1,112/23,600 writes (Core/Exploratory).
3. Inclusion of zero-call and final partial windows now appears immediately
   before the busiest-tenth statistic.

Evidence remains the unchanged validated derived summary, exact size histograms,
task table, and complete one-second series. No observations were dropped.

## Figure 2

The final **45-word** caption matches the redesigned, introductory overview.
It retains optional composition, the metadata example's separately stored file
bytes, and the explicit statement that each ordinary raw block forms an object
after applicable compression/framing. Matched U1/Op ports retain separate upload
contracts; dashed B hints remain optional, backends persist effective layouts,
and the caption points to the implementation section. This final wording
replaces the preceding 45-word version without changing its word count.

The adjacent overview prose now explicitly separates a directory entry's name,
attributes, and data references from the file bytes they reference. It also
distinguishes logical file ranges from upload and encoding blocks. The figure
uses a familiar main.py record and one ordinary upload path rather than the
previous file-range-source strips and paired g1/g2 alternatives. Those old
elements must therefore no longer be described as present in this caption.

Removed repetitions remain explicitly defined in existing text:

| Removed caption detail | Existing definition retained |
|---|---|
| Private metadata and data mappings in Delta | Overview: representation-independent workspace contract |
| Sealed native versus packed lower; standalone read-only use | Overview contract and examples; Packed optional-representation subsection |
| Directory/name indexing, joint records, authenticated descriptor resolution | Packed fetching/verifying subsection and the representative-path caption; the new overview makes the field-versus-bytes distinction explicit |
| Final length after applicable compression/framing; short tail | Layout: distinct boundaries and forming objects from file updates |
| Producer-specific upload contracts | Layout: composition and scope; Implementation: remaining connections |
| Backend validates B hints; q has independent admission gates | Layout: optional backend layout, explicitly stating separate compatibility gates; Implementation: object formation and layout gates |
| Fixed client g and alternative configurations | Layout: forming objects from file updates; the current figure shows configured g rather than separate g1/g2 rows |
| One-complete-stripe logical shard size s | Layout: optional backend layout; s is not separately labeled in the new simplified drawing |
| Research-backend scope and limitations | Implementation, explicitly referenced by the caption |

The caption does not explain every internal label again. Separately stored
bytes, the per-raw-block object relationship, and matched ports remain because
they define the examples in the drawing. Chunk/slice ranges and backend B/q
geometry remain labeled in the figure and defined in the adjacent overview and
layout section. A simplified caption does not imply all files require external
data objects, B determines q, hints are always accepted, or all producers share
ordinary upload geometry.

## Figure 3

The 26-word caption identifies a representative lookup/read path, joint
metadata/data locator, and descriptor-mediated fetching and verification.
Standalone read-only/workspace-lower uses already appear in the section opening.
Different operations' indexes remain described immediately below the figure.
Cold lookup traversing multiple pages and additional descriptor/payload requests
are still explained in the caching paragraph, so the caption no longer repeats
the non-fixed-GET-count qualification.

## Checks and handoff

All three existing figure labels/references and inclusion commands are retained.
The scope was checked against the active main-document inputs. All three caption
lengths were recomputed on 2026-10-24; Figure 1 still says hatched rather than
white. The updated system PNG was inspected independently. Its name/attributes/
data-reference example and shared/private distinction are substantially clearer.
The parent task adopted the readability refinement: Compress & frame now sits
above the Upload blocks-to-Objects arrow, and the separate per block label was
removed. The final caption states the per-raw-block relationship instead, so
the processing order is explicit without adding another graphic label.
The parent also confirmed main graphic text of at least 7 pt, headings of
8.5 pt, and the unchanged 240 x 258 pt canvas. No TeX or figure edit was made
during this final documentation synchronization. Compilation and rendered-page
QA remain with the parent task.
