LATEXMK ?= latexmk
LATEX_FLAGS = -xelatex -interaction=nonstopmode -halt-on-error -file-line-error
.PHONY: all paper clean

all: paper

paper:
	$(LATEXMK) $(LATEX_FLAGS) main.tex

clean:
	$(LATEXMK) -c main.tex
