# Validation report — numbers, provenance and evidence

This report records what the accompanying program actually computed, how each number in the
manuscript can be traced to a saved file, and what was verified. It deliberately separates
\emph{computed} results from \emph{analytical} identities and from \emph{estimates}.

All values refer to `../program/params/baseline.json` and were produced by

```bash
cd program && python run_all.py           # 402 s on 2 vCPU, 8 stages
```

with Python 3.11.2, NumPy 2.4.6, SciPy 1.17.1, Matplotlib 3.11.2.

---

## 1. Verification against analytical solutions

Source: `program/outputs/data/verification_benchmarks.json`,
`program/outputs/tables/table_verification.tex`, Figure `fig08_verification.pdf`.

| object | computed | reference | relative error |
|---|---|---|---|
| Poiseuille friction factor, $f\,Re_{D_h}$ | 96.0000 | 96 (exact, slit) | $-2.5\times10^{-15}$ |
| Poiseuille velocity profile, $\|u-u_h\|_2/U$ | — | 0 | $1.2\times10^{-13}$ |
| $Nu_{H2}$ (both walls, uniform flux) | 8.2267 | 8.235 | $-1.0\times10^{-3}$ |
| $Nu_{H1}$ (one wall, uniform flux) | 5.3811 | 5.385 | $-7.2\times10^{-4}$ |
| $Nu_{T}$ (both walls, uniform $T$) | 7.5759 | 7.541 | $+4.6\times10^{-3}$ |
| $Nu_{T1}$ (one wall, uniform $T$) | 4.8681 | 4.861 | $+1.5\times10^{-3}$ |
| beam–column FE vs closed form | 2.18858e-4 m | 2.18858e-4 m | $2.5\times10^{-8}$ |
| pressure-only bow vs $5pL^4/(384D_s)$ | — | — | $2.5\times10^{-9}$ |
| zero-force bow vs parabola $\kappa x(L-x)/2$ | — | — | $1.8\times10^{-9}$ |

The friction factor and the velocity profile agree at round-off because the exact solution
lies in the $P_2$ space; this verifies the assembly, the boundary data and the pressure
recovery, not the interpolation order. The four Nusselt numbers are a genuine discretisation
test on four meshes (`verification_nusselt.csv`). The uniform-flux conditions converge
monotonically: $Nu_{H2}$ from 7.863 to 8.227 ($-4.5\,\%$ to $-0.10\,\%$) and $Nu_{H1}$ from
5.281 to 5.381 ($-1.9\,\%$ to $-0.07\,\%$). The uniform-temperature conditions are already
within $0.6\,\%$ on the coarsest mesh and oscillate inside that band ($Nu_T$: 7.522, 7.568,
7.583, 7.576; $Nu_{T1}$: 4.857, 4.867, 4.870, 4.868), so their residual is a quadrature
artefact of the imposed hot wall rather than a convergence trend. The manuscript states this
explicitly rather than claiming monotone convergence for all four.

**Honest limitation.** The reference values are the classical plane-channel results tabulated
by Shah & London (1978). $Nu_{T1}=4.861$ for the mixed boundary condition is the value carried
by the source bibliography with a note that its digit was not re-extracted from the primary
table; the computed value 4.8681 agrees to $0.15\,\%$, which is consistent with the
discretisation error of the other three and therefore does not discriminate between 4.861 and
a slightly different tabulated value.

## 2. Conservation

| check | value | source |
|---|---|---|
| inlet mass flux | $2.500000\times10^{-5}\,\mathrm{m^2/s}$ | `coupled_baseline.json: metrics.flow_flux_inlet` |
| outlet mass flux | $2.500000\times10^{-5}\,\mathrm{m^2/s}$ | `...flow_flux_outlet` |
| wall/interface mass flux | 0 (exact) | `...flow_flux_walls` |
| heat input $q''L$ | 150.00 W/m | `...Q_in` |
| outlet enthalpy flux | 150.012 W/m | `...Q_out` |
| relative energy imbalance | $7.7\times10^{-5}$ | `...energy_imbalance` |
| interface flux, fluid side | 149.2 W/m | recomputed in `hff/thermal.py` |
| interface flux, wall side | 150.0 W/m | idem |
| pointwise interface flux jump ($L_2$) | $2.85\,\%$ | `...interface_flux_jump` |

