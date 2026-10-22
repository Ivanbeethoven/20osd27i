# OSDI 2027 USENIX paper template

This private repository is a writing-ready LaTeX skeleton based on the
[official USENIX conference paper template](https://www.usenix.org/conferences/author-resources/paper-templates).
The upstream `usenix2019_v3.sty` file is kept unchanged so that the page
geometry and typography match the published template.

## Quick start

```bash
make
# open build/main.pdf
```

If `make` is unavailable, run `latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex`.
The build places auxiliary files and the PDF in `build/`, which is ignored by
Git. A GitHub Actions job performs the same build on every push and pull
request.

## Before submitting

- Replace the title, author block, abstract, and the text under `sections/`.
- Edit `references.bib` and cite sources with `\cite{...}`.
- Put figures in `figures/` and reference them with `\includegraphics`.
- Set `\anonymousfalse` only for the camera-ready or non-blind version. For a
  blind review, keep `\anonymoustrue` and follow the exact anonymity rules in
  the OSDI call for papers.
- Confirm the current OSDI call for papers for page limits, required sections,
  supplementary-material rules, artifact policy, and submission deadline.
- Run the final PDF through the conference's format checker, if one is
  provided.

The USENIX template page currently specifies US letter paper, a two-column
layout, a 7 by 9 inch text block, and 10-point Times-style text with 12-point
leading. The conference CFP takes precedence if it adds or changes a rule.

For OSDI '27, also read the [Call for Papers](https://www.usenix.org/conference/osdi27/call-for-papers) and [Requirements for Authors](https://www.usenix.org/conference/osdi27/requirements-authors): the main paper is limited to 12 single-spaced pages (references may continue), the review is double-blind, pages should be numbered, and appendices cannot be used as supplementary-material pages.

## Layout

- `main.tex` - document entry point and submission-mode switch.
- `usenix2019_v3.sty` - official USENIX style file.
- `sections/` - editable section files.
- `references.bib` - BibTeX database.
- `figures/` - paper figures and plots.
- `Makefile` and `.latexmkrc` - local build commands.
- `.github/workflows/build.yml` - reproducible CI build.


