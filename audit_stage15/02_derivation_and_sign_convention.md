# Stage 15 — Derivation and sign convention

**Scope.** This document re-derives the wall mechanics from the printed equations rather than
from earlier audit summaries, decides the deflection convention on evidence, and settles the
`9.8881×10⁻⁴` vs `−5.1888×10⁻³` discrepancy in closed form. Line references are to the tree at
commit `e8ef0d7`.

---

## 1. The two packages that were interleaved

The manuscript contained two mutually exclusive sign packages. They differ in **one** choice —
the sign of the transverse displacement — and everything else follows from it.

| Quantity | Package A (prose, captions, old figure) | Package B (algebra, BCs, validation) |
|---|---|---|
| Deflection | `w = −d₂`, positive **into** the channel | `w = +d₂`, positive **away** from the channel |
| Curvature | `κ = −w''`, positive bowing into channel | `κ = −w''`, positive bowing away |
| Eigen-curvature | `κ_th > 0` ⇒ bows into channel | `κ_th > 0` ⇒ bows away |
| Pin condition | `w''(0) = −κ_th` | `w''(0) = −κ_th` |
| Moment | `M = D_s(w'' + κ_th)` | `M = D_s(w'' + κ_th)` |
| Pressure term | `D_s w'''' = −p` | `D_s w'''' = +p` |
| `w_p` sign | positive into channel | positive away |

The critical observation is in the last four rows: **the algebra is identical in both columns.**
`w''(0) = −κ_th`, `M = D_s(w''+κ_th)`, `w = κ_th x(L−x)/2 ≥ 0` are the *same equations* under
either reading of what "positive `w`" means. So the equations alone cannot decide the package;
only the boundary conditions and the physical heating direction can.

An internal count of sign-bearing relations gave **nine** explicit to Package B and exactly
**one** to Package A: `ch03:140`, `D_s w'''' = −p`. That one equation was the single place where
the sign of the pressure term had been written consistently with the prose. It has been corrected
to `D_s w'''' = +p`.

## 2. Independent derivation of the pin condition

This is the step that decides the package, and it was not done explicitly in the manuscript.

Take the plane-strain strip, `x` along the wall, `y` through the thickness with `y > 0` on the
heated (outer) face, thickness `d`. The kinematic assumption consistent with the printed
`ε_xx = ε₀ + κy` (`ch04:95`) and `κ = −w''` (`ch02:131`) is

    ε_xx(x,y) = ε₀(x) − y w''(x).

The eigenstrain from a through-thickness gradient is `ε_th(y) = α_eff θ̄ + α_eff Γ y` with
`α_eff = (1+ν)α` and `Γ = ∂T/∂y`. The mechanical strain is `ε − ε_th`, so

    σ_xx = E/(1−ν²) · [ (ε₀ − α_eff θ̄) − y (w'' + α_eff Γ) ].

Define `κ_th ≡ α_eff Γ = (1+ν)α q''/k_s`. Then

    σ_xx = E/(1−ν²) · [ (ε₀ − α_eff θ̄) − y (w'' + κ_th) ].          (2.1)

The `y`-independent part integrates to zero over a symmetric section, so the first moment is

    M_phys ≡ ∫_{-d/2}^{d/2} σ_xx y dy = −D_s (w'' + κ_th),   D_s = E d³/[12(1−ν²)].   (2.2)

At a pinned end the *applied* moment is zero, so the physical first moment must vanish:

    M_phys(0) = 0  ⟺  w''(0) = −κ_th.                                  (2.3)

This is exactly the printed pin condition. **The printed pin condition is therefore a consequence
of Package B kinematics, not an independent assumption** — and it is not available under Package A,
because under A the `y`-coupling flips sign. That is the content of (2.1)–(2.3).

Quantitatively, evaluating the *other* pairing at the pins,

    D_s (w''(0) − κ_th) = 2 κ_th D_s = −27.000 N·m      (the A residual),

against a mid-span moment the strip actually carries of `−6.3567 N·m`. The alleged alternative
leaves a pin moment **4.25 times larger than the moment carried at mid-span**, and of the wrong
sign. No support condition permits that. This is now stated in the manuscript at `ch02:134`.

## 3. Independent physical test: which face is hotter

Heat enters through the outer face `Γ_h` at `q'' = 5×10³ W/m²` (A10, B6) and leaves into the fluid,
so the outer face is the hot face: `∂T/∂y > 0` with `y` measured outward.

A strip whose outer face expands more than its inner face becomes **convex on the outer side** —
the longer face is the outside of the arc. Hence the strip bulges *away* from the fluid, i.e.
`w > 0` under Package B. Equivalently, `κ_th > 0` means the hot face is convex, which is the
wording already used in validation test V-C2 (`ch09:43`).

**Package B is the physically correct one.** Package A was not merely a labelling convention: as a
package it predicts the strip bowing the wrong way, which would partially close the passage under
heating.

## 4. Consequence that must not be buried: the rigid casing

