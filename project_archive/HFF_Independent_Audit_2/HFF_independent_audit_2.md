# Independent Scientific Audit of the HFF Scholarly Research Formulation

**Auditor:** independent senior researcher (mathematical modelling, conjugate heat transfer, fluid mechanics, thermoelasticity, computational mechanics, numerical methods)
**Date:** 18 October 2026
**Object audited:** repository `Paper_12` — the package *HFF_Scholarly_Research_Formulation* (`main.tex`, `chapters/ch01–ch11`, `chapters/appendix.tex`, `chapters/audit_appendix.tex`, `figures/`, `references.bib`, `main.pdf`, `README.md`, `REVISION_SUMMARY.md`) plus the six audit-archive documents in `audit/`.
**Scope:** audit only. The original package has not been modified. No replacement LaTeX, no solver code, no fabricated results.

**Evidence classes:** **[DOC]** = statement taken from the supplied package · **[IND]** = independently derived or recomputed in this audit (all arithmetic reproduced in `HFF_calculation_recheck.csv`) · **[LIT]** = verified against an external source this session (cited inline) · **[UNRESOLVED]** = evidence missing; exactly what is needed is stated.

**Bottom line.** The formulation's architecture — field equations, plane-strain reduction, interface conditions, weak-form coupling, verification hierarchy — is sound and, in most respects, unusually well disciplined. This audit independently reproduced every derivation and every baseline number. Three outright numerical defects were found (Gr, Ri, Br — each wrong by a factor of exactly 10³, in the direction that weakens the document's own argument), one substantive model-form/design conflict was found (the linear kinematics used by the model cannot represent the membrane-force/deflection interaction that the document's own buckling ceiling presupposes; at the baseline load the consistent beam–column deflection exceeds the document's own admissibility bound), and one boundary-load bookkeeping gap (strip pressure datum) was found. One bibliographic record declared unresolvable by the package (Gupta & Barak 2024) was positively identified and can be completed. One open benchmark digit (Nu_T1 = 4.861) was independently corroborated and the open item C-1 can be closed. All 16 journal/chapter citations with DOIs were verified at source level this session; no fabricated reference was found.

Decisions (details in `HFF_final_audit_decision.md`): mathematical model — **CONDITIONAL GO** (two qualifications) · baseline calculations — **reproducible after three corrections** · bibliography — **supports the principal claims** · numerical method — **CONDITIONAL GO** · research direction — **RETAIN** · isolated solver verification (V-A, V-B, V-C) — **GO** · fully coupled implementation — **HOLD** (seven conditions).

---

## 1. Package inventory

### 1.1 Files present

| Path | Role | Status |
|---|---|---|
| `main.tex` | Entry document (report class, 11 pt, A4, pdfLaTeX) | present, consistent with chapters |
| `chapters/ch01.tex … ch11.tex` | Research exposition (11 chapters) | present, complete |
| `chapters/appendix.tex` | Appendix A: notation, arithmetic cells A1–A8, dimensionless dictionary | present |
| `chapters/audit_appendix.tex` | Appendix B: discrepancy register D-1–D-13, evidence counts, open checks C-1…C-12, staged decisions | present |
| `figures/fig_geometry.tex`, `figures/fig_signs.tex` | TikZ figure bodies (no external graphics) | present; one labelling defect in fig_signs (§2.10) |
| `references.bib` | 17 entries | present; one entry intentionally incomplete (§4.2) |
| `main.pdf` | Compiled document, 41 pages | present, **in sync with sources** (spot-checked: Γ_p = 4.0×10³, w_p = 3.9×10⁻⁸ m, coefficient 5/384, Nu_H1 = 5.385, Nu_T1 ≈ 4.861, Ri = 0.43, Gr = 1.1×10³ all match the current `.tex`; the D-13 correction is therefore in the shipped PDF) |
| `README.md`, `REVISION_SUMMARY.md` | Package map, revision log vs. previous package | present, accurate against the sources I checked |
| `audit/HFF_research_discovery_report.md` | Original discovery report (portfolio + candidate problems) | present |
| `audit/HFF_research_audit_and_redesign.md` | First redesign audit (corrections A1–A14) | present |
| `audit/HFF_final_formulation.md` | "Frozen model" prior to coding (superseded by the LaTeX) | present |
| `audit/HFF_independent_audit.md` | The previous independent audit (E1–E15, P-series, C-1…C-12) | present |
| `audit/HFF_claim_evidence_register.csv` | 41-entry claim–evidence register | present; counts match Appendix B |
| `audit/HFF_pre_coding_checklist.md` | Ordered gates 0–3 | present |

**Missing files:** none. Every file the audit brief names as part of the package is present. The zip itself is not in the repository, but the repository is its extracted content (README references the zip only as an upload instruction).

### 1.2 Version layering and conflicting formulations

The package contains four document generations: discovery report → redesign audit → "final formulation" (frozen model) → the current scholarly LaTeX. The `REVISION_SUMMARY.md` and Appendix B document the intended deltas accurately (end-fixity change, H1/T1 benchmark reassignment, pinned buckling coefficient, 5/384 coefficient, arc-strain correction). The superseded documents are retained verbatim for traceability, which is good practice, but they retain **internal defects that are not annotated in place**, and two of those defects propagated forward:

1. `audit/HFF_independent_audit.md` E13 prints the pressure-drop scale as "Δp-channel = 12μUL/H³" and "Δp ∝ U·H⁻³" — the dimensionally wrong form that register D-5 of the current document itself corrects (the current document is right: Δp = 12μUL/H₀² [IND]). The earlier audit's *numbers* are consistent with H₀²; only its printed formula is wrong. No forward contamination.
2. `audit/HFF_independent_audit.md` P6 states "Gr ~ 1.1e3, Ri recomputed 0.4–1.7" and E3 states "Br ≈ 9.9×10⁻⁴ recomputed". **Both are wrong by a factor of 10³ [IND — §3.3, §3.4 below], and both wrong values were carried unchanged into the current formulation** (Table 7.1 and the dimensionless dictionary). The current document did not re-derive these two numbers; it inherited them from the previous audit. This is the clearest demonstration of the brief's warning not to assume the earlier audit is correct.

