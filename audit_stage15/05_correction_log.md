# Stage 15 — Correction log

**Source-correction commit:** `e8ef0d78443bef7e35408671983ce2b57af83eba` (`e8ef0d7`)
**Parent:** `9066c3b` (baseline re-verified clean, tree and remote in agreement)
**Diff:** 13 files changed, 108 insertions(+), 41 deletions(−)

Every entry records: the original claim **preserved verbatim** in Appendix B, why the change was
needed, the old and new text, the downstream dependencies, the recalculation, and the regression
check. Line numbers are post-edit.

---

## A. Convention and sign (workstreams A, F)

### D-21 — deflection convention
- **Original claim (preserved in register D-21):** `w = −d₂`, "positive into the channel";
  `κ = −w''` positive bowing into the channel; `D_s w'''' = −p`.
- **Why:** the algebra, both pin conditions, the fluid domain map (`ch03:157–159` builds `Ω_f` from
  `ŵ = d`) and nine of ten sign-bearing relations were already Package B. The prose was the outlier,
  and as a *package* it predicted bowing the wrong way. Full derivation in
  `02_derivation_and_sign_convention.md`.
- **Changes:**
  | File:line | Old | New |
  |---|---|---|
  | `ch02:27` (caption) | "positive into the channel" | "away from the channel" |
  | `ch02:129–133` | `w = −d₂`, "into the channel", "bows into" | `w = +d₂`, "away from", "bows away" |
  | `ch02:134–137` | — | new: the pin-moment argument, `−27 N·m` residual |
  | `ch03:140` | `D_s w'''' = −p` | `D_s w'''' = +p` |
  | `ch03:144` | "positive into the channel"; "pushing the wall away" | "away from the channel" (kept) |
  | `ch04:186` | `w''(0)=w''(L)=−κ_th`, "w positive into the channel" | same equation, "away from the channel" |
  | `ch04:190–192` | `M` unnamed | `M` sagging-positive, `M = −∫σ_xx y dy`, `M_phys = −M` |
  | `ch04:296` | load "**opposing** the bowing" | "acting in the same sense as the thermal bowing" |
  | `ch01:10` | "bows toward the interior" | "away from the interior" |
  | `main.tex:54` | "deflects the segment into the flow passage" | "away from the flow passage"; "the widened passage" |
  | `ch09:43` | V-C2 no sign | `κ = (1+ν)αΔT_t/d > 0` (hot face convex) |
  | `ch09:47` | V-C3 no sign | `w_max = κ_thL²/8 > 0` **measured away from the channel** |
  | `fig_geometry:18–22` | bow 6 pt into fluid; outer face straight | bow 6 pt **away**; **both faces** displaced equally |
  | `fig_geometry:36–38` | `w` arrow 11 pt against a 6 pt bow | arrow spans the drawn 6 pt bow |
  | `fig_geometry:27–28` | flux arrows end 2 pt above wall | lifted clear of the bow |
- **Downstream:** every use of `w`, `κ`, `w_p`, `Γ_p`, the wall figure, the validation tests.
- **Recalculation:** none — the equations are unchanged, so no numerical result moved. Confirmed by
  re-running the whole register: `w_max = 2.188704727879×10⁻⁴ m`, `0.437740946 H₀`, identical to
  three digits beyond every printed value.
- **Regression:** nine sign-bearing relations re-grepped and all now appear in Package B; `ch03:140`
  was the only A-consistent equation and is corrected. `ch05/ch06/ch08` confirmed to contain no
  `w`-sign dependence by inspection of every occurrence.

### D-21 (cont.) — figure geometry
- **Why:** the caption and the drawing disagreed with the text after the direction change; and the
  outer face was drawn straight while the inner face bowed, which is kinematically impossible for a
  strip of constant thickness under this model (both faces displace by the same `w`).
- **Recalculation:** control point `+12` gives a quadratic-Bézier mid-span of `+6` pt; the `w` arrow
  was `\Hf−12 → \Hf−1` (11 pt) against a 6 pt bow, and now spans `\Hf → \Hf+6`. Flux arrows moved
  from `+2` to `+12` above the wall so they clear the bow.
- **Regression:** `\begin`/`\end` balanced (1/1); braces 26/26; `\Le, \L, \Lo, \Hf, \ds` all
  defined at lines 4–6 before first use.

## B. Thermal and constitutive (workstream B)

### D-23 — arc-stretching term, six sites
- **Original claim:** `½⟨w'²⟩ = 1.8×10⁻⁴` (preserved in D-23, and the historical value in D-11).
- **Why:** not reproducible from `eq:beamcolsol`; and provably inconsistent with `6.1 %` in the
  same paragraph, since `1.8×10⁻⁴/e₀ = 7.968 %`.
- **Changes:** `ch02:92`, `ch04:230`, `appendix:73`, `appendix:104`, `ch07:33`, `ch07:75` →
  `1.39×10⁻⁴`.
- **Recalculation:** `1.3880097291955×10⁻⁴` analytically and `1.3880097291955×10⁻⁴` by Simpson
  quadrature — agreement `1.3×10⁻¹⁴` relative. Relaxation `6.1446 %`, printed `6.1 %`, retained.
- **Preserved, not corrected:** the circular-arc estimate `κ_geo²L²/24 = 1.590128×10⁻⁴ → 1.6×10⁻⁴`
  (−0.62 %). The formula is *correct* for a constant-curvature parabolic arc; it is retained and
  labelled a peak-curvature estimate. Do not "fix" it.
- **Regression:** no remaining `1.8×10⁻⁴` in body text; the two survivors are the historical
  register entries that record the withdrawal.

