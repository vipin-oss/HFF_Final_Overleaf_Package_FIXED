# HFF Stage‑5 — Git synchronisation and change report

**Date:** 19 October 2026
**Report scope:** identification of the repository, state at the start of the session, files inspected, differences found, and every change made. No history was rewritten and nothing was deleted.

---

## 1. Repository identification

| Item | Value | How established |
|---|---|---|
| GitHub repository | `vipin-oss/HFF_Final_Overleaf_Package_FIXED` | `gh repo view`; remote URL `https://github.com/vipin-oss/HFF_Final_Overleaf_Package_FIXED.git` |
| Visibility | private | `gh repo view --json isPrivate` |
| Default branch | `main` | `gh repo view --json defaultBranchRef` |
| Remote `main` head | `5a255212a51374f7eb178647eb12b0a9c2b67ded` | `git ls-remote origin` |
| Working branch | `arena/c875f9b3-hff-final-overleaf-package-fix` | pre‑created for this session, branched from `5a25521` |
| Starting commit | `5a255212a51374f7eb178647eb12b0a9c2b67ded` — *"Initial Overleaf Import"* | `git log` |
| Tags / other branches | none (only `main` and the working branch) | `git branch -a` |
| Open pull requests | none | `gh pr list --state all` |
| Working tree at start | clean | `git status --short` |

Identification was unambiguous: a single repository matching the project, containing the LaTeX sources, the compiled PDF, the Stage‑4 audit records and the pre‑coding checklist. No other candidate repository was found. No change was made to `main`, and no commit was made to `main`.

---

## 2. Starting state — files inspected

### 2.1 Document sources

| Path | Content | Inspected for |
|---|---|---|
| `main.tex` | document assembly | structure, chapter order, compile settings |
| `chapters/ch01.tex` | introduction/positioning | claims, literature framing |
| `chapters/ch02.tex` | configuration, assumptions A1–A10, geometry, properties, sign conventions | baseline data, property freeze, normal convention |
| `chapters/ch03.tex` | mass, momentum, energy, solid conduction, constitutive, equilibrium | strong forms and source attributions |
| `chapters/ch05.tex` | interface and boundary conditions (B1–B9) | traction/flux conditions, normal definitions, B6 sign |
| `chapters/ch06.tex` | dimensionless groups | `Gr`, `Ri`, `Br` and the `D_h`/`H₀` basis |
| `chapters/ch07.tex` | baseline arithmetic table | reproducibility of the design numbers |
| `chapters/ch08.tex` | discretization, weak form, solution procedure, quality controls, post‑processing | **weak-form signs**, `Nu` definition, mesh/conservation criteria |
| `chapters/ch09.tex` | verification/validation hierarchy V‑A…V‑G, staged decisions, independent replication | benchmark definitions and normalizations |
| `chapters/ch10.tex`, `ch11.tex` | contribution, limitations | claims and stated limitations |
| `chapters/audit_appendix.tex` | register, open checks C‑1…C‑12, bibliographic statement | open items and their status |
| `chapters/appendix.tex` | notation and arithmetic | symbol definitions |
| `figures/fig_geometry.tex`, `figures/fig_signs.tex` | TikZ figures | geometry/sign figure consistency |

### 2.2 Records and artefacts

| Path | Inspected for |
|---|---|
| `references.bib` | every entry (18), against Crossref/publisher where a DOI exists |
| `HFF_final_reference_status.csv` (+ `_notes.txt`) | Stage‑4 per-reference status; **three errors found** |
| `HFF_final_pre_coding_checklist.md` | Stage‑4 requirement statuses |
| `HFF_final_packaging_report.md`, `HFF_packaging_correction_note.md`, `HFF_revision_summary.md`, `HFF_source_pdf_consistency_report.md`, `README.md` | prior audit decisions and stated PDF/source consistency |
| `project_archive/**` (audit/, HFF_Independent_Audit_2/, HFF_Reconciliation_2/) | prior audit trail; **left untouched** |
| `main.pdf` | 49 pages; text extraction confirms the benchmark values (`4.861`, `7.541`, `8.235`, `5.385`) are present in the Stage‑4 build |

### 2.3 Comparison with the ZIP package

**No `HFF_Final_Overleaf_Package_FIXED.zip` (or any ZIP) exists in this session.** Nothing was uploaded to the workspace besides the repository checkout, so a byte-level comparison of ZIP vs Git could not be performed.

