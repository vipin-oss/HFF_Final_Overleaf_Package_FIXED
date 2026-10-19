# HFF Stage‑5 pre-coding checklist (evidence-based)

**Supersedes:** `HFF_final_pre_coding_checklist.md` (Stage 4). The Stage‑4 file is retained unchanged in the repository as an audit record.
**Scope:** the requirements that must hold *before* numerical solver development. No code exists; **no item is a statement that a solver works.**

### Status semantics

| Status | Meaning |
|---|---|
| **COMPLETE** | Satisfied by an identified derivation, calculation, inspected source, or recorded decision that exists in the package **and** that this audit has checked. "Checked" means re-derived or inspected, not merely present. |
| **INCOMPLETE** | Partially satisfied. A *named, executable* action remains. |
| **UNRESOLVED** | Cannot be closed with current evidence; external input or a decision by the project owner is required. |

Two audit rules were applied: (i) a requirement is **not** complete because a document asserts it — the evidence column cites where it was actually checked; (ii) where a check failed, the row says so.

**Totals: 12 COMPLETE · 9 INCOMPLETE · 3 UNRESOLVED (24 rows).**

---

## A. Mathematical and discretization requirements

| # | Requirement | Evidence (checked, not merely present) | Status | Remaining action | Blocks isolated verification? | Blocks coupled implementation? |
|---|---|---|---|---|---|---|
| 1 | **Weak-form mathematical consistency** (traction/test-function pairing, interface terms) | Ch. 8 eqs. (8.1)–(8.4) re-derived in this stage against the stated single-normal convention. **Two display signs were wrong**: the solid-elasticity boundary term (`eq:weaks`) and the fluid-energy boundary term (`eq:weaktf`). Both contradicted the chapter's own integration-by-parts prose. Corrected (S1, S2). The bilinear forms `a_T`, `a_kf`, `a_ks` are **never defined** in the text. | **INCOMPLETE** | (a) independent hand re-derivation and sign-off of the corrected four equations; (b) write the three missing bilinear-form definitions; (c) add a one-line discrete-level statement that the interface terms cancel only for identical test-function traces | **Yes** — a wrong sign is a different problem, not a discretization error | **Yes** |
| 2 | **Interface traction and heat-flux conditions survive discretization** | Three named conditions (single normal; conforming interface mesh; identical quadrature and identical isoparametric P2 geometry) in Ch. 8 §8.2; flux-jump norm `≤10⁻³` in the per-run controls. Specification is adequate. | **INCOMPLETE** | Implement conditions (i)–(iii) and execute the quadrature-consistency audit in V‑B/V‑D; report the measured jump norm | No (rigid-wall benchmarks unaffected) | **Yes** |
| 3 | **Energy-equation stabilization** at `Pe = 348` | Ch. 8 §8.1 specifies SUPG with "the standard residual-based coefficient". **No formula for `τ` is given** — not implementable as written. Acceptance ("no over/undershoot > 0.1% of range") is a monotone-scheme property that plain SUPG does not guarantee. Ch. 9 adds a stabilized-minus-Galerkin report (good practice). | **INCOMPLETE** | Specify `τ` explicitly (e.g. `τ = (h/2|u|)(coth Pe_h − 1/Pe_h)`) and its element Péclet definition; either add a discontinuity-capturing term or restate the overshoot criterion as a measured and reported quantity | Thermal runs only (V‑B) | **Yes** |
| 4 | **Material properties and their sources** (C‑6) | Ch. 2 table: water at near-ambient; PEEK `E=3.6 GPa, ν=0.40, α=5×10⁻⁵ K⁻¹, k_s=0.25 W m⁻¹K⁻¹, ρ_s=1300, c_s=1100`, all marked "freeze pending"; `β_f=2.1×10⁻⁴ K⁻¹` freeze pending. No datasheet is cited. | **INCOMPLETE** | Freeze the PEEK datasheet set and `β_f` at a fixed `T_ref`; **state the temperature at which `E, α, k_s` are evaluated** and justify constant properties across the computed `ΔT_t = 60 K` through-wall drop | No (verification may run on the documented band) | **Yes** |
| 5 | **Baseline geometry and operating conditions frozen** | Ch. 2 Table 2.1 fixes `H₀, L, L_e, L_o, d, U, q″`; **`T_in` and `T_ref` are explicitly "to be fixed at data freeze"**. All other baseline numbers are reproducible from the fixed set (spot-checked: `Re=50`, `Pe=348`, `Δp=72 Pa`, `ΔT_b=1.44 K`, `ΔT_t=60 K`, `w_p=9.2×10⁻⁸ m`, `N_cr=1.06×10⁵ N/m`). | **INCOMPLETE** | Fix `T_in`, `T_ref` (they set `β_f`, all properties and the mean wall temperature 32 K); confirm the PEEK operating temperature stays well below `T_g` at the 60 K drop | No | **Yes** |
| 6 | **Fluid and solid boundary conditions specified** | Ch. 5 Table 5.1: B1 inlet (parabolic + `T_in`), B2 do-nothing outflow with datum, B3 adiabatic rigid floor, B4 rigid casing, B6/B9 thermal load variants, B7 pinned ends, B8 insulated remaining faces. **B6 sign was wrong for a heater** and is corrected (S3). | **COMPLETE** after S3 | None; B2 is flagged under item 19 | No | No |
| 7 | **Interface traction and heat-flux conditions** | Ch. 5 eqs. (5.1)–(5.4): no-slip, `σ_s n = σ_f n`, `T_f = T_s`, `−k_f∇T_f·n = −k_s∇T_s·n`, all with one normal `n` (fluid→solid). Derivation of the traction balance rewritten correctly (S4). | **COMPLETE** after S4 | None | No | No |
| 8 | **Benchmark definitions and normalization** | V‑A closed form and `f_D Re=96` re-derived (consistent with `D_h=2H₀`, Darcy `f_D`). V‑B1 (7.541, 8.235) and `Nu_H1=5.385` were verified in earlier stages and were not re-inspected now. `Nu_T1=4.861` **re-confirmed this stage against Shah & London Table 43**; `D_h = 2H₀` wetted-perimeter basis and `T_w−T_b` normalization match Ch. 8. **But V‑B2 states neither the adiabatic companion wall nor an evaluation station/duct length**; T1 converges slowly in `x*`. V‑C targets are closed-form (derived in the prior reconciliation audit). V‑D and V‑E data sets not constructed. | **INCOMPLETE** | Write the V‑B2 test definition (one wall isothermal, other adiabatic; duct length or `x*` station; local vs perimeter mean; tolerance). Extract V‑D matching points (C‑2). Construct V‑E data set (C‑3) | No for V‑A/V‑C; V‑B needs the definition sentence only | **Yes** |
| 9 | **Benchmark applicability mapping** | Ch. 9 labels direct/analogous; Turek–Hron explicitly excluded from the steady small-strain class; two-sided `Nu` barred from one-sided use. Verified consistent with the source families. | **COMPLETE** | None | No | No |
| 10 | **Mesh convergence and conservation criteria** | Ch. 8 §8.4: three nested meshes, observed order + GCI, 1% (0.5% headline) tolerance; five per-run checks (enthalpy balance, flux-jump norm, load-case consistency, mean-stress identity, regime guards). | **COMPLETE** (specification) | Implement as runtime assertions, including the GCI safety factor and the definition of the flux-jump norm denominator | Assertions only | **Yes** |
| 11 | **Beam–column wall model and its limitation** | Targeted audit record: reduced frozen-force von Kármán classification, consistency update, 2.3% conservative error at baseline, <4% in envelope, `M_b = 3.64` exact. Document synchronized. | **COMPLETE** | None | No | No |
| 12 | **Dimensionless-group correctness (single length basis)** | 29 arithmetic cells re-checked; re-derived `Re, Pr, Pe, Ri, Gr, Br, Γ_p, M_b` from the stated inputs — all consistent on the single `H₀` basis with the stated `D_h` conversions. | **COMPLETE** | None | No | No |
| 13 | **Buoyancy disposition** | `Ri = 1.7×10⁻³` (single `H₀` basis); re-derived from `gβΔT*H₀/U²` — consistent. Guard `Ri > 10⁻²` re-arms Boussinesq. | **COMPLETE** | Guard as runtime assertion | No | Guard only |
| 14 | **Sign conventions and compatibility (axial force)** | Ch. 2 §signs: single normal fluid→solid, pressure positive in compression, solid tension positive, `w = −d₂`. Re-derived the interface symmetry from these conventions. **Inconsistencies found in Ch. 5 and Ch. 8** (normal definitions, B6, `q_w`) and corrected (S1–S6). | **INCOMPLETE** | One independent hand re-derivation of the whole sign chain (equations → weak form → post-processing) signed and filed | **Yes** | **Yes** |
| 15 | **Nonlinear/fixed-point convergence specification** | Ch. 8: increment tolerance `10⁻⁶ w_max` (feasible), escalation trigger `N_θ^c/N_cr > 0.5` or stagnation, stall reported as failure; achieved values reported per run. | **COMPLETE** (specification) | Implement and report achieved increments; do not report "converged" without the achieved value | No | **Yes** |
| 16 | **Code verification vs solution verification vs validation** | Taxonomy applied consistently in Ch. 9: V‑A…V‑E = code verification; mesh triples + GCI = solution verification; validation = experiment. **No experimental data set is identified anywhere in the package.** | **COMPLETE** (taxonomy) | Manuscript must state that the programme is verification-only unless data are identified | No | No |
| 17 | **Validation data set** | None identified. | **UNRESOLVED** | Identify an experimental data set (or state explicitly that no validation claim is made) | No | Requires a stated gap in any manuscript |
| 18 | **Independent second-solver verification** (C‑12) | Ch. 9 §9.5 methodology and pre-registered field metrics (deflection, `Nū`, `Δp`) exist; platform **not** committed. | **UNRESOLVED** | Project-owner decision: commit FEniCS (or other) and record the version | No | **Yes** |
| 19 | **Outflow-condition sensitivity** (C‑9) | Recorded as an open check; exit-length/no-backflow/datum study not done; the datum also fixes the wall-load reference (A9). | **INCOMPLETE** | Run the exit-length (e.g. `L_o` ×1, ×2, ×4), backflow and datum sensitivity; report `Δp` and `w_max` sensitivity | No (flag all results until done) | **Yes** |
| 20 | **Originality/positioning search** (C‑7) | Bounded claims in Ch. 10; systematic Scopus/WoS pass outstanding. | **UNRESOLVED** | Full-document search before any strengthened positioning claim | No | No (manuscript-level) |
| 21 | **Mesh-map error isolation** (V‑G) | Ch. 9 V‑G: mapped vs independently generated body-fitted mesh, field-level comparison. | **COMPLETE** (specification) | Execute once at the anchor point | No | **Yes** |
| 22 | **Steady → ALE relation** | Ch. 9: transient extension must state the initial condition; Turek–Hron reserved for the transient extension. | **COMPLETE** (documentation) | Execute only if the extension is undertaken | No | No |
| 23 | **Reference-record integrity** | All 18 `.bib` entries checked against Crossref/publisher where a DOI exists. **Three Stage‑4 CSV records were wrong** (Soti DOI, Lesoinne pages, Christov pages) and one `.bib` given name was unsupported (Rahimimotlagh); Appendix B contradicted the reference table on Gupta. All corrected in this stage's records and source. | **INCOMPLETE** | Human check of a printed copy of Shah & London for the Table 43 page number; no other bibliographic action | No | No |
| 24 | **Post-processing definitions** (`Nu`, stress) | Ch. 8 defines `Nu = 2H₀h/k_f`, `h = q_w/(T_w−T_b)`; **`q_w` had the wrong sign** (flux out of the fluid), which would have made `Nu` negative on a heated wall; corrected (S6). Solid export of complete Cauchy components with mean-stress identity as an assertion is adequate. | **COMPLETE** after S6 | None; confirm the same definition is used in the benchmark comparison table | No | No |

