# Stage 15 — Build and packaging report

Three different artefacts are routinely conflated. This document separates them explicitly.

| | Artefact | What it is | Status |
|---|---|---|---|
| **A** | `main.pdf` (tracked) | The *historical* PDF, built 2026-10-19T05:58:05Z by pdfTeX 1.40.29 | **STALE — does not correspond to current source** |
| **B** | Current source | `main.tex` + `chapters/` + `figures/` at `e8ef0d7` | **NOT BUILD-VERIFIED** |
| **C** | `HFF_Final_Overleaf_Source.zip` | The *historical* source bundle | **STALE — 13 of 16 `.tex` files differ from current source** |

---

## A. The tracked PDF

| Property | Value |
|---|---|
| Size | 469,859 bytes |
| SHA-256 | `59916a98cc082ded19c96d97b603797088b0ee865b654fa602373afa07939dba` |
| Producer | `pdfTeX-1.40.29`, Creator `LaTeX with hyperref` |
| Creation date | `D:20261019055805Z` |
| Last commit touching it | `5a25521` "Initial Overleaf Import" — the **only** commit that contains it |

**It does not correspond to the current source.** Three `.tex` commits postdate the import:

    e8ef0d7  Stage 15: single sign convention, weak-form closure, register D-21..D-25
    6b07aea  audit the coupled weak formulation independently and correct the interface-cancellation statements
    049cb36  Stage 6: define the bilinear/trilinear forms used in the weak statement
    58acd5c  Stage 5: benchmark/reference verification and pre-coding audit

The PDF therefore cannot reflect the Stage 15 corrections — it predates them, and it predates the
`6b07aea`/`049cb36`/`58acd5c` changes as well.

**Consequence for a reader.** The PDF still shows `w = −d₂`, `D_s w'''' = −p`, `1.8×10⁻⁴`, and
`Γ_p = w_th/w_p = 1.7×10³`. Any external reader who opens `main.pdf` gets the **superseded**
manuscript. This is the single highest-priority packaging defect and it cannot be repaired in this
environment.

**Attempted direct confirmation.** A text comparison against the PDF was attempted and **failed**:
the embedded fonts are subset and the extracted text stream is not reliably decodable with the
tools present. This is recorded as an unverified inference from metadata + git history, not as a
verified content diff. Treat "the PDF shows the old values" as *very likely* rather than proven.

## B. Current source

**Not build-verified.** No TeX engine is available:

| Binary | Status |
|---|---|
| `pdflatex` | ABSENT |
| `latexmk` | ABSENT |
| `bibtex` | ABSENT |
| `biber` | ABSENT |
| `tectonic` | ABSENT |
| `lualatex` | ABSENT |
| `xelatex` | ABSENT |

**No dependency was installed** (none is permitted), and **no build was fabricated**. What was
verified instead is the maximum obtainable without a compiler:

| Check | Result |
|---|---|
| Braces balanced, 16/16 files | PASS |
| `\begin`/`\end` balanced | PASS |
| 87 labels, 87 distinct, no duplicates | PASS |
| 0 dangling `\ref`/`\eqref` | PASS |
| 19 cited keys all present in `references.bib` | PASS |
| no uncited bib entries | PASS |
| no undefined shorthand macros (`\ie` was found and removed) | PASS |
| every TikZ macro used in `fig_geometry` defined before use (`\Le \L \Lo \Hf \ds`) | PASS |
| no `\include`/`\input` target missing | PASS |

**What this does not prove:** overfull boxes, TikZ compile errors, float placement, `hyperref`
warnings, and bibliography style output. A first real build may surface formatting issues; it should
not surface undefined references or missing citations, since those were checked structurally.

## C. The source ZIP

**26 members.** SHA-256 `b49ca34ea8f4f8e30a38f665a36778b48f67033ab750439cd8f1adacde4a054f`.

Comparison of the archive against the working tree, `.tex` files only:

| File | Status |
|---|---|
| `chapters/appendix.tex` | DIFFERS |
| `chapters/audit_appendix.tex` | DIFFERS |
| `chapters/ch01.tex` | DIFFERS |
| `chapters/ch02.tex` | DIFFERS |
| `chapters/ch03.tex` | DIFFERS |
| `chapters/ch04.tex` | DIFFERS |
| `chapters/ch05.tex` | DIFFERS |
| `chapters/ch06.tex` | DIFFERS |
| `chapters/ch07.tex` | DIFFERS |
| `chapters/ch08.tex` | DIFFERS |
| `chapters/ch09.tex` | DIFFERS |
| `main.tex` | DIFFERS |
| `figures/fig_geometry.tex` | DIFFERS |
| `chapters/ch10.tex`, `chapters/ch11.tex`, `figures/fig_signs.tex`, `references.bib` | identical |

**13 of 16 `.tex` files differ.** The archive also carries three stale audit reports
(`HFF_stage7_*`, `HFF_stage8_*`, `HFF_stage9_*`, `HFF_stage10_*`) that are not part of the
manuscript. **The ZIP must not be distributed as-is.**

## D. Other tracked bundles

