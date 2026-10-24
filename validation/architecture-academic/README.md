# File-first architecture redraw — 2026-10-24

## Intent and scope

Keep the accepted single-column footprint while explaining metadata and ordinary file-object formation to readers who do not already know the implementation. Update only the figure, its reproducible source, its caption and immediately adjacent overview explanation. Figure 1 coordination and caption compression are recorded separately in `../figure-coordination/` and `../../experiments/agent-fuse-observations/qa/coordinated/`.

## Label and concept review

| Displayed words/symbols | Meaning and paper basis |
|---|---|
| 1; Delta-Based Multi-Agent Workspaces | Formal mechanism name, Section 4. |
| FUSE; View W₁ / View W₂ | File-operation entry into a task's resolved filesystem view, Sections 2–4. |
| Private state Δ₁ / Δ₂; resolve private first | Current private namespace/attribute/deletion/mapping state. Lower inheritance occurs only when this state permits it, Section 3.2. It is not a transient buffer or byte-difference log. |
| Private bytes U₁; U₁ | Separately referenced private payload; matching labels denote the same schematic payload across panels. U₁ is a local figure reference, not a new paper variable. |
| Shared immutable baseline S; pinned | Stable baseline identity shared by workspaces. Undirected references avoid a write-to-S interpretation. Section 3.2. |
| 2; Packed Metadata | Formal mechanism name, Section 5. |
| Native records; or; Packed snapshot | Alternative baseline representations; Packed is not compulsory, Sections 3 and 5. |
| Read-only; mount | A packed snapshot also supports standalone read-only use, without a private workspace. |
| Name-range; index; dir: /src | Directory context and raw-name intervals select a bounded page. `/src` supplies context; it is not the Name field. Section 5. |
| Packed metadata page; Name; Attributes; Data ref. | Joint records co-locate entry names, common attributes, and logical data-location information. The selected row spans all three fields. Multiple schematic rows avoid implying one file per page/object. |
| main.py; size, mode | Familiar entry-name and attribute examples, not benchmark inputs or measured values. `mode` includes type/permission bits. |
| Data object; Bytes; Oₚ | A representative separately stored payload. The caption makes the separate-byte example explicit; inline contents remain possible. A data-reference arrow abstracts authenticated descriptor resolution, expanded in Figure 3. Oₚ is a matched schematic payload reference. |
| 3; Variable-Granularity Object Storage | Formal mechanism name, Section 6. |
| Ordinary file offsets; Chunk; address range | A chunk is a logical addressing range, not a file, remote object, or backend EC block. Section 6.2. |
| Slice: written range | A written interval inside the selected chunk. The connector magnifies that interval; it does not imply one write always creates one slice. Section 6.2. |
| Upload blocks; configured g | Slice data is partitioned using fixed client configuration g; the last depicted block is short. This is not a runtime adaptive algorithm. Section 6.2. |
| Compress; & frame; Objects; length Lₒ | Applicable formatting occurs after partitioning. Each raw block forms an object, whose final upload length is Lₒ. The caption supplies the applicability and per-block qualifiers. g and Lₒ are not equated. Section 6.1–2. |
| Backend selects layout; RustFS; EC block B | Compatible research backend validates any hint and persists the effective coding layout. Section 6.4 and Section 7 implementation limits. |
| Per-shard verify/read q | Physical verification/read quantum within a backend shard, distinct from file ranges, g, Lₒ and B. Detailed stripe span and admission constraints remain in Section 6.4. |
| B hint; optional | Dashed path denotes an optional encoding-block hint based on final object length. It does not set q or guarantee acceptance. U₁/Oₚ enter storage separately, avoiding a false common uploader/hint-policy claim. |

The total is **52 logical label occurrences / 49 distinct labels / 61 editable SVG text elements**. Subscripts account for the element split. The historical 56-label word audit has been frozen to its own `after-scene.json`.

## Visual decisions

- Canvas unchanged: **240 × 258 pt**, included at column width.
- Body labels raised from a 6.2 pt minimum to **7 pt minimum**; headings 8.5 pt; true subscripts 5.32 pt or larger.
- Orange: private state/payload. Blue: shared immutable records/payload. Gray: ordinary formation/backend. Color is redundant with labels and connectors.
- GroupMeta implementation type, frame-descriptor fields, LowerRange/Data/Hole enums, and shard span s remain in the relevant sections and Figure 3. Removing them from the overview makes room for the concepts they rely on; no implementation claim is changed.
- Applicable compression/framing sits above the upload-block-to-object arrow, not adjacent to the slice expansion. The caption states the per-block relation.

## Checks

- Figure exports are live vector/text; PDF contains zero raster images.
- SVG/font checks: no undersized text or missing glyphs; the sole SVG width warning is the skill's generic Nature 89/183 mm preset. This paper uses an 84.67 mm figure canvas.
- Collision check: **0 failures**. Three warnings result from PDF extraction merging each numbered circle with its adjacent heading. Visual review confirms the numerals sit inside their circles and the headings outside.
- Figure 1's plotted data remain exactly equal: 1,138,884 events, eight tasks, no exclusions. Its alignment/collision checks passed.
- Current caption lengths are **41 / 45 / 26 words**, versus 103 / 131 / 51 before this round. Supporting definitions stay in adjacent prose.
- Main and anonymous manuscripts are compiled and their three figure pages rendered for final placement checks. `../figure-coordination/integrated-pages.json` records page numbers and preview paths; build logs are adjacent.

`before.*`, `before-source.py`, and `before-scene.json` preserve the previous design. `after-scene.json` is the current label/edge inventory. The user-facing figure remains at its existing include path.
