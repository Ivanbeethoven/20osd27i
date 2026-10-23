# Editable BrewFS system figure

The current single-column figure introduces familiar file concepts before storage-format terminology. It retains the three formal mechanism names and numbered headings.

- `system-architecture-editable.svg`: edit labels, groups, shapes, and connector paths in a vector editor. Stable group IDs identify each component. Numeric subscripts are separate smaller text runs to avoid missing Unicode glyphs.
- `system-architecture-editable.pdf`: fully vector paper export, included by `architecture.tex`.
- `system-architecture-editable.png`: preview only.
- `../tools/draw_architecture_editable.py`: reproducible scene source; rerunning it overwrites all three exports. Keep lasting geometry or label changes in this source, or export a separately edited SVG under a new filename.

The canvas remains **240 × 258 pt (84.67 × 91.02 mm)**. The paper includes it at column width. Ordinary labels are now at least **7 pt**, the three headings are **8.5 pt**, and true subscripts are at least **5.32 pt**. Arial regular and bold are embedded in the PDF.

## Reading the diagram

1. FUSE operations enter each workspace view. Each view resolves private state first and holds a pinned reference to an immutable shared baseline. New private bytes are separately referenced; baseline connectors do not imply writes.
2. Native records and a packed snapshot are alternative baseline representations. Directory `/src` and entry `main.py` illustrate joint name, attribute, and data-reference fields in an indexed metadata page. A second schematic row indicates multiple records. The selected record references file bytes; the caption identifies a separate-byte example, not a claim that inline data is impossible. Descriptor resolution is expanded in Figure 3.
3. A selected logical chunk contains a written slice range. An expanded slice is partitioned into configured upload blocks, including a short tail. Applicable compression/framing determines each object's finalized length. `g` is a fixed configuration, not an online adaptive policy. `U₁` and `Oₚ` match the upper-panel payloads and bypass ordinary object formation. The backend selects and persists its effective EC block `B` and per-shard verification/read quantum `q`; the dashed `B` hint does not control `q` or guarantee acceptance.

Orange denotes private workspace state/data; blue denotes shared immutable records/data; gray denotes ordinary object formation and backend layout. Agents share the same neutral icon styling. Labels, grouping, and solid/dashed connectors also encode meaning.

Local review records use `validation/architecture-academic/` for semantic, font, collision, and rendered checks, and `validation/figure-coordination/` for caption/whole-paper checks. These local QA outputs are not included in this source update and are not required to compile the paper. The generator writes fresh scene and preview checks under `validation/architecture-editable/` when run.
