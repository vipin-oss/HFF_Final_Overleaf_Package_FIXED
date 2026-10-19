# Stage 15 — Weak form, boundary conditions and well-posedness verification

**What this document does.** It re-derives the weak statement from the printed equations, checks
every added or corrected line against the strong form it must reproduce, and records what is and is
not provable from the source. It is independent of the numerical register: nothing here uses a
manuscript result as an input.

---

## 1. The coupled statement as it now stands

`ch08:44–72`: find `(u, p, T_f, d, T_s) ∈ V_g × Q × S_f × V_s × S_s` such that for all test
functions

    â_f(u,v) + b(v,p) + c(u;u,v) = ∫_Γ σ_f(u,p) n · v ds                                        (1a)
    ρ c_p a_T(u;T_f,χ) + a_kf(T_f,χ)   = + ∫_Γ k_f ∇T_f · n χ ds                                (1b)
    ∫ σ(d,θ):ε(φ) dX − ∫ N_θ^c ∂_X d₂ ∂_X φ₂ dX = − ∫_Γ σ n · φ ds                             (1c)
    a_ks(T_s,χ) = ∫_{Γ_h⁰} q'' χ ds − ∫_Γ k_s ∇T_s · n χ ds                                    (1d)

## 2. Function spaces and traces (closes B-1)

Previously the five spaces were named and never defined. Now (`ch08:60–72`):

    V_g = { v ∈ [H¹(Ω_f)]² : v = 0 on the Dirichlet parts of ∂Ω_f },   Q = L²(Ω_f)
    S_f = { χ ∈ H¹(Ω_f) : χ = 0 at inflow x = −L_e }
    V_s = { φ ∈ [H¹(Ω_s⁰)]² : φ = 0 on the pinned ends },              S_s = H¹(Ω_s⁰)

**Check.** For (1a) and (1b) the Dirichlet data are essential on `V_g` and `S_f`; the outflow term
is natural (do-nothing) — this matches `ch05:58`, and the exit length `L_o` is required to make the
natural condition meaningful. For (1c), `V_s` carries the kinematic pin as an *essential*
condition, while `M = 0` at the pins is *natural* — which is why the pin condition
`w''(0) = −κ_th` is a consequence of the weak statement, not a datum imposed on it (§4).

**Traces.** The interface lives in `H^{1/2}(Γ_if)` for all five spaces. This is the correct trace
space for `H¹` functions on a Lipschitz domain, and it is the space in which the shared interface
unknown of §5 lives. Stating it is what makes "one unknown shared by two subdomains" well defined
rather than a figure of speech.

**Residual gap.** `V_g` as written requires `[H¹]²`, hence no re-entrant-corner or pressure
`H¹` regularity is claimed. The Navier–Stokes steady problem on a slit with a moving wall has the
regularity needed for this choice; the manuscript does not prove it. This is a *disclosed*
mathematical assumption, not a defect that can be repaired in the text.

## 3. Pressure gauge (closes B-2)

`Q = L²(Ω_f)` leaves one free constant in `p`. The source asserted the datum `p = 0` at outflow
(`ch05:47`) but never said how it is enforced. `ch08:70–72` now states it as a single scalar
constraint, `∫_{Γ_out} p ds = 0`, imposed on the algebraic system.

**Check — three statements must agree, and now do.** `ch05:58–63` (B2, do-nothing outflow),
`ch04:284–292` (the load datum: `p(0)=120`, `p(L)=48`, `p̄=84` Pa), and `ch08:70`. They agree
because the gauge is fixed at the *outlet*, where the do-nothing condition already sets the level,
and the casing is at the same reference (`A9`). The consequence is `p̄ = ½[p(0)+p(L)] = 84 Pa`
rather than `Δp/2 = 36 Pa` (D-16) — verified arithmetically in `03_numerical_register.md`.

**Residual.** `Q = L²` with a mean-pressure constraint is one legitimate gauge. An alternative is a
pinned pressure dof at a single node, which is equivalent for this problem but less robust. The
choice is now explicit, so it is a coding instruction rather than an ambiguity.

## 4. Geometric stiffness in the solid weak form (closes B-3)

**Repair.** The term `− ∫_{Ω_s⁰} N_θ^c ∂_X d₂ ∂_X φ₂ dX` was added to (1c).