**Inventory finding I-1 (non-blocking, must be recorded):** the audit chain is not self-correcting for arithmetic; two 10³-scale errors propagated from the previous audit into the current formulation.

### 1.3 Source-vs-PDF consistency

The compiled PDF matches the sources on every item spot-checked, including all items corrected by D-13. No stale-PDF divergence exists. The PDF's errors are exactly the sources' errors (Gr, Br, and the items in §3).

---

## 2. Independent mathematical audit

For each item: the document's statement **[DOC]**, my independent derivation **[IND]**, and a finding from {Correct, Correct under stated assumptions, Incorrect, Insufficiently justified, Unresolved}. Equation numbers refer to the LaTeX (chapter.equation order as compiled).

### 2.1 Fluid equations (E-01–E-03)

**(3.1) ∇·u = 0; (3.2) ρ(u·∇)u = −∇p + μ∇²u; (3.3) ρc_p(u·∇)T_f = k_f∇²T_f on Ω_f.**
These are the standard steady incompressible Navier–Stokes and advection–diffusion equations for constant properties [DOC]. Independent dimensional check: ρU²/H₀ = Pa/m ✓; μU/H₀² = Pa/m ✓; ρc_pUΔT/H₀ = W/m³ ✓ [IND]. Assumptions (steady, constant ρ, μ, c_p, k_f; laminar; no body force) are stated and justified (A2, A6, A7).
**Finding: Correct.** Conditions: (i) the buoyancy disposition built on (3.2) rests on a wrong Ri value — see §3.3; after correction, buoyancy is negligible by the document's own order-of-magnitude logic, which *strengthens* the model; (ii) omission of viscous dissipation is bounded by Br — whose correct value is 10⁻⁶, not 10⁻³ (§3.4) — so the re-inclusion rule (Br ≥ 10⁻²) is even safer than documented.

### 2.2 Solid conduction and coupling term (E-04)

**(3.4) ∇·(k_s∇T_s) = 0 in Ω_s⁰.** [DOC] argues the thermoelastic deformation-heating source −βT₀ tr(ε̇) vanishes identically at steady state, with the transient omission controlled by ξ. I verified: the source is proportional to ε̇ ≡ 0 at steady state [IND]; ξ = β²T₀/[(λ+2μ_L)ρ_sc_s] with β = 9.0×10⁵ Pa/K, λ+2μ_L = 7.71×10⁹ Pa, T₀ = 293 K gives ξ = 2.15×10⁻² ✓ matches the document's 2.2×10⁻² (cell A6) [IND]. Time scales t_wave = 1.8×10⁻⁶ s, t_f = 1.74 s, t_s = 51.5 s, t_adv = 0.6 s all reproduce ✓ (the ordering statements built on them are valid).
**Finding: Correct.**

### 2.3 Thermoelastic constitutive law and plane-strain closure (E-05–E-06)

**(3.5)** ε = sym∇d; σ = 2μ_L ε + λ(tr ε)I − βθI, β = 3Kα = Eα/(1−2ν). Standard Duhamel–Neumann law; identities λ = Eν/[(1+ν)(1−2ν)], μ_L = E/2(1+ν), K = E/3(1−2ν) verified [IND]. **Correct.**

**(3.6)** σ_zz = ν(σ_xx+σ_yy) − Eαθ from ε_zz = 0. Re-derived from compliance form with free thermal strain: ε_zz = [σ_zz − ν(σ_xx+σ_yy)]/E + αθ = 0 ⟹ σ_zz = ν(σ_xx+σ_yy) − Eαθ ✓. Equivalence with the stiffness form σ_zz = λ tr ε − βθ verified by substituting λ, β and the in-plane trace σ_xx+σ_yy = 2(λ+μ_L)e − 2βθ [IND]. **Correct.**

### 2.4 Mean-stress identity (E-07)

