# HFF Stage 7 — Independent mathematical audit of the coupled weak formulation

**Repository:** `vipin-oss/HFF_Final_Overleaf_Package_FIXED`
**Branch:** `arena/c875f9b3-hff-final-overleaf-package-fix`
**Commit reviewed:** `dc571eb8750737052fdfb6ed8fefec85d5549ced` (working tree clean at review start)
**Date:** 19 October 2026
**Nature of task:** independent derivation from the manuscript's own equations. No solver code was written and no simulation was run.

---

## 0. Scope, method, and evidence labels

Every derivation below starts from the strong forms actually printed in the manuscript:

| Quantity | Source |
|---|---|
| Fluid momentum | `chapters/ch03.tex:26` — eq. `eq:momentum` |
| Fluid continuity | `chapters/ch03.tex:15` — eq. `eq:continuity` |
| Fluid energy | `chapters/ch03.tex:47` — eq. `eq:fluidenergy` |
| Solid conduction | `chapters/ch03.tex:59` — eq. `eq:solidenergy` |
| Solid constitutive | `chapters/ch03.tex:79–80` — eq. `eq:constitutive` |
| Solid equilibrium | `chapters/ch03.tex:107` — eq. `eq:equilibrium` |
| Interface conditions | `chapters/ch05.tex:9–12` — eqs. `eq:ifkin`–`eq:ifflux` |
| Boundary data | `chapters/ch05.tex:46–54` — Table `tab:bcs`, rows B1–B9 |
| Normal convention | `chapters/ch02.tex:127–137` |
| Weak statement | `chapters/ch08.tex:33–79` — eqs. `eq:weakf`–`eq:weakts` |

I did not consult the Stage‑5/Stage‑6 reports while deriving. Where my result agrees with an earlier correction, the agreement is a coincidence of two derivations, not evidence that the earlier one was right.

**Labels.** PASS = the manuscript's statement is correct as printed. FAIL = a statement is wrong, or a symbol needed to make it well posed is undefined. UNRESOLVED = the manuscript does not contain enough information to decide, and I state exactly what is missing.

**Notation used only in this audit:** `n_f` = outward normal of `Ω_f`; `n_s` = outward normal of `Ω_s`; the manuscript's single interface normal `n` points from fluid into solid, so `n_f = n` and `n_s = −n`. `t_f = σ_f n_f`, `t_s = σ_s n_s`.

**Finding count: 29 — 19 PASS, 6 FAIL, 4 UNRESOLVED.**

---

## Task 2 — Independent derivation of the mechanical weak forms

### 2.1 Fluid momentum

**Governing equation** (`ch03:26`): `ρ(u·∇)u = −∇p + μ∇²u` in `Ω_f`, with `σ_f = −pI + 2μD(u)` so that the equation is `ρ(u·∇)u = ∇·σ_f`.

**Domain / spaces.** `Ω_f` is the *deformed* steady domain (`ch03:19–20`, `ch03:152–162`). `u ∈ V_g` (`ch08:34`); the test space is not named in the manuscript — it says only "for all test functions" (`ch08:47`). Throughout this audit I write `V_0` for that test space; the name is mine, introduced for the discussion, and is *not* a symbol the document defines (finding M6).

**Boundary partition** (from `ch05:46–54`): `Γ_in` — Dirichlet velocity (B1); lower wall and rigid upper sections — Dirichlet `u = 0` (B3, B4); `Γ_if` — Dirichlet `u = 0` (B5 with `eq:ifkin`); `Γ_out` — natural (B2). Body forces are absent (`ch03:23`).

**Derivation.** Multiply by `v` and integrate over `Ω_f`:

```
∫_{Ωf} ρ (u·∇)u·v dx = −∫_{Ωf} ∇p·v dx + μ ∫_{Ωf} ∇²u·v dx
```

Using `∇·(p v) = (∇p)·v + p ∇·v`:

```
−∫_{Ωf} ∇p·v dx = −∫_{∂Ωf} p n_f·v ds + ∫_{Ωf} p ∇·v dx
```

Using `(∇·σ_f)·v = ∇·(σ_f v) − σ_f : ∇v`, with `∇v = D(v) + W(v)` and `σ_f` symmetric so `σ_f : W(v) = 0`:

```
∫_{Ωf} ρ(u·∇)u·v dx = −2μ∫_{Ωf} D(u):D(v) dx + 2μ∫_{∂Ωf} (D(u) n_f)·v ds
                      + ∫_{Ωf} p ∇·v dx − ∫_{∂Ωf} p n_f·v ds
```

