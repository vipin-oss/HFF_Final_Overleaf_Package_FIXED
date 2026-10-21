# HFF program — conjugate flow / heat transfer / thermoelastic wall of a heated channel

Executable companion of the manuscript *"Thermally induced self-deformation of a
heated channel wall: a coupled conjugate flow, heat-transfer and thermoelastic
analysis"*.

The program solves, on the baseline geometry of the manuscript,

1. the steady incompressible Navier–Stokes equations in the (deformed) passage with
   P2–P1 Taylor–Hood elements (`hff/flow.py`),
2. the conjugate heat-transfer problem of the fluid and the wall, solved *monolithically*
   on a conforming fluid/solid discretisation so that interface temperature continuity is
   exact (`hff/thermal.py`),
3. the reduced von Kármán beam–column problem of the wall with the axial-compatibility
   fixed point (`hff/wall.py`),
4. the partitioned fixed-point coupling of the three (`hff/coupled.py`),

together with the closed-form estimates of the formulation (`hff/analytic.py`), a
code-verification suite (`hff/benchmarks.py`), and the generation of every figure and
table of the manuscript (`hff/figures.py`, `hff/tables.py`).

## Requirements

* Python ≥ 3.9 (tested with 3.11.9)
* `numpy ≥ 1.24`, `scipy ≥ 1.10`, `matplotlib ≥ 3.6`, `pytest ≥ 7`
  (installed versions used for the reported results: numpy 2.4.6, scipy 1.17.1,
  matplotlib 3.11.2, pytest 9.1.1)

## Install

```bash
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python run_all.py                 # full study (≈13 min on 2 cores)
python run_all.py --quick         # coarse meshes, short sweeps (≈1 min)
python run_all.py --only bench         # one stage only
python run_all.py --only figures,tables  # re-render artefacts only
python run_all.py --params params/baseline.json
```

Stages, in order: `analytic`, `wall`, `bench`, `coupled`, `mesh`, `sweep`, `param`,
`figures`, `tables`. `--skip-sweeps` omits the two geometric sweeps (`sweep`) and the
three parameter sweeps (`param`). `--quick` shortens the mesh levels, the sweeps and the
verification grids and is what the automated end-to-end test uses.

## Parameters

Everything physical or numerical is read from a JSON file; **no value is hard-coded in
the source**. `params/baseline.json` contains six blocks:

| block       | contents                                                              |
|-------------|-----------------------------------------------------------------------|
| `meta`      | case name, description, reference temperature                          |
| `geometry`  | `H0`, `L`, `Le`, `Lo`, `d`                                             |
| `operating` | `U`, `q_flux`, `Tin`                                                   |
| `fluid`     | `rho`, `mu`, `cp`, `k`, `beta`                                         |
| `solid`     | `E`, `nu`, `alpha`, `k`, `rho`, `cp`, `sigma_y`                        |
| `physics`   | gravity, model switches                                                |
| `numerics`  | mesh, flow, thermal, coupling and wall-solver controls                 |

`hff/config.py` validates the file: every field is range-checked, missing fields and
**unknown fields** (typos) raise `ConfigError` with the offending name. The solver is
deterministic — there is no stochastic component, hence no random seed; the tests check
that two identical runs produce bit-identical results.

## Outputs

```
outputs/data/      *.json (all numerical results) and *.csv (flat tables)
outputs/figures/   fig01..fig16 in vector PDF and 400 dpi PNG
outputs/tables/    LaTeX fragments (\input-able) generated from outputs/data
```

`outputs/data/run_metadata.json` records the parameter file, library versions, platform
and the runtime of each stage. The figures and tables are rendered **from the saved
JSON**, so `python run_all.py --only figures,tables` regenerates the manuscript
artefacts without re-running the solvers.

## Semi-analytical theory

`hff/asymptotics.py` holds the analytical part of the paper: the Graetz/Sturm--Liouville
series, the closed-form hydraulic resistance (Gauss hypergeometric), the closed-form
beam--column solution and the contraction data of the axial-compatibility map. It is run by

