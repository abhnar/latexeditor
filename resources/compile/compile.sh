pdflatex -interaction=nonstopmode -halt-on-error temp.tex
   bibtex temp.aux
	pdflatex -interaction=nonstopmode -halt-on-error temp.tex
	pdflatex -interaction=nonstopmode -halt-on-error temp.tex


