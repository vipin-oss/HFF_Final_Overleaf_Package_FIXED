# VALIDATION REPORT

Scope: what was actually run, what it shows, what it does **not** show. The coupled fluid–structure–thermal
solver was **not executed**; nothing below validates it. Text/format checks (`check_manuscript.py` C1–C4, C6–C8)
are consistency checks and are not offered as scientific validation. Numerical tests are listed separately.

## 1. Source branch and template-paper record

* Source: branch `hff-manuscript-package`, commit `094d98e` (itself on top of `main` = `5a25521`, untouched).
* Searched all four remote branches (`main`, `arena/c875f9b3-…`, `claude/independent-audit-7c9749f`,
  `hff-manuscript-package`) for earlier FEM research papers. **None exists**: the repository holds a chapter-style
  manuscript (`chapters/ch01–ch11`), audit/reconciliation notes and reference tables only.
* Therefore no previous FEM paper was used as a template. Structure, figure conventions and referencing follow the
  Emerald/HFF author guidelines (structured abstract ≤ 250 words, ≤ 6 keywords, Harvard references, Roman-numeral tables,
  EPS/PDF figures, 280 words per float). Published HFF fluid–structure papers (Alsabery 2019, Saleh 2025) are cited as
  literature; their full text was **not** available, so their figure style was not copied.

## 2. Decision register (compact)

| # | Issue | Decision | Evidence |
|---|---|---|---|
| A | Heated face / signs | Outer face heated (B5: +k_s ∇T·n_out = q″, heat supplied); y points fluid→solid; dT/dy > 0; outer face hot and convex; pinned strip bows **away** from the channel; passage **widens**. Fluid-face heating is a different model and is stated as out of scope. | Derivation in §3.1; closed form w = κ x(L−x)/2 >0; FE sign check (u_y > 0 mid-span) in `q8_strip.py`, `q8_nonlinear.py`, `fe_independent.py` |
| B | Beam vs FE restraints, membrane force, nonlinearity | Both use u_y=0 and zero mean axial displacement at the ends, eigenstrain (1+ν)αθ, no fluid load. The FE uses total-Lagrangian St Venant–Kirchhoff; the beam uses von Kármán beam–column. Residual difference (3.8 % at d/L=0.1) is a finite-thickness effect: it falls to 0.9 % at d/L=0.05 and −0.2 % at 0.025 (§5.4.3). | `slenderness_study.py` |
| C | Deflection vs passage height | H_mid = H0 + w_max is a derived beam-model height; no casing clearance or contact is modelled or inferred (A9). | §4.1 |
| D | Verification independence | Q8 code (own) vs scikit-fem P2-triangle code (different library, element, mesh, constraints): 0.018 %. Beam closed forms vs `solve_bvp`. Equations/kinematics are common to the FE codes and are **not** independently validated (no experiment). | `fe_independent.py`, `check_manuscript.py` C5 |
| E | Numbers | All computed numbers in the text are LaTeX macros generated from `code/results/*.json`. | `make_numbers.py` |
| F | Γp | Like-for-like Γp = 1714 is the headline; the mixed ratio of earlier drafts is excluded. | §3.5 |
| G | Q8 "not converged" claim | Superseded: full-edge-pin ratio converged (0.9980, mesh-independent to 4e-6); the clamp converges slowly (order 1.1–1.7), GCI indicative only. | §5.4.1 |

## 3. Numerical tests actually executed

