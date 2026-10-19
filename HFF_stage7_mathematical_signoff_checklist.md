# HFF Stage 7 — Mathematical sign-off checklist

**Branch:** `arena/c875f9b3-hff-final-overleaf-package-fix`
**Base commit:** `dc571eb8750737052fdfb6ed8fefec85d5549ced`
**Date:** 19 October 2026
**Meaning of sign-off here:** a statement that a derivation was performed from the manuscript's printed equations and that the result is recorded. It is **not** a statement that the formulation is validated, well posed, or numerically verified. No solver exists.

---

## 1. What has been independently derived in this stage

Each item was re-derived from `ch03`/`ch05` without consulting earlier reports. The right-hand column records whether the derivation reproduced what is printed.

| # | Derived quantity | Result | Matches source? |
|---|---|---|---|
| 1 | Weak form of `eq:momentum` (`ch03:26`) | `â_f + b + c = ∫_{∂Ωf} σ_f n_f·v` | yes — `eq:weakf` |
| 2 | Identity `â_f(u,v) + b(v,p) = ∫_{Ωf} σ_f : ∇v` | holds for symmetric `σ_f`, `∇·u = 0` | yes |
| 3 | Weak form of `eq:equilibrium` (`ch03:107`) | `∫σ:ε(φ) = ∫_{∂Ωs} (σ_s n_s)·φ` | yes — `eq:weaks` with `n_s = −n` |
| 4 | Action–reaction statement | `t_f + t_s = 0 ⇒ σ_s n = σ_f n` | yes — `eq:iftraction` |
| 5 | Consequence of `eq:ifkin` for test functions | `v = 0` on `Γ_if`; fluid interface integral `≡ 0` | **contradicted** the printed cancellation claim (M4) |
| 6 | Weak form of `eq:fluidenergy` (`ch03:47`) | `ρc_p a_T + a_kf = ∫_{∂Ωf} k_f∇T_f·n_f χ` | yes — `eq:weaktf` |
| 7 | Weak form of `eq:solidenergy` (`ch03:59`) | `a_ks = ∫_{Γh} k_s∇T_s·n_out χ − ∫_{Γif} k_s∇T_s·n χ` | yes — `eq:weakts` |
| 8 | Heater sign from `q = −k∇T` and from physical direction | `+k_s∇T_s·n_out = q''` for heat supplied | yes — B6 |
| 9 | Sign and magnitude of `q_w` | `q_w = +k_f∇T_f·n > 0` on a heated wall | yes — `ch08:163` |
| 10 | Consistency of `h = q_w/(T_w−T_b)` and `Nu = 2H₀h/k_f` | positive; `2H₀ = D_h` wetted-perimeter, matches V‑B | yes |
| 11 | Thermal interface cancellation | holds for a shared interface unknown under `eq:ifflux` | yes, **conditional on T7** |
| 12 | Type of each form | `â_f, b, a_kf, a_ks` bilinear; `c, a_T` trilinear | `a_T` was mistyped (B4) → corrected |
| 13 | Dimensional consistency of every form and right-hand side | consistent (N/s for momentum; W·K/m for thermal) | yes |
| 14 | Global enthalpy balance and its arithmetic | `Q' = 150 W/m`, `ṁ'c_p = 104.5 W/(m·K)`, `ΔT_b = 1.435 K` vs `1.44 K` tabulated | yes |
| 15 | Limiting behaviour as `d, θ → 0` | reduces to the rigid-slit problems of V‑A/V‑B | yes |

**Discrepancies found by derivation:** findings M4, M6, M7, B4, C4, T8 (see §3). Of these, M4, B4, C4, M7 have been corrected in the source; M6 and T8 require a decision and remain open.

---

## 2. What remains uncertain

| Item | Why it is uncertain | What would settle it |
|---|---|---|
| **M5** — surface on which each interface integral is taken | `Γ` is used for both `Γ_if^0` and `Γ_if`; the solid is posed on the reference configuration | One sentence naming the surface per integral, plus a decision on whether the `O(ε) = O(5.4×10⁻³)` mismatch is acceptable as an A4 approximation |
| **M6** — function spaces | `V_g, V_0, Q, V_s, S_f, S_s` never defined | Supply `P‑1`; depends on settling P‑2 and T7 first |
| **M8** — geometric stiffness in the solid | `ch03` and `ch08` describe different production solids | Author decision (`P‑4`) |
| **T7** — shared interface temperature unknown | `ch08:23–24` says only that values are "transferred" | One sentence: is there one temperature unknown per interface node, or two plus a constraint? |
| **T8** — thermal data-flow direction | `ch05:70–72` and `ch08:114` (step 2 of the solution procedure) contradict each other | Author decision (`P‑2`); also determines whether the solid thermal subproblem is well posed |
| **B7** — SUPG operator and `τ` | Never written | Discretization specification (`P‑5`) |
| Well-posedness of the coupled system | Not attempted: no inf–sup analysis, no existence/uniqueness argument for the Navier–Stokes–thermoelastic system on a moving domain | A separate analysis; outside this audit |
| Convergence of the fixed-point iteration | Asserted to be fast, not proved | A contraction estimate or numerical experiment |

---

## 3. Findings requiring a domain expert's approval

These are the items where my judgement, not a mechanical check, decided the outcome. Each should be reviewed by someone other than me before it is treated as settled.

