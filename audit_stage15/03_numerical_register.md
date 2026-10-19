# HFF numerical calculation register (generated)

Regenerate with `python3 calc_register.py`. All inputs are the printed design point
(`ch02:40-46`, `ch02:169-180`); no manuscript result is used as an input.

| Quantity | Governing relation | Source | Recomputed | Printed | Discrepancy |
|---|---|---|---|---|---|
| Thermal gradient | $\partial T/\partial y=q''/k_s$ | ch04:93, ch07:28 | 2.000000e+04 K/m | — | derived (not printed) |
| Through-thickness rise | $\Delta T_t=q''d/k_s$ | ch07:28 | 60.000 K | 60 K | exact |
| Thermal curvature | $\kappa_{th}=(1+\nu)\alpha q''/k_s$ | ch04:99 | 1.400000000 1/m | 1.4 | exact |
| Section rigidity | $D_s=Ed^3/[12(1-\nu^2)]$ | ch07:36 | 9.642857143 N.m | 9.6 | +0.45% (rounding) |
| Membrane resultant | $N_\theta=-Ed\alpha\bar\theta/(1-\nu)$ | ch07:35 | 2.904300e+04 N/m | -2.9e4 | exact |
| Beam-column parameter | $\mu=\sqrt{N_\theta^c/D_s}$ | ch04:190 | 54.880476188 1/m | 55 | exact |
| Dimensionless force | $\mu L$ | ch04:211 | 1.646414286 | 1.65 | exact |
| Linear bow | $w_{\max}^{lin}=\kappa_{th}L^2/8$ | ch04:123 | 1.575000000e-04 m | 1.58e-4 | -0.32% |
| Beam-column bow | eq:beamcolsol at x=L/2 | ch04:213 | 2.188704727879e-04 m | 2.19e-4 | exact |
| Relative bow | $w_{\max}/H_0$ | ch04:213 | 0.437740946 | 0.438 | exact |
| Amplification | $w_{\max}/w_{\max}^{lin}$ | ch04:219 | 1.389653795 | 1.39 | exact |
| Pin curvature | $w''(0)$ | ch04:186 | -1.400000000 1/m | -1.4 | exact |
| Mid-span curvature | $w''(L/2)$ | ch04:221 | -2.059208681 1/m | — | derived |
| Geometric curvature | $\kappa_{geo}=-w''(L/2)$ | ch04:221 | 2.059208681 1/m | — | derived |
| Physical moment at pin (B) | $-D_s(w''+\kappa_{th})$ | derived | -0.000000000e+00 N.m | 0 (imposed) | exact |
| Physical moment at pin (A) | $+D_s(w''-\kappa_{th})$ | derived | -27.000000 N.m | — | residual under A |
| Sagging moment, mid-span | $D_s(w''+\kappa_{th})$ | ch04:254 | -6.356655141 N.m | -6.4 | exact |
| Bending stress | $6|M|/d^2$ | ch04:255 | 4.237770094 MPa | 4.2 | exact |
| Membrane stress | $-E\alpha\bar\theta/(1-\nu)$ | ch07:43 | -9.681000000 MPa | -9.6 | exact |
| Max section stress (frozen) | $|\sigma_{memb}|+|\sigma_{bend}|$ | ch07:95 | 13.918770 MPa | 13.9 | exact |
| Max section stress (self-cons.) | with M=-5.9 N.m | appendix:109 | 13.614333 MPa | 13.6 | exact |
| Fibre strain | $(\kappa_{geo}-\kappa_{th})d/2$ | ch04:221 | 9.888130219613e-04 | 9.9e-4 | exact |
| Naive-flip value | $-(\kappa_{geo}+\kappa_{th})d/2$ | trap | -5.188813021961e-03 | -5.1888e-3 | exact |
| Flip error factor | $(1+\cos(\mu L/2))/(1-\cos(\mu L/2))$ | derived | 5.247516878 | 5.2475 | exact |
| Blocked strain | $e_0=(1+\nu)\alpha\bar\theta$ | ch04:227 | 2.258900000e-03 | 2.26e-3 | exact |
| Exact arc term | $\frac12\langle w'^2\rangle$ (quadrature) | ch04:228 | 1.388009729196e-04 | 1.39e-4 | exact |
| Circular-arc estimate | $\kappa_{geo}^2L^2/24$ | appendix:74 | 1.590127647440e-04 | 1.6e-4 | -0.62% |
| Relaxation | $\frac12\langle w'^2\rangle/e_0$ | ch04:229 | 6.144627 % | 6.1 % | exact |
| Relaxation from old value | $1.8e-4/e_0$ | superseded | 7.968480 % | — | contradicted 6.1% |
| Surface strain | $e_0+\kappa_{geo}d/2$ | ch04:223 | 5.347713022e-03 | 5.4e-3 | exact |
| Pressure deflection | $5\bar pL^4/(384D_s)$ | ch04:278 | 9.187500000e-08 m | 9.2e-8 | exact |
| Linear-limit ratio | $48\kappa_{th}D_s/(5\bar pL^2)$ | ch04, eq:gammap | 1714.285714 | 1.7e3 | exact |
| Deformation ratio | $w_{\max}/w_p$ | eq:gammap | 2382.263649 | 2.4e3 | exact |
| Ratio of ratios | $(w_{\max}/w_p)/(w_{lin}/w_p)$ | — | 1.389653795 | =1.389653795 | exact |
| Mid-span gap | $H_0+w_{\max}$ | not stated | 1.437740946 H0 | 1.4377 | exact |
| Max slope | $\max|w'|$ | ch04:220 | 0.027515789 rad | 0.027 | exact |

