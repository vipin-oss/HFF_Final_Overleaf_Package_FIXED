#!/usr/bin/env bash
# Full rebuild: numbers -> figures -> TeX.  Run from the package root.
set -euo pipefail
cd "$(dirname "$0")"
( cd code && python3 hff_model.py >/dev/null && python3 q8_strip.py >/dev/null && python3 q8_nonlinear.py >/dev/null && python3 make_numbers.py && python3 make_figures.py >/dev/null )
( cd figures && pdflatex -interaction=nonstopmode -halt-on-error fig1_geometry.tex >/dev/null && pdftops -eps fig1_geometry.pdf fig1_geometry.eps )
pdflatex -interaction=nonstopmode -halt-on-error main >/dev/null
bibtex main >/dev/null || true
pdflatex -interaction=nonstopmode -halt-on-error main >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main >/dev/null
echo "built main.pdf ($(pdfinfo main.pdf | grep Pages))"
