# Build report

What was built, how, and what could not be checked. Read together with
`VALIDATION_REPORT.md` (numerical evidence) and `../program/README.md` (how to run the code).

## 1. What this package is

A conventional single-column journal article replacing the previous
`report`-class document (cover page, table of contents, 11 chapters, appendices). The old
document was a pre-implementation design and audit record: it contained the formulation, the
baseline arithmetic and a verification *plan*, but no computed results and no code. The new
article keeps the scientific content that could be substantiated — geometry, assumptions with
their quantitative checks, governing equations, boundary and interface conditions, the reduced
wall equation, the dimensionless groups and regime bounds, the closed-form baseline and the
limitations — and adds what was missing: an executable implementation, executed results,
generated figures, verification against analytical solutions, and a refinement study.

Nothing was invented. Every numerical statement in the manuscript comes from a file in
`../program/outputs/data/`; the figures and tables are rendered from those files by
`hff/figures.py` and `hff/tables.py`. Where the study does not support a claim, the claim is
removed or explicitly qualified (see §5 below).

## 2. Manuscript structure

`main.tex`, `\documentclass[11pt,a4paper]{article}`, single column, no cover page, no table of
contents, no chapters, no preface. Sections:

1. Introduction
2. Physical model and formulation (geometry; assumptions A1–A10 with quantitative support;
   governing equations; interface and boundary conditions; reduced wall equation; dimensionless
   groups and regime bounds)
3. Computational formulation (discretisation; flow sub-problem; conjugate thermal sub-problem;
   structure sub-problem; coupling algorithm)
4. Results and discussion (closed-form baseline; flow; conjugate heat transfer; wall response
   and the coupled state; model-form error of the frozen-force closure; sensitivity)
5. Verification and convergence (benchmarks; mesh study; conservation and reproducibility)
6. Limitations
7. Conclusions
8. Declarations (data and code availability, competing interests, funding, contributions)
9. References

Nine figures and six tables, all cited in the text. The .bib file is the project's existing,
verified bibliography; three entries that were previously uncited (the FSI benchmark, the
geometric-conservation-law paper and the stratified-flow paper) are now cited where they are
actually relevant, and no entry was added.

## 3. Figures

| file | content | source of the data |
|---|---|---|
| `fig01_geometry` | configuration and boundary conditions | **schematic**, drawn to scale from the parameter file; stated as such in the caption |
| `fig02_mesh` | discretisation and detail of the throat | `coupled_baseline.json` (converged shape) |
| `fig03_flow` | velocity profiles and pressure distribution | `coupled_baseline.json: samples` |
| `fig04_thermal` | local Nusselt number; wall/bulk/mean temperatures | `coupled_baseline.json` |
| `fig05_wall` | deflection and bending moment | `wall_baseline.json`, `coupled_baseline.json` |
| `fig06_convergence` | coupling convergence and mesh refinement | `coupled_baseline.json: history`, `mesh_study.json` |
| `fig07_sensitivity` | flux and thickness sweeps | `sweep_flux.json`, `sweep_thickness.json` |
| `fig08_verification` | benchmark errors and values | `verification_benchmarks.json` |
| `fig09_model_form` | frozen-force closure error | `wall_baseline.json: consistency` |

Each figure is a vector PDF (used by the manuscript) and a 400 dpi PNG (for inspection), with a
consistent serif font at 8 pt, 0.6 pt axes, panel labels (a)/(b) and colour-blind-safe palette.
File names are zero-padded and descriptive. Only `fig01_geometry` is not computed; it is
labelled "schematic, not to scale" in its caption, exactly as the old document did.

## 4. Compilation status

**Not compiled.** No TeX engine is available in the build environment: `pdflatex`, `latexmk`,
`xelatex`, `lualatex` and `tectonic` are absent, `apt-get` cannot reach a mirror and no
TeX distribution is installable from PyPI. The instruction "ship a compiled PDF if possible"
therefore results in no PDF.

What was done instead — mechanical checks of the LaTeX source:

| check | result |
|---|---|
| `\begin`/`\end` environments balanced, correctly nested (main + 6 tables) | pass |
| braces balanced in every file | pass |
| `$` count even in every file | pass |
| every `\ref`/`\eqref` has a matching `\label` | pass (40 references, 62 labels) |
| duplicate labels | none |
| every `\cite` key present in `references.bib`; every bib entry cited | pass (18/18) |
| every `\includegraphics` target exists | pass: all 9 PDFs are present in `figures/` and are resolved through `\graphicspath{{figures/}}` (the checker reports them as "missing" only because it does not expand `\graphicspath`) |
| every `\input` target exists | pass (6 table fragments) |
| control sequences used | all standard `amsmath`/`amssymb`/`graphicx`/`booktabs`/`siunitx`/`longtable`/`caption`/`natbib`/`hyperref` commands plus locally defined macros |
| packages required | only those in a standard TeX Live/MiKTeX; no shell escape, no `biber`, no external fonts |
| numbers in tables | every numeric cell goes through `siunitx`'s `\num{}`; no math command is used in text mode, so the tables cannot raise "Missing $ inserted" |

The `plainnat` bibliography style and `natbib` are used, so the sequence
`pdflatex → bibtex → pdflatex → pdflatex` is sufficient. This is the standard Overleaf flow and
requires no configuration.

The remaining risk is a LaTeX error that a mechanical check cannot see (for example a
`siunitx` version difference in a unit expression). A first compile in Overleaf is therefore
the next action before submission; `README.md` gives the exact steps.

## 5. Claims removed or qualified relative to the earlier document

The earlier document contained statements that the executed study does not support. They were
not carried over:

* **A two-dimensional plane-strain thermoelastic continuum solver.** It does not exist in the
  implementation. The wall is the reduced beam–column of the formulation, and the manuscript
  says so in §3.4 and in the limitations. The frozen-versus-self-consistent comparison measures
  the axial-compatibility closure only.
* **"Future solver" placeholders** (verification gates V-A…V-G, audit registers D-1…D-20,
  arithmetic cells A1–A9). These were planning artefacts. The verification that is actually
  performed is reported as such (§5 of the manuscript, `VALIDATION_REPORT.md`).
* **`Γ_p` inconsistency between chapters** (1.7×10³ in one place, 2.4×10³ in another). The two
  numbers use different definitions: 1.7×10³ is the ratio of the *linear* bow to the
  pressure-only bow, 2.4×10³ the ratio of the *computed* bow to the pressure-only bow. Both are
  now reported explicitly with their definitions.
* **The stress fraction quoted as 0.15 of σ_y.** The computed total stress is 14.6 MPa, i.e.
  0.16 σ_y; the manuscript quotes the computed value and identifies the ceiling used.
* **`Nu` quoted as a single fully developed value.** The computed local Nusselt number varies
  from 18.6 to 6.2 along the strip; the manuscript reports the profile and states that no single
  value characterises the wall.
* **An "exact" treatment of the interface flux condition.** The condition holds in the weak
  sense; its pointwise residual is 2.85 % in the L2 norm and is reported.

## 6. Reproducibility

`../reproducibility_package/` contains the complete source, the parameter file, the saved
numerical results, the figures and tables, the test suite and the environment record. The
manuscript artefacts are regenerated by

```bash
python run_all.py --only figures,tables   # from saved JSON, seconds
python run_all.py                        # from scratch, 402 s (6.7 min) on 2 vCPU
```

`outputs/data/run_metadata.json` records the parameter file, the library versions, the platform
and the runtime of each stage of the run that produced the reported numbers.