**Derivation check (independent).** The printed reduced beam–column equation is
`D_s w'''' + N_θ^c w'' = 0` (`eq:beamcol`, `ch04:183`). Multiply by a test function `φ` vanishing
at the ends, integrate by parts twice:

    ∫ D_s w'''' φ + ∫ N_θ^c w'' φ = 0
    ⟹ ∫ D_s w'' φ'' − ∫ N_θ^c w' φ' = 0        (all boundary terms vanish)

The second integral is exactly `−∫ N_θ^c ∂_X d₂ ∂_X φ₂` because `w = +d₂`. **The sign is correct
for `N_θ^c > 0` in compression**, which is the case at the baseline (`N_θ = −2.904×10⁴ N/m`).

**Reduction check.** With the elastic part of `∫σ:ε(φ)` reducing to `∫D_s w''φ''`, (1c) becomes the
weak form of `D_s w'''' + N_θ^c w'' = p`, which is `eq:beamcol` when `p = 0` and `eq:beam` when
`N_θ^c = 0`. The manuscript states exactly this (`ch08:74–76`). The *earlier* claim that the
reduction "recovers `eq:beamcol`" without that qualification was tightened during this pass, because
`eq:beamcol` is the zero-load problem.

**Why this mattered.** Without the term, the 2-D production model was the *linear* solid, but
Chapter 4 builds the baseline on the beam–column level. The two disagreed by the amplification
factor `1.389654`, i.e. by `39 %` in `w_max`. Adding the term aligns the production model with the
design relation it is validated against.

## 5. Thermal coupling and the shared interface unknown (closes B-4)

`ch08:108–117` asserts: the interface temperature is **not prescribed**; continuity is enforced by
a **single unknown shared** by both subdomains; the two flux residuals sum for that unknown; under
`eq:ifflux` their sum vanishes, leaving the flux balance as the equation for the unknown.

**Independent check of the cancellation.** With the single normal `n` (fluid → solid), the fluid
residual contributes `−∫k_f∇T_f·n χ ds` and the solid `+∫k_s∇T_s·n χ ds`. Their sum is
`−∫(k_f∇T_f·n − k_s∇T_s·n)χ ds`, which vanishes precisely when `k_f∇T_f·n = k_s∇T_s·n`.

Now check that against the printed interface condition. `ch05:12` states
`−k_f∇T_f·n = −k_s∇T_s·n`, i.e. `k_f∇T_f·n = k_s∇T_s·n`. **They agree exactly.** So the
cancellation argument and the printed flux-continuity condition are consistent — verified, not
assumed.

**What was wrong.** `ch05:70–72` said the fluid receives the interface temperature *from the solid*
and that the solid receives the conjugate flux. That is (i) a different model from `ch08`, and
(ii) ill-posed as stated: the solid already has the prescribed flux on all of `Γ_h⁰` and zero flux
elsewhere, so a flux datum on `Γ_if` makes the solid **pure-Neumann** — temperature determined only
up to an additive constant, and that constant propagates into `N_θ`. The paragraph is now restated
in two parts: mechanically Dirichlet–Neumann, thermally a shared unknown.