### D-22 — `Γ_p` definition
- **Original claim:** `Γ_p = w_th/w_p = 48κ_thD_s/(5p̄L²) = 1.7×10³`; appendix row printed `2.4×10³`
  against that same closed form (+40.00 %).
- **Why:** the closed form is identically the **linear** ratio `w_lin/w_p = 1714.285714`. The quoted
  `2.4×10³` is `w_max/w_p = 2382.263649`. One symbol carried both.
- **Changes:** `ch04:299–309` redefined as `Γ_p = w_max/w_p = [closed form] × (w_max/w_max^lin)`;
  `ch06:83` definition updated from the closed form to `w_max/w_p`; `appendix:94` and `appendix:130`
  re-expressed as `w_max/w_p`.
- **Recalculation:** `1714.285714 × 1.389653795 = 2382.263649`; and
  `(w_max/w_p)/(w_lin/w_p) = 1.389653795 = w_max/w_lin` exactly.
- **Regression:** the reported value `2.4×10³` is unchanged everywhere; only its provenance moved.

## C. Weak form and boundary conditions (workstream G)

### D-25 — spaces, gauge, geometric stiffness, SUPG, solver split
- **Original claim:** five spaces named and undefined; gauge asserted but not enforced; geometric
  stiffness absent from `eq:weaks`; SUPG coefficient "standard"; monolithic cancellation and a
  staggered iteration described as if the same object.
- **Changes:**
  | File:line | Addition |
  |---|---|
  | `ch08:60–72` | `V_g, Q, S_f, V_s, S_s` defined; traces in `H^{1/2}(Γ_if)`; outlet mean-pressure gauge |
  | `ch08:53–54` | `−∫ N_θ^c ∂_X d₂ ∂_X φ₂ dX` added to `eq:weaks` |
  | `ch08:74–76` | its interpretation and reduction, qualified to `eq:beamcol` (no load) / `eq:beam` (no force) |
  | `ch08:21–28` | `eq:supg`: `τ_K`, `Pe_K`, units, `Pe≫1` limit |
  | `ch08:160–166` | assembled cancellation vs staggered recovery; V-B flux-jump norm as acceptance criterion |
- **Why:** the production model was linear while the baseline was beam–column (a `39 %` gap in
  `w_max`); and a coding team cannot implement a gauge, a `τ`, or a solver split that is not stated.
- **Derivation checks:** weak form of `eq:beamcol` reproduces the added term with the sign for
  `N_θ^c > 0`; the printed closed-form solution satisfies the printed ODE and all four BCs to
  `≤1.5×10⁻¹¹` (see `04_weak_form_and_bc_verification.md` §9).
- **Regression:** `eq:supg` is a unique new label; no dangling references introduced (87 labels, 87
  distinct, 0 missing targets).

### D-24 — thermal data flow
- **Original claim:** "the fluid subproblem receives its domain and the interface temperature from
  the solid; the solid subproblem receives the interface traction ... and the conjugate flux
  condition" (preserved in D-24).
- **Why:** contradicts `ch08:108` ("the temperature is not prescribed on `Γ_if`") and is ill-posed
  as stated — a flux datum on `Γ_if` leaves the solid pure-Neumann.
- **Change:** `ch05:70–79` restated: mechanically Dirichlet–Neumann; thermally a shared unknown
  whose equation is the flux balance; the pure-Neumann singularity and its propagation into `N_θ`
  given as the reason a flux datum is inadmissible.
- **Rejected first draft:** an earlier version of this edit described a Dirichlet–Neumann *thermal*
  exchange. It was caught on re-audit for contradicting `ch08:108` and `ch08:115` and replaced. The
  episode is recorded in `04_…` §5 because it is precisely the failure mode a batch introduces.

## D. Nothing else was edited

No change was made to: `eq:beamcol`, `eq:beamcolsol`, `eq:nupdate`, `eq:mf`, `eq:wpdef`,
`eq:ntheta`, `eq:tcr`, any material property, any benchmark value, `references.bib`, or any of the
Stage 11–14 reports (which remain outside the tree and are cited as external).

## E. Commit

    commit e8ef0d78443bef7e35408671983ce2b57af83eba
    parent 9066c3b
    13 files changed, 108 insertions(+), 41 deletions(-)

---

# Stage 16 correction log — Claude audit responses

Format: original claim (preserved), why it had to change, old → new, downstream dependencies,
recalculated results, regression check, commit. Commit hashes are recorded in
`10_final_readiness_report.md` once the Stage 16 commit exists.

## D-26 — the pin was specified as a clamp (I-01, the highest-priority defect)

- **Original claim (preserved verbatim in `ch02` A9):** the support was described as a "pinned"
  end; the constraint set actually imposed both `d_1 = 0` and `d_2 = 0` on the whole end edge,
  i.e. a **clamp**.
- **Why it had to change:** a clamp suppresses the thermal bow entirely (`w ≡ 0`), which is the
  mechanism the whole document analyses. The stated physics and the stated boundary condition were
  mutually exclusive, so every downstream deflection number was attached to the wrong idealisation.
- **Old → new:**
  - old: `d_1 = d_2 = 0` on `X = 0, L`;
  - new: `d_2 = 0` on the **full** end edge and the **edge mean** `⟨d_1⟩ = 0`, with zero applied
    moment left as a natural condition. Mean-preserving (not pointwise) suppression of `d_1` is what
    lets the strip bend while blocking mean axial expansion.
- **Downstream dependencies:** `eq:weaks` (`V_s`), `ch05` B7, the Q8 benchmark, and the
  interpretation of `w_max` in `ch04`/`ch07`.
