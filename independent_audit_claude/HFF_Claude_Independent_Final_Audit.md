# HFF — Claude Independent Final Audit

**Auditor:** Claude (Sonnet 5.5), independent of Arena
**Date:** 2026-10-19
**Repository:** `https://github.com/vipin-oss/HFF_Final_Overleaf_Package_FIXED` (public, read-only anonymous access; nothing was pushed, merged or modified)
**Audited commit:** `7c9749f7e7d22978b44c29ede5c76aba4825733f` on `arena/c875f9b3-hff-final-overleaf-package-fix`
**Evidence directory (outside the repo):** `/home/claude/hff_independent_audit_evidence/` — every number below is reproducible from the scripts there (commands in Appendix A).

---

## 0. Result at a glance

**Overall verdict: `NOT READY — MATHEMATICAL OR TECHNICAL ERRORS`**

Arena's own verdict is `NOT READY — AUTHOR DECISION REQUIRED`, driven by one open item (RU-01, casing clearance), with every other blocker reported CLOSED. I agree that RU-01 is a genuine, unresolved author decision. I do **not** agree that everything else is closed: several of the items Arena marked CLOSED are wrong as written, and one pre-existing boundary-condition defect that nobody has caught would make the specified 2-D production model predict essentially **no bowing at all**.

| | Category | Result |
|---|---|---|
| A | Repository and commit integrity | `PASS — independently verified` |
| B | Sign convention and constitutive chain | `PASS — independently verified` |
| C | Numerical calculations | `PARTIAL — some evidence missing` (all headline values reproduce; one mislabelled value, one undefined quantity, false precision in tests — §4) |
| D | Casing and physical model | `BLOCKED — requires author decision` |
| E | Strong/weak formulation and boundary conditions | `FAIL — incorrect or inconsistent` |
| F | Regression suite | `FAIL — incorrect or inconsistent` (passes under 4 of 4 injected semantic faults) |
| G | Solver specification | `PARTIAL — some evidence missing` (modular prototype: yes, with 4 do-not-implement-as-written items; coupled production: no) |
| H | Current-source compilation | `PASS — independently verified` (clean build in this environment) |
| I | Final Overleaf package | `FAIL — incorrect or inconsistent` (ZIP and PDF both stale; no valid final package exists) |
| J | Reproducibility and provenance | `PARTIAL — some evidence missing` |

The five findings that matter most, in order:

1. **I-01 (new, blocking).** Source assumption A9 and condition B7 prescribe `d₁ = d₂ = 0` on the **entire** end edge, and Arena's new function space `V_s` encodes it (`φ = 0` on the pinned ends). That is a clamp, not a pin. A plane-strain FE computation I wrote independently gives a mid-span bow of **−0.02 × the beam value** with full-edge zero displacement, versus **1.0000 ×** with true pins. The manuscript's claim that this differs from point pins by "a few per cent" is false by roughly two orders of magnitude.
2. **I-02 (blocking, author).** The strip now bows *toward* the casing by 0.219 mm and the source never gives a clearance. Agreed with Arena.
3. **I-03 (new).** The geometric-stiffness term Arena added to the weak form (`ch08`, eq. `weaks`) is dimensionally inconsistent as printed — it is missing a factor `1/d`, so it equals `d` times the intended term (numerically 3×10⁻³ of it in SI units, i.e. the geometric stiffness is effectively dropped, and the error changes with the unit system). The sign is right.
4. **I-07 (test suite).** `regression.py` stays green when I (a) corrupt the printed baseline deflection, (b) flip the sign of the geometric-stiffness term, (c) reintroduce "bows toward the interior", (d) change the Poisson ratio in the property table. It also contains a vacuous assertion and cannot be the "37 checks" Arena reports (it has 44).
5. **I-12 (package).** The ZIP is byte-identical to the pre-correction baseline and the tracked PDF still says "positive into the channel". Correctly flagged by Arena — but no valid final package exists, and the root `README.md` names a ZIP that is not in the repository.

What Arena got right and I independently confirm: the sign-convention decision and its propagation, the −27 N·m residual under the old pairing, the arc-term correction (1.388×10⁻⁴), the Γ_p numbers, the beam–column closed form, the frozen/self-consistent distinction (with one caveat), the stale ZIP and PDF, and the RU-01 diagnosis.

---

## 1. Repository and commit evidence