Collecting, with `â_f(u,v) = 2μ∫D(u):D(v)`, `b(v,p) = −∫ p ∇·v`, `c(u;u,v) = ρ∫(u·∇u)·v`:

```
â_f(u,v) + b(v,p) + c(u;u,v) = ∫_{∂Ωf} (σ_f n_f)·v ds
```

Restricting to the non-Dirichlet boundary and splitting `∂Ω_f`:

```
â_f(u,v) + b(v,p) + c(u;u,v) = ∫_{Γ_if} (σ_f n)·v ds + ∫_{Γ_out} (σ_f n)·v ds + ∫_{Γ_if}(...)?
```

The Dirichlet parts (`Γ_in`, B3, B4) contribute nothing because `v = 0` there. This reproduces `eq:weakf` (`ch08:36–39`) exactly, and it confirms the sign of the outflow term.

> **Finding M1 — PASS.** `eq:weakf` is the correct weak form of `eq:momentum` with `σ_f = −pI + 2μD`: the three left-hand terms reproduce `∫σ_f:∇v` exactly, and the boundary term carries `+σ_f n·v` (a residual written as LHS − RHS contains `−∫σ_f n·v`, as the text states).

**Correction applied in this stage:** the placeholder `+⟨data⟩` in `eq:weakf` (`ch08:38` of the pre-edit file) was an undefined symbol. With no body forces (`ch03:23`) and every non-Dirichlet boundary already listed, it contributes nothing. It has been removed.

> **Finding M7 — FAIL.** `⟨data⟩` in `eq:weakf` was undefined. Corrected by deletion; see correction log C‑2.

### 2.2 Solid equilibrium

**Governing equation** (`ch03:107`): `∇·σ = 0` in `Ω_s^0`; constitutive `eq:constitutive` (`ch03:79–80`), `ε = ½(∇d + ∇dᵀ)`, `σ = 2μ_L ε + λ(tr ε)I − βθI`.

**Space.** `d ∈ V_s`, test functions `φ`.

**Derivation.** With `σ` symmetric, `σ : ∇φ = σ : ε(φ)`:

```
0 = ∫_{Ωs0} (∇·σ)·φ dX
  = ∫_{Ωs0} ∇·(σ φ) dX − ∫_{Ωs0} σ : ε(φ) dX
  = ∫_{∂Ωs0} (σ n_s)·φ dS − ∫_{Ωs0} σ : ε(φ) dX
```

hence

```
∫_{Ωs0} σ(d,θ) : ε(φ) dX = ∫_{∂Ωs0} (σ_s n_s)·φ dS
```

On `Γ_if` the solid's outward normal is `n_s = −n`, so the interface contribution is `−∫_{Γ_if} (σ_s n)·φ ds`. On the pinned ends `φ = 0` (B7); on the remaining faces the traction is zero (B8). Therefore

```
∫_{Ωs0} σ(d,θ) : ε(φ) dX = −∫_{Γ_if} (σ_s n)·φ ds
```

> **Finding M2 — PASS.** `eq:weaks` (`ch08:42–43`) with the minus sign is exactly the result of integrating `eq:equilibrium` by parts under `n_s = −n`. The Stage‑5 correction to this sign is therefore independently confirmed: the earlier `+` sign would have implied `σ_s n_s = +σ_s n`, i.e. a fluid normal used as the solid's outward normal, and a pressure load of the wrong sign.

### 2.3 Traction continuity and action–reaction

The manuscript's `eq:iftraction` (`ch05:10`) reads `σ_s n = (−pI + 2μD(u)) n`, i.e. `σ_s n = σ_f n`.

Independent check: the traction the surroundings exert on a body with outward normal `n_b` is `t = σ n_b`. For the fluid, `t_f = σ_f n_f = σ_f n` (force of solid on fluid). For the solid, `t_s = σ_s n_s = −σ_s n` (force of fluid on solid). Action–reaction requires `t_f + t_s = 0`, i.e. `σ_f n − σ_s n = 0`, i.e. `σ_s n = σ_f n`.

> **Finding M3 — PASS.** `eq:iftraction` is the correct statement of action–reaction under the single-normal convention, and the derivation paragraph at `ch05:16–20` (as corrected in Stage 5) is now internally consistent: it writes `σ⁽ˢ⁾·n_s + σ⁽ᶠ⁾·n_f = 0` with `n_s = −n`, `n_f = n`, which reduces correctly to `eq:iftraction`.