```bash
./.venv/bin/python tools/asymptotics_report.py    # outputs/data/asymptotics.json
./.venv/bin/python tools/asymptotic_figures.py    # figures 13-15, tables *_asymptotics, *_pressure_series
./.venv/bin/python tools/thermal_path_report.py   # outputs/data/thermal_path.json, table_thermal_path.tex
./.venv/bin/python tools/collapse_analysis.py     # outputs/data/collapse.json, fig16_collapse, table_collapse.tex
```

`collapse_analysis.py` re-reads the five sweeps and tests whether the strip resistance is a
function of the bow ratio alone: one shape integral, computed once from the design-point
profile with no fitted coefficient, is compared with every converged run.

`thermal_path_report.py` re-runs the coupled baseline (≈30 s) and separates the wall
temperature into the exact thickness average (Simpson along each column, exact for P2), the
mid-surface value returned by the least-squares fit used in the coupling, the conduction path
term `q''w/2k_s` and the curvature residual. `hff.thermal.column_average` is the routine
behind it; `tests/test_thermal_path.py` checks the one-dimensional Neumann wall against its
exact solution.

## Tests

```bash
python -m pytest -q                 # 45 tests, ≈15 s
python -m pytest -q -m slow         # the coupled / multi-grid tests
```

The suite checks configuration validation, the FE primitives (partition of unity,
quadrature, mesh area, boundary tags, conforming fluid/solid numbering), the
closed-form identities, the beam–column solver against its closed-form solution and
limiting cases, the flow solver against the Poiseuille solution (`fRe = 96`), the
thermal solver against the four classical channel Nusselt numbers, global energy
conservation, and the coupled driver on a coarse mesh (including determinism).

## Runtime

| stage                     | work done in the reported run                     | time      |
|---------------------------|---------------------------------------------------|-----------|
| `analytic`                | closed-form baseline and groups                    | 1 s       |
| `wall`                    | frozen + self-consistent wall, envelope, catalogs  | 35 s      |
| `bench`                   | four Nusselt grids, Poiseuille, beam benchmarks    | 9 s       |
| `coupled`                 | baseline coupling (9 iterations, 120×12×8)         | 28 s      |
| `mesh`                    | three coupled levels (30,3,2)…(120,12,8) + GCI     | 33 s      |
| `sweep`                   | flux (8) and thickness (5) coupled runs            | 323 s     |
| `param`                   | Reynolds (5), conductivity (4), expansion (4) runs | 336 s     |
| `figures`, `tables`       | 16 figures, 13 LaTeX tables                        | 12 s      |
| **total**                 | `python run_all.py` (no flags)                     | **775 s** |

Measured on 2 vCPU / 3 GB RAM with the versions recorded in
`outputs/data/run_metadata.json` (Python 3.11.2, NumPy 2.4.6, SciPy 1.17.1,
Matplotlib 3.11.2). The linear systems are factorised with SuperLU; the production mesh
has 3 456 fluid triangles (14 450 velocity and 1 885 pressure unknowns) and 1 920 wall
triangles on the shared quadratic thermal numbering.

Two auxiliary measurements are kept in `tools/`:

```bash
./.venv/bin/python tools/supg_sensitivity.py     # element Péclet statistics and the
                                                 # measured effect of the SUPG term
```

The script writes `outputs/data/supg_sensitivity.json`, which is the source of the
Péclet-number and stabilisation numbers quoted in the manuscript (§5.3). It is not part of
`run_all.py` because it repeats the baseline thermal solve twice and would double the cost
of the `coupled` stage for a single table entry.

## What is *not* done by this program

* The flow is steady and two-dimensional; the formulation and its regime bounds are
  those of the manuscript (§2, §6). Unsteady, three-dimensional and turbulent cases are
  outside the present scope.
* The wall is treated as a reduced plane-strain beam–column (Euler–Bernoulli with
  geometric stiffness); shell/3-D elasticity is not implemented.
* Radiation, contact between the deformed wall and the opposite face, and property
  variation with temperature are neglected, as stated in the manuscript. Radiation is
  *not* negligible at the design point (about 9 % of the imposed flux), which is why it
  is disclosed as a modelling uncertainty rather than dismissed.
* Buoyancy is evaluated *a posteriori* through the Grashof/Richardson numbers and is not
  included in the momentum equation (the formulation justifies the neglect,
  Ri < 4×10⁻³).