| Claim | Verified? | Evidence |
|---|---|---|
| Repository and branch accessible | **Yes** | `git ls-remote --heads` returns exactly two heads: `main` → `5a255212…`, `arena/c875f9b3-…` → `7c9749f7…` |
| HEAD = `7c9749f` | **Yes** | `git rev-parse` on the fetched branch tip |
| Ancestry | **Yes** | `9066c3b` is an ancestor of HEAD; `git rev-list --count 9066c3b..HEAD` = **3** |
| `e8ef0d7` source corrections, 13 files | **Yes** | `--stat`: 13 files, 108 insertions, 41 deletions: `chapters/{appendix,audit_appendix,ch01–ch09}.tex`, `figures/fig_geometry.tex`, `main.tex` |
| `5861d4d` ten audit docs + two scripts | **Yes** | 12 files, 1550 insertions, all under `audit_stage15/` (10 `.md`, `calc_register.py`, `regression.py`) |
| `7c9749f` hash record | **Yes** | one-line change in `10_final_readiness_report.md` (`*(this commit)*` → `` `5861d4d` ``) |
| `origin/main` unchanged | **Yes, as far as observable** | `main` is a single commit `5a25521 "Initial Overleaf Import"`, which is the root ancestor of the Arena branch. No Arena commit has reached `main`. (I cannot see `main`'s history before my observation.) |
| Working tree clean | **Yes** | detached worktree at `7c9749f`: `git status --short` empty |
| Untracked files needed for reproduction | **None found** | both scripts and all 10 reports are tracked |

Full ancestry (newest first): `7c9749f` → `5861d4d` → `e8ef0d7` → `9066c3b` → `613d04d` → `37123ec` → `d449bc7` → `e76cc60` → `d52aeb1` → `6b07aea` → `dc571eb` → `1e8387d` → `a413e54` → `049cb36` → `3082490` → `58acd5c` → `5a25521` (root = `main`).

**One caveat on provenance:** `06_regression_results.md` states the result was obtained "at `e8ef0d7`". `audit_stage15/` does not exist at that commit (`git ls-tree -r e8ef0d7 | grep -c audit_stage15/` → 0); `regression.py` first appears in `5861d4d`. The run therefore happened in an uncommitted tree. Not a correctness problem, but the sentence is not literally reproducible. (See I-13.)

---

## 2. Diff audit

Every substantive change in `9066c3b..e8ef0d7`, checked in its surrounding context.

### 2.1 D-21 — single sign convention (`w = +d₂`, positive *away* from the channel)

| Location | Original | Corrected | Verdict |
|---|---|---|---|
| `ch02` Fig. 2.1 caption; `ch02` §2.3 (signs) | `w = −d₂`, positive into the channel; "bows into the channel" | `w = +d₂`, positive away | **Correct** |
| `ch02` §2.3 new text | — | pin-moment argument: residual −27 N·m, "four times the 6.4 N·m" | **Correct** (I reproduce −27.0 N·m and 4.25×; §3) |
| `ch03` eq. `beam` | `D_s w'''' = −p` | `D_s w'''' = +p` | **Correct** (traction on solid = `−σ_f n = +p n`, `n` fluid→solid, i.e. +y) |
| `ch04` §4.5 | "w positive into the channel" | "away from the channel" | **Correct** |
| `ch04` §4.7 | `M` unlabelled | `M = −∫σ_xx y dy`… "sagging-positive; physical first moment is −M" | **Correct** (§3) |
| `ch04` `wpdef` text | pressure "opposing the bowing" | "in the same sense as the thermal bowing" | **Correct** |
| `appendix` symbol table; `ch01`; `main.tex` abstract; `ch09` V-C2/V-C3 | into-channel wording | away/widened; "hot face convex"; `w_max > 0` away | **Correct** |
| `figures/fig_geometry.tex` | bow drawn downward | bow drawn upward, flux arrows raised | **Correct direction** (I rendered it: §9.4). Label collisions visible (I-15). |

**Propagation check.** I grepped all `.tex` for `constrict|narrow|into the (flow|channel|passage)|toward the (interior|channel)|H_0 ± w|bows|inward|away from`. No stale direction statement remains. The deformed interface is defined `x = X + d(X)` at `Y = H₀` (`ch02` §2.1), so the local passage height is `H₀ + d₂ = H₀ + w`, consistent with `w = +d₂`. `fig_signs.tex` (n pointing up, pressure force pointing up) was already consistent.

**New inconsistency introduced by the direction change (not fixed):** the admissibility bound A-3, `|w|/H₀ ≤ 0.5 "mesh-generation bound with positive Jacobians"`, and the ceilings derived from it (`ch07`: q'' ≈ 5.5×10³ W/m²) were motivated by *inward* motion compressing fluid elements. With outward motion the mesh widens; the physically binding limit is now the casing clearance, which is undefined (I-02).

### 2.2 D-22 — Γ_p

Now `Γ_p = w_max/w_p` in all seven occurrences (`ch04` eq. `gammap`, `ch06:83`, `ch07:41, :87`, `appendix:94, :130`; `ch10:44` uses the symbol only). Values reproduce (§4). The closed form `48κ_th D_s/(5 p̄ L²) = 1714.29` is correctly identified as the *linear-limit* ratio. **Status: correct and consistently propagated.** Definition caveat in I-11.

### 2.3 D-23 — arc-stretching term 1.8×10⁻⁴ → 1.39×10⁻⁴

Reproduced by quadrature (`mpmath`) and by a symbolic closed-form integral (`sympy`) — agreement to 15 digits (§4). Six occurrences updated (`ch02:93`, `ch04:230`, `ch07:33, :75`, `appendix:73, :104`); the surviving `1.8×10⁻⁴` in the register row D-11 is annotated "superseded by D-23". The collateral change `ch02` slope `0.03 → 0.027` rad is also correct (0.0275 rad). **Status: correct.**

### 2.4 D-24 — thermal data flow (`ch05`, label `sec:datamodel`)

The prose is now consistent with `ch08`, label `sec:coupling` (single shared interface temperature; flux equality is its equation; a flux datum on `Γ_if` would leave the solid pure-Neumann). **Correct as a statement of the monolithic structure. Incomplete for the staggered algorithm** — step 2 of the iteration (`ch08`) still reads "transfer … interface temperature requirements to the solid" without saying which side takes Dirichlet and which Neumann data (I-05).

### 2.5 D-25 — weak-form closure (`ch08`)

| Sub-item | Verdict |
|---|---|
| Function spaces and traces defined | **Partly wrong**: `V_s = {φ = 0 on the pinned ends}` encodes a **clamp** (I-01); `Q = L²(Ω_f)` has no trace on `Γ_out` |
| Pressure gauge `∫_{Γ_out} p ds = 0` | **Wrong** — there is no nullspace to remove (I-04) |
| Geometric-stiffness term added | **Sign correct; dimensionally inconsistent** (I-03) |
| SUPG `τ_K` (`eq:supg`) | Formula and units correct for P1; "exact one-dimensional optimal" overstated for P2; stabilised bilinear form never written (I-06) |
| Monolithic cancellation vs staggered | **Correct** and now properly distinguished |

### 2.6 Other changes

`ch07` added: "`σ_max = 13.6 MPa` on the self-consistent comparison … the frozen-force value 13.9 MPa being the one the bound is enforced against". The 13.9 is right; the **13.6 is not a self-consistent value** (I-08).

---

## 3. Independent derivation of the sign and curvature chain

Script: `indep_audit.py` §S1–S2 (symbolic) and `fe_pin_vs_clamp.py` (2-D confirmation). Derived from the source definitions only.

**Coordinates and orientation (source `ch02` §2.1, B6).** Fluid `0 ≤ Y ≤ H₀`; solid `H₀ ≤ Y ≤ H₀ + d`; interface at `Y = H₀`; **the heated face is the top face `Y = H₀ + d`**, farthest from the channel. With `y` measured upward from the strip mid-plane and flux entering at the top and flowing down, `θ(y) = θ̄ + Γy`, `Γ = q''/k_s = 2.0×10⁴ K/m > 0`.

**Constitutive law (source `eq:widebeam`).** `σ_xx = E/(1−ν²) [ε_xx − (1+ν)αθ]`, with `ε_xx = ε₀ + κ y` where `κ ≡ ∂ε_xx/∂y`.

**Kinematics.** For vertical displacement `d₂` (up positive), `ε_xx = ε₀ − y d₂''`, so **`κ = −d₂''`**. With the selected convention `w = +d₂` this is `κ = −w''` — exactly the "design relation" the source prints.

**Physical first moment (sympy, exact).**

```
∫_{−d/2}^{d/2} σ_xx · y dy = D_s [ κ − (1+ν)αΓ ] = D_s (κ − κ_th),   D_s = E d³/[12(1−ν²)]
```

Setting it to zero reproduces `κ_th = (1+ν)αΓ = (1+ν)α q''/k_s` (source `eq:kappa`) — a free strip bends with positive `κ`. Substituting `κ = −w''`:

```
M₁ ≡ ∫σ_xx y dy = −D_s (w'' + κ_th)      (w = +d₂)
```

so the **pin condition** `M₁ = 0` is `w''(0) = w''(L) = −κ_th`, exactly the printed `eq:beamcol` boundary condition, and Arena's "sagging-positive `M = D_s(w'' + κ_th) = −M₁`" is the correct reading of the printed `M`.

**The old convention.** With `w = −d₂`, `κ = +w''`. Keeping the *same printed pin condition* `w'' = −κ_th` gives `κ = −κ_th` and

```
M₁(pin, old) = D_s(−κ_th − κ_th) = −2 D_s κ_th = −2 (9.6429)(1.4) = −27.0 N·m
```

— 4.25× the 6.355 N·m the strip actually carries at mid-span. Confirmed (Arena: −27 N·m, "about four times 6.4"). Under the selected convention the same expression is exactly `0`. This is a non-trivial check: it is the *integral* of the stress, not the value of a convention-dependent symbol.

**Direction, independent of algebra.** The top (heated) fibre is hotter, so it elongates relative to the bottom. The hot face becomes the convex face, so the strip bows toward the heater, i.e. **away from the channel**. The selected convention agrees; the old prose ("bows into the channel") did not.

**Pressure traction.** With `n` pointing fluid→solid (up), the force on the solid is `−σ_f n = +p n`, i.e. +y, away from the channel. With `w = +d₂`, `D_s w'''' = +p` is the correct sign. ✓.

**Closed form.** `w(x) = (κ_th/μ²)[(1−cos μL)/sin μL · sin μx + cos μx − 1]` satisfies `D_s w'''' + N_c w'' = 0` (sympy: exact) and all four BCs (residuals ≤ 2×10⁻¹⁶); an independent `scipy.solve_bvp` solve of `w'' + μ²w = −κ_th` agrees to 1.1×10⁻¹⁵ relative. At mid-span `w'' = −κ_th(A sin + cos)|_{μL/2} = −κ_th sec(μL/2)`, hence

```
κ_geo/κ_th = sec(μL/2),     (κ_geo + κ_th)/(κ_geo − κ_th) = (1+cos(μL/2))/(1−cos(μL/2)) = cot²(μL/4)
```

— exact identities. The "factor near 5.247516878" is the value of `cot²(μL/4)`; its digits depend on θ̄ (see I-10).

**Independent 2-D confirmation of the sign.** My plane-strain Q8 FE model (§5.1 table) with the heated face at the top yields mid-plane displacement **+1.5750×10⁻⁴ m**, i.e. *positive y, away from the channel*, equal to `κ_th L²/8` to 5 significant figures. The corrected direction is confirmed in the 2-D continuum, not only in the beam model.

**Consistency across the source.** Captions, `fig_signs.tex`, `fig_geometry.tex` (rendered), the symbol table, channel-height definition (`H₀ + w`), abstract, `ch09` tests: consistent. **Category B: PASS.**

---

## 4. Independent numerical audit

Inputs: printed design point only (`ch02` tables; θ̄ from the source's own components `ΔT_t/2 + q''/h + ΔT_b/2` with `h = 5.385 k_f/D_h`, `ΔT_b = q''L/(ρUH₀c_p)`). No value from Arena's scripts or reports was used as an input. Script: `indep_audit.py` → `indep_audit_output.txt`; `indep2.py` → `indep2_output.txt`.

| Quantity | Relation / inputs | Independent value | Printed | Verdict |
|---|---|---|---|---|
| Thermal gradient | `q''/k_s = 5000/0.25` | 2.000×10⁴ K/m | (implicit) | ✓ |
| Through-wall rise | `q''d/k_s` | 60.0 K | 60 K | ✓ |
| Thermal curvature | `(1+ν)α q''/k_s = 1.4·5e-5·5e3/0.25` | **1.4000 m⁻¹** | 1.4 | ✓ exact |
| Rigidity | `E d³/[12(1−ν²)]` | 9.6429 N·m | 9.6 | ✓ (rounding) |
| θ̄ | 30 + 5000/3231 + 1.4354/2 | 32.265 K | ≈32 / 32.3 | ✓ estimate |
| Compressive force / critical | `E d α θ̄/(1−ν)`; `π²D_s/L²` | 2.9039×10⁴ ; 1.0575×10⁵ N/m ; ratio 0.2746 | 0.275 | ✓ |
| `T_cr`, `M_b` | `π²d²/[12α(1+ν)L²]` | 117.50 K ; 3.64 | 117 ; 3.64 | ✓ |
| `μL` | `√(N_c/D_s)·L` | 1.6463 | 1.65 | ✓ |
| Linear bow | `κ_th L²/8` | 1.5750×10⁻⁴ m | 1.58×10⁻⁴ | ✓ |
| Beam–column bow (frozen) | closed form at `L/2` | **2.18858×10⁻⁴ m = 0.43772 H₀** | 2.19×10⁻⁴; 0.438 | ✓ |
| Amplification | `w_max/w_lin` | 1.38957 | 1.39 | ✓ |
| Leading-order factor | `1/(1−N_c/N_cr)` | 1.3786 | 1.38 | ✓ |
| Mid-span `κ_geo` | `−w''(L/2)` | 2.05907 m⁻¹ | — | ✓ `= κ_th sec(μL/2)` |
| Max slope | `|w'(0)|` | 0.02751 rad | 0.027 | ✓ |
| Mid-span moment (frozen) | `D_s(w''+κ_th)` | −6.3553 N·m | −6.4 | ✓ |
| Physical moment at pin, selected | `D_s(κ_kin − κ_th)` | **0** | 0 | ✓ |
| Physical moment at pin, old | `−2D_sκ_th` | **−27.0 N·m** | −27 | ✓ |
| Bending stress | `6|M|/d²` | 4.2369 MPa | 4.2 | ✓ |
| Fibre strain | `(κ_geo−κ_th)d/2` | 9.886×10⁻⁴ | 9.9×10⁻⁴ | ✓ |
| Blocked strain | `(1+ν)αθ̄` | 2.2586×10⁻³ | 2.26×10⁻³ | ✓ |
| Arc term | `½⟨w'²⟩` (quad = closed form) | **1.38785×10⁻⁴** | 1.39×10⁻⁴ | ✓ |
| Circular-arc estimate | `κ_geo²L²/24` | 1.5899×10⁻⁴ | 1.6×10⁻⁴ | ✓ |
| Relaxation (first iterate) | arc / blocked | **6.145 %** | 6.1 % | ✓ |
| Relaxation if arc = 1.8×10⁻⁴ | 1.8e-4 / 2.2586e-3 | 7.97 % | (Arena: 8.0 %) | ✓ — confirms 1.8×10⁻⁴ was inconsistent with 6.1 % |
| Self-consistent fixed point | scalar root of `eq:nupdate` | relaxation **5.88 %**; `w_max` 2.1399×10⁻⁴ m = 0.42798 H₀; frozen over-predicts by **2.28 %** | 5.9 %; 2.14×10⁻⁴; 0.428; 2.3 % | ✓ |
| Self-consistent `M_mid` | | −5.848 N·m (−5.857 at θ̄ = 32.3) | −5.9 | ✓ within rounding |
| **Stress, frozen** | `N_c/d + 6|M|/d²` | 9.680 + 4.237 = **13.916 MPa** | 13.9 | ✓ |
| **Stress, "self-consistent"** | relaxed `N` **and** relaxed `M` | 9.110 + 3.899 = **13.009 MPa** | **13.6** | **✗ — I-08** |
| Pressure drop; gauge | `12μUL/H₀²`; `+12μU L_o/H₀²` | 72 Pa; p(L)=48, p(0)=120, p̄=84 Pa | same | ✓ |
| Pressure deflection | `5p̄L⁴/(384D_s)` | 9.1875×10⁻⁸ m | 9.2×10⁻⁸ | ✓ |
| Linear-limit ratio | `48κ_thD_s/(5p̄L²)` | **1714.29** | 1.7×10³ | ✓ |
| `Γ_p = w_max/w_p` | | **2382.1** (2382.26 at θ̄ = 32.27) | 2.4×10³ | ✓ (value) |
| Mid-span passage height | `H₀ + w_max` | 7.1886×10⁻⁴ m = **1.4377 H₀ (+43.8 %)** | *not stated anywhere* | see I-02/RU-03 |
| `(κ_geo+κ_th)/(κ_geo−κ_th)` | `cot²(μL/4)` | **5.2484** (θ̄ = 32.265); 5.2475 (θ̄ = 32.27) | 5.247516878 | ✓ identity; digits depend on θ̄ (I-10) |

**Two-method checks performed:** (a) `κ_th` — symbolic zero-moment solve and direct arithmetic; (b) `w(x)` — closed form vs `solve_bvp` (rel. diff 1.1×10⁻¹⁵) and vs sympy ODE residual; (c) arc term — `mpmath.quad` vs sympy symbolic integral (agree to all printed digits); (d) bow direction/magnitude — beam closed form vs 2-D Q8 FE (1.0000); (e) self-consistent state — `findroot` fixed point.

### 4.1 Discrepancies found in this section

**I-08 — the "13.6 MPa self-consistent" value is a mixed state.** The frozen state has membrane `N_c/d = 9.68 MPa` and bending `4.24 MPa`. In the true self-consistent state the membrane force is *relaxed* (`N_c` 29 039 → 27 331 N/m), so both terms change: `9.11 + 3.90 = 13.01 MPa`. The printed 13.6 MPa is `9.68` (frozen membrane) `+ 3.90` (self-consistent bending) = 13.58. `regression.py` encodes this very mixture (`abs(sig_m) + 6*5.9/d²`) and "verifies" it. The ordering the text relies on (frozen > self-consistent, frozen conservative) still holds, and the 0.2σ_y cap is not affected (13.9 < 18 MPa), so this is a labelled-value error, not a conclusion error — but it was added to `ch07` in this very cycle.

**I-09 — "total mechanical surface strain ≈ 5.4×10⁻³" has no definition and does not reproduce.** The source gives it a name and a bound (A-3: ≤ 10⁻²) but no formula. Arena's register shows it equals `e₀ + κ_geo d/2` = 5.347×10⁻³, which is a composite of a blocked thermal strain and the *full* geometric curvature strain. From the source's own constitutive law the stress-producing (mechanical) strain at the bottom/top fibres of the frozen-shape solution is `−3.108×10⁻³` / `−1.131×10⁻³` (max magnitude **3.1×10⁻³**; `E/(1−ν²) × −3.108e-3 = −13.3 MPa`, between the frozen 13.9 and relaxed 13.0), and the total kinematic strain is `+3.23×10⁻³ / −2.95×10⁻³`. Neither is 5.4×10⁻³. Passing the 10⁻² bound is unaffected; the number should be defined or replaced. The same 5.4×10⁻³ is also used in `ch08` as the `O(ε)` accuracy of the reference-configuration cancellation.

**I-10 — false precision.** The 12-digit "expected" values in `regression.py` (e.g. `w_max = 2.188704727879e-4`, `μL = 1.646414286`, ratio `5.247516878`) rest on a *rounded* θ̄ = 32.27 K that the source itself calls an estimate "≈32". Using the source's own components (θ̄ = 32.265) every one of them shifts in the 4th–5th digit (`w_max` 2.18858×10⁻⁴; ratio 5.2484; `Γ_p` 2382.1 vs 2382.26), so those 12-digit assertions would fail on the source-derived input. Printed 2–3-digit values are unaffected.

**I-11 — Γ_p mixes an amplified numerator with an un-amplified denominator.** `w_max` carries the beam–column amplification (1.3896) from the compressive membrane force; `w_p` is the un-amplified simply-supported value. The same pre-stressed strip also amplifies the pressure deflection (I solved the beam–column problem under uniform p̄ = 84 Pa: `w_p(N)/w_p(0) = 1.3799`). Like-for-like `Γ_p = 2.1886e-4 / 1.2678e-7 = 1726` ≈ the linear-limit 1714, not 2382. Both ≫ A-5's threshold of 5, so no conclusion changes, but the manuscript's statement that "the amplification converts" the linear ratio to the quoted one describes an apples-to-oranges comparison. Author to confirm which is intended.

---

## 5. Casing and clearance

**Verified from the source.**

- `ch02` §2.1: "The strip is embedded in a rigid casing and is pinned at both ends." Upper face `Y = H₀ + d` "receives the imposed thermal load".
- A9: "the surrounding casing is taken rigid and adiabatic, and its interior pressure equals the outlet datum of condition B2."
- B4: "rigid upper sections: `u = 0` … rigid casing". B8: "remaining solid faces: zero traction, zero flux — insulated casing."
- Fig. 2.1 (rendered): no casing, cavity wall or standoff is drawn above the strip; the heater arrows float above the bowed wall.
- A grep for `clearance|standoff|gap|contact|backing|cavity` finds no specification of any distance, and `contact` appears only in `ch01` as "contact resistance … excluded".
- Corrected-convention bow: `w_max = 0.21886 mm` toward that casing (Arena: 0.219 ✓). Mid-span passage height 1.4377 H₀; the baseline admissible envelope reaches `w/H₀ ≈ 0.5` (0.25 mm) by A-3 and `≈ 1.2` (0.6 mm) at the buckling ceiling.

**What the manuscript does and does not determine.**

| Reading | Supported by source? |
|---|---|
| Freely deforming wall, with clearance | **Suggested, not stated.** A9's "casing interior pressure equals the outlet datum" implies a space at p_out above the strip; no size is given |
| Gapless rigid backing | **Not excluded** by "rigid casing", but it would suppress the bow entirely and contradict the whole bowing mechanism |
| Unilateral contact | **Not specified** — no contact law, gap function or constraint anywhere |

I did not choose the reading that preserves the numbers. **Conclusion: `AUTHOR DECISION REQUIRED`.**

**Exact missing information.** (1) The clearance `g(x)` between the heated outer face and the casing (value, and whether uniform); (2) whether the cavity is vented to the outlet datum or sealed (A9 says "equals the outlet datum", which reads as vented but is not stated for the *cavity*); (3) how the film heater is mounted — whether it adds thickness/stiffness and moves with the wall; (4) if `g < w_max`, the contact law.

**Calculations that depend on it.** If `g > w_max` and vented: every printed number stands. If sealed: back-pressure rises with the bow, so `w_max`, `Γ_p`, the stresses and A-3/ceiling estimates change. If `g < w_max` or gapless: the frozen-force beam–column solution is invalid (inequality-constrained problem), `T_cr`/`M_b` and all of Chapter 7 change. In all cases the A-3 "mesh bound" and the ceiling heat fluxes (5.5/5.9/9.1 kW/m²) must be re-derived, because the binding constraint is now the clearance, not mesh collapse. I agree with Arena's RU-01 and RU-03 in full.

**Which modules are independent of it:** rigid-wall fluid flow, rigid-wall conjugate heat transfer, and the free-strip thermoelastic checks V-C1/V-C2 (§8).

### 5.1 Related, separate defect: the end condition (I-01)

This is not the casing issue; it is the **end support** of the strip, and it is the most consequential new finding.

**Source text.** B7 (`ch05`): strip ends `X = 0, L`: `d₁ = d₂ = 0`, **zero applied moment**. A9: "the pins are imposed on the **full end edge** (`X = 0, L`), which differs from ideal point pins by Saint-Venant end layers of width `O(d)` … a few per cent of global stiffening." Arena's new `V_s = {φ ∈ [H¹]² : φ = 0 on the pinned ends}` (`ch08`) adopts that.

**Why it is wrong.** If both components of displacement vanish on the whole end edge, no cross-section at that end can rotate. That is a **clamped** end. The source itself states in `ch04` §4.4 that a clamped–clamped strip at uniform `κ_th` "does not bow at all (`w ≡ 0`)". "Zero applied moment" cannot be imposed on an edge where displacement is prescribed — the moment becomes a reaction.

**Independent 2-D test.** `fe_pin_vs_clamp.py` — plane-strain Q8 serendipity, 3×3 Gauss, printed E, ν, α, k_s, q'', L, d; θ̄ = 0 so the beam benchmark is exactly `κ_th L²/8 = 1.5750×10⁻⁴ m`; heated face on top.

| End condition | Mesh | `w` mid-plane (m) | Ratio to beam value |
|---|---|---|---|
| Point pins at the mid-plane (`u = v = 0` at one node per end) | 60×4 | +1.5750×10⁻⁴ | **1.0000** |
| Point pins | 90×6 | +1.5750×10⁻⁴ | **1.0000** |
| `v = 0` on the whole edge, `u = 0` at the mid node (rotation free) | 60×4 / 90×6 | +1.5718×10⁻⁴ / +1.5718×10⁻⁴ | **0.9980** |
| **`d₁ = d₂ = 0` on the full end edge (B7 / `V_s` as written)** | 60×4 | −3.13×10⁻⁶ | **−0.0199** |
| **same** | 90×6 | −2.90×10⁻⁶ | **−0.0184** |

The model is validated by the first row (exact agreement with the beam solution and the correct positive sign). Taking the source's own boundary condition literally suppresses ~98 % of the bowing — not a "few per cent". A solver built to the printed `V_s`/B7 would fail its own V-C3 benchmark, and every baseline result would be unreproducible. **Pre-existing in the source (A9/B7), propagated into `V_s` by Arena's D-25; not noticed by Arena** (their `09` §3 discusses B7/B8 only in the casing context). The fix is a specification choice, not an invention: impose `d₂ = 0` (not `d₁`) on the end edge plus `d₁ = 0` at a single point per end, or point pins; keep "zero applied moment" as the natural condition.

---

## 6. Weak form and well-posedness

For each requested item: what the source says, my derivation, status. Arena's claim is in brackets.

1. **Function spaces and interface traces** [CLOSED] — **FAIL (partial).** Spaces are now defined. (a) `V_s` imposes `φ = 0` on the full end edges = clamp (I-01). (b) `Q = L²(Ω_f)`: the pressure has no trace on `Γ_out`, so the constraint in item 3 is undefined at the continuous level. (c) `S_f` (zero at the inflow) is used for trial and test alike; correct only because `T_ref = T_in`, which the source leaves "to be fixed at data freeze". The `H^{1/2}(Γ_if)` trace statement is correct.
2. **Boundary and natural conditions** [—] — **FAIL.** B7 (`d₁ = d₂ = 0` *and* zero moment) is self-contradictory (I-01). The printed RHS of `eq:weakf` still carries `∫_{Γ_out} σ_f n·v ds`; under B2 (traction-free) that term is zero and should not appear as an unknown boundary integral.
3. **Pressure gauge** [CLOSED] — **FAIL (I-04).** With velocity Dirichlet only on inlet and walls, and a **do-nothing** natural condition at `Γ_out` (B2), constants are *not* in the kernel of the pressure–velocity coupling: `b(v, 1) = −∫_{Γ_out} v·n ds ≠ 0` for admissible `v`, so `p` is uniquely determined by the natural condition and the saddle-point matrix is nonsingular. There is no "one-parameter freedom" to remove. Adding `∫_{Γ_out} p ds = 0` over-determines the system: for the exact do-nothing solution `∫p ds = 2μ∫∂ₓu ds`, which vanishes only for fully developed outflow. Implemented with a Lagrange multiplier it injects a spurious mass source of size λ at the outlet; implemented by row replacement it breaks the traction-free condition. Arena's own text (`04` §3) concedes "the do-nothing condition already sets the level", which contradicts the need for the constraint. **Correct specification:** no gauge for this geometry; the datum is the natural condition (and a pressure gauge is needed only if velocity were prescribed on the entire boundary).
4. **Geometric-stiffness term** [CLOSED] — **FAIL (I-03).** Arena's 1-D derivation is correct: `∫D_s w'' φ'' − ∫N_c w' φ' = 0` ⇒ minus sign for compression ✓. But the term was transcribed into the **2-D area integral** `−∫_{Ω_s⁰} N_θ^c ∂_X d₂ ∂_X φ₂ dX`, where `dX` is the area measure (same as the first term) and `N_θ^c` is a force **per unit depth** (N/m). Units: `(N/m)·1·1·m² = N·m`, while the other terms are `N`. Reduction through the thickness gives `d · N_c ∫ w' φ' dX`, not `N_c ∫ w' φ' dX` as claimed (`ch08`: "one-dimensional reduction … reproduces `eq:beamcol`"). The consistent 2-D statement is `−∫_{Ω_s⁰} (N_θ^c/d) ∂_X d₂ ∂_X φ₂ dX` (equivalently a uniform pre-stress `σ₀ = −N_c/d`), or the integral over the mid-line. Implemented as printed, the geometric stiffness equals `d` times the intended value — 3×10⁻³ of it in SI units (333× too small, effectively dropped), and a different factor in any other unit system, which is itself the signature of a dimensional error. The consequence is the opposite of over-stiffening: the 2-D model would behave almost like the linear solid, which Arena's own `04` §4 says differs from the beam–column level by the amplification 1.39 (~39 % in `w_max`).
5. **Thermal data flow between `ch05` and `ch08`** [CLOSED] — **PASS for the monolithic structure, PARTIAL for the staggered algorithm.** `ch05` (`sec:datamodel`) and `ch08` (`sec:coupling`) now agree. Staggered step 2 remains ambiguous (I-05).
6. **Interface temperature: prescribed or shared unknown** [CLOSED] — **PASS.** Shared unknown; flux equality `k_f∇T_f·n = k_s∇T_s·n` is its equation; the printed flux condition `−k_f∂ₙT_f = −k_s∂ₙT_s` matches. I re-derived the boundary-term signs from `n_f = n`, `n_s = −n`: fluid `+∫k_f∇T_f·n χ`, solid `−∫k_s∇T_s·n χ`; they cancel under flux continuity ✓.
7. **Monolithic cancellation vs staggered algorithm** [CLOSED] — **PASS.** The text now states that cancellation is a property of the assembled system and that the staggered iteration recovers it only at convergence, with the flux-jump norm of V-B as the acceptance measure.
8. **SUPG** [CLOSED] — **PARTIAL (I-06).** `τ_K = h_K/(2|u|)(coth Pe_K − 1/Pe_K)`, `Pe_K = |u|h_K/(2κ_f)`: units are seconds ✓; `Pe_K → ∞` limit ✓. At the baseline `κ_f = 1.435×10⁻⁷ m²/s`, `u_max = 0.075 m/s`, so `Pe_K ≈ 13` at `h_K = 50 µm` — stabilisation is indeed needed ✓. Gaps: (a) the stabilised weak form (`Σ_K ∫_K τ_K (u·∇χ) R(T) dx`) is never written, so `eq:weaktf` is still the Galerkin form; (b) "the exact one-dimensional optimal value" is the classical result for **linear** elements — the source specifies **quadratic** (P2) temperature elements, for which the choice of `h_K` and the "optimal" claim need restating (usually `h_K/p`).
9. **Strong / weak / discrete / physical compatibility** — **FAIL** until items 1–4 are fixed.
10. **Enough to implement a solver** — **PARTIAL.** See §8.

---

## 7. Regression suite

**Location and execution.** `audit_stage15/regression.py` (Python 3, standard library only; no dependency file). Command: `python3 audit_stage15/regression.py` from the repo root. Environment: Linux, Python 3.13.16. **Exit status 0; all checks print PASS.** Count printed: **44**, not 37.

**Count reconciliation.** Arena's `06_regression_results.md`: "37/37", with section headings 7 + 4 + 7 + 20 = **38**. The script as committed has 7 structural + 4 superseded + 7 convention-marker + 25 numeric + 1 build = **44**. The report documents neither the real count nor the real grouping.

### 7.1 Classification of all 44 checks

| Group | Checks | What they actually test | Can fail on a wrong equation/sign? |
|---|---|---|---|
| 1 Structural (7) | braces, environments, label uniqueness, dangling refs, cite keys, uncited bib, undefined macros | Syntax/consistency of the TeX | **Meaningful** — my independent clean build confirms (0 errors, 0 undefined refs/citations). Unrelated to the mathematics |
| 2 Superseded text (4) | absence of `1.8\times10^{-4}`, `w=-d_2`, "positive into the channel", `w^{''''}(x)= -\,p` | Literal-string absence | Only for these four exact strings. A re-worded error (`bows toward the interior`) passes |
| 3 Convention markers (7) | substring *presence* of `w=+d_2`, `+\,p(x)`, the geometric term, `eq:supg`, `V_g=\{`, gauge, `Gamma_p=\frac{w_{\max}}{w_p}` | That a string exists | **No** — no sign, units or content check. A flipped sign on the geometric term passes |
| 4 Numeric (25) | D_s, κ_th, μL, w_max, κ_geo, M, σ_bend, fibre strain, ODE, BCs, arc term, identities, Γ_p, stress columns | **An in-script re-implementation of the formulas** with hard-coded inputs | **Never reads the manuscript.** The numbers in the TeX can change arbitrarily and these still pass |
| 5 Build (1) | `os.path.exists('main.pdf')` | Presence of a file that is **known to be stale** | Passing is misleading; it asserts the stale PDF exists |

### 7.2 Specific defects

- **Vacuous assertion** — `check("circular-arc estimate = 1.6e-4", abs(-w2(L/2))**2*L*L/24/1e-4 - 1.59 < 0.005)`: there is no `abs()` around the difference (the parenthesis closes after `-w2(L/2)`), so it is true for **any** value below 1.595. Evaluated as written with `κ_geo` = 0, 1.0 and 2.059 it passes all three (`mutation_test_output.txt`, V1).
- **No-op term** — `abs((w(L/2)/w(L/2)/1) * 0 + w(L/2)/wp/cf - 1.389654)`: the first term is multiplied by 0. Harmless but indicates unreviewed code.
- **Tautology** — "amplification == w_max/w_lin" and "closed form × amplification = w_max/w_p" test an identity between quantities computed by the same lines.
- **Unverified constant** — θ̄ = 32.27 is hard-coded rather than derived from `ΔT_t/2 + q''/h + ΔT_b/2` (I-10); `thbar` for the "self-consistent column" is the frozen membrane stress (I-08).
- **Missing coverage** — no first-principles integration of `σ_xx y` (the physical pin moment); no sign test of the pin or of pressure; no 2-D/FE test; no units/dimension check of weak-form terms; no comparison between printed TeX numbers and computed numbers; no ZIP-vs-source or PDF-freshness check; no compile test.

### 7.3 Mutation test (can the suite fail?)

`mutation_test_regression.sh` makes a scratch copy of the repo at `7c9749f`, applies one fault at a time, and runs the suite. Output: `mutation_test_output.txt`.

| ID | Fault injected | Suite result |
|---|---|---|
| C1 (control) | `ch03`: `+p` → `-p` | **Caught** (2 FAIL) |
| C2 (control) | `ch02` caption → "positive into the channel" | **Caught** (1 FAIL) |
| M5 | `ch08`: gauge integral changed to `p²` with RHS 7 | Caught (1 FAIL) — a *string* check |
| **M1** | `ch04`: printed `w_max` 2.19×10⁻⁴ → **7.77×10⁻⁴** | **ALL CHECKS PASSED** |
| **M2** | `ch08`: geometric-stiffness term `−` → **`+`** | **ALL CHECKS PASSED** |
| **M3** | `ch01`: "bows away from the interior" → **"bows toward the interior"** | **ALL CHECKS PASSED** |
| **M4** | `ch02` property table: Poisson ratio 0.40 → **0.30** | **ALL CHECKS PASSED** |

The suite catches exact-string reversions of faults Arena already knew about and nothing else. It therefore does not protect the one thing it was created to protect — the corrected sign convention and numbers. **Runtime verification: complete. Meaningfulness: `FAIL`.** The numeric group is, however, *correct as arithmetic*: every expected value matches my independent computation to the precision allowed by θ̄ (§4).

---

## 8. Solver readiness

Checked against `ch03`, `ch05`, `ch06`, `ch08`, `ch09`, and Arena's `09_solver_ready_specification.md`.

| Required item | Present? | Note |
|---|---|---|
| Unknowns and governing equations | ✅ | `u, p, T_f, d, T_s`; plane-Poiseuille, advection–diffusion, conduction, plane-strain thermoelasticity |
| Material properties | ⚠️ | All values given, but PEEK `E, ν, α, k_s, ρ_s, c_s` are "freeze pending" (item C-6); `T_in/T_ref` "to be fixed at data freeze" |
| Boundary and interface conditions | ❌ | **B7 as written is a clamp and self-contradictory (I-01); casing undefined (I-02); B2 gauge wrong (I-04)** |
| Coupling strategy | ⚠️ | Staggered fixed-point + escalation to monolithic Newton specified; thermal Dirichlet/Neumann partition not stated (I-05) |
| Spatial discretisation | ⚠️ | Taylor–Hood P2–P1; P2 temperature/displacement; conforming interface mesh. No target `h_K`, near-wall resolution, or mesh sequence values |
| Time discretisation | n/a | Steady problem; time scales given (`§4.9`) |
| Stabilisation | ⚠️ | `τ_K` given; stabilised form absent (I-06) |
| Nonlinear strategy | ⚠️ | Newton for fluid, under-relaxed fixed point (ω "tuned once"), fixed-point tolerance 10⁻⁶ `w_max`; no residual tolerances or Newton stopping criteria |
| Gauge / nullspace | ❌ | Stated gauge is unnecessary and over-determining (I-04) |
| Tolerances / convergence | ✅ | GCI 1 % (0.5 % headline); enthalpy 10⁻³ Q'; flux-jump 10⁻³ |
| Benchmarks and expected values | ✅ | V-A, V-B1/B2, V-C1a/b, V-C2, V-C3, V-D, each with reference and tolerance |
| Independent validation | ✅ | V-D vs published conjugate channel data |
| Physical assumptions for intended configuration | ❌ | Casing/clearance (I-02) |

**Modular prototype vs coupled production.**

- **Safe to begin now (independent of RU-01 and of the defects above):**
  1. Rigid-wall fluid solver against V-A (plane Poiseuille) and the pressure-datum arithmetic (72 Pa; 48 → 120 Pa).
  2. Rigid-wall conjugate heat transfer against V-B1/V-B2 and V-D, with SUPG (add the stabilised form; treat `h_K` for P2 explicitly).
  3. Free-strip thermoelastic solver against V-C1a/V-C1b/V-C2 (`σ_m = −Eαθ/3`, `κ = (1+ν)αΔT_t/d > 0`, hot face convex).
  4. Beam–column verification: closed form and 1-D BVP (both independently reproduced above).
- **Do not implement as written:** (i) B7 / `V_s` full-edge `d₁ = d₂ = 0` (use point pins or `d₂ = 0` on the edge, §5.1); (ii) the geometric-stiffness term without the `1/d` factor; (iii) the mean-pressure constraint on `Γ_out`; (iv) a partitioned thermal exchange without stating which side takes Dirichlet data.
- **Not ready:** the coupled production simulation (needs RU-01, I-01, I-03, I-05 resolved) and V-C3 in 2-D until the pin condition is corrected.

Verdict for this category is `PARTIAL`: a modular prototype can safely start, but the specification as written is not acceptable for coupled production.

---

## 9. PDF, ZIP, and build audit

### 9.1 Claims checked

| Arena claim | Verified |
|---|---|
| Tracked `main.pdf` is stale | **Yes.** 49 pages; `pdftotext` finds "into the channel" ×6 and "1.8 × 10⁻⁴" ×7; Creator/Producer: pdfTeX-1.40.29; contains the superseded manuscript |
| ZIP stale, 13 of 16 `.tex` files differ | **Yes — exactly.** `HFF_Final_Overleaf_Source.zip` (26 members, SHA-256 `b49ca34e…054f`, matches Arena's recorded hash): 13/16 `.tex` differ from HEAD (`main`, `appendix`, `audit_appendix`, `ch01–ch09`, `fig_geometry`); **0 of 17 source files differ from the baseline `9066c3b`**, i.e. the ZIP is the pre-correction baseline |
| No TeX toolchain was available | **Environment-specific.** Here `pdflatex`, `xelatex`, `lualatex`, `latexmk`, `bibtex` are installed (pdfTeX 3.141592653-2.6-1.40.25, TeX Live 2023/Debian) |

### 9.2 Clean build of the current source (Category H)

```
git archive 7c9749f main.tex references.bib chapters figures | tar -x -C <empty dir>
cd <empty dir> && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex     # exit 0
```

Result: **exit 0; 53 pages; 0 `!` errors; 0 `LaTeX Warning` lines; no undefined citations or references; no `??` in the text; bibtex resolved all 18 entries (bibliography present); 16 `Overfull \hbox` reports (cosmetic)**. Packages used: `geometry, amsmath, amssymb, booktabs, longtable, array, xcolor[table], siunitx, tikz, caption, graphicx, natbib[numbers,sort&compress], hyperref` (all standard in TeX Live and Overleaf). Built-PDF SHA-256 `89535db15000e4ff49f58a442acbe7aa6e5b9eb2cf6646cec8ab10dc842475eb` (not bit-reproducible across TeX versions). The new PDF contains "away from the channel" ×8, no "into the channel", and no 1.8×10⁻⁴ arc term (the remaining "1.8 × 10⁻⁶ s" hits are the structural wave time).

**Not tested:** compilation on Overleaf itself; a second TeX distribution.

### 9.3 Provenance of the tracked PDF

I built three sources and compared extracted text: baseline `9066c3b` → 50 pages; initial import `5a25521` → 49 pages (912 token-level differences from the tracked PDF); current → 53 pages. **The tracked `main.pdf` cannot be matched to any committed source.** It must not be described as the corrected manuscript.

### 9.4 Figure check Arena skipped

I rendered Fig. 2.1 from the new build (page 8). The strip bows **upward (away from the channel)** ✓. Defects (cosmetic, I-15): "pinned ends (parameter-locked, register D-4)" overprints "outlet, p = p_out"; the "adiabatic" and "adiabatic rigid lid" labels collide with the strip ends and the `T_in` annotation; no casing or standoff is drawn above the strip.

### 9.5 Package problems and instructions

- `README.md` says "This is the final Overleaf-ready package (`HFF_Final_Overleaf_Package.zip`)" — **no such file is tracked.** The tracked ZIPs are `HFF_Final_Overleaf_Source.zip` (stale), plus `Stage6/8/9` ZIPs (historical).
- **Do not distribute `HFF_Final_Overleaf_Source.zip`.** Do not label `main.pdf` as the current manuscript.
- **To produce and verify a valid package (after I-01…I-06 are fixed):** upload the *source tree* (`main.tex`, `references.bib`, `chapters/`, `figures/`) to Overleaf (compiler pdfLaTeX, main document `main.tex`, bibliography via BibTeX), confirm 0 errors/warnings, then export the ZIP from that project; record its SHA-256 in a report committed at the same commit; delete or clearly rename the three historical ZIPs and the stale PDF; fix the `README.md` filename.

**Category I: `FAIL` — no valid final package exists.** (Rebuilding now would package I-01/I-03/I-04, so it should wait.)

---

## 10. Correction and provenance audit

**What is good.** Every substantive correction has a ledger entry, original claim preserved in Appendix B (register D-21…D-25), changed file/line, downstream list and a regression reference (`05_correction_log.md`, `01_master_issue_ledger.md`). Withdrawn claims are recorded rather than erased: the "naive flip" value −5.1888×10⁻³ (explained as `−(κ_geo+κ_th)d/2`, a factor 5.25 error) and the 1.8×10⁻⁴ arc term; the `%`-continuation false positive on a `\cite` key is documented. Audit reports and both scripts are tracked in Git (`5861d4d`), so a fresh clone contains them.

**Defects (I-13).**
1. "Result at `e8ef0d7`" — the script did not exist at that commit (§1).
2. 37 checks claimed; 44 executed; section sum 38 (§7).
3. `06` says "19 cited, 18 entries, 0 missing"; the actual count is 18 distinct cited keys for 18 entries (I computed it).
4. `10` says "Eight of eleven closed" while its own table lists nine closed.
5. `calc_register.py` **writes `03_numerical_register.md` into the tracked tree** when re-run, so re-running it modifies the repository (I ran it only on a scratch copy).
6. `README.md` names a nonexistent package file (§9.5).
7. Six items marked CLOSED (B-1, B-2, B-3, B-6 and parts of B-4/B-10) do not survive independent checking (§6, §4).
8. Minor arithmetic presentation: `ch07` Table "`9.87(9.6)/(9×10⁻⁴) = 1.06×10⁵`" evaluates to 1.053×10⁵; 1.06×10⁵ is correct only for the unrounded `D_s = 9.643`.

**Category J: `PARTIAL`.**

---

## 11. Unresolved issues and consequences

| ID | Severity | Issue | Consequence if left | Closes when |
|---|---|---|---|---|
| **I-01** | **Blocking (technical)** | A9/B7/`V_s`: full-edge `d₁ = d₂ = 0` is a clamp; contradicts "zero applied moment"; FE shows bow suppressed to −2 % | 2-D model cannot reproduce V-C3 or any baseline result; whole thermomechanical coupling is wrong | Pin specified as point pin or `d₂ = 0` on edge + one-point `d₁ = 0`; A9 "few per cent" claim removed; 2-D V-C3 test within 1 % of `κ_thL²/8` |
| **I-02** | **Blocking (author)** | Casing clearance / vent / contact undefined (Arena's RU-01) | Final coupled model undefined; ceilings and A-3 meaningless | Author supplies clearance, vent/sealed, heater mounting, contact law |
| **I-03** | High | Geometric-stiffness term missing `1/d` | Geometric stiffness ~333× too small in SI units if coded literally (unit-dependent), so the 2-D model would behave nearly linearly and under-predict the bow by up to the amplification (~39 %) | Term corrected to `−∫(N_θ^c/d)…dA`; dimensional check + sympy through-thickness reduction |
| **I-04** | Medium | Pressure-gauge constraint is wrong/redundant | Over-determined system or spurious outlet mass source | Constraint removed (or justified for a Dirichlet-outlet variant) |
| **I-05** | Medium | Staggered thermal Dirichlet/Neumann partition unspecified; step list omits an explicit fluid-energy solve | Implementer can choose a pure-Neumann (singular) partition | Algorithm states which side takes `T_if` and which takes flux |
| **I-06** | Medium | SUPG stabilised form not written; "exact optimal" stated for P2 | Ambiguous, possibly mis-scaled stabilisation | Stabilised form and `h_K` convention for P2 written |
| **I-07** | High (process) | Regression suite passes under 4/4 semantic faults; vacuous assertion; count mismatch | False assurance for every later edit | Numeric checks read printed TeX values; sign/BC/units checks added; M1–M4 all caught |
| **I-08** | Low–Med | "Self-consistent 13.6 MPa" is a mixed state; correct value 13.0 MPa | Mislabelled comparison value | `ch07`, appendix A9 and the test corrected to 13.0 MPa (or relabelled) |
| **I-09** | Low | "Total mechanical surface strain 5.4×10⁻³" undefined, not reproducible (3.1×10⁻³ mechanical / 3.2×10⁻³ kinematic) | A bound is compared with an undefined number | Define the quantity; recompute |
| **I-10** | Low | 12-digit test constants on rounded θ̄ | Tests fail on source-derived inputs; false precision | Derive θ̄ in the script; relax tolerances to the 3-digit printed precision |
| **I-11** | Low | Γ_p numerator amplified, denominator not (like-for-like 1726) | Misleading "amplification converts" text | Author states intended definition |
| **I-12** | High (release) | Stale ZIP and PDF; README names nonexistent file; no valid final package | Wrong manuscript distributed | §9.5 procedure completed |
| **I-13** | Low | Documentation inconsistencies (§10) | Weakens provenance | Reports corrected to match the code |
| **I-15** | Cosmetic | Fig. 2.1 label collisions | Readability | Labels repositioned and the PDF visually checked |

---

## 12. Final verdict

# `NOT READY — MATHEMATICAL OR TECHNICAL ERRORS`

**Evidence.**

- The sign-convention correction itself is right and fully propagated (Category B `PASS`), the headline numbers reproduce (C `PARTIAL`, no conclusion changes), the repository state is exactly as Arena reports (A `PASS`), and the current source compiles cleanly (H `PASS`).
- But the specification that a solver would be built from contains defects Arena marked CLOSED or never examined: a full-edge boundary condition that is a clamp and suppresses the entire bowing mechanism (I-01, demonstrated numerically), a dimensionally inconsistent geometric-stiffness term (I-03), an unnecessary and over-determining pressure constraint (I-04), and an unspecified thermal partition (I-05). The regression suite does not detect these or the faults I injected (I-07). The package is stale and the final deliverable does not exist (I-12).
- Independently of those technical errors, the physical configuration is not determined by the source (I-02, `AUTHOR DECISION REQUIRED`), exactly as Arena concluded.

I chose `TECHNICAL ERRORS` rather than `AUTHOR DECISION REQUIRED` because I-01/I-03/I-04 are errors in already-written specification text that block coding independently of the author's answer, and Arena's report states the opposite (that RU-01 is the *only* blocker to coding).

**Can independent modules be prototyped safely?** Yes — §8 lists four that make no assumption affected by I-01…I-06 or RU-01. They must not use the end-condition, geometric-stiffness or gauge text as currently printed.

---

## 13. Executive summary — evidence needed to close every blocker

The corrected sign convention is correct, consistently propagated, and independently confirmed in 1-D and 2-D; headline numbers reproduce; the source compiles. The project is **not** ready for coding the coupled solver, and Arena's list of closed blockers is incomplete. To close each remaining blocker:

1. **I-01 — end condition.** Replace `d₁ = d₂ = 0` on the full end edge (A9, B7, `V_s`) with a genuine pin (e.g. `d₂ = 0` on the edge, `d₁ = 0` at one point per end); delete the "few per cent" claim. *Evidence:* re-run `fe_pin_vs_clamp.py` for the new condition (ratio to `κ_thL²/8` within 1 %, positive sign).
2. **I-02 — casing.** The author states the standoff, vented/sealed, heater mounting and (if applicable) contact law. *Evidence:* a sentence in A9 plus a figure showing the cavity; re-derive A-3/ceilings against the clearance; state the deformed mid-span height (1.4377 H₀ at baseline).
3. **I-03 — geometric stiffness.** Correct the term to `−∫(N_θ^c/d)∂_X d₂ ∂_X φ₂ dA`. *Evidence:* a dimensional check of all four terms of `eq:weaks` and a symbolic through-thickness reduction to `−N_c∫w'φ'dX`.
4. **I-04 — gauge.** Remove the outlet mean-pressure constraint (or restrict it to a Dirichlet-outlet variant). *Evidence:* a statement that b(v,1) ≠ 0 for B2.
5. **I-05, I-06 — coupling and SUPG.** Write the thermal partition and the stabilised form and the P2 `h_K` convention.
6. **I-07 — regression.** Make the numeric checks parse the TeX and add pin-moment, sign and unit tests. *Evidence:* `mutation_test_regression.sh` reports every M1–M4 fault caught.
7. **I-08/I-09/I-10/I-11 — values.** 13.6 → 13.0 MPa (or relabel); define or replace 5.4×10⁻³; derive θ̄ in the tests; state the Γ_p definition.
8. **I-12 — package.** Build the corrected source on Overleaf, export a new ZIP, commit its SHA-256 with the report, remove/rename the stale ZIPs and PDF, fix `README.md`.

**Not audited (outside the brief):** the literature review's claims and bibliographic accuracy beyond key resolution; PEEK/water property values against datasheets; Chapter-6 groups other than those listed (Gr, Ri, Br, ξ); the V-B/V-D reference values other than Nu_H1 = 5.385; compilation on Overleaf itself.

---

## Appendix A — Reproduction commands

```bash
# repo state
git clone --depth 1 https://github.com/vipin-oss/hff_final_overleaf_package_fixed R && cd R
git fetch --depth=1000 origin arena/c875f9b3-hff-final-overleaf-package-fix
git worktree add --detach ../wt 7c9749f7e7d22978b44c29ede5c76aba4825733f

# independent numerics + symbolic (inputs = printed design point only)
python3 -I hff_independent_audit_evidence/indep_audit.py      # §3, §4  (needs sympy, mpmath, numpy, scipy)
python3 -I hff_independent_audit_evidence/indep2.py           # sympy-flag resolution, M_sc, like-for-like Γ_p
python3 -I hff_independent_audit_evidence/fe_pin_vs_clamp.py  # §5.1 (needs numpy, scipy, sympy)

# regression suite as shipped, and mutation test
(cd ../wt && python3 audit_stage15/regression.py; echo exit=$?)
bash hff_independent_audit_evidence/mutation_test_regression.sh ../wt

# clean build
git -C ../wt archive HEAD main.tex references.bib chapters figures | tar -x -C /tmp/b && cd /tmp/b && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Evidence files: `indep_audit.py`, `indep_audit_output.txt`, `indep2.py`, `indep2_output.txt`, `fe_pin_vs_clamp.py`, `fe_output.txt`, `mutation_test_regression.sh`, `mutation_test_output.txt` (all in `/home/claude/hff_independent_audit_evidence/`).
