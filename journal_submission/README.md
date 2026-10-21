# Manuscript package — `journal_submission/`

Journal research article in the layout of the *International Journal of Numerical Methods
for Heat & Fluid Flow* (Emerald): single-column, structured abstract, nomenclature placed
after the field equations, twelve figures, eleven tables, three appendices and 55
references. The section tree follows the journal's 2023 pattern (Gupta, Kumar, Kumar and
Barak, HFF 33(6), 2250-2277): Introduction -> Field equations (with limiting cases) ->
Nomenclature -> Problem formulation -> Solution of the problem -> Numerical results and
discussion -> Discussion -> Limitations -> Conclusions -> References -> Appendices ->
Corresponding author. Everything needed to
compile it and to reproduce every number is in this folder or in `../program`.

**The LaTeX was not compiled in the environment where the package was assembled** — no TeX
distribution is available in the build sandbox. The sources were validated structurally
(strict parse of the whole file, label/reference/citation audit, figure and table resolution
for both build layouts); the first real compile will happen in Overleaf. See
`BUILD_REPORT.md` for exactly what was and was not checked.

## Contents

```
main.tex                 the manuscript (article class, 11 pt, A4, single column)
references.tex           generated bibliography (thebibliography, 55 entries)
references.bib           55 entries: 46 articles, 7 books, 2 book chapters
figures/fig01..fig12     PDF (vector) and PNG (400 dpi) of every figure
tables/table_*.tex       nine generated LaTeX tables (\tabinput by main.tex)
README.md                this file
BUILD_REPORT.md          how the package was built, what was verified, what was not
VALIDATION_REPORT.md     numerical results, conservation, verification and DOI evidence
```

Figure and table inventory (all produced by `../program/run_all.py` from
`../program/outputs/data`):

| Figure | File | Content |
|---|---|---|
| 1 | `fig01_geometry.pdf` | configuration (schematic, labelled as such) |
| 2 | `fig02_mesh.pdf` | body-fitted mesh at the converged state, interface detail |
| 3 | `fig03_grid.pdf` | grid refinement and relative difference to the Richardson limit |
| 4 | `fig04_verification.pdf` | Nusselt-number verification on four grids |
| 5 | `fig05_flow.pdf` | velocity profiles and streamwise pressure |
| 6 | `fig06_thermal.pdf` | local Nusselt number and temperature levels |
| 7 | `fig07_wall.pdf` | deflection, bending moment and bending stress |
| 8 | `fig08_convergence.pdf` | coupling convergence and mesh trend of the bow |
| 9 | `fig09_sensitivity.pdf` | response to imposed flux and wall thickness |
| 10 | `fig10_reynolds.pdf` | Reynolds-number sensitivity |
| 11 | `fig11_material.pdf` | wall conductivity and thermal expansion |
| 12 | `fig12_model_form.pdf` | model-form error of the frozen-force closure |

| Table | File | Content |
|---|---|---|
| 1 | `table_parameters.tex` | geometry, operating point, material data |
| 2 | *(in `main.tex`)* | boundary and interface conditions |
| 3 | `table_baseline.tex` | closed-form quantities of the formulation |
| 4 | `table_coupled.tex` | coupled solution at the design point |
| 5 | `table_mesh.tex` | grid study with observed order, extrapolation and GCI |
| 6 | `table_sweep.tex` | imposed-flux sweep |
| 7 | `table_reynolds.tex` | Reynolds-number sweep |
| 8 | `table_material.tex` | wall-conductivity sweep |
| 9 | `table_expansion.tex` | thermal-expansion sweep |
| 10 | `table_verification.tex` | code-verification benchmarks |
| 11 | *(in `main.tex`)* | nested iterations, tolerances and test inventory (Appendices B–C) |

## Compile locally

```bash
cd journal_submission
pdflatex main
pdflatex main
```

Two passes, no BibTeX run: the bibliography is read from `references.tex`, which is
generated once from `references.bib` by

```bash
python3 tools/make_references.py          # writes journal_submission/references.tex
python3 tools/make_references.py --check  # fails if the file is stale
```

The generator sorts the entries alphabetically and emits Emerald (Harvard) style with
natbib-compatible `\bibitem[Surname et al.(Year)]{key}` labels, so `\citep`/`\citet`
keep working unchanged.

Required packages: `amsmath`, `amssymb`, `graphicx`, `booktabs`, `siunitx`, `longtable`,
`array`, `enumitem`, `caption`, `natbib`, `hyperref`, `mathptmx`, `helvet` — all part of a
standard TeX Live or MiKTeX installation. `\graphicspath` lists both `figures/` and
`journal_submission/figures/`, and `\tabinput` resolves `tables/` or
`journal_submission/tables/` at compile time, so the same file compiles from this folder and
from the repository root without edits.

## Import into Overleaf

### Route A — ZIP upload (works on every plan)

1. Build the archive with `python3 tools/build_zip.py` from the repository root (or use the
   ready-made `hff_journal_submission.zip`). The archive contains `main.tex`,
   `references.bib`, `figures/` and `tables/` at its **root**.
2. Overleaf → *New Project* → *Upload Project* → choose the ZIP.
3. The project opens with `main.tex` as the root document; press *Recompile*. The first pass
   reports undefined references; a second pass resolves them. No BibTeX run is needed,
   because `references.tex` is part of the upload.

### Route B — GitHub synchronization (Overleaf premium)

Overleaf mirrors the **default branch** of the repository (`main`); it cannot follow a
feature branch and cannot create branches. Therefore:

1. Merge the pull request that contains this manuscript into `main`.
2. Overleaf → *New Project* → *Import from GitHub* → select
   `vipin-oss/HFF_Final_Overleaf_Package_FIXED` and the branch `main`.
3. Set the main document to `main.tex` at the repository root. That file is a two-line
   wrapper that `\input`s `journal_submission/main.tex`; the manuscript resolves its own
   figures, tables and bibliography, so no path needs editing.
4. Press *Recompile*.

Because Overleaf re-syncs from `main` on demand, any later correction must be committed to
`main` (through a reviewed pull request) before it can be pulled into the project.

### If the journal requires its own class file

The manuscript uses `article` with an Emerald-style front matter so that it compiles with a
stock TeX installation. When the submission portal requires `emerald.cls`, replace
`\documentclass[11pt,a4paper]{article}` by the class supplied by the journal and drop the
`\usepackage{mathptmx}`/`helvet` lines; the structured abstract, keywords, nomenclature and
sectioning of the present file map one-to-one onto the Emerald template.

## Relationship to the rest of the repository

| Path | Role |
|---|---|
| `program/` | the executable study: solvers, parameters, tests, figure/table generators |
| `program/outputs/` | saved numerical results (JSON/CSV), figures (PDF/PNG), tables (`.tex`) |
| `reproducibility_package/` | program + saved outputs + this manuscript, self-contained |
| `legacy_report/` | superseded report-class document, kept unchanged for provenance |
| `hff_journal_submission.zip` | ready-to-upload Overleaf archive built from this folder |