---

## B. Gating summary

### Isolated verification may start now

| Component | Gate | Conditions attached |
|---|---|---|
| **V‑A fluid solver** | Unconditional | Uses the corrected post-processing sign once `Nu` is computed; `f_D Re = 96` and the profile are exact |
| **V‑C solid thermoelastic solver** | Conditional | Items 1 and 14 signed off; run on the documented property band pending C‑6 |
| **V‑B rigid thermal solver** | Conditional | Item 3 (`τ`) and item 8 (V‑B2 evaluation station + adiabatic companion wall) written down first |

### Coupled implementation remains on HOLD

Required before any coupled production run: **1, 2, 3, 4, 5, 8 (incl. C‑2, C‑3), 10 (as assertions), 14, 18, 19, 21.**

### Not validated

- No solver has been written, compiled, run, or compared with anything.
- Approving an isolated verification solver is **not** approval for the coupled solver.
- Confirming `Nu_T1 = 4.861` is a benchmark fact, not evidence that the thermoelastic channel model is physically correct.

---

## C. What changed relative to the Stage‑4 checklist

| Stage‑4 row | Stage‑4 status | Stage‑5 status | Reason |
|---|---|---|---|
| 1 Weak-form consistency | COMPLETE | **INCOMPLETE** | two boundary-term signs wrong; three bilinear forms undefined |
| 3 SUPG | COMPLETE (spec) | **INCOMPLETE** | no `τ` formula; overshoot criterion not guaranteed by SUPG |
| 4 Properties | INCOMPLETE | INCOMPLETE | scope widened: evaluation temperature across a 60 K drop |
| 5 Benchmarks | INCOMPLETE | INCOMPLETE | C‑1 closed; V‑B2 definition and C‑2/C‑3 still open |
| 11 Sign conventions | COMPLETE | **INCOMPLETE** | sign errors found in Ch. 5/Ch. 8; corrections need independent sign-off |
| 13 Verification taxonomy | COMPLETE / UNRESOLVED (validation) | split into rows 16 (COMPLETE) and 17 (UNRESOLVED) | removes a mixed-status row |
| — | — | new row 23 (reference integrity) | three erroneous audit records found |
| — | — | new row 24 (post-processing) | `q_w` sign error found |

No status was upgraded without new evidence, and no numerical parameter was changed to obtain a status.
