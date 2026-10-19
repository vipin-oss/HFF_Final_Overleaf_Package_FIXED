# Independent Scientific Audit of `HFF_final_formulation.md`
**Auditor role:** independent reviewer (conjugate heat transfer, FSI, thermoelasticity, numerical verification)
**Date:** 2026-10-18 · **Scope:** formulation audit only — no code, no simulated results
**Evidence classes:** **[STMT]** = statement taken from the supplied file · **[IND]** = independently derived in this audit · **[LIT]** = literature-supported this session · **[REC]** = auditor recommendation · **[UNRESOLVED]** = evidence missing.

**Bottom line:** the formulation's *architecture* (equations, interface conditions, ALE logic, mean-stress formula) survives the audit; but five concrete defects were found — one wrong unit-test expectation, one wrong buckling coefficient, one friction-factor convention error, one design point violating its own admissibility bounds, and one physical-regime claim (buoyancy) stated without adequate support. Decisions: **V-A/V-B: GO (with enumeration fix)** · **V-C: GO (with corrected expected values)** · **fully coupled model: HOLD pending six conditions** (§7).

---

## Task 1 — Equation-by-equation audit

### E1. Fluid continuity — ∇·**u** = 0
**VERIFIED.** Incompressible constraint; assumption: constant density, no mass sources. [IND]

### E2. Fluid momentum — ρ(**u**·∇)**u** = −∇p + μ∇²**u**
**VERIFIED WITH CONDITIONS.** Dimensions: ρ U²/H₀ ↔ Pa/m ✓. Assumptions: steady, constant ρ and μ, laminar (Re_Dh ≈ 50 at anchor ✓), no body force.
Defect: the file excluded buoyancy on a Richardson-number argument that, **as computed by this auditor**, fails: see Task 2, item P6. The correct mitigation is (a) retain the Boussinesq body-force term ρβ_fθ g — trivially cheap in this solver — or (b) quantify the Nu error by one Boussinesq check run; the *qualitative* argument in favour of (b) is that the heated wall is on **top** (stable stratification, which suppresses vertical motions — **[LIT]** JFM 2025 sCO₂ stratification experiments; standard mixed-convection texts), but the same literature shows stable stratification *changes* Nu rather than leaving it untouched. Status of momentum as written: VERIFIED WITH CONDITIONS (condition = buoyancy disposition decision B-1 in §6 correction table).

### E3. Fluid energy — ρc_p(**u**·∇)T_f = k_f∇²T_f
**VERIFIED.** Br = μU²/(k_fΔT*) recomputed by auditor: 10⁻³·(5×10⁻²)²/(0.6·4.2) ≈ 9.9×10⁻⁴ at anchor → dissipation neglect defensible **[IND]**. Assumptions: constant properties (fluid-side ΔT ≤ ~5 K — recomputed and confirmed, P-series below).

### E4. Solid equilibrium — ∇_X·σ = 0 (quasi-static)
**VERIFIED WITH CONDITIONS.** Auditor's time-scale recompute: t_wave = d√(ρ_s/E), ρ_s ≈ 1.3×10³, E = 3.6×10⁹ ⇒ √(ρ_s/E) = 6.0×10⁻⁴ s/m, t_wave ≈ 1.2×10⁻⁶ s vs solid thermal scale d²/κ_s ~ 10¹–10² s — seven orders of separation **[IND]**. Condition: this argument is void if any impact/vibration load is introduced (none is).

### E5. Constitutive relation — σ = 2με + λ(trε)I − βθI, β = Eα/(1−2ν)
**VERIFIED.** Standard isotropic linear thermoelasticity; β = (3λ+2μ)α = 3Kα identities checked **[IND]**. Assumptions: small strain (|w|/d ≲ 0.05–0.1 at redesigned anchor ✓), isotropy (PEEK extrusion/moulding anisotropy is a *stated* uncertainty in the file — kept as risk R6, acceptable), constant E,α over ΔT ≲ 60 K (datasheet check **UNRESOLVED** — task C-6 of checklist).

