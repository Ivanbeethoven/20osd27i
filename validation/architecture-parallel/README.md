# Parallel, independently optional architecture — 2026-10-24

The user requested explicit 1→2 and 1→3 relationships with every mechanism optional. The revision replaces three stacked sections with a view choice above parallel metadata and data paths.

## Structure and evidence boundaries

- FUSE reaches either an ordinary volume or mechanism 1. Both join the same metadata/data interfaces, so 1 is not a prerequisite for 2 or 3.
- The two workspace views retain their separate private state, private-first resolution, and pinned shared immutable baseline. Baseline links are references, not writes.
- Mechanism 2 retains Native records versus Packed and an independently boxed, side-entering read-only mount. The joint page illustrates a name, common attribute, and data reference. A second schematic row represents additional records. Data references lead to already stored file bytes, never into the ordinary uploader. This is a non-inline example; format details remain in Section 5/Figure 3.
- Mechanism 3 retains defaults and distinguishes client configuration g, optional B hints, and backend q policy. They are separate choices with compatibility/admission constraints, not freely interchangeable values or a claim of automatic adaptation.
- The **Ordinary upload** inset is a named example: a selected written slice inside a logical chunk is magnified, then partitioned into upload blocks. Open guides encode magnification; arrows encode processing. Three separate output objects avoid implying that all input blocks are concatenated into one object. Each object's final length is L_o, not the object's name.
- Workspace/snapshot producers retain their own upload contracts, explicitly stated in the caption. The figure does not claim that every producer uses ordinary g formation or supports the same hint controls.
- The caption and Section 7 retain the distinction between architectural optionality and currently supported combinations. B hint admission and q framing admission are separately gated; effective layouts are persisted.

## Visual contract

- Unchanged canvas: 240 × 258 pt, 84.67 × 91.02 mm, included at column width.
- Body labels ≥7 pt; headings 8.5 pt; subscripts ≥5.32 pt.
- Both lower panels share y=107, height=141 pt, and width=112 pt, with an 8 pt gutter. Their repeated selection rows align at y=137. The top view choices deliberately have unequal widths because the workspace branch expands two private views and a shared baseline.
- Orange marks private state; blue marks shared immutable representation/reference; gray marks ordinary formation/backend. Colors are redundant with wording and structure. Dark brown text replaces lighter orange on pale orange for readable small text.
- The previous U₁/Oₚ matched ports and isolated stacked sections are removed. Mechanisms keep their exact formal names.

## Verification

- Export inventory: 52 logical labels, 50 distinct labels, live Arial regular/bold text, no raster images in the PDF.
- SVG and PDF font checks pass. The only SVG warning is the skill's generic Nature 89/183 mm width preset, which does not apply to this OSDI single-column canvas.
- Collision audit: 0 failures. Three warnings are intentional numeral-circle overlaps in PDF extraction that combines the badge and adjacent heading into one text box. Actual glyphs remain properly separated.
- Independent semantic review passed after correcting one-object-per-block depiction, Native records terminology, and the separate read-only entry.
- Both manuscript variants are rebuilt. `integrated-pages.json` and adjacent PNGs record the final Figure 2 location and page render; build logs record compilation. No experimental data or other figures are changed by this revision.

`before.*`, `before-source.py`, `before-scene.json`, and `before-overview.tex` preserve the incoming state. `after-source.py` and `after-scene.json` freeze the final diagram. The canonical editable source remains `tools/draw_architecture_editable.py`.