- **Recalculated evidence (self-checking Q8 program, `/tmp/v16/fe5.py`):** pin 1.0000, full-edge
  roller 0.9980, full-edge clamp −0.0199 / −0.0184. The earlier "few per cent" claim for the clamp
  is withdrawn; the clamp does not reduce the bow by a few per cent, it reverses and nearly
  annihilates it.
- **Residual author decision:** point pin vs rigid end face (≈0.5 % difference). Both are now
  described; the document uses the edge-mean form and says so.
- **Regression check:** `B7 is not a full-edge clamp`, `B7 imposes d_2=0`, `B7 blocks mean axial
  displacement`, `V_s is not a clamp`. Mutation `m6` (replacing the pin by `d_1=d_2=0`) is caught.

## D-27 — missing `1/d` in the geometric-stiffness term (I-03)

- **Original claim:** `−∫ N_θ^c ∂_X d_2` in the weak form.
- **Why:** `N_θ^c` is a membrane **force per unit length** (N/m); `N_θ^c ∂_X d_2` has units N/m, not
  N, so the term does not balance `∫ σ:ε dX` (N). The stress resultant must be divided by the
  thickness to become a stress, which is what the moment-curvature derivation produces.
- **Old → new:** `−∫ N_θ^c ∂_X d_2 dX` → `−∫ (N_θ^c/d) ∂_X d_2 dX`. The accompanying text now
  states the units of every factor and why the `1/d` appears; the geometric stiffness in SI per
  unit width is `3×10⁻³` of the elastic one at the baseline.
- **Downstream:** the beam–column coefficient `μ`, hence `w_max`, `κ_geo`, `σ_max`, `Γ_p`.
  Numerically the change is absorbed by the definition of `N_θ^c` (see D-28 note), so the printed
  values are unchanged — this is a *dimensional* correction, not a numerical one, and is stated as
  such rather than presented as a change in results.
- **Regression check:** `geometric term present, negative, with N/d`, `old no-1/d geometric form
  removed`, `geometric term sign not flipped`. Mutations `m2` (sign flip) and `m5` (drop `1/d`) are
  both caught.

## D-28 — two stress values that contradicted each other (I-08)

- **Original claim (preserved):** `σ_max = 13.9 MPa` and, elsewhere, `σ_max = 13.6 MPa`, with the
  same input data.
- **Why:** the two came from different iterations of the membrane-force update (frozen `N` vs the
  converged `N`), but the text presented them as one number used in two places. Keeping both without
  labels made the document self-contradictory.
- **Resolution (two valid columns, not a contradiction):**
  - **self-consistent** `σ_max = 13.0 MPa = 0.145 σ_y` (`σ_bend 3.9`, `|σ_memb| 9.11`,
    `N_θ^c = 2.733×10⁴ N/m`);
  - **frozen-force** `σ_max = 13.9 MPa`, which is *higher* and therefore conservative; it is the
    value used wherever a design margin is being enforced.
  - the mixed `13.6 MPa` figure is **withdrawn**, with the reason stated in the appendix (it belonged
    to neither column).
- **Downstream:** the `0.2 σ_y` cap statement, the strain envelope, and `Γ_p`.
- **Regression check:** `appendix self-consistent sigma_max matches D-28`, `frozen stress exceeds
  self-consistent (conservative)`, `frozen stress below 0.2 sigma_y cap`, and the identity
  `E/(1−ν²)·max|ε_mech| = σ_max,frozen`.

## D-29 — `Γ_p` compared unlike with like (I-11)

- **Original claim:** `Γ_p = 2.4×10³`.
- **Why:** the numerator was the thermal bow under the thermal membrane force while the denominator
  was the hydraulic deflection under the *pressure* resultant; the two use different `N`.
- **Change:** `Γ_p` is now labelled a **mixed** ratio, and a like-for-like value is added:
  `w_p(N_θ^c) = 1.27×10⁻⁷ m`, giving `Γ_p = 1.7×10³`. Both are printed, each with its definition.
- **Downstream:** the statement that hydraulic deflection is negligible relative to thermal bowing —
  true for both definitions, so the conclusion is unaffected; the *strength* of the statement is.
- **Regression check:** `ch04 Gamma_p = w_max/w_p matches`, `ch04 linear-limit closed form
  matches`, `ch04 like-for-like w_p matches beam-column pressure solution` and
  `ch04 like-for-like Gamma_p matches`. The second pair is new: `w_p` is recomputed from the
  beam-column pressure solution (not from the linear formula times an amplification), giving
  `1.2678×10⁻⁷ m` against the printed `1.27×10⁻⁷ m` and `1726` against the printed `1.73×10³`,
  so the like-for-like pair cannot drift.
- **Residual author decision:** which definition is headline.

## D-30 — the pressure gauge constraint did not exist (I-04)

- **Original claim:** the pressure was fixed by imposing `∫_{Γ_out} p ds = 0`.
- **Why it had to change:** the gauge freedom does not exist here, because the bilinear form
  `b(v,1) = −∫_{Γ_out} v·n ds ≠ 0` — the incompressibility constraint is already non-singular. The
  constraint was removing nothing, and imposing it would *over-determine* the discrete system.
- **Change:** the constraint is **deleted**, not reworded; the paragraph states why no gauge is
  required and what would create one. The `ch05` sentence that referenced a prescribed pressure
  level was rewritten: the level is an **output** of the flow solve.
- **Downstream:** none in the pressure chain, which stays exact: `p(L) = 48 Pa`, `p(0) = 120 Pa`,
  `p̄ = 84 Pa` for `L_o = 20 mm`, `U = 0.05 m/s`, `H₀ = 0.5 mm`.
