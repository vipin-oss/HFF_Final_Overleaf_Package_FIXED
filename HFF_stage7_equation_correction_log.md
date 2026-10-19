# HFF Stage 7 — Equation and statement correction log

**Branch:** `arena/c875f9b3-hff-final-overleaf-package-fix`
**Base commit:** `dc571eb8750737052fdfb6ed8fefec85d5549ced`
**Date:** 19 October 2026

This log separates three things rigorously:

- **APPLIED** — a change made to the source in this stage, included in `HFF_stage7_source_diff.patch`.
- **PROPOSED** — a correction I consider necessary but did **not** apply, because it requires a decision that belongs to the author (a modelling or algorithmic choice), not a sign fix. These are *not* in the patch.
- **REJECTED** — considered and deliberately not done.

No material property, geometry, operating point, dimensionless group, benchmark value, tolerance or research objective was touched. No physics was changed.

---

## Summary

| # | Class | Item | Files | Status |
|---|---|---|---|---|
| C‑1 | APPLIED | `a_T` re-typed as trilinear | `ch08` | applied |
| C‑2 | APPLIED | undefined placeholder `⟨data⟩` removed from `eq:weakf` | `ch08` | applied |
| C‑3 | APPLIED | mechanical interface-cancellation paragraph rewritten | `ch08` | applied |
| C‑4 | APPLIED | `ch02` "antisymmetric … without modelling error" claim corrected | `ch02` | applied |
| P‑1 | PROPOSED | function spaces `V_g, V_0, Q, V_s, S_f, S_s` defined | `ch08` | not applied |
| P‑2 | PROPOSED | thermal data-flow contradiction (`ch05` vs `ch08`) resolved | `ch05`, `ch08` | not applied |
| P‑3 | PROPOSED | reference vs deformed surface stated for the interface integrals | `ch08` | partly covered by C‑3 |
| P‑4 | PROPOSED | geometric-stiffness status of the solid model settled | `ch03`, `ch08` | not applied |
| P‑5 | PROPOSED | SUPG operator and time-scale `τ` written out | `ch08` | not applied |
| R‑1 | REJECTED | changing any interface sign of `eq:weakf`–`eq:weakts` | — | not done |
| R‑2 | REJECTED | expanding the solid weak form to von Kármán | `ch08` | not done |
| R‑3 | REJECTED | redefining `q_w`, B6 or `Nu` | — | not done |

---

## APPLIED corrections

### C‑1 — `a_T` declared as a two-argument form but depends on `u`

**Source:** `chapters/ch08.tex`
**Locations:** definition at line 52; use in `eq:weaktf` at line 40; explanatory sentence at lines 56–60.

**Original (definition):**
```
& a_T(T,\chi)&=\int_{\Om_f}(\bu\cdot\nabla T)\,\chi\,\mathrm dx,\\
```
**Corrected:**
```
& a_T(\bu;T,\chi)&=\int_{\Om_f}(\bu\cdot\nabla T)\,\chi\,\mathrm dx,\\
```

**Original (use in `eq:weaktf`):**
```
&\rho c_p\,a_T(T_f,\chi)+a_{kf}(T_f,\chi)
```
**Corrected:**
```
&\rho c_p\,a_T(\bu;T_f,\chi)+a_{kf}(T_f,\chi)
```

**Original (sentence):**
> "In `a_T` the advecting velocity is the current state, so that the Newton linearization of the solution procedure below applies to `c` and `a_T` together."

**Corrected:**
> "The forms `â_f`, `b`, `a_kf` and `a_ks` are bilinear; `c` and `a_T` are trilinear and are written with the advecting velocity in the first (parameter) slot, that velocity being the current state. The Newton linearization of the solution procedure below therefore applies to `c` and `a_T` together."

**Justification.** The integrand `(u·∇T)χ` is homogeneous linear in `u`, in `T` and in `χ` separately; the form is trilinear and depends on the velocity unknown. Writing it as `a_T(T,χ)` contradicts both its own definition (which contains the free symbol `u`) and the sentence that groups it with the bilinear forms. The semicolon convention `(u; ·,·)` is already used for `c(u;u,v)` in the same display, so the fix uses existing notation rather than introducing new notation.

