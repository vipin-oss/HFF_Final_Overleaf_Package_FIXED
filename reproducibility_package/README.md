# Reproducibility package

Everything needed to regenerate every number, figure and table of the manuscript
*"Thermally induced self-deformation of a heated channel wall: a coupled conjugate flow,
heat-transfer and thermoelastic analysis"*.

```
reproducibility_package/
├── README.md                  this file
├── ENVIRONMENT.txt            interpreter, libraries, platform, timings
├── program/                   complete source, parameters, tests, saved outputs
│   ├── run_all.py             single entry point
│   ├── requirements.txt       numpy, scipy, matplotlib, pytest
│   ├── pytest.ini
│   ├── README.md              program-level documentation
│   ├── params/baseline.json   all physical and numerical inputs
│   ├── hff/                   the package (config, analytic, fem, flow, thermal,
│   │                          wall, coupled, benchmarks, figures, tables)
│   ├── tests/test_hff.py      30 automated tests
│   └── outputs/
│       ├── data/              saved numerical results (JSON) and flat tables (CSV)
│       ├── figures/           fig01..fig09 as PDF and 400 dpi PNG
│       └── tables/            LaTeX fragments used by the manuscript
└── manuscript/                the manuscript as submitted, with its figures/tables
```

## 1. Environment

Python 3.9 or newer; the reported results were produced with Python 3.11.2, NumPy 2.4.6,
SciPy 1.17.1 and Matplotlib 3.11.2 on Linux (x86-64), 2 vCPU, 3 GB RAM. `ENVIRONMENT.txt`
records the exact versions and the runtime of each stage.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r program/requirements.txt
```

## 2. Reproduce from scratch

```bash
cd program
python run_all.py                # full study, 402 s (measured) on 2 vCPU
python -m pytest -q              # 30 tests, ~5 s
```

The run writes `outputs/data/*.json`, `outputs/figures/*.pdf|png` and `outputs/tables/*.tex`
and records the parameter file, library versions and per-stage runtimes in
`outputs/data/run_metadata.json`.

A faster smoke run (`--quick`, coarse meshes and shortened sweeps) exercises every stage in
about 84 s; it was executed here as a consistency check, but it produces lower-quality figures
and is not the run used in the paper.

## 3. Regenerate the manuscript artefacts without re-solving

The figures and tables are rendered from the saved JSON, so

```bash
cd program
python run_all.py --only figures,tables
```

reproduces exactly the artefacts in `manuscript/figures` and `manuscript/tables`. Copy them
across with

```bash
cp outputs/figures/*.pdf outputs/figures/*.png ../manuscript/figures/
cp outputs/tables/*.tex ../manuscript/tables/
```

## 4. Reproduce the paper

```bash
cd manuscript
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

See `manuscript/README.md` for the Overleaf route.

## 5. Inputs

`program/params/baseline.json` holds every physical and numerical input in seven blocks
(`meta`, `geometry`, `operating`, `fluid`, `solid`, `physics`, `numerics`). Nothing is
hard-coded in the source: changing the flux, the wall thickness, the mesh or the tolerances and
re-running is the supported way to explore the model. `hff/config.py` validates the file and
rejects unknown keys, out-of-range values and non-finite numbers, so a typo cannot silently fall
back to a default.

The solver is deterministic; there is no random seed to control, and the test suite asserts
that two identical runs give bit-identical results.

## 6. Test and validation evidence

* `program/tests/test_hff.py` — 30 tests: configuration validation, finite-element primitives,
  closed-form identities, beam–column solver against its closed-form solution, flow against
  Poiseuille ($fRe=96$), thermal against the four classical channel Nusselt numbers, energy
  conservation, and the coupled driver including determinism.
* `program/outputs/data/verification_benchmarks.json` — the benchmark values behind
  `fig08_verification` and the verification table.
* `program/outputs/data/verification_nusselt.csv` — Nusselt-number errors on four meshes.
* `manuscript/VALIDATION_REPORT.md` — itemised evidence for every reported number, and the list
  of what was not run or not verified.

## 7. Data volume and omissions

All saved data are plain text (JSON/CSV) and total about 1 MB; the figures add about 1.5 MB.
Nothing large or binary is excluded, because no large dataset exists: the program is the data
generator. `__pycache__`, `*.pyc`, `.venv` and LaTeX auxiliary files (`*.aux`, `*.log`, `*.out`,
`*.toc`, `*.bbl`, `*.blg`) are not included.

## 8. Known limitations of this package

* The manuscript was **not compiled** here: no TeX engine was available. The LaTeX source was
  checked mechanically (see `manuscript/BUILD_REPORT.md`); a first compile in Overleaf is the
  remaining step.
* No experimental data are included, because none were used.
* The wall is the reduced beam–column model, not a two-dimensional thermoelastic continuum; the
  package reproduces exactly what the manuscript reports and nothing more.