### 2.4 The interface-cancellation claim — the central question

The manuscript states (`ch08:63–72`, before this stage):

> "the fluid residual contains the interface term `−∫_Γ σ_f n·v ds` … while the solid residual contains `+∫_Γ σ_s n·φ ds` … Under the traction equality (5.1), `σ_s n = σ_f n`, and with identical test functions on a conforming interface mesh the two terms enter the assembled residual with opposite signs and cancel identically; likewise the flux terms … The monolithic statement therefore contains *no* modelled interface quantity, which removes one class of coupling error by construction."

I test each clause separately.

**(a) Are the two terms individually correct?** Yes — see M2 and the residual form of M1.

**(b) Are the test-function traces identical?** **No, and they cannot be in the steady formulation.** `eq:ifkin` (`ch05:9`) prescribes `u(X + d(X)) = 0` on `Γ_if`. That is a homogeneous Dirichlet condition. The test functions belonging to the momentum equation therefore lie in `V_0`, and `v = 0` on `Γ_if`. The solid test function `φ` is *not* constrained on `Γ_if`, because `d` is the unknown there. Hence `v ≠ φ` on the interface: one is zero and the other is a free test function.

**(c) Consequence.** With `v = 0` on `Γ_if`,

```
∫_{Γ_if} (σ_f n)·v ds ≡ 0
```

so the fluid residual does **not** contain a nonzero interface integral. There is nothing for the solid's `+∫(σ_s n)·φ` term to cancel against. The solid term is not a cancelling partner; it is the virtual work of the fluid traction acting on the solid, and it is the coupling load that must be assembled.

**(d) Does the physics still hold?** Yes, and the conclusion the author wants is still true, for a different reason. The interface traction is not discretized as an independent unknown because it is *computed* from `(u, p)`, not because two integrals cancel. The reverse coupling acts through the domain: `Γ_if` moves with `d`, so `Ω_f(d)`, and the fluid residual depends on `d` through the geometry — which is precisely where the shape derivatives of the monolithic escalation (`ch08`, solution procedure) belong.

**(e) Does mesh conformity make them cancel?** No. Conformity is a *precondition* for cancellation at the discrete level (it makes the two discrete surfaces coincide and lets test-function traces be compared), but it is not a *cause*. The cause would have to be a shared test function plus traction equality; the shared test function is absent here because of the Dirichlet condition.

**(f) Is the intended statement perhaps the transient one?** If the velocity were an unknown tied to the solid by `u = ∂d/∂t`, then `v` and `φ` would share the interface trace and the standard cancellation would hold. That is the standard FSI argument, and the document reserves transient ALE to a future extension (`ch03:160–162`, `ch09`). The claim as printed is therefore a transient-formulation argument applied to a steady Dirichlet formulation.

> **Finding M4 — FAIL.** The mechanical interface terms do not cancel: the fluid interface integral vanishes identically under the no-slip Dirichlet condition, and the solid interface integral is a computed load. The sentence "the two terms … cancel identically" and the associated claim that the monolithic statement contains "no modelled interface quantity" are not supported. The defensible conclusion (no independent interface traction unknown) survives on the correct ground. Correction applied; see correction log C‑3 and the rewritten paragraph at `ch08:61–102`.

> **Finding M5 — UNRESOLVED.** The two interface integrals are taken over different surfaces: the solid is posed on `Ω_s^0` (`ch03:70–73`) and the fluid on `Ω_f` (`ch03:19–20`), yet `eq:weaks` and `eq:weakts` write their boundary integrals over `Γ` without saying whether this is `Γ_if^0` (reference) or `Γ_if` (deformed). For small strains the surfaces differ by `O(ε)`; at the baseline the total mechanical surface strain is `5.4×10⁻³`, so the surface and normals agree to about 0.5%. **What is missing:** the manuscript must state on which surface each integral is evaluated, and must classify the residual `O(ε)` discrepancy as a modelling approximation of Assumption A4 rather than as an identity. The rewritten paragraph now states this explicitly; the choice of surface remains the author's.

### 2.5 Geometric stiffness not represented in the weak form

