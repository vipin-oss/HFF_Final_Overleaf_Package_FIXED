# Build report — v2 manuscript

Date of build: 21 October 2026.
Branch: `arena/75958f95-hff-final-overleaf-package-fix` (merged to `main` through the pull
request that carries this report).

This report states what was produced, how it was checked, and what was **not** checked. It
supersedes the v1 build report, which described a 16-page article-class document with 18
references.

## 1. What was rebuilt and why

| Item | v1 (superseded) | v2 (this package) |
|---|---|---|
| Length | 16 pp, report-like density | 2 190 source lines, 12 560 words of prose, 34 display equations, 12 figures, 11 tables, 3 appendices; estimated 30–36 compiled pages |
| Front matter | plain `abstract` | Emerald-style structured abstract (Purpose / Design / Findings / Research limitations / Practical implications / Originality, 249 words including the six headings), keywords, article classification, nomenclature table |
| References | 18 entries | **55 entries** (46 articles, 7 books, 2 chapters); **every entry cited**; **48 DOIs resolved against Crossref on 21 Oct 2026** |
| Structure | intro → formulation → results → verification → conclusions | introduction and literature review with a stated gap → physical model and assumptions → governing equations and non-dimensionalisation → full reduced-wall derivation → computational formulation → boundary-condition table → grid independence with GCI → verification → results → discussion → limitations → conclusions → three appendices |
| Figures | 9 | 12, all rendered from the current run of `program/run_all.py` |
| Tables | 6 | 11 (9 generated from `outputs/data`, 2 typeset in the source) |
| Numbers | v1 run (2026-10-18) | v2 run of 21 Oct 2026, 775.2 s, all nine stages |

The scientific content, the model, the solvers and the limitations of v1 are preserved. What
changed is the presentation depth, the reference base and the numbers, which were regenerated
from scratch after the mesh study was extended with the observed order and the Grid
Convergence Index, and after the parameter sweeps were made complete runs.

## 2. Reproducible numerical build

```
program/.venv/bin/python run_all.py           # 775.2 s, stages:
                                             # analytic, wall, bench, coupled, mesh,
                                             # sweep, param, figures, tables
program/.venv/bin/python -m pytest -q        # 41 passed in 20 s
program/.venv/bin/python tools/supg_sensitivity.py   # 5 s, writes supg_sensitivity.json
```

`program/outputs/data/run_metadata.json` records interpreter, library versions, platform,
the nine stages and the total runtime. Every number quoted in the manuscript is traceable to
one of these files:

| Manuscript element | Source file |
|---|---|
| Table 1 (parameters) | `params/baseline.json` |
| Table 3 (closed-form baseline), §3.4 groups, §4.7 critical load | `outputs/data/analytic_baseline.json` |
| Table 4 (coupled state), Fig. 5–8, §9.2–9.5 | `outputs/data/coupled_baseline.json` |
| Table 5 (grid study, GCI), Fig. 3 | `outputs/data/mesh_study.json` |
| Table 6 (flux sweep) and the thickness sweep, Fig. 9 | `outputs/data/sweep_flux.json`, `sweep_thickness.json` |
| Table 7, Fig. 10 | `outputs/data/sweep_reynolds.json` |
| Tables 8–9, Fig. 11 | `outputs/data/sweep_conductivity.json`, `sweep_expansion.json` |
| Table 10, Fig. 4 | `outputs/data/verification_benchmarks.json` |
| Fig. 12, §9.9 model-form error | `outputs/data/wall_baseline.json` (`consistency`) |
| Kinematic/strength/stability ceilings (§9.6, §10.3) | `outputs/data/wall_baseline.json` (`envelope_crossings`) |
| Element Péclet numbers and the SUPG measurement (§5.3) | `outputs/data/supg_sensitivity.json` |

The figures and the nine generated tables were written by the same run, from the JSON above,
by `hff/figures.py` and `hff/tables.py`. They were not edited afterwards; the two typeset
tables (boundary conditions; iteration/tolerance inventory) contain no numerical result that
is not already in the JSON files.

## 3. Reference audit (how the 55 entries were checked)

1. Every entry with a DOI (48 of 55) was resolved through the Crossref REST API on
   21 October 2026 using `https://api.crossref.org/works?filter=doi:...&select=DOI,title,
   container-title,volume,page,issued`. Title, container title, volume, pages and year in
   `references.bib` were read from the response, not transcribed.
2. Four earlier pairings that had proved wrong in the v1 bibliography were re-sourced and are
   now correct: `10.1017/jfm.2018.30` is Christov, Cognet, Shidhore and Stone on deformable
   shallow microchannels; `10.1108/HFF-07-2023-0380` is Gupta and Barak on photo-thermo-piezo-elastic
   waves; `10.1017/jfm.2025.10162` is Draškić et al. on stratified supercritical CO₂;
   `10.1108/HFF-09-2017-0348` is Zargartalebi et al. on a flexible partition.
