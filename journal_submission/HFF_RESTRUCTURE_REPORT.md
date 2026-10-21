# Restructure report — v3 (HFF journal pattern)

Date: 21 October 2026.
Base: `main` @ `e19e493` (v2 manuscript).
Driver: the author asked for the paper to be organised the way the 2023 HFF article by
Gupta, Kumar, Kumar and Barak (*International Journal of Numerical Methods for Heat & Fluid
Flow*, 33(6), 2250–2277, doi: 10.1108/HFF-11-2022-0654) is organised — same section
architecture, same writing register, same presentation of front matter, nomenclature,
results and closing matter.

## 1. Section tree, v2 → v3

| v2 | v3 |
|---|---|
| Abstract (Emerald heads) | unchanged, plus `Paper type: Research paper` and a disclosure line |
| — | *Nomenclature moved out of the front matter* |
| 1. Introduction with 1.1–1.5 | **1. Introduction** — flat, no subsections (HFF style), same five paragraphs' worth of material |
| 2. Physical model and assumptions (2.1–2.2) | **3. Problem formulation**, 3.1–3.2 |
| 3. Governing equations (3.1–3.5) | **2. Field equations**, 2.1–2.6 (new 2.5 *Limiting cases*) |
| — | **Nomenclature** — now after §2, as in the journal |
| 4. Reduced wall model and its derivation (4.1–4.7) | **3.3** with 3.3.1–3.3.7 (subsubsections, as HFF nests derivations) |
| 5. Boundary conditions and closure | **3.4** |
| 6. Computational formulation (6.1–6.6) | **4. Solution of the problem**, 4.1–4.6, with a new section lead |
| 7. Grid independence | **4.7 Mesh independence and the grid-convergence index** |
| 8. Verification (8.1–8.2) | **4.8 Verification of the implementation** (4.8.1–4.8.2) |
| 9. Results (9.1–9.9) | **5. Numerical results and discussion**, 5.1–5.9, with a new section lead |
| 10. Discussion | **6. Discussion** (unchanged subsections) |
| 11. Limitations | **7. Limitations** |
| 12. Conclusions (numbered points) | **8. Conclusions**, each point now opens *"It is shown that …"* (HFF convention) |
| Declarations | unchanged (competing interests renamed *Disclosure statement*) |
| `\bibliographystyle{plainnat}` + `\bibliography{references}` | **References** built from `references.tex` (`thebibliography`, no BibTeX run) |
| Appendices A–C | unchanged, still after References |
| — | **Corresponding author** block, as on the last page of the HFF paper |

## 2. What else changed

* **Bibliography route.** `tools/make_references.py` reads `references.bib` and writes
  `references.tex`: alphabetical, Emerald/Harvard, `\bibitem[Surname et al.(Year)]{key}`
  labels so that natbib's `\citep`/`\citet` keep working. The build is now
  `pdflatex; pdflatex` — no BibTeX pass and no `.aux`/`.bbl` dependency. `--check` fails if
  the file is stale.
* **Front matter.** `Paper type: Research paper`, a disclosure sentence, and the reference
  paper's habit of closing the first page with a rule.
* **New §2.5 *Limiting cases*** — the rigid-wall, one-dimensional wall-conduction,
  frozen-force and Euler-column limits, written in the same register as the reference
  paper's §2.1 and tied to the equations used later as checks.
* **Undefined behaviour fixed.** The nomenclature table was introduced by a bare `\small`
  with no `\normalsize` after it in v2, which would have set the whole paper in small type;
  the size change is now scoped.
* **Cross-references re-pointed.** The only hard-coded range (`§2.–§2.5`) in the
  contributions paragraph now reads `§2 and §3`, because the sections it named were
  reordered.
* **Build scripts.** `tools/build_zip.py` ships `references.tex` and requires it;
  `tools/check_tex.py` audits citations against `references.tex` as well as
  `references.bib`.
* **Reproducibility of the restructure itself.** `tools/restructure_hff.py` performs the
  remapping from the v2 source (read with `git show main:journal_submission/main.tex`), so
  the transformation is reviewable rather than a hand edit of 2 200 lines.

## 3. What did *not* change

* Every number, figure, table, citation and limitation of v2. The restructure moved and
  retitled material; it did not add or remove a result. Word count rose from ≈13 600 to
  ≈14 000 because of the new section leads, §2.5 and the four extra sentences of the
  conclusions.
* The 55 references, the 12 figures and the 11 tables, all unchanged.
* No PDF was compiled: there is still no TeX engine in this environment. Validation is
  structural only (`python3 tools/check_tex.py`: 119 labels, 86 references, 0 unresolved,
  0 duplicate, 55 citations against 55 keys, all figures and table fragments present).

## 4. Known gaps after this pass

1. **Page count is still an estimate** (30–36 pp). The new nesting adds roughly one page of
   heading space; the two-pass compile in Overleaf is the first real measurement.
2. **`emerald.cls` is not used.** The article class with Emerald-style front matter is a
   stand-in; the mapping to the journal class is described in `README.md`.
3. **Author block is a placeholder.** Names, affiliations and the corresponding e-mail are
   the author's to insert; inventing them would be improper.
4. **Received/revised/accepted dates** are deliberately absent — they are journal-assigned
   data, not manuscript content.