The comparison was therefore made **inside** the repository: the compiled PDF against the sources, and the Stage‑4 records against each other and against the primary literature. Result: the Stage‑4 PDF was consistent with the Stage‑4 sources (values present, 49 pages as claimed in `README.md`); the *records* were not fully consistent with each other (see §3).

If the ZIP is re‑uploaded, the comparison to request is: ZIP `main.pdf` vs repository `main.pdf`, and ZIP `references.bib` vs repository `references.bib` — the latter is the only file changed in this stage that also exists in the ZIP.

---

## 3. Differences found

### 3.1 Between Git and the Overleaf source (within the repository)

None at the start: the checkout was clean, `main` and `origin/main` were identical, and no local modifications existed. The repository already contained the latest Stage‑4 corrections.

### 3.2 Internal inconsistencies within the package

| # | Location | Finding | Severity |
|---|---|---|---|
| D1 | `chapters/ch08.tex` `eq:weaks` | solid-elasticity boundary term sign contradicted the chapter's own integration-by-parts prose and the single-normal convention; with the old sign, a pressure load entered as a suction and the two interface terms added instead of cancelling | **high** — affects the load-bearing argument of the formulation |
| D2 | `chapters/ch08.tex` `eq:weaktf` | fluid-energy boundary term sign contradicted the prose; the stated thermal cancellation fails as printed | **high** |
| D3 | `chapters/ch05.tex` B6 | `−k_s∇T_s·n_out = q″` describes heat *extraction* for `q″>0`, while the text (A10) and `eq:weakts` treat `q″` as a heater | **high** — wrong sign of the thermal load |
| D4 | `chapters/ch08.tex` post-processing | `q_w = −k_f∇T_f·n` is the flux *out of* the fluid, so `h = q_w/(T_w−T_b)` is negative on a heated wall and `Nu` would come out negative | **high** — would have invalidated every thermal benchmark comparison |
| D5 | `chapters/ch05.tex` | traction balance written with `n` for the solid and `n_f = −n` for the fluid (two norms in one equation) | medium — result correct, statement wrong |
| D6 | `chapters/ch08.tex` | `a_T`, `a_kf`, `a_ks` used but never defined | medium — blocks independent implementation |
| D7 | `chapters/ch08.tex` | Taylor–Hood sentence implied Hood–Taylor supports the discrete inf–sup condition; it establishes the element, not the LBB proof | medium — bibliographic over-attribution |
| D8 | `references.bib` `rahimi2024conjugate` | given name "Peyman" unsupported; publisher byline is "Z. Rahimimotlagh" (Zahra) | medium — fabricated-looking field |
| D9 | `HFF_final_reference_status.csv` | Soti DOI `…01.014` (an unrelated paper), Lesoinne pp. 71–99, Christov pp. 267–305; the `.bib` was correct in all three cases | medium — audit record, not manuscript |
| D10 | `chapters/audit_appendix.tex` | bibliographic statement said Gupta's title and DOI were "not retrievable", contradicting the reference table | low |
| D11 | `chapters/audit_appendix.tex` | C‑1 listed as fully open after the T1 value had become confirmable | low |
| D12 | `HFF_final_pre_coding_checklist.md` | rows 1, 3, 11 marked COMPLETE on the basis of the text alone; the checks above show they were not | medium |

No difference was found that required changing the model, the geometry, the material values, the operating point, the dimensionless groups, or the research direction.

---

## 4. Changes made

All changes are on `arena/c875f9b3-hff-final-overleaf-package-fix`. `main` is untouched.

