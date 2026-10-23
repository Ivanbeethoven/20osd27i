# Architecture concept review

Date: 2026-10-23. Scope: revise the existing Figure 4 visually while preserving
its source-grounded scientific scope. The prior architecture brief remains the
component/edge authority. The user explicitly requested imagegen, then
authorized use of the configured image API relay and subsequent refinement.

## Generated concepts

The relay model list exposed `gpt-image-2.5-flare`,
`gpt-image-2.5-sunburst` and `gpt-image-2`, among others. The chosen request model
was `gpt-image-2.5-flare`. Calls used the unmodified imagegen CLI with credentials
loaded from local configuration in process memory, not written into the repo.
No raw workload records or full manuscript were sent: the payload was the saved
architecture prompt, and the second request also included the first generated
concept. No external reference artwork was used.

The first concept made private edits, repeated workspaces and layered sharing
more recognizable but introduced dark atmospheric shading, put the metadata
service inside RustFS, added a snapshot-to-metadata dependency, and mis-sized
the B/q brackets. It was rejected as a scientific figure.

The edit removed the dark background, separated mutable metadata, and improved
the geometry inset. It still placed the producer inside storage and retained
a duplicate center-workspace path that bypassed the local Packed reader.
It also omitted a clear client payload path. It is retained as a visual
reference, not as the paper architecture itself.

## Editable reconstruction

The final reconstruction uses original vector geometry and live labels, with
no embedded generated image. It adopts the concepts' three folder-shaped
workspaces, private edit sheets, local blue readers, layered snapshot and
object-layout detail. All connectivity is rebuilt from the architecture brief.

Corrections include separate mutable/producer regions; one reader per client;
one lower request path per reader; explicit representative upper/control and
private-payload requests; a single meaning for dashed lines; B spanning a
block, q spanning one cell; and an explicit schematic-size note. The backend
is responsible for validating and persisting effective geometry, as stated
in the caption. This is a logical dependency figure, not a timed pipeline.

The three repeated folder glyphs are deliberately equal in size and aligned.
Shallow flat storage/page faces and two semantic color families are deliberate
exceptions to generic flat single-accent style guidance, following the user's
visual request. There are no gradients, filters, shadows or outlined labels.

The paper uses the editable reconstruction in both named and neutral-name
PDFs. This remains an author-review architecture draft, with no new
performance or correctness claim. AI-art submission eligibility and exact
venue disclosure have not been certified by this drawing workflow.
