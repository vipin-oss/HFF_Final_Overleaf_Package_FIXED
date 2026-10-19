# Revision 3 report — synchronization of the main document with the beam–column audit

**Scope:** main LaTeX source, its appendix cells and registers, and the reconciliation records.
**No change to:** research objective, geometry, material parameters, baseline operating point,
governing model, resolved values (Richardson definitions and values untouched), admissibility
limits. **No solver code.**

## 1. Exact changes

| # | File | Change |
|---|---|---|
| 1 | `chapters/ch04.tex` | Beam–column section reclassified: "consistent von Kármán wall equation" → *reduced (frozen-force) beam–column equation*, the transverse member retaining the full geometric stiffness of the prescribed compressive force. New equation `eq:nupdate` states the consistent-force update `N_θ(w) = N_θ + Ed⟨w′²⟩/[2(1−ν²)]` from axial compatibility (both end edges blocked, ⟨u′⟩ = 0). The frozen-force equation is identified as the first iterate of that system. "Treating N constant is self-consistent … about 7 %" replaced by the quantified statement: blocked strain e₀ = (1+ν)αθ̄ = 2.26×10⁻³; arc-stretching ½⟨w′²⟩ = 1.8×10⁻⁴ (circular-arc 1.6×10⁻⁴); first-iterate relaxation 6.1 %; self-consistent 5.9 %; frozen force overpredicts w_max by 2.3 % (0.438 → 0.428 H₀), one-sided conservative; error < 4 % in the admissible envelope; M_b = 3.64 exact; error grows beyond N/N_cr ≈ 0.5 where the Chapter-8 escalation applies. Solver-level consequence reworded (frozen force within each solve, state re-evaluated across iterations). Sign convention added after `eq:ntheta`: signed resultant N_θ < 0 in compression vs positive magnitude N_θ^c = |N_θ| in μ² and all ratios. `eq:beamcolbase` labelled "(frozen force, adopted)". |
| 2 | `chapters/ch07.tex` | Table: beam–column row labelled adopted with the self-consistent comparison (2.14×10⁻⁴ m, 0.428 H₀) in the same cell; fibre/arc row now quotes the exact arc-stretching term 1.8×10⁻⁴. Interpretation (i): adopted 0.438 flagged as the frozen-force value with comparison 0.428. Interpretation (iii): ceilings re-solved exactly — A-3 mesh bound at N/N_cr = 0.302 (q″ ≈ 5.5×10³ W/m²), A-6 stress cap at 0.327 (≈ 5.9×10³, w ≈ 0.56 H₀, M_b = 3.1), M_b = 2 at 0.5 (≈ 9.1×10³, w ≈ 1.2 H₀) — replacing the second-pass interpolations (1.0/1.2/1.6×10⁴), which used an inconsistent r-scaling; envelope error statement (< 4 %, one-sided) added; ordering unchanged. |
| 3 | `chapters/ch02.tex` | A4: "von Kármán beam–column level" → "reduced (frozen-force) von Kármán beam–column level"; arc strain 1.4×10⁻⁴ → 1.8×10⁻⁴. |
| 4 | `chapters/ch06.tex` | relbow paragraph: 0.438 flagged as frozen-force adopted value with 0.428 comparison. |
| 5 | `chapters/ch08.tex` | Thermoelastic solve item: "reduced (frozen-force) von Kármán level", with the per-iteration membrane-state re-evaluation recovering `eq:nupdate` at the fixed point. |
| 6 | `chapters/ch11.tex` | Limitation (4) rewritten with the quantified frozen-force error and escalation linkage. **Regression repair:** limitation (2) (buoyancy guard, Ri = 1.7×10⁻³) and (3) (O(d/L) pin-ideality stiffening) — intended for Revision 2 but lost to a failed editing pass — restored; the Revision-2 PDF had carried the stale "Ri = O(1) forbids closing the question" sentence. Recorded as D-20. |
| 7 | `chapters/appendix.tex` | Cells A3/A9: frozen-force labelling, exact relaxation figures (6.1 % / 5.9 %), self-consistent comparison values, blocked strain 2.26×10⁻³, exact ceiling re-solve table. |
| 8 | `chapters/audit_appendix.tex` | Register caption D-1…D-20; D-11 arc figure updated; D-15 ceiling re-solve noted; new row **D-20** (classification, ceilings, ch11 regression); new section "Stage-3 synchronization" summarizing the audit verdict. |
| 9 | Reconciliation records | `HFF_correction_log.csv` +ST3-01…04; reconciliation CSV R-12 (sign convention), R-15/CAL2-19 (arc 1.8/1.6×10⁻⁴, e₀ 2.26×10⁻³), R-29/CAL2-24 (exact ceilings), CAL2-18 (comparison value), R-02 (Stage-3 untouched note); `HFF_precoding_checklist_v2.md` (V-C3 frozen-force note + optional consistent-update check); `README.md` (new zip name); `REVISION_SUMMARY.md` (Revision 3 section). |

## 2. Consistency verification performed

* Audit's comparison values re-derived independently before insertion (audit script re-run with
  the documented inputs E = 3.6 GPa, ν = 0.40, q″ = 5×10³ W/m², θ̄ = 32.3 K): μL = 1.647 → 1.598,
  relaxation 6.1 %/5.9 %, w_max 0.438 → 0.428 H₀, σ_bend 4.24 → 3.90 MPa, M_b exact; ceilings
  solved by bisection on the frozen-force relation (0.302 / 0.327 / 0.5). All LaTeX numbers
  trace to these computations.
* Sign audit: `eq:ntheta` (signed, negative), Table 7.1 N_θ row (signed value), N_cr > 0,
  `eq:beamcol`/`eq:beamcolsol`/`eq:tcr` use the positive magnitude N_θ^c; `eq:nupdate` acts on
  the signed resultant with a positive correction (compression relief) — one consistent scheme.

## 3. Compilation status

**The PDF was regenerated** from the revised source: pdflatex → bibtex8 → pdflatex ×2, zero
errors, zero unresolved references/citations. A full-text sweep of the new PDF confirmed: no
"consistent von Kármán wall equation"/"self-consistent" freeze wording; no 1.0/1.2/1.6×10⁴
ceiling figures; no "Ri = O(1) forbids"; adopted 0.438 always labelled frozen-force with 0.428
present as the comparison; 6.1 %/5.9 % relaxation figures present; zero `??`. Package delivered
as `HFF_Research_Formulation_Revision_3.zip` (Overleaf-ready source + regenerated PDF +
references.bib + figures + full audit trail).