The interface flux jump is reported, not hidden: the two subdomains approximate the same
continuous flux with different element geometries, and the integrated discrepancy is
$0.5\,\%$ while the pointwise one is $2.85\,\%$.

**Note on the pressure datum.** The first version of the flow solver replaced one continuity
equation by a pressure constraint. That produced an outflow deficit of $0.87$--$0.96\,\%$ and
was rejected: the datum is now obtained from the do-nothing outflow condition and applied as a
post-processing shift, after which the fluxes agree exactly. A sweep of the pin magnitude
($\alpha=10^{-8}\ldots10^{-2}$) was also run and is not used in the reported results.

## 3. Mesh refinement

Source: `mesh_study.json`, Table `table_mesh.tex`, Figure `fig06_convergence.pdf`.

| $n_x$ | $n_y^{f}$ | $n_y^{s}$ | $w_{\max}/H_0$ | $\Delta p$ (Pa) | $\bar\theta$ (K) | $\sigma_b^{\max}$ (MPa) |
|---|---|---|---|---|---|---|
| 60 | 8 | 4 | 0.440029 | 313.126 | 33.983 | 4.342 |
| 120 | 10 | 6 | 0.440990 | 314.048 | 34.165 | 4.374 |
| 240 | 16 | 8 | 0.441524 | 314.499 | 34.266 | 4.393 |

Observed order of the maximum deflection: $p=0.85$; Richardson limit
$w_{\max}=2.2110\times10^{-4}$ m. The production mesh gives $2.2050\times10^{-4}$ m, i.e.
$0.27\,\%$ below the extrapolation. The order is below the nominal second order because the
deflection is a derived quantity obtained from two discretisations plus a fixed point, and the
wall mesh is not refined at the same rate as the flow mesh.

## 4. Coupled baseline results

Source: `coupled_baseline.json`, `wall_baseline.json`, Tables `table_coupled.tex` and
`table_baseline.tex`.

| quantity | value | remark |
|---|---|---|
| coupling iterations | 9 | converged, $\Delta<10^{-4}$ |
| $w_{\max}$ | $2.20495\times10^{-4}$ m | $0.44099\,H_0$ |
| $|N|$ | 29 843.1 N/m | $0.2822\,N_{cr}$ |
| $N_\theta$ | $-30\,748.6$ N/m | from the computed $\bar\theta$ |
| $M_{\rm mid}$ | $-6.5616$ N·m/m | |
| $\sigma_b^{\max}$ | 4.3744 MPa | $6|M|/d^2$ |
| $\sigma_m$ | $-10.2495$ MPa | $-E\alpha\bar\theta/(1-\nu)$ |
| fibre strain | $1.021\times10^{-3}$ | $|\kappa_{geo}-\kappa_{th}|d/2$ |
| $\bar\theta$ (mean, computed) | 34.165 K | 1-D estimate 32.265 K, i.e. $5.6\,\%$ below the computed value ($5.9\,\%$ relative to itself) |
| $\Delta p$ | 314.05 Pa | undeformed slit value 143.93 Pa |
| $u_{\max}$ | 0.13410 m/s | undeformed 0.07492 m/s |
| mean interface shear | 1.2900 Pa | |
| $\overline{Nu}$ | 8.677 | local range 18.6 (first station) → 6.21 |
| $Q'$ | 150.00 W/m | imbalance $7.7\times10^{-5}$ |

Wall-model comparisons (same $D_s$, 241 nodes):