**Effect.** Notation and type only. The integrand is unchanged; no term, sign, coefficient or domain is altered. Findings affected: B4.

---

### C‑2 — undefined placeholder `⟨data⟩` in `eq:weakf`

**Source:** `chapters/ch08.tex`, `eq:weakf`, line 38.
**Original:**
```
+\int_{\Ga_{\mathrm{out}}}\sigma_f\bn\cdot\mathbf v\,\mathrm ds +\langle\text{data}\rangle,
```
**Corrected:**
```
+\int_{\Ga_{\mathrm{out}}}\sigma_f\bn\cdot\mathbf v\,\mathrm ds,
```

**Justification.** `⟨data⟩` is never defined anywhere in the manuscript. Under the stated model it is also identically zero: there are no body forces (`ch03:23`, "no volume forces"), and every non-Dirichlet part of `∂Ω_f` is already represented — `Γ_if` and `Γ_out` (`ch05:46–54`). The Dirichlet parts contribute nothing because test functions vanish there. Deleting an undefined zero placeholder is the smallest correction that leaves a complete equation.

**Effect.** Equation completeness only. The remaining terms are unchanged; the physics is unchanged.

**Alternative considered and rejected.** Defining `⟨data⟩` as the lift contribution of the non-homogeneous inlet data. Rejected because that contribution is already absorbed by choosing `u ∈ V_g` rather than `V_0`, so the definition would be redundant and could only confuse.

---

### C‑3 — the mechanical interface terms do not cancel

**Source:** `chapters/ch08.tex`, lines 61–79 of the pre-edit file (the paragraph beginning "The sign of each boundary term is fixed …"); replaced by lines 61–105 of the current file.

**Original claim (verbatim):**
> "… the fluid residual contains the interface term `−∫_Γ σ_f n·v ds` …, while the solid residual contains `+∫_Γ σ_s n·φ ds` (the solid's outward normal on `Γ` is `−n`). Under the traction equality (5.1), `σ_s n = σ_f n`, and with identical test functions on a conforming interface mesh the two terms enter the assembled residual with opposite signs and cancel identically; likewise the flux terms … The monolithic statement therefore contains *no* modelled interface quantity, which removes one class of coupling error by construction."

**Why it is wrong.** `eq:ifkin` (`ch05:9`) prescribes `u(X + d(X)) = 0` on `Γ_if` — a homogeneous Dirichlet condition. Test functions of the momentum equation therefore vanish on `Γ_if`, so

```
∫_{Γ_if} (σ_f n)·v ds ≡ 0
```

The fluid interface integral is zero, not a term with a sign. There is no second nonzero integral for the solid's `+∫(σ_s n)·φ` term to cancel against: that term is the virtual work of the fluid traction on the solid, i.e. the coupling load. "Identical test functions on a conforming interface mesh" cannot be met, because the solid test function is free on `Γ_if` (the displacement is the unknown there) while the fluid test function is constrained to zero. Mesh conformity is a precondition for cancellation at the discrete level, never its cause.

**Corrected text.** The paragraph now separates the two couplings and states, for mechanics, that the fluid term vanishes under the Dirichlet condition and that the solid carries the computed fluid traction, with the reverse coupling acting through the moving domain; for the thermal problem, that continuity is enforced by a *shared* interface unknown so one test function serves both sides and the interface flux terms do sum to zero. It retains the three discretization conditions (single normal, conforming mesh, matched quadrature) and now adds that both statements are exact only for a common surface, the reference/deformed difference being `O(ε) = O(5.4×10⁻³)`, and are not identities of the discrete system.

**Justification.** The conclusion the author draws — that no interface traction unknown is discretized — is true, but for a different reason (the traction is evaluated from `(u,p)`), and the printed reason is false. An unsupported cancellation claim is a mathematical error even when its conclusion happens to hold.

**Effect.** No equation changes. Findings affected: M4, M5 (statement of the surface), T6/T7 (clarified).

---

### C‑4 — `ch02` "exactly antisymmetric … without modelling error"