| ID | Test | Result | Script / output |
|---|---|---|---|
| T1 | Q8 shape functions: partition of unity, derivatives vs central differences (asserted) | pass (< 1e-14 / < 1e-7) | `q8_strip.py` |
| T2 | Q8 patch test (exact stress-free thermal-bending field) on every mesh | max relative residual 5e-13 | `q8_strip.py` → `q8_study.json` |
| T3 | Free bow, ideal point pin | 1.00000 on all meshes (exact field is in the element space; tests implementation only) | `q8_study.json` |
| T4 | Free bow, full-edge pin, 6×2…192×8 | 0.99800 at 192×8; 0.20 % mesh-independent defect (4e-6 thickness, 3e-8 axial change) | `q8_study.json` |
| T5 | Free bow, clamp | −0.0174 at 192×8, extrapolated −0.0168, order 1.1, GCI 4.2 % (indicative; asymptotic range not shown) | `q8_study.json` |
| T6 | Nonlinear tangent vs central finite difference | ≤ 2e-5 (limited by round-off) | `q8_nonlinear.py` |
| T7 | Nonlinear Newton convergence | ≤ 5 iterations/step, relative residual ≤ 4e-11 | `q8_nl.json` |
| T8 | Restrained nonlinear wall, Q8, 24×2…192×8 | w = 2.221e-4 m = 0.444 H0; amplification 1.413; force relaxation 6.5 % (beam 5.9 %); mesh change 0.014 % (axial), 0.07 % (thickness) | `q8_nl.json` |
| T9 | Independent code (scikit-fem P2 triangles, 3072 el.) | w_NL 2.222e-4 m (0.018 % from Q8); mid-span force 0.01 %; linear solution < 1e-4 %; mesh change 0.03 % | `fe_independent.py` |
| T10 | Thin-strip study, d/L = 0.1 … 0.025 at fixed κ and N_c/N_cr = 0.275 | FE/beam(sc) = 1.038, 1.023, 1.009, 1.002, 0.998; force ratio → 1.00; mesh check at d/L=0.025: 0.01 % | `slenderness_study.py` → `slenderness.json` |
| T11 | Closed forms vs independent `solve_bvp` (frozen force, self-consistent fixed point) | relative differences < 1e-6 / 1e-5 | `check_manuscript.py` C5 |
| T12 | Hand recomputation of κ_th, θ̄, N_c, N_cr, p̄, Γp | exact to rounding | `check_manuscript.py` C5 |

## 4. Reference verification (record checked 2026-10-21, OpenAlex bibliographic API)

| Entry | Checked field set | Status |
|---|---|---|
| Soti et al. 2015 (IJHMT 84, 1070–1081, doi …01.048) | authors, title, year, volume, pages | confirmed |
| Alsabery et al. 2019 (HFF 29(10), 3756–3780) | same | confirmed |
| Saleh et al. 2025 (HFF 35(4), 1484–1511) | same | confirmed (OpenAlex misspells one author) |
| Kumar et al. 2026 (Phys. Fluids 38(9)) | authors, title, year, vol/issue | confirmed; article number 092128 taken from the repository audit record, not re-confirmed |
| Christov et al. 2018 (JFM 841, 267–286) | authors, title, volume, pages | confirmed (the repo CSV's 267–305 was wrong) |
| Draskic et al. 2025 (JFM 1012, A17) | authors, title, volume | confirmed; article number from the repository record |
| Rahimimotlagh et al. (IJTS 195, 108637) | authors, title, volume, article no. | confirmed; indexed year 2023 (online), volume year 2024 used |
| Lesoinne & Farhat 1996 (CMAME 134, 71–90) | all | confirmed |
| Brooks & Hughes 1982 (CMAME 32, 199–259) | all | confirmed |
| Celik et al. 2008 (J. Fluids Eng. 130(7), 078001) | title, volume, article | confirmed; author list not returned by the record, standard list used |
| Books (Bird 1960, Carslaw & Jaeger 1947, Boley & Weiner 1960, Timoshenko & Gere 1961, Timoshenko & Goodier 1970, Shah & London 1978, Brezzi & Fortin 1991) | | standard records, as audited earlier in the repository; not re-checked online here |
| Hood & Taylor 1974 (pp. 121–132) | | page range **not machine-verified** |
| Soti DOI | | correct DOI is …2015.01.048 (the repo CSV's …014 is wrong) |

## 5. Unresolved issues and limitations

1. No coupled solution exists; every flow-side number is a reduced-order estimate (lubrication Re·H0/L = 0.42, L/L_T = 1.7: outside the regime where the estimates are reliable).
2. The wall equations (St Venant–Kirchhoff, plane-strain eigenstrain, perfect contact, ideal pins, uniform heater) are assumptions shared by all wall models and are not validated against experiment or an independent physical model.
3. 0.2 % residual in the thinnest strip (d/L = 0.025) is not a mesh error; it is not isolated (candidate: higher-order rotation terms).
4. The clamp-case convergence order (1.1–1.7) is below the formal order; its GCI is indicative.
5. Material data are PEEK-representative, not a datasheet. All numbers scale with them.
6. Not verified online: Hood & Taylor pages, the seven books, Kumar and Draskic article numbers.
7. Fixed-point convergence of the coupled algorithm is not proven or tested.
8. Emerald checks not possible here: the journal's current instructions page was used from earlier web verification only; recheck word limits, anonymisation and AI-disclosure wording on submission.

## 6. Author decisions required before submission

* Confirm the heated face (outer face) matches the physical mounting.
* Supply authors, funding, acknowledgements, AI-use disclosure and data-availability statement (submission system, not the anonymised file).
* Decide whether to replace the PEEK-representative data by a specific grade.
* Produce the Word version required by HFF.
