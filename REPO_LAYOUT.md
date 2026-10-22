# Repository layout

The BrewFS OSDI research package is the canonical project under `paper/`,
`planning/`, `experiments/`, `evidence/`, `references/`, `validation/`, and
`skills/`. Build the named and anonymous paper previews with `make -C paper`,
or build the package from the repository root with `make`.

The root `main.tex`, `sections/`, `references.bib`, and `figures/` are the
generic USENIX starter template created before the BrewFS package was added.
They are retained as a clean template for a separate paper; they are not the
BrewFS manuscript. The official style and manuscript-specific template remain
under `paper/template/`.

Documents inside the imported package are research artifacts and may contain
planning notes or instructions for their original workflow. They are stored as
reference material; repository operations are governed by the top-level
project instructions and the current task.
