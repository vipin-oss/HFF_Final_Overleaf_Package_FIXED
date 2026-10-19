# Stage 15 — Solver-ready specification

A coding team should be able to implement the baseline from this document alone. Anything that is
**not** determined by the source is marked `DECISION` with the options and the consequences, so it is
visible rather than silently chosen. Everything else is fixed by the manuscript at `e8ef0d7`.

---

## 1. Physical configuration

| Item | Value | Source |
|---|---|---|
| Channel reference height `H₀` | `5.0×10⁻⁴ m` | `ch02` |
| Heated wall length `L` | `3.0×10⁻² m` | `ch02` |
| Entry / exit lengths `L_e`, `L_o` | `3.0×10⁻² m` each | `ch02` |
| Wall thickness `d` | `3.0×10⁻³ m` | `ch02` |
| Mean inlet speed `U` | `5.0×10⁻² m/s` | `ch02` |
| Imposed outer-face flux `q''` | `5.0×10³ W/m²` | A10, B6 |
| Solid: `E`, `ν`, `α`, `k_s` | `3.6×10⁹ Pa`, `0.40`, `5.0×10⁻⁵ K⁻¹`, `0.25 W/(m·K)` | Table `tab:props` |
| Fluid: `ρ`, `μ`, `k_f`, `c_p` | `1.0×10³ kg/m³`, `1.0×10⁻³ Pa·s`, `0.60 W/(m·K)`, `4.18×10³ J/(kg·K)` | Table `tab:props` |
| Derived | `D_s = 9.642857143 N·m`, `κ_th = 1.4 m⁻¹`, `w_max = 2.188704727879×10⁻⁴ m` | `03_numerical_register.md` |

Plane strain in the solid. Steady, incompressible, constant-property fluid.

## 2. Governing equations

**Fluid** (`Ω_f`, deformed): `ρ(u·∇)u = −∇p + μ∇²u`, `∇·u = 0`,
`ρc_p u·∇T_f = k_f∇²T_f`, with SUPG stabilisation of the energy equation only (§6).

**Solid** (`Ω_s⁰`, reference): equilibrium with thermoelastic constitutive law and the beam–column
reduction,

    ∫_Ωs⁰ σ(d,θ):ε(φ) dX − ∫_Ωs⁰ N_θ^c ∂_X d₂ ∂_X φ₂ dX = −∫_Γ σ n·φ ds

with `σ = C:(ε − ε_th)`, `ε_th = α_eff θ I`, `α_eff = (1+ν)α`, and `N_θ^c = |N_θ|` recomputed from
the current state each outer iteration. Conduction: `−k_s∇²T_s = 0` in `Ω_s⁰`.

## 3. Boundary conditions (verbatim from the B-table)

| ID | Location | Condition |
|---|---|---|
| B1 | inlet | `u = (U,0)`, `T_f = T_in` |
| B2 | outlet | do-nothing natural condition; pressure datum (see §5) |
| B3 | rigid walls of `Ω_f` | `u = 0`, `∂_n T_f = 0` |
| B4 | rigid upper sections | `u = 0`, `∂_n T_f = 0` |
| B5 | `Γ_if` | `eq:ifkin`–`eq:ifflux` (no-slip, traction continuity, temperature continuity, flux continuity) |
| B6 | `Γ_h⁰` (outer face) | `q''` prescribed |
| B7 | strip ends `X = 0, L` | `d₁ = d₂ = 0`, zero applied moment, `∂_n T_s = 0` |
| B8 | remaining solid faces | zero traction, zero flux |
| B9 | regime D | imposed `T_h` instead of `q''` — separately labelled study |

**B7 and B8 together are the RU-01 problem.** B8 says "zero traction" on the remaining faces, which
is only consistent with the strip bowing toward the casing if there is clearance (§`02_…` §4).

## 4. Interface treatment

Single unit normal `n`, fluid → solid. Single interface temperature unknown (not prescribed),
shared between subdomains; its equation is the flux balance `k_f∇T_f·n = k_s∇T_s·n`.

**Requirement:** the interface mesh must be **conforming** — nodes and edges coincide — and the
curved P2 interface must use the **same isoparametric representation and quadrature** on both
sides. Without this the cancellation is not an identity of the discrete system (see
`04_…` §7).

## 5. Pressure gauge

`p` is determined up to a constant. **Specification:** fix the mean pressure over the outflow
section, `∫_{Γ_out} p ds = 0`, as one scalar constraint on the algebraic system, consistent with the
do-nothing outflow and with the casing at the same reference pressure (A9). Consequence at the
baseline: `p(0) = 120 Pa`, `p(L) = 48 Pa`, `p̄ = 84 Pa`.

`DECISION` — implement the gauge as (a) a scalar Lagrange multiplier on the outlet mean, or (b) a
pinned pressure dof at one outlet node. Both are legitimate; (a) is cleaner for a direct solver and
is the form stated in `ch08`. **Record which one is used**, because the reported `Γ_p` depends on
`p̄` and `p̄` depends on the datum.

## 6. Discretisation

| Component | Choice | Source |
|---|---|---|
| Fluid velocity–pressure | Taylor–Hood (`P2`–`P1`) | `ch08:213` |
| Fluid temperature | `P2` with SUPG | `ch08:19–28` |
| Solid displacement | `P2` | conforming interface requirement |
| Solid temperature | `P2` | same |
| Domain map | pseudo-elastic, coefficient graded to stiffen small elements near `Γ_if`, `ŵ = d` on `Γ_if⁰`, `ŵ = 0` on rigid boundaries | `ch08:134–137` |
| Meshes | three nested uniform refinements per configuration | `ch08:180` |

