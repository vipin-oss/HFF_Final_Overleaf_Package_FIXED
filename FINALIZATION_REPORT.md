# HFF finalization report — Stage 20

**Repository** `vipin-oss/HFF_Final_Overleaf_Package_FIXED`
**Branch** `arena/c875f9b3-hff-final-overleaf-package-fix`
**Final implementation commit** `3d58e775a7d71966fe3d50e11541c08994b02eff` (parent `90b237f`, Stage 19)
**Working tree at the time of writing** clean, except the untracked audit deliverable
`independent_audit_stage19/` (which is not part of the package, by design) and this report. The only
commit after `3d58e77` contains this file and nothing else, so `3d58e77` is the full content change of
Stage 20.

**Status: BLOCKED — AUTHOR DECISION REQUIRED.**

The manuscript text, the checks and the package are final and self-consistent: 163/163 checks pass,
the Stage 18 and Stage 19 campaigns and the Stage 20 probe all detect what they are supposed to
detect, and the archive rebuilds deterministically to a recorded hash. Two independent things stand
between this and *READY FOR SUBMISSION*, and neither is a manuscript defect:

1. **Five items need an author decision** (section 7). Until the headline ratio, the outer-face
   condition and the heater description are decided, the text reports them as open, and no automated
   check can close them.
2. **The typeset PDF has not been produced in this environment** (section 6). There is no TeX engine
   here, and the `main.pdf` inside the package predates every audit stage. It is a binary I inherited,
   not a build of this source. I did not and will not claim that the sources compile or that the PDF
   matches the text.

Nothing in this report should be read as self-approval: the verdict above is a statement about what
was and was not executed, not a judgement that the paper is correct. Solver readiness is a separate
matter and remains **NOT READY** (section 8).

---

## 1. What was in scope

One bounded repair cycle, closing the four findings of the independent Stage 19 acceptance audit
(`independent_audit_stage19/HFF_Stage19_Independent_Acceptance_Audit.md`, verdict *conditional
acceptance*):

| Finding | Subject |
|---|---|
| F-1 | Q8 observation height and the withdrawn through-thickness claim |
| F-2 | The gauge explanation was not required to be in the formulation |
| F-3 | Three legitimate heated-face sentences were rejected by the flux-location test |
| F-4 | `eq:beamcol` had no substantive check |

Plus one defect I found while rebuilding the package, S20-5, which blocks any build (section 3.5).
Nothing else was reopened. No Stage 21 exists. The audit programme is closed.

## 2. Changed files

Seventeen files, 998 insertions, 61 deletions, in commit `3d58e77`:

| File | Change |
|---|---|
| `chapters/ch04.tex` | Q8 paragraph rewritten: mid-surface sampling, corrected clamp, through-thickness claim withdrawn, convergence language restricted to what the meshes support |
| `chapters/ch02.tex` | Assumption A9 likewise (`$0.2\%$`, `$-0.045$`, mid-surface) |
| `chapters/ch11.tex` | End-effect paragraph likewise |
| `chapters/audit_appendix.tex` | D-26 values and scope; **new register row D-35**; S20-5 cell rebalancing of D-32…D-35 |
| `audit_stage15/regression.py` | Suite v5 → v6: 156 → 163 checks (F-1 ×2, F-2 ×2, F-4 ×2, table shape ×1, plus the two existing `eq:beamcol` checks re-pointed at parsed coefficients) |
| `audit_stage15/q8_height_study.py` | **new** — independent fixed-height Q8 study, six meshes, three heights |
| `audit_stage15/stage20_probe.py` + `_results.txt` | **new** — ten-case targeted probe of the repaired findings |
| `audit_stage15/table_shape_check.py` | **new** — static cell-count check against every table's column specification |
| `audit_stage15/equation_fingerprints.json` | regenerated twice, deliberately and documented below |
| `audit_stage15/01_master_issue_ledger.md` | Stage 20 section, S20-5 entry, final tally |
| `audit_stage15/05_correction_log.md` | S20-A … S20-E entries and a supersession note on the Stage 19 sentences that F-1 contradicts |
| `audit_stage15/15_stage19_repair_report.md` | correction note on its own Q8 table |
| `audit_stage15/stage18_mutation_results.txt`, `stage19_mutation_results.txt` | re-run evidence |
| `audit_stage15/package_manifest.txt`, `HFF_Final_Overleaf_Package.zip` | rebuilt package and manifest |

`origin/main` (`5a25521`) was not touched and no independent audit branch was modified. All work is on
the Arena implementation branch.

## 3. The corrections