| Archive | Members | SHA-256 | Status |
|---|---|---|---|
| `HFF_Stage6_Overleaf_Source.zip` | 23 | `5ef86a3e…016865` | historical, superseded |
| `HFF_Stage8_Overleaf_Source.zip` | 23 | `819bcc15…fac5a990` | historical, superseded |
| `HFF_Stage9_Overleaf_Source.zip` | 24 | `cbed5018…396953` | historical, superseded |

These are stage snapshots and are correctly labelled as such. They are not distribution candidates
and should not be mistaken for the current package.

## E. What a verified package needs

1. **A TeX installation** (pdfTeX or Tectonic) with the packages `main.tex` currently loads.
2. A clean build: `pdflatex → bibtex → pdflatex → pdflatex`.
3. **Log triage**: zero undefined references, zero undefined citations, zero missing files; overfull
   boxes examined.
4. A **byte-level check** that the rebuilt PDF's text contains `+d_2`, `13.9`, `13.6`,
   `1.39×10⁻⁴` and does **not** contain `1.8×10⁻⁴` or `into the channel`.
5. Regenerate the ZIP from the tree **after** the build is accepted, and record a new SHA-256.

Until step 1 is possible, **the packaging deliverable is a corrected source tree, not a corrected
document.** This is stated plainly because the distinction is the whole point of the item.

## F. Verdict on workstream I

**NOT VERIFIED.** The source is consistent and structurally sound; the PDF and the ZIP are both
stale relative to it; no build is possible in this environment. This is a toolchain/access blocker,
independent of the mathematical state of the manuscript.

---

# Stage 16 packaging

## 1. What was rebuilt

`HFF_Final_Overleaf_Package.zip` was regenerated from exactly the tracked sources by
`python3 audit_stage15/build_package.py`, which is deterministic: fixed member order, fixed
timestamps (2026-10-19), deflate level 9, sorted directory walks. The member count, byte size and
hash are not restated here — `package_manifest.txt` is the record, and the ZIP contains this file,
so any literal figure printed here would be stale the moment the archive is rebuilt.

The ZIP now contains, at its root: `main.tex`, `references.bib`, `main.pdf`, `README.md`,
`chapters/`, `figures/`, `audit_stage15/` (suite, mutation harness, manifest, correction log),
the supporting reports and `project_archive/`. This matches the tree printed in `README.md`.

## 2. Integrity record

`audit_stage15/package_manifest.txt` holds the ZIP's SHA-256, its size, its member count, and the
SHA-256 of every member. The hash is deliberately kept **out of** `README.md`: that file is itself a
ZIP member, so a literal hash inside it could never match the archive containing it. The manifest is
the record.

## 3. Build status — NOT EXECUTED, and not claimed

There is no TeX engine in this environment (`pdflatex`, `latex`, `tectonic` and `lualatex` are all
absent). Therefore:

- **no rebuild of `main.pdf` was performed**;
- the bundled `main.pdf` is the last successful build (49 pages) from the **pre-Stage-16** sources;
- the bundled PDF does **not** contain D-26 … D-31, and its page count will change once recompiled
  (the register grew by six rows and chapter 8 by two displayed equations);
- `README.md` now states this explicitly, and §7 of `regression.py` prints a staleness warning
  naming every source file newer than the PDF. That section **asserts nothing** — it cannot, because
  the toolchain is missing; it reports.

The consequence is honest rather than convenient: a reader who compiles the ZIP gets the corrected
document, while a reader who opens the bundled PDF gets the previous text. The README says so in the
first paragraph that mentions the PDF.

## 4. Reproducing

    python3 audit_stage15/build_package.py     # writes the ZIP and the manifest
    python3 audit_stage15/regression.py        # 56 checks, exit 0
    python3 audit_stage15/mutation_test.py     # 6 mutants, all must be caught

---

# Stage 17 rebuild of the package

The archive is rebuilt deterministically (fixed member order, fixed timestamp `(2026,10,19)`,
deflate level 9) after the Stage 17 source and audit edits, with:

    python3 audit_stage15/build_package.py
    HFF_Final_Overleaf_Package.zip   75 members

The **authoritative** SHA-256, size and per-member hashes are in
`audit_stage15/package_manifest.txt`, regenerated with the archive. That file is deliberately
**not** a ZIP member — the manifest cannot contain the hash of the archive that contains it, and by
the same argument no hash printed *inside* this report describes the archive that contains this
report. The manifest is therefore the record; a number typed here would be stale by construction.

Stage 17 additions to the archive: `audit_stage15/equation_fingerprints.json`,
`audit_stage15/mutation_campaign_stage17.py`, `audit_stage15/mutation_stage17_results.txt` and the
new report files (`12_…`, `13_…`), plus the corrected `chapters/*.tex` of D-32, D-26/NEW-05 and
D-29/I-11.

**The PDF is still stale.** No TeX engine exists here; `main.pdf` remains the 49-page pre-Stage-16
build. `regression.py` §7 reports (does not assert) that `main.pdf` predates every modified source,
and `README.md` states it. Items I-13 and I-15 stay **OPEN** until a real TeX/TikZ build and a visual
figure check are performed by someone with the toolchain.
