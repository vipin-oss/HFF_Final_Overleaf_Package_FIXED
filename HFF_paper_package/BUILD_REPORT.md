# BUILD REPORT

## Environment actually used
| Item | Version |
|---|---|
| OS | Linux 6.18.44 (container) |
| pdfTeX | 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian) |
| BibTeX | 0.99d |
| pdftops (poppler) | 24.02.0 |
| Python | 3.13.16 |
| numpy / scipy / matplotlib / scikit-fem | 2.5.3 / 1.18.1 / 3.11.2 / 12.0.2 |

## Procedure
`./build.sh` runs, in order: `hff_model.py`, `q8_strip.py`, `q8_nonlinear.py`, `fe_independent.py`,
`slenderness_study.py`, `convergence_study.py`, `make_numbers.py`, `make_figures.py`; builds `figures/fig1_geometry.pdf/.eps`; then
`pdflatex`, `bibtex`, `pdflatex` ×2 on `main.tex`. Then `python3 code/check_manuscript.py`.

## Result
* **Clean-copy build:** the package was copied to an empty directory with `main.pdf` and `main.bbl` removed, and
  `build.sh` was run from scratch: success, 18 pages, wall time about 2 min 20 s.
* The rebuilt `main.pdf` has text identical (`pdftotext`) to the included `main.pdf`, and the regenerated
  `numbers.tex`, `tab_*.tex` and all five `code/results/*.json` are byte-identical to the included files. (PDF binaries
  differ only by creation timestamps.)
* `check_manuscript.py`: 54 checks, 0 failed (after the clean build).
* LaTeX log: 0 overfull boxes, 7 underfull boxes (cosmetic, in the table/abstract line breaking), 0 undefined
  references or citations. BibTeX: no warnings.
* `pdftotext` prints "Mismatch between font type and embedded font file" for `main.pdf`. This comes from the
  matplotlib TrueType (Type 42) fonts embedded in the figure PDFs; text extraction and rendering are unaffected.
* No dependence on absolute local paths: scripts locate files relative to their own directory.

## Not tested
Compilation on Overleaf (TeX Live version may differ); Word export.
