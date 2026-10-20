# HFF Stage 17 — Independent Mathematical, Numerical and Mutation Audit

**Auditor role:** independent auditor, not the implementation agent. No manuscript, figure, test,
package or commit content was modified during this audit.
**Audit date:** 2026-10-20 (UTC), user time zone Asia/Kolkata.
**Evidence:** every number in this report was produced by a script committed under
`independent_audit_stage17/evidence/` and executed during this audit; no result is inferred from
prior reports or from the audited campaign's own logs.

---

## 0. Verdict summary

| Gate | Question | Verdict |
|---|---|---|
| **A** | Is the Stage 17 thermal partition (solid Dirichlet + fluid Neumann + inflow datum) mathematically correct and well posed? | **PASS** — the argument is sound, the sign/normal/unit chain closes, the level is determined, and the propagation into `θ̄ → N_θ →` geometric stiffness is correct. |
| **B** | Do the printed numbers follow from the printed inputs? | **PASS** — every value in the chain was independently recomputed and lands on its printed rounding, including `θ̄ = 32.2652 (prints 32.3)`, `N_θ = −2.9039×10⁴`, `w_max = 2.1886×10⁻⁴`, `σ = 4.2369/13.9165 MPa`, mixed `Γ_p = 2382`, like-for-like `1726`, and the self-consistent fixed point `2.13988×10⁻⁴ m`. |
| **C** | Is the *verification claim* (109 checks, 34/34 mutants) trustworthy as evidence of correctness? | **FAIL** — 7 semantic defects escape the suite (proved below), 1 check is provably vacuous, the `θ̄` formula cell and `T̄_cr` are unverified, and 9 of the 34 "detections" are fingerprint-only. `34/34` is not evidence of semantic coverage. |
| **Solver** | Is the coupled production solver ready? | **NO.** Well posed but not shown to converge; no coupled run exists; the PDF cannot be rebuilt or read in this environment; RU-01/RU-03, heater face, contact law and the headline `Γ_p` remain author decisions. |

**Direct answers (detail in §9):**

1. **Is Stage 17 accepted?** *The repair is accepted as mathematically correct and numerically
   consistent* (Gates A and B). *The claim that the repair is verified is not accepted* (Gate C).
   Overall: **conditional acceptance of the repair, rejection of "audit-complete".**
2. **Does it need another repair stage?** **Yes — one bounded, suite-only stage** (no physics
   rewrite): seven named mutants must be made to fail (§9, C1–C7). One additional sentence in
   `ch08` is needed for convergence honesty.
3. **Is the coupled production solver ready?** **No.**

---

## 1. Freeze and scope

### 1.1 Frozen target

| Item | Value |
|---|---|
| Branch | `arena/c875f9b3-hff-final-overleaf-package-fix` |
| Audited commit | `211f75163485a2b209b79fb3e22ecb0d7227d342` (`211f751`, "Stage 17: repair Stage 16 audit findings …") |
| `origin/main` | `5a255212a51374f7eb178647eb12b0a9c2b67ded` (untouched) |
| Working tree | clean (`git status --porcelain` shows only the new untracked `independent_audit_stage17/`) |
| Interpreter | Python 3.11.2 |
| TeX toolchain | **absent** — `pdflatex`, `latex`, `lualatex`, `xelatex`, `latexmk`, `tectonic`, `pdftoppm`, `pdftotext`, `gs`, `qpdf` all `MISSING`; `convert` present but ImageMagick's PDF coder is disabled by policy; no `pypdf`/`fitz`/`pdfminer` |

Evidence: `evidence/freeze_and_toolchain.txt`.

### 1.2 What was read (source-level, not summaries)

`chapters/ch02.tex` (assumptions, `tab:geometry`, A9), `ch03.tex` (fluid buoyancy),
`ch04.tex` (constitutive reduction, `eq:beamcolsol`, `eq:nupdate`, `eq:gammap`, support idealisation),
`ch05.tex` (interface conditions `eq:ifkin`–`eq:ifflux`, `tab:bcs`, data-model paragraph, pressure
gauge paragraph), `ch06.tex` (A-1…A-6, "Dependence on yet-unfrozen data"), `ch07.tex` (arithmetic
table, `Γ_p`, supports), `ch08.tex` (`sec:iteration`, steps 1–6, "Why the solid receives the
temperature and not the flux", assembled-cancellation paragraph, escalation trigger, quality
controls), `ch09.tex` (V-C3, Nu values), `ch10.tex`, `ch11.tex`, `appendix.tex` (A1–A9, nomenclature,
tables), `audit_appendix.tex` (D-16, D-20, D-22, D-26, D-28, D-29, D-31, D-32),
`audit_stage15/regression.py` (all 456 lines), `audit_stage15/equation_fingerprints.json` (76
entries: 44 equation entries of which 12 are positional, plus 32 register rows),
`audit_stage15/mutation_campaign_stage17.py`, `audit_stage15/{12_stage17_repair_report.md,
13_stage17_audit_request.md}`, `audit_stage15/package_manifest.txt`, `audit_stage15/build_package.py`,
`independent_audit_stage16/evidence/q8_pin_verification.py`.

### 1.3 Independence statement

- No file in the repository outside `independent_audit_stage17/` was created or edited; all mutation
  work ran in isolated copies under `/tmp/audit17/{nv,am,m2,m3,m4,rebuild}`.
- All prior reports (Stage 15/16/17, including the Claude independent audit) were treated as claims.
  Every number quoted as "printed" below was read from the source in this audit.
- Two of my own preliminary suspicions were **disproved by my own tests** and are retracted in
  Appendix B. They are not carried into the findings.
- No push was made to any branch other than the session branch (see §10 note).

---

## 2. Re-derivation of the thermal boundary-value problem

Notation: `n` is the fluid's outward normal (single-normal convention, `ch05:5–12`); the solid's
outward normal is `n_out = −n` on `Γ_if`.

### (a) Was the Stage 16 pure-Neumann solid doubly inadmissible?

**Yes, and the manuscript's reason is correct.** With flux data on *all* of the solid boundary
(`q''` on `Γ_h⁰`, zero on `Γ_end` and the remaining faces, conjugate flux on `Γ_if`), the operator
is pure-Neumann: the constant is in its kernel (`ker = span{1}`) so the level is free, and the data
are compatible only if the boundary fluxes sum to zero. At an intermediate iterate the conjugate
flux extracted from the fluid does not balance `q''L`, so the iterate is not merely non-unique, it
has **no solution**. `ch08:205–214` states both halves ("doubly inadmissible"), and `ch05:77–84`
states them independently. I re-derived both statements from the divergence theorem; they are
correct, including the discrete case (a pure-Neumann stiffness matrix is singular with the constant
mode).

### (b) Is Stage 17's solid subproblem genuinely well posed?