**Source:** `chapters/ch02.tex`, lines 134–137.
**Original:**
> "Fluid heat flux along `+n` carries heat out of the fluid. Using one normal on both sides of the traction equality is what renders the interface boundary terms in the weak statement of Section 8.2 exactly antisymmetric, so that they cancel in a monolithic assembly without modelling error."

**Corrected:**
> "Fluid heat flux along `+n` carries heat out of the fluid, so the flux *into* the fluid is `+k_f∇T_f·n` and is positive on the heated wall. Using one normal throughout makes the traction equality (5.1) and the flux equality (5.3) single-valued and gives the two subdomains opposite boundary-term signs. That convention is bookkeeping: it does not by itself make any interface integral cancel, and Section 8.2 states what does and does not cancel and under which conditions."

**Justification.** Two defects. (i) A common normal is necessary but not sufficient for cancellation; a shared test function is also required, and it is absent for mechanics (C‑3). (ii) "without modelling error" conflates an identity with a `O(ε)` approximation: the two boundary integrals are taken over `Γ_if^0` and `Γ_if` respectively. The sentence also now states the sign of `q_w` explicitly, which is the convention everything downstream depends on.

**Effect.** No equation changes. Finding affected: C4.

---

## PROPOSED corrections (not applied)

These are recorded so the author can decide. None is in `HFF_stage7_source_diff.patch`.

### P‑1 — define the function spaces

