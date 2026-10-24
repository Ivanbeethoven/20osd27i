# Technical architecture revision, 2026-10-23

The user accepted the shared-base composition and requested a more technical,
concise paper style with larger relative labels, a concrete dynamic-block-size
mechanism, and an image_gen concept before deterministic redrawing.

## Authorized design choices

- Keep the final 504 × 230 pt footprint. Use Arial 9.5–10.5 pt rather than 8–9 pt.
- Preserve the two-private-views/one-S relationship; use short A/B′/C cell labels.
- Replace rounded frames with square 0.8 pt boundaries and 1 pt arrows.
- Use pale blue for inherited data and pale amber for private payload; backend
  geometry is neutral gray so it is not confused with a shared lower reference.
- Remove repeated frame identifiers, long implementation explanations and
  repeated block-size text. Put validity boundaries in the supplied caption.
- Allocate about 42% of the canvas to per-object EC layout. Two equal-width
  rows show a common 1 MiB byte domain under B=256 KiB and B=1 MiB fixed policies.
- Show an enlarged EC2+2 geometry inset for B=256 KiB, s=128 KiB, q=64 KiB.
  It uses its own visual scale; it is not aligned to the object-byte scale above.

## Image-generation provenance

Built-in image_gen was used on 2026-10-23. The tool did not disclose an exact
model-version identifier; none is inferred. The generated concept is retained
as output/imagegen/architecture-technical/concept.png, with the complete prompt.
Input 1 was the prior BrewFS figure; Oxbow Fig.3 and Umap Fig.5 were visual-style
references. Source references are the user's local PDFs. No source artwork is
copied into the final vector drawing.

Selected ideas: square technical boundaries, large short labels, an explicit
equal-byte-domain B comparison, and a subordinate shard inset. Manual corrections:
remove redundant numeric labels; keep image-model text out of the final figure;
use exact supported B/q geometry; distinguish fixed policy examples from auto;
keep integration and whole-object integrity boundaries in the caption.

This is an internal author-review design. Submission eligibility of generated
artwork was not asserted; the image serves as a composition reference.

## Semantic sources and constraints

Sources: sections/03-overview.tex through 06-layout.tex;
evidence/source_evidence.md; validation/architecture-technical/dynamic-audit.md.

- Δ contains private current state in the metadata service. U is a private object
  in object storage. Workspace rectangles depict logical views, not processes.
- Lower inheritance is explicit. The diagram's focused overwrite example omits
  Hole and namespace branches; the caption points to their actual rules.
- The lower route is representative; direct inherited reads need not repeat a
  name lookup. No fixed GET count, sharing frequency or performance gain is shown.
- The B comparison deliberately holds the illustrative object length fixed.
  Different fixed policies are supported. It does NOT infer a small-object/small-B
  and large-object/large-B decision rule from the current auto implementation.
- Current auto omits a hint for objects <=1 MiB, and requests 1 MiB above it;
  backend default B is also 1 MiB. Per-object configurability is not an optimizer.
- q must fit shard geometry; smaller-q writes are eligible, gated and default-off.
  Reads/repair use stored metadata rather than choosing a fresh B/q per request.
- Packed authentication/compression frames, B coding blocks and q verification
  quanta are separate scales. The shard inset is enlarged independently.

The SVG and caption form one review unit. Essential limitations must remain
in the caption if the short diagram is inserted in the manuscript.
