# Compatibility build directory

The canonical manuscript is now `../main.tex`. Sources, figures, bibliography,
styles and reviewed PDFs live at the repository root. This directory retains
only a forwarding Makefile so `make -C paper` still builds the root project.
Run `latexmk -xelatex main.tex` from the repository root, not this directory.
Any ignored LaTeX intermediates left here are historical build output.
