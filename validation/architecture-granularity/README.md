# Figure 2: visible granularity comparison

The accepted parallel architecture is preserved. The SVG prefix containing mechanisms 1 and 2 and their interface connections is byte-identical to the saved pre-edit version.

Mechanism 3 compares two fixed client configurations for the same aligned 10 MiB written slice: g = 4 MiB (default) yields 4 + 4 + 2, while g = 8 MiB yields 8 + 2. Equal total bar widths and proportional partitions make the changing granularity visible. These are configuration alternatives, not sequential stages or an online adaptation controller. The 8 MiB example illustrates the manuscript's configuration design space; it is not an experimental result.

Bar values denote raw MiB, not finalized object lengths. Each raw block forms an object after applicable formatting. The B hint and q policy remain independent backend controls, with separate admission gates; neither is depicted as following g proportionally. Other upload producers retain separate contracts.

The vector canvas remains 240 x 258 pt. Body labels are at least 7 pt; 5.32 pt is used only for subscripts. The PDF contains zero raster images. SVG and PDF font audits passed; the SVG auditor's sole warning concerns a generic Nature width preset, whereas the intentional 84.67 mm width fits this OSDI single column. Collision checks report zero failures and three warnings caused by text-box merging around the numbered heading badges; visual inspection confirms no actual collision.

Both main.pdf and anonymous-preview.pdf compiled successfully with latexmk/XeLaTeX. Each current document has 13 pages, with Figure 2 on page 4. Full-page renders were inspected for both versions: the figure fits one column, and the partition values, default label, arrows, and caption are readable. Neither build log reports overfull boxes, missing characters, undefined references, or float-only pages. Scoped git diff whitespace checks passed. No measured data were changed.

Evidence: export-check.json, svg-audit.json, font-audit.json, collision.json, integrated-pages.json, and the two integrated page PNGs in this directory.
