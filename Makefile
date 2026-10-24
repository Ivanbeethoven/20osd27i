LATEXMK ?= latexmk
LATEX_FLAGS = -xelatex -interaction=nonstopmode -halt-on-error -file-line-error
.PHONY: all paper named anonymous clean

all: named anonymous

paper: all

named:
	$(LATEXMK) $(LATEX_FLAGS) main.tex

anonymous:
	$(LATEXMK) $(LATEX_FLAGS) anonymous-preview.tex

clean:
	$(LATEXMK) -c main.tex
	$(LATEXMK) -c anonymous-preview.tex