`ch03:147–150` states that the production model is the two-dimensional system `eq:solidenergy`–`eq:equilibrium` and that the beam equation is used "only for design estimates and benchmark construction". But the solution procedure (`ch08`, step 3) instructs the solver to "solve the thermoelastic subproblem `eq:weaks`–`eq:weakts` at the reduced (frozen-force) von Kármán level … linear thermoelasticity augmented by the geometric-stiffness contribution of the current membrane state".

`eq:weaks` together with `eq:constitutive` is *linear* thermoelasticity with `ε = ½(∇d + ∇dᵀ)`. That strain measure contains no `½(w′)²` term, so no geometric stiffness can arise from it; the augmentation described in the solution procedure is not obtainable from the displayed weak form.

> **Finding M8 — UNRESOLVED.** Two chapters describe incompatible production solid models: the 2D linear system (`ch03`) versus a reduced von Kármán augmentation (`ch08`). **What is missing:** a decision by the author. Either (i) the production solid is the linear 2D system, in which case `ch08` step 3 must drop the augmentation and the design-level beam–column results stay in the design lane; or (ii) the geometric stiffness is to be retained, in which case the weak form must be written with the von Kármán strain (and `eq:constitutive` and `eq:weaks` change). I have not altered either, because choosing is a modelling decision, not a correction.

---

## Task 3 — Independent derivation of the thermal weak forms

### 3.1 Fluid energy

**Governing equation** (`ch03:47`): `ρ c_p (u·∇)T_f = k_f ∇²T_f` in `Ω_f`.

**Boundary data:** `T_f = T_in` on `Γ_in` (B1, Dirichlet); `∂_n T_f = 0` on B3, B4, `Γ_out` (natural); `T_f` continuous across `Γ_if` (not prescribed).

**Derivation.** Multiply by `χ`, integrate, and integrate the diffusion term by parts:

```
ρ c_p ∫_{Ωf} (u·∇)T_f χ dx = k_f ∫_{Ωf} ∇²T_f χ dx
                           = k_f ∫_{∂Ωf} (∇T_f·n_f) χ ds − k_f ∫_{Ωf} ∇T_f·∇χ dx
```

hence

```
ρ c_p ∫_{Ωf}(u·∇)T_f χ dx + k_f ∫_{Ωf} ∇T_f·∇χ dx = ∫_{∂Ωf} k_f (∇T_f·n_f) χ ds
```

Only `Γ_if` survives among the boundary terms (Dirichlet on `Γ_in`; zero normal derivative elsewhere), and `n_f = n` there:

```
ρ c_p a_T(u;T_f,χ) + a_kf(T_f,χ) = + ∫_{Γ_if} k_f ∇T_f·n χ ds
```

> **Finding T1 — PASS.** `eq:weaktf` (`ch08:40–41`) with the `+` sign is correct. The Stage‑5 correction is independently confirmed: the earlier `−` sign could not be obtained from the stated integration by parts.

Note that the advective term is kept in convective form and is *not* integrated by parts; consequently it contributes no boundary term. This is legitimate for `∇·u = 0` but is a choice, not an identity, at the discrete level where `∇·u = 0` holds only weakly.

### 3.2 Solid conduction

**Governing equation** (`ch03:59`): `∇·(k_s ∇T_s) = 0` in `Ω_s^0`.

**Boundary data:** B6 imposed flux on `Γ_h^0`; B7, B8 zero flux; `Γ_if` continuity.

**Derivation:**

```
0 = ∫_{Ωs0} ∇·(k_s∇T_s) χ dX
  = ∫_{∂Ωs0} k_s (∇T_s·n_s) χ dS − ∫_{Ωs0} k_s ∇T_s·∇χ dX
```

so

```
a_ks(T_s,χ) = ∫_{∂Ωs0} k_s (∇T_s·n_s) χ dS
            = ∫_{Γ_h^0} k_s(∇T_s·n_out) χ dS − ∫_{Γ_if} k_s(∇T_s·n) χ dS
```

using `n_s = −n` on the interface and `n_out` on the heater face.

> **Finding T2 — PASS.** `eq:weakts` (`ch08:44–45`) is correct, given B6 in the form `+k_s∇T_s·n_out = q''` and the minus sign on the interface term.

### 3.3 The heater condition B6

The manuscript now reads (`ch05:51`): `+k_s ∇T_s·n_out = q''`, with `q'' > 0` supplied to the solid.

