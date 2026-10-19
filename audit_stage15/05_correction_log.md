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