- **Regression check:** `gauge constraint removed`, `no-gauge argument stated`, and
  `B2 does not impose a pressure datum`. The last one was added after this batch: B2 still read
  "traction-free outflow with datum `p=0`", which reads as an imposed Dirichlet datum and
  contradicts "nothing is imposed". B2 now says the level at the outflow section is an
  **output** of the solve. Caught on the separate Stage 16 consistency pass, not by the batch.

## D-31 — SUPG and the thermal stagger (I-05, I-06)

- **Original claim:** the stabilisation was named but not written down; the thermal exchange was
  described in a way that left the solid problem pure-Neumann.
- **Change:**
  - the stabilised weak form is now printed as `eq:supgwf`, with the `h_K → h_K/p` caveat for `P2`
    elements stated explicitly (using `h_K` for `p = 2` over-stabilises);
  - the stagger is written as two distinct steps: (i) the fluid sees a **Dirichlet** datum `T_Γ` and
    the flux `q_Γ` is extracted as an output; (ii) the solid sees a **Neumann** datum `q_Γ`; (iii)
    the loop closes when the solid returns `T_Γ^{k+1}`.
- **Why:** naming a method is not a specification, and the earlier wording implied a flux datum on
  the interface, which is ill-posed for the solid.
- **Regression check:** `SUPG stabilised weak form written`, `SUPG P2 length scale addressed`,
  `staggered thermal partition stated`.

## Regression and mutation evidence (I-07)

`audit_stage15/regression.py` v2 runs 56 checks in six functional sections plus a reported
(not asserted) build-freshness section; `audit_stage15/mutation_test.py` clones the repository six
times into `/tmp/hff_mut`, applies one mutation per clone, and requires the baseline to pass and
every mutant to fail. Results are in `06_regression_results.md`.

---

# Stage 17 — repair of the independent Stage 16 findings

Every entry below states: the claim as it stood, why a change was needed, the old and new
value/equation, the downstream dependents, the recomputed results, the regression check that now
guards it, and the commit (a commit hash is recorded in `12_stage17_repair_report.md` §7, because a
commit cannot contain its own hash).

## SUPERSEDED — the D-31 entry above describes the wrong thermal assignment

The D-31 entry in this log says "(i) the fluid sees a Dirichlet datum `T_Γ` and the flux `q_Γ` is
extracted; (ii) the solid sees a Neumann datum `q_Γ`; (iii) the loop closes when the solid returns
`T_Γ^{k+1}`". That is the assignment the independent audit then showed to be ill-posed. The entry is
left in place as the historical record of what Stage 16 believed; **it must not be read as the
current specification**. The current specification is D-32 below and §12 of `09_…`.

## D-32 — the solid thermal subproblem was ill-posed (NEW-01)

- **Original claim (Stage 16, `ch05` and `ch08`):** the fluid was solved first with a Dirichlet
  interface temperature, the flux `q_Γ` was extracted, and the solid then received `q_Γ` as a
  Neumann datum; the text asserted that the prescribed flux `q''` **fixes the level** of `T_s`.
- **Why this is wrong.** The solid carries flux data on its whole boundary (`q''` on `Γ_h⁰`, zero
  elsewhere, `q_Γ` on `Γ_if`). A pure-Neumann problem has `ker = span{1}`: the solution is a line,
  and it exists only when the boundary fluxes sum to zero. At an intermediate iterate they do not.
  So the old iterate was *doubly* inadmissible — free level **and** generally unsolvable — and the
  claim that a flux fixes a level contradicted the chapter's own B7 remark.
- **Derivation of the well-posed solid problem.**
  `∇·(k_s∇T_s) = 0` in `Ω_s`, `T_s = T_Γ` on `Γ_if`, `+k_s∇T_s·n_out = q''` on `Γ_h⁰`,
  `k_s∇T_s·n = 0` on `Γ_end`, `Γ_h^out`, `Γ_c⁰`. With at least one Dirichlet surface the problem is
  uniquely solvable for every admissible flux data; the constant that a pure-Neumann form leaves
  free is exactly the interface temperature, which is *unknown of the coupled problem*, not a datum
  to be chosen.
- **Is a reference condition legitimate?** Yes — the model already contains one: `eq:iftemp`
  (temperature continuity on `Γ_if`) together with the inflow datum `T_in` of B1. No reference
  temperature, mean-zero projection or gauge was added. Choosing a datum "to make the solid
  solvable" would have replaced an output of the conjugate problem by an invention.
- **Change (iteration reordered, model untouched):**
  1. solid thermal with Dirichlet `T_s = T_Γ^{(k)}` on `Γ_if` and `+k_s∇T_s·n = q''` on `Γ_h⁰`;
     extract `q_Γ^{(k)} = +k_s∇T_s^{(k)}·n`;
  2. fluid thermal with Neumann `k_f∇T_f·n = q_Γ^{(k)}` on `Γ_if`, level anchored by `T_in` (B1);
     extract `T_Γ^{(k+1)} = T_f^{(k)}|_{Γ_if}`, which closes the loop;
  3–5. thermoelastic solve, mesh extension, under-relaxation (unchanged).
- **Trace through the dependency chain.** Level of `T_s` → `θ̄` (mean wall rise, `eq:ntheta`
  inputs) → `N_θ = −Eαθ̄d/(1−ν)` → `κ_geo`, `w_max` → `M_mid`, `σ_bend` → `Γ_p`. Recomputing from
  the parsed inputs: `θ̄ = 32.2652 K` (printed `32.3`), `N_θ = −2.9039×10⁴ N/m`
  (printed `−2.91×10⁴`), `N_cr = 1.0575×10⁵ N/m`, `μL = 1.6463`, `w_max = 2.1886×10⁻⁴ m`
  (printed `2.19×10⁻⁴`), `M_mid = −6.3554 N·m/m`, `σ_bend = 4.2369 MPa` (printed `4.2`),
  `Γ_p = 2.382×10³` mixed and `1.726×10³` like-for-like (printed `2.4×10³`, `1.73×10³`). **No
  printed value changes**, because the physical level was and remains the one set by `T_in`; what
  changes is that the algorithm can now reach it.
