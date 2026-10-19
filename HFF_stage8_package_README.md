# HFF — Overleaf source package (Stage 8)

LaTeX source for the pre-implementation research document

**"Thermally induced deformation and conjugate heat transfer in a channel with two-way thermoelastic coupling"**

This package contains **LaTeX source only**. It contains **no PDF**, and no PDF was built while preparing it — see "About the PDF" below.

---

## Compilation

Compiler: **pdfLaTeX**. Bibliography: **bibtex**. No shell-escape, no external graphics files, no fonts beyond a standard TeX Live installation.

```
pdflatex -interaction=nonstopmode main
bibtex   main
pdflatex -interaction=nonstopmode main
pdflatex -interaction=nonstopmode main
```

The first pass writes the `.aux`; `bibtex` resolves the 18 natbib entries; two further passes settle citation numbers, the table of contents and all `\ref`/`\eqref` cross-references. `main.tex` also carries `% !TEX program = pdflatex` so editors and Overleaf pick the right engine automatically.

### On Overleaf

1. *New Project* → *Upload Project* → select `HFF_Stage8_Overleaf_Source.zip`.
2. `main.tex` is detected as the main document. Leave the compiler as **pdfLaTeX** and the bibliography tool as **bibtex**.
3. Press *Recompile*.

No settings need changing, and no file needs to be moved: `main.tex` sits at the ZIP root and every `\input` path is relative to it.

**Compilation has not been performed.** No TeX engine was available in the environment where this package was assembled, so the package's build-ability is unverified. The checks that *were* performed are listed in `README` §"What was verified" and in `HFF_stage8_package_verification.md`.

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
HFF_stage7_independent_weak_form_audit.md    Stage-7 independent derivation of the weak forms
HFF_stage7_equation_correction_log.md        Stage-7 correction log (applied / proposed / rejected)
HFF_stage7_mathematical_signoff_checklist.md Stage-7 sign-off gates and open items
HFF_stage7_source_diff.patch                 The exact Stage-7 source diff (+56/−31, 3 hunks)
HFF_stage5_pre_coding_checklist.md           Pre-coding readiness checklist (referenced by the
                                             Stage-7 sign-off checklist)
```

All figures are inline TikZ; there are no `.pdf`, `.png` or `.eps` assets to lose in transfer.
The prose refers in two places to files in the repository's `project_archive/` directory
(`audit/HFF_claim_evidence_register.csv`, `HFF_Reconciliation_2/...`, `audit/HFF_pre_coding_checklist.md`).
Those are documentary references, not LaTeX inputs; they are not needed to compile and are not
included in this package.

---

## Source provenance

| Item | Value |
|---|---|
| Repository | `vipin-oss/HFF_Final_Overleaf_Package_FIXED` (private) |
| Branch | `arena/c875f9b3-hff-final-overleaf-package-fix` — **not** merged into `main` |
| Source commit packaged | `6b07aea8838bf13581670c385846559ae6723cc5` |
| `main` | untouched at `5a255212a51374f7eb178647eb12b0a9c2b67ded` |
| Package built | 19 October 2026 |

Every `.tex` file in this archive is the blob of commit `6b07aea`; the Stage-8 build made no
source edit of any kind.

---

## What changed since the Stage-6 package

Four corrections from the Stage-7 audit, all textual or notational, **+56/−31 lines in two files**
(`chapters/ch02.tex` +6/−4, `chapters/ch08.tex` +50/−27):

1. **C‑1 — `a_T` is trilinear.** Written `a_T(\bu;T,\chi)` and defined as
   `∫_{Ω_f}(u·∇T)χ dx` in the same three-argument form already used for `c(u;u,v)`. Previously it
   was declared with two arguments while its definition contained the free symbol `u`.
2. **C‑2 — undefined placeholder removed.** `+⟨data⟩` deleted from the fluid momentum equation
   `\eqref{eq:weakf}`. It was never defined and is identically zero under the stated model.
3. **C‑3 — the interface-cancellation paragraph rewritten.** The mechanical statement "the two
   terms … cancel identically" was **not supported**: the no-slip condition `\eqref{eq:ifkin}`
   makes admissible fluid test functions vanish on `Γ_if`, so the fluid interface integral is
   zero, while the solid interface integral is the computed fluid-traction load. The corrected text
   says so, keeps the defensible conclusion (no independent interface-traction unknown, because the
   traction is evaluated from `(u,p)` and the reverse coupling acts through the moving domain), and
   separates the thermal statement, where cancellation *is* genuine — but only with one shared
   interface temperature unknown, and only up to the `O(ε)` reference/deformed-surface difference.
4. **C‑4 — `ch02` sign-convention prose.** "exactly antisymmetric … without modelling error"
   replaced by a bookkeeping statement of the single-normal convention plus a pointer to where
   cancellation does and does not occur.

**No equation's physics, sign, coefficient, domain, material property, geometry, operating
condition, dimensionless group, tolerance or research objective was altered.** The Stage-7 audit
independently re-derived all four weak forms and found every interface *sign* correct; it did not
change one.

Details: `HFF_stage7_equation_correction_log.md` (applied C‑1…C‑4; proposed P‑1…P‑5; rejected R‑1…R‑4)
and `HFF_stage7_source_diff.patch`.

---

## What was verified

Performed on the extracted archive, not on the working tree:

| Check | Result |
|---|---|
| ZIP integrity (`unzip -t`, per-entry CRC) | pass |
| Every `\input`/`\include` path resolves from the ZIP root | pass |
| Every cited key exists in `references.bib`, and every entry is cited | pass (18 / 18) |
| Duplicate labels | none (86 labels) |
| Undefined `\ref`/`\eqref` targets | none (73 targets) |
| Braces and `\begin`/`\end` balanced in every `.tex` | pass |
| Figure files present (`figures/fig_geometry.tex`, `figures/fig_signs.tex`) | pass |
| Every `.tex` byte-identical to commit `6b07aea` | pass |
| Stage-7 audit, correction log, sign-off checklist, diff patch present | pass |

**Not performed, and not claimed:** LaTeX compilation, BibTeX execution, PDF generation, page
count, visual inspection of typeset output, numerical verification, validation.

---

## About the PDF

**No PDF is included.** The PDF in the repository (`main.pdf`, 49 pages) is the **Stage-4 build**.
It predates the Stage-5, Stage-6 and Stage-7 corrections and therefore does not reflect the
equations in this archive. It was deliberately omitted rather than shipped as though it were
current. Compile this package to obtain a PDF that matches the source — and note that no such
compilation has yet been performed.

---

## Status and gates

- **No solver code exists.** Nothing in this package has been numerically verified or validated.
- The package check performed for this archive verifies **file structure and cross-references
  only**. It is not evidence that the document compiles, and not evidence that any derivation is
  correct.
- **Open before solver implementation** (from `HFF_stage7_mathematical_signoff_checklist.md`):
  reviewer acceptance of the mechanical statement (C‑3); function spaces `V_g, Q, V_s, S_f, S_s`
  still undefined (P‑1); whether the interface temperature is one shared unknown (T7); the
  contradictory thermal data-flow directions in `ch05:70–72` and `ch08:114` (P‑2/T8); the
  geometric-stiffness mismatch between `ch03`/`ch08` and `\eqref{eq:weaks}` (P‑4/M8); and the SUPG
  time-scale `τ` (P‑5/B7).
- **Nothing in this package authorises coupled production computation.** Isolated verification of
  V‑A, V‑B and V‑C remains gated by the Stage-5 pre-coding checklist.