| # | File | Change | Motivation |
|---|---|---|---|
| S1 | `chapters/ch08.tex` | `eq:weaks` RHS: `+∫σ n·φ` → `−∫σ n·φ` | D1 |
| S2 | `chapters/ch08.tex` | `eq:weaktf` RHS: `−∫k_f∇T_f·nχ` → `+∫k_f∇T_f·nχ` | D2 |
| S3 | `chapters/ch05.tex` | B6: `−k_s∇T_s·n_out = q″` → `+k_s∇T_s·n_out = q″`; remark notes `q″>0` is heat supplied | D3 |
| S4 | `chapters/ch05.tex` | traction balance: `σ⁽ˢ⁾·n + σ⁽ᶠ⁾·n_f = 0, n_f = −n` → `σ⁽ˢ⁾·n_s + σ⁽ᶠ⁾·n_f = 0, n_s = −n, n_f = n` | D5 |
| S5 | `chapters/ch08.tex` | added one sentence fixing each boundary-term sign by the subdomain outward normal | prevents re‑introduction of D1/D2 |
| S6 | `chapters/ch08.tex` | `q_w = −k_f∇T_f·n` → `q_w = +k_f∇T_f·n` ("into the fluid") | D4 |
| S7 | `chapters/ch08.tex` | Taylor–Hood sentence split: origin → Hood–Taylor; inf–sup stability → Brezzi–Fortin | D7 |
| S8 | `references.bib` | `hood1974navier`: `pages = {121--132}`, editors added, note updated (no DOI exists) | Hood–Taylor verification |
| S9 | `references.bib` | `shah1978laminar` note: Table 43 confirmation, wetted-perimeter basis, residual page check | C‑1 |
| S10 | `references.bib` | `rahimi2024conjugate`: `Peyman` → `Zahra` | D8 |
| S11 | `chapters/audit_appendix.tex` | C‑1 updated to "closed at table level" with the residual page check | D11 |
| S12 | `chapters/audit_appendix.tex` | bibliographic integrity statement corrected (Gupta; Hood–Taylor pages; Shah) | D10 |

### 4.1 New files (this stage)

| File | Purpose |
|---|---|
| `HFF_stage5_benchmark_verification.md` | full verification of `Nu_T1 = 4.861` and of Hood–Taylor; remaining requirements; final decisions |
| `HFF_stage5_reference_status.csv` | 18-row reference register with Stage‑5 evidence and the three Stage‑4 record corrections |
| `HFF_stage5_pre_coding_checklist.md` | 24-row evidence-based checklist, 12 COMPLETE / 9 INCOMPLETE / 3 UNRESOLVED |
| `HFF_stage5_git_sync_report.md` | this report |

### 4.2 Not changed

- `main.tex`, `chapters/ch01,02,03,04,06,07,09,10,11`, `figures/`, `main.pdf`
- every file in `project_archive/` (all prior audit records preserved verbatim, including the ones whose summaries are now known to contain errors; the errors are recorded in the Stage‑5 CSV rather than silently edited)
- `HFF_final_reference_status.csv`, `HFF_final_pre_coding_checklist.md` and the other Stage‑4 records (superseded, not overwritten)
- all equations' *physics*, all numerical values, tolerances and parameters

---

## 5. Compilation status

**`main.pdf` was not regenerated.** No TeX distribution is present in this sandbox (`pdflatex`, `latexmk`, `tectonic` all absent) and package installation is not possible within the allowed network egress. The bundled PDF remains the 49-page Stage‑4 build and is now one revision behind the source on the edited lines.

**Action required by the project owner:** recompile in Overleaf (`pdfLaTeX` → `bibtex` → `pdfLaTeX` ×2) and confirm:
1. no new warnings reference `eq:weaks`, `eq:weaktf`, `eq:weakts` or the B6 row;
2. the Hood–Taylor entry renders with pages 121–132;
3. the PDF page count remains 49 and the cross-references are unchanged.

The edits are sign changes inside display maths, two prose sentences, and reference fields; no LaTeX structure, label, `\ref`, or package dependency was altered.

---

## 6. Git operations performed

- No branch creation was necessary: this session is bound to `arena/c875f9b3-hff-final-overleaf-package-fix`, which was already branched from `5a25521`.
- No force-push, no rebase, no history rewrite, no deletion.
- `main` was never checked out for modification and never pushed to.
- Changes committed on the working branch only, and pushed to `origin/arena/c875f9b3-hff-final-overleaf-package-fix`.

---

## 7. Integrity statement

- The original project history is preserved; nothing was deleted or overwritten in place.
- Previous audit records were retained even where their summaries are now known to be inaccurate; the inaccuracies are documented instead of erased.
- No solver code was written and no simulation was run.
- No reference, page number, DOI, or benchmark value was invented. Unverified facts are marked UNRESOLVED with the evidence they need.
- Every source claimed as inspected in this report was actually opened during this session; sources relied on indirectly (e.g. the printed Shah & London volume) are explicitly labelled as not inspected.
