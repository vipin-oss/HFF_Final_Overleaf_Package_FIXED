# Correction Plan (Priority-Ordered)

**Companion to `HFF_independent_audit_2.md`.** The research problem and its objective are retained unchanged. Each item lists the defect, the exact correction, and whether it blocks coding. Original package untouched; these are instructions for the next revision stage.

---

## P1 — Critical mathematical / numerical defects

### CP-1. Grashof, Richardson, and Brinkman values (wrong by 10³ each)
- **Where:** ch07 Table 7.1 (Gr row, Ri row, Br row); ch06 dimensionless dictionary; ch03 §3.2 (buoyancy paragraph); ch07 §7.3; ch11 limitation (2); appendix B register D-8; cell-level prose.
- **Defect:** Gr printed as 1.1×10³ while the row's own substitution evaluates to 1.07; Ri printed as 0.43 (true value Gr/Re²_Dh = 4.3×10⁻⁴); Br printed as 1.0×10⁻³ while its own substitution evaluates to 1.0×10⁻⁶. Propagation path: both wrong values were inherited from `audit/HFF_independent_audit.md` (P6 and E3) without re-derivation.
- **Correction:** Gr = 1.07 (≈1.1); Ri = 4.3×10⁻⁴; Br = 1.0×10⁻⁶. Consequences to write in: buoyancy is excludable by the ordinary Ri ≪ 1 argument; register D-8 closes as resolved; the "Ri = O(1) forbids closing the question by estimate" statements are deleted; the mandatory B-1 Boussinesq check becomes optional (retaining a dormant Boussinesq weak-form term is still recommended practice); the stable-stratification citation (Draskic) may remain as context but no longer carries the argument.
- **Blocks coding:** coupled physics claims only; not the V-A/V-B/V-C solvers.

### CP-2. Membrane-force/deflection model-form gap at the baseline operating point (F-3)
- **Where:** ch02 A4; ch04 §4.5–4.6; ch06 bound A-3; ch07 Table 7.1 rows (w_max, σ_bend, stress fraction); ch09 V-C3.
- **Defect:** the linear model omits the N_θ–w interaction that its own buckling ceiling presupposes; at the baseline N/N_cr = 0.275 the consistent von Kármán beam–column solution gives w_max = 2.19×10⁻⁴ m (1.39× linear; w/H₀ = 0.438 > A-3 bound 0.35) while midspan bending drops to σ_bend = 4.2 MPa (total ≈ 13.9 MPa, σ/σ_y ≈ 0.15).
- **Correction (choose one, recommended first):**
  1. **Adopt von Kármán kinematics for the strip** (small strain is retained: fibre strain 3.1×10⁻³, slopes 0.04 rad). Add the geometric-stiffness term ∫N_θ w′φ′ dx (approx., from the computed membrane state) to the solid weak form; buckling then emerges as a property of the model; A-3 must be re-derived against the amplified deflection and the mesh bound restated; document the amplification factor at baseline (1.39) and the exact solution `w(x) = (κ_th/μ²)[(1−cos μL)/sin μL · sin μx + cos μx − 1]` as a new V-C benchmark (V-C4) — it is analytic and closes the loop between the buckling section and the solver.
  2. **Detune the operating point** so N/N_cr ≲ 0.1 (linear theory then self-consistent): at d = 3 mm this requires q″ ≈ 1.5–2 kW/m² giving w/H₀ ≈ 0.10–0.14 (audit-detuned table available: d ∈ {4,5,6,7} mm at 5 kW/m² gives N/N_cr ∈ {0.202, 0.160, 0.132, 0.113}); accept the smaller deformation magnitude and re-examine the "first-order feedback" ambition honestly.
  3. **Keep linear and disclose:** quote the first-order amplification 1/(1−N/N_cr) ≈ 1.38 as a documented model-form correction on w_max, and re-set A-3 (e.g. linear-|w|/H₀ ≤ 0.25 so amplified ≤ 0.35). Weakest option.
- **Blocks coding:** the coupled design point; not V-A/V-B/V-C (V-C unit tests are linear and remain exactly valid; add V-C4 if option 1).

### CP-3. Strip pressure-load datum
- **Where:** ch04 §4.7 (p̄ ≈ Δp/2); ch07 Table 7.1 (w_p, Γ_p rows); ch05 B2/B6; ch08 post-processing.
- **Defect:** with the B2 datum (p = 0 at the outlet), the gauge pressure on the strip is 48–120 Pa (mean 84 Pa), not Δp/2 = 36 Pa; the incompressible pressure level on the wall is set by the datum relative to the casing environment, which the document never states.
- **Correction:** state the datum/environment assumption (natural baseline: casing vented to outlet pressure ⟹ p̄ = 84 Pa); re-quote w_p = 9.2×10⁻⁸ m and Γ_p = 1.7×10³; note the load is linearly varying, not uniform; conclusion (Γ_p ≫ 5) unchanged. In the solver, the traction transfer already handles this automatically — the correction is to the *analysis* numbers and the datum statement.
- **Blocks coding:** no (analysis consistency only).

### CP-4. Admissibility bound A-6 wording
- **Where:** ch06 §6.3 item A-6; ch07 Table 7.1 stress-fraction row.
- **Defect:** "computed wall stress within 20% of the PEEK yield stress" is ambiguous (reads as σ ≈ σ_y ± 20 %); the table applies it as a ~0.2σ_y cap.
- **Correction:** restate explicitly, e.g. "σ_max ≤ 0.2 σ_y(design cap; margin 5 against the datasheet band)" or a proper safety-factor form; record the corrected baseline value (≈ 0.15σ_y under CP-2 option 1).
- **Blocks coding:** regime guards only.