### 3.1 F-1 — observation height (S20-A, register D-35)

The Stage 19 text said the Q8 ratios "shift with the through-thickness discretisation". They do not.
The evidence script read lattice rows `lat[(NX,1)]` and `lat[(NX,2)]`, whose physical heights move with
the mesh: `y=d/4, d/2` for two elements through the thickness, `y=d/8, d/4` for four. The "shift" was
a change of sampling height.

`audit_stage15/q8_height_study.py` re-solves the same six meshes with independent code (own mesh, own
shape functions validated by finite differences, own banded Cholesky, patch test on the exact
stress-free field at `1e-13`) and samples three fixed heights. At the mid-surface `y=d/2`:

| mesh `NX×NY` | elements | POINT | PIN | CLAMP |
|---|---|---|---|---|
| 6×2 | 12 | 1.0000 | 0.9999 | −0.0803 |
| 12×2 | 24 | 1.0000 | 0.9981 | −0.0450 |
| 24×2 | 48 | 1.0000 | 0.9979 | −0.0288 |
| 6×4 | 24 | 1.0000 | 0.9998 | −0.0660 |
| 12×4 | 48 | 1.0000 | 0.9981 | −0.0379 |
| 24×4 | 96 | 1.0000 | 0.9980 | −0.0253 |

Read correctly: point pins are `1.0000` everywhere; the pin ratio depends only on the axial mesh and
falls from `0.9999` to `0.9979` as the strip goes from twelve to forty-eight elements; doubling the
through-thickness mesh changes either pin ratio by at most `0.0001`; only the clamp magnitude is
mesh-dependent, falling from `0.045` to `0.029`. The `0.2 %` (`0.0019` of `κ_th L²/8`) pin difference
is therefore a finite-mesh result, not a converged one, and the text now says so — the sentence "the
pin ratio approaches 1" is withdrawn, and no Richardson extrapolation is attempted. The Stage 19
report's own table carries a correction notice pointing here.

### 3.2 F-2 — the gauge explanation must be in the formulation (S20-B)

The old check counted a pattern anywhere in the tree, so the D-30 register row — which *describes* the
removed gauge constraint — kept it green even after the whole argument was deleted from `ch08`. Two
checks are now scoped to `chapters/ch08.tex`: one requires at least one gauge occurrence in the
formulation, the other requires the "No pressure gauge is required" statement there. The manuscript
needed no change; the test was wrong.

### 3.3 F-3 — legitimate heated-face descriptions (S20-C)

The detector required the literal `on Γ_h^0` *after* the flux. The clause carrying the flux is now
located with `_clause_of()` (delimited by `;` and `:`) and searched in either direction for the symbol
or for *outer/heated face, surface, wall, side*. Three legitimate constructions pass; a flux placed on
`Γ_if` in prose and a double thermal datum with no surface named are still rejected, so the protection
against an actually incompatible datum is intact rather than relaxed away.

### 3.4 F-4 — `eq:beamcol` is parsed (S20-D)

The Stage 19 checks compared the coded solution with hard-coded `κ_th`; the printed equation was never
read, so `w''(0)=w''(L)=−κ_th` → `−½κ_th` survived the suite *and* fingerprint regeneration. The printed
ODE `D_s w'''' + N_θ^c w'' = 0` and the printed end condition `w''(0)=w''(L)=−c κ_th` are now parsed,
and the parsed coefficients drive the residual and the boundary-condition test. `c=1` is not invented:
the text defines `M = D_s(w''+κ_th)` and requires `M=0` at the pins, so the zero-moment condition *is*
`w''=−κ_th`. Parsed result: `1.0·D_s + 1.0·N_θ^c`, ODE residual `1.46e-11`. Side effect: Stage 18 cases
A1 and A18 were fingerprint-only and are now detected substantively (38 substantive, 6 fingerprint-only,
instead of 36/8).

### 3.5 S20-5 — a hard LaTeX error in the register (found during the rebuild)

`chapters/audit_appendix.tex` declares four columns; rows D-33, D-34 and D-35 carried six cells each and
D-32 carried three. A row with more `&` than the declaration is a hard LaTeX error — the document would
not have compiled. Every gate in this repository is semantic; none counted cells, so three stages each
added "evidence" and "dependencies" columns to a table that had four. The three rows are folded back into
four columns (the resolution cell now carries `… Dependencies: … Recalculation: …`; no content lost), and
D-32's empty status cell is filled with `resolved (Stage 16)`, taken from the ledger and the D-32
correction entry, not invented.

