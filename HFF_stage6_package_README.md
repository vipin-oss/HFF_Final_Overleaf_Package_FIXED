# HFF — Overleaf source package (Stage 6)

Source package for the pre-implementation research document

**"Thermally induced deformation and conjugate heat transfer in a channel with two-way thermoelastic coupling"**

The package contains **LaTeX source only. It contains no compiled PDF** — see "About the PDF" below.

---

## Compilation

Compiler: **pdfLaTeX**. Bibliography: **bibtex**. No shell-escape, no external graphics, no fonts beyond the standard TeX Live set.

```
pdflatex -interaction=nonstopmode main
bibtex   main
pdflatex -interaction=nonstopmode main
pdflatex -interaction=nonstopmode main
```

Four passes are required: the first builds the `.aux`, `bibtex` resolves the 18 natbib entries, and two further passes settle citation numbers, the table of contents and all `\ref`/`\eqref` cross-references.

### On Overleaf

1. *New Project* → *Upload Project* → select `HFF_Stage6_Overleaf_Source.zip`.
2. `main.tex` is automatically the main document; leave the compiler as pdfLaTeX and the bibliography tool as bibtex.
3. Press *Recompile*. No settings need changing.

Expected result: ~49 pages, 0 errors. Warnings of the "undefined references on first pass" kind disappear after the second run.

---

## Contents

```
main.tex                     Main document (report class, 11 pt, A4)
references.bib               Bibliography, 18 entries
chapters/
  ch01.tex ... ch11.tex      Research exposition
  appendix.tex               Appendix A — notation and arithmetic
  audit_appendix.tex         Appendix B — audit register and open checks
figures/
  fig_geometry.tex           TikZ: configuration (no external graphics)
  fig_signs.tex              TikZ: interface sign conventions
README.md                    This file
HFF_stage5_benchmark_verification.md    Stage-5 benchmark and reference verification
HFF_stage5_reference_status.csv         Per-reference verification register (18 rows)
HFF_stage5_pre_coding_checklist.md      Pre-coding readiness checklist (24 rows)
HFF_stage5_git_sync_report.md           Stage-5 repository and change report
HFF_stage6_export_report.md             This export: checks, manifest, commit hashes
```

All `\input{chapters/...}` and `\input{figures/...}` paths are relative to the ZIP root; unpacking the ZIP into a project preserves them.

---

## Source provenance

| Item | Value |
|---|---|
| Repository | `vipin-oss/HFF_Final_Overleaf_Package_FIXED` (private) |
| Branch | `arena/c875f9b3-hff-final-overleaf-package-fix` — **not** merged into `main` |
| Stage-5 corrections | `58acd5c` |
| Bilinear-form definitions | `049cb36` |
| LaTeX source at | `049cb36` (the packaging files below do not affect the LaTeX) |
| `main` | untouched at `5a25521` |

---

## What changed relative to the previous package

Fourteen source lines, all corrections of signs, definitions or attribution. **No equation's physics, no material property, no geometry, no dimensionless group, no tolerance and no research objective was altered.** In full:

1. **Solid elasticity weak form** `\eqref{eq:weaks}` — boundary term `+\int \sigma n\cdot\varphi` → `-\int \sigma n\cdot\varphi`. The solid's outward normal is `-\mathbf n`; with the old sign a pressure load entered as suction and the interface terms added instead of cancelling.
2. **Fluid energy weak form** `\eqref{eq:weaktf}` — boundary term `-\int k_f \nabla T_f\cdot n\,\chi` → `+\int ...`. Restores the thermal cancellation under flux continuity.
3. **Bilinear forms** `a_T`, `a_{kf}`, `a_{ks}` (and `\hat a_f`, `b`, `c`) — now defined explicitly; previously used but never defined.
4. **Heater boundary condition B6** — `-k_s\nabla T_s\cdot n_{out} = q''` → `+k_s\nabla T_s\cdot n_{out} = q''`, with the note that `q''>0` is heat supplied to the solid.
5. **Post-processing wall flux** — `q_w = -k_f\nabla T_f\cdot n` → `q_w = +k_f\nabla T_f\cdot n` ("into the fluid"). The old definition made `h` and `Nu` negative on a heated wall.
6. **Normal convention** in the traction balance — `\sigma^{(s)}\cdot n + \sigma^{(f)}\cdot n_f = 0, n_f = -n` → `\sigma^{(s)}\cdot n_s + \sigma^{(f)}\cdot n_f = 0, n_s=-n, n_f=n`. Result unchanged; the statement is now correct.
7. **Citation attribution** — P2–P1 origin to Hood & Taylor, discrete inf–sup stability to Brezzi & Fortin (previously one joint claim).
8. **Bibliography** — Hood & Taylor pages 121–132 added; Shah & London note updated; Rahimimotlagh given name corrected.

---

## About the PDF

**No PDF is included in this package.** The PDF in the repository (`main.pdf`, 49 pages) is the **Stage-4 build**. It predates the Stage-5 and Stage-6 source corrections listed above, so it does **not** reflect the current equations. It has been deliberately omitted rather than shipped as if it were a current build.

Compile this package to obtain a PDF that matches the source.

---

## Status and gates

- **No solver code exists.** Nothing in this package has been numerically verified or validated.
- **Isolated verification may proceed** for V‑A (fluid), V‑B (rigid thermal) and V‑C (thermoelastic), subject to the conditions in `HFF_stage5_pre_coding_checklist.md`.
- **The fully coupled implementation remains on HOLD** pending the interface-quadrature conditions, C‑2 (V‑D data), C‑3 (V‑E data), C‑6 (property freeze including the evaluation temperature for a 60 K wall drop), C‑9 (outflow sensitivity), C‑12 (independent second solver) and V‑G.
- Internal consistency of the LaTeX is **not** evidence that the derivation is correct. An independent hand re-derivation of the corrected weak form is still outstanding.

### Known residuals carried in the text

| Item | Status |
|---|---|
| Shah & London Table 43 printed page number | unresolved; value 4.861 itself confirmed |
| V‑B2 evaluation station / duct length, adiabatic companion wall | to be written |
| SUPG time-scale `\tau` | to be specified |
| C‑2, C‑3, C‑6, C‑7, C‑9, C‑12 | open (see Appendix B) |
