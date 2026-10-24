# Repository layout

The sole BrewFS manuscript entry point is the repository-root `main.tex`.
Its chapters live in `sections/`; `figures/`, `references.bib`, USENIX styles,
and the generated `main.pdf` also live at the root. `sections/` contains the
actual manuscript text and is required for compilation.

Run `make`, `make paper`, or `latexmk -xelatex main.tex` from the repository
root. The obsolete `paper/` forwarding directory and the name-switching
preview were removed; historical reports may still refer to those old paths.

The unchanged official USENIX example and style are preserved in
`templates/usenix-official/`. The unused generic starter and its Make target
have been removed.

The active architecture source is `tools/draw_architecture_editable.py`, with
SVG, PDF and PNG exports in `figures/`. The active workload figure is
`fuse-single-column`; `fuse-profile` and `fuse-time` remain companion diagnostics.
Superseded architecture variants, image-generation drafts, old combined
workload figures and generated QA assets have been removed from the checkout.

Supporting research material remains in `planning/`, `experiments/`,
`evidence/`, `references/`, `validation/`, and `skills/`. Historical evidence
and QA reports retain the paths and version information recorded at the time
of inspection; those records do not define the current build layout. See
`validation/README.md` for the distinction between retained review evidence and
removed generated assets. The pre-cleanup files remain in Git commit `5994769`.
The stale package hash manifest was removed; use Git and the current validator.

Documents inside the imported package are research artifacts and may contain
planning notes or instructions for their original workflow. They are stored as
reference material; repository operations are governed by the top-level
project instructions and the current task.