**Yes.** `ch08:174–180`: `T_s = T_Γ^(k)` on `Γ_if` (Dirichlet), `+k_s∇T_s·n_out = q''` on `Γ_h⁰`
(Neumann), zero flux on `Γ_end` and the remaining faces. The Dirichlet part is non-empty and has
positive measure, so the bilinear form is coercive on the constrained space: **unique solution for
every data set, no compatibility condition on the fluxes**. The interface flux is then an *output*,
`q_Γ^(k) = +k_s∇T_s^(k)·n`. This is a mixed Dirichlet–Neumann problem on disjoint boundary parts,
not an over-determined one.

Energy consequence, which the manuscript states more weakly than it holds: because every boundary
of the solid is adiabatic except `Γ_h⁰` and `Γ_if`, the extracted interface flux satisfies
`∮_{Γ_if} q_Γ ds = q''L` **exactly at every iterate** (up to the solid's own discretisation). The
global enthalpy balance is therefore not a fixed-point property. What is only asymptotic is the
*pointwise* conjugate consistency (temperature continuity and local flux equality), which is what
`ch08:224–229` says ("the discrete flux balance is recovered only in the limit"). Read carefully,
the text is right; a reader could conflate the two, and I recommend one extra clause.

### (c) Does the fluid Neumann + `T_in` uniquely determine `T_f`?

**Yes, under the stated outflow condition.** `ch08:181–187` imposes `k_f∇T_f·n = q_Γ^(k)` on
`Γ_if`; `ch05:46` (B1) imposes `T_f = T_in` on the inflow plane; `ch05:47` (B2) imposes the
do-nothing natural outflow and `∂_nT_f = 0`; B3/B4 are adiabatic. With inflow Dirichlet data and a
natural outflow condition the discrete energy equation is non-singular for *any* interface flux:
there is no flux-compatibility constraint to satisfy. The interface temperature
`T_Γ^(k+1) = T_f^(k)|_{Γ_if}` is an output and closes the loop.
Caveat, already documented by the paper (B2 remark, register C-9): this requires no backflow; the
exit-length/backflow sensitivity is listed as required evidence and has **not** been produced.

### (d) Signs, normals, units and heat balance

The chain closes. With `q_vec = −k∇T`:

| Quantity | Definition in source | Value/units | Consistency check |
|---|---|---|---|
| Heater (B6, `ch05:51`) | `+k_s∇T_s·n_out = q''`, `q''>0` supplied | W/m² | `k∇T·n_out = +q''` ⇒ outward conductive flux `−q''`; correct for heat *in* |
| Solid interface flux (`ch08:177–178`) | `q_Γ = +k_s∇T_s·n`, `n` fluid-outward | W/m² | `= −k_s∇T_s·n_out` = heat leaving the solid into the fluid |
| Fluid interface (`ch08:184–185`) | `k_f∇T_f·n = q_Γ` | W/m² | heat entering the fluid `= −q_vec,f·n = +k_f∇T_f·n` ✔ |
| Model form (`ch05:12`, `eq:ifflux`) | `−k_f∇T_f·n = −k_s∇T_s·n` | W/m² | identical to the two lines above ✔ |
| Through-wall drop (`ch07:28`) | `ΔT_t = q''d/k_s = 60 K` | K | 5000·0.003/0.25 = 60.000 ✔ |
| Bulk rise (`ch07:48`) | `ΔT_b = q''L/(ρUH_0c_p) = 1.44 K` | K | 1.4354 ✔ |

Units are coherent throughout (`N_θ` N/m, `D_s` N·m, `κ` 1/m, `w` m, `σ` Pa). **No sign, normal or
unit error was found in the Stage 17 thermal partition.**

### (e) Are the iteration's fixed-point/convergence assumptions justified?

**No — and this is the one genuine mathematical gap in the repair.** A well-posed subproblem is not
a convergent iteration. Specifically:

1. **No contraction argument.** The iteration is a composition of a Dirichlet-to-Neumann map
   (solid) and a Neumann-to-Dirichlet map (fluid) on `Γ_if`. Its convergence depends on the
   spectral radius of that composition, i.e. on the solid/fluid thermal coupling stiffness. Nothing
   in `ch08:166–239` estimates it, and the Dirichlet–Neumann (heat-flux) coupling is precisely the
   arrangement that is known to be *weakly* convergent or divergent for strong coupling. The text
   does not claim a proof — `ch08` never uses the words contraction/Banach — so this is an **absent
   justification, not a false claim**.
2. **Relaxation is applied to only half the loop.** `ch08:197–198` under-relaxes the interface
   *displacement* with a factor `ω` "tuned once and reported per run". The *thermal* loop
   (`q_Γ → T_Γ`) carries no relaxation, although it is the loop whose convergence is unproved.
3. **The stopping rule is mechanical.** `ch08:199–203` stops on
   `‖d^(k+1) − d^(k)‖_∞ ≤ 10⁻⁶ w_max` plus subproblem residuals. The displacement can be converged
   while `T_Γ` still drifts, because `d` depends on `T_s` through a contractive thermoelastic
   operator; there is no `‖ΔT_Γ‖` criterion in the stopping rule.
4. **The escalation trigger is mechanical only.** `ch08:231–236` escalates on
   `N_θ^c/N_cr > 0.5` or on stagnation of the geometry increment. A thermal-loop divergence at
   moderate `N_θ^c/N_cr` would not trigger it.

None of these is a defect *in the model*; all four are gaps in the *solver specification* and must
be closed before the solver-readiness claim can be made.

### (f) Does the level follow from the model without an arbitrary datum?

**Yes, in the model.** The fluid's inflow datum `T_in` (B1) fixes the level; `T_ref` is a bookkeeping
shift that cancels from every equation (`ch02:200` `θ = T_s − T_ref`, `ch03:32` `θ_f = T_f − T_ref`,
`ch04:140–141` `N_θ ∝ θ̄`, buoyancy in `θ_f`). The interface condition `eq:iftemp` is the matching
condition, so both fields share the same shift and `θ̄` is invariant: adding `δT` to both `T_s` and
`T_f` leaves `θ̄`, `N_θ`, `κ_geo` and `w_max` unchanged. Therefore `ch08:216–223` ("nothing is added
to the model, and no reference temperature is invented") is **correct**.

What remains open is data, not mathematics: `ch02:47` still lists `T_in, T_ref` as "to be fixed at
data freeze", and `ch06:111–115` states explicitly that both enter only through property values.
No printed number in this paper depends on them. I therefore record this as **OPEN-DATA
(documented, register C-6, non-blocking)**, not as a defect. My earlier working note that the
unfrozen `T_ref` was an unresolved leading finding is downgraded accordingly.

### (g) Does the level propagate correctly into `θ̄ → N_θ →` geometric stiffness?

**Yes.** `θ̄` enters only through the product `N_θ = E d α θ̄/(1−ν)` (`ch04:140–141`, `eq:ntheta`), which
sets `μ² = N_θ^c/D_s` and hence both the beam–column amplification and the geometric-stiffness term
of `eq:weaks`. I verified the whole chain from parsed inputs (§6), including that a *uniform* shift
of the level cancels (f) while a *differential* shift would move `N_θ` one-for-one — which is
exactly why the Dirichlet-to-Neumann assignment of (b) matters: it makes the level an output of the
conjugate problem rather than a datum of the solid subproblem.

**§2 verdict:** the Stage 17 repair is correct (a, b, c, d, f, g). The convergence/stopping-rule
issues in (e) are open and are the only barrier to the solver verdict.

---

## 3. The 109 checks: what they actually assert

### 3.1 Executed counts (this audit, target `211f751`)

```
python3 audit_stage15/regression.py
→ PASS 109, FAIL 0, exit 0, "ALL 109 CHECKS PASSED"   (0.97 s)
```

The 109 executed assertions are 75 top-level `check(...)` sites plus 34 `cmp(...)` invocations
(the `check` calls inside `cmp` are counted once per call; two static `check` sites at
`regression.py:328,330` are the body of `cmp`). Classification of what each assertion *does*
(`evidence/check_classification.py`, `check_group_counts.txt`):

| Class | Count | Notes |
|---|---|---|
| Numeric recompute / identity | **42** | 34 `cmp` + 8 `check`: parse inputs from `ch02`/`ch09`, recompute, compare with the printed value |
| Prose-value consistency | 4 | membership/threshold tests on numbers quoted in prose (`circular-arc band`, `σ_fr > σ_sc`, `0.2σ_y`, `ch07` stress set) |
| Structural | 8 | braces, environments, label uniqueness, refs, citations, macros, register-row count |
| Fingerprint (aggregate) | 3 | 44 equation entries + 32 register rows in `equation_fingerprints.json` |
| Provenance / package | 2 | `main.pdf` exists; README filenames exist |
| **Claim string / presence only** | **50** | substring presence or absence; no recomputation |

So **50 of 109 assertions (46 %) test wording, not content**, and one of them is provably
vacuous.

### 3.2 Non-vacuity tests (do the checks bite when the target is missing/corrupted?)

Run in isolated copies (`/tmp/audit17/nv`):

| Probe | Result |
|---|---|
| Delete `chapters/ch08.tex` | `KeyError: 'chapters/ch08.tex'`, exit 1 — fails, but **by crash**, not by a named FAIL. Acceptable for CI, poor as a diagnostic. |
| Empty `chapters/appendix.tex` | 88 PASS / 21 FAIL, exit 1 — the appendix-dependent numeric checks fail with `printed=None`, i.e. they cannot pass on a missing target ✔ |
| Missing package ZIP | 1 FAIL (`every package filename in README.md exists`) ✔ |
| `θ̄ 32.3 → 32.4` in the appendix | FAIL (`printed theta-bar equals the recomputed value …`) ✔ |
| `θ̄ 32.3 → 32.31` | would pass (|Δ| = 0.045 < 0.05). The tolerance is exactly half a unit in the printed last digit (1 dp), so this is **correct rounding behaviour, not a defect** |
| `−2.91×10⁴ → −2.71×10⁴` | FAIL ✔ (positive control C2) |
| `eq:ifflux` sign flip | FAIL ✔ (positive control C3) |

### 3.3 The `32.27` vs `32.3` question

- The check is `abs(thbar − printed) ≤ 0.05` where `thbar` is recomputed from parsed inputs
  (`regression.py:334`). The printed value is `32.3` (`appendix.tex:80`), the recomputed value is
  `32.2652`. `|32.2652 − 32.3| = 0.0348 ≤ 0.05`: **PASS, and the tolerance is the correct
  half-ULP for a one-decimal print.**
- Internal precision and printed rounding are cleanly separated: the 4-decimal value exists only
  in the code (`thbar = 32.2652`), the manuscript prints `32.3` everywhere it quotes `θ̄`
  (`appendix:80`, `ch07:38–39`, `appendix:82`).
- The expected value is *independently sourced* in the sense that it is recomputed from the parsed
  inputs rather than copied — **but** the formula itself is duplicated in Python. This is the
  weakness proved in §3.4.
- One genuine (low-severity) rounding slip remains in the **component** line of `ch07:34`:
  `30 + 1.6 + 0.7 ≈ 32`. With `h = Nu_{H1}k_f/D_h = 5.385(0.6)/10⁻³ = 3231`,
  `q''/h = 1.5475 K`, which is `1.5` at one decimal — not `1.6`. The paper's own table row
  (`ch07:49`) prints `1.55 K`. The sum `30 + 1.55 + 0.72 = 32.27 → 32.3` is right; only the
  middle component is rounded up by 0.05 K.

### 3.4 What the suite does **not** check (proved by mutation, §4)

1. **The `θ̄` formula itself.** `ch07:34` is a `longtable` cell, not a display equation, so it is
   not fingerprinted and no check scans it. Corrupting **both** coefficients
   (`ΔT_t/2 → ΔT_t/3`, `q''/h → q''/(2h)`) leaves the printed total `≈32` untouched and the suite at
   **109/109 PASS** (mutant **T1**).
2. **The critical temperature.** `T̄_cr = 117.5 K` (`ch07:38`, `appendix:77`) is recomputed by
   nothing: the `M_b` check compares the printed quotient `3.64` against the *hard-coded*
   `117.5/thbar`. Changing `117 K → 130 K` in `ch07` gives **109/109 PASS** (mutant **T2**), even
   though `M_b ≥ 2` is an admissibility bound derived from it.
3. **The gauge constraint.** The check at `regression.py:135` excludes occurrences found within
   ±260 characters of "over-determine"/"Constraining". Inserting a real constraint
   `∫_{Γ_out} p dY = 0` immediately next to its own explanation ("which removes the gauge freedom")
   is absorbed by that window: **109/109 PASS** (mutant **G1**). A gauge constraint invented in
   `ch05` is invisible because the check scans only `ch08` (mutant **G2**). I also tested the
   regex for over-escaping and **disproved** a suspected vacuity (Appendix B).
4. **The boundary-condition set.** No check enumerates the conditions on any boundary. Adding a
   Neumann flux to `Γ_if` *as well as* the Dirichlet temperature in step 1 — making the solid
   subproblem over-determined, the exact class of defect Stage 17 repaired — is **109/109 PASS**
   (mutant **G3**).
5. **The nomenclature definition.** `check("dictionary labels Gamma_p", 'mixed; like-for-like' in APP)`
   is anchored at `appendix.tex:136` (a table row), not at the dictionary entry `appendix.tex:49`.
   Removing the label from the dictionary entry is **109/109 PASS** (mutant **N1**).
6. **Claim classes vs claim wording.** `NEW-05` is guarded against the phrase "a few per cent"; a
   re-worded stale claim ("stiffens the ends by about two per cent") passes (**S1**).
7. **One assertion asserts nothing.** `regression.py:174`:
   `check("figure fix is not claimed as visually verified", ('I-15' in read(...)) or True)` — the
   `or True` makes this a **constant PASS**. This is the only *provably* vacuous check in the suite.

### 3.5 Is a fingerprint match proof of correctness?

**No, and the suite's own workflow demonstrates it.** Mutating `eq:wmax` from `κ_thL²/8` to
`κ_thL²/12` is caught (`no display equation has changed`). Running the documented
`python3 audit_stage15/regression.py --update-fingerprints` and re-running gives **109/109 PASS**
while the display equation now contradicts the printed `1.58×10⁻⁴ m = κ_thL²/8`. Fingerprints
detect *edits to a frozen text*, not *correctness*; 9 of the 34 campaign detections are of this
kind and 4 of them (A1–A4) leave a manuscript whose display algebra contradicts its own printed
numbers, undetected by any numeric check.

**§3 verdict:** Gate C fails. The numeric layer is real and non-vacuous (42 genuine recomputations),
but the semantic layer (well-posedness, BC sets, formula cells, parameter values quoted in prose) is
thin and, in three places, provably absent.

---

## 4. Mutation campaign

### 4.1 The official campaign, re-executed by me

```
python3 audit_stage15/mutation_campaign_stage17.py
→ DETECTED 34 / 34, SURVIVING 0
  (caught by a numeric/identity check: 25; caught only by the equation fingerprint: 9)
```
(35 s; log in `evidence/mutation_campaign_rerun.txt`.) Baseline passes first; the script aborts if
the baseline fails; every mutant asserts `count(anchor) == 1` before editing; runs are in isolated
copies. **The execution claim is reproduced. Its interpretation is not.**

Re-classifying the *biting* check of each of the 25 "non-fingerprint" kills
(`evidence/check_classification.txt`, join at the end):

| Class of the check that actually fired | Mutants | Count |
|---|---|---|
| Numeric recompute | A5, A6, A7, A12, A13, A14, A20, A24, A25, B6 | **10** |
| Claim string / presence | A8, A9, A16, A17, A21, A23, B1, B2, B3, B5, B8, B9 | **12** |
| Regex/pattern guards | A15, A19, B4 | **3** |
| Fingerprint only | A1, A2, A3, A4, A10, A11, A18, A22, B7 | **9** |

The campaign's summary line therefore **mis-describes its own result**: "caught by a numeric/identity
check: 25" should read "caught by a non-fingerprint check: 25, of which 10 numeric, 12 claim-string
and 3 pattern guards". This is a reporting defect, not a detection defect (finding AU17-09).

### 4.2 Do the re-anchored A8/A15/A17 still attack the original defects?

| Mutant | What it edits now | Biting check | Judgement |
|---|---|---|---|
| **A8** | Replaces the D-25 sentence, *deleting* the words "corrected in D-30", and inserts `∫_{Γ_out}p dY = 0` | `register pointer corrected to D-30` (string) | **No.** The gauge constraint itself is not caught — the ±260 "explained" window absorbs it (§3.4.3). The kill is triggered by the lost pointer. My **G1** keeps the pointer and passes 109/109. |
| **A15** | Replaces `$0.2\%$` with "a few per cent" in `ch04` | `ch04 has no stale few-per-cent stiffening claim` (phrase scan) | **Partly.** It attacks the original sentence, but only lexically: inserting a *new* stale claim in different words passes (**S1**). |
| **A17** | Rewrites the loop-closure sentence so the loop closes on an assumed wall temperature | `the loop closes on the extracted interface temperature` (string) | **Partly.** It removes the literal phrase; it does not test the closure *semantics*. An over-determined or mis-ordered BC set passes (**G3**). |

### 4.3 My independent campaign

Two layers. First, the surviving-defect battery that must fail and does not
(`evidence/auditor_mutants.py`, re-runnable, 13.3 s, baseline 109/109 first, 0 anchor skips):

| ID | Injected defect | Suite | Why it matters |
|---|---|---|---|
| **G1** | gauge constraint re-inserted beside its own explanation, pointer kept | **109/109 PASS** | the exact A8/D-30 defect class survives when the wording is honest |
| **G2** | gauge constraint invented in `ch05` (contradicts B2/ch08) | **109/109 PASS** | the gauge check scans `ch08` only |
| **G3** | step 1 gives `Γ_if` **both** Dirichlet temperature and Neumann flux | **109/109 PASS** | over-determined solid subproblem — the defect Stage 17 repaired |
| **T1** | `θ̄` formula cell: `ΔT_t/3 + q''/(2h) + ΔT_b/2` | **109/109 PASS** | the defining formula of `θ̄` is unprotected |
| **T2** | `T̄_cr`: `117 K → 130 K` | **109/109 PASS** | the `M_b ≥ 2` bound rests on an unchecked number |
| **N1** | nomenclature entry `Γ_p` left unlabelled | **109/109 PASS** | I-11 residue; the "dictionary" check anchors at a table row |
| **S1** | new stale end-stiffening claim "about two per cent" | **109/109 PASS** | NEW-05 closed by phrase, not by claim |
| C1 | `θ̄ 32.3 → 32.4` | detected (`theta-bar` check) | positive control |
| C2 | `N_θ −2.91×10⁴ → −2.71×10⁴` | detected (`appendix N_theta matches`) | positive control |
| C3 | `eq:ifflux` sign flipped | detected (fingerprint) | positive control |
| **F1** | `eq:wmax` `1/8 → 1/12`, then `--update-fingerprints` | **109/109 PASS after regeneration** | fingerprint ≠ correctness |

Second, earlier in this audit I also ran 17 hand-built mutants against *semantic* prose targets
(not reproduced in the script above because their anchors were one-off): 10 detected, **7 escaped**
— X7 (delete the free-constant passage), X8 (adiabatic strip ends → heater flux), X12 (`q_Γ` sign
flip in prose), X14 ("leaving" → "entering" in the heat-balance sentence), Y1 (gauge sentence
re-inserted = exact A8 revert), Y2 (gauge invented in `ch05`), Y3 (interface over-determined).
Their reproduction is subsumed by G1–G3 for the three most important classes; the remainder are
listed here as **reported-not-preserved** because I did not archive those scripts.

### 4.4 Unrepresented defects

- No mutant targets `T̄_cr` in the official campaign → **T2** is an unrepresented defect class.
- No mutant targets the `θ̄` formula cell → **T1**.
- No mutant adds a *second* thermal condition to `Γ_if` → **G3**.
- No mutant adds a gauge constraint *without* disturbing a pointer → **G1**.
- No mutant re-words a stale claim → **S1**.
- No mutant removes the dictionary label while leaving the table label → **N1**.

**§4 verdict:** the campaign executes as advertised and detects 34/34 of *its own* mutants, but 9 of
those are edit-detectors, 12 more are phrase detectors, and seven semantic defects of the same
classes the Stage 17 repair addressed survive at 109/109.

---

## 5. NEW-05: the 0.2 % end effect and stale-claim sweep

### 5.1 Repo-wide stale-claim sweep (body text)

| Pattern | Hits | Assessment |
|---|---|---|
| "few per cent" | `ch02:77` (property variation, A2 — legitimate); `ch04:168` and `ch11:29` (both explicitly "earlier … superseded") | **no stale claim** ✔ |
| "one-time numerical check" | none | ✔ |
| "closing the residual" / "end-compliance" | `ch04:169` ("no separate end-compliance correction is applied") and `ch08:145` (weak-form cancellation) — both negative/technical | ✔ |
| "clamp" | 12 hits, all negative or historical (B7/A9 "pin, not a clamp", D-26, rejected eigenvalues) | ✔ |

Evidence: `evidence/greps_new05_ru.txt`.

### 5.2 The 0.2 % claim against the Q8 evidence

Re-executed `independent_audit_stage16/evidence/q8_pin_verification.py` (log:
`evidence/q8_rerun.txt`):

```
shape-derivative check (max abs vs FD): 4.48e-11        mesh 24 elements 101 nodes
case    w (mid-surface)   ratio     w (top face)   ratio
POINT      6.57891e-05    1.0025      6.56250e-05   1.0000
PIN        6.56617e-05    1.0006      6.54976e-05   0.9981
CLAMP     -2.67744e-06   -0.0408     -2.95531e-06  -0.0450
exact-field residual: 1.393e-09
```

- The printed numbers `1.0000`, `0.998`, `−0.02…−0.06` are reproduced **exactly** from the
  top-face extraction.
- The 0.2 % is arithmetically right and **extraction-independent**:
  `(1.0000 − 0.9981)/1.0000 = 0.19 %`; `(1.0025 − 1.0006)/1.0025 = 0.19 %`. Rounds to 0.2 % ✔.
- **Scope, stated honestly:** this is a **single finite-mesh check** — 24 Q8 elements, 101 nodes,
  one mesh, a patch test validated to `4.5×10⁻¹¹` against finite differences. It is **not** a
  converged strip solution: there is no refinement study, no grid-convergence index, and the
  mid-surface ratio `1.0025` differs from the analytic `1.0000` by 0.25 %, i.e. by slightly
  *more* than the 0.2 % effect being claimed. The quoted `1.0000` is the top-face extraction, which
  happens to coincide with the analytic value.
- `ch04:169`'s "**the check is complete**" therefore overstates the evidence; the defensible
  statement is "a single-mesh plane-strain Q8 patch test gives 0.19 % between the two end
  idealisations, robust to the extraction line". Finding AU17-08 (LOW).
- Evidence-quality flag: the script prints `FREE case: solved (unexpected: rigid modes not
  removed)` — the unconstrained case should not have solved. The reported POINT/PIN/CLAMP cases are
  all constrained so their ratios are unaffected, but the script lacks the assertion that would
  have caught this. Finding AU17-16 (INFO).

### 5.3 Is NEW-05 closed?

- The *specific* stale sentence is gone, and its replacement carries the measured value with the
  register pointer ✔.
- The *claim class* is not guarded: a re-worded stale claim passes (**S1**), because the guard is
  `a few per[\s\n]*cent` with a ±200-character "superseded"/"earlier" exemption.
- **PARTIALLY CLOSED** (as a manuscript matter it is closed; as a verification matter it is not).

---

## 6. `Γ_p` at all sites, and the full numeric trace

### 6.1 All presentations of `Γ_p`

| Site | Presentation | Labelled? | Value |
|---|---|---|---|
| `appendix.tex:49` | nomenclature: "thermal-to-pressure deflection ratio" | **NO** — neither mixed nor like-for-like | — |
| `appendix.tex:94` | A8 prose, `emph{mixed}` | yes | `2.4×10³` (recomputed 2382.1) |
| `appendix.tex:96` | A8 prose, like-for-like with `w_p(N_θ^c)` | yes | `1.73×10³` (recomputed 1726.3) |
| `appendix.tex:136` | arithmetic table: "(mixed; like-for-like 1.73×10³, D-29)" | yes | `2.4×10³` |
| `ch04.tex:307` | `eq:gammap`, amplified form | yes (mixed, `ch04:318–321`) | `2.4×10³` (recomputed 2382.1) |
| `ch06.tex:83` | ordering parameter, `Γ_p = w_max/w_p, eq:gammap` | **not at that sentence**; clarified by A-5 at `ch06:101–104` | — |
| `ch07.tex:41` | design table "(mixed)" | yes | `2.4×10³` |
| `ch07.tex:87` | prose "the mixed ratio is `Γ_p ≈ 2.4×10³`" | yes | 2382.1 |
| `ch10.tex:44` | mechanism-parameter mention | n/a | — |
| `audit_appendix` D-5, D-16, D-22, D-29 | register | yes | — |

**I-11 status: PARTIALLY CLOSED.** All *numerical* presentations are labelled; the **nomenclature
entry itself is not** (`appendix.tex:49`), and the check named "dictionary labels Gamma_p" is
satisfied by the table row at `:136` — removing the dictionary label leaves 109/109 PASS (**N1**).
Secondary: `ch06:83` defines the ratio at first use without the mixed qualifier, though A-5 five
lines later supplies it.

**A-5** (`ch06:101–104`): `Γ_p ≥ 5`, "evaluated on the like-for-like definition … `1.73×10³` at the
baseline"; both `1726` and `2382` exceed 5 by more than two orders of magnitude, so the criterion is
met under either definition ✔. The headline choice remains an author decision (§8).

### 6.2 Independent recomputation of the whole chain

Scripts `evidence/auditor_numerics{,_2,_3,_4}.py`; inputs parsed from `ch02` (`tab:geometry`, property
table) and `ch09` (`Nu_H1 = 5.385`); formulas written from the manuscript's own equations.

| Quantity | Recomputed | Printed | Rel. dev. | Class |
|---|---|---|---|---|
| `h = Nu_H1 k_f/D_h` | 3231.0 W m⁻²K⁻¹ | 3231 | 0 | recomputed |
| `ΔT_t` | 60.000 K | 60 | 0 | recomputed |
| `ΔT_b` | 1.4354 K | 1.44 | −0.3 % | recomputed |
| `θ̄ = ΔT_t/2 + q''/h + ΔT_b/2` | **32.2652 K** | 32.3 | −0.11 % | **recomputed** |
| `N_θ = −Edαθ̄/(1−ν)` | **−29038.7 N/m** | −2.91×10⁴ | −0.21 % | recomputed |
| `N_cr = π²D_s/L²` | 105745.8 N/m | 1.057×10⁵ / 1.06×10⁵ | +0.04 % | recomputed |
| `T̄_cr = π²d²/[12α(1+ν)L²]` | 117.495 K | 117 (`ch07:38`), 117.5 | 0 | recomputed *(by me; not by the suite)* |
| `M_b = T̄_cr/θ̄` | 3.6415 | 3.64 | +0.04 % | recomputed |
| `D_s` | 9.6429 N m | 9.6 | +0.4 % | recomputed |
| `κ_th` | 1.4000 m⁻¹ | 1.4 | 0 | recomputed |
| `μL` | 1.64629 | 1.65 | −0.22 % | recomputed |
| `w_max^lin = κ_thL²/8` | 1.5750×10⁻⁴ m | 1.575×10⁻⁴ | 0 | recomputed |
| `w_max` (`eq:beamcolsol`) | **2.18858×10⁻⁴ m**, `0.43772 H₀` | 2.19×10⁻⁴, 0.438 | −0.06 % | recomputed |
| amplification | 1.3896 | 1.39 | −0.03 % | recomputed |
| `κ_geo = κ_th sec(μL/2)` | 2.05907 m⁻¹ | 2.06 | −0.05 % | recomputed (identity holds to ≤1e−12) |
| `M_mid = D_s(κ_geo−κ_th)` | 6.35535 N m | 6.4 | −0.70 % | recomputed |
| `σ_bend = 6|M|/d²` | **4.2369 MPa** | 4.2 | +0.88 % | recomputed |
| `σ_memb = −Eαθ̄/(1−ν)` | −9.6796 MPa | −9.6 | −0.8 % | recomputed |
| `σ_max = |σ_memb|+σ_bend` | 13.9165 MPa (0.1546 σ_y) | 13.9, 0.15 | +0.12 % | recomputed |
| `ε_mech = e₀ + (κ_geo−κ_th)d/2` | 3.2472×10⁻³ | 3.25×10⁻³ | −0.08 % | recomputed |
| arc term `½⟨w'²⟩` (quadrature) | 1.38786×10⁻⁴ | 1.39×10⁻⁴ | −0.15 % | recomputed |
| circular-arc `κ_geo²L²/24` | 1.58992×10⁻⁴ | 1.6×10⁻⁴ | −0.6 % | recomputed (ratio to exact 1.146, inside the stated 10–20 % band) |
| first-iterate relaxation `ΔN/N_θ` | 6.14 % | 6.1 % | +0.7 % | recomputed |
| fixed point of `eq:nupdate` | `N* = 27330.6 N/m` (5.88 %), `w_max = 2.13988×10⁻⁴ m = 0.4280 H₀`, `σ_bend* = 3.8989`, `σ_memb* = 9.1102`, `σ* = 13.009` | 2.733×10⁴, 5.9 %, 2.14×10⁻⁴, 0.428, 3.9, 9.11, 13.0 (D-28) | ≤0.4 % | recomputed |
| `p̄` | 84.0 Pa | 84 | 0 | recomputed |
| `w_p = 5p̄L⁴/(384D_s)` | 9.1875×10⁻⁸ m | 9.2×10⁻⁸ | −0.14 % | recomputed |
| `Γ_p` mixed | **2382.13** | 2.4×10³ | −0.74 % | recomputed |
| `w_p(N_θ^c)` | 1.26778×10⁻⁷ m | 1.27×10⁻⁷ | −0.17 % | recomputed |
| `Γ_p` like-for-like | **1726.3** | 1.73×10³ | −0.21 % | recomputed |
| linear-limit ratio `48κ_thD_s/(5p̄L²)` | 1714.3 | 1.7×10³ | +0.8 % | recomputed |
| mid-span height `1 + w_max/H₀` | 1.437716 | 1.4377 (register) | 2×10⁻⁵ | recomputed |
| `Gr`, `Ri` | 1.073, 1.717×10⁻³ | 1.07, 1.7×10⁻³ | 0 | recomputed |
| ODE residual `D_s w'''' + N w''` | ≤ 1.5×10⁻¹¹ (3 stations) | 0 | — | identity |
| BCs `w(0), w(L), w''+κ_th` | 0, 1×10⁻¹⁹, 0, −2×10⁻¹⁶ | 0 | — | identity |

Everything in §6.2 is **recomputed**, not copied: I re-derived each formula from the manuscript and
re-implemented it independently of `regression.py`. The only values that are author-dependent are
the *inputs* (materials data, `σ_y` band, `Nu` choice) and the `Γ_p` headline convention (§8).

### 6.3 Retraction of a preliminary auditor finding (important)

My working notes from earlier in this audit recorded `θ̄` as unreachable from its own formula,
because `q''/h` was computed with `D_h = 6 mm`. That was an **auditor error**: `D_h = 2H₀ = 1 mm`
(`ch02:41`). With the correct hydraulic diameter, `q''/h = 1.5475 K` and
`θ̄ = 30 + 1.5475 + 0.7177 = 32.2652 K` exactly matches the register value. **The `θ̄` formula is
closed and correct**; the only residue is the 0.05 K component rounding in §3.3. See Appendix B.

---

## 7. Build and package

### 7.1 Build / render attempt

| Attempt | Result |
|---|---|
| `pdflatex`/`latex`/`lualatex`/`xelatex`/`latexmk`/`tectonic` | **MISSING** |
| `pdftoppm`/`pdftotext`/`gs`/`qpdf` | **MISSING** |
| `convert main.pdf[0]` (ImageMagick) | `attempt to perform an operation not allowed by the security policy 'PDF'` |
| Python PDF readers (`pypdf`, `PyPDF2`, `fitz`, `pdfminer`) | **MISSING** |

Consequences, stated exactly:
- **I-13 (TeX build) remains OPEN.** No compile was attempted or claimed.
- **I-15 (figure/TikZ render) remains OPEN.** No figure was rendered or inspected.
- I could not even read the tracked `main.pdf`. The suite reports
  `WARNING main.pdf predates 15 source file(s); a LaTeX rebuild is REQUIRED` and
  `the tracked main.pdf does NOT contain the Stage 17 corrections` — this is a *reported, not
  asserted* observation (`regression.py` Section 7), and I cannot independently confirm the
  content claim without a PDF reader. **Treat "the PDF is stale" as the suite's claim, not as my
  verified finding.**
- I did not install a TeX engine or a PDF library: unapproved dependencies are excluded by the
  standing constraints.

### 7.2 Package verification (independent)

```
zip sha256 = 8f67ef7c03e8d4e138383d87e9b7237c994c51125f959dc3981c77f5d6f5d5d1
size = 802932 bytes ; members = 75 ; CRC (testzip) = ok
manifest rows = 75 ; member-digest mismatches = none ; members not in manifest = none
member timestamps = all (2026-10-19 00:00:00), compression = deflate
```

`evidence/verify_package.py` parses `audit_stage15/package_manifest.txt`, recomputes SHA-256 of every
member and compares. **75/75 match.**

**Determinism:** I extracted `git archive HEAD` into an empty directory and re-ran
`python3 audit_stage15/build_package.py`:

```
8f67ef7c03e8d4e138383d87e9b7237c994c51125f959dc3981c77f5d6f5d5d1  802932  75
```

Byte-identical to the shipped ZIP, hence to its member hashes. The build is reproducible from the
frozen commit with no working-tree state.

**Unresolved anomaly (carried from the implementation cycle):** one earlier rebuild in the previous
cycle produced `32b315a0…`. It is **not reproducible** now — the clean-copy rebuild matches the
shipped artifact exactly — so I record it as an unexplained one-off rather than a determinism
failure. Anyone relying on the determinism claim should re-run the two-command check in Appendix A.

---

## 8. Items that remain unresolved by instruction

I did **not** resolve, and the source still does not determine, the following. Each remains
`OPEN-AD` where it bites:

| Item | State in the manuscript | Where it bites |
|---|---|---|
| **RU-01** casing clearance / contact / vented vs sealed cavity | no standoff distance anywhere; B8 gives zero traction on the remaining solid faces, so the outer face is mechanically free, while the strip bows **towards** the casing by `0.4377 H₀ = 0.219 mm` | the outer-face mechanical BC, contact, and any passage-geometry claim |
| **RU-03** deformed mid-span height | **no sentence** states the *value* (`ch01:10` does state the direction, "bows away from the interior of the passage"); `1.4377 H₀` appears only in `audit_stage15/` (ledger, register, spec), never in `chapters/` (my recomputation: `1.437716 H₀`) | post-processing and any passage-height statement |
| **Heater mounting / face** | `q''` is applied on `Γ_h⁰` (B6) as a design choice; no mounting hardware, contact resistance or axial conduction path is modelled | A8 perfect-contact assumption; regime D variant B9 |
| **Contact law** | A8 assumes perfect thermal contact (no contact resistance, no gap conductance) | interface flux continuity `eq:ifflux`; RU-01 |
| **Headline `Γ_p`** | mixed (2382) reported as headline, like-for-like (1726) disclosed (D-29) | A-5 classification; any paper-level claim of thermal dominance (both ≫ 5, so the conclusion is insensitive) |

The manuscript is honest about these: it does not assert a standoff, a contact resistance, or a
mid-span height. No "silent resolution" was found.

---

## 9. Findings, required corrections, gate verdicts

### 9.1 Finding table

| ID | Sev. | Location | Evidence | Finding | Status |
|---|---|---|---|---|---|
| AU17-01 | **MED** | `ch08:166–206, 231–239` | §2(e) | Fixed-point convergence is neither proved nor bounded; relaxation applies only to displacement; stopping rule is mechanical (`‖Δd‖`); escalation trigger ignores the thermal loop | **OPEN** |
| AU17-02 | **MED** | `ch08:173–223`; `regression.py:110–128,132–137`; `audit_appendix:56` | G1, G2, G3 | The Stage 17 well-posedness repair is not protected by any check: over-determined `Γ_if` and re-inserted gauge constraints pass 109/109. D-32's "Regression: … the fingerprint of the iteration text" is inaccurate — the step list is an `enumerate`, not a display equation, and no fingerprint covers it | **OPEN** |
| AU17-03 | **MED** | `ch07:34` | T1, mutF, mutF2 | The `θ̄` formula cell is unprotected: `ΔT_t/3 + q''/(2h) + ΔT_b/2` passes 109/109 | **OPEN** |
| AU17-04 | **MED** | `ch07:38`, `appendix:77,82` | T2 | `T̄_cr` (117.5 K) is recomputed by no check; `M_b ≥ 2` depends on it and the `M_b` check uses a hard-coded 117.5 | **OPEN** |
| AU17-05 | MED | `regression.py:135` | G1, G2 | Gauge check defeated by its ±260-character "explained" window and scans `ch08` only | **OPEN** |
| AU17-06 | LOW | `regression.py:174` | source | `check(..., … or True)` is a constant PASS | **OPEN** |
| AU17-07 | LOW | `appendix:49`; check at `regression.py:168` | N1 | I-11 residue: nomenclature `Γ_p` unlabelled; the "dictionary" check anchors at `appendix:136` | **PARTIALLY CLOSED** |
| AU17-08 | LOW | `ch04:166–169`, `ch11:27–29` | Q8 rerun, S1 | 0.2 % is right and extraction-robust, but "the check is complete" overstates a single 24-element mesh; the NEW-05 guard is phrase-specific | **PARTIALLY CLOSED** |
| AU17-09 | INFO | campaign summary line | §4.1 | "25 numeric/identity" actually = 10 numeric + 12 claim-string + 3 pattern guards | **OPEN (reporting)** |
| AU17-10 | LOW | `ch07:34`, `ch07:49` | retraction | The `q''/h` component prints `1.6` where `1.5475 → 1.5` at one decimal, while the same table prints `1.55` at `ch07:49`; total `32.3` correct. (A preliminary auditor claim that `θ̄` was unreachable is retracted — Appendix B) | **OPEN (editorial, C5)** |
| AU17-11 | — | `ch08:173–223`, `ch05:5–25` | §2 | Stage 17 partition well posed; sign/normal/unit chain and level determinacy correct | **CLOSED (verified)** |
| AU17-12 | — | `ch04`, `ch07`, `appendix` | §6.2 | Every printed scalar in the chain reproduces independently to printed precision | **CLOSED (verified)** |
| AU17-13 | — | build | §7.1 | No TeX engine, no renderer, no PDF reader | **OPEN-ENV** (I-13, I-15) |
| AU17-14 | LOW | `ch02:47`, `ch06:111–115` | §2(f) | `T_in`, `T_ref` unfrozen; documented (C-6); no printed number depends on them | **OPEN-DATA** |
| AU17-15 | — | §8 | — | RU-01, RU-03, heater face, contact law, headline `Γ_p` unresolved | **OPEN-AD** |
| AU17-16 | INFO | `q8_pin_verification.py` | `FREE case: solved (unexpected: rigid modes not removed)` | evidence script lacks the assertion that would catch this; reported cases unaffected | **OPEN (INFO)** |
| AU17-17 | LOW | `ch08:176–177` | source | "zero flux on `Γ_end` and on the remaining faces (B6–B8)": the parenthetical range includes B6, which is the **non-zero** heater flux | **OPEN (editorial)** |

### 9.2 Required corrections (for the next stage; not applied by this audit)

**C1 — make the seven survivors fail (verification only).**
(a) delete `or True` and assert the ledger claim properly (`regression.py:174`);
(b) replace the gauge check by an *occurrence-level* test: any `∫p = 0`-type relation must be
present only inside a sentence that contains "would over-determine" **before** the relation, with a
window measured to the sentence, not ±260 characters — and scan `ch05`, `ch08` and the appendix;
(c) add a **boundary-condition-set** assertion: for each boundary ID in `tab:bcs`, exactly one
thermal condition; and `Γ_if` must never carry Dirichlet *and* Neumann for the same field in the
iteration description;
(d) fingerprint (or numerically parse) the `θ̄` table row, the `T̄_cr` row and the iteration
`enumerate`;
(e) add an explicit recomputation of `T̄_cr = π²d²/[12α(1+ν)L²]` and of the `M_b` quotient from it;
(f) re-anchor the `Γ_p` label check to `appendix:49`;
(g) add G1, G2, G3, T1, T2, N1, S1 to the permanent campaign with *expected detection* recorded,
and do not count fingerprint-only kills as semantic coverage.

**C2 — `ch08`: add one limitation sentence** after step 6 stating that the staggered iteration's
convergence is not proved, that the under-relaxation factor and the escalation trigger are the
safeguards, and that the trigger is mechanical; add `‖ΔT_Γ‖` to the stopping rule.

**C3 — `appendix:49`**: label the nomenclature entry `Γ_p` (mixed; like-for-like, D-29).

**C4 — `ch04:169`**: qualify "the check is complete" by the resolution of the single-mesh Q8
computation (24 elements, 101 nodes), or cite a refinement study.

**C5 — `ch07:34`**: `ΔT_t/2 + q''/h + ΔT_b/2 = 30 + 1.55 + 0.72 = 32.27 ≈ 32.3`, which is what `h = 3231` gives (the current text prints `1.6` for a `1.5475` term).

**C6 — `audit_appendix` D-32**: correct the "Regression:" cell — the iteration text is not
fingerprinted; the protecting checks are the claim strings at `regression.py:110–128`, which G3
defeats until C1(c) is done.

**C7 — `ch08:176`**: change "(B6–B8)" to "(B7–B8)" after "zero flux", so the range does not imply
that B6 is a zero-flux condition.

### 9.3 Gate verdicts

- **Gate A (formulation and well-posedness): PASS.** The Stage 16 diagnosis was right, the Stage 17
  remedy is right, and it is the only assignment (among the two pure ones) that is solvable at every
  iterate. Reserved: convergence (AU17-01).
- **Gate B (numbers): PASS.** Full independent recomputation of every headline scalar, both `Γ_p`
  definitions, and the self-consistent fixed point.
- **Gate C (verification evidence): FAIL.** 7 semantic escapes, 1 vacuous check, 3 unprotected
  formula/parameter cells, 9 fingerprint-only detections, 12 phrase-only detections among the
  claimed 25 "numeric".
- **Solver readiness: NOT READY.** Well posed ⇏ convergent; no coupled run; no build; five
  author decisions open.

### 9.4 Direct answers

1. **Is Stage 17 accepted?** The *repair* is **accepted** — mathematically correct (Gate A) and
   numerically verified (Gate B), with one editorial rounding fix (C5) and one limitation sentence
   (C2). The *verification claim* of `12_stage17_repair_report.md` — that the suite now protects the
   repair, with 34/34 mutants caught — is **not accepted** as stated (Gate C).
2. **Does it need another repair stage?** **Yes, one bounded stage**, confined to
   `audit_stage15/regression.py`, the fingerprint file, the permanent mutation campaign, the D-32
   evidence cell, and three editorial sentences (C1–C7). No physics, no derivation and no printed
   result needs changing; nothing in §6.2 is wrong.
3. **Is the coupled production solver ready?** **No** — see Gate C and the four items in §2(e);
   RU-01/RU-03, the heater face, the contact law and the `Γ_p` headline remain author decisions.

---

## 10. Discipline and limitations of this audit

- No source, figure, test, package or commit was modified. The only addition is
  `independent_audit_stage17/` (this report plus `evidence/`).
- All mutation work ran in isolated copies under `/tmp/audit17/`; the repository's own
  `regression.py` and `equation_fingerprints.json` were never regenerated in place (the
  `--update-fingerprints` run was executed only inside a copy, as mutant F1).
- **Branch limitation (reported, not worked around):** this session is bound to
  `arena/c875f9b3-hff-final-overleaf-package-fix`. I therefore could **not** publish this report on a
  separate independent audit branch, and I did not touch `origin/main` or
  `claude/independent-audit-7c9749f`. The report is committed on the session branch under
  `independent_audit_stage17/`; that is the exact and only push made.
- I did not claim any build, render, PDF inspection, or coupled solver run.
- `34/34` was reproduced and then re-interpreted; no PASS in this report rests on internal
  consistency, on a prior report, or on the campaign's detection count.

---

## Appendix A — reproduction

```bash
cd /home/user/HFF_Final_Overleaf_Package_FIXED          # HEAD 211f751, tree clean

python3 audit_stage15/regression.py                     # 109/109
python3 audit_stage15/mutation_campaign_stage17.py      # 34/34, 25 "non-fingerprint" (see §4.1)
python3 independent_audit_stage17/evidence/auditor_mutants.py        # 7 escaped, 3 detected, F1
python3 independent_audit_stage17/evidence/auditor_numerics.py       # chain part 1
python3 independent_audit_stage17/evidence/auditor_numerics3.py      # fixed point (this supersedes
#   the fixed-point block of auditor_numerics2.py, whose compatibility update carried a sign error;
#   the ODE/BC and strain blocks of numerics2 are unaffected)
python3 independent_audit_stage17/evidence/auditor_numerics4.py      # T_cr, M_b, sigma, Gamma_p
python3 independent_audit_stage17/evidence/check_classification.py   # 109-assertion taxonomy
python3 independent_audit_stage17/evidence/verify_package.py         # 75/75 digests
python3 independent_audit_stage16/evidence/q8_pin_verification.py    # 0.2 % evidence, re-executed

# determinism (does not touch the working tree)
rm -rf /tmp/rebuild && mkdir -p /tmp/rebuild
git archive HEAD | tar -x -C /tmp/rebuild
cd /tmp/rebuild && python3 audit_stage15/build_package.py
sha256sum HFF_Final_Overleaf_Package.zip        # 8f67ef7c…d5d1, 802932 bytes, 75 members
```

Evidence files: `evidence/{freeze_and_toolchain,auditor_numerics,auditor_numerics2,
auditor_numerics3,auditor_numerics4,check_classification,check_group_counts,mutation_campaign_rerun,
auditor_mutants,q8_rerun,verify_package,greps_new05_ru}.txt`.

## Appendix B — two of my own preliminary findings, tested and retracted

1. **"`θ̄` is unreachable from its own formula."** *Retracted.* The claim rested on
   `D_h = 6 mm`; the manuscript defines `D_h = 2H₀ = 1 mm` (`ch02:41`). With the correct value,
   `h = 3231`, `q''/h = 1.5475 K`, and `θ̄ = 32.2652 K` exactly. The formula is closed. What remains
   is the 0.05 K component rounding (AU17-10).
2. **"The gauge check's regex is over-escaped and can never match, so the check is vacuous."**
   *Disproved.* The file's pattern carries two backslashes before `int`, i.e. the regex matches
   one literal backslash followed by `int`, which is exactly TeX — it does match; my counter-test
   had over-escaped the pattern, not the suite. The real defect is the ±260 character exemption
   window (§3.4.3), proved by G1. The only provably vacuous assertion in the suite is the
   `or True` at `regression.py:174`.

Both cases are recorded because an audit that only reports confirmed findings, and not the ones it
retracted, cannot be re-checked.
