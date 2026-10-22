.PHONY: all named anonymous clean

all: named anonymous

named:
	latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex

anonymous:
	latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error anonymous-preview.tex

clean:
	latexmk -c main.tex
	latexmk -c anonymous-preview.tex
