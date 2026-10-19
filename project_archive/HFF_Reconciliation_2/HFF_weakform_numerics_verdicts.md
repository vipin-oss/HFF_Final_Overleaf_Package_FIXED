# Verdicts: weak-form consistency, coupling mechanism, and numerical-specification issues

Companion to the second reconciliation pass. Each item: issue → examination → verdict (with the
document location where the resolution now lives). "Verdict" language: **RESOLVED** (written into
the document), **OPEN** (named action item retained), **REJECTED** (proposed criticism not
sustained).

## W-1. Traction term and test-function consistency in the weak form
**Issue:** the original (8.1) wrote a generic interface traction ∫ t·v on the fluid side while
the solid side carried ∫ σ_s n_s·φ; "cancellation" was asserted without showing the two terms are
the same object.
**Examination:** after integration by parts the fluid residual carries −∫_Γ σ_f n·v (n = outward
normal of Ω_f); the solid residual carries +∫_Γ σ_s n_s·φ with n_s = −n. Under the traction
equality (5.1), σ_s n = σ_f n, the two enter the assembled residual with opposite signs and
cancel identically; likewise the flux terms under (5.3). This requires (i) the single-normal
convention, (ii) a conforming interface mesh (no projection), (iii) identical quadrature and the
same isoparametric representation of the curved P2 interface on both sides — (iii) restored
explicitly (it had been lost in an earlier revision).
**Verdict: RESOLVED** — ch08 §8.2 rewritten with the exact mechanism and the three conditions;
outflow natural term shown in (8.1). The original text was defective as written; the monolithic
cancellation claim itself is correct under (i)–(iii). No automatic interface-cancellation claim
survives without those conditions.

## W-2. Kinematic coupling direction (Dirichlet data on which configuration?)
**Issue:** no-slip u(X + d(X)) = 0 couples the fluid solution at the *deformed* point to the
solid reference-coordinate field; a steady ALE statement must say which configuration the fluid
problem is posed on.
**Examination:** the formulation is steady ALE: the fluid problem is posed on the current
deformed Ω_f, the mesh map ŵ extends d into Ω_f⁰, and the fixed point iterates the geometry;
the condition is standard and consistent with the pseudo-elastic mesh-extension device.
**Verdict: RESOLVED (clarified)** — already correctly specified in ch05/ch08; the second pass
added no change beyond wording in the specification review. (Register: none needed.)

## W-3. Flux continuity vs interface quadrature
**Issue:** flux continuity −k_f ∂_n T_f = −k_s ∂_n T_s can silently fail at the discrete level
if the two sides evaluate the boundary integrals with different quadrature or different geometry
approximation of the curved P2 interface.
**Examination:** same three conditions as W-1(iii); discrete flux-jump norm already part of the
per-run controls (‖[k ∂_n T]‖/‖q″‖ ≤ 10⁻³).
**Verdict: RESOLVED** — quadrature-consistency audit made explicit and attached to V-B/V-D.

## W-4. Nonlinear convergence specification
**Issue:** (a) increment tolerance ‖Δd‖∞ ≤ 10⁻⁸ H₀ = 5×10⁻¹² m is below achievable fixed-point
accuracy — infeasible as written; (b) escalation to monolithic Newton had only a qualitative
trigger.
**Verdict: RESOLVED** — tolerance replaced by 10⁻⁶ w_max with achieved values reported; numeric
escalation trigger added (N_θ^c/N_cr > 0.5 or increment stagnation: four consecutive iterations
with < 2× reduction). Baseline (0.275) remains on the fixed-point path. Inner Newton on the
frozen-coefficient system is exact Newton; the outer coefficient update is a fixed point on the
coefficient state with its own monitor; stall at caps is reported as failure.

## W-5. Energy stabilization at Pe = 348
**Issue:** the original specification was silent on advection stabilization; Galerkin transport
at Pe = 348 (cell Péclet ≫ 2 on affordable meshes) oscillates.
**Verdict: RESOLVED** — SUPG with standard residual-based coefficient specified (ch08 §8.1);
acceptance requires benchmark reproduction within tolerance with no under/overshoot beyond 0.1%
of the applied range, and the stabilized-minus-Galerkin difference reported on the finest bounded
mesh (ch09). Stronger (variational-multiscale) stabilization deliberately not invoked at baseline
parameters; any re-arming would be a documented specification change.

## W-6. Steady formulation vs future ALE/transient extension
**Issue:** a transient extension could silently inherit steady results (initial condition,
approach to stationarity) without stating the relation.
**Verdict: RESOLVED (documentation)** — ch09 now requires the transient extension to state its
relation to the steady formulation explicitly (initial condition = converged steady solution, or
reported start-up to stationarity). The Turek–Hron benchmark remains reserved for that extension
and its description was corrected (steady FSI1 / transient FSI2-3).

## W-7. Superposition validity for the coupled solution
**Issue:** the original text called d = d_th + d_p "an algebraic identity of the linear model,
not an approximation" and demanded the implementation reproduce it — but across coupled
iterations the loads depend on d, and at the von Kármán level the geometric-stiffness term
couples the two load systems.
**Verdict: RESOLVED (scope clause)** — ch05 now states: exact only at fixed configuration and
fixed loads; across iterations exact only at the converged state; at the von Kármán level
approximate with relative error controlled by N/N_cr (≈ 28% in w_max at baseline). Mechanism
attribution is performed by *separate load-case solutions* (thermal only / traction only / both);
exact additivity is verified on a detuned case at N/N_cr ≤ 0.05 (ch08 check (iii),
ch09/ch08 load-case consistency). No superposition identity is claimed for the coupled solution
without linearity and fixed-domain justification — the fixed-domain caveat is precisely the
converged-state restriction.

## W-8. Mesh-map error isolation
**Issue:** the pseudo-elastic mesh extension introduces its own error; the verification hierarchy
did not isolate it.
**Verdict: RESOLVED** — new test V-G: one anchor case computed on the mapped domain and on an
independently generated body-fitted mesh of the same deformed geometry; field-level agreement
(deflection, Nu-bar, Δp) isolates the mesh-map contribution. Mandatory once for the coupled
solver.

## W-9. Buoyancy term in the weak form
**Issue:** original text demanded a mandatory Boussinesq check case before any constant-density
result, on the strength of Ri = 0.43 — a defective estimate.
**Verdict: RESOLVED (superseded)** — with Ri = 1.7×10⁻³ the exclusion is closed by order of
magnitude at the baseline; the Boussinesq term is kept as a dormant one-term option; the regime
guard (Ri > 10⁻²) re-arms the check; Ri is recomputed from computed fields in every reported run.
See HFF_Ri_resolution_note.md.

## W-10. Interface-cancellation claim in marketing language
**Issue:** "exact interface cancellation removes a class of coupling error by construction" could
be read as a guarantee independent of discretization.
**Verdict: RESOLVED (qualified)** — the claim is retained but now explicitly conditioned on
W-1(i)–(iii); the V-B/V-D quadrature audit and the V-G mesh-map test are the corresponding
verification obligations.

## Open items carried (not weaknesses of the written specification, but pending actions)
* C-1 primary-table T1 digits (corroboration in place).
* C-2 digit-level V-D matching against rahimi2024conjugate.
* C-3 V-E data-set construction (in-house lubrication + pinned-strip benchmark V-E′).
* C-6 property freeze (PEEK datasheet set + β_f).
* C-7 systematic originality search.
* C-9 outflow-condition sensitivity.
* C-12 second-solver platform commitment (FEniCS default).
