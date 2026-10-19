# Final Audit Decision

**Auditor:** independent (mathematical modelling, CHT, fluid mechanics, thermoelasticity, numerical methods)
**Date:** 18 October 2026 · **Object:** `HFF_Scholarly_Research_Formulation` package (unchanged by this audit)
**Verdict vocabulary:** GO / CONDITIONAL GO / HOLD, each with the evidence that determines it.

---

## 1. Is the mathematical model internally consistent?

**CONDITIONAL GO.**

Consistent and independently verified: fluid equations; solid conduction and the exact steady-state argument for dropping the deformation-heating term; Duhamel–Neumann law with β = 3Kα; plane-strain closure and σ_zz identity; the mean-stress identity in both forms with three correctly paired sanity states; the wide-beam law; free thermal curvature with its d-independence; pinned bowing, membrane force, and the pinned buckling ceiling (with the catalogue reproduced exactly); pressure drop with two independent cross-checks; the 5/384 pressure-deflection coefficient; interface conditions with the single-normal convention; the monolithic weak-form cancellation (verified sign-by-sign); the steady deformed-domain formulation with correctly gated GCL; the time-scale ordering; ξ = 2.2×10⁻²; the dimensionless dictionary (except two rows, below).

Two inconsistencies prevent an unqualified GO:
1. **Gr, Ri, Br are wrong by 10³ each** (independent values 1.07, 4.3×10⁻⁴, 1.0×10⁻⁶). The errors propagate from the previous audit's own "recomputation" (P6, E3). Correcting them *strengthens* the model: buoyancy is negligible by the ordinary Ri ≪ 1 argument, register D-8 closes, and the B-1 contingency becomes optional.
2. **Linear kinematics vs the buckling physics at the baseline load:** the model omits the N_θ–w interaction that its own buckling ceiling presupposes; at N/N_cr = 0.275 the consistent von Kármán deflection is 1.39× the linear value (w/H₀ = 0.438 > the A-3 bound 0.35), while midspan bending falls to 4.2 MPa. A one-page model-form decision (von Kármán upgrade recommended, or operating-point detune, or disclosed amplification factor) is required.

Minor internal defects: A-6 wording ambiguous; strip pressure-load datum unstated (p̄ = 84 Pa, not 36 Pa, under the B2 datum — conclusion unchanged); V-C3 needs the zero-mean-gradient specification; fig_signs labels swapped; K notation collision.

## 2. Are the baseline calculations reproducible?

**YES, after three corrections — all arithmetic now anchored.**

~35 of 38 reported quantities reproduce exactly from the documented inputs (Table 7.1, dictionary, cells A1–A8): Re 50, Pr 6.97, Pe 348, f_D 1.92, Δp 72 Pa (both cross-checks), ΔT* 4.17 K, ΔT_t 60 K, κ_th 1.4 m⁻¹, w_max 1.58×10⁻⁴ m, strains, θ̄ 32.3 K, N_θ, D_s, N_cr, T̄_cr 117.5 K, catalogue, M_b 3.64, q″ ceiling ≈ 9 kW/m², ΔT_b 1.44 K, h 3231, time scales, ξ, entry lengths, steel contrast. Not reproduced: Gr (1.07 vs 1.1×10³), Ri (4.3×10⁻⁴ vs 0.43), Br (1.0×10⁻⁶ vs 1.0×10⁻³) — each a 10³ mis-transcription contradicted by its own printed substitution. Additionally re-derived here (not in the package): the datum-consistent strip load (48–120 Pa, mean 84 Pa), the exact beam–column solution and its detune tables, and the corroboration of all four Nusselt benchmark digits.

## 3. Does the bibliography support the principal claims?

**YES.**

All eight journal-article/chapter DOIs were verified at source this session (Soti, Christov, Lesoinne–Farhat, Alsabery, Saleh, Kumar, Turek–Hron, Draskic) — authors, titles, volumes, pages, years all exact. Carslaw & Jaeger's 1947 first edition is confirmed by contemporary reviews and library records. Book attributions (Bird; Boley–Weiner; Timoshenko–Goodier; Timoshenko–Gere; Shah–London) are accurate, and the benchmark values quoted from Shah–London (7.541, 8.235, 5.385, 4.861, fRe = 96 Darcy) are independently corroborated. The one entry the package declared unresolvable (gupta2024photothermo) was positively identified — title and DOI 10.1108/HFF-07-2023-0380 — and can be completed. No fabricated reference, DOI, or value was found. Open items: hood1974 page range (declared), one unverified clause ("high Péclet", kumar2026), and the two benchmark datasets (V-D series, V-E dataset) that the package itself correctly marks as unprocured.

## 4. Is the proposed numerical method adequate?

**CONDITIONAL GO.**