This direction has a physical consequence the manuscript had not previously had to face. A9 says
the casing is *rigid* and its interior pressure equals the outlet datum. Under Package B the strip
bows **into the casing side** by

    w_max = 0.4377 H₀ = 2.189×10⁻⁴ m ≈ 0.219 mm.

The standoff behind the heated face is **nowhere stated in the source**. Three readings exist, and
they are not equivalent (this is RU-01, carried to the ledger):

| Reading | Consequence if adopted |
|---|---|
| `R1` Vented cavity, standoff > `w_max` | Current model valid as written; `p̄ = 84 Pa` from casing at `p = 0` |
| `R2` Sealed cavity (fixed mass of gas) | Back pressure rises with the bow; net load `p_fluid − p_cavity`; `w_max`, `Γ_p` and the stress all change; the linear model is no longer exact |
| `R3` Contact (no standoff, or `< w_max`) | The bow is physically blocked; the frozen-force beam–column solution is *invalid*, not merely approximate. `κ_geo`, the arc term `1.39×10⁻⁴`, and the fibre strain all change |

`R1` is the only reading under which every number in the manuscript stands. It is also the reading
the text *leans towards* ("casing at the same reference pressure", `ch04:287`), but it never states
a standoff, so `R1` is inferred rather than given. Per the protocol this is **not** to be chosen on
the grounds that it preserves the numbers; it is recorded as an author decision with the three
branches above. All baseline mechanical results are conditionally valid pending that decision.

## 5. The `9.8881×10⁻⁴` vs `−5.1888×10⁻³` discrepancy — closed form

These two numbers are not a rounding dispute. They are the two curvature pairings of §2:

    fibre strain (adopted)      (κ_geo − κ_th) d/2 = +9.888130219613×10⁻⁴
    naive-flip value            −(κ_geo + κ_th) d/2 = −5.188813021961×10⁻³

Their ratio is `5.247516878`, and it is **not a free number**. From the closed-form solution,
`κ_geo = κ_th sec(μL/2)` (verified to `2.2×10⁻¹⁶` at the baseline), so

    (κ_geo + κ_th)/(κ_geo − κ_th) = (1 + cos(μL/2))/(1 − cos(μL/2))
                                 = cot²(μL/4)
                                 = 5.247516878.

This is an identity in `μL` alone. It is **independent of `E`, `d`, `q''`, `θ̄` and every material
property**, so it cannot be tuned and it cannot be an artefact of the baseline chosen. Its limits
are `16/(μL)² → ∞` as `μL → 0` and `→ 1` as `μL → π`; at the baseline `μL = 1.646414286` it is
`cot²(0.411604) = 5.2475`.

**Root cause.** The wrong value arises if `κ_th` is subtracted with the sign that belongs to the
*other* convention, i.e. if the "curvatures subtract" rule of §2 is replaced by "curvatures add".
Because the two curvatures are within a factor `1.47` of each other, that error is not a small
perturbation — it changes both magnitude (by `5.25×`) and sign. It is the one place where a sign
slip is catastrophic rather than cosmetic.

**Disposition.** The adopted value `9.8881×10⁻⁴` is correct and is retained; the `−5.1888×10⁻³`
figure is withdrawn with this closed-form explanation attached, so that the correction can be
checked by a reader in one line rather than by trusting the register.

## 6. Moment convention, stated once

The manuscript's `M` (`ch04:191`) is defined sagging-positive:

    M ≡ −∫ σ_xx y dy = D_s (w'' + κ_th) = −M_phys.

The physical first moment that a support sees is `M_phys = −M`. **The pin condition is unchanged**,
because `M = 0 ⟺ M_phys = 0`; this is why the sign work in Stage 15 alters no numerical result.
The mid-span value `M = −6.3567 N·m` is a *hogging* moment in this convention, and the
"bending fibre strain" `(κ_geo − κ_th)d/2 > 0` is consistent with it: at mid-span
`σ_xx = −E y (w''+κ_th)/(1−ν²)` with `w'' + κ_th = −0.6592 < 0`, so the heated face is in tension.

## 7. What the convention change does *not* touch

Verified by inspection of every occurrence, not assumed:

- `ch05`, `ch06`, `ch08` contain no expression depending on the sign of `w`. The interface
  conditions `eq:ifkin`–`eq:ifflux` and the weak forms are written in terms of `d` and `T` only.
- `ch03:157–159` builds the fluid domain map from `ŵ = d`, so the geometry was **already**
  Package B. Adopting B removes a latent inconsistency between the beam chapter and the fluid
  domain construction; it does not introduce one.
- The buckling threshold `T̄_cr = 117.5 K`, `N_cr = 1.057×10⁵ N/m`, and `M_b = 3.64` depend on
  `|N_θ|` and are invariant.

## 8. Register cross-references

| Item | Document location |
|---|---|
| Convention, curvature, pin, pressure term, moment | D-21 |
| `Γ_p` definition and the two ratios | D-22 |
| Arc-stretching value | D-23 |
| Thermal data flow | D-24 |
| Weak form, gauge, geometric stiffness, SUPG, solver split | D-25 |
| Casing standoff (open) | RU-01, §4 above |