**Source:** `chapters/ch08.tex` line 34 (`u ∈ V_g`, `p ∈ Q`, `T_f ∈ S_f`, `d ∈ V_s`, `T_s ∈ S_s`); the test spaces are never named (`ch08:47` says only "for all test functions").
**Problem.** None of these five trial spaces is defined anywhere in the document (`ch02`, `ch03`, `ch05`, `ch08`, `appendix.tex` were searched), and no test space is written down. The fact that drives finding M4 — that admissible test functions vanish on `Γ_if` — has to be inferred from boundary row B5 together with `eq:ifkin` rather than read from a definition. (`V_0` appears in this log and in the audit as the auditor's shorthand for the fluid test space; it is not a symbol of the manuscript. The applied C‑3 wording says "admissible test functions vanish there" precisely so that the patch does not introduce a new undefined name.)
**Proposed addition (indicative, for the author to confirm):**

```
V_g = { v ∈ [H¹(Ω_f)]² : v = u_g on Γ_D^f },   V_0 = { v ∈ [H¹(Ω_f)]² : v = 0 on Γ_D^f },
Q   = L²(Ω_f),   S_f = { T ∈ H¹(Ω_f) : T = T_in on Γ_in },   S_f^0 its homogeneous counterpart,
V_s = [H¹(Ω_s^0)]²,   S_s = H¹(Ω_s^0),
Γ_D^f = Γ_in ∪ Γ_if ∪ (lower wall) ∪ (rigid upper sections).
```

**Why not applied.** A correct statement depends on resolving P‑2 (what thermal data each subproblem receives) and on whether the interface temperature is one shared unknown (T7). Writing the spaces now would prejudge both.

---

### P‑2 — contradictory thermal data flow between `ch05` and `ch08`

**Sources.**
`chapters/ch05.tex:70–72`: "the fluid subproblem receives its domain and the **interface temperature** from the solid; the solid subproblem receives the interface traction (pressure-dominated) and the **conjugate flux condition**."
`chapters/ch08.tex:91` (step 2): "transfer pressure-dominated traction and **interface temperature** requirements to the solid."

**Problem.** The two statements assign the interface temperature in opposite directions. The consequence is not cosmetic:

- solid receives **temperature** (Dirichlet on `Γ_if`) → its conduction problem is well posed;
- solid receives **flux** only → `eq:weakts` is a pure-Neumann problem, singular up to an additive constant, and feasible only if the net flux over `∂Ω_s^0` vanishes. Because the flux is computed from the fluid iterate, that compatibility is not guaranteed during iteration and the subproblem can be infeasible.

**Proposed resolution.** Adopt one of:
(i) Dirichlet–Neumann: fluid receives `T_Γ` from the solid, solid receives `q_Γ` — then add the well-posedness note that the solid Neumann problem needs a flux-balance compatibility check and a temperature datum (or must be solved monolithically); or
(ii) the reverse, with the fluid receiving the flux. Either way one sentence in `ch05` and step 2 of `ch08` must be made to agree.

**Why not applied.** This is an algorithmic choice with consequences for the solver, not a sign correction. The task forbids redesign.

---

### P‑3 — state the surface on which each interface integral is taken

**Sources:** `ch08` `eq:weaks`, `eq:weakts` write `∫_Γ …` while the solid is posed on `Ω_s^0` (`ch03:70–73`).
**Problem.** `Γ` is used for both `Γ_if^0` and `Γ_if`. The integrals cannot be over the same surface unless both are stated, and the discrepancy is `O(ε)`.
**Status.** Partly addressed by C‑3, which now states that the integrals are over `Γ_if^0` and `Γ_if` respectively and that agreement is `O(ε)`. A complete fix would rewrite the two integrals with explicit superscripts; not applied because it touches two displayed equations without changing their content.

---

### P‑4 — settle the geometric-stiffness status of the solid model

**Sources.** `chapters/ch03.tex:147–150` ("the production model is the two-dimensional system … the beam equation is used only for design estimates and benchmark construction") versus `chapters/ch08.tex`, step 3 ("solve the thermoelastic subproblem `eq:weaks`–`eq:weakts` at the reduced (frozen-force) von Kármán level … augmented by the geometric-stiffness contribution of the current membrane state").
**Problem.** `eq:weaks` with `eq:constitutive` is linear thermoelasticity with `ε = ½(∇d + ∇dᵀ)`; that strain measure contains no `½(w′)²` term, so the described geometric stiffness cannot be obtained from the displayed weak form. Two incompatible production models are described.
**Proposed resolution.** Either (i) production solid = linear 2D system, and step 3 drops the augmentation (design-level beam–column results stay in the design lane); or (ii) the geometric stiffness is retained, in which case the von Kármán strain must enter `eq:constitutive` and `eq:weaks`.
**Why not applied.** Choosing changes the governing model. Explicitly out of scope.

---

### P‑5 — write out the stabilization operator and `τ`

**Source:** `chapters/ch08.tex:19–20`.
**Problem.** "a consistent streamline-upwind (SUPG) term with the standard residual-based coefficient" — the operator and the time-scale `τ` are never defined; the element Péclet number and element size are not named. The discrete problem is therefore not fully specified. (Carried from Stage 5 as item B‑3.)
**Why not applied.** Adding a stabilization operator is a discretization specification, not a correction of an error; and the acceptance criterion ("no over/undershoot beyond 0.1% of range") is a property of monotone schemes that plain SUPG does not provide, so the choice interacts with the acceptance criteria and needs the author's decision.

---

## REJECTED changes

| # | Considered | Why rejected |
|---|---|---|
| R‑1 | Any alteration of the interface signs in `eq:weakf`, `eq:weaktf`, `eq:weaks`, `eq:weakts` | All four were independently re-derived and are correct as they stand. Changing them would introduce error. |
| R‑2 | Expanding `eq:weaks` to a von Kármán strain to match `ch08` step 3 | Would alter the governing model to make two chapters agree; the governing model is not mine to change. Recorded as P‑4. |
| R‑3 | Redefining `q_w`, B6, or `Nu` | Independently verified as correct (§3.3, §3.4 of the audit). No change justified. |
| R‑4 | Introducing a Lagrange-multiplier or Nitsche interface traction formulation to make the cancellation claim true | Would be a redesign of the numerical method. The correct remedy for a false justification is a correct justification, not a different method. |

---

## Verification of the applied patch

```
$ git diff --stat
 chapters/ch02.tex | 10 +++++---
 chapters/ch08.tex | 77 ++++++++++++++++++++++++++++++++++++++-------------------
 2 files changed, 56 insertions(+), 31 deletions(-)
```

Three hunks. All are textual or notational; no displayed equation's mathematical content, no sign of any interface term, and no numerical parameter is changed. `HFF_stage7_source_diff.patch` contains exactly these three hunks and nothing else.

**Not compiled.** No TeX engine is available in this environment, so the effect of the edits on page count and float placement is unverified. The edits are confined to running text and to argument lists of two forms; `\ref`, `\label` and package dependencies are untouched.
