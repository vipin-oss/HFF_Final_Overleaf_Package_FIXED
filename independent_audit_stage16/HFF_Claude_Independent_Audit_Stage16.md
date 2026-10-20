# Independent audit — HFF Stage 16 implementation

**Auditor:** Claude (independent reviewer; no write access to, and no edits of, the audited sources)
**Repository:** `vipin-oss/HFF_Final_Overleaf_Package_FIXED`
**Branch audited:** `arena/c875f9b3-hff-final-overleaf-package-fix`
**HEAD verified before and after the audit:** `b63d34c145428ec7a07642fe5d551f34f50f2f14`
(`git rev-parse` on a fresh fetch; the branch had **not** advanced beyond the requested target).
**Previous audit:** `claude/independent-audit-7c9749f`, report `HFF_Claude_Independent_Final_Audit.md`,
baseline `7c9749f`.
**Date:** 2026-10-20.

---

## 0. Verdict in one page

The Stage 16 work is a genuine implementation, not a rewrite of the report. Three of the four
mathematical corrections I asked for are correct and I can reproduce them independently (I-01, I-03,
I-04). Two are not: **the thermal stagger in I-05/I-06 reintroduces exactly the ill-posedness that
D-24 removed**, and **the test suite, though much stronger, is blind to equation-level mutation** —
24 of 25 of my adversarial mutants survive. The numerical corrections (I-08, I-09, I-10, I-11) are
arithmetically right, with two propagation gaps.

| Gate | Meaning (defined here, since the project defines none) | Verdict |
|---|---|---|
| **Gate A** — mathematics and internal consistency of the manuscript | **FAIL** |
| **Gate B** — verification integrity: do the tests catch a wrong document? | **FAIL** |
| **Gate C** — build, package and visual release readiness | **BLOCKED** (not attempted by the author; cannot be passed by me) |
| **Coupled production solver** | **NOT READY** |

