# Revision summary

Source: `HFF_Overleaf_Verification_Package` (internal audit-oriented dossier).
Result: `HFF_Scholarly_Research_Formulation` (research-exposition document). Date: 18 October 2026.

> **Superseded in part by Revision 2 (same date).** The second reconciliation pass
> (`HFF_Reconciliation_2/`) re-derived every dimensionless group and design quantity, adopted the
> pinned beam–column wall relation at finite membrane force, stated the hydraulic load datum, and
> corrected the Gr/Ri/Br cluster: final baseline values are Gr = 1.07, Ri = 1.7×10⁻³ (single
> length basis; 3.4×10⁻³ on the D_h basis), Br = 1.0×10⁻⁶, w_max = 2.19×10⁻⁴ m = 0.438 H₀
> (linear limit 0.315 H₀ labelled as such), p̄ = 84 Pa, w_p = 9.2×10⁻⁸ m, Γ_p = 2.4×10³,
> σ_max ≈ 13.9 MPa = 0.15 σ_y. The buoyancy question is closed at the baseline by order of
> magnitude and guarded by a regime check. Two bullets below quote the superseded intermediate
> values and are marked accordingly.

## 1. Writing and structure
- Rewrote the entire main text in formal research English: connected paragraphs, physical
  motivation, assumption-by-assumption justification with scope of validity, and natural
  transitions into and out of equations.
- Removed the sentence-level audit labels (VERIFIED / UNRESOLVED / …) from the body; a
  consolidated evidence-status table survives in Appendix B, where the labels are useful.
- Removed procedural/procedural-style phrasing (gate language in body text, instructions to a
  future implementer as declarations, and self-evaluative novelty statements). Implementation
  conditions are now stated in Chapter 9 and Appendix B in measured terms.
- Restructured per the requested 12-part layout: 11 chapters (Introduction → Limitations and
  concluding remarks) plus Appendix A (notation, arithmetic, dimensionless dictionary) and
  Appendix B (audit record: discrepancy register, evidence status, open checks, staged decisions).
- Research categories made explicit: established theory (cited), present analytical development
  (derived in situ), future computational investigation (stated prospectively only; no simulated
  results or trends).

## 2. Citations added (all verified via Crossref/publisher records on 18 Oct 2026)
- Bird, Stewart & Lightfoot, *Transport Phenomena* (Wiley, 1960) — Navier–Stokes and energy
  equations.
- Carslaw & Jaeger, *Conduction of Heat in Solids* (Clarendon, 1947) — slab conduction,
  conjugate flux continuity.
- Timoshenko & Goodier, *Theory of Elasticity*, 3rd ed. (McGraw-Hill, 1970) — plane-strain
  closure, equilibrium, flexural rigidity.
- Timoshenko & Gere, *Theory of Elastic Stability*, 2nd ed. (McGraw-Hill, 1961) — pinned Euler
  load, shear-correction estimate, pinned uniform-load deflection.
- Brezzi & Fortin, *Mixed and Hybrid Finite Element Methods* (Springer, 1991,
  DOI 10.1007/978-1-4612-3172-1) — inf–sup stability of the Taylor–Hood pair.
- Total bibliography: 17 entries (12 retained and re-verified, 5 added).

## 3. Mathematical corrections found during the re-examination
- **(New, register D-13)** Pinned–pinned strip under uniform pressure load: the deflection uses
  the pinned coefficient 5/384, not the clamped–clamped 1/384 used in the earlier package.
  Corrected: `w_p = 5 p̄ L⁴/(384 D_s)` → `w_p = 3.9×10⁻⁸ m`, `Γ_p = 4.0×10³` (was 2.0×10⁴).
  **[Superseded by Revision 2: p̄ = 84 Pa → w_p = 9.2×10⁻⁸ m, Γ_p = 2.4×10³; see D-13/D-16.]**
  The conclusion (thermal dominance of deformation) is unchanged; the formula, the baseline
  table, the dimensionless dictionary, and arithmetic cell A8 were updated consistently.
- **Membrane strain estimate corrected**: the earlier package quoted the beam-extensibility order
  `(w/d)²=2.8×10⁻³` as the membrane strain. The arc-stretching strain actually governing
  geometric linearity is `κ²L²/24 = 7.4×10⁻⁵`; Assumption A4 and the baseline table now report
  the correct quantity (register D-11 note updated).
- Sign convention locked cleanly: interface deflection `w` measured positive into the channel,
  `w = −d₂`, `κ = −w″` (previous package mixed the two in one paragraph).
- All other derivations re-checked: plane-strain relations, σ_m identity and its three sanity
  states, free thermal curvature factor (1+ν), pinned buckling coefficient π²/12, slit pressure
  drop 12 μUL/H₀² = 72 Pa, Richardson and Brinkman numbers, thermal bookkeeping — values stand as
  in the audited package (Table now carries scholarly "basis" remarks instead of status labels).

## 4. Audit material disposition
- `audit/` directory preserved verbatim (six source documents).
- Discrepancy register extended from D-12 to D-13 and moved to Appendix B.
- Consolidated evidence-status table (41 register entries, counts unchanged from the frozen CSV)
  moved to Appendix B.
- Open checks (C-1, C-2, C-3, C-6, C-7, C-9, C-12) retained verbatim with named actions.
- Staged decisions unchanged: V-A may proceed; V-B after C-1 for T1 quotations; V-C with the
  corrected unit-test expectations; **coupled production computations remain on HOLD** pending
  C-2, C-3, B-1 (buoyancy check case), C-6, and regime guards as runtime assertions; manuscript
  positioning statements remain on HOLD pending C-7.