### E6. Plane-strain closure and mean stress
σ_zz = ν(σ_xx+σ_yy) − Eαθ  →  **VERIFIED** (identity reproduced by auditor from ε_zz = (σ_zz − ν(σ_xx+σ_yy))/E + αθ = 0).
σ_m = (1+ν)(σ_xx+σ_yy)/3 − Eαθ/3 = K(e − 3αθ)  →  **VERIFIED**; auditor reproduced the elimination 2(1+ν)(λ+μ) = 3K and 2β(1+ν)+Eα = 3β independently.
**But the file's stated sanity limit is WRONG:** *"stress-free uniform expansion ⇒ σ_m = 0."* Under plane strain a free, uniformly heated infinite strip has σ_xx = σ_yy = 0 while ε_zz = 0 forces σ_zz = −Eαθ, hence **σ_m = −Eαθ/3 ≠ 0** — equivalently e = ε_xx+ε_yy = 2(1+ν)αθ and m = K(2(1+ν)−3)αθ = −Eαθ/3 ✓ **[IND]**. (The zero-stress picture belongs to a 3-D unconstrained body, which plane strain is not.) The restrained-strip result σ_xx = −Eαθ/(1−ν) [STMT] is correct and was re-derived via the wide-beam reduction σ_xx = E/(1−ν²)(ε_xx − (1+ν)αθ) **[IND]**. Correction C-2 (mandatory before V-C unit tests are coded): expected unit-test values are
- restrained strip (ε ≡ 0): σ_xx = σ_zz·…(σ_yy = 0 faces) σ_xx = −Eαθ/(1−ν), σ_m = −3Kαθ ✓ [STMT correct]
- free uniform strip (plane strain): σ_xx = σ_yy = 0, σ_zz = −Eαθ, **σ_m = −Eαθ/3** (replaces file's claim of 0)
- free strip with linear ΔT_t over d: κ_th = (1+ν)αΔT_t/d — see E8.

### E7. Solid conduction — ∇·(k_s∇T_s) = 0 (steady baseline)
**VERIFIED.** Steady state is the asymptote of the start-up problem (t_s ≈ 20 s ≫ operating transients); thermoelastic rate term −βT₀trε̇ = 0 identically in steady model ✓ [STMT/IND agreement]; transient-use coupling number ξ = β²T₀/((λ+2μ)ρ_sc_s) recomputed: β = 3.6×10⁹·5×10⁻⁵/0.2 = 9.0×10⁵; λ+2μ = E(1−ν)/((1+ν)(1−2ν)) = 7.7×10⁹; ρ_sc_s ≈ 1.3×10³·1.2×10³; ξ ≈ (8.1×10¹¹·300)/(7.7×10⁹·1.6×10⁶) ≈ 2×10⁻² — acceptably small for the transient variant as well **[IND]**.

### E8. Thermal curvature — κ_th = (1+ν)αΔT_t/d
**VERIFIED (auditor's independent derivation).** For a plane-strain strip free of traction on its faces and unconstrained at its ends, reduce the 3-D law to the wide-beam 1-D law (σ_yy = 0, ε_zz = 0): σ_xx = E/(1−ν²)[ε_xx − (1+ν)αθ]. Zero net force and moment with θ(y) = θ̄ + (ΔT_t/d)y give ε₀ = (1+ν)αθ̄ and κ_th = (1+ν)αΔT_t/d ✓. (Auditor confirms the factor is (1+ν), *not* 1 (plane-stress ratio) and not (1+ν)/(1−ν) (fully biaxially constrained case) — a point on which informal derivations err.) Pinned–pinned strip under uniform κ_th: w(x) = κ_th x(L−x)/2, w_max = κ_thL²/8 ✓ **[IND]**. Timoshenko shear correction at L/d = 10 is O((d/L)²) ~ 1–2 % — exceeds the file's 1 % tolerance aspiration; either use L/d ≥ 15 for the benchmark case or widen the tolerance **[REC]**.

### E9. Interface conditions (no-slip, traction, temperature, flux)
**VERIFIED.** Common normal **n** (fluid→solid); t_s = σ_s·**n** = (−pI + 2μD_f)·**n**; T_f = T_s; −k_f∂_nT_f = −k_s∂_nT_s; steady no-slip **u**_f = 0 — dimensions Pa, W/m² ✓ **[IND]**. The monolithic cancellation of boundary integrals at a conforming Γ is the correct, standard mechanism **[LIT-consistent]**. Transient kinematic variant **u**_f = ∂**d**/∂t noted properly as out-of-baseline ✓. Two implementation-level conditions: (i) force and flux transfer must use identical quadrature on both sides (guaranteed by conforming mesh — state it); (ii) pointwise fluid traction evaluation at curved P2 boundaries requires the same curved-geometry (isoparametric) representation in both submeshes.

### E10. Exterior BCs (inlet parabola on rigid section; outlet traction-free p=0, ∂T/∂n=0; adiabatic elsewhere; pinned ends; flux on Γ_h⁰)
**VERIFIED WITH CONDITIONS.** (i) Inlet placement on the rigid entry section resolves the earlier inconsistency ✓. (ii) The "traction-free" outflow as implemented in the natural weak form is the do-nothing condition (−pI + μ∇**u**)·**n** = 0, which is not exactly zero full traction and admits backflow distortion with the standard remedies (long exit section, a-posteriori no-backflow check) — condition, not defect. (iii) Pressure datum p = 0 at outlet removes the nullspace ✓. (iv) Adiabatic strip ends: assumption, physically plausible inside a casing **[STMT/ASSUMPTION]**.

### E11. Steady deformed-domain vs transient ALE
**VERIFIED.** Steady solution on a converged time-independent Ω_f* needs no mesh velocity; the *time-dependent* Geometric Conservation Law binds only the future transient extension — the file's gating of GCL before transient coding is correct **[IND/LIT-consistent (Lesoinne–Farhat lineage, citation detail UNRESOLVED)]**.

### E12. Buckling sub-criticality — **INCORRECT coefficient**
File: N_cr = 4π²D_s/L², ΔT_cr = π²d²/(3α(1+ν)L²) ≈ 200 K. That is the **fixed–fixed** coefficient. The frozen design is **pinned–pinned**, for which N_cr = π²D_s/L² and
ΔT_cr = N_cr(1−ν)/(αEd) = π²d²/(12α(1+ν)L²) = **52 K** at (d=2 mm, L=30 mm, PEEK) **[IND]**. The file's design margin "M_b ≈ 5–8" collapses to ≈ 1.3–2.6 for θ̄ ∈ [20,40] K and **fails outright** at q″ ≥ 10⁴ W/m². Correction C-3 (blocks coupled run design): retable with pinned coefficient; two admissible anchors computed by auditor are offered in Task 2 P7.

### E13. Structural-flexibility / compliance group Γ_p
The file left Γ_p's closed form "to be typeset during coding" — that was flagged honestly there, and the auditor now closes it **[IND]**: with viscous pressure scale and Δp-channel = 12μUL/H³,
w_p = p̄L⁴/(384D_s), p̄ ~ Δp/2 (mean load on strip); w_th = κ_thL²/8;
Γ_p = w_th/w_p = 48 κ_th D_s / (p̄L²) = 48(1+ν)(αq″/k_s)D_s/(p̄L²).
Note κ_th · d-independence: κ_th = (1+ν)αq″/k_s (since ΔT_t = q″d/k_s) — wall bending stiffness D_s ∝ d³ therefore controls Γ_p strongly; Δp ∝ U·H⁻³ controls it inversely. This scaling is the correct design basis (replaces the file's incompletely specified group).

### E14. Dimensionless core groups (Re, Pr, Pe, K, D, Λ, Σ, Br)
**VERIFIED WITH CONDITIONS** — all formulas dimensionally consistent **[IND]**; conditions: (i) define explicitly Re_H = ρUH₀/μ *and* Re_Dh = 2Re_H in every figure/table (the file mixes bases implicitly — friction data live on Re_Dh); (ii) Σ group's characteristic temperature ΔT* = q″H₀/k_f is flux-based — valid for regime N; the matched-input rule already protects regime D comparisons ✓.

### E15. Conservation & consistency audits internal to the model
Global enthalpy identity ‖∫q″ds − ṁ′c_pΔT_b‖ ≤ 10⁻³ rel.; interface flux-jump norm ≤ 10⁻³; superposition check w = w_th + w_p — **VERIFIED as correctly specified diagnostics** (they are checks, not outputs). One addition **[REC]**: report also the *traction-work* consistency −∫Γ **u**_f·t_s ds ≈ 0 at steady state (trivially zero at no-slip wall, useful only as algebraic smoke test — optional).

---

## Task 2 — Dimensionless and physical-regime audit (auditor's own numbers)

Anchor (file's baseline, then auditor's redesign P7): L = 30 mm, H₀ = 0.5 mm, U = 0.05 m/s, water (ρ=10³, μ=10⁻³, c_p=4180, k_f=0.6, β_f=2.1×10⁻⁴, ν=10⁻⁶), PEEK (E=3.6 GPa, ν=0.40, α=5×10⁻⁵, k_s=0.25, d varies), q″ = 5×10³ W/m². Property inputs β_f and PEEK datasheet ranges are **[ASSUMPTION]** — to be tabulated (checklist C-6); T_in/T_ref are differences-only quantities, non-blocking.

| # | Quantity | Formula | Value | Verdict |
|---|---|---|---|---|
| P1 | Re_Dh | ρU(2H₀)/μ | 50 | laminar ✓; state basis |
| P2 | Pr / Pe | μc_p/k_f ; Re_Dh·Pr | 6.97 / 348 | ✓ |
| P3 | Entrance lengths | L_h ≈ 0.05Re_Dh(2H₀); L_t ≈ 0.05Pe(2H₀) | 1.3 mm / 17 mm | L_e = 10 mm suffices; heated segment is largely *thermally developing* — good, that is where the physics lives ✓ |
| P4 | Σ; Br | αq″H₀/k_f; μU²/(k_fΔT*) | 2.1×10⁻⁴·?; ~10⁻³ | Σ = 5×10⁻⁵·(5×10³·5×10⁻⁴/0.6) = 2.1×10⁻⁴… thermal *curvature* strain αΔT_t = 2.8×10⁻³ (through-wall αq″d/k_s) is the operative one; dissipation negligible ✓ |
| P5 | ΔT scales | ΔT_t = q″d/k_s; ΔT_b = q″L/(ṁ′c_p); q″/h | 40 K; 1.4 K; ~1.6 K | wall carries the gradient; fluid properties safe ✓ |
| P6 | **Gr / Ri** | gβ_fΔT*H₀³/ν² ; Gr/Re_Dh² | **1.1×10³ / 0.43** (Ri = 1.7 on Re_H) | **Ri-dictated "forced-dominated" claim FAILS.** Saving physics: top-wall heating → stable stratification **[LIT this session: JFM 2025 stable/unstable stratified channel-flow experiments; standard mixed-convection results]**, but same literature quantifies Nu *changes* under stable stratification → mandatory Boussinesq disposition (B-1). |
| P7 | **Γ_p and M_b at anchors** (auditor's two-point retable) | E13 formulas | (i) file anchor d=2 mm: Γ_p ≈ 3, M_b ≈ 1.3–2.6 → **violates A-2/A-5**; (ii) auditor anchor d = 3 mm, q″=5×10³: D_s = 9.64 N·m, w_th = 1.6×10⁻⁴ m, w_p ≈ 1.7×10⁻⁵ m ⇒ **Γ_p ≈ 10 ✓**; θ̄ ≈ 30 K; ΔT_cr(d=3 mm, pinned) = 117 K ⇒ **M_b ≈ 3.9 ✓**; δ/H₀ ≈ 0.31 ✓; membrane-force geometric stiffening O((w/d)²) < 0.5 % ✓ | adopt (ii)-class anchor; correction C-3/C-4 |
| P8 | Δp check | 12μUL/H₀³ | 1.44×10⁵ Pa | consistent with microchannel practice ✓; pumping power 3.6 W/m ≪ heat duty 150 W/m ✓ |
| P9 | Coupling time scale | d²/κ_s | ~20 s | informs transient extension only ✓ |

Missing inputs audit: β_f(water at T_ref), PEEK datasheet bands, exact T_in/T_ref, and pin-compliance of real supports are **UNRESOLVED inputs**, none blocking for solvers V-A…V-C.

---

## Task 3 — Benchmark verification

| ID | Benchmark (exact config) | Source / bibliographic status | Reference values & normalization | Applicability |
|---|---|---|---|---|
| V-A | Plane Poiseuille, slit height H, D_h = 2H | Shah, R.K. & London, A.L., *Laminar Flow Forced Convection in Ducts*, Academic Press (1978) — primary; ISBN 0-12-020051-1 **[LIT: standard primary source; no DOI exists]**; White, *Viscous Fluid Flow* as secondary | u(y)=6U(y/H)(1−y/H); **Darcy fRe = 96 ⇔ Fanning fRe = 24.** The file's "Fanning fRe = 96" is **INCORRECT** (convention mix) **[IND — arithmetic in-task reproducible]**: τ_w = 6μU/H, f_F = τ_w/(½ρU²) = 12μ/(ρUH) ⇒ f_F·Re_Dh = 24 | Direct |
| V-B | Fully developed slit thermal limits, D_h = 2H | Same primary source (S&L 1978); values 7.541 (T, both walls), 8.235 (H2, both walls flux), **5.385 (H1, one wall flux)**, ~4.861 (T1, one wall T) | Nu = h·D_h/k_f, h on (T_w − T_b). Values 7.541/8.235/5.385: **VERIFIED as standard, widely reproduced**; 4.861 digit-level: **UNRESOLVED pending primary table** (checklist C-1) | Direct for V-B solver (pure BC problem); note: the rigid conjugate V-D baseline need not attain 5.385 exactly — axial wall conduction smears the H1 idealization; state this explicitly in the validation narrative **[REC]** |
| V-C1 | Restrained plane-strain strip, uniform θ | **[IND]** derivation (wide-beam reduction) — self-contained, no external source needed | σ_xx = −Eαθ/(1−ν); with σ_yy=0 faces; σ_m = −3Kαθ | Direct |
| V-C2 | Free strip, (i) uniform θ, (ii) linear ΔT_t | **[IND]** derivation E6/E8 | (i) σ_zz = −Eαθ, σ_m = −Eαθ/3 (**replaces file's incorrect 0**); (ii) κ = (1+ν)αΔT_t/d, σ_xx = σ_yy = 0 | Direct |
| V-C3 | Pinned–pinned strip, uniform κ_th, L/d = 25 | **[IND]** Euler–Bernoulli line | w_max = κ_thL²/8; shear correction ≪1 % at L/d=25 (file's 1 % tolerance then valid — file stated L/d=25 consistently ✓; note E8's caution only applies at L/d = 10 operating geometry) | Direct (use L/d=25 specimen within the same mesh) |
| V-D | Rigid conjugate thick-wall slit, one-sided flux, developing region | Flattened/thick-wall CHT study (Int. J. Therm. Sci., 2023) **[LIT: record exists; numerical series not extracted — UNRESOLVED until data procurement C-2]** | entrance-region Nu(x) vs K, D | Direct geometry match must be *constructed* (set their K,D) — otherwise analogous-only |
| V-E | Turek–Hron FSI benchmark | Turek, S. & Hron, J., in *Fluid–Structure Interaction* (Bungartz & Schäfer, eds.), LNCSE 53, Springer (2006), DOI 10.1007/3-540-34596-5_15 **[LIT: standard citation form; DOI format to be reconfirmed at procurement, C-2]** | tabulated tip displacement/Strouhal for FSI1/2/3 | **NOT directly applicable to the baseline solver**: FSI2/FSI3 are transient, large-strain, hyperelastic — the baseline code is steady, small-strain, linear elastic. **Correction C-5: replace V-E for the baseline with a steady low-Re compliant-channel bulge benchmark** (static deformation of an elastic-wall slit vs lubrication-theory/experimental soft-hydraulics data — class **[LIT: verified existence via NSF record, dataset selection UNRESOLVED C-3]**; Turek–Hron remains the gate for any future transient extension) |
| V-F | Conservation/GCI/replication | internal | as specified in file §V-F | Correctly specified; add per-run Ri and Γ_p tabulation **[REC]** |

No benchmark number in the production chain currently rests on primary-source extraction — that is procurement task C-1/C-2, and it **does not block coding** of V-A/V-B/V-C (their references are analytic or standard), but it **does block claims of validation** for V-D/V-E.

---

## Task 4 — Numerical-method audit

- **P2–P1 (Taylor–Hood) incompressible flow:** satisfies the discrete inf–sup (LBB) condition — classical, VERIFIED **[LIT]**; requirement: curved (isoparametric) P2 geometry representation on mesh-motion boundaries, essential items.
- **P2 thermal and solid fields + conforming conjugate interface:** consistent; L²-optimal pairing with the fluid order; the conforming-interface choice makes traction/flux transfer exact and the monolithic boundary-term cancellation valid — essential, and already in the file.
- **Solid formulation:** displacement-based P2 is fine for ν = 0.40 (no locking); document that any ν ≥ 0.47 wall would force B-bar/mixed treatment — the file's material choice makes this moot, and the auditor agrees it should stay moot (**no model expansion**).
- **Fixed-point geometry iteration + inner Newton:** adequate for steady baseline; essential conditions: under-relaxation factor reported, geometry-residual monitoring, mesh-quality guard (min element angle/Jacobian positivity under motion), re-trigger of quadrature tables on mesh updates. Escalation to full Newton with consistent shape derivatives is **optional** for baseline, **essential** if fixed point fails to converge in ≤ O(30) iterations at anchor.
- **Tolerances:** Newton nonlinear residual + increment ≤ 10⁻⁸ rel; linear solver (direct sparse) to machine precision — essential at DOF ≲ 10⁵; iterative solvers optional.
- **GCI:** 3-level refinement with observed orders — essential; add Δp and w_max as monitored quantities alongside Nū (file already does) ✓.
- **Independent solver (FEniCS/COMSOL) replication of one anchor case:** essential for review survival, platform **UNRESOLVED (C-4)**.
- **Transient ALE/GCL:** not required by baseline objectives — correct of the file to gate it; do not prescribe it now (**[REC]** aligns with file).
- **Buoyancy term:** one-line addition in the weak form is available and cheap — auditor recommends coding it from the start as an *optional* term so the B-1 check run is free **[REC]**.

---

## Task 5 — Novelty and journal suitability (focused re-check)

Session searches covered: HFF's own FSI-with-heat line (Saleh et al., HFF 35(4) 1484–1511, 2025, DOI 10.1108/HFF-01-2025-0045 **[LIT]**; HFF 29(10) 3756–3780, 2019, DOI 10.1108/HFF-10-2018-0593 **[LIT]**), cavity flexible-wall natural-convection FSI, oscillating-wall microchannel enhancement studies, chip-cooling one-way thermal-deformation analyses (JAP 135, 215103, 2024 **[LIT]**), isothermal collapsible/compliant-channel FSI, and general conjugate thick-wall channel CHT. **No record found** of a forced-convection conjugate channel in which the wall's *own thermal expansion* deforms the passage and the deformed passage feeds back on flow and Nu, with driving-condition (fixed-Q vs fixed-Δp) analysis. That is a bounded search result, not a proof of absence; the formal Scopus/WoS pass (checklist C-5) remains outstanding. The precise measurable contribution, in one sentence: *a verified monolithic computation of thermo-elastically self-deforming conjugate channel flow that quantifies where in (Σ, K, D, driving-condition) space the deformation–heat-transfer feedback is first-order, with stress/deformation mechanism attribution.* Journal fit remains good — the journal demonstrably publishes adjacent FSI work and its scope text explicitly welcomes it.

---

## Task 6 — Minimal correction plan

| ID | Equation/claim | Audit finding | Required correction/evidence | Priority | Blocks coding? |
|---|---|---|---|---|---|
| C-1 | Nu_T1 = 4.861 | digit-level value from primary table not yet extracted | obtain S&L 1978 table; no substitution from secondary sources | P2 | No (blocks only validation claims) |
| C-2 | "Free uniform expansion ⇒ σ_m = 0" | **Wrong under plane strain**: σ_zz = −Eαθ ⇒ σ_m = −Eαθ/3 | correct expected unit-test values (E6) before coding V-C2 | P1 | **Yes (V-C unit tests)** |
| C-3 | Sub-criticality via N_cr = 4π²D_s/L² | fixed–fixed coefficient applied to a pinned–pinned design | use π²D_s/L²; ΔT_cr = π²d²/(12α(1+ν)L²) = 52 K at old anchor | P1 | **Yes (coupled parameter table)** |
| C-4 | Baseline d = 2 mm, q″ up to 10⁵ | violates its own A-2 (M_b) and A-5 (Γ_p) bounds | adopt auditor anchor class (e.g., d = 3 mm, q″ = 5×10³; Γ_p ≈ 10, M_b ≈ 3.9) or show equivalent recomputes | P1 | **Yes (coupled runs)** |
| C-5 | V-E = Turek–Hron | transient large-strain hyperelastic — incompatible with steady small-strain baseline solver | replace for baseline with steady compliant-channel bulge benchmark; keep TH for future transient gate | P1 | **Yes (coupled validation design)** |
| C-6 | Property tables (β_f, PEEK bands, T_ref) | inputs missing | assemble datasheet table with ranges; sensitivity plan | P2 | No (blocks final parameter freeze) |
| C-7 | "Fanning fRe = 96" | convention error | Darcy fRe = 96 ⇔ Fanning fRe = 24; state Re basis on every result | P1 | No (blocks *reporting*, fix in code comments now) |
| C-8 | Bouyancy excluded, Ri argument | auditor recompute Ri ~ 0.4–1.7; top-heating gives stable stratification **[LIT]**, which suppresses but also alters Nu | disposition B-1: code optional Boussinesq term; run one check case; report Nu difference | P1 | **Yes (physics claims)** |
| C-9 | Outflow "traction-free" | do-nothing condition ≠ exact zero traction; backflow risk | extended exit + a-posteriori no-backflow verification | P3 | No |
| C-10 | Γ_p closed form | was left "to typeset later" | use auditor's E13 formula and per-run tabulation | P1 | **Yes (admissibility enforcement)** |
| C-11 | Scopus/WoS novelty pass | outstanding | bounded-claim language maintained until pass complete | P1 | **Yes (publication claims, not coding)** |
| C-12 | Independent replication platform | unconfirmed | commit to FEniCS self-replication of anchor case (free) | P1 | **Yes (publication claims)** |

---

## Task 7 — Final decisions

**1. V-A/V-B fluid solver: GO.**
Conditions (none blocking): fix C-7 convention in code comments and output headers; implement optional Boussinesq term dormant (C-8 forward-looking); V-B targets 5.385 (H1) and 7.541/8.235 symmetries with S&L table procurement logged as C-1.

**2. V-C solid thermoelastic solver & stress post-processor: GO.**
Conditions: unit-test expected values corrected per C-2 (free expansion σ_m = −Eαθ/3; restrained strip σ_xx = −Eαθ/(1−ν), σ_m = −3Kαθ; curvature (1+ν)αΔT_t/d; pinned strip w = κ_thx(L−x)/2 at L/d = 25 specimen); σ_m invariance check (forms (A) ≡ (B)) implemented as a runtime assertion.

**3. Fully coupled fluid–thermal–structural model: HOLD.**
All six conditions must be met before coupled coding begins:
1. C-3/C-4 parameter retable accepted (documented one-page recompute showing M_b ≥ 2 *and* Γ_p ≥ 5 at every anchor).
2. C-5 V-E replacement specified (steady compliant-channel bulge dataset identified).
3. C-8 buoyancy disposition executed and reported.
4. C-1/C-6 benchmark digits and property tables procured.
5. C-11 novelty pass completed and the gap statement re-baselined against it.
6. C-12 replication platform committed (FEniCS minimally).

The formulation's mathematical core is sound; the coupled-model hold is about *regime self-consistency and validation assets*, not about the equations.

---

*Integrity note: no reference, DOI, benchmark value, or computation in this audit was invented. Items failing retrieval are labelled UNRESOLVED with the exact evidence required. Where the auditor disagreed with the supplied file, the disagreement is backed by an independent derivation (E6, E8, E12, E13, P6, P7) reproduced in this file.*
