# Final pre-coding checklist — Stage 4 closure (evidence-based)

Supersedes `HFF_precoding_checklist_v2.md` (kept in the archive). **Status semantics:** COMPLETE
= the requirement is satisfied by an identified derivation, calculation, source, or recorded
decision that exists in the package; INCOMPLETE = partially satisfied, named action remains;
UNRESOLVED = cannot be closed with current evidence (external input required). No status refers
to solver execution — no code exists; nothing is "validated".

| # | Requirement | Current evidence | Status | Remaining action | Blocks isolated verification? | Blocks coupled implementation? |
|---|---|---|---|---|---|---|
| 1 | Weak-form mathematical consistency (fluid–solid): traction/test-function pairing, monolithic interface cancellation | ch08 §8.2 exact derivation (eqs. 8.1–8.4); opposite-sign cancellation under traction equality (5.1); verdict W-1 in `HFF_weakform_numerics_verdicts.md` | **COMPLETE** (as specification) | None at specification level; discrete survival is item 2 | No | Yes |
| 2 | Interface traction & heat-flux conditions survive discretization | Three named conditions (single-normal convention; conforming mesh; identical quadrature + same isoparametric P2 geometry) in ch08 §8.2; flux-jump norm ≤10⁻³ in per-run controls | **INCOMPLETE** | Implement conditions (i)–(iii); execute the quadrature-consistency audit in V-B/V-D | No (rigid-wall benchmarks unaffected) | **Yes** |
| 3 | Energy-equation stabilization at Pe = 348 | SUPG with residual-based coefficient specified (ch08 §8.1); acceptance = benchmark tolerance + no over/undershoot >0.1% of range + stabilized-minus-Galerkin report (ch09) | **COMPLETE** (specification) | Implement and demonstrate on V-B cases | Blocks *thermal* verification runs only | Yes |
| 4 | Baseline material properties & operating conditions frozen | ch02 property table with per-item freeze status; C-6 open; every datasheet-dependent number carries the qualifier | **INCOMPLETE** | Freeze PEEK datasheet set (E, ν, α, k_s, ρ_s, c_s, yield band) + β_f at fixed T_ref (C-6) | No (verification may run on the documented band) | **Yes** |
| 5 | Benchmark sources & normalizations | V-A analytic (fRe = 96); V-B1/B2 Shah–London Nu_T 7.541 / Nu_H2 8.235 / Nu_H1 5.385; V-C1a/b,V-C2 derived identities; V-C3(i) parabola, (ii) beam–column (4.10); V-D anchor `rahimi2024conjugate` (DOI verified); V-E class Christov; normalizations stated per row (Nu on T_w−T_b, D_h basis) | **INCOMPLETE** | C-1: digit-level T1 = 4.861 primary-table confirmation (corroboration chain recorded); C-2: extract matched (R_k, D_r, Pe) case; C-3: construct V-E data set (in-house V-E′ direct target) | V-A: no. V-B: T1 quotation needs C-1 note. V-C: no. V-D/V-E: yes | **Yes** |
| 6 | Benchmark applicability mapping | ch09 hierarchy with direct/analogous labels; Turek–Hron explicitly excluded from the steady small-strain class (description corrected, reserved for transient); two-sided Nu values barred from one-sided use | **COMPLETE** | None | No | No |
| 7 | Mesh convergence & conservation criteria | ch08 §8.4: three nested meshes, observed orders + GCI, 1% (0.5% headline) tolerance; per-run checks (i)–(v): enthalpy balance, flux-jump norm, load-case consistency, mean-stress identity, regime guards | **COMPLETE** (specification) | Implement as runtime assertions (also gate 4 of HOLD list) | Assertions only; solver dev may start | **Yes** |
| 8 | Beam–column wall model & its limitation | Targeted audit `HFF_beamcolumn_model_consistency.md`: reduced frozen-force vK classification; eq:nupdate consistency update; 2.3% conservative error at baseline; <4% in envelope; M_b = 3.64 exact; document synchronized (Revision 3) | **COMPLETE** | Optional: consistent-update check added to checklist table | No | No |
| 9 | Dimensionless-group correctness (single length basis) | `HFF_calculation_recheck_v2.csv` (29 cells, full arithmetic); Ri note (Case A/B); dictionary harmonized (Stage 4: M_b = 3.64, N_cr = 1.057×10⁵) | **COMPLETE** | None | No | No |
| 10 | Buoyancy disposition | Ri = 1.7×10⁻³ single-basis (3.4×10⁻³ D_h Case-A; 6.9×10⁻³ Case-B), D-8/D-14 closed; regime guard Ri > 10⁻² re-arms Boussinesq case | **COMPLETE** | Guard as runtime assertion | No | Guard only |
| 11 | Sign conventions & compatibility (axial force) | ch04 convention paragraph (signed N_θ < 0 in compression; positive magnitude N_θ^c in μ², ratios); eq:nupdate acts on signed resultant | **COMPLETE** | None | No | No |
| 12 | Nonlinear/fixed-point convergence specification | Tolerances feasible (10⁻⁶ w_max); numeric escalation trigger (N/N_cr > 0.5 or stagnation); stall = reported failure (ch08) | **COMPLETE** (specification) | Implement with achieved-value reporting | No | Yes |
| 13 | Code verification vs solution verification vs validation | Taxonomy applied throughout ch09: V-A–V-E = code verification (exact/benchmark); mesh triples + GCI = solution verification (ch08 §8.4); validation = comparison with physical experiment — **no experimental data set is identified in the package** | **COMPLETE** (taxonomy) / **UNRESOLVED** (validation) | Identify validation data or state explicitly that the programme is verification-only | No | Validation gap must be stated in any manuscript |
| 14 | Independent second-solver verification (C-4/C-12) | ch09 §9.5 methodology + pre-registered field metrics (deflection, Nu-bar, Δp); platform commitment open | **UNRESOLVED** | Commit platform (FEniCS default) — project-owner decision | No | **Yes** |
| 15 | Outflow-condition sensitivity (C-9) | Recorded as open check (App. B); B2 datum statement added (D-16) | **INCOMPLETE** | Exit-length/no-backflow/datum sensitivity study in V-A/V-B | No (flag results until done) | Yes |
| 16 | Originality/positioning search (C-7) | Bounded claims in ch10; systematic Scopus/WoS pass outstanding | **UNRESOLVED** | Full-document search before any strengthened positioning | No | No (manuscript-level) |
| 17 | Mesh-map error isolation (V-G) | ch09 V-G row: mapped vs independently generated body-fitted mesh, field-level comparison | **COMPLETE** (specification) | Execute once at anchor point | No | **Yes** |
| 18 | Steady→ALE relation | ch09: transient extension must state initial condition (steady solution or reported start-up); Turek–Hron reserved | **COMPLETE** (documentation) | Execute only if extension undertaken | No | No |

## Gating summary

- **Isolated verification may start now for:** V-A (unconditional), V-C (unit-test anchors as
  corrected; documented property band), V-B (with SUPG acceptance; T1 quoting note).
- **Coupled implementation remains on HOLD** until: items 2, 4, 5 (C-2, C-3), 7 (as assertions),
  14 (C-12), 15 (C-9), and 17 (V-G) close. Beginning an isolated verification solver is **not**
  approval for the coupled solver.
- **No solver has been validated**; no validation claim may be made anywhere until code,
  verification results, and (identified) experimental data exist.