## P2 — Physical-model clarifications (no redesign)

- **CP-5.** Add one sentence justifying the wide-plate rigidity in N_cr = π²D_s/L² by plane strain (out-of-plane restraint); note the (1−ν²) reduction if antielastic bending were free. *(ch04 §4.6)*
- **CP-6.** Note the pinned-edge (full-edge u = v = 0) vs point-pin idealization: O(d) Saint-Venant end layers; add a one-time numerical sensitivity check (full-edge pins vs corner pins) at the coupled geometry L/d = 10. *(ch02 A9; ch05 B7)*
- **CP-7.** Specify V-C3's benchmark temperature as the zero-mean linear gradient (θ = Γy, θ̄ = 0) so that pinned ends carry no membrane force and the parabola is exact; or use roller ends. *(ch09 V-C3)*
- **CP-8.** Add a linear-scope clause to (5.14): superposition is exact at fixed configuration/loads; across coupled iterations it is a first-order attribution device. *(ch05 §5.3)*
- **CP-9.** Tighten the §8.2 cancellation prose ("the boundary terms enter the assembled residual with opposite signs and cancel by (5.1)–(5.2)/(5.3)–(5.4)") and show the outflow natural term in (8.1). *(ch08 §8.2)*

## P3 — Numerical-method issues

- **CP-10.** Specify the advection-stabilization strategy for the energy equation (Pe = 348; cell Péclet ≫ 2 on affordable meshes): SUPG or a demonstrated oscillation-free resolved mesh, verified through the V-B developing-profile comparison. **Blocks coupled credibility, not V-A.**
- **CP-11.** Add V-G (mesh-map isolation): one case computed both on the mapped domain and on an independently generated body-fitted mesh of the same deformed geometry; field-level agreement isolates mesh-map error.
- **CP-12.** Restore the interface-quadrature condition (identical quadrature and isoparametric geometry on both sides of the curved P2 interface; quadrature-refinement check in V-B/V-D).
- **CP-13.** Replace the increment tolerance ‖Δd‖∞ ≤ 10⁻⁸H₀ with a feasible criterion (e.g. ≤ 10⁻⁶·w_max, with achieved values reported), or demonstrate machine-precision feasibility.
- **CP-14.** Keep independent replication mandatory with pre-registered field-level metrics (deflection, Nū, Δp) and commit the platform (C-12/FEniCS). Flag the self-built-MATLAB effort as the dominant schedule risk in the limitations.
- **CP-15.** Give the fixed-point escalation a numeric trigger once CP-2 is resolved (e.g. escalate to monolithic Newton when N/N_cr exceeds half the design margin or when the geometry increment stagnates).

## P4 — Missing benchmark evidence

- **CP-16.** C-2 (V-D series): candidate located — flattened thick-channel CHT study, Int. J. Therm. Sci. (2023); extract Nu(x) vs (K, D, Pe) and construct the matched case.
- **CP-17.** C-3 (V-E): derive the 2-D slit lubrication + pinned-strip benchmark in-house as the *direct* target (V-E′); keep a Christov-class comparison as the analogous anchor (shallow 3-D, Stokes Re, clamped plate — label accordingly).
- **CP-18.** C-6: property freeze (PEEK datasheet set + β_f at fixed T_ref) before any reported number loses its "datasheet dependent" qualifier.
- **CP-19.** C-7: systematic Scopus/WoS novelty pass before any positioning sentence; the bounded claims of ch10 must additionally cite and distinguish the regenerative-cooling CHT-deformation optimization class (Applied Thermal Engineering 2026) located by this audit.
- **CP-20.** C-9: outflow sensitivity (exit length, no-backflow, datum) — unchanged, still required.

## P5 — Bibliographic corrections

- **CP-21.** Upgrade `gupta2024photothermo` to a full `@article`: Gupta, V. and Barak, M. S., "Photo-thermo-piezo-elastic waves in semiconductor medium subject to distinct two temperature models with higher order memory dependencies", HFF 34(1), 84–108 (2024), DOI 10.1108/HFF-07-2023-0380.
- **CP-22.** Close C-1: record the corroboration chain for Nu_T1 = 4.861 (Purdue Shah–London reproduction; Incropera-family tables; ASME 2025 source), retaining the primary-table practice note.
- **CP-23.** Complete hood1974 metadata at next revision; adjust the Turek–Hron description to "steady (FSI1) and transient (FSI2/3) large-displacement configurations"; verify or drop the "high Péclet number" clause for kumar2026; optionally note in `audit/HFF_independent_audit.md`-lineage documents that E13's H³ formula and P6/E3's Gr/Br values are superseded (for archive hygiene).

## P6 — Nonessential writing improvements

- **CP-24.** Fix fig_signs arrow labels (swap "σn: traction of fluid at wall" ↔ "−σn: force ON solid" per the stated convention).
- **CP-25.** Rename the conductivity ratio K (collides with bulk modulus), e.g. K_κ or R_k, consistently in ch06, Table 7.1, dictionary, and appendix A.
- **CP-26.** Minor: state that h_rigid (fully developed H1) makes θ̄ conservative given L/L_T ≈ 1.7; note the strip load's linear variation; reconcile t_f as 1.7 vs 1.8 s (both roundings of 1.74 s).

---

**Sequencing recommendation.** CP-1, CP-3, CP-4, CP-5–CP-9, CP-21–CP-26 are document edits and can be applied in one revision pass. CP-2 requires a one-page design decision (recommended: von Kármán + V-C4) before the coupled operating point is frozen. CP-10–CP-15 belong in the numerical specification before coding starts. CP-16–CP-19 gate coupled production runs, exactly as the package's own HOLD already states.