Gate A fails on one new defect of substance (NEW-01: the solid's temperature level is claimed to be
fixed by a flux, which is false and contradicts the author's own ch05 and audit doc §5) and one
residual contradiction (NEW-05: chapters 4 and 11 still say the full-edge pin costs "a few per cent"
where D-26 measured 0.2 %).

Gate B fails because a passing count is not evidence: I altered the *governing equations* — the
moment boundary condition, the closed-form solution, the compatibility update, the buckling load, the
critical eigenvalue, the SUPG sign — and the suite reported **ALL 56 CHECKS PASSED** every time
except one.

### Findings at a glance

| ID | Item | Verdict |
|---|---|---|
| I-01 | Pin vs clamp | **CLOSED** (independently reproduced: 1.0000 / 0.9981 / −0.041…−0.045) |
| I-03 | `1/d` in the geometric term | **CLOSED** (dimensional + numeric 2-D→1-D reduction, ratio 1.0000) |
| I-04 | Pressure gauge | **CLOSED** (discrete identity verified; deletion correct) |
| I-05/I-06 | Thermal stagger + SUPG | **PARTIALLY CLOSED** — SUPG acceptable; stagger is ill-posed (NEW-01) |
| I-07 | Vacuous tests | **PARTIALLY CLOSED** — 6 named mutants caught, 24/25 adversarial mutants escape |
| I-08 | Stress values | **CLOSED** (13.0091 / 13.9165 MPa reproduced; frozen > self-consistent; 13.6 withdrawn) |
| I-09 | Strain envelope | **CLOSED** (3.2472e-3 / 5.3472e-3 reproduced) |
| I-10 | θ̄ rounding | **CLOSED as a document matter** — but the test and its report describe a number that does not exist (NEW-02) |
| I-11 | `Γ_p` interpretations | **PARTIALLY CLOSED** — ch04 correct; appendix, ch06 and ch07 still print the mixed value unlabelled |
| I-12 | Stale ZIP | **CLOSED** (ZIP + manifest match; SHA verified) |
| I-13 | Provenance | **PARTIALLY CLOSED** — staleness is now declared; the PDF is still stale, so Gate C cannot pass |
| I-15 | Figure collisions | **NOT VERIFIED** — no renderer available; structural checks only |
| NEW-01 | Solid pure-Neumann in the stagger | **NEW DEFECT (critical)** |
| NEW-02 | θ̄ check compares to a hardcoded literal; the report claims a printed 32.27 K that is absent | **NEW DEFECT (test integrity)** |
| NEW-03 | No-gauge paragraph cites register D-25 (the erroneous entry) instead of D-30 | **NEW DEFECT (minor)** |
| NEW-04 | D-26's Q8 evidence is not in the repository and is not reproducible from it | **NEW DEFECT (evidence provenance)** |
| NEW-05 | ch04 and ch11 still claim "a few per cent" stiffening, contradicting D-26's 0.2 % | **NEW DEFECT (contradiction)** |

---

## 1. Scope and what was actually executed

**Executed by me** (scripts archived in `evidence/`, all run against a clean checkout of `b63d34c`):

| Check | Script | Result file |
|---|---|---|
| Full independent re-derivation of every printed baseline number | `verify_numerics.py` | `output_numerics.txt` |
| 25 adversarial source mutations, each in an isolated copy, scored against the suite | `mutation_campaign.py` | `output_mutations.txt` |
| Independent Q8 plane-strain FE: pin / point-pin / clamp, with derivative, patch and exact-field tests | `q8_pin_verification.py` | `output_q8_pin.txt` |
| Discrete gauge functional and 2-D→1-D reduction of the geometric term | `gauge_and_geometric_term.py` | `output_gauge_geom.txt` |
| The authors' own suite and mutation harness, re-run from a clean tree | `audit_stage15/regression.py`, `audit_stage15/mutation_test.py` | reproduced: 56/56 pass, 6/6 mutants caught |

**Not executed, and not claimed:**

- **No LaTeX compilation.** No TeX engine exists in this environment. I did not rebuild the PDF and
  I assert nothing about the typeset result (page count, reference resolution at typeset time,
  overfull boxes). I checked source-level structure only.
- **No figure rendering.** `fig_geometry.tex` was reviewed as source; whether labels collide at final
  scale is a visual judgement I cannot make here. I-15 therefore stays open.
- **No coupled solver run** (none exists), and no coupled 2-D FSI computation.

Raw counts from source: 88 unique labels, 0 dangling references, 31 register rows (D-01…D-31),
braces/environments balanced in all 16 source files, every `.bib` key cited and every citation
resolvable (reproduced with the authors' Section 1, and spot-checked by me).

---

## 2. I-01 — pin, not clamp — **CLOSED**

### 2.1 What the source now says

`ch02` A9, `ch05` B7 and `ch08` `V_s` all state the same condition:

    d2 = 0 on the end edges,  <d1> = 0 (edge mean),  zero applied moment (natural)

and all three explicitly exclude `d1 = d2 = 0`. `V_s` is written as

    V_s = { φ ∈ [H¹(Ω_s⁰)]² : φ₂ = 0 on Γ_end ,  ∫_{Γ_end} φ₁ dY = 0 }

### 2.2 My re-derivation

*Subspace test.* The constraints are homogeneous (linear and vanishing at zero), so `V_s` is a closed
linear subspace of `[H¹]²` — conforming Galerkin applies without a multiplier. ✓

*Rotation is not blocked.* Take `φ₂ = 0` and `φ₁ = -φ (Y - d/2)`. Then `φ₂ = 0` on the end edges and
`∫φ₁ dY = -φ[d²/2 - d²/2] = 0`, so the field is admissible, while `φ ≠ 0` is a section rotation
carried by the linear-in-`Y` axial displacement. A clamp (`φ = 0` pointwise) would exclude it.
This is the exact sense in which the new condition is a **hinge at mid-thickness**, not a clamp. ✓

*Rigid modes.* The three in-plane rigid modes are (i) translation in `X` — killed by
`∫φ₁ dY = 0`; (ii) translation in `Y` — killed by `φ₂ = 0`; (iii) rotation about `Z`, whose
`φ₂ = φ(X - X₀)` is nonzero at both `X = 0` and `X = L` unless `φ = 0` — also killed. So the
elasticity problem has no zero-energy mode: the discrete system is non-singular. ✓

*Compatibility with the weak form.* `eq:weaks` carries no Lagrange multiplier, so the mean condition
must be enforced on the space (a linear constraint equation). That is implementable and the document
says the mean is "taken as the mean over the edge"; it does **not** say how the discrete system
enforces it. Minor, not a defect, but a solver-spec line is missing.

*One honest addition the text does not make.* `φ₂ = 0` along the **whole** end edge also suppresses
through-thickness (Poisson) displacement at the ends, i.e. it forces `ε_YY ≈ 0` in an end layer.
This is precisely why the full-edge pin is 0.2 % stiffer than a point pin, and the document's own
numbers show that — but the text attributes the difference only to "full-edge versus corner",
without naming the mechanism.

### 2.3 Independent numerical reproduction (my own FE, not theirs)

New 8-node serendipity plane-strain program (`evidence/q8_pin_verification.py`), written for this
audit, with three gates that must pass before any result is read:

1. analytic shape-function derivatives vs central differences: max error `4.5e-11`;
2. the exact zero-stress free-bending field satisfies the assembled equations:
   `max |K u_ex − f| = 1.4e-9` against a load scale of `1.9e4` (i.e. machine precision);
3. the point-pin case reproduces the beam value exactly: fitted curvature ratio `1.0000`.

Load: linear through-thickness temperature with zero mean, so the strip is in pure thermal bending;
the plane-strain thermal law uses the **effective** eigenstrain `(1+ν)αθ` (using `αθ` instead gives a
spurious factor `1/(1+ν)` — a trap worth naming, because it is easy to get wrong in a solver).

| Support | `w_mid / (κ_th L²/8)`, mid-thickness | `w_mid / (κ_th L²/8)`, fluid-side face |
|---|---|---|
| point pin, mean axial blocked | 1.0025 | **1.0000** |
| full-edge `d₂ = 0` + edge-mean `d₁ = 0` (**the adopted condition**) | 1.0006 | **0.9981** |
| full-edge `d₁ = d₂ = 0` (clamp) | −0.0408 | **−0.0450** |

This reproduces the document's claim — "1.0000 point pins, 0.998 full-edge vertical support,
−0.02 to −0.06 for a clamp" — to the quoted precision. **The physics claim is confirmed**, and the
clamp really does annihilate the mechanism rather than reduce it by a few per cent.

**Caveat (NEW-04).** The program that produced the document's numbers is **not in the repository**.
`audit_stage15/` contains `regression.py`, `mutation_test.py`, `build_package.py` and
`calc_register.py` — no FE code, no input deck, no output log. Register D-26 and A9 cite results a
reader cannot reproduce. My run above closes that gap for me; it does not close it for the package.

**Smallest correction:** commit the Q8 program, its input deck and its console output under
`audit_stage15/evidence/`, and cite it from D-26 and A9. Optionally adopt the two-line
through-thickness explanation in §2.2.

---

## 3. I-03 — the `1/d` factor — **CLOSED**

### 3.1 Units

`N_θ^c` is a hoop force per unit length (N/m). In `eq:weaks` the term

    −∫_{Ω_s⁰} (N_θ^c/d) ∂_X d₂ ∂_X φ₂ dX dY

has `(N/m)/m · 1 · 1 · m² = N` per unit depth, matching `∫σ:ε dX dY = Pa·m² = N` on the same line.
The pre-Stage-16 form without `/d` was `N/m` — off by `1/d`. ✓

### 3.2 The 2-D → 1-D reduction, verified numerically

Integrating across the thickness must give `N_θ^c ∫ w' φ' dX`. I assembled the 2-D term with the
actual Q8 mesh (24 elements) and compared it with the 1-D integral for `d₂ = sin(πX/L)`,
`φ₂ = X(L−X)`, `N = 2.9e4 N/m`:

    2-D assembly = 1.10772021e+03
    N × 1-D integral = 1.10771840e+03
    ratio = 1.0000016

So the `/d` is exactly what makes the 2-D term equal the intended 1-D term. Without it the 2-D term
is a factor `d = 3×10⁻³` of the intended value: in SI units the geometric stiffness would simply
disappear, which is what the corrected text says. ✓

The supporting claim that the coefficient is "a uniform pre-stress `σ₀ = −N_θ^c/d`" is also correct
for a uniaxial membrane state: only `∂_X d₂ ∂_X φ₂` appears, which is the right geometric stiffness
for a uniaxial force (a biaxial force would add `∂_Y` terms).

**Verdict: CLOSED.** `d` cancels identically — the *number* does not change, only the
dimensional bookkeeping; the document now says exactly that, and does not present it as a numerical
correction. That framing is honest and I confirm it.

---

## 4. I-04 — pressure gauge — **CLOSED**

Their argument: constants are not in `ker b(·,1)` because

    b(v,1) = −∫_{Ω_f} ∇·v = −∫_{Γ_out} v·n ds ≠ 0.

**Continuous.** Correct, provided some admissible test function has nonzero normal component on
`Γ_out`. With Dirichlet data on inflow and walls and only the do-nothing condition at `Γ_out`,
such functions exist. ✓

**Discrete.** I assembled the Q8 velocity / element-wise-constant pressure divergence operator on the
same channel mesh and evaluated `(Bᵀ1)_j` for every velocity node:

    interior nodes:            max |(Bᵀ 1)| = 4.9e-18     (exact cancellation)
    inflow / outflow nodes:    max |(Bᵀ 1)·n| = 1.0e-3
    outflow nodal values:      2.5e-4, 1.0e-3, 5.0e-4, 1.0e-3, 2.5e-4   (= the edge flux weights)

So the constant pressure is **not** annihilated: there is no gauge freedom to remove, and deleting
`∫_{Γ_out} p ds = 0` is right. The counterfactual also checks out in the same computation: if
`Γ_out` were Dirichlet, every test function would vanish there and the outflow weights would be
zero — constants *would* be in the kernel. The condition B2 rewording ("the level p→0 there is an
output, not an imposed datum") is consistent with this.

**Consequence their text states correctly:** adding a scalar constraint to a system that already has
full column rank makes it rank-deficient by one — the constraint does not "fix" anything, and with a
multiplier it injects an outlet mass source. ✓

**Verdict: CLOSED.** One citation slip (NEW-03, §11).

---

## 5. I-05 / I-06 — SUPG and the thermal stagger — **PARTIALLY CLOSED**

### 5.1 SUPG — acceptable

`eq:supgwf` adds `Σ_K ∫_K τ_K (u·∇χ) R(T_f) dx` with `R = ρc_p u·∇T_f − k_f∇²T_f` to the energy
equation only. Units: `[s][1/s][W/m³][m³] = W`, matching the other terms. Consistency: `R = 0` for
the exact solution, so the term vanishes and the scheme is consistent. The `h_K → h_K/p` caveat for
`P2` is stated and is the right thing to say: the classical `h_K/(2|u|)` is the 1-D optimal value for
linear elements, and keeping the bracket at `p = 2` is a robust choice, not an optimum. The claim that
the interface cancellation is unaffected is correct because the stabilisation carries no boundary
term and the flux condition is untouched.

*Small observation, not a defect:* calling `h_K/p` "the effective length scale" is a heuristic
(the `1/p` scaling is not exact for all element types); the text already refuses to call it optimal,
so it is honest as written.

### 5.2 The stagger — **NEW DEFECT (critical)**

`ch08` (the iteration list) now reads:

> "At this stage the interface temperature `T_Γ^(k)` is a **Dirichlet datum** on `Γ_if`, and the
> resulting interface flux is extracted as `q_Γ^(k) = −k_f ∇T_f^(k)·n`; … transfer to the solid
> (i) the pressure-dominated traction … and (ii) the interface flux `q_Γ^(k)` as a **Neumann datum**
> on `Γ_if`. Neither side is ever left with Neumann data on its whole boundary: the solid
> additionally carries the prescribed flux `q''` on `Γ_h⁰`, **so its temperature level is fixed**."

The last clause is false, and it contradicts two places in the authors' own corrected text:

- `ch05` (lines 76–83, the D-24 repair): "prescribing a conjugate flux on the solid side in place of
  it, would be inadmissible: the solid carries the prescribed flux on the whole outer face `Γ_h⁰`
  and zero flux on its remaining faces, so a flux datum on `Γ_if` would leave the solid subproblem
  **pure-Neumann, its temperature level undetermined up to an additive constant**, and that constant
  would propagate into the membrane force `N_θ` (register D-24)."
- `audit_stage15/04_weak_form_and_bc_verification.md` §5: the same statement, with the explicit
  words "**ill-posed as stated**".

**The mathematics.** A pure-Neumann steady conduction problem `−∇·(k_s∇T_s) = 0` with data
`∂ₙT_s` prescribed on the *whole* boundary:

- is solvable only if `∮ k_s ∂ₙT_s = 0` (compatibility), which in the stagger holds only *at* the
  fixed point, not at iterate `k`;
- when solvable, has the one-parameter family `T_s + C`, because the constant is in the kernel of the
  Neumann operator;
- therefore `q''` does not and cannot fix a *level*. A flux is a gradient datum; only a Dirichlet
  trace, a Robin condition, or a reaction/regularisation can pin `C`.

**Why it matters here, quantitatively.** `N_θ = −E d α θ̄/(1−ν)` and the whole beam–column chain is
driven by `θ̄` (32.3 K). A free additive constant in `T_s` shifts `θ̄` by that constant and therefore
`N_θ`, `μL`, `w_max`, `σ_max` and `M_b`. The authors' own text says so ("that constant would
propagate into the membrane force `N_θ`"). At the level of the iteration the defect also shows up as
non-compatibility of the solid subproblem at `k < ∞`: unless the transferred `q_Γ^(k)` happens to
have zero net flux, the discrete Neumann problem is *unsolvable* (`q''` in, `q_Γ` out, no balancing
term), so a solver will either fail or silently project the flux.

**What is already right.** The monolithic weak form (`eq:supgwf` + `eq:weakts` with the interface
terms cancelling) is well posed: there the interface temperature is a single shared unknown, the flux
jump is the natural condition, and the level is anchored by the fluid inflow Dirichlet datum. The
defect is confined to the *staggered algorithm* described in `ch08`, which is the text a solver
implementer will follow.

**Smallest correction.** Replace the claim and the data transfer with one of:

1. **Preferred (matches `ch05` D-24):** solve the *solid* with the interface **temperature** as a
   Dirichlet datum and extract `q_Γ^s`; solve the *fluid* with `q_Γ` as a Neumann datum and extract
   `T_Γ^f`; close the loop on the flux jump `‖q_Γ^f + q_Γ^s‖`. (This is the fluid/solid reversal of
   the current text; it keeps the level anchored by the solid's Dirichlet datum, but then the fluid
   must not also have a Dirichlet interface datum — check the fluid's own well-posedness.)
2. **Or:** keep the present split but add the explicit statement that the solid subproblem is
   solved *up to a constant* fixed by the interface-temperature continuity from the previous
   iterate, i.e. `T_s ← T_s − mean_Γ(T_s − T_Γ^(k))`, and that the flux balance is then enforced by
   alternation. This is defensible but must be written down as part of the algorithm, because the
   constant is a modelling choice, not a consequence.
3. **Or:** anchor `T_s` with a reference-temperature Dirichlet condition on a non-physical cut,
   explicitly flagged as a regularisation, with a sensitivity check.

Option 1 is the only one that removes the freedom rather than managing it. Whatever is chosen, the
sentence "so its temperature level is fixed" must go.

---

## 6. I-07 — are the tests non-vacuous? — **PARTIALLY CLOSED**

The suite is genuinely better than v1: it now parses inputs and printed values out of the `.tex` and
recomputes, so corrupting a printed number or a material constant breaks it. I verified this:

    $ python3 audit_stage15/regression.py      -> ALL 56 CHECKS PASSED
    $ python3 audit_stage15/mutation_test.py   -> BASELINE PASS, m1..m6 all CAUGHT

**That claim is true.** But it is a claim about *six chosen mutations*, five of which are caught by
one or two string checks. I therefore wrote my own campaign aimed at the mathematics
(`evidence/mutation_campaign.py`), each mutation applied to an isolated copy, keeping all superficial
phrasing intact:

| # | Mutation (mathematics) | Suite verdict |
|---|---|---|
| A1 | moment BC `w''(0)=w''(L)=−κ_th` → `−κ_th/2` | **ESCAPED** |
| A2 | `eq:beamcolsol` particular integral halved | **ESCAPED** |
| A3 | `eq:nupdate` loses the factor 2 | **ESCAPED** |
| A4 | `eq:wmax` `κL²/8` → `κL²/12` | **ESCAPED** |
| A5 | printed `θ̄ = 32.3 K` → `34.3 K` | **ESCAPED** |
| A6 | water viscosity `1.0e-3` → `2.0e-3` (whole pressure chain) | **ESCAPED** |
| A7 | imposed flux `5.0e3` → `6.0e3` (whole thermal chain) | **ESCAPED** |
| A8 | a gauge constraint re-inserted in different notation | **ESCAPED** |
| A9 | `V_s` integral condition `= 0` → `= 1` (not a subspace) | **ESCAPED** |
| A10 | SUPG term sign flipped | **ESCAPED** |
| A11 | register D-31 reverts to the withdrawn false claim | **ESCAPED** |
| A12 | ch07 table `Γ_p = 2.9e3` | **ESCAPED** |
| A13 | appendix `σ_bend = 5.2 MPa` | **ESCAPED** |
| A14 | appendix circular-arc estimate `1.6e-4` → `1.9e-4` | **ESCAPED** |
| A15 | ch11 stiffening claim reversed ("order one") | **ESCAPED** |
| A16 | explanatory `N_θ^c/d` → `N_θ^c/(2d)` (equation untouched) | **ESCAPED** |
| A17 | thermal loop closure removed, both keywords kept | **ESCAPED** |
| A18 | beam–column ODE sign flipped (`+N w''` → `−N w''`) | **ESCAPED** |
| A19 | ch07 conservative stress `13.9` → `14.9` | **ESCAPED** |
| A20 | appendix mid-span moment `−6.4` → `−8.4` N·m | **ESCAPED** |
| A21 | A9 reverted to a clamp, B7 untouched | **ESCAPED** |
| A22 | convective term sign flipped in `eq:weakf` | **ESCAPED** |
| A23 | `N_cr` uses the clamped eigenvalue `4π²D_s/L²` | **ESCAPED** |
| A24 | printed `μL = 2.65` | **ESCAPED** |
| A25 | ch09 benchmark amplification `1.39` → `1.29` | caught |

**24 of 25 escape.** The pattern is diagnostic, not random:

- the suite checks **printed numbers** and **a handful of strings**, never the **displayed equations**,
  which is where the mathematics lives (`eq:beamcol`, `eq:beamcolsol`, `eq:nupdate`, `eq:wmax`,
  `eq:weakf`, `eq:supgwf`, `V_s`);
- `Section 5` "exact identities" does not read the source at all — it re-checks the authors' own
  formulas against themselves, so a mutated equation passes while the identity still holds;
- loads and geometry (`q''`, `μ`, `L`, `d`, `H₀`, `Nu`) are **not parsed**, so the entire thermal and
  hydraulic chains are unguarded (A6, A7);
- several checks are anchored to one specific value (`near(C4,'w_{max}=2',…)`), so a different
  corruption of that same number can slip past the anchor.

**Smallest correction:** treat the equations as data. Extract each displayed equation as a string
with `\label`, normalise whitespace, hash it, and assert the hash against a recorded value — that is
cheap, mechanical, and catches exactly A1–A4, A18, A22, A23. Add the remaining material constants
(`q''`, `μ`, `L`, `d`, `H₀`, `κ_s` …) to the parsing block so the recompute is driven by the
manuscript and not by module-level literals. Then re-run my campaign as the acceptance test for the
suite: the suite is adequate when at least the A1–A4, A9, A10, A18, A22, A23 group is caught.

---

## 7. I-08, I-09, I-10 — numerics — **CLOSED** (with one test-integrity defect)

Independent re-derivation from the printed inputs (`evidence/output_numerics.txt`):

| Quantity | Printed | Mine | rel. |
|---|---|---|---|
| `θ̄` | 32.3 K | 32.2652 | 1.1e-3 |
| `Δp` over strip + exit length | 120 Pa at inlet, 48 Pa at `x=L` | 120.0 / 48.0 | — |
| `p̄` over the strip | 84 Pa | 84.0 | — |
| `D_s` | 9.64 (9.6) N·m | 9.64286 | — |
| `κ_th` | 1.4 1/m | 1.400 | — |
| `N_θ` | −2.91e4 N/m | −2.90387e4 | 2e-3 |
| `N_cr` | 1.057e5 N/m | 1.05746e5 | 4e-4 |
| `M_b` | 3.64 | 3.6417 | 5e-4 |
| `μL` | 1.65 | 1.6463 | 2e-3 |
| `w_max` frozen | 2.19e-4 m (0.438 H₀) | 2.18858e-4 (0.43772) | 6e-4 |
| `w_max` linear | 1.575e-4 m | 1.57500e-4 | 0 |
| amplification | 1.39 (1.38 leading order) | 1.38957 (1.37857) | 4e-4 |
| `M_mid` frozen | −6.4 N·m | −6.35535 | 7e-3 |
| `σ_bend` frozen | 4.2 MPa | 4.2369 | 9e-3 |
| `w'_max` | 0.027 rad | 0.027515 | 2e-2 |
| fibre strain | 9.9e-4 | 9.8861e-4 | 1e-3 |
| `½⟨w'²⟩` exact | 1.39e-4 | 1.38785e-4 | 2e-3 |
| circular-arc estimate | 1.6e-4 | 1.58992e-4 (14.6 % above exact) | 6e-3 |
| first-iterate relaxation | 6.1 % | 6.1449 % | 7e-3 |
| `e_0` | 2.26e-3 | 2.25856e-3 | 6e-4 |
| `max|ε_mech|` | 3.25e-3 | 3.24717e-3 | 9e-4 |
| envelope `e₀ + κ_geo d/2` | 5.35e-3 | 5.34717e-3 | 5e-4 |
| `w_max` self-consistent | 2.14e-4 m (0.428 H₀) | 2.13988e-4 (0.42798) | 6e-5 |
| frozen overprediction | 2.3 % | 2.276 % | 1e-2 |
| `N_θ^c` self-consistent | 2.733e4 N/m | 2.73306e4 | 2e-5 |
| `σ_memb` frozen / self-consistent | 9.68 / 9.11 MPa | 9.6796 / 9.1102 | 5e-5 |
| `σ_bend` self-consistent | 3.9 MPa | 3.8989 | 3e-4 |
| `σ_max` frozen | 13.9 MPa | 13.9165 | 1e-3 |
| `σ_max` self-consistent | 13.0 MPa (0.145 σ_y) | 13.0091 | 7e-4 |
| `w_p` linear | 9.2e-8 m | 9.1875e-8 | 1e-3 |
| `Γ_p` mixed | 2.4e3 | 2382.1 | 7e-3 |
| `w_p(N_θ^c)` beam–column | 1.27e-7 m | 1.26778e-7 | 2e-3 |
| `Γ_p` like-for-like | 1.73e3 | 1726.3 | 2e-3 |

Every printed value reproduces. The two stress columns are genuinely two states of the same model,
the frozen value is genuinely the larger (conservative), and the withdrawn `13.6 MPa` is correctly
described as belonging to neither. `Γ_p`'s two definitions are both correct and both `≫ 5`.

**I-10 (θ̄):** the document prints **32.3 K** (appendix A5, ch07 table). My recompute is 32.2652,
which rounds to 32.3. Fine. But the suite's check is

    check("theta_bar within 0.05 K of printed 32.27", abs(thbar-32.27) < 0.05, thbar)

and **the string `32.27` does not occur anywhere in the manuscript** (`grep -rn "32\.27" chapters/`
returns nothing). The check is a comparison against a literal in the script; `audit_stage15/06_…`
even records it as "printed 32.27 K" in a table. This is NEW-02: a check that cannot fail when the
*printed* value changes, and a report that states something about the manuscript that is not true.

**Smallest correction:** print `32.3` in the source (or 32.27 if that precision is wanted) and parse
it; correct the row in `06_regression_results.md`.

---

## 8. I-11 — `Γ_p` — **PARTIALLY CLOSED**

`ch04` is now correct and complete: `Γ_p` is labelled a **mixed** ratio, the reason is given, and the
like-for-like alternative `w_p(N_θ^c) = 1.27e-7 m` → `1.73e3` is printed, with the observation that
it "essentially" recovers the linear-limit value. I reproduced all of it.

What did not propagate:

| Location | Text | Problem |
|---|---|---|
| `appendix.tex` A8 | `Γ_p = 2.19e-4/9.2e-8 = 2.4e3` | the mixed value with no label; A8 is the *arithmetic* appendix |
| `appendix.tex` (dictionary) | `Γ_p ... 2.4e3` | no label |
| `ch06` A-5 | `Γ_p ≥ 5` classified as thermally driven | criterion defined on an unlabelled ratio |
| `ch07` table | `2.19e-4/9.2e-8 = 2.4e3 (≥5, A-5 met)` | no label |
| `ch07:87` | "`Γ_p ≈ 2.4e3` at the …" | no label |

The conclusion (thermal dominance) is unaffected because both definitions exceed 5 by two orders of
magnitude — I checked that — but a reader who consults only `ch07` or the appendix sees the mixed
number presented as if it were a homogeneous ratio, which is the finding I raised.

**Smallest correction:** one parenthetical at each of the five places — "(mixed ratio; like-for-like
`1.73e3`, `ch04`)" — and define A-5 on the *like-for-like* value, which is the conservative one.

---

## 9. I-12 / I-13 — package and provenance — **I-12 CLOSED, I-13 PARTIALLY CLOSED**

Verified directly:

    HFF_Final_Overleaf_Package.zip
    sha256  cf0df92ebe8f1e1bd6bdc194f9ce367c6a5dfc081efc3491357348895c36514c
    size    770159 bytes, 70 members
    manifest audit_stage15/package_manifest.txt: sha256 matches the archive

Every filename named in `README.md` exists; the ZIP contains `main.tex`, `references.bib`,
`main.pdf`, `README.md`, `chapters/`, `figures/`, `audit_stage15/` and `project_archive/`. The
manifest sits beside the archive (it cannot contain its own hash), which the README explains.
I-12 is closed.

I-13 is **declared but not closed**: `main.pdf` predates every Stage 16 source file. The README says
so, and `regression.py` §7 reports rather than asserts it — both are the right behaviour, and I
credit it. But the package still ships a PDF that does **not** contain D-26…D-31, and the declared
page count (49) will change. That is a release blocker, not a document defect: it cannot be closed
by text.

---

## 10. I-15 — the figure — **NOT VERIFIED**

I have no TikZ/LaTeX renderer. I inspected `figures/fig_geometry.tex` as source: the rewrite replaces
the collision-prone annotations with shaded lid blocks and external labels, and moves the flux arrows
above the bow. That is the right shape of fix, but "labels no longer collide" is a statement about
rendered output, and I will not sign it off from source. **Verdict: OPEN (unverified).**
Smallest correction: compile once with a real TeX installation and attach the page image; then the
claim is checkable by anyone.

---

## 11. New defects — details and smallest corrections

### NEW-01 — the solid is pure-Neumann in the staggered algorithm (**critical**)
See §5.2. `ch08` iteration step 2 claims the solid's "temperature level is fixed" by the imposed
flux `q''`; a flux cannot fix a level. It contradicts `ch05:76–83` (D-24) and the authors' own
`audit_stage15/04_…` §5, which calls the same construction "ill-posed". Affected: the well-posedness
of the coupled algorithm and, through `θ̄`, every membrane-force-dependent number.
**Smallest correction:** restate the data transfer so that the solid receives a *temperature* datum
(or a regularising anchor) and the fluid receives the flux; delete the sentence about the level.

### NEW-02 — a check that cannot see the manuscript (**test integrity**)
`regression.py` compares `θ̄` to a hardcoded `32.27` that appears nowhere in the sources; the
manuscript prints `32.3`. `06_regression_results.md` reports it as "printed".
**Smallest correction:** parse the printed value; fix the report row.

### NEW-03 — register citation slip
`ch08`'s no-gauge paragraph ends "(register D-25)". D-25 is the entry that *introduced* the gauge
constraint; the correction is **D-30**. D-25 is already annotated as superseded, so the pointer is
merely wrong, not contradictory.
**Smallest correction:** `(register D-25, corrected in D-30)` or `(register D-30)`.

### NEW-04 — unshipped Q8 evidence
D-26 and A9 quote Q8 results (`1.0000`, `0.998`, `−0.02…−0.06`) that no file in the repository can
reproduce; the program and its output are not committed. The numbers are **correct** — I reproduced
them with an independent implementation (§2.3) — but the package does not carry the evidence.
**Smallest correction:** commit the program, input deck and console output; cite from D-26/A9.

### NEW-05 — residual "few per cent" claims contradict D-26
`ch04:165–167`: "The full-edge pin idealization … stiffens the ends by `O(d/L)` … the catalogue is
therefore read as accurate to a few per cent at the baseline aspect ratio, with the one-time
numerical check of Chapter 5 closing the residual."
`ch11:26–28`: "carries an `O(d/L)` stiffening relative to ideal point pins — a few per cent at the
baseline aspect ratio — closed by the one-time numerical check".
D-26 measures **0.2 %** and the check is **done**, not pending. Both sentences are leftovers of the
pre-correction narrative and contradict the chapter the correction lives in.
**Smallest correction:** replace "a few per cent … closing the residual" with "0.2 % at the baseline
aspect ratio (D-26), which is negligible; the check is complete" in both places.

---

## 12. Casing, contact and ventilation (item 10) — author decisions, not defects

These are unchanged and I am not inventing answers:

| Question | State in the source | Why it cannot be closed here |
|---|---|---|
| RU-01 radial casing clearance | no gap is specified anywhere (`grep` over all sources) | three distinct interpretations (no contact / crown contact / distributed contact) differ by an order of magnitude in the effective support stiffness |
| vent vs sealed cavity | not stated | changes the outer-face pressure by an order of magnitude; `p̄ = 84 Pa` is the load datum *if* the cavity is at the outlet level |
| heater mounting | `q''` is applied to `Γ_h⁰` without saying which face or how it is bonded | determines the sign of the thermal gradient, hence the bow direction — currently justified kinematically, not from hardware |
| contact law | absent | needed only if RU-01 resolves to contact |
| pin idealisation | point pin vs rigid end face | now quantified: 0.2 % (D-26 and §2.3) — the *decision* remains open, the *magnitude* no longer does |
| `Γ_p` headline definition | both printed | mixed `2.4e3` or like-for-like `1.73e3`; conclusion identical, presentation differs |
| RU-03 mid-span `1.4377 H₀` | flagged open | not re-litigated here |

Two of these are now *cheaper* to close than before: the pin decision is bounded to 0.2 %, and the
`Γ_p` decision is bounded to a factor 1.4 in a quantity that exceeds its threshold by 300×.

---

## 13. Gate verdicts and blockers

### Gate A — mathematics and internal consistency: **FAIL**
Blocks: NEW-01 (thermal well-posedness; contradicts D-24 and `ch05`), NEW-05 (two chapters still
carry the pre-correction stiffening claim). Everything else I checked at the equation level
(`eq:beam`, `eq:beamcol`, `eq:beamcolsol`, `eq:nupdate`, `eq:kappa`, `eq:weaks`, `eq:weakf`,
`eq:supgwf`, the function spaces, the pressure chain) is dimensionally consistent and internally
coherent, and every printed number reproduces.

### Gate B — verification integrity: **FAIL**
Blocks: 24/25 adversarial mutants escape; the `θ̄` check is phantom; the Q8 evidence is unshipped.
The suite is a good *regression* guard for printed values and a poor *correctness* guard for
mathematics. This is a fixable engineering gap, not a research gap.

### Gate C — build, package, visual: **BLOCKED**
Blocks: no LaTeX rebuild exists for the Stage 16 sources (the shipped PDF is pre-correction);
I-15 is unverified as rendered output. The package (ZIP, manifest, hash, README) is otherwise sound
and internally consistent.

### Coupled production solver: **NOT READY**
Exact blockers, in the order I would clear them:

1. **NEW-01** — the staggered thermal data transfer must be re-specified so the solid's temperature
   level is determined (or explicitly anchored), and the "level is fixed by `q''`" claim removed.
   Until then the coupled algorithm is under-determined and the membrane force inherits a free
   constant.
2. **Author physics (RU-01, vent, heater mounting, contact law)** — unchanged; each changes the
   numbers, not the text, and none may be chosen to preserve the current results.
3. **Gate B** — the verification suite must be able to fail on an equation-level error before any
   solver built against it can be trusted.
4. **Gate C** — a rebuild and one rendered figure page, so that what is being approved is what
   exists.

---

## 14. Statement of limitations

I did not modify the audited sources, did not merge anything, and did not run the authors' tooling
in a way that alters their tree (each mutation ran in an isolated copy under `/tmp`). I could not
compile LaTeX or render TikZ. My FE program is new code written for this audit; its own verification
(derivative check, exact-field residual, exact point-pin solution) is reported above, and its mesh is
coarse (24 Q8 elements) — it establishes the pin/clamp physics to the precision quoted, not a
converged solution of the strip problem. Where I report "reproduced", I mean: my independent
computation agrees with the printed value to the relative error shown in §7.