- **Where:** `ch08` §`sec:iteration` steps 1–2 and the new paragraph *"Why the solid receives the
  temperature and not the flux"*; `ch05` §`sec:datamodel`; register `D-32`; solver spec §12.
- **Downstream dependents rechecked:** `ch05` decomposition `d = d_th + d_p`, `eq:iftemp`,
  `eq:ifflux`, `eq:ntheta`, `eq:weaks` geometric term, V-B/V-D acceptance criteria, D-26/D-29
  numbers and the whole printed result set (109 regression checks pass).
- **Regression checks:** `solid receives the interface temperature (Dirichlet)`, `fluid receives
  the interface flux (Neumann)`, `step 1 gives the solid T_s = T_Gamma^{(k)} on the interface`,
  `the kernel/compatibility argument is spelled out`, `the pure-Neumann argument is stated`,
  `the false 'temperature level is fixed' claim is gone`, `the loop closes on the extracted
  interface temperature`, `the level is traced into theta-bar and N_theta`, `ch05 and ch08 agree
  that a solid flux datum is inadmissible`. Mutation evidence: B1, B2, B3, B9 are all detected.

## D-26 reconciliation — the end effect is 0.2 %, not "a few per cent" (NEW-05)

- **Original claim:** the pin idealisation was said to leave "an `O(d/L)` stiffening — a few per
  cent at the baseline", to be settled by "a one-time numerical check".
- **Change:** the measured plane-strain Q8 values are quoted (`1.0000` of `κ_th L²/8` for point
  pins, `0.998` for a full-edge vertical support with free axial mean, `−0.02` to `−0.06` for
  `d₁ = d₂ = 0`), i.e. **0.2 %**, `D-26`; the phrase "few per cent", the "one-time numerical check"
  and the "closing the residual" wording are removed from `ch04` and `ch11`, and the check is
  declared complete with no separate end-compliance correction.
- **Downstream:** none of the printed results moves by more than its last digit; the admissibility
  argument (A-3/A-6) is unchanged because the penalty is an order of magnitude below the bound.
- **Regression checks:** `ch04 has no stale few-per-cent stiffening claim`, `ch11 has no stale …`,
  `ch04 states the measured 0.2 % with its Q8 evidence`, `ch11 …`, `no 'one-time numerical check'
  left in the pin context`. Mutation B4 (`0.2 % → 2 %`) is detected.

## D-29 completion — every `Γ_p` presentation is labelled (I-11)

- **Original claim:** a single `Γ_p = 2.4×10³` was quoted as a like-for-like amplification,
  mixing an amplified numerator (`w_max`, beam–column) with an unamplified denominator
  (`w_p`, simply supported pressure deflection).
- **Change:** the mixed ratio is labelled as mixed wherever it appears (`ch04`, `ch07` table and
  prose, appendix A8 and the dictionary); the like-for-like value is given as
  `w_p(N_θ^c) = 1.27×10⁻⁷ m → Γ_p = 1.73×10³`; condition A-5 is evaluated on the like-for-like
  ratio and is met under either definition, so the *conclusion* (thermal dominance) never depended
  on the choice.
- **Still open (author):** which ratio is the headline figure — `OPEN-AD`, unchanged.
- **Regression checks:** `A8 labels the mixed ratio`, `A8 gives the like-for-like value`,
  `dictionary labels Gamma_p`, `ch07 table labels Gamma_p mixed`, `ch07 prose gives both ratios`,
  `A-5 is defined on the like-for-like ratio`, plus numeric checks on all five printed ratios.
  Mutations B5, B6 are detected.

## Regression suite v3 (I-07) and the mutation campaign

- `regression.py` now has three layers: (a) structural/claim checks; (b) **fingerprints** — every
  display equation body and every register row is canonicalised and SHA-256 hashed into
  `equation_fingerprints.json`, so any edit to an equation fails the suite until the file is
  deliberately regenerated with `--update-fingerprints`; (c) **parse-and-recompute** — the inputs
  are parsed from `ch02`/`ch09` and `θ̄`, `N_θ`, `N_cr`, `M_b`, `μL`, `w_max`, `w'_max`, `κ_geo`,
  the strains, the arc term, `M_mid`, `σ_bend`, both `Γ_p`, the self-consistent state and the four
  exact identities are recomputed and compared with the **printed** values, not with rounded
  intermediates.
- Results: **109 checks, all passing**; **34/34 mutants detected, 0 survivors** — the 25 independent
  Stage 16 mutants (A1–A25; A8, A15, A17 re-anchored because the sentences they attacked were
  rewritten, and the re-anchoring is recorded in the campaign file) plus nine new mutants B1–B9 that
  attack the Stage 17 repairs themselves.
- Honest limitation: 9 of the 34 are caught **only** by the fingerprint layer, which is a change
  detector — it would also fire on a legitimate edit. The 25 remaining are caught by a numeric or
  identity check that recomputes the quantity from the inputs.

## Stage 19 — the five surviving mutation classes, the reference-temperature clause, the ceiling display, and the Q8 scope

Supersedes nothing above; this section records four changes made after the independent Stage 18 audit
(`independent_audit_stage18/HFF_Stage18_Final_Acceptance_Audit.md`, commit `39ef118`). Implementation
report: `15_stage19_repair_report.md`.

### S19-A. Five blind spots in the verification suite (reproduced, then closed)

