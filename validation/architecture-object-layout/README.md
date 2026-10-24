# Figure 2: object, encoding block, and shard quantum

This revision retains the accepted optional/parallel architecture and the two fixed-g comparisons. The canvas remains 240 x 258 pt, ordinary text remains at least 7 pt, and the PDF has no raster content. Numeric subscripts are 5.32 pt or larger.

## Changed relationships

- The Joint metadata page connects straight down from below its Data ref. column to Referenced file bytes. The connector describes reference resolution, not upload.
- One illustrated raw block forms an object after applicable formatting. The object is shown in a pale Backend container so encoding is not attributed to the client.
- Two full encoding spans and a shorter tail illustrate object layout. A Coding block bracket identifies the first complete span, marked B. B is the erasure-coding input block size across data shards, not a per-shard byte count.
- That complete B span fans out to shards. An ellipsis deliberately avoids claiming a specific data/parity shard count. The highlighted initial half of one schematic shard and the Read/verify q bracket locate the physical verification/read unit within that shard.
- This backend geometry is schematic and is not on the raw-MiB scale of the g examples. No automatic adaptation, proportional g/B/q coupling, particular q/s measurement, or padded tail is claimed. Independent admission gates and producer contracts remain in the caption/manuscript.

## Validation

The final SVG/font audits pass with one intentional width-preset warning: 84.67 mm fits this OSDI column, whereas the generic auditor expects Nature widths. The collision audit has zero failures and the same three intentional numbered-heading warnings as before; they result from merged PDF text bounds, not actual overlapping glyphs. Final standalone and integrated renders were inspected after the last edit.

Both main.pdf and anonymous-preview.pdf compile successfully, with 13 pages each. Figure 1 is on page 2 and Figure 2 on page 4. Both variants fit their figures in single columns and report no overfull boxes, missing characters, undefined references, or float-only pages. Scoped whitespace checks pass.

The accompanying Figure 1 revision uses Arial at 9 pt throughout. Initial runs and Extended runs replace Core (5) and Exploratory (3) in the graphical legend; the caption retains sample counts and the manuscript's existing group correspondence. Panels a/b preserve their separate request-weighted denominators, while panel c uses neutral task markers. Data are unchanged. Its independent font, alignment, collision, data-equivalence, and provenance records are under experiments/agent-fuse-observations/qa/typography-groups/.

The before files preserve this turn's starting state. after-scene.json and after-source.py capture the final architecture export. verify.py regenerates manuscript page previews and export-check.json. The main rendering source remains tools/draw_architecture_editable.py.
