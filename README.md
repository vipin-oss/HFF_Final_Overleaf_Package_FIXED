# HFF Scholarly Research Formulation

Pre-implementation research document for the proposed study
**"Thermally induced deformation and conjugate heat transfer in a channel with two-way
thermoelastic coupling"** (target venue: *International Journal of Numerical Methods for Heat &
Fluid Flow*, Emerald).

## What this package contains

This is the **final Overleaf-ready package** (`HFF_Final_Overleaf_Package.zip`). All compilation
sources sit at the ZIP **root** — upload the ZIP as an Overleaf project and compile; nothing
needs to be located or rearranged.

```
HFF_Final_Overleaf_Package.zip
├── main.tex                 <- Overleaf "Main document" (pdfLaTeX, report class, 11pt, A4)
├── references.bib           <- 18 verified BibTeX entries (no duplicates; see note below)
├── chapters/                <- ch01...ch11, appendix.tex, audit_appendix.tex
├── figures/                 <- fig_geometry.tex, fig_signs.tex (TikZ; no external graphics)
├── main.pdf                 <- freshly compiled from exactly these sources (49 pages)
├── README.md                <- this file
├── HFF_final_pre_coding_checklist.md
├── HFF_final_reference_status.csv (+ ..._notes.txt)
├── HFF_source_pdf_consistency_report.md
├── HFF_revision_summary.md
├── HFF_final_packaging_report.md
└── project_archive/         <- full audit trail (audit/, HFF_Independent_Audit_2/,
                                HFF_Reconciliation_2/, REVISION_SUMMARY.md) — preserved verbatim
```

## Overleaf upload

1. Overleaf → *New Project* → *Upload Project* → select `HFF_Final_Overleaf_Package.zip`.
2. Compiler: **pdfLaTeX** (Overleaf default); bibliography: **bibtex** (Overleaf default).
   No settings changes needed; only standard TeX Live packages are used
   (`enumitem`/`multirow` intentionally avoided).

## Compilation (local or Overleaf)

```
pdflatex -interaction=nonstopmode main
bibtex main
pdflatex -interaction=nonstopmode main
pdflatex -interaction=nonstopmode main
```

Four passes resolve natbib citation numbers and cross-references. The bundled build used an
equivalent TeX Live 2026 toolchain with `bibtex8` (8-bit BibTeX); for this all-ASCII
bibliography `bibtex` is interchangeable.

## Reference status (explicitly open items)

All 18 entries were verified against Crossref/DOI or publisher records during the audit stages;
details per entry in `HFF_final_reference_status.csv`. **Two items remain explicitly open and
are not silently claimed as fully verified:** (i) the digit-level confirmation of the Shah &
London (1978) Nu_T1 = 4.861 value from the primary table (action C-1; value is corroborated by
three independent reproductions); (ii) the page range of Hood & Taylor (1974) (note retained in
the bib entry).

## Reading guidance
Chapters 1–11 are the research exposition. The appendices carry, respectively, the complete
arithmetics and notation (Appendix A) and the audit record with discrepancy register, evidence
statuses, open checks, and the staged implementation decisions (Appendix B). The coupled
production computations remain on HOLD under the conditions listed in Chapter 9 and Appendix B.
