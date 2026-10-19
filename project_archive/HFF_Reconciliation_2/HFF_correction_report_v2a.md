# Correction report v2a — narrow-scope consistency fix (membrane-force transcription; Ri basis wording)

**Scope:** `HFF_Reconciliation_2/` only. No change to the research problem, the model, the
LaTeX source, or any numerical result. No solver programming.

---

## 1. Thermal membrane force N_θ (ERR-01) — resolved: reconciliation layer was wrong, document was right

**Re-derivation from the stated constitutive assumptions.** Plane-strain strip (ε_zz = 0), free
lateral faces (σ_yy = 0), uniform rise θ̄, axial displacement blocked (mean ε_xx = 0):

* ε_zz = 0 ⟹ σ_zz = ν σ_xx − E α θ̄;
* ε_xx = σ_xx/E − ν σ_zz/E + α θ̄ = 0 ⟹ σ_xx (1−ν²)/E + α θ̄ (1+ν) = 0
  ⟹ **σ_xx = −E α θ̄/(1−ν)**;
* **N_θ = d σ_xx = −E d α θ̄/(1−ν)** (Chapter 4, eq. `eq:ntheta` — unchanged).

Numbers: N_θ = −(3.6×10⁹)(3×10⁻³)(5×10⁻⁵)(32.3)/0.6 = **−2.91×10⁴ N/m**;
N_cr = π²D_s/L² = 1.053×10⁵ N/m; **N/N_cr = 0.276 ≈ 0.275** — as recorded everywhere.

**Origin of the spurious factor 2.** The mean stress of the same restrained state is
σ_m = (σ_xx + σ_zz)/3 = −2E α θ̄/[3(1−ν)] (register EQ-09, benchmark V-C1b). Transcription of
that coefficient into a *force* formula dropped the 3, yielding the erroneous
"−2Eαθ̄/(1−ν)·d" in three Stage-2 reconciliation-layer spots — while every one of them still
quoted the correct number 2.9×10⁴ N/m (the CAL2-13 substitution even contained the tell-tale
"= 5.8e4/2"). A genuine factor 2 would give N/N_cr = 0.55, contradicting all recorded values;
the number was always computed from the single-factor law.

**Conflict search (all project files).**
| Location | Formula found | Status |
|---|---|---|
| `chapters/ch04.tex` eq:ntheta | −Ed αθ̄/(1−ν) | correct — untouched |
| `chapters/ch07.tex` Table 7.1 | −Ed αθ̄/(1−ν), substitution → −2.9×10⁴ | correct — untouched |
| `chapters/appendix.tex` A5 | −2.88×10⁴ (θ̄ = 32 K rounding) | correct — untouched |
| `HFF_Independent_Audit_2/HFF_calculation_recheck.csv` CAL-11 | −E d α θ̄/(1−ν) → −2.90×10⁴ | correct — untouched (original preserved) |
| `HFF_Reconciliation_2/HFF_beamcolumn_rederivation.md` §1 | −**2**E α θ̄/(1−ν)·d | **fixed** (§1b derivation + erratum note added) |
| `HFF_Reconciliation_2/HFF_discrepancy_reconciliation.csv` R-12 | "2 E alpha theta_bar/(1-nu)" | **fixed** (in-cell erratum note) |
| `HFF_Reconciliation_2/HFF_calculation_recheck_v2.csv` CAL2-13 | "2 E alpha theta_bar d/(1-nu)", "5.8e4/2" | **fixed** (in-cell erratum note) |
| `audit/` (stage-1 archive) | not touched (traceability preserved) | — |

## 2. Richardson-number basis (ERR-02) — explanation corrected, values unchanged

The previous revision of `HFF_Ri_resolution_note.md` §2 wrote the per-length scale ΔT*(ℓ) while
asserting ℓ¹ scaling — internally inconsistent. §2–§3 now distinguish:

* **Case A** (same physical ΔT held fixed, only ℓ changes): Ri(ℓ) = gβΔT ℓ/U² **∝ ℓ**;
  H₀ → D_h doubles Ri.
* **Case B** (scale redefined per length, ΔT*(ℓ) = q″ℓ/k_f): Ri(ℓ) = (gβq″/k_f)ℓ²/U² **∝ ℓ²**;
  H₀ → D_h quadruples Ri (Gr ×16, Re² ×4).

**Consistency check against the formulation:** the document's temperature scale is the fixed
ΔT* = q″H₀/k_f = 4.17 K (used identically in Gr and Br), so its D_h-basis variant is Case A:
Gr(D_h) = 8.6, Re(D_h) = 50, Ri = 3.4×10⁻³ = 2× the adopted H₀ value — exactly what eq. 6.3,
§6.2 and the dictionary state. The adopted baseline Ri = **1.7×10⁻³** and the quoted pair
{1.7×10⁻³, 3.4×10⁻³} are therefore consistent with the actual temperature scale; they are
**unchanged**. (The Case-B variant at D_h, 6.9×10⁻³, is now noted for completeness; excludability
holds under all three.) R-02 and CAL2-05 cells annotated accordingly.

## 3. Impact assessment — no numerical consequence

The factor 2 existed only in symbolic transcription in the Stage-2 reconciliation layer; every
downstream quantity was computed from the number 2.9×10⁴ N/m, which is correct:

* μ² = N/D_s = 2.9×10⁴/9.6 = 3.02×10³ m⁻², μ = 55 m⁻¹, μL = 1.65 — unchanged;
* w_max = 2.19×10⁻⁴ m = 0.438 H₀, amplification 1.39 — unchanged;
* M_mid = −6.4 N·m, σ_bend = 4.2 MPa, |σ|_max ≈ 13.9 MPa = 0.15 σ_y — unchanged;
* M_b = 117.5/32.3 = 3.64, ceiling ordering (≈1.0×10⁴ / 1.16×10⁴ / 1.63×10⁴ W m⁻²) — unchanged;
* Ri pair {1.7×10⁻³, 3.4×10⁻³} and the buoyancy disposition — unchanged.

**All conclusions of the formulation and of the second reconciliation pass stand as written.**

## 4. Files changed in this correction

1. `HFF_beamcolumn_rederivation.md` — §1 loading bullet fixed; new §1b (constitutive derivation
   + ERR-01 note).
2. `HFF_Ri_resolution_note.md` — §2 replaced by the two-case derivation; §3 restated as
   "Convention adopted" with the Case-A/B values; historical-defect relations kept.
3. `HFF_discrepancy_reconciliation.csv` — R-12 fixed with erratum note; R-02 annotated (Case A).
4. `HFF_calculation_recheck_v2.csv` — CAL2-13 fixed with erratum note; CAL2-05 annotated.
5. `HFF_correction_log.csv` — ERR-01 and ERR-02 rows appended.
6. `REVISION_SUMMARY.md` — Revision 2a note appended.
7. `HFF_correction_report_v2a.md` — this report.

`audit/` and `HFF_Independent_Audit_2/` are intentionally untouched; the original (correct)
records there serve as the traceability anchor, and the errata are documented in this folder.

## 5. Main document status (explicit)

**The main research document required no change.** Chapter 4 (`eq:ntheta`), Table 7.1, cell A5,
§6.2, §7.3 and the dictionary were verified correct on both points. No LaTeX source was edited
in this pass and **no new PDF was compiled**; the package PDF remains the 48-page build of
commit `baea69c`.