The five classes below were **first reproduced on `5741d36`**: the new campaign reported
`REQUIRED CLASSES 5 (M3c M6b M7 M8 M10): detected 0 of 5`, each surviving with the unmodified suite
(`stage19_before_after.txt`, first block). They are now permanent cases in
`mutation_campaign_stage19.py`, and all five fail for their intended assertion.

| Class | v4 behaviour | v5 rule | Evidence |
|---|---|---|---|
| pointwise gauge `p(\mathbf 0)=0` | not recognised | pointwise notations added to `P_NORM`; verdict clause-scoped | M3c → detected |
| "we choose … rather than …" | "rather than" excused the adoption | contrastive connectives are clause boundaries; negation may cross a noun | M6b → detected; P1 control now passes |
| double datum in a `Condition` column whose Boundary cell omits `Γ_if` | row never inspected | every `tab:bcs` row tested; non-zero solid flux only on the heated face | M7 → detected |
| prose double datum without "on surface" | required the phrase | datum-shape rule (solid Dirichlet + non-heated solid flux in one sentence) | M8 → detected |
| stale magnitude written `pct` | not in the pattern | `pct`, `percentage points`, `per-cent` added | M10 → detected |

No tolerance was loosened and no check was removed. The Stage 18 check names are retained, which is
why the 44-case campaign still declares and finds the same intended assertions.

**A fixed false positive, not only a closed hole.** Control P1 — "No normalisation is imposed:
constraining `∫_{Γ_out} p ds=0` would over-determine the system" — was **rejected by suite v4**,
because the negation reached "is imposed" across the noun "normalisation". The clause-scoped test
accepts it, so the hardening is not a one-way ratchet.

**Deliberate fingerprint regeneration.** Editing the `D-26` register row (scope) and adding `D-33`
(reference-temperature convention) and `D-34` (ceiling display) changes the register fingerprints, so
`equation_fingerprints.json` was regenerated once: 78 entries, `reg:D-26` changed, `reg:D-33` and
`reg:D-34` added, **nothing removed, no display-equation fingerprint changed**. This is a content
change recorded here and in the ledger, not a suppression of a failing check: the suite's substantive
layer still fails on any corrupted expression, and F1 (`eq:wmax` corrupted **with**
`--update-fingerprints`) is still detected by four substantive assertions.

### S19-B. `ch06` — `T_in` is a datum, not a property input (register D-33)

The sentence "Only temperature differences appear in the equations, so `T_ref` and `T_in` enter the
solution exclusively through property values" is true for `T_ref` and false for `T_in`. `T_in` is the
inflow Dirichlet datum of B1 and, through `eq:iftemp`, the anchor of the interface temperature level;
it enters as `T_in − T_ref`. The quoted `θ̄ = 32.3 K` is measured from the inlet bulk temperature
(`ΔT_t/2 + q''/h + ΔT_b/2`, with `ΔT_b` the rise from the inlet plane), so the baseline uses
`T_ref = T_in`. Both facts are now stated, with the offset a solver must carry if the two differ.
**No physical model changes and no printed value changes.**

### S19-C. `ch07` — the `M_b = 2` ceiling is 58.7 K, not 58.8 K (register D-34)

Recomputed from the parsed inputs (`d = 3 mm`, `α = 5×10⁻⁵ K⁻¹`, `ν = 0.4`, `L = 9 mm`):
`T̄_cr = 117.495290 K`, `T̄_cr/2 = 58.747645 K`, one-decimal rounding **58.7 K**. The printed 58.8 K
came from rounding the already-rounded `117.5/2 = 58.75`. The dependent flux ceiling
`q'' ≈ 9.1×10³ W/m²` is unchanged, as are `M_b = 3.64`, the thickness catalogue and every other
printed number. The regression assertion now compares the displayed value with
`round(T_cr/2, 1)` at `1e-12`, i.e. with **no tolerance**, so reverting to 58.8 fails.

### S19-D. Q8 evidence scope (ch04, ch11, ch02 A9, register D-26)

The six-mesh study (re-run in Stage 19, `15_stage19_repair_report.md` §5) gives, as a ratio to
`κ_th L²/8`:

| mesh | elements | POINT mid/top | PIN mid/top | CLAMP mid/top |
|---|---|---|---|---|
| 6×2 | 12 | 1.0025 / 1.0000 | 1.0024 / 0.9999 | −0.0761 / −0.0803 |
| 12×2 | 24 | 1.0025 / 1.0000 | 1.0006 / 0.9981 | −0.0408 / −0.0450 |
| 24×2 | 48 | 1.0025 / 1.0000 | 1.0004 / 0.9979 | −0.0245 / −0.0288 |
| 6×4 | 24 | 1.0056 / 1.0025 | 1.0054 / 1.0023 | −0.0564 / −0.0617 |
| 12×4 | 48 | 1.0056 / 1.0025 | 1.0037 / 1.0006 | −0.0284 / −0.0336 |
| 24×4 | 96 | 1.0056 / 1.0025 | 1.0036 / 1.0005 | −0.0159 / −0.0211 |

The point-pin ratio is independent of the axial refinement and depends only on the through-thickness
discretisation; the pin ratio approaches 1 as the axial mesh is refined; the clamp magnitude falls
monotonically under every refinement.

