# HFF manuscript package — thermally induced wall deformation in a laminar channel

Target journal: *International Journal of Numerical Methods for Heat & Fluid Flow* (HFF, Emerald).
Title: *Thermally induced deformation and conjugate heat transfer in a channel with a thermoelastic wall:
formulation, reduced-order analysis and finite-element verification.*

**Scope statement (important).** The paper reports a formulation, a reduced-order (closed-form) analysis and a
finite-element verification of the *wall only*. The coupled fluid–structure–thermal solver is **specified, not
executed**: no coupled result is reported and every flow-side number is labelled a reduced-order estimate.

## Contents

| Path | What it is |
|---|---|
| `main.tex`, `sections/*.tex` | manuscript source (abstract, Sections 1–6, nomenclature appendix) |
| `references.bib`, `emerald_harvard.bst` | bibliography (18 entries, all cited) and a local Emerald-style Harvard style |
| `numbers.tex`, `tab_q8_mesh.tex`, `tab_q8_nl.tex` | **auto-generated** by `code/make_numbers.py`; every computed number in the text is a macro from here |
| `figures/` | Fig. 1 (TikZ source + PDF/EPS); Figs. 2–5 as vector **PDF and EPS** (fonts embedded) |
| `code/hff_model.py` | reduced-order model; single source of the analytical numbers |
| `code/q8_strip.py` | plane-strain Q8 free-bow / end-support / mesh study (Table VI, Fig. 4) |
| `code/q8_nonlinear.py` | restrained, geometrically nonlinear Q8 wall (Table VII, Fig. 5) |
| `code/make_numbers.py`, `code/make_figures.py` | regenerate macros, tables and figures from `code/results/*.json` |
| `code/check_manuscript.py` | cumulative consistency checks (52 checks, all pass) |
| `main.pdf` | built manuscript, 17 pages |

## Rebuild

```bash
pip install -r code/requirements.txt          # numpy, scipy, matplotlib (Python >= 3.10)
./build.sh                                      # model + Q8 solvers -> numbers/tables/figures -> pdflatex/bibtex
python3 code/check_manuscript.py                # all checks must pass
```
`build.sh` needs `pdflatex`, `bibtex` and `pdftops`. Runtime of the numerical part is about one minute.
On Overleaf, upload the folder, set the main file to `main.tex`, and keep `numbers.tex`, `tab_*.tex`, `figures/`.

## Headline results (all produced by the code)

* Strip heated on its **outer** face bows **away from the channel**; free curvature
  κ_th = (1+ν)α q″/k_s = 1.4 1/m (independent of thickness); the passage widens.
* Baseline (H0 = 0.5 mm, L = 30 mm, d = 3 mm, U = 0.05 m/s, q″ = 5 kW/m², water, Re = 50, PEEK-class strip):
  w_max = 0.428 H0 (self-consistent beam–column), 0.438 H0 (frozen force), **0.444 H0 (2-D nonlinear Q8)**;
  the 2-D result is 3.8 % above the self-consistent reduced-order value.
* Heat-flux ceilings (frozen force): guard w/H0 = 0.5 at 5.5 kW/m², stress cap at 6.0 kW/m², buckling margin 2 at 9.1 kW/m².
* Γp (thermal/hydraulic deflection) = 1714 (like-for-like); the "mixed" ratio of earlier drafts is **not** used.
* Q8: patch test passes (5e-13); ideal point pin 1.00000; full-edge pin 0.9980 (mesh-independent 0.20 % defect);
  restrained nonlinear amplification 1.413; membrane-force relaxation 6.5 % (beam 5.9 %).

## Decisions taken (please confirm or change)

1. **Source version.** The sign chain of the `b04b30e` line was verified independently and is used (outer-face heating,
   bow away from the channel). The fluid-side-heater variant is *not* modelled (stated in Section 6).
2. **Journal style.** The repository contains no earlier FEM paper to copy from, so structure, figure fonts/sizes,
   introduction register and the Harvard reference style follow the Emerald/HFF author guidelines
   (structured abstract ≤ 250 words, ≤ 6 keywords, Roman-numeral tables, EPS/PDF figures). Figures use serif
   (Times-compatible) text at 10 pt labels / 9 pt ticks / 8–8.5 pt legends, 16 cm wide.
3. **Removed on purpose:** the mixed Γp headline, the old "Q8 not converged" claim (superseded: the full-edge pin *is*
   converged), unsupported statements about the casing clearance and the heater mounting, two unverifiable references.
4. **Added:** a restrained, geometrically nonlinear Q8 solver. It was needed because the earlier Q8 study used zero
   axial restraint and zero-mean temperature (no membrane force), so it could not test the beam–column amplification.

## Honest limitations to keep in mind

* No coupled results; lubrication and quasi-developed estimates (Section 4.4) are order-of-magnitude only
  (Re·H0/L = 0.42, L/L_T = 1.7).
* Material data are representative of PEEK, not a datasheet. Perfect thermal contact, ideal pins, idealised heater,
  no casing contact.
* The 2-D wall is 3.8 % above the beam–column value. The force difference does not explain it and shear flexibility
  explains about 1.2 percentage points; the rest is **not attributed**.
* The fixed-point algorithm has no convergence proof.

## Reference verification status (check before submission)

* **Saleh et al. (2025), HFF 35(4), 1484–1511, doi 10.1108/HFF-01-2025-0045 — NOT re-verified** in the last session
  (Crossref returned HTTP 429). Please check authors, title and pages.
* Hood & Taylor (1974) page numbers are from memory; please verify.
* The repository's reference CSV listed a wrong DOI for Soti et al. (…014); the bib uses …048, which is the correct one.
* Gupta and Turek entries were dropped (could not be verified).

## Emerald / HFF submission notes

* Word count (Emerald counting: text + captions + 280 words per figure/table, display maths excluded):
  about 8.7 k including 5 figures and 8 tables; limit 10 000. Re-count in your Word file.
* HFF asks for **Word** submission and **double-anonymous** review: `\author{}` is empty; add authors, funding,
  acknowledgements and the **AI-use disclosure** in the submission system / title page, not in the anonymised file.
* To make a .docx: export from Overleaf, or use `pandoc main.tex -o main.docx --citeproc` and re-insert the generated
  numbers (the macros come from `numbers.tex`); check equations and Roman-numeral tables afterwards.
* The `.bst` is a local Emerald-style approximation; the journal's own typesetting will reformat references.

## Corrections to my earlier advisory

* I inferred α ≈ 7e-5 from (1+ν)α = 7e-5; the correct α = 5e-5.
* I wrote dT/dy < 0 in the wall; the correct sign is dT/dy > 0 (outer face hot), as in the paper.
