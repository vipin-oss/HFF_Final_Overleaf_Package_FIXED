# HFF — final Overleaf source package

LaTeX source for the pre-implementation research document

**"Thermally induced deformation and conjugate heat transfer in a channel with two-way thermoelastic coupling"**

This archive contains **LaTeX source only** — no PDF, and no PDF was produced from it.

> **Build status: NOT VERIFIED.** No TeX engine was available in the environment where this package
> was assembled, so the sequence below has **never been executed against this source**. See "What
> was verified" and `HFF_stage10_build_environment_report.md`.

---

## Compilation

Compiler **pdfLaTeX**, bibliography **BibTeX**, no shell-escape, no external graphics, no fonts
beyond a standard TeX Live installation.

```
pdflatex -interaction=nonstopmode main
bibtex   main
pdflatex -interaction=nonstopmode main
pdflatex -interaction=nonstopmode main
```

First pass writes the `.aux`; BibTeX resolves the 18 `natbib`/`plainnat` entries; two further passes
settle citation numbers, the table of contents and all `\ref`/`\eqref` targets. `main.tex` carries
`% !TEX program = pdflatex`.

### On Overleaf

1. *New Project* → *Upload Project* → select the ZIP.
2. `main.tex` is detected as the main document — leave the compiler as **pdfLaTeX** and the
   bibliography tool as **BibTeX**.
3. *Recompile*.

No settings change and no file needs moving: `main.tex` sits at the archive root and every
`\input` path is relative to it.

---

## Contents

```
main.tex                                      Main document (report, 11 pt, A4)
references.bib                                Bibliography, 18 entries
README.md                                     This file
chapters/ch01.tex … ch11.tex                  Research exposition
chapters/appendix.tex                         Appendix A — notation and arithmetic
chapters/audit_appendix.tex                   Appendix B — audit register and open checks
figures/fig_geometry.tex                      TikZ: configuration (inline, no external asset)
figures/fig_signs.tex                         TikZ: interface sign conventions
HFF_stage5_pre_coding_checklist.md            Pre-coding readiness checklist (24 rows)
HFF_stage7_independent_weak_form_audit.md     29 findings: 19 PASS / 6 FAIL / 4 UNRESOLVED
HFF_stage7_equation_correction_log.md         C‑1…C‑4 applied, P‑1…P‑5 proposed, R‑1…R‑4 rejected
HFF_stage7_mathematical_signoff_checklist.md  Sign-off gates and open items
HFF_stage7_source_diff.patch                  The exact Stage-7 diff (+56/−31, 3 hunks)
HFF_stage8_package_verification.md            Stage-8 package verification record
HFF_stage9_build_and_package_report.md        Stage-9 build attempt + package verification
HFF_stage10_build_environment_report.md       Toolchain audit, error analysis, 16 static checks
```

Two passages in the prose point at files in the repository's `project_archive/` directory. Those are
documentary references, not LaTeX inputs; they are not required to compile.

---

## State of the source

| Item | Value |
|---|---|
| Branch | `arena/c875f9b3-hff-final-overleaf-package-fix` (not merged into `main`) |
| Source commit | `613d04d4f031f98c67a0d9d61775801ca1e8e55d` |
| `main` | `5a255212a51374f7eb178647eb12b0a9c2b67ded`, untouched |

Corrections carried since the original import: the Stage-5 sign/metadata fixes, the Stage-7
weak-form and interface-statement corrections (C‑1 `a_T(u;T,χ)` trilinear; C‑2 removal of the
undefined `⟨data⟩`; C‑3 the mechanical interface terms do **not** cancel — the fluid integral
vanishes under no-slip and the solid carries the fluid traction as its load; C‑4 the `ch02`
sign-convention claim), and the Stage-9 bibliography escape (`D_h` → `D\_h` in the Shah–London
note, the one-character fix for a genuine pdfLaTeX error).

---

## What was verified

Static checks only, on the extracted archive: ZIP integrity; 15/15 `\input` targets resolve;
18/18 citation keys defined and no uncited entry; `.bib` parses without failed blocks and every
entry has the fields `plainnat` needs; no duplicate labels (86) and no undefined references (73
targets); braces, `$` parity, `\left`/`\right` and environment nesting balanced in all 16 `.tex`;
every package-provided command has its package; figures present; zero non-ASCII bytes; packaged
sources byte-identical to the Git commit; no PDF inside.

**Not verified:** LaTeX compilation, BibTeX execution, PDF generation, page count, warning-free
build, visual layout, Overleaf upload. A static check is not a build.

---

## Status and gates

- **Scientific validation is incomplete.** No solver, no simulation, no numerical result exists.
- **Open before solver implementation:** reviewer acceptance of the corrected mechanical interface
  statement (C‑3/M4); function spaces `V_g, Q, V_s, S_f, S_s` undefined (P‑1/M6); whether the
  interface temperature is a single shared unknown (T7); contradictory thermal data-flow directions
  in `ch05:70–72` and `ch08:114` (P‑2/T8); geometric stiffness absent from `\eqref{eq:weaks}`
  (P‑4/M8); SUPG operator and `τ` unspecified (P‑5/B7); plus Stage-5 items C‑2, C‑3, C‑6, C‑9, C‑12.
- **Nothing here authorises coupled production computation.**
