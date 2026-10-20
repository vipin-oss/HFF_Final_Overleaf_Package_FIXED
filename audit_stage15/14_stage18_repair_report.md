# Stage 18 — repair of the verification defects (implementation report)

**Branch:** `arena/c875f9b3-hff-final-overleaf-package-fix` (the only push target; `origin/main`
stays at `5a255212`, `claude/independent-audit-7c9749f` is untouched).
**Parent:** `a61837e` (the Stage 18 acceptance audit, which found that no Stage 18 existed).
**Implementation baseline on entry:** `211f751`, regression suite **v3**, 109 assertions.
**Status:** implemented, executed and mutation-tested here; **not independently verified**. The
coupled production solver remains **NOT READY**. Commit hashes are in §12; the ZIP hash is in
`audit_stage15/package_manifest.txt` line 2 and in the commit message (this report is itself a
member of the archive, so it cannot quote the archive's own hash).

Every number below comes from an executed command. Nothing in this report is a claim about a build,
a render, a solver run or an iteration history: those were **not executed** (§13).

---

## 0. Summary of what changed

| # | Defect (Stage 18 request) | Repair | Guarding assertions | Mutation proof |
|---|---|---|---|---|
| 1 | `or True` unconditional pass in `regression.py` | removed; two real assertions (figure-verification claim; ledger status) | 2 | V1 |
| 2 | Gauge detection exempted any constraint near its explanation | condition-based sentence test, no exemption window | 2 | G1, G2 |
| 3 | BC set not validated against the real solid/fluid definitions | `tab:bcs` parsed row by row + surface-clause parsing of the prose | 5 | G3 |
| 4 | Numerics not independently validated (`θ̄` cell, `T̄_cr`, `M_b≥2`, `eq:wmax`) | recomputation from the printed cell/formula and from parsed inputs | 19 | T1, T2, F1 |
| 5 | Nomenclature `Γ_p` entry never checked; stale end-condition claims | nomenclature row validated and made precise; sentence-scoped scan of 22 files | 4 + 1 | N1, S1, S2 |
| 6 | Fingerprints could launder a corrupted equation | `--update-fingerprints` no longer short-circuits; banner; substantive checks decide | 1 behaviour | F1 |
| 7 | Mutation campaign incomplete | 44 cases, fresh copies, declared intended assertion, raw evidence | — | 44/44 executed |
| 8 | No statement that well-posedness ≠ convergence | `ch08` paragraph defining `‖ΔT_Γ‖` and its use as a stopping criterion | — | — |

Suite size: **v3 = 109 assertions → v4 = 144 assertions**, of which 68 parse numbers out of the
manuscript and compare them with values recomputed in code (§9).

---

## 1. `or True` (finding F1 of the audit, §1 of the request)

`grep -n "or True\|if True\|pass$"` over `regression.py` returns exactly one site (v3 line 175):

```python
check("figure fix is not claimed as visually verified",
      ('I-15' in read('audit_stage15/01_master_issue_ledger.md')) or True)
```

It passed unconditionally. It is replaced by two assertions that read the actual sources:

* `no chapter claims a visual verification of a figure (I-15 remains open)` — every chapter, figure
  and `main.tex` is scanned for positive claims (`visually verified`, `visual check passed`,
  `rendered correctly`, `verified by eye`, `figures were inspected`). There is **no exemption
  window**: a claim is a claim anywhere in the text.
* `the ledger still records I-15 as OPEN` — regex on the I-15 row of
  `01_master_issue_ledger.md` requiring `**OPEN**`.

No other unconditional-success path was found: `check()` appends to `FAIL` on a false argument, and
the two `check` sites inside `cmp()` are reached only through `cmp(name, printed, computed, tol)`,
which itself fails when the printed value cannot be found. A missing source file no longer produces
a traceback either: `REQUIRED` files are listed explicitly and their absence exits non-zero with
`FAIL  required source files missing: …` and the explicit statement that no check was executed
(probes: `rm chapters/ch07.tex`, `rm references.bib` → exit 1, no traceback, no "PASSED").

**Mutation V1** inserts `Figures were visually verified against the source files.` after the
`ch09` section head. v4 exits 1 with
`FAIL  no chapter claims a visual verification of a figure (I-15 remains open)`. The claim is
therefore falsifiable; it is not an unconditional pass.

---

## 2. Gauge detection (§2 of the request)

### 2.1 Why the old check could not work

v3 searched `\int … p … = 0` in `ch08` only, then *forgave* every hit that had `over-determine` or
`Constraining` within ±260 characters:

```python
explained = [i for i in gauge_hits if ('over-determine' in C8[i-260:i+260]) or …]
check("no pressure-gauge constraint in any notation", len(gauge_hits) == len(explained))
```

Any constraint placed next to the sentence that rejects it is exempt by construction. Verified: with
v3, appending `the level is fixed by imposing $\int_{\Om_f}p\,\mathrm dx=0$` to the D-30 sentence
**passes 109/109**. (An earlier suspicion that the v3 regex was vacuous was tested and disproved —
it does match both occurrences; the defect is the exemption window, not the pattern.)

### 2.2 What replaces it

`P_NORM` — five patterns for the *mathematical condition* in any notation: `\int … p … = 0`,
`\langle p\rangle = 0`, `\overline{p} = 0`, `\bar p = 0`, and the phrases `zero-mean pressure` /
`mean-zero pressure`. Files scanned: all 16 source files (not `ch08` alone).

For each occurrence the **sentence** that contains the condition is located (sentence boundaries, not
a character window) and must satisfy both

* `REJECT` — rejecting language present (`over-determine`, `would be inadmissible`, `would inject`,
  `spurious`, `nothing is imposed`, `is not imposed`, `must not be`, `no gauge`, `no such freedom`,
  `rather than`, `instead of`, `unnecessary`, `redundant`, `not required`), **and**
* `ADOPT` — adopting language absent (`we impose/fix/set/enforce/adopt/normalise`,
  `is imposed/enforced/fixed/required/normalised`, `imposes`, `enforces`, `adding the`, `we take`,
  `is set to zero`). Negated forms (`nothing is imposed`, …) are stripped before the `ADOPT` test so
  that a correctly rejected constraint is not punished for the words of its rejection.

Locations found in the current manuscript (printed by the suite as `INFO` lines):

| File | Occurrence | Verdict |
|---|---|---|
| `chapters/ch08.tex` | `\int_{\Ga_{\mathrm{out}}}p\,\mathrm ds=0` in “Constraining, say, … would over-determine the system” | rejected counterfactual (correct) |
| `chapters/audit_appendix.tex` | register row D-30, “D-25 removed … by constraining `\int … = 0` … over-determines …” | historical record of the removed error |

The register is treated separately and deliberately: it must *describe* the removed constraint, and
its row must carry `over-determin`/`removed`/`no such freedom`; the formulation itself is held to the
strict rule.

### 2.3 Mutations

* **G1** re-inserts a normalisation *inside the sentence that explains the over-determination*:
  “…inject a spurious outlet mass source; in practice the level is fixed by adding the normalisation
  `\int_{\Om_f}p\,\mathrm dx=0` to the system”. v4 exits 1 with
  `FAIL  a pressure normalisation occurs only as an explicitly rejected counterfactual`.
* **G2** places an equivalent reworded condition elsewhere: in `ch05`, beside “nothing is imposed to
  fix the level”, it adds “the discrete pressure is normalised to a zero mean, `\langle p\rangle=0`”.
  v4 exits 1 with the same assertion.

Both escape v3 (109/109); both are detected by v4. The Stage 16/17 mutant **A8** (a constraint added
in `\mathrm dY` notation at the end of the D-25 sentence) is now caught by this assertion as well,
not only by the register-pointer string.

---

## 3. Boundary-condition sets (§3 of the request)

`tab:bcs` in `chapters/ch05.tex` is **parsed**, not searched: 9 rows (B1–B9) are read with their
four fields. The Γ_if row is B5 (`\eqref{eq:ifkin}--\eqref{eq:ifflux}`, “conjugate interface”).

Rules asserted:

1. `no Gamma_if row prescribes a solid flux datum` — no `\nabla T_s\cdot` / `\partial_n T_s` in the
   Γ_if row.
2. `no Gamma_if row gives the solid a Dirichlet AND a Neumann temperature datum` — the specific
   double-datum failure, reported with the offending row text.
3. Prose: every solid datum is located **together with the surface it is imposed on**
   (`T_s=…$ on $\Ga_{\mathrm{if}}$`, `\nabla T_s\cdot\bn=q''$ on $\Ga_h^0$`, …). The adopted set is
   then asserted: exactly one solid Dirichlet datum on Γ_if (found: `ch08` step 1, `T_s=T_\Gamma^{(k)}`
   on `\Ga_{\mathrm{if}}`), **zero** solid flux data on Γ_if, and the solid's flux datum on the outer
   face `\Ga_h^0` (B6), not on the interface.

**Mutation G3** gives B5 both data (`$T_s=T_\Gamma^{(k)}$`, `$\partial_nT_s=q''/k_s$`, keeping the
original eqrefs). v4 exits 1 with
`FAIL  no Gamma_if row gives the solid a Dirichlet AND a Neumann temperature datum` — the intended
reason, not a fingerprint and not an unrelated failure. The same mutation passes v3 (109/109).

---

## 4. Independent numerical validation (§4 of the request)

No value below is a phrase search: each is recomputed from the printed formula and from the parsed
inputs (`q=5000 W/m²`, `d=3 mm`, `k_s=0.25`, `Nu_{H1}=5.385`, `k_f=0.60`, `H_0=0.5 mm`,
`ρ=1000 kg/m³`, `U=0.05 m/s`, `c_p=4180 J/kgK`, `L=30 mm`, `E=3.6 GPa`, `ν=0.4`, `α=5×10⁻⁵ 1/K`).

### 4.1 `θ̄` — the table cell itself (T1)

The cell (now `chapters/ch07.tex:34`) quotes its formula and three components. Each component is
recomputed:

| Component | Formula | Recomputed | Printed (new) | Deviation |
|---|---|---|---|---|
| `ΔT_t/2` | `q''d/(2k_s)` | 30.0000 K | 30.0 | < 0.005 |
| `q''/h` | `q''/(Nu_{H1}k_f/2H_0)`, `h=3231.0 W/m²K` | 1.5475 K | 1.55 | 0.0025 |
| `ΔT_b/2` | `q''L/(2ρUH_0c_p)` | 0.7177 K | 0.72 | 0.0023 |
| total | sum | **32.2652 K** | ≈ 32.3 | 0.035 |

Internal vs displayed precision is kept separate: the internal value is 32.2652 K; 32.3 is its
1-d.p. display, and 32.3 is the divisor used in the `M_b` row of the same table, so the two rows now
agree to the displayed precision as well.

**Correction found and made (display only, no physics, no value changed).** The cell previously read
`30+1.6+0.7\approx32`: `q''/h = 1.5475` rounded to one decimal is `1.5`, not `1.6`, and the total was
shown as `≈32` while the same table used `32.3`. It now reads `30.0+1.55+0.72\approx32.3` — every
component correct at the precision printed, and the total equal to the recomputed `θ̄` at that
precision. **No numerical result changed.**

**Retraction of an auditor suspicion.** An earlier internal note suggested that `q''/h` was not
consistent with the printed `θ̄`, computed with `D_h = 6 mm`. That was an auditor error: the hydraulic
diameter is `D_h = 2H_0 = 1 mm`, `h = Nu_{H1}k_f/D_h = 3231 W/m²K`, `q''/h = 1.548 K`, and the chain
is consistent. The suspicion is withdrawn here rather than carried into the ledger as a defect.

**Mutation T1**: `30.0+2.55+0.72\approx33.3` → exits 1 with
`FAIL  each component printed in the theta-bar cell is its recomputed value at 2 dp`. The same
mutation passes v3.

### 4.2 `T̄_cr` and the `M_b ≥ 2` dependency (T2)

`eq:tcr` is `\bar T_{\mathrm{cr}} = \pi^2 d^2/(12\,\alpha(1+\nu)L^2)`; the coefficient is parsed from
the display and the value recomputed:

* `T̄_cr = π²(3×10⁻³)²/[12(5×10⁻⁵)(1.4)(9×10⁻⁴)] = 117.495 K`; printed as `117` in the `ch07` cell
  (3 s.f.) and as `117.5` in A5 and in the `M_b` row (4 s.f.) — both correct roundings, checked
  separately.
* Denominator printed in A4 `12α(1+ν)L² = 7.56×10⁻⁷` — reproduced exactly.
* Thickness catalogue `d = {1,1.5,2,2.5,3} mm → T̄_cr = {13.06, 29.37, 52.22, 81.59, 117.50} K`
  against the printed `{13,29,52,82,117}` (max deviation 0.5 K, i.e. the printed rounding).
* `M_b = 117.495/32.2652 = 3.6415`; printed `3.64`; numerator, denominator and quotient are each
  checked against recomputation.
* The admissibility conclusion is derived, not read: **`M_b ≥ 2` is asserted on the computed ratio**
  (`3.6415 ≥ 2`), and its two consequences are recomputed: `θ̄ ≤ T̄_cr/2 = 58.75 K` (printed 58.8) and
  `q'' ≤ 9104 W/m²` (printed `9.1×10³`).

**Coverage defect found while implementing.** The printed `T̄_cr` value in the `ch07` table was not
read by any v3 assertion: mutating `117 → 130` passes v3 at 109/109. It is now caught
(`FAIL  ch07 table T_cr is the recomputed threshold`), and a mutation of the `M_b` quotient
(`130/32.3=4.02`) is caught by three assertions.

**Mutation T2** halves `T̄_cr` in the *displayed* `eq:tcr` (`12 → 24`) while leaving every printed
number untouched. Under v4 the recomputed `M_b = 1.82 < 2`, and the run exits 1 with
`FAIL  bound A-2 (M_b >= 2) is met by the recomputed margin`. The conclusion now depends on the
computed `T̄_cr`, not on a hard-coded constant.

### 4.3 `eq:wmax` against its governing expression and its printed result (F1's target)

`eq:wmax` (`chapters/ch04.tex:121–125`) states the parabola and its maximum with explicit constants.
The constants are parsed and three independent conditions are asserted:

1. **Internal algebra**: the parabola's mid-span value `κ_th L²/(4·2)` must equal the stated
   `w_max = κ_th L²/8`; `1/(4·2) = 1/8`.
2. **Governing relation**: the parabola must satisfy `w'' = −κ_th` with `w(0)=w(L)=0`
   (second-difference residual `1.5×10⁻⁷` against `κ_th = 1.4 m⁻¹`).
3. **Limit of the beam–column solution**: `eq:beamcolsol` at `μL = 10⁻⁴π` reproduces the stated
   `w_max` to `1.1×10⁻⁸` relative — so `eq:wmax` is the zero-force limit of the printed solution, not
   an independent assertion.
4. **Printed result**: `κ_th L²/8 = 1.575×10⁻⁴ m` against the printed `1.575×10⁻⁴ m` (A3) and
   `1.58×10⁻⁴ m` (`ch07`), both at their displayed precision.

**Mutation F1** corrupts the denominator (`8 → 16`) and then regenerates the fingerprint with
`--update-fingerprints`. See §6: the run exits 1 on four substantive assertions. **The corruption
cannot be laundered.**

---

## 5. Nomenclature and stale claims (§5 of the request)

### 5.1 `Γ_p` nomenclature entry (N1)

The entry itself (`chapters/appendix.tex:49`) is now parsed and asserted — previously only the
*dictionary* row and A8 were checked, so the nomenclature could say anything.

* Was: `$\Gamma_p$ & thermal-to-pressure deflection ratio & --` (no equation, no distinction between
  the two presentations, and “thermal-to-pressure” invites the reading that the ratio is a
  pressure-normalised thermal quantity).
* Now: `$\Gamma_p$ & deflection ratio $w_{\max}/w_p$, \eqref{eq:gammap}; mixed and like-for-like
  presentations & --`.

Three assertions: the entry defines `w_{\max}/w_p` and cites `\eqref{eq:gammap}`; it distinguishes
the mixed and like-for-like presentations; it is no longer a bare “thermal-to-pressure” description.
The **headline** choice between the two definitions remains an author decision (RU; unchanged) — the
entry records both, it does not choose.

**Mutation N1** reverts the entry to the bare description while leaving the dictionary intact →
exits 1 with `FAIL  the Gamma_p nomenclature entry defines the labelled ratio`.

### 5.2 Stale end-condition claims (S1, S2)

The scan covers **22 files** — all 16 `.tex` sources (`main.tex`, `chapters/*.tex`,
`figures/*.tex`) and `README.md`, `HFF_revision_summary.md`,
`HFF_source_pdf_consistency_report.md`, `HFF_final_packaging_report.md`,
`HFF_final_pre_coding_checklist.md`, `HFF_final_reference_status_notes.txt` — and the suite prints
the location list with the number of end-effect sentences found in each
(`main.tex 0`, `appendix 2`, `audit_appendix 13`, `ch01 0`, `ch02 6`, `ch03 0`, `ch04 12`, `ch05 2`,
`ch06 0`, `ch07 1`, `ch08 2`, `ch09 1`, `ch10 0`, `ch11 3`, `fig_geometry 2`, `fig_signs 0`,
`README 2`, `revision_summary 0`, `pdf_consistency 1`, `packaging 1`, `checklist 0`,
`reference_notes 0`).

Detection is **sentence-scoped** (not a ±N-character window): a sentence that mentions the end
effect/pin/clamp context and contains a magnitude of the form
`(about|approximately|roughly|some|around|nearly|close to|~|≈)? (one|two|three|few|couple|1|2|3)
(\.d)? (of)? (per cent | %)` is a hit **unless the same sentence explicitly supersedes it**
(`supersed`, `withdrawn`, `earlier`, `previously`, `no longer`, `replaced`, `obsolete`). The correct
magnitude `$0.2\%$` with its Q8 evidence is asserted to be present in `ch04` and `ch11`.

* **S1**: “gives, **to within about two per cent**, `1.0000` of `κ_th L²/8` …” → exits 1.
* **S2**: the same with “**a couple of per cent**” → exits 1 (a second wording, not a repeat).
* Additional probes (not retained as permanent cases): `the end effect is about 2 per cent …` → exits
  1; `end effect ~3 per cent` → exits 1.
* All four pass v3 (109/109).

---

## 6. Fingerprint safety (F1 of the request)

v3 wrote the fingerprint file and then `sys.exit(0)` **before any check ran**, so
`--update-fingerprints` always looked green. v4:

* writes the file, prints a four-line `WARNING` that a fingerprint is *change detection, never a
  correctness proof*, and **continues**; the fingerprint comparison is skipped **only** for that run
  and says so (`INFO  fingerprint comparison SKIPPED`); every substantive check still runs and the
  exit status is decided by them;
* keeps the docstring statement to the same effect (§B of the module header).

Two executed results:

1. **Regeneration is stable on the current tree**: running `--update-fingerprints` in a clean copy
   rewrites `equation_fingerprints.json` with 76 entries, **byte-identical** to the committed file
   (`identical: True`, no added/removed/changed keys). The `ch08` paragraph added in §8 therefore
   did not shift any unlabelled display-equation key (`eq:chapters/ch08.tex#N`): it contains inline
   math only, no new display environment.
2. **Corruption plus regeneration fails** (case F1): denominator `8 → 16` in `eq:wmax`, then
   `python3 audit_stage15/regression.py --update-fingerprints` → exit **1**, with four substantive
   failures (`the parabola's mid-span value equals the w_max of the same equation`,
   `the eq:wmax denominator reproduces the printed linear w_max (appendix A3)`,
   `… (ch07 table)`, `eq:wmax is the mu -> 0 limit of eq:beamcolsol`), stderr empty.

---

## 7. `ch08`: well-posedness is not convergence (§8 of the request)

Inserted after the well-posedness paragraph of `sec:iteration` (inline math only, no new display
environment), the new paragraph states:

* each of the four subproblems is uniquely solvable at every iterate, and **that says nothing about
  whether the alternation converges**; “no contraction argument or energy-stability proof of the
  staggered map is given or claimed here”;
* the thermal exchange is a Dirichlet-to-Neumann-to-Dirichlet loop whose error amplification depends
  on the relative interface admittances of the two sides and is **not controlled by the
  well-posedness constants**; convergence must be demonstrated numerically, not inferred;
* the loop is monitored by `ΔT_Γ^{(k)} = T_Γ^{(k)} − T_Γ^{(k−1)}` and its discrete maximum norm
  `‖ΔT_Γ^{(k)}‖ = max_{Γ_if} |T_Γ^{(k)} − T_Γ^{(k−1)}|` in kelvin, on the interface nodes of the
  current mesh, reported per run;
* the thermal loop is accepted only when `‖ΔT_Γ^{(k)}‖` falls below a tolerance fixed by the
  mesh-refinement and iteration study and reported per configuration — **“no numerical value of that
  tolerance is asserted here, because none has been demonstrated by a computation in this work”**;
* the interface flux-jump criterion (ii) of `sec:quality` is an a-posteriori test on the converged
  state and does not supply the missing proof; a stagnating `‖ΔT_Γ‖` joins a stagnating geometry
  increment as a trigger for escalation to the monolithic path.

No tolerance is invented and no convergence proof is asserted. **No computation of
`‖ΔT_Γ‖` was performed** — that requires the solver that does not exist yet (§13).

---

## 8. Mutation campaign (finding I-07 / §7 of the request)

`audit_stage15/mutation_campaign_stage18.py`, raw evidence in
`audit_stage15/stage18_mutation_results.txt`.

Method: clean baseline first; each case applied to a **fresh isolated copy** under `/tmp` (the
repository is never modified); the copy is discarded and re-cloned for the next case; each case
declares the **intended assertion**; a case is `detected` only if the suite exits non-zero, does not
crash, **and** the intended assertion is among the failures. The retained 34 cases are imported from
`mutation_campaign_stage17.M`, so they are byte-identical to the permanent Stage 17 record.

Result (all 44 cases executed, nothing skipped):

| Group | Cases | Substantive detection | Fingerprint-only |
|---|---|---|---|
| Retained Stage 16/17 (A1–A25, B1–B9) | 34 | 26 | 8 |
| New: G1, G2, G3, T1, T2, N1, S1, S2, F1 | 9 | 9 | 0 |
| Proof case for the removed `or True` (V1) | 1 | 1 | 0 |
| **Total** | **44** | **36** | **8** |

* Escapes: **0**. Invalid detections (syntax error, traceback, or a failure that is not the intended
  assertion): **0**. Anchor failures: **0**.
* The 8 fingerprint-only cases are A1, A2, A3, A10, A11, A18, A22, B7 — all of them edits of a
  display equation or a register row. They are reported separately because a fingerprint shows only
  that text changed: it is not evidence that a wrong expression would be noticed. **No claim of
  "100 % semantic detection" is made**; the honest statement is 36 substantive detections out of 44
  executed cases, with the 8 remainder caught only by change detection.
* Before/after evidence for the new layer, measured with the v3 script from `HEAD` on the same five
  mutations that v4 now catches: `θ̄` cell, `T̄_cr`, gauge-in-sentence, B5 double datum, reworded
  stale magnitude — **all five pass v3 at 109/109** and all five fail v4 for the intended reason.

---

## 9. Suite composition (v4, 144 assertions, all passing)

| Section | Assertions | What it does |
|---|---|---|
| 1 structural integrity | 8 | braces, environments, labels, refs, bib, macros, 32 register rows |
| 2 claims (sign, BCs, units, model, gauge) | 48 | presence/absence and sentence-level conditions, incl. the gauge test (§2) |
| 2b fingerprints | 3 | 76 fingerprints (44 display equations + 32 register rows) |
| 3 parsed inputs | 3 | the inputs every numeric check uses, parsed from the manuscript |
| 4 printed results vs recomputation | 64 | numbers parsed from the text, compared with code-recomputed values |
| 5 exact identities | 4 | ODE/BC satisfaction, `κ_geo = κ_th sec(μL/2)`, `cot²(μL/4)` |
| 5b interface data / nomenclature / stale scan | 12 | §3, §5 above |
| 6 package provenance | 2 | `main.pdf` present, every README filename exists |

By kind: **68 recomputation**, **3 fingerprint aggregates**, **13 structural/input/provenance**,
**14 condition-parsing** (BC table and surface clauses, gauge sentences, nomenclature fields, stale
scan), **46 presence/absence**. §7 (build freshness) is reported and **not** asserted: no TeX engine
exists here.

---

## 10. Files modified in this stage

| File | Change |
|---|---|
| `audit_stage15/regression.py` | v3 → v4: `or True` removed; gauge test replaced; `REQUIRED` file guard; `--update-fingerprints` no longer exits; new §4 numeric blocks (T1, T2, `eq:wmax`); new §5b (BC set, nomenclature, stale scan); fingerprints-are-not-proof wording |
| `audit_stage15/mutation_campaign_stage18.py` | **new**: 44 cases, declared intended assertions, fresh copies, raw evidence writer |
| `audit_stage15/stage18_mutation_results.txt` | **new**: raw per-case evidence (command, exit status, intended assertion, all failures, stderr) |
| `audit_stage15/14_stage18_repair_report.md` | **new**: this report |
| `audit_stage15/01_master_issue_ledger.md` | Stage 18 section appended (§11) |
| `audit_stage15/build_package.py` | `__pycache__`/`*.pyc` excluded from the archive (stray byte-code otherwise entered the ZIP) |
| `audit_stage15/package_manifest.txt` | regenerated with the ZIP |
| `HFF_Final_Overleaf_Package.zip` | rebuilt deterministically (§12) |
| `chapters/ch07.tex` | `θ̄` cell components at their displayed precision (display only; no value changed) |
| `chapters/ch08.tex` | new paragraph: well-posedness ≠ convergence, `‖ΔT_Γ‖` definition and use |
| `chapters/appendix.tex` | `Γ_p` nomenclature entry made precise and labelled (headline still open) |

`audit_stage15/equation_fingerprints.json` is **unchanged** (regeneration reproduces it byte for
byte). No physics, no input, no result and no tolerance was altered to make a test pass.

---

## 11. Ledger effects

Appended to `01_master_issue_ledger.md`: the Stage 18 entries (S18-1 … S18-8) with original claim,
why it was needed, old and new source, dependencies, recomputation, regression check and commit
hash. Statuses that must **not** be read as closed by this stage: `RU-01` (casing clearance, contact
interpretation, vented/sealed cavity), `RU-03` (`1.4377 H₀`), heater mounting and heated-face
interpretation, the contact law, the intended headline definition of `Γ_p`, **I-13** (PDF staleness /
no TeX engine) and **I-15** (no renderer, no visual check) — all remain **OPEN**. The coupled
production solver remains **NOT READY**.

---

## 12. Build, manifest and commit

* The ZIP is rebuilt by `python3 audit_stage15/build_package.py` from exactly the tracked sources,
  with fixed member order, fixed timestamps `(2026,10,19,0,0,0)` and deflate level 9. It was built
  twice in independent copies and the two archives are byte-identical (**executed**, output in §12.1
  below).
* `audit_stage15/package_manifest.txt` records the archive SHA-256, its size and member count, and
  the SHA-256 of every member. The archive's hash and the member count are quoted in the commit
  message; the manifest cannot contain itself, and this report is a member of the archive, so the
  hash is not repeated inside the tree.
* Independent verification: every member digest was recomputed from the ZIP and compared with the
  manifest, the member list was compared with the manifest order, and the archive hash was
  recomputed from the file — **all match** (executed, §12.2).

### 12.1 Executed build and verification

* `python3 audit_stage15/build_package.py` → an archive of **78 members**; its SHA-256 and size are
  lines 2–3 of `package_manifest.txt`.
* The stage added exactly three members (75 → 78): `mutation_campaign_stage18.py`,
  `stage18_mutation_results.txt`, `14_stage18_repair_report.md`. Stray `__pycache__` byte-code is
  excluded by the build script (it would otherwise have entered the archive).
* Built twice, in two independent copies of the tree, by two separate invocations: the two archives
  are **byte-identical** (same SHA-256, same size, same member order).
* Independent verification of the shipped archive: **78/78** member digests recomputed from the ZIP
  match the manifest; the member list matches the manifest order; `testzip()` reports no CRC error;
  every member timestamp is `2026-10-19 00:00:00`; the archive SHA-256 recomputed from the file
  matches line 2 of the manifest.

---

## 13. Explicitly NOT executed

* **No LaTeX build.** No TeX engine, no BibTeX, no `pdftotext`, no rasteriser exists in this
  environment. `main.pdf` still predates the modified sources; **I-13 stays OPEN** and the new
  `ch08` paragraph and `appendix` row have **not** been seen typeset (page-breaking, overfull boxes
  and the `longtable` column widths are unverified).
* **No figure rendering.** **I-15 stays OPEN**; the figure claim is only that no positive
  “visually verified” statement exists and that the ledger says OPEN.
* **No solver runs, no mesh study, no iteration history.** The `‖ΔT_Γ‖` tolerance is deliberately
  left unset; nothing in this stage demonstrates convergence of the staggered iteration.
* **No resolution of the open physics**: RU-01, RU-03, heater mounting, contact law, `Γ_p` headline.

---

## 14. What an independent auditor should check

1. That the parent commit the stage started from is `211f751`, suite v3 (109 assertions), and that
   the audit report `independent_audit_stage18/HFF_Stage18_Independent_Acceptance_Audit.md`
   (`a61837e`) is unchanged.
2. `python3 audit_stage15/regression.py` → 144/144 in a clean clone of the stage commit.
3. `python3 audit_stage15/mutation_campaign_stage18.py` → 44/44 executed, 36 substantive, 8
   fingerprint-only, 0 escapes, and that the per-case evidence in
   `stage18_mutation_results.txt` names the intended assertion each time.
4. That the five v3 escapes of §8 are now caught, and that each new test fails for its own subject
   (not for a fingerprint, not for a syntax error).
5. That no numeric value, input or tolerance of the manuscript changed in this stage — only the
   `θ̄` display components, the `Γ_p` nomenclature text and the new `ch08` paragraph.
6. That the ZIP in the commit matches `package_manifest.txt` and rebuilds byte-identically.

**This stage is not self-approved.** It is submitted for a fresh independent acceptance audit of the
exact commit named in §12/§15; the coupled production solver stays **NOT READY** until that audit
(and the physical items of §11) are resolved.

---

## 15. Commit

The commit hash, the ZIP SHA-256, its size and its member count are recorded in the commit message
of this stage and in `audit_stage15/package_manifest.txt` (lines 2–4). Because this report is a
member of the archive, quoting the archive hash inside it would change the archive; the manifest and
the commit message are the authoritative record.
