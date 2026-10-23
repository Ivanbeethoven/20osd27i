# Repository layout

The canonical BrewFS manuscript starts at the repository-root `main.tex`.
`anonymous-preview.tex` builds the name-switching preview. The manuscript's
`sections/`, `figures/`, `references.bib`, USENIX styles, and generated
`main.pdf` and `anonymous-preview.pdf` also live at the root.

Run `make` from the repository root to build both previews, or run
`latexmk -xelatex main.tex` and `latexmk -xelatex anonymous-preview.tex`.
`paper/Makefile` only forwards legacy `make -C paper` commands to the root;
`paper/` is no longer the manuscript source directory.

The former generic root template is preserved in `templates/usenix-starter/`
for use in a separate paper. The unchanged official USENIX example and style
are preserved in `templates/usenix-official/`.

Supporting research material remains in `planning/`, `experiments/`,
`evidence/`, `references/`, `validation/`, and `skills/`. Historical evidence
and QA reports retain the paths and version information recorded at the time
of inspection; those records do not define the current build layout.

Documents inside the imported package are research artifacts and may contain
planning notes or instructions for their original workflow. They are stored as
reference material; repository operations are governed by the top-level
project instructions and the current task.