3. Four DOIs that were found in v1 to belong to unrelated work
   (`10.1016/0045-7930(73)90017-0`, `10.1109/T-ED.1981.20303`, `10.1137/S0895479895290954`,
   `10.1002/nme.2354`) were removed with their entries and are not cited anywhere.
4. The seven entries without a DOI are monographs and conference proceedings of the theory
   background (Bird et al. 1960; Carslaw and Jaeger 1947; Boley and Weiner 1960; Timoshenko
   and Goodier 1970; Timoshenko and Gere 1961; Shah and London 1978; Hood and Taylor 1974);
   their imprint details are those of the publisher/library record. They carry no DOI to
   resolve, and this is stated in the file header.
5. The complete per-DOI log, with the resolved title and container, is in
   `VALIDATION_REPORT.md` §6.

No reference was generated or inferred. Where an entry could not be verified it was dropped
rather than "repaired".

## 4. LaTeX validation actually performed

No TeX distribution exists in the build environment (`pdflatex`, `latex`, `xelatex` and
`tectonic` are all absent, and the sandbox has no route to a TeX repository), so **no PDF was
produced here**. Instead:

1. **Strict parse of the whole document.** `pylatexenc`'s `LatexWalker` in non-tolerant mode
   consumed all 112 801 characters of `main.tex` with no parse error, which excludes
   unbalanced braces and mismatched `\begin`/`\end` pairs.
2. **Custom audit** — `python3 tools/check_tex.py`, which is shipped with the package:
   123 labels (114 in the manuscript, 9 inside the generated table fragments), 83
   `\ref`/`\eqref` uses, 0 duplicate labels, 0 unresolved references, 0 unused
   bibliography keys, 55 citations against 55 keys, **0 undefined citations**, all 12 figure
   files present, all 9 `\tabinput` fragments present. Exit code 0.
3. **Path resolution in both layouts.** Each `\includegraphics` file exists in
   `journal_submission/figures/`; `\tabinput{...}` resolves `tables/` first and falls back to
   `journal_submission/tables/`; `\graphicspath` lists both directories; the bibliography is
   located by `\IfFileExists`. The same `main.tex` therefore compiles as a ZIP upload and
   from the repository root (GitHub sync).
4. **Archive check.** `python3 tools/build_zip.py --check` writes
   `hff_journal_submission.zip` (38 members, 2.57 MB), re-opens it, verifies the CRC of every
   member, confirms that `main.tex` is at the archive root, and confirms that all 12 figure
   PDFs are referenced from the source.

## 5. What is *not* verified

* **No compiled PDF.** The exact page count, the float placement and the absence of Overfull
  boxes are unknown until the first Overleaf compile. The page estimate of 30–36 pp is
  arithmetic (word count, float count, reference list length), not a measurement.
* **`emerald.cls` was not used.** The manuscript reproduces the Emerald house style
  (structured abstract, nomenclature, author–year citations, section numbering) with the
  standard `article` class so that it compiles anywhere. Swapping in the journal class at
  submission is described in `README.md`; that swap has not been tested.
* **The author block is a placeholder.** Names, affiliations and the corresponding author's
  e-mail are marked "to be inserted before submission"; inventing them would have been
  improper.
* **No experimental validation.** Nothing in this package compares the model with measured
  hardware, and the manuscript says so in §11 and §12. "Verification" is used in its
  computational sense throughout (code against analytical solutions, grid convergence,
  conservation), never as validation.
* **Publisher house rules** (reference style details, figure resolution thresholds,
  cover-letter requirements) were not applied beyond the layout described above.

## 6. Files changed or added in this revision

```
journal_submission/main.tex             rewritten (v2, 2 190 lines)
journal_submission/references.bib       rewritten (55 entries, all DOIs resolved)
journal_submission/figures/fig01..12    replaced by the v2 run (24 files, PDF + PNG)
journal_submission/tables/*.tex         regenerated (9 files; mesh table mislabelled unit fixed)
journal_submission/README.md            rewritten (Overleaf routes A and B, inventory)
journal_submission/BUILD_REPORT.md      this file
journal_submission/VALIDATION_REPORT.md rewritten (numbers, conservation, DOI log)
main.tex                                unchanged wrapper (\input of the v2 manuscript)
tools/build_zip.py                      added (archive builder + verifier)
tools/check_tex.py                      added (label/reference/citation/figure audit)
hff_journal_submission.zip              rebuilt from v2 sources
program/hff/figures.py                  figure numbering aligned with the manuscript order
program/hff/tables.py                   mesh-table unit label fixed; GCI block unchanged
program/run_all.py                      envelope crossings added to the wall stage
program/tools/supg_sensitivity.py       added (Péclet statistics and SUPG measurement)
program/README.md                       runtime, stages and tools updated
reproducibility_package/                re-synchronised with the above
legacy_report/                          untouched (superseded document, kept for provenance)
```