Independent check by physical reasoning and by sign: let `q = −k_s∇T_s` be the heat-flux vector. Heat leaving the solid across a face with outward normal `n_out` is `q·n_out = −k_s∇T_s·n_out`. Heat *entering* is `+k_s∇T_s·n_out`. A heater supplying `q'' > 0` therefore satisfies `k_s∇T_s·n_out = q''`. Independent consistency check: the outer face is the top face, `n_out = +ŷ`; heat entering from above means the temperature is highest at that face, so `∇T_s` points in `+ŷ`, giving `∇T_s·n_out > 0` and hence `q'' > 0`. Both routes agree.

> **Finding T3 — PASS.** B6 is correct in its current form. The pre‑Stage‑5 form `−k_s∇T_s·n_out = q''` would have required `q'' < 0` for heating, i.e. a sign flip of the entire thermal load. Independently confirmed.

### 3.4 Wall heat flux and Nusselt number

The manuscript now defines (`ch08:163–166`): `q_w = +k_f ∇T_f·n`, "into the fluid", with `Nu = 2H₀ h/k_f`, `h = q_w/(T_w − T_b)`.

Independent check: `q = −k_f∇T_f`; heat leaving the fluid across `Γ_if` is `q·n = −k_f∇T_f·n`; heat entering the fluid is `+k_f∇T_f·n`. On a heated wall the fluid adjacent to the wall is hotter than the bulk, so `T_f` decreases away from the wall; `n` points away from the fluid into the solid, i.e. towards increasing `T_f`, so `∇T_f·n > 0` and `q_w > 0`. With `T_w > T_b`, `h > 0` and `Nu > 0`.

Dimensional check: `Nu = 2H₀ h/k_f = [m][W m⁻²K⁻¹]/[W m⁻¹K⁻¹]`, dimensionless. Normalization check: `2H₀ = D_h` for the slit on the wetted-perimeter basis, matching the benchmark definition of `ch09` V‑B.

> **Finding T4 — PASS.** `q_w`, `h` and `Nu` are mutually consistent and positive on a heated wall. The pre‑Stage‑5 definition `q_w = −k_f∇T_f·n` was the flux *out of* the fluid and would have produced `Nu < 0` on every heated-wall benchmark.

### 3.5 Flux continuity

`eq:ifflux` (`ch05:12`): `−k_f∇T_f·n = −k_s∇T_s·n`, which is `k_f∇T_f·n = k_s∇T_s·n`, i.e. continuity of the normal component of `q = −k∇T` evaluated with one normal.

> **Finding T5 — PASS.** The condition is correctly stated and correctly normalized.

### 3.6 Do the thermal interface terms cancel?

Here the situation differs from mechanics in a decisive way: **the temperature is not prescribed on `Γ_if`**. `eq:iftemp` states continuity, not a Dirichlet value, so the thermal test functions do not vanish on the interface.

If continuity is enforced by a single interface unknown shared by the two subdomains (one basis function `χ` whose support includes elements on both sides), the assembled equation for that unknown is the sum of the two residual contributions:

```
R_f(χ) + R_s(χ),  where
R_f(χ) = ρ c_p a_T(u;T_f,χ) + a_kf(T_f,χ) − ∫_{Γ_if} k_f∇T_f·n χ ds
R_s(χ) = a_ks(T_s,χ) − ∫_{Γ_h^0} q''χ ds + ∫_{Γ_if} k_s∇T_s·n χ ds
```

The interface terms sum to

```
−∫_{Γ_if} (k_f∇T_f·n − k_s∇T_s·n) χ ds = 0   under eq:ifflux.
```

> **Finding T6 — PASS.** The thermal interface terms do cancel, and the cancellation is genuine: it is the standard conforming conjugate-heat-transfer statement, and it makes the interface unknown's equation the discrete statement of normal-flux balance. This requires shared unknowns and is *not* a consequence of mesh conformity alone.

> **Finding T7 — UNRESOLVED.** The prerequisite of T6 — that the interface temperature is a *single shared unknown* — is not stated. `ch08:23–24` says only that "interface quantities are then transferred by identical nodal values", which is compatible both with one shared unknown and with two unknowns whose values are copied. The two readings give different weak forms: under the first, the interface terms cancel and flux continuity is satisfied weakly; under the second, they do not cancel and flux continuity must be imposed as an extra constraint. **What is missing:** one sentence stating that the interface temperature is a single unknown in the monolithic system.

---

## Task 4 — Audit of the bilinear and trilinear forms

