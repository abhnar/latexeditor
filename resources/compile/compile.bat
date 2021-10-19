pdflatex -interaction=nonstopmode -halt-on-error temp.tex
if not exist temp.aux exit
bibtex temp.aux
pdflatex -interaction=nonstopmode -halt-on-error temp.tex
pdflatex -interaction=nonstopmode -halt-on-error temp.tex
