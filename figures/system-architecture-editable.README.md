# Editable BrewFS system figure

The current single-column figure places metadata access and data access in parallel beneath the view choice. It retains the three formal mechanism names and explicitly identifies all three as independently optional.

- `system-architecture-editable.svg`: editable labels, groups, shapes, and connector paths. Stable group IDs identify each component.
- `system-architecture-editable.pdf`: fully vector paper export, included by `architecture.tex`.
- `system-architecture-editable.png`: preview only.
- `../tools/draw_architecture_editable.py`: reproducible scene source; rerunning it overwrites all three exports. Keep lasting geometry or label changes in this source, or export a separately edited SVG under a new filename.

The canvas is **240 × 280 pt (84.67 × 98.78 mm)**, included at column width. Labels are **7–8.5 pt**. Arial regular and bold are embedded in the PDF; it contains no raster objects.

## Reading the diagram

1. Agents enter through FUSE. The left line bypasses workspace composition and rejoins the shared metadata and data paths; an ordinary volume needs no separate box. Workspaces resolve private state first and pin a shared immutable baseline. The dashed legend uses the same numbered badges as the three mechanism headings.
2. Native records and a published read-only pack are alternative lower representations. The joint page groups names, attributes, and data locators; its example record is `file A`. A standalone read-only mount reaches the name-range index directly. Locators reference existing file bytes. Figure 3 expands descriptor and payload resolution.
3. The ordinary BrewFS uploader forms objects under fixed client geometry g. Object bytes cross a solid arrow to RustFS; a separate dashed arrow carries an optional B hint. The **RustFS optimizations** region explicitly identifies our backend changes: per-object coding-block selection and finer shard verification units q. Two equal schematic extents illustrate alternative coding-block sizes, with unpadded tails. One complete B block expands into shards, with q marking a unit within a shard. RustFS admits and persists the actual geometry; B and q have separate backend gates, and q is selected by RustFS. The current automatic hint can retain the default B. Producer coverage and policy details are in Sections 6–7.

Orange identifies private workspace state and the optional layout hint; blue identifies shared immutable records/data; gray identifies object formation and backend layout. Arrow style and labels distinguish the hint from payload delivery without relying on color. The numbered regions map to Sections 4–6.

Current scene, font, collision, and SVG checks are under `validation/architecture-editable/`. The 2026-11-03 revision preserves the connected architecture after the author rejected the stacked-card redesign. The first mechanism heading stays on one line at 8.5 pt. QA files are not required to compile the paper.