Current definitions (`ch08:48–55`, after this stage's corrections):

| Form | Definition | Type | Trial / test | Domain | Coefficient |
|---|---|---|---|---|---|
| `â_f(u,v)` | `2μ ∫_{Ωf} D(u):D(v) dx` | bilinear | `V_g × V_0` | `Ω_f` | `μ` constant (A2) |
| `b(v,p)` | `−∫_{Ωf} p ∇·v dx` | bilinear | `V_0 × Q` | `Ω_f` | none |
| `c(u;u,v)` | `ρ ∫_{Ωf} (u·∇u)·v dx` | trilinear | `V_g × V_g × V_0` | `Ω_f` | `ρ` constant |
| `a_T(u;T,χ)` | `∫_{Ωf} (u·∇T) χ dx` | trilinear | `V_g × S_f × S_f^0` | `Ω_f` | `ρc_p` enters in `eq:weaktf` |
| `a_kf(T,χ)` | `k_f ∫_{Ωf} ∇T·∇χ dx` | bilinear | `S_f × S_f^0` | `Ω_f` | `k_f` constant |
| `a_ks(T,χ)` | `k_s ∫_{Ωs0} ∇T·∇χ dX` | bilinear | `S_s × S_s` | `Ω_s^0` | `k_s` constant |

**Consistency with the governing equations.** `â_f + b = ∫σ_f:∇v`, reproducing `eq:momentum` — verified in §2.1. `ρc_p a_T + a_kf` reproduces `eq:fluidenergy` — verified in §3.1. `a_ks` reproduces `eq:solidenergy` — verified in §3.2. `c(u;u,v)` reproduces the convective term of `eq:momentum`, kept in convective (non-conservative) form.

> **Finding B1 — PASS.** `â_f` is correctly defined and correctly used.
> **Finding B2 — PASS.** `b` is correctly defined and correctly used; its `−` sign is the one that makes `â_f + b = ∫σ_f:∇v`.
> **Finding B3 — PASS.** `c` is correctly defined as trilinear with the semicolon convention placing the advecting velocity first.

> **Finding B4 — FAIL.** `a_T` was written as a two-argument ("bilinear") form, `a_T(T,χ) = ∫(u·∇T)χ dx`, but the integrand contains `u`, an *unknown*. The form is therefore trilinear, not bilinear, and its printed arity contradicts the sentence that grouped it with the bilinear forms. Corrected: `a_T(u;T,χ)`, matching the semicolon convention already used for `c`. This is a notation/type correction only; the integrand is unchanged and no physics is altered.

> **Finding B5 — PASS.** `a_kf` is correctly defined and used; its domain `Ω_f` matches `eq:fluidenergy`.
> **Finding B6 — PASS.** `a_ks` is correctly defined and used; its domain `Ω_s^0` matches `eq:solidenergy`.
> **Finding B8 — PASS.** Every form's domain of integration and coefficient assumptions match the chapter that states the corresponding strong equation (constant `μ`, `k_f`, `k_s`, `ρ` under A2).

> **Finding B7 — UNRESOLVED.** The stabilization form (`ch08:19–20`) is invoked as "a consistent streamline-upwind (SUPG) term with the standard residual-based coefficient" but is never written. **What is missing:** the definition of the stabilization operator and of the time-scale `τ` (including the element Péclet number and the element size), without which the discrete problem is not specified. This was already open as item B‑3 in the Stage‑5 checklist; it is not a sign error.

> **Finding M6 — FAIL (spaces).** `V_g`, `Q`, `V_s`, `S_f`, `S_s` are used at `ch08:34` and defined nowhere (`ch02`, `ch03`, `ch05`, `ch08`, `appendix.tex` searched). The test spaces are not named at all: after the weak equations the text says only "for all test functions" (`ch08:47`). `V_0`, which this audit uses for the fluid test space, is therefore the auditor's notation and not a document symbol — the C‑3 replacement text deliberately avoids introducing it, so that the applied patch does not add a new undefined name. A weak formulation without its function spaces is not a well-posed statement; in particular, whether `v = 0` on `Γ_if` (the fact that drives finding M4) is a property of the test space that the reader must infer from boundary row B5 and `eq:ifkin` rather than read from a definition. Correction proposed but **not applied** (see correction log P‑1), because a correct statement of the spaces depends on resolving finding T8 first.

---

## Task 5 — Mathematical and physical implications

### 5.1 Interface action–reaction

`t_f + t_s = 0` follows from `eq:iftraction` under the single normal (§2.3). The two subdomain weak forms then place the traction on the fluid with `+` and on the solid with `−` relative to the same normal — but see M4 for which of the two survives the Dirichlet condition.

> **Finding C5 — PASS.** Every boundary condition in Table `tab:bcs` is consistent with the weak forms: Dirichlet data (B1, B3, B4, B5-kinematic, B7) appear nowhere as integrals because the corresponding test functions vanish; Neumann/natural data (B2, B6, B8) appear exactly once each with the correct sign.

### 5.2 Conservation of heat

Integrating `eq:fluidenergy` over `Ω_f` and using `∇·u = 0` gives `ṁ' c_p (T_b,out − T_b,in) = ∫_{Γ_if} q_w ds`. Combined with the solid balance `∫_{Γ_h^0} q'' dS = ∫_{Γ_if} q_w ds`, the global enthalpy check of `ch08:149–150`, `|∫_{Γ_h}q'' ds − ṁ'c_p ΔT_b| ≤ 10⁻³ Q'`, is the correct global statement. Arithmetic check: `Q' = q''L = 5000 × 0.03 = 150 W/m`; `ṁ'c_p = ρUH₀c_p = 1000 × 0.05 × 5×10⁻⁴ × 4180 = 104.5 W/(m·K)`; hence `ΔT_b = 1.435 K`, against `1.44 K` tabulated at `ch07:49`. Consistent.

> **Finding C2 — PASS.** The conservation check follows from the weak forms and the boundary data, and its arithmetic is correct.

### 5.3 Dimensional consistency

`â_f`, `b`, `c` each carry `Pa·m²/s = N/s`: `[2μD:D dx] = (Pa s)(s⁻²)(m²) = Pa m² s⁻¹`; `[p∇·v dx] = (Pa)(s⁻¹)(m²)`; `[ρ(u·∇u)·v dx] = (kg m⁻³)(m s⁻²)(m s⁻¹)(m²) = kg m s⁻³ = N s⁻¹`. The thermal forms carry `W·K/m`: `[ρc_p(u·∇T)χ dx] = (J m⁻³K⁻¹)(K s⁻¹)(K)(m²) = J K m⁻¹ s⁻¹` and `[k_f∇T·∇χ dx] = (W m⁻¹K⁻¹)(K m⁻¹)²(m²) = W K m⁻¹`, equal since `J s⁻¹ = W`. The heater term `[q''χ ds] = (W m⁻²)(K)(m) = W K m⁻¹`. All consistent.

> **Finding C1 — PASS.** Every form, every right-hand side and every interface term is dimensionally consistent.

### 5.4 Limiting cases

As `d → 0` and `θ → 0`, `eq:weaks` decouples and the system reduces to the rigid-slit fluid and thermal problems that the benchmark hierarchy V‑A/V‑B targets; `eq:weakf` reduces to the standard Galerkin Navier–Stokes weak form; `Pe → 0` reduces `eq:weaktf` to pure conduction. No limiting case contradicts the stated equations.

> **Finding C3 — PASS.** The weak forms have the expected limits, and those limits are the ones the verification hierarchy uses.

### 5.5 Identity vs assumption vs approximation

Three distinct kinds of statement are conflated in the manuscript's original prose and are now separated at `ch08:61–102`:

| Statement | Kind |
|---|---|
| `σ_s n = σ_f n` | model statement (perfect bonding, no interfacial stress) |
| The solid interface term equals the virtual work of the fluid traction | **identity** given `eq:iftraction` |
| The thermal interface terms sum to zero | **identity** given `eq:ifflux` and shared unknowns |
| The two boundary integrals are taken over the same surface | **approximation**, `O(ε) = O(5.4×10⁻³)` |
| The integrals cancel after discretization | **approximation**, subject to conforming mesh and matching quadrature |

> **Finding C4 — FAIL (before correction).** `ch02:134–137` repeated the mechanical cancellation claim and additionally asserted that using one normal "renders the interface boundary terms … exactly antisymmetric, so that they cancel in a monolithic assembly without modelling error". Two defects: (i) a common normal is necessary but not sufficient for cancellation — a shared test function is also required, and it is absent (M4); (ii) "without modelling error" conflates the `O(ε)` surface discrepancy (an approximation) with an identity. Corrected; see correction log C‑4.

---

## 6. Findings register

| ID | Item | Status |
|---|---|---|
| M1 | Fluid momentum → weak form, all terms and signs | **PASS** |
| M2 | Solid equilibrium → weak form, sign of `eq:weaks` | **PASS** |
| M3 | Traction continuity / action–reaction under `n_s = −n` | **PASS** |
| M4 | Mechanical interface terms "cancel identically" | **FAIL** — corrected |
| M5 | Reference vs deformed surface for the interface integrals | **UNRESOLVED** |
| M6 | Function spaces `V_g, V_0, Q, V_s, S_f, S_s` undefined | **FAIL** — correction proposed, not applied |
| M7 | `⟨data⟩` undefined in `eq:weakf` | **FAIL** — corrected |
| M8 | Geometric stiffness invoked but absent from `eq:weaks` | **UNRESOLVED** |
| T1 | Fluid energy → weak form, sign | **PASS** |
| T2 | Solid conduction → weak form, sign | **PASS** |
| T3 | Heater condition B6 sign | **PASS** |
| T4 | `q_w` sign, `h`, `Nu` positivity and normalization | **PASS** |
| T5 | Heat-flux continuity statement | **PASS** |
| T6 | Thermal interface cancellation | **PASS** |
| T7 | Shared interface temperature unknown not stated | **UNRESOLVED** |
| T8 | Contradictory thermal data flow (`ch05:70–72` vs `ch08` step 2) | **FAIL** — correction proposed, not applied |
| B1 | `â_f` | **PASS** |
| B2 | `b` | **PASS** |
| B3 | `c` | **PASS** |
| B4 | `a_T` declared bilinear but depends on `u` | **FAIL** — corrected |
| B5 | `a_kf` | **PASS** |
| B6 | `a_ks` | **PASS** |
| B7 | SUPG form and `τ` undefined | **UNRESOLVED** |
| B8 | Domains and coefficients match the strong equations | **PASS** |
| C1 | Dimensional consistency | **PASS** |
| C2 | Global heat conservation and its arithmetic | **PASS** |
| C3 | Limiting cases | **PASS** |
| C4 | `ch02` cancellation/antisymmetry/`O(ε)` conflation | **FAIL** — corrected |
| C5 | Boundary conditions consistent with the weak forms | **PASS** |

**19 PASS · 6 FAIL · 4 UNRESOLVED.**

### 6.1 Detail on T8 (the only finding not yet described above)

`ch05:70–72` states: "the fluid subproblem receives its domain and the interface temperature from the solid; the solid subproblem receives the interface traction (pressure-dominated) and the conjugate flux condition." `ch08`, step 2 (line 91) instead states: "transfer pressure-dominated traction and interface temperature requirements to the solid."

These assign the interface temperature in opposite directions. The distinction is not cosmetic:

- If the solid receives **temperature** (Dirichlet on `Γ_if`), its conduction problem is well posed.
- If the solid receives **flux** only (as `ch05` says), `eq:weakts` becomes a pure-Neumann problem: singular up to an additive constant, and feasible only if the net flux through `∂Ω_s^0` vanishes. Since the flux passed in is computed from the fluid solution, that compatibility is not guaranteed during iteration, so the subproblem can be infeasible, not merely indeterminate.

**Finding T8 — FAIL.** Two internally contradictory specifications; the well-posedness of a subproblem depends on which is meant. Correction proposed (P‑2), not applied: the choice is an algorithmic decision.

---

## 7. What this audit does and does not establish

**Established.** The four weak equations `eq:weakf`–`eq:weakts` are correct weak forms of the strong equations `eq:momentum`, `eq:fluidenergy`, `eq:solidenergy`, `eq:equilibrium` with the interface conditions `eq:iftraction`–`eq:ifflux`, under the single-normal convention, once the corrections of this stage are accepted. The thermal interface terms cancel for a conforming discretization with a shared interface temperature unknown. The mechanical interface terms do not cancel, and the reason the formulation needs no interface traction unknown is different from the one printed.

**Not established.** This is an audit of the *statement* of the formulation. It is not a proof that the formulation is well posed (no inf–sup analysis, no existence/uniqueness argument), not a proof that the discretization converges, and not a validation of the physical model. No code was run, so nothing here is a numerical verification.

**Independence.** The derivations were performed from the printed strong forms. Where they reproduce Stage‑5 corrections (M2, T1, T2, T3, T4), that is confirmation by independent route. Where they contradict earlier prose (M4, C4), the earlier prose was wrong even though the equations it described were right.
