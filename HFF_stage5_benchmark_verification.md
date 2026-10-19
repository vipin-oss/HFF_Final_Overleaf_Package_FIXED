# HFF Stage 5 — Benchmark verification and pre-coding readiness

**Repository:** `vipin-oss/HFF_Final_Overleaf_Package_FIXED`
**Working branch:** `arena/c875f9b3-hff-final-overleaf-package-fix`
**Starting commit:** `5a255212a51374f7eb178647eb12b0a9c2b67ded` (`Initial Overleaf Import`)
**Date of audit:** 19 October 2026
**Scope:** literature/benchmark verification and readiness audit only. **No solver code was written and no simulation was run in this stage.**

---

## 0. How to read the evidence labels

| Label | Meaning |
|---|---|
| **CONFIRMED (primary)** | Inspected the primary document itself (or the publisher's own rendering of it) and read the value/statement there. |
| **CONFIRMED (independent records)** | Primary document not accessible; the fact is fixed by several independent records that agree, each traceable. |
| **CORROBORATED** | Consistent with independent reproductions, but the originating document was not inspected. |
| **UNRESOLVED** | Evidence insufficient; the item is named and retained open. Never silently substituted. |
| **DERIVED** | Obtained by derivation inside this audit, not taken from a source. |

Nothing in this report is labelled *validated*. Validation requires comparison with physical experiment; no experimental data set has been identified in the package.

---

## 1. `Nu_T1 = 4.861` — full verification

### 1.1 Exact source

| Field | Verified content |
|---|---|
| Authors | R. K. Shah and A. L. London |
| Title | *Laminar Flow Forced Convection in Ducts: A Source Book for Compact Heat Exchanger Analytical Data* |
| Edition / series | First edition; Supplement 1 to *Advances in Heat Transfer* (series editors T. F. Irvine, Jr. and J. P. Hartnett) |
| Publisher / place / year | Academic Press, New York, 1978 |
| ISBN | 0-12-020051-1 (13-digit 978-0-12-020051-1) |
| Extent | xiv + 477 pp. |
| Chapter | **Chapter VII, "Rectangular Ducts", pp. 196–222** (parallel plates are the aspect-ratio-zero limit of this chapter; the parallel-plate chapter itself, Chapter VI, is pp. 153–195) |
| Section | §A, fully developed flow, §2 "Specified wall temperature" |
| Table | **Table 43** — caption reproduced by the publisher as *"RECTANGULAR DUCTS: Nu_T FOR FULLY DEVELOPED LAMINAR FLOW, FOR ONE OR MORE WALLS TRANSFERRING HEAT"* |
| Page of Table 43 | **not established** — only the chapter range (196–222) is documented. See §1.7. |
| DOI | none (pre-DOI monograph) |
| Publisher record | Elsevier/ScienceDirect monograph ISBN 978-0-12-020051-1; Chapter VII PII `B9780120200511500127` |

### 1.2 What the table actually contains

The publisher-hosted rendering of the Chapter VII text reproduces Table 43, including the parallel-plate limit. The relevant row is the aspect-ratio `2b/2a = 0.0` row, whose single-heated-wall entry is **4.861**. The accompanying narrative records the provenance of the numbers:

> "Shah and London [13] defined the Nusselt number with the hydraulic diameter based on the wetted perimeter, instead of the heated perimeter, as done in [95]. They recomputed Nu_T, as provided by Schmidt [252], and are reported in Table 43 and Fig. 39."

(Quoted from the publisher's rendering of the chapter, not from a scanned copy of the printed page.)

Two consequences follow immediately and matter for us:

1. the characteristic length is the **wetted-perimeter** hydraulic diameter, not the heated-perimeter one;
2. the numbers are **recomputed** values (from Schmidt's finite-difference solutions), not a fresh analytical solution — which is why the book, not Schmidt, is the correct citation, but also why a digit-level transcription error is conceivable and a printed-copy check is still desirable.

### 1.3 What thermal boundary condition the value belongs to

- **T1 family**: one wall held at a **uniform (constant) temperature**, the opposite wall **adiabatic**. This is *not* uniform wall heat flux.
- The sibling single-heated-wall value is **Nu_H1 = 5.385** for one wall at uniform heat flux with the other adiabatic (Table 44 of the same chapter; the value was verified in an earlier stage and was **not** re-inspected in this one).
- The two-sided values belong to different configurations: **Nu_T = 7.541** (both walls at the same uniform temperature) and **Nu_H2 = 8.235** (both walls at equal uniform heat flux). The document already forbids using these as one-sided targets (Chapter 9); that prohibition is correct.

So the four values used in V‑B map as:

| Document target | Shah & London boundary condition | Value |
|---|---|---|
| V‑B1 (i) | both walls uniform *T* (T) | 7.541 |
| V‑B1 (ii) | both walls equal uniform flux (H2, parallel plates where H1≡H2) | 8.235 |
| V‑B2 (i) | one wall uniform flux, other adiabatic (H1) | 5.385 |
| V‑B2 (ii) | one wall uniform *T*, other adiabatic (T1) | **4.861** |

### 1.4 Characteristic length and Nusselt definition

For a plane slit of spacing `H₀`, with one wall heated and one adiabatic:

- wetted perimeter `P = 2` per unit width; area `A = H₀`; hence `D_h = 4A/P = 2H₀`;
- Shah & London's `Nu` is `h D_h / k_f` with `h = q″_heated /(T_w − T_b)`, where `q″` is the flux **at the heated wall** and `T_b` is the mass-averaged (bulk) temperature.

The document's own post-processing (Ch. 8, §"Post-processing definitions") uses `Nu = 2H₀ h/k_f` with `h = q_w/(T_w − T_b)` and `D_h = 2H₀` in the geometry table. **The normalization therefore matches exactly**, provided (a) `D_h` is the wetted-perimeter value `2H₀` and not the heated-perimeter value `4H₀`, and (b) `q_w` is the flux *into the fluid* at the heated wall. Both are now stated explicitly in the source (the `q_w` sign was corrected in this stage; see §5).

> **Trap recorded for the implementation:** if the same physical flux is normalized with the heated-perimeter diameter `D_h,heated = 4H₀`, the number becomes `2 × 4.861 = 9.722`. A factor-of-two error here is easy to make and would not look like a sign error in a plot.

### 1.5 Development assumptions

The 4.861 value is the **fully developed asymptotic value**, i.e. the limit `x* → ∞` with `x* = x/(D_h Re Pr)`, under:

- hydrodynamically fully developed, laminar, constant-property flow (plane Poiseuille);
- thermally fully developed temperature profile;
- negligible axial conduction in the fluid (consistent with `Pe = 348`; relative error `O(Pe⁻²) ≈ 10⁻⁵`);
- negligible viscous dissipation (`Br ≈ 10⁻⁶`);
- negligible buoyancy (`Ri ≈ 1.7 × 10⁻³`);
- no conjugate wall conduction (the wall is a boundary condition, not part of the domain).

For the **T1** family the approach to the asymptote is controlled by the decaying wall-to-bulk temperature difference; convergence to 4.861 is therefore *slower in physical length* than for the H1 family, and the benchmark duct must be long enough (or the computation extrapolated in `x*`) before the value is compared. **The document's V‑B rows currently specify neither a duct length nor an evaluation station**, which is a genuine specification gap independent of the value itself (§5, item B‑2).

### 1.6 Applicability to *our* formulation — verdict

| Requirement | Shah & London | Document | Match |
|---|---|---|---|
| Slit geometry, one heated wall | yes | rigid limit of the slit; upper wall heated, lower wall adiabatic (B3) | **yes** |
| Characteristic length | `D_h = 2H₀` (wetted perimeter) | `D_h = 2H₀` | **yes** |
| Temperature difference | `T_w − T_b` | `T_w − T_b` | **yes** |
| Flux location | heated wall only | `q_w` on `Γ_if` (heated wall) | **yes**, after sign correction |
| One wall isothermal, other adiabatic | yes | V‑B2 says "one wall uniform T"; the adiabatic companion is implied by B3 but **not stated in the V‑B2 row** | **needs one sentence** |
| Hydrodynamic development | fully developed inlet | B1: plane-Poiseuille inlet | **yes** |
| Thermal development | `x* → ∞` | not stated; no duct length given | **needs specification** |
| Constant properties / no axial conduction / no dissipation / no buoyancy | yes | A2, A7, Pe = 348, Ri = 1.7×10⁻³ | **yes** |

**Verdict: 4.861 is directly applicable to the V‑B2 T1 case as normalized in this document.** The value does not need replacing; the *test definition* needs two additions (adiabatic companion wall; evaluation station / duct length), and the *normalization* should be written out once in the chapter rather than left implicit.

### 1.7 Evidence status and the one residual item

| Question | Status |
|---|---|
| Does the primary source contain 4.861 for one wall transferring heat? | **CONFIRMED** — publisher-hosted Table 43 text |
| Is it constant *T*, not uniform flux? | **CONFIRMED** — table heading "specified wall temperature"; T1 family |
| Characteristic length | **CONFIRMED** — wetted-perimeter `D_h`, stated in the chapter text |
| Independent corroboration | Independent standard heat-transfer tables give 4.86 for parallel plates with one side insulated at uniform wall temperature; the annular-duct correlation literature reproduces 4.861 in the `r* → 1` limit |
| Exact **printed page number** of Table 43 | **UNRESOLVED** — the accessible publisher record gives the chapter range (196–222) but not the table page |
| Direct inspection of a scanned/printed copy | **not performed** — the archive.org scan is lending-restricted (search-inside disabled); no other full scan is accessible |

**Action retained (non-blocking for solver development):** consult a printed or library copy of the 1978 edition and record the page on which Table 43 sits, plus a verbatim transcription of the `2b/2a = 0.0` row. This is a *documentation* residual only; the value and its meaning are no longer in doubt.

**Do not** quote a page number for this table until that check is done. No page number has been invented here.

---

## 2. Hood & Taylor (1974) — bibliographic verification and claim check

### 2.1 Verified record

| Field | Verified content |
|---|---|
| Authors | P. Hood and C. Taylor |
| Title | "Navier–Stokes equations using mixed interpolation" |
| Publication | In *Finite Element Methods in Flow Problems*, Proceedings of the International Symposium, University of Alabama in Huntsville, 1974 |
| Editors | J. T. Oden, O. C. Zienkiewicz, R. H. Gallagher, C. Taylor |
| Publisher | University of Alabama in Huntsville Press, Huntsville, Alabama |
| Pages | **121–132** |
| DOI | **none** (1974 conference proceedings volume; no DOI exists) |
| Stable identification | ISBN-less proceedings; cite by editors, place, year and pages. Companion journal paper: Taylor, C. & Hood, P., *Computers & Fluids* **1** (1973) 73–100, DOI `10.1016/0045-7930(73)90027-3` |

**Evidence:** the primary volume is not digitised in any accessible repository, so the page range is **CONFIRMED (independent records)** rather than from the volume itself. Independent citing records that agree on 121–132 include: Springer, *Finite Element Spaces for Linear Saddle Point Problems* (2016); Springer, *Refined a posteriori error estimation for classical and pressure-robust Stokes FEM* (Numer. Math., 2019); *Int. J. Numer. Methods Fluids* (2012, p. 121–132); *Int. J. Numer. Methods Eng.* (Kawahara, 1976, p. 121–132). One citing record gives 121–131; the weight of independent citations is 121–132. A citation-level discrepancy of one page is recorded rather than hidden.

### 2.2 Does the reference support the statement it is attached to?

The original sentence in Ch. 8 read:

> "… approximated by Taylor–Hood elements …, **satisfying the discrete inf–sup condition for the Stokes limit** of (2) **[hood1974navier, brezzi1991mixed]**"

Assessment:

- Hood & Taylor (1974) is the **origin of the P2–P1 pair** and demonstrates mixed interpolation for the Navier–Stokes equations. It **does** support: "this element pair is the one we use, and it is the historical Taylor–Hood pair."
- It **does not** prove the discrete inf–sup (LBB) condition. That result belongs to the Babuška–Brezzi theory and is established for this pair in Brezzi & Fortin (1991), which is already cited.
- Therefore the *joint* citation was defensible only if the two roles are separated. **Corrected** in this stage by rewriting the sentence to attribute origin to Hood–Taylor and stability to Brezzi–Fortin.

### 2.3 Benchmark verification vs physical-model validation — kept distinct

Hood & Taylor is a **numerical-method** reference. It supports nothing about thermoelastic channel behaviour, conjugate heat transfer, steady small-strain validity, or the present model's fidelity. Taylor–Hood is **not** an FSI benchmark and must not be described as one. Likewise, the document's exclusion of Turek–Hron from the steady small-strain class (Ch. 9) remains correct and is not affected by this verification.

---

## 3. Remaining reference and benchmark requirements

Only items that are still open, plus items where this stage found a discrepancy, are listed. Resolved items were not re-searched.

| ID | Exact claim / equation | Source needed | Located & inspected? | Supports the claim directly? | Blocks isolated verification? | Blocks coupled implementation? |
|---|---|---|---|---|---|---|
| **C‑1** | `Nu_T1 = 4.861` | Shah & London (1978), Table 43 | **Yes** (publisher text); printed page not inspected | **Yes** | No | No |
| **C‑2** | V‑D: developing `Nu(x)` at matched `R_k, D_r, Pe` | Rahimimotlagh et al. (2024), *Int. J. Therm. Sci.* **195**, 108637 | Record + abstract inspected; **numerical series not extracted** | Record yes; matching points **not yet** | No | **Yes** |
| **C‑3** | V‑E: steady bulge / `Q–Δp` target | Christov et al. (2018), *JFM* **841**, 267–286 | Record inspected; **no data set constructed** | Theory class only | No | **Yes** |
| **C‑6** | PEEK property set `E, ν, α, k_s, ρ_s, c_s`, yield band; `β_f` at fixed `T_ref` | Manufacturer datasheet(s) + property evaluation temperature | **No** | — | No (verification may run on the documented band) | **Yes** |
| **C‑7** | Originality/positioning claims | Scopus/WoS systematic search | **No** | — | No | No (manuscript-level) |
| **C‑9** | Outflow condition B2 (exit length, no backflow, pressure datum) | Sensitivity study, to be computed | **No** | — | No (flag results) | **Yes** |
| **C‑12** | Independent second solver (FEniCS) | Platform commitment | **No** | — | No | **Yes** |
| **B‑1** | Buoyancy exclusion `Ri = 1.7×10⁻³` | Derived + guard | Yes (re-derived consistent) | **Yes** | No | Guard only |
| **B‑2** *(new)* | V‑B2 evaluation station, duct length, adiabatic companion wall, wetted-perimeter normalization | Shah & London + test definition | Partial — value confirmed, test definition incomplete | — | Thermal runs only | Yes (as a reporting rule) |
| **B‑3** *(new)* | Energy-equation SUPG coefficient | Standard stabilized-FEM literature | **Not specified in the document** | — | Thermal runs only | **Yes** |
| **B‑4** *(new)* | Weak-form signs and definitions of `a_T, a_kf, a_ks` | Derivation (this stage) | **Yes — errors found and corrected** | — | **Yes (must be signed off)** | **Yes** |
| **B‑5** *(new)* | Property evaluation temperature for a 60 K through-wall drop | Datasheet + justification | **No** | — | No | **Yes** |

### 3.1 Reference-record errors found (documentation only)

The manuscript's `references.bib` was **correct** in all three cases; the Stage‑4 summary CSV (`HFF_final_reference_status.csv`) was **wrong**. These are audit-record errors, not manuscript errors, but they matter because the CSV is the traceable record.

| Entry | Stage‑4 CSV says | Crossref / publisher says | Disposition |
|---|---|---|---|
| Soti, Bhardwaj & Sheridan (2015) | DOI `…2015.01.014` | DOI `…2015.01.048`; vol. 84, pp. 1070–1081. The `.014` DOI resolves to an **unrelated** paper (Barash, *Dependence of fluid flows in an evaporating sessile droplet…*) | CSV wrong; `.bib` right; corrected in Stage‑5 CSV |
| Lesoinne & Farhat (1996) | pp. 71–**99** | vol. 134, pp. 71–**90** | CSV wrong; `.bib` right |
| Christov et al. (2018) | pp. 267–**305** | vol. 841, pp. 267–**286** | CSV wrong; `.bib` right |
| Rahimimotlagh et al. (2024) | authors "Rahimimotlagh, …" | publisher byline "**Z.** Rahimimotlagh"; `.bib` gave the given name as "**Peyman**" | `.bib` **corrected** to "Zahra"; see note below |

Rahimimotlagh note: the publisher displays the initial only; the author's professional profile gives "Zahra Rahimimotlagh". The given name "Peyman" in the previous `.bib` is not supported by any record and has been replaced. If a journal proof requires initials only, `Z.` is safe.

Also found: Appendix B's "Bibliographic integrity statement" still described `gupta2024photothermo` as having "title and DOI not retrievable", contradicting the reference table (which records it as verified at Stage 2). Corrected to match the verified record.

**Unchanged and re-confirmed this stage:** Turek & Hron (2006) pp. 371–385, DOI `10.1007/3-540-34596-5_15`; Rahimimotlagh et al. (2024) vol. 195, art. 108637, DOI `10.1016/j.ijthermalsci.2023.108637`; Saleh et al. (2025) vol. 35(4), pp. 1484–1511; Kumar et al. (2026) vol. 38(9), art. 092128; Draskic et al. (2025) vol. 1012.

### 3.2 V‑D source parameters actually visible

The Rahimimotlagh et al. abstract confirms: steady laminar flow in straight **thick-walled flattened channels**, **constant outside wall temperature**, **Re 50–1250**, thickness ratios **0.153 / 0.6 / 0.8** (solid-to-fluid), conductivity ratios **1.3 / 27 / 646** (glass / steel / copper), and reports local interface heat flux, interface temperature, bulk temperature and axial Nusselt number. It does **not** state "water" or "338 K" in the abstract. The Stage‑4 CSV's "water; 338 K" is therefore **not confirmed at abstract level** and must be checked against the full text before it is used as a matching condition. This sharpens C‑2 rather than closing it.

---

## 4. Pre-coding checklist outcome (summary)

Full table in `HFF_stage5_pre_coding_checklist.md`. Counts across 24 requirement rows:

- **COMPLETE:** 12
- **INCOMPLETE:** 9
- **UNRESOLVED:** 3

The most consequential change from Stage 4 is that **weak-form consistency is now INCOMPLETE**, not COMPLETE: two boundary-term signs in the displayed weak form contradicted the chapter's own integration-by-parts prose and the stated single-normal convention, and the bilinear forms `a_T, a_kf, a_ks` were never defined. The signs are corrected on this branch; the item stays INCOMPLETE until an independent hand re-derivation is signed off and the forms are defined in the text.

---

## 5. Corrections applied to the source (working branch only)

| # | File | Change | Reason |
|---|---|---|---|
| S1 | `chapters/ch08.tex` | `eq:weaks`: RHS `+∫σ n·φ` → `−∫σ n·φ` | Solid outward normal is `−n`; the corrected sign is what makes the chapter's own stated residual `+∫σ_s n·φ` true, and restores cancellation against the fluid term `−∫σ_f n·v` under `σ_s n = σ_f n`. With the old sign the pressure load entered with the wrong sign and the two interface terms added instead of cancelling. |
| S2 | `chapters/ch08.tex` | `eq:weaktf`: RHS `−∫k_f∇T_f·n χ` → `+∫k_f∇T_f·n χ` | Direct consequence of integration by parts with `n_f = n`; restores the cancellation against the solid term `+∫k_s∇T_s·n χ` under flux continuity. |
| S3 | `chapters/ch05.tex` | B6: `−k_s∇T_s·n_out = q″` → `+k_s∇T_s·n_out = q″`, with "`q″>0` is heat supplied to the solid" | For a heater on the outer face the temperature increases outward, so `∇T·n_out > 0`; the old form required `q″<0`. The corrected form is the one consistent with `eq:weakts` and with `ΔT_t = q″d/k_s > 0`. |
| S4 | `chapters/ch05.tex` | Traction-balance sentence: `σ⁽ˢ⁾·n + σ⁽ᶠ⁾·n_f = 0, n_f = −n` → `σ⁽ˢ⁾·n_s + σ⁽ᶠ⁾·n_f = 0, n_s = −n, n_f = n` | The old notation used `n` for the solid and `n_f = −n` for the fluid, i.e. two different norms in one equation; the result `σ_s n = σ_f n` is unchanged, but the statement is now correct. |
| S5 | `chapters/ch08.tex` | Added one sentence fixing the sign of each boundary term by the subdomain outward normal | Prevents re-introduction of S1/S2 during implementation. |
| S6 | `chapters/ch08.tex` | `q_w = −k_f∇T_f·n` → `q_w = +k_f∇T_f·n` ("into the fluid") | The old definition was the flux *out of* the fluid, so `h = q_w/(T_w−T_b)` was negative on a heated wall and would have produced `Nu < 0` in every thermal benchmark. |
| S7 | `chapters/ch08.tex` | Taylor–Hood sentence re-attributed: origin → Hood–Taylor; inf–sup → Brezzi–Fortin | Citation supports the element choice, not the LBB proof. |
| S8 | `references.bib` | `hood1974navier`: added `pages = {121--132}`, editors; note updated | Page range verified. |
| S9 | `references.bib` | `shah1978laminar` note: C‑1 status updated | Records the Table 43 confirmation and the residual page check. |
| S10 | `references.bib` | `rahimi2024conjugate`: given name `Peyman` → `Zahra` | Unsupported given name removed. |
| S11 | `chapters/audit_appendix.tex` | C‑1 status updated | Reflects the evidence. |
| S12 | `chapters/audit_appendix.tex` | Bibliographic integrity statement corrected (Gupta; Hood–Taylor; Shah) | Removed a self-contradiction with the reference table. |

**Not changed:** geometry, material data, operating conditions, dimensionless groups, benchmark tolerances, model assumptions, and the research direction. No numerical parameter was adjusted.

**Compilation status:** no TeX engine exists in this sandbox, so `main.pdf` was **not** regenerated. The PDF in the repository is the 49-page Stage‑4 build and is now one revision behind the source on the twelve lines above. **Overleaf must be recompiled** before the PDF is circulated. All edits are local sign/attribution changes in math mode or reference fields; no structural LaTeX was altered.

---

## 6. Final decisions

### 6.1 Fluid solver verification — **READY TO PROCEED**

- V‑A is an exact solution of the same equations and boundary conditions: plane Poiseuille. The document's profile `u = 6U(y/H₀)(1−y/H₀)` and `f_D Re_{D_h} = 96` were re-derived and are mutually consistent with `D_h = 2H₀` and Darcy normalization (`f_D = 2τ_w/(ρU²)`, `Δp = 12μUL/H₀²`).
- Outflow condition B2 is a do-nothing condition with a pressure datum; it is well posed, and its sensitivity (C‑9) is a *reporting* requirement, not a blocker for V‑A.
- No code exists. Nothing is verified yet.

### 6.2 Solid thermoelastic solver and stress post-processing — **READY, CONDITIONAL**

Ready: V‑C1a, V‑C1b, V‑C2, V‑C3 are closed-form targets whose structure is consistent with standard thermoelasticity (spot-checked this stage: the plane-strain closure `Eαθ/(1−ν)`, the free-strip mean `−Eαθ/3`, and the amplification `1/(1−(μL/π)²) = 1.38` at `μL = 1.65`, matching the tabulated 1.39). The full set was re-derived in the earlier reconciliation audit, not re-derived from scratch here. The mean-stress identity is a genuine runtime assertion.

Conditions:
1. the corrected sign of the interface traction in `eq:weaks` must survive an independent hand re-derivation (S1);
2. material magnitudes remain datasheet-conditional (C‑6) — verification can run on the documented band, but reported stresses are not final numbers until the freeze;
3. the reduced beam–column model carries a documented 2.3% one-sided error at baseline; it is a *model* limitation, not a solver defect.

### 6.3 Thermal solver verification — **READY, CONDITIONAL**

Ready: the four targets are the correct one-/two-sided families and the normalization matches (`D_h = 2H₀`, `T_w − T_b`, heated-wall flux). **4.861 was re-confirmed against Table 43 in this stage.** 7.541, 8.235 and 5.385 were verified in earlier stages and were not re-inspected now; they belong to the same table family (Tables 43 and 44) and no discrepancy has appeared.

Conditions:
1. state the adiabatic companion wall and the evaluation station/duct length for V‑B2 (T1 converges slowly in `x*`);
2. specify the SUPG coefficient `τ` explicitly — "standard residual-based coefficient" is not an implementable specification, and the stated "no overshoot > 0.1% of range" acceptance criterion is not guaranteed by plain SUPG (it is a monotone-scheme property). Either add a discontinuity-capturing term or restate the criterion as a measured, reported quantity;
3. note that the code includes axial conduction while the benchmark neglects it; at `Pe = 348` the difference should be `O(10⁻⁵)`, but it must be shown, not assumed.

### 6.4 Fully coupled fluid–thermal–structural implementation — **HOLD**

Released only when **all** of the following close:

| Blocker | Why it blocks |
|---|---|
| B‑4 weak-form correction signed off | a wrong interface sign is not a discretization error; it is a different problem |
| Interface conditions (i)–(iii) implemented, quadrature-consistency audit run | interface cancellation is the formulation's central claim |
| C‑2: V‑D data extracted at matched `R_k, D_r, Pe` | no conjugate thermal benchmark exists otherwise |
| C‑3: V‑E data set constructed | no coupled elastic-wall benchmark exists otherwise |
| C‑6: property freeze, including evaluation temperature for a 60 K wall drop | reported `w`, `N_θ`, `σ` are not reproducible quantities until frozen |
| C‑9: outflow sensitivity | the pressure datum sets the wall load |
| C‑12: independent second solver committed | no independent check of the coupled fields |
| V‑G mesh-map isolation executed once | separates mesh-motion error from model error |
| Regime guards A‑1–A‑6 implemented as runtime assertions | the model's validity envelope is otherwise unenforced |

---

## 7. Integrity statement

- No solver code was written; no simulation was run; no numerical result is reported as verification.
- No reference, page number, DOI, or benchmark value was fabricated. Where a fact could not be inspected, it is marked UNRESOLVED and the required evidence is named.
- Confirmed facts (Table 43 value; Hood–Taylor pages; Crossref records), independently derived results (the sign analysis of §5), and unresolved evidence (Table 43 page number; C‑2/C‑3 data) are kept separate throughout.
- The research direction, model, geometry, and all numerical parameters are unchanged.
- Benchmark verification and physical-model validation have been kept distinct: confirming 4.861 verifies a *code* against a tabulated solution; it says nothing about whether the thermoelastic channel model is physically valid.