**SUPG coefficient** (`eq:supg`):

    τ_K = (h_K / 2|u|_K)(coth Pe_K − 1/Pe_K),  Pe_K = |u|_K h_K/(2κ_f),  κ_f = k_f/(ρc_p)

`h_K` = element length in the mean-flow direction, `|u|_K` = element mean speed. `τ_K` is a **time**.
`DECISION` — for graded/anisotropic elements `h_K` is not unique; use the projection of the element
length along `u/|u|` and record the choice. Do **not** clip `τ_K`: the bracket is bounded as
`Pe_K → 0` (`→ Pe_K/3`), so no clipping is needed and clipping would silently degrade accuracy.

## 7. Solution procedure

1. Solve the fluid subproblem on the current `Ω_f` by exact Newton, with the advection derivative
   linearized analytically.
2. Transfer pressure-dominated traction and the interface temperature requirement to the solid.
3. Solve the thermoelastic subproblem at the reduced (frozen-force) von Kármán level: linear
   thermoelasticity **plus** the geometric-stiffness term of the current membrane state; one direct
   solve. Re-evaluate `N_θ` from the computed state after each solve, so that
   `N_θ(w) = N_θ + Ed⟨w'²⟩/[2(1−ν²)]` (`eq:nupdate`) is recovered at the fixed point.
4. Solve the mesh-extension problem, update `Ω_f`, recompute normals, Jacobians and quadrature.
5. Under-relax the interface displacement by `ω` (tune once, report per run).
6. Iterate until `‖d^(k+1) − d^(k)‖_∞ ≤ 10⁻⁶ w_max` **and** all four subproblem residuals are small
   **and** the interface flux-jump norm passes (§8).

**Escalation to monolithic Newton** (with consistent shape derivatives) if
`N_θ^c/N_cr > 0.5` at any iterate, or the geometry increment stagnates (four consecutive iterations
with the increment reduced by less than a factor of two). Pseudo-transient continuation is the
fallback. Linear systems: direct sparse factorisation at the target size (`10⁴–10⁵` dofs).

## 8. Acceptance criteria per run

| Check | Threshold |
|---|---|
| Global enthalpy balance, deformed geometry | `\|∫_{Γ_h}q''ds − ṁ'c_p(T_b,out − T_b,in)\| ≤ 10⁻³ Q'` |
| Interface flux-jump norm `‖[k∂_nT]‖_{L²(Γ)}/‖q''‖` | `≤ 10⁻³` |
| Mesh convergence, fine-to-medium | `≤ 1 %` (`0.5 %` for headline figures) |
| Mean-stress identity | pointwise within interpolation accuracy (runtime assertion) |
| Regime guards A-1–A-6 | recomputed from computed fields |
| Load-case consistency | additivity verified on a detuned case with `N_θ^c/N_cr ≤ 0.05` |

**The flux-jump norm is not optional.** Because the staggered iteration recovers the flux balance
only in the limit (`04_…` §7), this norm is the operative test that the limit has been reached.

## 9. Post-processing

    T_b(x) mass-flux weighted;   q_w(x) = +k_f ∇T_f·n|_Γ  (> 0 on the heated wall)
    h(x) = q_w/(T_w − T_b);      Nu(x) = 2H₀ h(x)/k_f

`Nu` is singular where `T_w → T_b` near the start of the heated segment — **plot it, do not clip**.
Export complete Cauchy components, never the mechanical part alone. Form `σ_m` from its definition
and assert the mean-stress identity at runtime.

## 10. Verification targets the solver must reproduce

These are the numbers the implementation is checked against (all recomputed in
`03_numerical_register.md`):

| Target | Value |
|---|---|
| `D_s` | `9.642857143 N·m` |
| `κ_th` | `1.400000000 m⁻¹` |
| `w_max` (frozen force) | `2.188704727879×10⁻⁴ m = 0.437740946 H₀` |
| Amplification over linear | `1.389653795` |
| `κ_geo` | `2.059208681 m⁻¹` |
| Fibre strain | `9.888130219613×10⁻⁴` |
| `½⟨w'²⟩` | `1.388009729196×10⁻⁴` |
| `Γ_p` | `2382.263649` (printed `2.4×10³`) |
| `σ_max` | `13.9188 MPa` frozen, `13.6143 MPa` self-consistent |

V-C2 and V-C3 in `tab:validation` are the direct unit tests: free strip with uniform `θ`
(`σ_m = −Eαθ/3`) and with a linear gradient (`κ = (1+ν)αΔT_t/d > 0`, hot face convex); pinned strip
with constant eigen-curvature (`w_max = κ_thL²/8 > 0` **away from the channel**).

## 11. Open decisions that block completion

| ID | Decision | Blocks |
|---|---|---|
| **RU-01** | Casing standoff behind the heated face; vented or sealed cavity; contact or free | The entire baseline mechanics if not "free with clearance ≥ 0.44 H₀" |
| **RU-03** | State the deformed mid-span height (`1.4377 H₀` under the adopted convention) | Post-processing and any passage-geometry claim |
| RU-02 | Label `M` or `M_phys` (no numerical consequence) | Nothing |
| — | `h_K` for anisotropic elements; gauge implementation | Nothing, but must be **recorded per run** |

**Coding may begin on:** the fluid solver (V-A), the conjugate thermal solver (V-B), the
thermoelastic solver with V-C1/C2 unit tests, and the beam–column verification (V-C3). These do not
depend on RU-01.

**Coding must not begin on:** the coupled production runs, mesh convergence at the baseline, or any
`Γ_p`/stress headline figure — all of which inherit the RU-01 conditional.