## Identity checks

- `sec(muL/2)` = 1.470863343791; `kgeo/kth` = 1.470863343791; difference 2.22e-16
- `(1+cos(u/2))/(1-cos(u/2))` = 5.247516878033; `cot^2(muL/4)` = 5.247516878033
- closed form x amplification = 2382.263649; `w_max/w_p` = 2382.263649
- analytic arc integral = closed form (see sign-convention doc)

---

# Stage 16 numerical register (supersedes the rows above where they conflict)

| Quantity | Value | Definition | Source |
|---|---|---|---|
| `θ̄` | 32.27 K | `ΔT_t/2 + q/h + ΔT_b/2`; components recompute to 32.2652 | `ch04` |
| `D_s` | 9.6429 N·m | `E d³/12(1−ν²)` | derived |
| `κ_th` | 1.400 1/m | `(1+ν)αq/k_s` | `ch04` |
| `N₀` (frozen) | 2.9039×10⁴ N/m | `E d α θ̄/(1−ν)` | derived |
| `N_θ^c` (converged) | 2.7330×10⁴ N/m | fixed point of the arc relaxation | `ch04` |
| `μL` (frozen) | 1.6463 | `√(N₀/D_s)·L` | derived |
| `w_max` frozen | 2.1886×10⁻⁴ m = 0.4377 `H₀` | `eq:beamcolsol` | `ch04`, `ch07` |
| `w_max` self-consistent | 2.1399×10⁻⁴ m = 0.4280 `H₀` | fixed point | `ch04` |
| linear (no membrane) | 1.5750×10⁻⁴ m | `κ_th L²/8` | `ch04` |
| amplification | 1.3896 | `w_max / w_lin` | `ch04`, `ch09` |
| `κ_geo` | 2.0591 1/m | `−w″(L/2)` | derived |
| `κ_geo/κ_th` | 1.4708 | `sec(μL/2)` (identity, machine precision) | §5 of the suite |
| `½⟨w′²⟩` exact | 1.3879×10⁻⁴ | quadrature, 200 001 points | `ch04` |
| circular-arc estimate | 1.5899×10⁻⁴ | `κ_geo²L²/24`, 14.6 % high | `ch04` |
| force relaxation (1st iterate) | 6.145 % (printed 6.1 %) | `½⟨w′²⟩/ε₀`, `ε₀=(1+ν)αθ̄` | `ch04` |
| fibre strain | 9.886×10⁻⁴ | `(κ_geo−κ_th)d/2` | `ch04` |
| `σ_max` frozen | 13.9165 MPa = 0.155 `σ_y` | `N₀/d + 6M/d²` | appendix |
| `σ_max` self-consistent | 13.0091 MPa = 0.145 `σ_y` | `N_θ^c/d + 6M/d²` | appendix |
| `w_p` | 9.1875×10⁻⁸ m | `5p̄L⁴/(384D_s)` | `ch04` |
| `Γ_p` mixed | 2.38×10³ | `w_max/w_p(p̄)` | `ch04` |
| `Γ_p` like-for-like | 1.71×10³ | `48κ_thD_s/(5p̄L²)` | `ch04` |

Note on the relaxation figure: `ε₀ = (1+ν)αθ̄ = 2.2586×10⁻³` and `½⟨w′²⟩ = 1.3879×10⁻⁴`, so the first-iterate relaxation is 6.14 %, printed as 6.1 %. The suite recomputes both factors
from the parsed table, so a drift in either is caught.