**Note on an earlier draft of this repair.** The first rewrite in this pass described the exchange
as "the solid receives a Dirichlet temperature, returns a flux; the fluid receives the flux". That
was rejected on re-audit because it contradicts `ch08:108` ("not prescribed") and `ch08:115` ("no
separate interface heat flux is discretized"). The corrected text keeps the shared-unknown
formulation and uses the pure-Neumann argument only to rule out the *flux-datum* alternative. This
is recorded because it is exactly the class of error a batch introduces and a regression pass must
catch.

## 6. Reference vs deformed interface (closes B-10)

The solid is posed on `Ω_s⁰` and the fluid on the deformed `Ω_f`, so the two boundary integrals are
taken over `Γ_if⁰` and `Γ_if`, coinciding only to `O(ε)`. The manuscript states `5.4×10⁻³` at the
baseline.

**Check.** The total mechanical surface strain is `e₀ + κ_geo d/2 = 2.2589×10⁻³ + 3.0888×10⁻³ =
5.347713×10⁻³`, i.e. `5.3×10⁻³`. The stated order and magnitude are **correct**. The disclosure is
also correctly worded: "exact at the level of the model on a common surface, accurate to that order
in the adopted reference-configuration solid — it is not an identity of the discrete system." No
change required.

## 7. Monolithic cancellation vs staggered iteration (closes B-5)

The source asserted both that the interface terms cancel ("monolithic interface cancellation",
`ch08:31`) and described a fixed-point iteration (`ch08:80`, `86–88`). Both are true but of different
objects.

**Resolution now stated at `ch08:160–166`.** The cancellation is a property of the **assembled**
system, where `T_Γ` is one unknown. The fixed-point iteration solves the two subproblems separately
with transferred data, so within an unconverged iterate the residuals do not cancel and the flux
balance is recovered **only in the limit**. Therefore the interface flux-jump norm of test V-B is an
**acceptance criterion**, not an optional diagnostic. The monolithic path changes the *solver*, not
the discretization of the interface unknown.

**Check.** This is consistent with `ch08:118–131`, which lists the three conditions for the
cancellation to survive discretization (single normal, conforming interface mesh, identical
quadrature and isoparametric representation). A conforming mesh makes the two discrete interfaces
coincident, which is precisely what the limit argument needs. No contradiction remains.

## 8. SUPG parameter (closes B-6)

Previously "the standard residual-based coefficient". Now (`eq:supg`, `ch08:21–28`):

    τ_K = (h_K / 2|u|_K)(coth Pe_K − 1/Pe_K),   Pe_K = |u|_K h_K / (2κ_f),   κ_f = k_f/(ρc_p)

**Check.**
- Units: `[h/|u|] = s`, the parenthesis is dimensionless ⟹ `τ_K` is a time. Correct.
- `Pe_K ≫ 1`: `coth Pe_K → 1`, so `τ_K → h_K/(2|u|_K)`. Correct, and stated.
- `Pe_K → 0`: `coth x − 1/x → x/3`, so `τ_K → h_K²/(12κ_f)`. Finite. Correct, though not stated;
  it is the reason `τ` needs no clipping.
- The bracket is the exact optimal value for the 1-D steady advection–diffusion problem, which is
  what justifies calling it "consistent". Correct.
- `Pe = 348` is the global Péclet; `Pe_K` is the cell value. The two must not be conflated, and the
  text no longer does.

**Residual.** `h_K` is defined as "the element length in the mean-flow direction", which is
adequate for a graded boundary-layer mesh but is not a unique definition for anisotropic elements.
This is a coding choice to be fixed in the implementation and recorded, not a mathematical gap.

## 9. Verification of the printed closed-form solution

The printed solution `eq:beamcolsol` was checked *against the printed ODE and BCs*, not against
recalled values, using the printed constants (`D_s = 9.642857143`, `κ_th = 1.4`, `μL = 1.646414286`):

| Condition | Residual |
|---|---|
| `w(0) = 0` | `0.000×10⁰` |
| `w(L) = 0` | `0.000×10⁰` |
| `w''(0) = −κ_th` | `0.000×10⁰` |
| `w''(L) = −κ_th` | `0.000×10⁰` |
| `D_s w'''' + N_θ^c w''` at `x/L = 0.30, 0.50, 0.77` | `1.5×10⁻¹¹`, `7.3×10⁻¹²`, `7.3×10⁻¹²` |

The solution with `A = tan(μL/2)` is
`w(x) = (κ_th/μ²)[tan(μL/2) sin μx + cos μx − 1]`, matching the printed form because
`(1−cos μL)/sin μL ≡ tan(μL/2)`. **The printed solution is exact.**

## 10. Two exact identities used elsewhere

Both are provable in one line and are not numerical coincidences:

1. `κ_geo ≡ κ_th sec(μL/2)`.
   `κ_geo = −w''(L/2) = κ_th[A sin(μL/2) + cos(μL/2)]` with `A = tan(μL/2)`, so the bracket is
   `sin²(μL/2)/cos(μL/2) + cos(μL/2) = 1/cos(μL/2)`. Verified numerically to `2.2×10⁻¹⁶`.

2. `(κ_geo+κ_th)/(κ_geo−κ_th) = (1+cos(μL/2))/(1−cos(μL/2)) = cot²(μL/4)`.
   Verified to `1.1×10⁻¹⁵`; equals `5.247516878033` at the baseline.

Identity 2 is what closes the `9.8881×10⁻⁴` vs `−5.1888×10⁻³` question: their ratio is fixed by
`μL` alone, independent of every material and load parameter.

## 11. Arc-stretching term: analytic vs quadrature

With `w' = (κ_th/μ)(A cos μx − sin μx)`, the analytic average is

    ⟨w'²⟩ = (κ_th/μ)² [ (1+A²)/2 + (A²−1) sin(2μL)/(4μL) − A sin²(μL)/(μL) ]

and `½⟨w'²⟩ = 1.388009729195511×10⁻⁴`.

| Method | Value | Agreement |
|---|---|---|
| Analytic | `1.3880097291955×10⁻⁴` | — |
| Composite Simpson, 400001 nodes | `1.3880097291955×10⁻⁴` | `1.3×10⁻¹⁴` relative (absolute `1.8×10⁻¹⁸`) |

The circular-arc estimate `κ_geo²L²/24 = 1.590127647×10⁻⁴` differs by `−0.62 %`. **The estimate is
sound** — for a parabolic arc of constant curvature `κ`, `w' = κ(L/2 − x)` gives
`½⟨w'²⟩ = κ²L²/24` exactly, so the formula is right and the discrepancy is the (correct) difference
between a parabolic and a beam–column profile. The manuscript retains `1.6×10⁻⁴` and now labels it
a peak-curvature estimate.

## 12. Disclosed limitations that are *not* defects

- Regularity of the steady Navier–Stokes solution on the moving-wall slit is assumed, not proved.
- `h_K` for anisotropic elements is a coding choice.
- The `O(ε)` reference/deformed interface mismatch is disclosed with its magnitude.
- The frozen-force reduction is a model level with a quantified, one-sided `2.3 %` error, not an
  approximation silently used.
