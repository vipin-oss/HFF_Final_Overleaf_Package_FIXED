# Superseded document (kept for provenance)

This folder holds the previous deliverable: a 49-page `report`-class document with a cover
page, table of contents, eleven chapters and two appendices (`main.tex`, `main.pdf`), its
chapter sources and its TikZ figure sources.

It is **not** the submission. It was a pre-implementation design and audit record: it
contains the formulation, the baseline arithmetic and a verification *plan*, but no computed
results and no code, and its verification gates (V-A…V-G), audit registers (D-1…D-20) and
arithmetic cells (A1–A9) were never executed. Its claims were replaced by the executed study
in `../journal_submission/`; `../journal_submission/BUILD_REPORT.md` §5 lists exactly which
claims were removed or qualified and why.

Nothing here is referenced by the current manuscript, the program or the reproducibility
package. It is kept only so that the earlier version remains inspectable in the repository.

To build it anyway (from this folder):

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main
```