> **Corrected in Stage 20 — see S20-A and register D-35.** These two sentences, and the two column
> headings of the table above, are wrong: both columns were read from lattice rows whose physical
> heights move with the through-thickness mesh ($y=d/4$ and $y=d/2$ at $NY=2$, $y=d/8$ and $y=d/4$ at
> $NY=4$). At a fixed height the point-pin ratio is $1.0000$ on every mesh, the pin ratio is
> independent of the through-thickness refinement (to within $0.0001$) and falls towards $0.998$ as
> the axial mesh is refined, and only the clamp magnitude is mesh-dependent. The table values above
> are correct *as numbers*, at the heights actually sampled; they are not a through-thickness
> comparison. The corrected evidence is `q8_height_study.py`; the sentence ``approaches 1'' is
> withdrawn. The measured values (`1.0000`, `0.998`, `−0.02` to `−0.06`)
are **preserved**, and are now described as values on one 24-element mesh: finite-mesh evidence that
the clamped alternative is not the measured configuration, **not** a converged strip solution and not
a converged clamp penalty. The `0.2 %` difference between the two pin idealizations is reproduced at
two and four elements through the thickness, which is why the *difference* is quoted while the
absolute ratios are not.

## Stage 20 — the Q8 observation height, the gauge explanation, the heated-face detector, and `eq:beamcol`

Final implementation stage. It repairs the four findings of the independent Stage 19 acceptance
audit (`independent_audit_stage19/HFF_Stage19_Independent_Acceptance_Audit.md`) and adds nothing
else, plus one build-fatal defect found while rebuilding the package (S20-E). Suite v5 (156) → v6
(163). Fingerprints regenerated deliberately, twice and each time documented: 79 entries,
`reg:D-26` changed and `reg:D-35` added in the first pass; `reg:D-32`…`reg:D-35` re-canonicalised in
the second, after their cells were rebalanced. Nothing removed, and in neither pass did a
display-equation key change.

### S20-A. Q8 observation height and the withdrawn through-thickness claim (F-1, register D-35)

**What was wrong.** The Stage 19 text said the ``absolute ratios shift with the through-thickness
discretisation'' and compared clamp values $-0.041$ ($24$ elements) and $-0.025$ ($48$) with pin
values read at a different height. Both were artefacts of the evidence script, whose two columns read
`lat[(NX,1)]` and `lat[(NX,2)]`; the lattice maps node $j$ to $y=d\,j/(2\,NY)$, so those rows sit at

| elements through the thickness | `lat[(NX,1)]` | `lat[(NX,2)]` |
|---|---|---|
| $NY=2$ | $y=d/4$ | $y=d/2$ |
| $NY=4$ | $y=d/8$ | $y=d/4$ |

The ``shift'' was therefore the difference between $y=d/2$ and $y=d/4$, not a through-thickness
effect.

**Recomputation.** `audit_stage15/q8_height_study.py` re-solves the same six meshes (independent
code: own mesh, own shape functions validated against finite differences, own banded Cholesky, patch
test on the exact stress-free field $10^{-13}$) and samples three fixed heights. At the mid-surface
$y=d/2$:

| mesh | elements | POINT | PIN | CLAMP |
|---|---|---|---|---|
| 6x2 | 12 | 1.0000 | 0.9999 | -0.0803 |
| 12x2 | 24 | 1.0000 | 0.9981 | -0.0450 |
| 24x2 | 48 | 1.0000 | 0.9979 | -0.0288 |
| 6x4 | 24 | 1.0000 | 0.9998 | -0.0660 |
| 12x4 | 48 | 1.0000 | 0.9981 | -0.0379 |
| 24x4 | 96 | 1.0000 | 0.9980 | -0.0253 |

The point-pin ratio is $1.0000$ on every mesh; the full-edge pin ratio depends only on the axial
mesh, falling from $0.9999$ to $0.9979$ ($NY=2$) and from $0.9998$ to $0.9980$ ($NY=4$), i.e. at
most $0.0001$ apart between the two through-thickness meshes at fixed $NX$; the clamp magnitude is
the only quantity that is not mesh-converged, falling from $0.045$ to $0.029$ under axial
refinement. The $0.2\%$ pin difference ($0.0019$ of $\kappa_{\mathrm{th}}L^2/8$) is unchanged between
two and four elements through the thickness.

**Corrections.** `ch04`, `ch11`, `ch02` A9 and the D-26 register row now sample at the mid-surface
and quote the clamp as $-0.045$ ($24$ elements) and $-0.029$ ($48$); the through-thickness claim is
withdrawn; D-35 records the defect, the recomputation and the dependency set. The ``not a converged
strip solution'' scope is retained and is now *better* supported: the pin values are a trend in the
axial mesh, not a converged limit, and no Richardson extrapolation is attempted.

**Regression.** `ch04 states that the Q8 ratios are sampled at the mid-surface (y = d/2)` and
`the withdrawn claim that the Q8 ratios shift with the through-thickness mesh is absent` (both
failing before the text was corrected, passing after). Probe F1a/F1b in `stage20_probe.py` remove and
reintroduce the statements respectively; both are DETECTED.

### S20-B. The gauge explanation must be in the formulation (F-2)

**What was wrong.** `the rejected pressure normalisation is still identified explicitly` counted
occurrences of a constraint pattern over every file, including `audit_appendix.tex`. Deleting the
whole argument from `ch08` (``No pressure gauge is required ... would over-determine the system ...
spurious outlet mass source'') left the suite green, satisfied by the D-30 register row that
*describes* the removed constraint. The independent audit reproduced this as A27b.

**Correction.** Two checks now require the explanation in the formulation itself:
`the formulation itself states why no pressure gauge is imposed` (at least one gauge occurrence whose
file is `chapters/ch08.tex`) and `the formulation states that no pressure gauge is required`
(the statement is present in `ch08`). The register row is no longer able to satisfy either.

**Regression.** Probe F2 deletes the argument from `ch08`; DETECTED by the first of the two checks.
The manuscript itself needed no change — the explanation was present; only the test's scope was wrong.

### S20-C. Legitimate heated-face descriptions (F-3)