* frozen force: $w_{\max}=2.18858\times10^{-4}$ m ($0.43772\,H_0$), $M_{\rm mid}=-6.3554$ N·m/m,
  $\sigma_b=4.237$ MPa;
* self-consistent $N$: $w_{\max}=2.16344\times10^{-4}$ m ($0.43269\,H_0$), $N=28\,166.3$ N/m
  (converged in 11 iterations, tolerance $10^{-9}$);
* closed form for the frozen force: agreement to $2.5\times10^{-8}$.

## 5. Sensitivity and model-form error

Sources: `sweep_flux.json`, `sweep_thickness.json`, `wall_baseline.json: consistency`.

Flux sweep (each point a full coupled computation): $w_{\max}/H_0$ = 0.0665, 0.1418, 0.2275,
0.2750, 0.3261, 0.3813, 0.4410 at $q''=1,2,3,3.5,4,4.5,5$ kW/m². Runs at 5.25 and
$5.5$ kW/m² exceed the $0.45\,H_0$ guard and are reported as first-iteration predictors
(0.4611 and 0.4917), explicitly outside the validity of the model.

Thickness sweep (3 → 5 mm): $w_{\max}/H_0$ 0.4410 → 0.3771, $\sigma_b^{\max}$ 4.374 → 3.603 MPa,
$\bar\theta$ 34.17 → 53.88 K. At $d=2.5$ mm the predictor reaches $0.466\,H_0$ and is outside
the validity.

Frozen-force closure error (bow / moment): 0.03 % / 0.43 % at 1.09 kW/m², 0.16 % / 1.21 % at
2.41 kW/m², 1.20 % / 4.39 % at 5.05 kW/m², 14.9 % / 30.7 % at 10 kW/m².

Design envelope (reduced wall model, one-dimensional thermal estimate): $|w|/H_0=0.5$ at
5.5 kW/m², $|\sigma|_{\max}=0.2\sigma_y$ at 6.0 kW/m², $M_b=2$ at 9.15 kW/m².

## 6. Tests

`python -m pytest -q` → **30 passed** in about 5 s. The suite covers configuration
validation (including rejection of unknown keys and out-of-range values), the FE primitives
(partition of unity, quadrature normalisation, mesh area against the exact $H_0(L_e+L+L_o)$,
completeness of the boundary tags, conforming fluid/solid numbering), the closed-form
identities of the formulation, the beam–column solver (closed form, pressure limit, zero load,
bad-grid rejection, self-consistent convergence), the flow solver (mass conservation, pressure
drop against the strip pressure), the thermal solver (energy balance, through-thickness
difference, positivity of $Nu$), and the coupled driver on a coarse mesh including a
determinism check.

Tests marked `slow` (the coupled coarse solve, the multi-grid benchmark, the consistency
curve) are included in the default run; `-m "not slow"` skips them.

## 7. What was not run or not verified

* **The manuscript was not compiled.** No TeX distribution exists in this environment
  (`pdflatex`, `latexmk`, `tectonic` all absent, and no package manager reachable). The LaTeX
  was checked mechanically instead: environment balance, brace and `$` balance, every
  `\ref`/`\eqref` has a `\label`, every `\cite` key exists in `references.bib`, and every
  `\input`/`\includegraphics` target exists. `BUILD_REPORT.md` records the exact checks.
* **No experimental validation** was performed or is claimed.
* **The 2-D plane-strain thermoelastic continuum** is not implemented; the wall is solved as
  the reduced beam–column of the formulation. The frozen-vs-consistent comparison quantifies
  the axial-compatibility closure only, not the beam reduction itself.
* **Unsteady, 3-D, transitional and buoyant cases** are outside the formulation. Buoyancy is
  assessed a posteriori ($Ri=1.7\times10^{-3}$) and not included in the momentum equation.
* **Property variability** is not modelled: the wall properties are datasheet-representative
  values and the fluid properties are held at their inlet values, with a stated $\pm7\,\%$
  viscosity band over the largest computed temperature excursion.
