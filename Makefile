LATEXMK ?= latexmk
LATEX_FLAGS = -xelatex -interaction=nonstopmode -halt-on-error -file-line-error
.PHONY: all paper named anonymous template clean

all: named anonymous

paper: all

named:
	$(LATEXMK) $(LATEX_FLAGS) main.tex

anonymous:
	$(LATEXMK) $(LATEX_FLAGS) anonymous-preview.tex

template:
	cd templates/usenix-starter && $(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex

clean:
	$(LATEXMK) -c main.tex
	$(LATEXMK) -c anonymous-preview.tex