## 7. v4 — analytical upgrade (21 October 2026)

The manuscript now derives its model instead of postulating it. Added: §2.3 (two-field
variational reduction, with the beam--column equation and the axial compatibility obtained as
its Euler--Lagrange equations and the three discarded terms bounded); §4.1 (closed forms,
Theorem 1 on the contraction of the axial map, Theorem 2 giving the hydraulic resistance as
`₂F₁(3,½;1;a)`, Theorem 3 giving the Sturm--Liouville solution of the thermal-entry problem,
five particular cases); §5.2 (comparison of the semi-analytical model with the finite-element
solution, the scaling law `Nu/Nu_Graetz ≈ (H0/H)^0.79`); Appendix D (proofs).

New files:

```
program/hff/asymptotics.py              the semi-analytical theory
program/tools/asymptotics_report.py     runs it, writes outputs/data/asymptotics.json
program/tools/asymptotic_figures.py     figures 13-14 and tables/table_asymptotics.tex
program/tests/test_asymptotics.py       6 tests (36 in total, all passing)
tools/insert_analysis.py                the anchored edit that inserted the new sections
journal_submission/ANALYTICAL_UPGRADE.md  what is proved and how it was checked
```

Key verification numbers: the closed form reproduces the computed pressure drop to **+0.03 %**
when the computed shape is used, the frozen-force closed-form bow to **−0.85 %**, and the
developed Nusselt number `70/13` against the classical 5.385. No number in the new sections is
typed by hand: the comparison table and both figures are generated from
`outputs/data/asymptotics.json`.

The abstract was rewritten for this version (249 words including the six headings) and the
conclusions gained four "It is shown that …" items corresponding to the new theorems.


## 8. v4 — what changed in the mathematics

1. **New Theorem (self-similar reduction).** The hydraulic functional is now stated for an
   arbitrary self-similar shape, with its moment coefficients, engine radius and truncation
   bound, and a Lipschitz lemma in the shape. §5.1.4, proofs in Appendix D.4–D.5.
2. **Correction of an error.** The Taylor coefficients of `₂F₁(3,½;1;a)` were printed as
   `1, 3/2, 27/8, 75/16`; they are `1, 3/2, 9/4, 25/8, 525/128`. Fixed in \eqref{eq:dpclosed}
   and in every downstream document.
3. **New Theorem (thermal closure) and Corollaries.** The horizontal mean of the wall
   temperature is affine in `y` for any interface shape and any interface temperature; the
   one-dimensional closure is exact in the flat limit and, with the deformed thickness
   `d+w`, reproduces the exact thickness average to 0.0075 %. §5.1.5, proof in D.6.
4. **The 6.3 % wall-temperature discrepancy is resolved**, not excused: −4.36 % is the
   lengthening of the conduction path by the bow (`w/d = 7.36 %` at the crown) and +3.38 % is
   the difference between the mid-surface value used in the coupling and the thickness average.
   New Table `tab:thermal_path`, new `hff.thermal.column_average`.
5. **New benchmark.** The one-dimensional Neumann wall is added to §5.6.1 with its exact
   solution (`θ̄=30 K`, `Γ=2×10⁴ K/m`, `Q′=150 W/m`), reproduced to round-off.
6. **New figure and table.** `fig15_pressure_series` and `tab:pressure_series` carry the
   law/shape/truncation decomposition over the seven converged sweep points.
7. **Abstract rewritten** around the resolved decomposition; 240 words including headings.
8. **Test suite** grows from 30 to 45 tests (`test_asymptotics.py` 7, `test_thermal_path.py` 5,
   `test_collapse.py` 4, which guards the collapse against regression).
9. **Collapse across the parameter space** (new §5.3, Table `tab:collapse`, Figure 16):
   `tools/collapse_analysis.py` reads all 24 converged coupled runs of the five sweeps and
   shows that one shape integral, evaluated once and containing no fitted coefficient,
   reproduces the strip resistance to 0.40 % (mean 0.11 %), against 19.7 % for the kinematic
   `sin²` law. This is the result that turns the design rule from a formula checked at a point
   into a chart with a measured error bar, and it is the answer to the obvious referee
   objection that the study is anchored at a single design point.

Not claimed: no PDF was compiled (no TeX engine in the build container), so the LaTeX is
validated structurally (`tools/check_tex.py`: 180 labels, 132 references, 55 citations against
55 keys) and by careful reading, not by a successful `pdflatex` run.