**(3.8)** σ_m = (1+ν)(σ_xx+σ_yy)/3 − Eαθ/3 = K(tr ε − 3αθ). Re-derived: trace of (3.5) plus (3.6); the algebraic steps 2(1+ν)(λ+μ_L) = 3K and 2β(1+ν) + Eα = 3β both check [IND]. The three reference states were re-derived independently:
- (a) fully constrained: σ = −βθ I, σ_m = −βθ = −3Kαθ ✓ (4.4);
- (b) axially restrained, traction-free faces: σ_xx = σ_zz = −Eαθ/(1−ν), ε_yy = (1+ν)αθ/(1−ν), σ_m = −2Eαθ/3(1−ν) ✓ (4.5) — and the two σ_m values are correctly **not** conflated (register D-12 resolved);
- (c) free plane-strain strip: σ_xx = σ_yy = 0 ⟹ σ_zz = −Eαθ, σ_m = −Eαθ/3 ≠ 0 ✓ (4.6); the strain-form consistency K[2(1+ν)−3]αθ = −Eαθ/3 also checks [IND].
**Finding: Correct.** This block (including D-2's correction of the naive "σ_m = 0" expectation) is right and is a genuinely useful set of unit-test anchors.

### 2.5 Wide-beam law and free thermal curvature (E-08–E-09)

**(4.1)** σ_xx = E/(1−ν²)[ε_xx − (1+ν)αθ]. Derived by eliminating ε_yy through σ_yy = 0 on the traction-free faces; numerator and denominator verified with λ+2μ_L = E(1−ν)/[(1+ν)(1−2ν)] [IND]. **Correct under stated assumptions** (plane strain, traction-free faces, uncoupled conduction).

**(4.7)** κ_th = (1+ν)αΔT_t/d = (1+ν)αq″/k_s. Re-derived from zero axial force and zero moment resultants with θ(y) = θ̄ + Γy: ε₀ = (1+ν)αθ̄ and κ_th = (1+ν)αΓ = (1+ν)αΔT_t/d ✓; the second form follows from ΔT_t = q″d/k_s ✓ [IND]. The document's warnings (factor 1+ν for free bending, not 1; not (1+ν)/(1−ν), which belongs to biaxially constrained curvature) are correct. The d-independence of κ_th is exact and is the document's central design insight — verified. The clamped-strip no-bow statement (uniform κ_th fully reacted, w ≡ 0, M₀ = D_sκ_th) is correct [IND].
**Finding: Correct.**

### 2.6 Pinned–pinned bowing, membrane force, buckling (E-10–E-12)

**(4.8)** w = κ_th x(L−x)/2, w_max = κ_thL²/8, from w″ = −κ_th with w(0) = w(L) = 0. Verified within linear Euler–Bernoulli/plate-strip theory, with **zero total moment** at the pins (the physical moment is D_s(w″+κ_th) = 0 at the ends; the shear is zero because the total moment is constant-zero) — the document's own supporting prose is internally consistent [IND]. **Correct under stated assumptions** — with one model-form caveat that becomes substantive at the baseline load: see §2.12 (F-3).

**(4.12)** N_θ = −Edαθ̄/(1−ν). Verified by integrating (4.1) over the thickness with mean axial strain blocked [IND]. **Correct.**

**(4.13)–(4.14)** N_cr = π²D_s/L² and T̄_cr = π²d²/[12α(1+ν)L²]. Verified algebra: equating |N_θ(T̄_cr)| = π²D_s/L² reproduces (4.14) exactly [IND]; the pinned coefficient is the one consistent with the adopted supports (clamped would give 4×) and the register D-4 correction is right. Value: T̄_cr = 117.5 K at d = 3 mm ✓ (document: 117 K); catalogue A4 {13, 29, 52, 82, 117} K reproduces exactly [IND]. Two conditions should be stated in the document:
- π²D_s/L² with the *wide-plate* rigidity is correct **because plane strain suppresses out-of-plane (antielastic) curvature**; a strip free to anticlastically bend (plane stress) would buckle at (1−ν²)π²E d³/12L² — i.e. ~16 % lower at ν = 0.4. The plane-strain justification (full out-of-plane restraint by the casing, A1) should be made explicit in one sentence, since the ceiling number M_b depends on it.
- "Pinned" in A9/B7 is implemented as zero displacement on the entire end edge. For a strip with L/d = 10 this differs from ideal point pins by a Saint-Venant end layer of width O(d) and a global stiffening of order d/L; the V-C3 benchmark at L/d = 25 keeps this below the 1 % tolerance, but the coupled geometry (L/d = 10) carries a few-percent effect that should be checked once, numerically, by comparing full-edge pins against bottom-corner pins. **Correct under stated assumptions** (conditions as above).

### 2.7 Hydraulics (E-13–E-14)

**(4.15)** Δp = 12μUL/H₀². Verified: dp/dx = μu″ with u = 6U(y/H₀)(1−y/H₀) gives −12μU/H₀² [IND]; Δp = 72 Pa at baseline ✓; cross-checks f_D(L/D_h)ρU²/2 = 72 Pa ✓ and ΔpH₀ = 2τ_wL with τ_w = 6μU/H₀ = 0.6 Pa ✓ (cell A1) [IND]. The D-5 correction (H₀², not H₀³) is right; the Darcy convention f_D Re_Dh = 96 (Fanning 24) is the correct slit value [LIT: standard; e.g. Shah & London correlations] and the basis-printing rule (D-6) is good practice. **Correct.**

**(4.16)** w_p = 5p̄L⁴/384D_s for a pinned–pinned strip under uniform transverse load. The 5/384 coefficient is the correct simply-supported value (1/384 is clamped–clamped); register D-13 is a genuine correction, verified [IND; standard beam tables]. **However, the load level p̄ ≈ Δp/2 = 36 Pa is under-specified [Insufficiently justified]:**
with the datum of B2 (p = 0 at the outlet), the gauge pressure **on the strip** runs from p(0) = 120 Pa to p(L) = 48 Pa (gradient 12μU/H₀² = 2.4 kPa/m over the strip plus the exit length), mean p̄ = 84 Pa, not 36 Pa [IND]. For an incompressible fluid the pressure *level* on the wall is set by the outlet datum relative to the casing environment; the document must state which environment pressure the strip's outer face sees (vented casing ≈ outlet datum is the natural baseline). With p̄ = 84 Pa: w_p = 9.2×10⁻⁸ m and Γ_p = 1.7×10³ — the conclusion (Γ_p ≫ 5, thermal dominance) is **unchanged**, but the printed number chain (36 Pa → 3.9×10⁻⁸ m → 4.0×10³) is not consistent with the document's own datum convention. Also note the load on the strip is *linearly varying* (48→120 Pa), not uniform; the uniform-load formula is an estimate, adequate given Γ_p ≫ 5, and should be labelled as such.

### 2.8 Interface conditions and weak coupling (E-15–E-18)

**(5.1)–(5.4)**: steady no-slip at the deformed point; σ_s·n = (−pI + 2μD)·n with a single normal n (fluid→solid); T_f = T_s; −k_f∇T_f·n = −k_s∇T_s·n. Verified semantics: with n the outward normal of the fluid domain, σ_f·n is the force on the fluid from the solid, so the equality σ_s·n = σ_f·n is exactly action–reaction consistency; the flux equality is the standard perfect-contact condition [IND]. **Correct.**

**Weak forms (8.1)–(8.4) and the monolithic cancellation.** I verified the cancellation sign-by-sign: the fluid residual contains the interface term −∫_Γ σ_f n·v ds (integration by parts, n outward of Ω_f) and the solid residual contains +∫_Γ σ_s n·φ ds (solid outward normal = −n); under (5.2) with v = φ on the conforming interface the pair cancels exactly. For energy: fluid term −∫_Γ k_f∇T_f·n χ and solid term +∫_Γ k_s∇T_s·n χ cancel under (5.4) [IND]. The document's prose ("equal with opposite signs") is loose — the *RHS expressions* are equal under the interface conditions, and they enter the assembled residual with opposite signs — but the net claim (no modelled interface quantity in a monolithic assembly) is **correct** and is properly conditioned on the single-normal convention. Conditions to record: (i) the outflow boundary term of (8.1) (do-nothing traction) must appear in the discrete residual — only the interface terms are shown; (ii) traction/flux transfer across the curved isoparametric P2 interface must use consistent quadrature on both sides (the superseded `final_formulation` carried this as risk R7; it was dropped in the rewrite and should be restored). **Correct; two presentation/spec conditions.**

### 2.9 Superposition, deformed domain, mesh motion (E-19–E-20)

**(5.14)** d = d_th + d_p. Exact for the *linear solid problem at fixed configuration and fixed loads* [IND] — as stated, correct. As a mechanism-attribution tool across the coupled iterations it is first-order (the fluid state and the traction distribution depend on d); the document should say so in one clause. Related and more important: the **posed linear model cannot represent the interaction between the compressive membrane force N_θ and the transverse deflection** — yet the document's own buckling ceiling M_b is built on exactly that interaction. See §2.12.

**Deformed fluid domain (§3.9) and pseudo-elastic extension (§8.3).** Correct: the steady problem needs no mesh velocity and no GCL; the discrete GCL binds only a transient ALE extension [IND; consistent with the Lesoinne–Farhat theory, verified LIT]. The steady/transient distinction, repeatedly and correctly drawn, is one of the document's strengths. **Correct.**

### 2.10 Figures and notation (E-21–E-22)

- **Figure 2 (fig_signs) traction labels are swapped relative to the stated convention [Incorrect, non-blocking]:** with n (fluid→solid) drawn upward, the force **on the solid** from the fluid is −σ_f·n (points *into the solid*, up); σ_f·n is the force on the fluid (down). The figure labels the up-arrow "σn: traction of fluid at wall" and the down-arrow "−σn: force ON solid (Newton 3)" — both labels are the reverse of the convention the document otherwise enforces. Given that sign discipline is a stated selling point of the formulation, this must be corrected before any manuscript use.
- **Notation collision [Incorrect, editorial]:** K is defined as the bulk modulus (§2.5) *and* as the conductivity ratio k_s/k_f (Ch. 6, dictionary). μ vs μ_L and β vs β_f are disambiguated by subscripts; K is not. Rename one of the two (e.g. K_s for the conductivity ratio).

### 2.11 Boundary conditions (E-23)

B1–B9 audited: inlet parabola on a rigid section (mass-flow fixed) ✓; outflow "traction-free with datum p = 0" is the standard do-nothing natural condition, with the correctly required exit-length/no-backflow sensitivity (C-9) ✓; adiabatic rigid surfaces ✓; pinned adiabatic strip ends ✓; flux on the outer face ✓; regime-D variant with matched-input rule ✓. The enthalpy-balance check (V-F i) is exactly consistent with these BCs (with zero-flux ends, all of Q′ = q″L enters the fluid) ✓. **Correct under stated assumptions**, plus the datum statement required by §2.7.

### 2.12 The membrane-force/deflection model-form gap (F-3) — the substantive physics finding

The posed solid model is *linear* elasticity on the reference strip: its solution for the baseline is the parabolic bowing (plus an O(10⁻⁴) traction correction), w_max = 1.58×10⁻⁴ m = 0.315 H₀, fibre strain 2.1×10⁻³. Simultaneously, the same document derives that the pinned, axially blocked strip carries N_θ = −2.9×10⁴ N/m, i.e. **N/N_cr = 0.275 at the baseline** — and uses that force to define the buckling ceiling. These two positions are mutually inconsistent at the level of precision the document itself enforces:

- A strip bearing 27.5 % of its Euler load does **not** deflect according to the linear solution. The consistent small-strain/moderate-rotation theory (von Kármán beam–column; the slopes here are O(0.02 rad), so von Kármán hypotheses hold comfortably) gives, for uniform eigen-curvature with pinned immovable ends and sub-critical compression N, the exact solution
  w(x) = (κ_th/μ²)[(1−cos μL)/sin μL · sin μx + cos μx − 1], μ² = N/D_s,
  which recovers the parabola as μL → 0 and diverges at μL = π [IND]. At the baseline (μL = 1.646):
  **w_max = 2.19×10⁻⁴ m = 1.39 × the linear value ⟹ w/H₀ = 0.438, which exceeds the document's own mesh/kinematics bound A-3 (|w|/H₀ ≤ 0.35).**
- The same interaction *reduces* the mid-span bending moment: M = D_s(w″+κ_th) = −6.36 N·m/m, i.e. σ_bend = 4.2 MPa (not 9.0), so the combined stress magnitude is ≈ 13.9 MPa, σ/σ_y ≈ 0.15 — the document's stress figures (≈ 19 MPa, 0.21) are conservative, and A-6 passes with more room once this is accounted.
- Consequences for the formulation: (i) the linear model **under-predicts** the headline quantity (deflection) by ~28 % at the baseline; (ii) the baseline operating point, honestly evaluated in the theory the buckling ceiling itself implies, **violates A-3**; (iii) superposition (5.14) remains a linear-theory identity and cannot capture the amplification.

Resolution options (all preserve the research problem; see `HFF_correction_plan.md`):
1. **Adopt von Kármán kinematics for the strip** (still small-strain: fibre strain 3.1×10⁻³, slopes 0.04 rad). One geometric-stiffness term (N_θ w′·∇φ) added to the solid weak form; the buckling ceiling then becomes a *property of the model* rather than an external estimate, and the baseline stays at the designed deformation magnitude. This is my recommendation: it is the minimal consistent upgrade and it strengthens the paper (the coupling between membrane state and passage geometry becomes computable).
2. **Detune the operating point** to N/N_cr ≲ 0.1 where the linear model is self-consistent: at d = 3 mm this needs q″ ≈ 1.5–2 kW/m², giving w/H₀ ≈ 0.10–0.14 — which risks the "dead feedback" regime the redesign explicitly tried to avoid (their risk R4).
3. **Keep the linear model and state the model-form error**: quote the beam–column amplification factor 1/(1−N/N_cr) ≈ 1.38 (first-order) as a documented correction on w_max and re-set the A-3 bound accordingly. Weakest option, but publishable if the bound logic is made honest (the current 0.315-vs-0.35 comparison has only 11 % margin and silently ignores the interaction its own buckling analysis predicts).

**Finding: the linear-kinematics claim (A4) as applied to the baseline operating point is Insufficiently justified / internally inconsistent with the document's own buckling analysis.** This is the single most important technical correction; it does not block V-A/V-B/V-C (which are linear-solver verifications), but it blocks the coupled design point.

### 2.13 Buoyancy disposition (F-1)

[DOC] computes Gr = 1.1×10³, Ri = 0.43, declares Ri = O(1) so that buoyancy "cannot be excluded by order-of-magnitude arguments alone", and builds an elaborate mitigation (upper-wall heating ⟹ stable stratification, citing Draskic et al. 2025 [LIT — verified: JFM 1012, A17 (2025), doi:10.1017/jfm.2025.10162; that paper does report that top-heating/stable stratification suppresses vertical motion and deteriorates heat transfer, so the citation is used accurately]) plus a mandatory Boussinesq check case B-1.

**Independent recomputation:** Gr = gβ_fΔT*T₀H₀³/ν_kin² = (9.81)(2.1×10⁻⁴)(4.17)(1.25×10⁻¹⁰)/10⁻¹² = **1.07** — exactly the value of the substitution string printed in Table 7.1, which the table then mis-transcribes as 1.1×10³ [IND]. Ri = Gr/Re²_Dh = 1.07/2500 = **4.3×10⁻⁴**, not 0.43 (the table's "1073/2500 = 0.43" is arithmetically false twice over: Gr is 1.073, and 1073/2500 = 0.43 happens to be true for the *wrong* numerator). The same 10³ slip appears in the dimensionless dictionary and in Appendix B (D-8).

**Finding: Incorrect (Gr, Ri as evaluated).** Consequences: (i) with Ri ≈ 4×10⁻⁴ ≪ 1, buoyancy **is** excludable by the very order-of-magnitude argument the document said was unavailable — the stable-stratification argument and the B-1 check case become unnecessary (retaining a dormant Boussinesq option is still good practice and costs one weak-form term); (ii) register D-8 closes as "resolved by corrected arithmetic"; (iii) the limitation paragraph "Ri = O(1) forbids closing the question by estimate" must be rewritten; (iv) the Draskic citation becomes tangential for the baseline (it may remain as context for the high-Ri extension). **The correction strengthens the formulation.**

### 2.14 Brinkman number (F-2)

[DOC] Table 7.1: "Br = μU²/(k_fΔT*) = (10⁻³)(2.5×10⁻³)/2.5 = 1.0×10⁻³". The printed substitution evaluates to **1.0×10⁻⁶** (μU² = 10⁻³·2.5×10⁻³ = 2.5×10⁻⁶ W/m; k_fΔT* = 2.5 W/m) [IND]. **Finding: Incorrect (value); formula and units correct; conclusion direction unchanged and in fact stronger** (dissipation even more negligible than claimed; the A-7 re-inclusion rule stands).

### 2.15 Nondimensionalization, groups, admissibility (E-24–E-26)

- Re_Dh = 50, Pr = 6.97, Pe = 348, K = 0.42, D = 6, Λ = 60, ΔT_t/ΔT* = D/K = 14.4, Σ_κ = 5×10⁻⁴, w_max/H₀ = (1+ν)Σ_κΛ²/8 = 0.315, Γ_p formula, M_b: all reproduce [IND]. The Reynolds-basis discipline (Re_H vs Re_Dh = 2Re_H, Darcy vs Fanning printed everywhere) is correct and verified [LIT].
- **(6.5)** w_max/H₀ = (1+ν)Σ_κΛ²/8 — verified [IND]; this is a correct and genuinely useful collapse of the mechanism into one number.
- Admissibility bounds A-1…A-6: A-1, A-2, A-4, A-5 verified as stated. **A-3 is in conflict with §2.12** (0.315 has 11 % margin in the linear theory; 0.438 violates it in the consistent theory). **A-6 is defective as written [Insufficiently justified]:** "computed wall stress within 20% of the PEEK yield stress" reads as σ ≈ σ_y ± 20 % (which would be an *upper* bound at 1.2σ_y — surely not intended); the table applies it as σ/σ_y ≈ 0.21 "met", i.e. as a cap of ~0.2σ_y. Restate as an explicit design cap (e.g. σ_max ≤ σ_y/SF with a stated SF, or ≤ 0.2σ_y as a conservative cap) — and note that under the corrected stress state (§2.12) the baseline sits at ≈ 0.15σ_y.

### 2.16 Baseline wall-temperature estimate (E-27)

θ̄ = ΔT_t/2 + q″/h + ΔT_b/2 = 30 + 1.55 + 0.72 ≈ 32.3 K ✓ (document: ≈ 32 K, honestly labelled an estimate with register D-7) [IND]. One refinement worth a clause: q″/h uses the *fully developed, rigid-wall* H1 coefficient (h = 3231 W/m²K); the developing region over the first ~40 % of the strip has a higher local h, so the true interface excess is somewhat smaller — the estimate is conservative for N_θ and M_b. **Correct as an estimate.**

---

## 3. Baseline calculation recheck (summary)

Every number in Table 7.1, the dimensionless dictionary, and arithmetic cells A1–A8 was recomputed from the documented inputs (full table in `HFF_calculation_recheck.csv`). Outcome:

**Reproduced exactly (to rounding):** Re_Dh = 50; Pr = 6.97; Pe = 348; f_D = 1.92; Δp = 72 Pa (with both independent cross-checks); ΔT* = 4.17 K; ΔT_t = 60 K; κ_th = 1.4 m⁻¹; w_max = 1.58×10⁻⁴ m; w_max/H₀ = 0.315; fibre strain 2.1×10⁻³; arc strain 7.4×10⁻⁵ (the D-11 correction to κ²L²/24 is itself verified: Δs/L = ½·mean(w′²) = κ²L²/24 [IND]); θ̄ ≈ 32.3 K; N_θ = −2.9×10⁴ N/m; D_s = 9.64 N·m; N_cr = 1.06×10⁵ N/m; T̄_cr = 117.5 K; catalogue {13,29,52,82,117} K; M_b = 3.64; q″ ceiling at M_b = 2 ≈ 9.0 kW/m²; ΔT_b = 1.44 K; h_rigid = 3231 W/m²K; q″/h = 1.55 K; t_wave = 1.8×10⁻⁶ s; t_s = 51.5 s; t_f = 1.74 s; ξ = 2.15×10⁻²; L_h = 2.5 mm; L_T = 17.4 mm; steel contrast κ_th = 5.3×10⁻³ m⁻¹, w/H₀ = 1.2×10⁻³; σ_bend and σ_memb expressions.

**Not reproduced — incorrect as printed:**

| Item | Documented | Independent | Discrepancy |
|---|---|---|---|
| Gr | 1.1×10³ | **1.07** | printed substitution evaluates to 1.07; result mis-transcribed by 10³ |
| Ri | 0.43 | **4.3×10⁻⁴** | follows from Gr |
| Br | 1.0×10⁻³ | **1.0×10⁻⁶** | numerator μU² = 2.5×10⁻⁶, not 2.5×10⁻³ |

**Reproduced but physically under-specified:**

| Item | Documented | Datum-consistent value | Comment |
|---|---|---|---|
| p̄ on strip | Δp/2 = 36 Pa | **84 Pa** (48–120 Pa span) | B2 datum p = 0 at outlet ⟹ gauge load on strip is fixed by it; casing environment must be stated |
| w_p | 3.9×10⁻⁸ m | 9.2×10⁻⁸ m | Γ_p: 4.0×10³ → **1.7×10³**; conclusion unchanged |
| w_max (model form) | 1.58×10⁻⁴ m (0.315 H₀) | **2.19×10⁻⁴ m (0.438 H₀)** in consistent von Kármán theory; σ_bend 4.2 MPa, not 9.0 | N/N_cr = 0.275 ⟹ 39 % amplification; violates A-3; stresses drop (§2.12) |

---

## 4. Literature and reference audit

### 4.1 Entry-by-entry verification (details in `HFF_reference_audit.csv`)

All 17 entries were checked this session against publisher/library records:

- **Journal articles and chapters with DOIs — all verified exactly as cited:** soti2015 (IJHMT 84, 1070–1081, doi:10.1016/j.ijheatmasstransfer.2015.01.048) [LIT]; christov2018 (JFM 841, 267–286, doi:10.1017/jfm.2018.30) [LIT]; lesoinne1996 (CMAME 134, 71–90, doi:10.1016/0045-7825(96)01028-6) [LIT]; alsabery2019 (HFF 29(10), 3756–3780, doi:10.1108/HFF-10-2018-0593) [LIT]; saleh2025 (HFF 35(4), 1484–1511, doi:10.1108/HFF-01-2025-0045) [LIT]; kumar2026 (Phys. Fluids 38(9), 092128, doi:10.1063/5.0349114) [LIT]; turek2006 (LNCSE 53, pp. 371–385, doi:10.1007/3-540-34596-5_15) [LIT]; draskic2025 (JFM 1012, A17, doi:10.1017/jfm.2025.10162) [LIT].
- **Books — verified as standard editions:** bird1960 ✓; carslaw1947 (**first edition 1947 confirmed** — Nature and Math. Gazette reviews of 1947 and library records; the occasional "1946" in secondary sources is wrong) [LIT]; boley1960 ✓; timoshenko1970 (3rd ed., 1970) ✓; timoshenko1961 (2nd ed., 1961) ✓; shah1978 ✓.
- **brezzi1991** — Springer Series in Computational Mathematics vol. 15 (1991); the DOI given (10.1007/978-1-4612-3172-1) is the standard Springer eBook DOI for this title; consistent, not independently fetched this session (flagged as such).
- **hood1974** — the standard origin citation of the Taylor–Hood element; the entry itself declares its page range unverified. Acceptable; complete at next revision.
- **Attribution accuracy:** every claim attached to a source in the text is one the source plausibly/actually supports — Navier–Stokes/energy (Bird), slab conduction and flux continuity (Carslaw–Jaeger), Duhamel–Neumann and coupled term and curvature (Boley–Weiner), plane-strain closure and flexural rigidity (Timoshenko–Goodier), Euler load and 5/384 (Timoshenko–Gere), fRe = 96 and Nu values (Shah–London, corroborated below), GCL (Lesoinne–Farhat), Q–Δp relation (Christov), stable-stratification heat-transfer deterioration (Draskic). The two FSI/cavity characterisations (Alsabery, Saleh: traction/buoyancy-driven flexible-wall cavity FSI) match the abstracts. One detail is unverified: ch01's "computed at high Péclet number" for kumar2026 — plausible but not confirmed from the retrieved abstract; verify against the full text or drop the clause.
- **No fabricated entries, DOIs, or benchmark values were found.**

### 4.2 The "unresolvable" entry is resolvable

`gupta2024photothermo` is stored as an incomplete `@misc`. It is identifiable with certainty [LIT]: **Vipin Gupta and M. S. Barak, "Photo-thermo-piezo-elastic waves in semiconductor medium subject to distinct two temperature models with higher order memory dependencies", International Journal of Numerical Methods for Heat & Fluid Flow 34(1), 84–108 (2024), DOI 10.1108/HFF-07-2023-0380.** The indexing facts already in the package (authors, journal, volume, issue, pages, year) all match. The entry should be upgraded to a full `@article` at the next revision. (It is currently cited only in the limitations chapter as an example of an incomplete record.)

### 4.3 The open benchmark digit C-1 can be closed

The package's C-1 withholds Nu_T1 = 4.861 pending primary-table extraction. Independent corroboration obtained this session [LIT]: a Purdue reproduction of the Shah–London parallel-plate constants lists **Nu_FD = 5.385 (H1, one wall flux/one adiabatic) and 4.861 (T1, one wall T/one adiabatic)** explicitly; standard heat-transfer tables (Incropera-family) give 5.39/4.86 for the same family and 8.23/7.54 for the two-sided H2/T cases; and an independent ASME source confirms Nu_T = 7.541 for isothermal plates. All four values quoted in V-B are therefore corroborated by multiple independent reproductions of the Shah–London data. I recommend closing C-1 on this basis (recording the corroboration chain) while still noting the primary table in the manuscript's bibliography practice.

### 4.4 Novelty / positioning review (Task 8)

What is established (all verified this session): (i) thermo-FSI in cavities with flexible walls, deformation driven by buoyant flow loading — Alsabery 2019, Saleh 2025, and the nonlinear cantilever-cavity line of Kumar 2026 (buoyancy-driven, large-deformation, transient) [LIT]; (ii) flow-induced deformation of a thermally *passive* structure as a heat-transfer enhancer — Soti 2015 (vortex-induced vibration of a plate behind a cylinder in a heated channel) [LIT]; (iii) isothermal compliant-channel Q–Δp theory — Christov 2018 (plate-bending wall + Stokes lubrication, shallow 3-D channel) [LIT]; (iv) conjugate thick/flattened-channel heat-transfer data — the Int. J. Therm. Sci. 2023 flattened-channel CHT study located this session is a concrete V-D candidate [LIT]; (v) **newly located nearest-neighbour class**: a 2026 Applied Thermal Engineering study on a single-side-heated rectangular regenerative cooling channel treats **area-averaged thermally induced wall deformation as a coupled design objective together with Nu and Δp** (turbulent, supercritical-fuel, corrugated metal channel; deformation is thermal-expansion response, not eigen-curvature bowing of a pinned polymer strip) [LIT].

What the package proposes: thermal eigen-curvature of a pinned low-conductivity wall segment as the *designed* deformation mechanism, a closed two-way steady conjugate loop, analysis in (Σ_κ, Γ_p, M_b) with fixed-Q vs fixed-Δp contrast, and a verification-first methodology.

Assessment: the bounded gap statement of Chapter 10 **survives my independent searches** — I found no record combining (i)–(iv) in the specific sense claimed (mechanism = wall's own thermal curvature; laminar confined slit; steady two-way closure through the conjugate condition; driving-condition contrast). However, the regenerative-cooling class under (v) shows that "thermally induced deformation coupled with conjugate heat transfer in a channel" as a *phrase-level* claim would be false; the positioning must cite and distinguish that class explicitly. The package's own restraint (no priority claim, C-7 pending) is exactly right. The stated objectives are answerable by the proposed model once the §2.12 model-form decision is taken and the §3 corrections are applied.

---

## 5. Numerical-methodology audit (Task 6)

Verified sound: P2–P1 Taylor–Hood satisfies the discrete inf–sup condition for the Stokes limit [LIT: Brezzi–Fortin 1991; Hood–Taylor 1974]; P2 for both temperatures and displacement is L²-consistent with it; the conforming interface with identical nodal transfer eliminates projection error in the conjugate flux; displacement-based P2 at ν = 0.40 has no volumetric-locking concern; the pseudo-elastic mesh extension with graded stiffness is standard for steady deformable-domain computations; the fixed-point geometry iteration with documented under-relaxation and an escalation path to a monolithic Newton with shape derivatives is appropriate — and its convergence is *expected to be fast* here, because the estimated loop gain is small: the fluid's feedback on the wall thermal state is the interface excess (~1.6 K of a 32 K wall rise), so the geometry fixed point is weakly coupled [IND]. The feasibility estimate (10⁴–10⁵ DOF, direct sparse solves) is credible for the 2-D baseline.

Gaps and required specifications (none changes the method choice):

1. **Advection-dominated energy equation not addressed (P-1).** Pe = Re·Pr = 348 on the D_h basis. On any affordable transverse mesh (say 40–80 elements across H₀) the cell Péclet number is ≫ 2, and Galerkin will exhibit over/under-shoots in T_f precisely where the interface flux — the coupling quantity — is measured. The plan must state the strategy: SUPG (or equivalent) for the energy equation, or a boundary-layer-resolved mesh demonstrated to be oscillation-free via the V-B Graetz developing-profile comparison. This is the largest unaddressed numerical risk.
2. **No code-verification item isolates the mesh-motion map (P-2).** Recommended addition (V-G): compute one case on the mapped domain *and* on an independently generated body-fitted mesh of the same deformed geometry; field-level agreement isolates mesh-map error from physics. (Alternatively a manufactured-solution test with an analytic map.)
3. **Interface quadrature consistency (P-3).** Restore the superseded package's R7: identical quadrature and isoparametric geometry on both sides of the curved P2 interface for traction and flux transfer; add a quadrature-refinement check to V-B/V-D.
4. **Convergence tolerance feasibility (P-4).** ‖Δd‖∞ ≤ 10⁻⁸H₀ = 5×10⁻¹² m is ~3×10⁻⁸ relative to the baseline w_max; that is at the edge of double-precision direct-solve practice. Specify 10⁻⁶·w_max (or demonstrate machine-precision feasibility) and report achieved values.
5. **MATLAB-scale implementation risk (P-5).** A production-quality P2–P1 Navier–Stokes + energy + plane-strain thermoelasticity + deforming-mesh solver in a self-built MATLAB environment is a multi-month expert effort with a high silent-bug surface. The package mitigates this correctly with the mandatory independent replication (C-4/C-12, FEniCS default); that mitigation must remain mandatory, and the replication metric (field-level differences on deflection, Nū, Δp) should be fixed *in advance*, as the earlier checklist already demanded.
6. Minor: (8.1)'s RHS should show the outflow natural term; the "equal with opposite signs" prose should be tightened (§2.8); the buckling-escalation trigger ("near the buckling margin") should carry a number once the §2.12 decision is made (e.g. escalate when N/N_cr > 0.5·design margin).

---

## 6. Verification & validation plan audit (Task 7)

- **V-A (plane Poiseuille): Direct, valid.** Exact profile and f_D Re = 96 [LIT]; machine-precision aspiration is realistic for fully developed flow; specify that the friction metric is evaluated in the developed region.
- **V-B1/V-B2 (Nusselt families): Direct, values verified.** Nu_T = 7.541, Nu_H2 = 8.235, Nu_H1 = 5.385, Nu_T1 = 4.861 all corroborated independently (§4.3). The package's refusal to use the two-sided values as single-wall targets is correct and important. Close C-1.
- **V-C1a/b, V-C2 (constitutive sanity states): Direct, valid** — expectations independently re-derived here and confirmed (including the D-2/D-12 corrected pairings). This is now a clean, self-contained unit-test suite.
- **V-C3 (pinned strip, uniform eigen-curvature, w_max = κ_thL²/8): Direct with one specification gap.** The analytic value assumes **zero membrane force**; with A9-style pins (u = 0 on both end edges) and a benchmark temperature field that has a nonzero mean rise, the strip carries N_θ ≠ 0 and the true solution is the beam–column one, not the parabola. Specify that the benchmark uses the **zero-mean linear gradient** (θ = Γy, θ̄ = 0) — then pins are consistent and the parabola is exact — or use roller ends. Add the end-edge-vs-point-pin sensitivity check (§2.6).
- **V-D (rigid conjugate limit vs published CHT data): correctly labelled "Direct after matching; analogous otherwise"; data still unextracted (C-2).** A concrete candidate series now exists (flattened thick-channel CHT, Int. J. Therm. Sci. 2023) [LIT]; extraction and (K, D, Pe) matching remain to be done. Not a coding blocker; a validation blocker, exactly as the package says.
- **V-E (steady compliant-channel test against the Christov class): as published, this is analogous, not direct [Insufficiently justified as "Direct"].** Christov et al. solve a *shallow 3-D* channel (Hele-Shaw/lubrication, width ≫ height) with a *clamped* plate/membrane wall at *Stokes* Reynolds number; the present geometry is a 2-D slit with a pinned strip at Re = 50. Recommended fix (strengthens the plan at zero external dependency): derive the 2-D slit lubrication + Euler–Bernoulli pinned-strip Q–Δp/w solution in-house (a page of algebra) and use that as the direct V-E′ target, keeping a Christov-class comparison as the analogous external anchor.
- **V-F (per-run conservation and identity checks): correctly specified** — enthalpy balance exactly consistent with the stated BCs; flux-jump norm, superposition identity, mean-stress identity, regime guards. Note the superposition check validates the *linear* decomposition only (§2.9).
- **Turek–Hron exclusion: correct and commendable.** One precision: FSI1 of that benchmark is a *steady* case (FSI2/3 are transient); all three remain large-displacement St. Venant–Kirchhoff cylinder-flag problems, so the exclusion logic stands — but the text should say "steady and transient large-displacement configurations" rather than "transient".
- **Missing items:** the buoyancy check B-1 becomes optional after §2.13 (keep the dormant Boussinesq term as good practice); add V-G (mesh-map isolation) and the quadrature audit (P-3).

---

## 7. Research contribution without changing the problem (Task 8 summary)

Retained as posed. The mechanism (thermal eigen-curvature of a heated low-conductivity pinned wall), the flow class (laminar conjugate slit), the steady two-way closure, the mechanism parameters (Σ_κ, Γ_p, M_b), and the driving-condition contrast together constitute a defensible, bounded novelty per the searches of §4.4; the nearest identified neighbours (Kumar 2026; Soti 2015; Christov 2018; the 2026 regenerative-cooling CHT-deformation optimization study) differ in mechanism, regime, or coupling closure, and must be cited and distinguished explicitly. The formulation's own bounded-claim discipline and its refusal to report trends before computations are model scholarly practice. The principal threats are (a) the C-7 formal database pass still outstanding, and (b) the §2.12 model-form decision — if the linear model is retained unchanged while its deflection claim silently relies on ignoring the membrane interaction, a competent reviewer will find the inconsistency via the buckling section exactly as this audit did.

---

## 8. Required corrections (priority order; full detail in `HFF_correction_plan.md`)

**Critical mathematical/numerical defects (must fix before any coupled design claim):**
1. Gr, Ri, Br values (×10³ each); close D-8/B-1 on corrected arithmetic; rewrite the buoyancy paragraphs (Ch. 3 §3.2, Ch. 7 §7.3, Ch. 6 dictionary, App. B).
2. Model-form/design conflict: membrane-force/deflection interaction vs linear kinematics at N/N_cr = 0.275; take one of the three resolutions of §2.12; re-evaluate A-3, σ_bend, and the stress-fraction row accordingly.
3. Strip pressure-load datum: state the casing/outlet datum and re-quote p̄, w_p, Γ_p (values change; conclusion does not).
4. A-6 wording: replace with an explicit stress cap and margin.

**Physical-model clarifications:** plane-strain justification of the wide-plate buckling coefficient; pinned-edge vs point-pin sensitivity at L/d = 10; V-C3 zero-mean-gradient specification; linear-scope clause on superposition (5.14).

**Numerical-method additions:** advection-stabilization strategy for the energy equation; mesh-map isolation test (V-G); interface quadrature audit; feasible convergence tolerance; keep mandatory independent replication with pre-registered metrics.

**Benchmark evidence to procure:** V-D series extraction (C-2; candidate located), V-E 2-D-slit benchmark derivation + Christov-class anchor (C-3), property/datasheet freeze (C-6), C-7 novelty pass before any positioning sentence.

**Bibliographic corrections:** complete gupta2024photothermo (title + DOI now known); close C-1 with the corroboration chain; finish hood1974 metadata; adjust the Turek–Hron description (steady *and* transient); verify the "high Péclet" clause for kumar2026 or drop it.

**Nonessential writing:** fig_signs label swap; K notation collision; the loose cancellation prose in §8.2.

---

*Integrity note: every number in this audit was independently recomputed; every literature claim is tagged with its source; the two previous-audit errors that propagated into the package (Gr, Br) are documented with the propagation path; no reference, DOI, or benchmark value has been invented, and nothing has been added to or changed in the original package.*