Adequate and verified: P2–P1 Taylor–Hood (inf–sup stable), P2 temperature/displacement, conforming interface with exact nodal transfer, no locking at ν = 0.40, pseudo-elastic mesh extension, fixed-point geometry iteration with escalation path (convergence expected to be fast — the estimated loop gain is small), direct sparse solves at the stated DOF scale, and an unusually strong per-run conservation/identity audit set. Conditions: specify energy-equation advection stabilization (Pe = 348; the largest unaddressed numerical risk); add a mesh-map isolation test; restore the interface-quadrature condition; make the increment tolerance feasible; keep independent replication mandatory with pre-registered metrics; treat the self-built MATLAB implementation as the dominant schedule risk. None of these changes the method choice.

## 5. Should the existing research direction be retained?

**YES — RETAIN (CONDITIONAL GO on the formulation).**

The research problem — thermal eigen-curvature of a pinned low-conductivity wall segment driving a closed two-way steady conjugate loop, analysed in (Σ_κ, Γ_p, M_b) with fixed-flow vs fixed-Δp contrast — survives an independent literature scan: the nearest neighbours (Kumar 2026 cavity thermo-FSI; Soti 2015 flow-deformation heat enhancement; Christov 2018 compliant-channel theory; and the 2026 regenerative-cooling study treating thermally induced deformation as a coupled CHT objective) differ in mechanism, regime, or closure. The bounded-claim discipline of Chapter 10 is correct and must be kept; that study class must be cited and distinguished. The direction is defensible and the corrections required are local, not structural.

## 6. Which components may proceed to isolated verification?

**GO:**
- **V-A** (plane Poiseuille, rigid): unconditional.
- **V-B** (rigid thermal families): all four target values now independently corroborated; close C-1; use H1/T1 as the single-wall targets exactly as planned.
- **V-C1a/b, V-C2** (constitutive sanity states): expectations independently re-verified — correct as written.
- **V-C3** (pinned bowing): with the zero-mean-gradient specification (CP-7); L/d = 25 specimen keeps shear and end-layer effects under the 1 % tolerance.
- **New V-C4** (if CP-2 option 1): beam–column benchmark — analytic, closes the buckling/deflection loop.
- **New V-E′** (2-D slit lubrication + pinned strip): derive in-house as the direct steady compliant-channel target.
- Dormant Boussinesq option (one weak-form term) may be implemented for future use.

**Not yet GO:** anything requiring the V-D/V-E external datasets (C-2/C-3), the property freeze (C-6), or the novelty pass (C-7) for claims.

## 7. Is the fully coupled implementation ready to begin?

**HOLD — not ready.** The coupled design point cannot be frozen until:

1. CP-1 applied (Gr/Ri/Br corrected; buoyancy disposition closed) — *arithmetic edit*.
2. CP-2 decided (model form: von Kármán recommended / detune / disclosed amplification) and the baseline re-evaluated against a re-derived A-3 — *design decision, one page*.
3. CP-3 applied (strip-load datum; re-quoted w_p, Γ_p) — *edit*.
4. CP-4 (A-6 restated) and CP-10 (advection-stabilization strategy) and CP-11–CP-13 (mesh-map test, quadrature, tolerance) — *specification edits before coding*.
5. C-2 and C-3 benchmark datasets procured/constructed (candidate for C-2 identified by this audit).
6. C-6 property freeze completed.
7. C-12 replication platform committed; C-7 novelty pass completed before any positioning statement (not before coding).

Evidence base for the HOLD: the deflection bound violation under consistent kinematics (0.438 vs 0.35), the three 10³-scale value errors, the unspecified strip-load datum, and the two unprocured benchmark datasets — all discovered and documented in the companion files. None of these threatens the research problem; all are correctable without redesign.

---

## Companion files

| File | Content |
|---|---|
| `HFF_independent_audit_2.md` | Full audit: inventory, equation-by-equation derivations, calculation recheck, literature verification, numerical-method and V&V audits, novelty assessment |
| `HFF_equation_audit.csv` | 37 equation/claim-level findings with derivation, dimensional check, finding, action, coding-block flag |
| `HFF_calculation_recheck.csv` | 35 calculation rechecks: reported vs independent values, formulas, inputs, discrepancy, status |
| `HFF_reference_audit.csv` | 17 package references + 2 newly identified sources: bibliographic verification, DOIs, supported claims, status |
| `HFF_correction_plan.md` | 26 corrections in priority order (P1–P6) with locations and coding-block flags |

**Integrity statement:** no original file was modified; no code was written; no replacement LaTeX was produced; no benchmark value, DOI, or result was fabricated; every discrepancy is backed by an independent derivation or a cited source, and every unresolved item names exactly the evidence required.