`audit_stage15/table_shape_check.py` counts cells against the declared specification, brace-aware and
honouring `\multicolumn`: **16 files, 156 rows, 0 over-full, 0 short**. One suite check runs it and probe
case E1 injects an extra `&` with fingerprint regeneration → DETECTED.

## 4. Final verification results

All run on the final tree, in this environment, in this order.

| Gate | Result |
|---|---|
| Regression suite v6 | **163 / 163 pass** |
| Stage 18 mutation campaign | **44 / 44 detected** — 38 substantive, 6 fingerprint-only |
| Stage 19 mutation campaign | **10 / 10 detected**, all substantive; **3 / 3 controls** behave as intended |
| Stage 20 probe (F-1…F-4 + S20-5) | **10 / 10** as intended (6 must-fail cases DETECTED, 3 legitimate cases PASS, 1 build-integrity case DETECTED) |
| Table shape | 16 files, 156 rows, 0 over-full, 0 short |
| Label/reference static scan (ad hoc, not a suite check) | 89 labels, 0 duplicates, 0 undefined `\ref`/`\eqref`, environments and braces balanced |

Fingerprints: **79 entries** throughout. They were regenerated twice, each time deliberately and in the
open: once for the corrected D-26 values and the new D-35 row (`reg:D-26` changed, `reg:D-35` added),
once for the S20-5 cell rebalancing (`reg:D-32`…`reg:D-35`). **No display-equation fingerprint changed in
either pass.** Regeneration is never used here to make a failing substantive check pass: F-4 and E1 both
regenerate *and* still fail, which is the point of the F-4 repair.

Numbers that are unchanged by this stage and re-verified by the suite: `θ̄ = 32.265 K`, `T_cr = 117.4953 K`,
`58.7 K` ceiling at `M_b=2`, `M_b = 3.6415`, `w_max = 2.1886e-4 m`, `Γ_p = 2382.1 / 1714.3 / 1726.3`,
`σ_max = 13.92 / 13.01 MPa`.

## 5. Package integrity

`HFF_Final_Overleaf_Package.zip`, rebuilt from the final tree by `audit_stage15/build_package.py`:

- **SHA-256 `46e290c452ef2e3d0673a06c28520ee7b57c1b269a31f7b9edcb95b6046b20cf`**, 895 520 bytes, **91 members**.
- Recorded in `audit_stage15/package_manifest.txt` together with the SHA-256 of every member; **all 91
  member hashes re-verified against the archive, 0 mismatches**.
- Deterministic: an immediate rebuild reproduced the manifest byte-for-byte.
- `zipfile.testzip()` clean. No byte-code caches are shipped.
- The archive contains the sources, `main.pdf`, the chapters, figures, `audit_stage15/` (including the
  three new scripts and the probe results) and the `project_archive/` material. It does **not** contain
  this report (the report quotes the archive hash) and does not contain the untracked
  `independent_audit_stage19/` audit.

## 6. Build and PDF status — NOT EXECUTED

**No TeX engine and no PDF tooling exist in this environment.** I checked explicitly: `pdflatex`,
`latexmk`, `tectonic`, `xelatex`, `lualatex`, `pdftotext`, `pdftoppm`, `pdfinfo`, `gs` and `qpdf` are all
absent. Therefore:

- **LaTeX build: NOT EXECUTED.** I make no claim that the sources compile.
- **PDF content/visual inspection: NOT EXECUTED.** I make no claim that the PDF matches the text.
- **`main.pdf` is stale, and worse than stale.** Its `CreationDate` is `D:20261019055805Z`
  (2026-10-19 05:58 UTC) and it was committed in `5a25521` "Initial Overleaf Import". It predates
  **every** audit stage from 14 to 20. The PDF inside the package therefore does not contain any
  correction described in this report. It is a binary inherited from the author's original upload, not
  an output of the current source tree.
- Items **I-13** (build) and **I-15** (figure render / visual verification) from the independent audit
  therefore **remain OPEN**.

What the static checks do and do not tell you. They confirm: every table row has its declared cell
count, every `\ref`/`\eqref` target exists, no label is duplicated, and environments and braces balance
in all 16 scanned files. They cannot see unmatched `\left`/`\right`, undefined control sequences,
missing packages, `siunitx` version quirks, overfull boxes, page-break quality, or whether a figure
renders as intended. A cell count is not a compile.

**Exact steps for the author** (any TeX Live 2023+ or Overleaf build):

```
pdflatex -interaction=nonstopmode -halt-on-error main.tex   # pass 1
bibtex main                                                 # references.bib
pdflatex -interaction=nonstopmode -halt-on-error main.tex   # pass 2, resolves refs
pdflatex -interaction=nonstopmode -halt-on-error main.tex   # pass 3, resolves longtable widths
```