| # | Finding | My conclusion | What a reviewer must confirm |
|---|---|---|---|
| **M4** | Mechanical interface terms "cancel identically" | **Not supported.** The fluid interface integral vanishes under the no-slip Dirichlet condition; the solid carries the fluid traction as a load. | That `u = 0` on `Γ_if` is indeed a *strong* Dirichlet condition in the intended method — i.e. that no Nitsche, Lagrange-multiplier or weak no-slip variant is planned. If a weak no-slip imposition is intended, the analysis changes and the claim may be recoverable. |
| **C4** | Same claim in `ch02`, plus "exactly antisymmetric" and "without modelling error" | **Not supported**; wording corrected | Agreement that the reference/deformed surface discrepancy is properly an A4 approximation, not an identity |
| **T6/T7** | Thermal cancellation is genuine *only* with a shared temperature unknown | Conditional pass | That the monolithic assembly really does share the interface temperature DOF (this is the standard reading of "conforming mesh, no mortar", but it is not printed) |
| **T8** | `ch05` and `ch08` contradict each other on the thermal data flow | **FAIL** | Which scheme the author intends; and, if flux-only, acceptance of the pure-Neumann caveat |
| **M8** | Geometric stiffness cannot come from `eq:weaks` | **FAIL to reconcile** | Which solid model is the production one |

---

## 4. Sign-off status

| Gate | Status | Note |
|---|---|---|
| Fluid momentum weak form | **SIGNED OFF** | derived, all signs verified |
| Solid equilibrium weak form | **SIGNED OFF** | derived, sign verified independently of Stage 5 |
| Traction continuity / action–reaction | **SIGNED OFF** | derived |
| Fluid energy weak form | **SIGNED OFF** | derived, sign verified |
| Solid conduction weak form | **SIGNED OFF** | derived |
| Heater condition B6 | **SIGNED OFF** | verified two independent ways |
| `q_w`, `h`, `Nu` definition | **SIGNED OFF** | sign and normalization verified |
| Form types and definitions | **SIGNED OFF after C‑1** | `a_T` re-typed; all six forms defined |
| Dimensional consistency | **SIGNED OFF** | complete |
| Thermal interface cancellation | **SIGNED OFF, CONDITIONAL on T7** | mathematics correct; prerequisite not printed |
| **Mechanical interface cancellation** | **NOT SIGNED OFF** | claim false as printed; corrected text needs expert review (M4) |
| **Function spaces** | **NOT SIGNED OFF** | undefined (M6) |
| **Thermal data flow / subproblem well-posedness** | **NOT SIGNED OFF** | contradictory (T8) |
| **Solid model completeness (geometric stiffness)** | **NOT SIGNED OFF** | unresolved (M8) |
| **Stabilization specification** | **NOT SIGNED OFF** | `τ` undefined (B7) |
| Overall formulation well-posedness | **NOT CLAIMED** | no analysis attempted |
| Numerical verification | **NOT PERFORMED** | no code exists |
| Validation | **NOT PERFORMED** | no experimental data identified |

---

## 5. What must be resolved before Overleaf compilation

These are document-level items; none blocks producing a PDF, but each affects whether the PDF is correct.

| # | Item | Owner |
|---|---|---|
| 1 | Recompile the edited sources (no TeX engine available here, so the build is unverified) | author |
| 2 | Confirm the three edited hunks read correctly in the PDF, especially the new two-paragraph structure at `ch08:61–102` | author |
| 3 | Decide `P‑2` / T8 and `P‑4` / M8, since both change printed text | author |
| 4 | Supply `P‑1` (function spaces) once 3 is settled | author |
| 5 | Supply `P‑5` (SUPG `τ`) | author |

Items 1–2 are mechanical. Items 3–5 are content decisions that change what the manuscript asserts.

## 6. What must be resolved before solver implementation

| # | Item | Why it blocks implementation |
|---|---|---|
| 1 | M4 / C4 accepted by an independent reviewer | a wrong interface sign or a wrong justification propagates into the assembly |
| 2 | M6 function spaces defined | the discrete trial/test spaces, and hence the Dirichlet elimination, follow from them |
| 3 | T7 shared temperature unknown decided | determines whether flux continuity is natural or must be imposed |
| 4 | T8 data flow decided and made consistent | determines whether the solid thermal subproblem is well posed at all |
| 5 | M8 solid model decided | determines the solid residual to be assembled |
| 6 | B7 SUPG `τ` specified | the discrete energy equation is otherwise undefined |
| 7 | Interface quadrature-consistency audit defined | the cancellation conditions (i)–(iii) must be testable |
| 8 | Stage‑5 open items C‑2, C‑3, C‑6, C‑9, C‑12 | benchmark data, property freeze, outflow, second solver |

**Nothing in this checklist authorises coupled production computation.** Isolated verification of V‑A, V‑B and V‑C remains gated as set out in `HFF_stage5_pre_coding_checklist.md`.

---

## 7. Statement of limits

- I derived the weak forms; I did not prove the formulation well posed, convergent, or physically valid.
- The four APPLIED corrections are textual, notational and expository. No sign of any interface term was altered, because none needed to be.
- The two most consequential findings (M4, T8) are **not** fixed by anything in this patch: M4 is fixed as a statement, and T8 is not fixed at all.
- No solver code was written; no simulation was run; no numerical result is reported.
- Compilation was **not** performed and is **not** claimed.
