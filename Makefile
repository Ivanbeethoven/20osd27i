.PHONY: all paper template clean

all: paper

paper:
	$(MAKE) -C paper

template:
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex

clean:
	$(MAKE) -C paper clean
	$(LATEXMK) -C main.tex