Then inspect, in this order: (1) the appendix register table D-1…D-35 — it should now build at all, with
four columns per row; (2) the Q8 paragraph at the end of the buckling section and A9 in Chapter 2 for the
`−0.045` / mid-surface wording; (3) `eq:beamcol` and the sentence that defines `M = D_s(w''+κ_th)`,
which now has a test behind it; (4) the figures, which nobody has ever rendered in this environment
(I-15); (5) the log for undefined references and overfull boxes. After the rebuild, re-run
`python3 audit_stage15/regression.py`: the "tracked main.pdf exists" check passes either way, and the
freshness section will stop warning once the PDF is newer than the sources.

## 7. Unresolved items — one list for the author

These are **not** defects and are **not** closable by me. Each is a scientific or scope decision that
changes what the paper claims. My recommendation, where the evidence points one way, is in italics.

| # | Item | Why it is open | My recommendation |
|---|---|---|---|
| 1 | **RU-01 — outer-face condition**: free, backed by a vented cavity, or in contact with the rigid casing? No standoff distance is stated anywhere in the source | It decides whether the clamp limit or the free limit is the physically relevant bound, i.e. whether `−0.045` is a curiosity or the design case | *State the standoff explicitly and keep the strip free-standing; the casing is already declared adiabatic and rigid, and the clamp comparison is then a bound, which is how the text uses it* |
| 2 | **RU-03 — mid-span passage height**: under the adopted convention the gap is `H₀ + w_max = 1.4377 H₀`; the source never says so | It is a consequence of the model, not a choice within it, but stating it invites a `1.44 H₀` reading of the channel | *State it once, next to `w_max`, as a derived consequence; it is the strongest single number showing the deflection matters* |
| 3 | **Heater mounting / heated-face interpretation** | Whether `q''` sits on the fluid-side or casing-side face changes the through-wall drop and hence `θ̄` | *Keep the fluid-side face, which is what every printed number assumes; add one sentence naming the face and the mounting* |
| 4 | **Contact law** for the strip against the casing | No law is specified and none is needed while the strip is free; it becomes load-bearing the moment item 1 is answered "in contact" | *Do not add a contact law; scope the paper to the free strip and say the contact case is out of scope* |
| 5 | **Intended headline `Γ_p`**: `2382.1` (mixed) or `1714.3` / `1726.3` (like-for-like) | The mixed ratio divides an amplified numerator by an unamplified denominator; both are reported and labelled, but which one is "the" result is an authorial choice | *Quote the like-for-like value as the headline and the mixed one as the design-facing number; the like-for-like ratio is the one that means "amplification", and both clear the A-5 threshold by two orders of magnitude* |

Items 1 and 4 are coupled: answering 1 as "in contact" reopens 4, and would require a new derivation and
a new stage, which the freeze forbids.

## 8. Accepted limitations

Class **B** (documented and accepted, not fixed):

- **A passing suite is not a proof.** The checks pin what the manuscript says and recompute the printed
  numbers from the printed inputs. They do not prove the model, and they cannot tell a correct equation
  from a wrong one that is consistently labelled. F-4's repair makes one equation *self-consistent with
  its own derivation*, which is weaker than deriving the reduced beam-column model from the
  three-dimensional problem.
- **Fingerprint layers are change detection, not correctness.** Six of the 44 Stage 18 detections are
  fingerprint-only, and the campaign says so in its own summary.
- **Q8 evidence is finite-mesh.** The clamp magnitude is not converged and the pin ratio is a trend in
  the axial mesh. No extrapolation is claimed, and the end-compliance correction is not applied.
- **`Γ_p` nomenclature.** Both ratios remain in the text, labelled; see item 5 above.
- **Table-shape check is syntactic and narrow** (section 3.5): it sees cell counts, nothing else.
- **Build and render are NOT EXECUTED**, and the shipped `main.pdf` predates the corrections (section 6).

Class **C** (author decision): the five items in section 7.

**Solver status: NOT READY**, and deliberately unchanged by this stage. This stage repaired a manuscript
and its checks; it did not write, run or validate a solver. Nothing here should be read as evidence that
the finite-element implementation described in the paper exists, converges, or reproduces these numbers.

## 9. Freeze

With this report the Stage 20 repair cycle is closed. The remaining issues are stated once, above, and
will not be reopened. No Stage 21, no further mutation campaign, no additional verification layer. The
only things that should now change the repository are the author's answers to section 7 and the LaTeX
rebuild of section 6.
