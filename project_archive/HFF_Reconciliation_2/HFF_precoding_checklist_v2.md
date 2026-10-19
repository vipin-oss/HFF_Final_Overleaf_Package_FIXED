# Revised pre-coding checklist (v2, after the second reconciliation pass)

Supersedes the checklist in `audit/HFF_pre_coding_checklist.md`. Items are grouped as gates.
Nothing here authorises coupled production computations; the HOLD conditions are restated in the
last section.

## G0 — Document state (closed by this revision)

- [x] All dimensionless groups carry full formula / inputs / units / substitution and a stated
      length basis (Ri basis-explicit, eq. 6.3; dictionary rows for Re_H0 and both Ri conventions).
- [x] Wall model carried to the pinned beam–column form at finite membrane force; buckling
      threshold and deflection law are limits of one relation (eqs. 4.9–4.11; cell A9).
- [x] Hydraulic load datum stated (outlet B2 + vented casing A9; p̄ = 84 Pa; linear variation).
- [x] A-6 recast as σ_max ≤ 0.2 σ_y; A-3 restated at the beam–column level (mesh bound 0.5).
- [x] Weak form: traction/flux cancellation mechanism exact with the three discretization
      conditions; outflow natural term shown; quadrature-consistency audit attached to V-B/V-D.
- [x] Superposition replaced by load-case attribution with a detuned additivity check.
- [x] Stabilization (SUPG) specified with benchmark acceptance criteria; V-G mesh-map test added.
- [x] Fixed-point tolerances feasible (10⁻⁶ w_max); numeric escalation trigger defined.
- [x] Symbol collisions resolved (R_k, D_r, K_T, C_lump); figure labels consistent with (5.1).
- [x] Bibliography: 18 entries, all verified at source; no invented fields; Gupta record complete.

## G1 — May proceed now (isolated solver verification)

1. **V-A** rigid hydrodynamic solver — no conditions.
2. **V-B** rigid conjugate thermal solver — run at baseline Pe = 348 with SUPG; acceptance per
   ch09 (benchmark tolerance + oscillation criteria + stabilized-minus-Galerkin report). T1
   quotations (4.861) must cite the corroboration status until C-1 closes.
3. **V-C** thermoelastic solver — the wall model is the reduced (frozen-force) von Kármán
   beam–column relation (audit verdict: justified with explicit limitation; ≤4% one-sided error
   inside the admissible envelope N/N_cr ≤ 0.33; escalation to the consistent update beyond
   N/N_cr ≈ 0.5 is mandatory per ch08). — unit tests against: V-C1a/b (mean-stress identities as
   corrected, D-2/D-12), V-C2 (curvature to 0.1%), V-C3 (i) zero-force parabola 1% and (ii)
   beam–column target (eq. 4.10, amplification 1.39 at μL = 1.65).
4. Any verification run must print: property set + freeze status, datum statement, regime-guard
   values recomputed from fields.

## G2 — Conditions before the coupled solver is coded against the frozen design

1. **C-2**: digit-level extraction of the matched V-D case from rahimi2024conjugate
   (matched R_k, D_r, Re/Pe; report developing Nu(x)).
2. **C-3**: V-E benchmark data set constructed (in-house 2-D lubrication + pinned-strip V-E′ as
   the direct target; Christov-class comparison labelled analogous).
3. **C-6**: property freeze (PEEK datasheet set: E, ν, α, k_s, ρ_s, c_s, yield band; β_f at fixed
   T_ref). Until then every datasheet-dependent number carries its qualifier.
4. Regime guards A-1…A-6 implemented as runtime assertions (recomputed from computed fields,
   including Ri and N/N_cr).
5. Platform commitment for the second solver (C-12; FEniCS default) recorded.

## G3 — HOLD release conditions for coupled production computations (unchanged in substance)

Coupled computations are authorised only when ALL of:
- G2 items 1–5 closed;
- V-D evidence obtained and accepted; V-E data set constructed; V-G executed at the anchor point;
- replication (C-4/FEniCS) of one anchor operating point agreed at field level;
- buoyancy regime guard armed (re-opens a Boussinesq case at Ri > 10⁻²).

## G4 — Positioning (manuscript-level)

- C-7 systematic Scopus/WoS pass before any positioning sentence is strengthened; the bounded
  claims of ch10 stand as written until then.

## Verification-acceptance quick table

| Test | Quantity | Tolerance |
|---|---|---|
| V-A | friction f_D Re = 96; profile | 10⁻⁴ rel.; machine-precision L² |
| V-B1/B2 | Nu_T 7.541; Nu_H2 8.235; Nu_H1 5.385; Nu_T1 4.861 (corroborated) | benchmark tolerance + no over/undershoot > 0.1% of range at Pe = 348 |
| V-C2 | curvature κ = (1+ν)αΔT_t/d | 0.1% |
| V-C3(i) | w_max = κ_th L²/8 | 1% |
| V-C3(ii) | beam–column eq. (4.10), amp 1.39 at μL = 1.65 (frozen force) | 1% |
| (optional) | consistent-force update eq. (eq:nupdate): w_max 0.428 H₀ at baseline | 1% of adopted |
| V-D | developing Nu(x) vs rahimi2024conjugate at matched (R_k, D_r, Pe) | per matched-case sheet (C-2) |
| V-G | mapped vs body-fitted mesh fields | field-level agreement report |
| V-F | flux-jump norm ≤ 10⁻³; enthalpy balance ≤ 10⁻³ Q′; mean-stress identity | mandatory every run |