**What was wrong.** The companion assertion `no prose sentence puts a non-zero solid flux datum on a
surface other than the heated face` located the heated face only through the literal sequence
``on $\Gamma_h^0$'' **after** the flux, and so rejected three correct sentences: ``... $=q^{''}$ on
the outer face $\Gamma_h^0$'', a fronted ``On $\Gamma_h^0$ the solid carries the prescribed flux
...'', and ``... is applied on the heated face''.

**Correction.** The clause that carries the flux is located with `_clause_of` (delimited by `;` and
`:`) and searched **in either direction** for the heated-face symbol or for the words
``outer/heated face, surface, wall, side''. A flux whose clause names no heated surface is still a
datum in the wrong place, and a flux whose immediate tail names $\Gamma_{if}$ is still a flux datum on
the interface, so both genuine failure modes are preserved.

**Regression.** Probe F3a-F3c (the three legitimate sentences) PASS; F3d (a solid flux datum placed
on $\Gamma_{if}$ in prose) and F3e (a double thermal datum with no surface named) are both DETECTED.
Stage 19's M8 and the Stage 18 cases that depend on the double-datum rule still detect.

### S20-D. `eq:beamcol` has a substantive check (F-4)

**What was wrong.** The two Stage 19 checks compared the *coded* solution with hard-coded
$\kappa_{\mathrm{th}}$; nothing parsed the printed equation. Changing
$w''(0)=w''(L)=-\kappa_{\mathrm{th}}$ to $-\tfrac12\kappa_{\mathrm{th}}$ therefore left the suite
green even after `--update-fingerprints` (independent audit mutation A29).

**Correction.** The printed equation is parsed: the ODE coefficients of
$D_s w''''+N_\theta^c w''=0$ and the end-curvature coefficient of $w''(0)=w''(L)=-c\,\kappa_{\mathrm{th}}$.
The derivation fixes $c=1$, because the text defines the total moment as
$M=D_s(w''+\kappa_{\mathrm{th}})$ and requires $M=0$ at the pins; no new constant is invented. The
parsed coefficients now drive the ODE residual and the boundary-condition test, so the solution is
tested against the *printed* equation rather than against literals in the test file. Two checks are
added (`eq:beamcol is the reduced beam-column equation ...`, `eq:beamcol states the zero total end
moment ...`) and two existing ones are re-pointed at the parsed coefficients.

**Regression.** Probe F4 halves the printed end curvature **with** fingerprint regeneration; DETECTED
by the end-moment check. Two Stage 18 cases improved as a side effect: A1 (moment boundary condition)
and A18 (beam-column ODE sign) were fingerprint-only and are now detected substantively, so the Stage
18 campaign reads 44/44 with **38 substantive and 6 fingerprint-only** rather than 36/8.

**Remaining limitation (accepted, class B).** The check validates the printed ODE and end conditions
against the printed closed-form solution and against the identity stated in the text; it does not
re-derive the reduced beam-column model from the three-dimensional problem, and it does not test the
physical correctness of the frozen-force assumption. The same is true of every other statement pin in
the suite: a passing suite means the manuscript still says what it is supposed to say.

### S20-E. Three over-full register rows — a hard LaTeX error (build integrity)

**What was wrong.** `chapters/audit_appendix.tex` declares its register table with four columns,
`\begin{longtable}{p{1cm}p{4.6cm}p{5.2cm}p{3.2cm}}`, but rows D-33, D-34 and D-35 each carried six
cells, and D-32 carried three. A row with more `&` than the declaration is a hard LaTeX error
(*"Extra alignment tab has been changed to \cr"*): `main.tex` would not have compiled. This was found
while rebuilding the package, not by any test — there is no TeX engine in this environment, the suite
never counted cells, and the fingerprint layer hashes cell contents without knowing how many cells
the table declares. It affects the *shipped* appendix, so it is a delivery defect, not a
documentation one.

**Why it went unseen.** Every gate this repository has is semantic: does the text still say the right
thing. None of them is syntactic. The three broken rows were introduced by three separate later
stages (D-33, D-34 in Stage 19, D-35 in Stage 20), each of which added its evidence columns in the
belief that the table had six, and the earlier rows were never recounted because nothing counted.

**Repair.** The three six-cell rows are folded into the declared four columns: the former
"resolution" and "dependencies" cells are joined into the resolution cell as
`… Dependencies: … Recalculation: …`, and the status remains the fourth cell. D-32's empty fourth
cell is filled with its actual status, `resolved (Stage 16)`, taken from the ledger entry and the
D-32 correction-log entry — no status is invented. The register still has **35 rows** and no row
lost content: every word of the three merged cells is still present, in the same row.

**Check.** New `audit_stage15/table_shape_check.py` counts the cells of every row of every
`tabular`/`longtable` in `main.tex`, `chapters/` and `figures/`, brace-aware and honouring
`\multicolumn`, against the column specification (also brace-aware, so `p{5.2cm}` counts as one
column and `@{}` counts as none). Result: **16 files, 156 rows, 0 over-full, 0 short**. One suite
check runs that scan, so the suite is 163, and probe case **E1** appends an extra `&` to the D-35 row
**with** fingerprint regeneration → **DETECTED**.

**Limitation (accepted, class B).** A cell count is not a compile. It catches over-full and short
rows, which are the common structural faults, and nothing else: unmatched braces, undefined control
sequences, missing packages, duplicate labels, bad `\ref`/`\eqref` targets and overfull boxes are
outside what this check can see, and the build itself remains NOT EXECUTED — no TeX engine exists
here (see the finalization report). The register table's *contents* are still only checked
semantically, by the per-row fingerprints and by the checks that cite them.
