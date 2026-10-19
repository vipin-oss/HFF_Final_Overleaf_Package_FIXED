# HFF — Overleaf source package (Stage 9)

LaTeX source for the pre-implementation research document

**"Thermally induced deformation and conjugate heat transfer in a channel with two-way thermoelastic coupling"**

This package contains **LaTeX source only**. It contains **no PDF**, and no PDF was produced while preparing it — see "About the PDF".

> **Build status: NOT VERIFIED.** No TeX engine was available in the environment where this package was assembled, so the compilation sequence below has **not** been executed against this source. What *was* checked is listed under "What was verified". Do not read this package as a tested build.

---

## Compilation

Compiler: **pdfLaTeX**. Bibliography: **bibtex**. No shell-escape, no external graphics files, no fonts beyond a standard TeX Live installation.

```
pdflatex -interaction=nonstopmode main
bibtex   main
pdflatex -interaction=nonstopmode main
pdflatex -interaction=nonstopmode main
```

The first pass writes the `.aux`; `bibtex` resolves the 18 natbib entries; two further passes settle citation numbers, the table of contents and all `\ref`/`\eqref` cross-references. `main.tex` carries `% !TEX program = pdflatex`, so Overleaf and most editors select the engine automatically.

### On Overleaf

1. *New Project* → *Upload Project* → select `HFF_Stage9_Overleaf_Source.zip`.
2. `main.tex` is detected as the main document. Leave the compiler as **pdfLaTeX** and the bibliography tool as **bibtex**.
3. Press *Recompile*.

No settings need changing and no file needs moving: `main.tex` sits at the ZIP root and every `\input` path is relative to it.

---

## What changed in this stage

**One character, one line, one file.** The `note` field of the `shah1978laminar` entry in `references.bib` contained a bare underscore in ordinary text:

```
Nu uses D_h based on the wetted perimeter.
```

`plainnat` prints `note` verbatim into the `.bbl`, and a bare `_` in text mode is a hard pdfLaTeX error (*Missing $ inserted*). It is now

```
Nu uses D\_h based on the wetted perimeter.
```

No bibliographic metadata was touched: authors, title, journal, volume, pages, year, publisher, series — none altered, and the DOI field is untouched.

One further underscore exists in `references.bib`, inside the `doi` field of `turek2006proposal` (`10.1007/3-540-34596-5_15`). It was deliberately **not** escaped: the DOI is metadata and must stay byte-exact, and `plainnat` does not typeset `doi` fields, so it never reaches LaTeX. If a DOI-printing bibliography style is adopted later, that field must be escaped (or emitted through `\url`) at that time.

No other source file was changed in this stage.

---

## Contents

```
main.tex                     Main document (report class, 11 pt, A4)
references.bib               Bibliography, 18 entries
README.md                    This file
chapters/
  ch01.tex ... ch11.tex      Research exposition
  appendix.tex               Appendix A — notation and arithmetic
  audit_appendix.tex         Appendix B — audit register and open checks
figures/
  fig_geometry.tex           TikZ: configuration (no external graphics)
  fig_signs.tex              TikZ: interface sign conventions
HFF_stage7_independent_weak_form_audit.md     Stage-7 independent derivation of the weak forms
HFF_stage7_equation_correction_log.md         Stage-7 correction log (applied / proposed / rejected)
HFF_stage7_mathematical_signoff_checklist.md  Stage-7 sign-off gates and open items
HFF_stage7_source_diff.patch                  The exact Stage-7 source diff (+56/−31, 3 hunks)
HFF_stage8_package_verification.md            Stage-8 package verification record
HFF_stage5_pre_coding_checklist.md            Pre-coding readiness checklist (cited by the Stage-7
                                              sign-off checklist)
```

All figures are inline TikZ; there are no `.pdf`, `.png` or `.eps` assets to lose in transfer.
Two places in the prose refer to files in the repository's `project_archive/` directory
(`audit/HFF_claim_evidence_register.csv`, `HFF_Reconciliation_2/...`,
`audit/HFF_pre_coding_checklist.md`). Those are documentary references, not LaTeX inputs; they are
not needed to compile and are not in this package.

---

## Source provenance

| Item | Value |
|---|---|
| Repository | `vipin-oss/HFF_Final_Overleaf_Package_FIXED` (private) |
| Branch | `arena/c875f9b3-hff-final-overleaf-package-fix` — **not** merged into `main` |
| Starting commit for this stage | `d52aeb181ecaf999017ffdfae006fefa46e0ca39` |
| `main` | untouched at `5a255212a51374f7eb178647eb12b0a9c2b67ded` |
| Package built | 19 October 2026 |

Every `.tex` file and `references.bib` in this archive is the blob of the Stage-9 commit on that
branch; the packaging step itself made no source edit.

---

## What was verified

Performed on the extracted archive, not on the working tree:

| Check | Result |
|---|---|
| ZIP integrity (`unzip -t`, per-entry CRC, `testzip()`) | pass |
| Every `\input`/`\include` path resolves from the ZIP root | pass — 15/15 |
| Every cited key exists in `references.bib`, every entry cited | pass — 18 / 18 |
| `references.bib` parses without failed blocks | pass — 18 entries |
| Bare underscore fixed in the `shah1978laminar` note, and no other text-mode `_` / `^` remains | pass |
| Duplicate labels / undefined `\ref`–`\eqref` targets | pass — 86 labels, 73 targets, 0 / 0 |
| Braces and `\begin`/`\end` balanced in every `.tex` | pass |
| Figure files present; no external graphics referenced | pass |
| Every `.tex` and `references.bib` byte-identical to the Git commit | pass |
| Stage-7 audit, correction log, sign-off checklist, diff patch; Stage-8 verification report | pass |
| No PDF in the archive | pass |

**Not performed:** LaTeX compilation, BibTeX execution, PDF generation, page count, visual
inspection of the typeset output, Overleaf upload, numerical verification, validation.

---

## About the PDF

**No PDF is included.** The PDF in the repository (`main.pdf`, 49 pages) is the **Stage-4 build**. It
predates the Stage-5, Stage-6, Stage-7 and Stage-9 corrections and therefore does not reflect the
equations in this archive. It is deliberately omitted rather than shipped as though it were
current. No replacement PDF was produced, because no compiler was available.

---

## Status and gates

- **Scientific validation is incomplete.** There is no solver, no simulation and no numerical
  result. Nothing in this package has been verified against a manufactured solution, a benchmark or
  experimental data.
- A structural package check and a clean bibliography do **not** prove that the document compiles,
  and a successful compile would not prove that the mathematics is correct.
- **Open before solver implementation** (from `HFF_stage7_mathematical_signoff_checklist.md`):
  reviewer acceptance of the corrected mechanical interface statement (C‑3/M4); function spaces
  `V_g, Q, V_s, S_f, S_s` still undefined (P‑1/M6); whether the interface temperature is one shared
  unknown (T7); the contradictory thermal data-flow directions in `ch05:70–72` and `ch08:114`
  (P‑2/T8); the geometric-stiffness mismatch between `ch03`/`ch08` and `\eqref{eq:weaks}` (P‑4/M8);
  and the SUPG time-scale `τ` (P‑5/B7).
- **Nothing in this package authorises coupled production computation.** Isolated verification of
  V‑A, V‑B and V‑C remains gated by the Stage-5 pre-coding checklist.