## 5. Unresolved issues (visible, none disguised)
- Nu(T1) digit not yet extracted from the primary table (C-1).
- No V-D CHT series and no V-E compliant-channel dataset constructed yet (C-2, C-3).
- PEEK datasheet values and β_f are datasheet-representative, freeze pending (C-6).
- Gupta & Barak 2024 entry remains bibliographically incomplete (title/DOI not retrievable).
- Buoyancy question at Ri=0.43 remains open until the B-1 check case is executed.
  **[Superseded by Revision 2: the 0.43 value was defective (mixed basis, mis-transcribed
  powers); the corrected Ri = 1.7×10⁻³ closes the question by three orders of magnitude; see
  D-8/D-14 and `HFF_Reconciliation_2/HFF_Ri_resolution_note.md`.]**

## Revision 2a — narrow-scope consistency correction (same date)

Two transcription/wording defects in the Stage-2 reconciliation layer were found and fixed;
**the main document and all numerical results are unchanged, and no new PDF was compiled**
(the package PDF remains the 48-page build of commit `baea69c`):

1. **ERR-01** — the membrane-force *formula* in `HFF_beamcolumn_rederivation.md` (§1) and in two
   reconciliation CSV rows carried a spurious factor 2 (`N_θ = −2Eαθ̄/(1−ν)·d`), originating in
   the mean-stress coefficient σ_m = −2Eαθ̄/[3(1−ν)]; the re-derivation
   (beam-column note §1b) confirms the document's `N_θ = −Ed αθ̄/(1−ν)` ≈ −2.91×10⁴ N/m
   (N/N_cr = 0.276), which was the value actually used everywhere. Formula cells corrected;
   erratum notes embedded for traceability.
2. **ERR-02** — `HFF_Ri_resolution_note.md` §2 conflated the two possible meanings of a
   "length-basis" change; it now derives both (fixed physical ΔT: Ri ∝ ℓ; per-length scale
   ΔT*(ℓ) = q″ℓ/k_f: Ri ∝ ℓ²) and states that the formulation's fixed ΔT* = 4.17 K makes the
   quoted D_h-basis value 3.4×10⁻³ a Case-A quantity. Adopted Ri = 1.7×10⁻³ unchanged.
   See `HFF_Reconciliation_2/HFF_correction_report_v2a.md`.

## Revision 3 — synchronization with the beam–column consistency audit

Source audit: `HFF_Reconciliation_2/HFF_beamcolumn_model_consistency.md` (verdict: *existing
beam–column model justified with an explicit limitation*). Changes, all in the main source and
its registers — no change to the research objective, geometry, material data, operating point,
governing model, or resolved values (Ri definitions untouched):

1. **Classification corrected (ch04).** The beam–column equation is no longer described as the
   "consistent von Kármán wall equation" nor its constant-force treatment as "self-consistent".
   It is now identified as the *reduced (frozen-force) von Kármán* relation — the transverse
   member retaining the full geometric stiffness of the prescribed compressive force — with the
   consistency update `N_θ(w) = N_θ + Ed⟨w′²⟩/[2(1−ν²)]` (eq. `eq:nupdate`) stated explicitly.
2. **Quantified error written in (ch04, ch06, ch07, ch11, Appendix A9/A3).** Frozen-force
   baseline w_max = 2.19×10⁻⁴ m (0.438 H₀, adopted) overpredicts the self-consistent value
   2.14×10⁻⁴ m (0.428 H₀) by 2.3 % — one-sided (conservative); force relaxation 6.1 %
   (first iterate; the earlier "≈7 %" refined), 5.9 % self-consistent; error < 4 % inside the
   admissible envelope; buckling margin M_b = 3.64 exact (relaxation vanishes at onset); error
   grows beyond N_θ^c/N_cr ≈ 0.5 where the Chapter-8 escalation triggers. Comparison values are
   labelled as analytical, not simulation results.
3. **Ceilings re-solved exactly (ch07 (iii), D-15, cell A9).** The second-pass interpolations
   (≈1.0/1.2/1.6×10⁴ W/m²) used an inconsistent amplification scaling; exact frozen-force
   ceilings: A-3 mesh bound at N/N_cr = 0.302 (q″ ≈ 5.5×10³), A-6 stress cap at 0.327
   (≈ 5.9×10³), M_b = 2 at 0.5 (≈ 9.1×10³). Ordering unchanged.
4. **Sign convention stated (ch04).** Signed axial resultant N_θ < 0 in compression (tension
   positive) vs the positive compressive magnitude N_θ^c = |N_θ| used in μ² and all force
   ratios; compatibility acts on the signed resultant.
5. **Regression repaired (ch11, D-20).** Three limitation updates (buoyancy guard, support
   ideality, reduced wall equation) lost to a failed editing pass in Revision 2 are restored;
   limitation (4) now carries the quantified frozen-force error.
6. **Registers synchronized.** D-11 (arc strain 1.8×10⁻⁴ exact / 1.6×10⁻⁴ circular-arc), D-15
   (exact ceilings), new D-20; correction log rows ST3-01…04; reconciliation CSV rows updated
   (R-02, R-12, R-15, R-29, CAL2-05, CAL2-13, CAL2-19, CAL2-24).
7. **PDF regenerated** from the revised source (pdflatex → bibtex8 → pdflatex ×2) and swept for
   stale statements. See `HFF_Reconciliation_2/HFF_revision3_report.md`.
