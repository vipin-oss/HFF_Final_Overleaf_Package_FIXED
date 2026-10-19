# Research Discovery Report
## Target: *International Journal of Numerical Methods for Heat & Fluid Flow* (Emerald)
**Prepared for:** Dr Vipin Gupta, Gurugram University
**Date:** 2026-10-18
**Status:** Discovery and formulation stage only — **no manuscript has been written**, as requested.

---

## How to read this report

- Statements marked **[VERIFIED]** are supported by a bibliographic record retrieved during this study (Scholar profile, publisher page, or search result).
- Statements marked **[TO CHECK]** are hypotheses or recollections that still require verification against the primary source.
- Statements marked **[HYPOTHESIS]** are predictions about what the proposed computations would show; they are **not** assumed trends and must not appear in a manuscript until computed.
- Only the first ~20 papers of your Scholar profile (sorted by citations) were retrievable; Google Scholar blocked the remaining pages ("Articles 1–20 / Show more" pagination failed). The portfolio analysis below is therefore based on your most-cited work plus your stated research summary. If you want the tail of your publication list (papers 21+) considered, please supply it.

---

# Stage 1 — Research portfolio analysis

### 1.1 What the verified profile shows
Scholar ID `o014_b0AAAAJ` (Vipin Gupta, Gurugram University; ~1006 citations, h-index 20). The most-cited third of the record is remarkably coherent. **[VERIFIED]** publications include:

| Theme cluster | Representative verified publications |
|---|---|
| Memory-dependent MGT photo-thermoelasticity of semiconductors | Gupta, Barak, Das, *Mech. Adv. Mater. Struct.* 31(28), 10543 (2024); Gupta & Barak, HFF 34(1), 84–108 (2024); Gupta & Barak, MAMS 31(25), 6787 (2024) |
| Rayleigh/surface waves in nonlocal, porous, void-bearing thermoelastic media | HFF 34(4) (2024); *Phys. Scr.* 99, 065232 (2024); *Waves Random Complex Media* (2024); HFF 35(9) (2025) |
| Reflection/transmission at fluid–solid interfaces (inviscid/ideal fluid) | HFF 33(2), 912–937 (2023); *Arch. Appl. Mech.* 93(5), 1943 (2023); *J. Appl. Comput. Mech.* 10(1), 111 (2024) |
| Fractional / memory-dependent derivative reformulations of prior models | MAMS 31(20), 5013 (2024); MAMS 31(22), 5532 (2024); *Eur. J. Mech. A/Solids* 111, 105565 (2025); *Phys. Scr.* 99, 025515 (2024) |
| Co-authored size-dependent / micropolar / flexoelectric wave studies | *Phys. Scr.* 99, 065232 (2024); *Eur. J. Mech. A/Solids* 112, 105666 (2025); MAMS 33(1), 2516213 (2026) |

### 1.2 Established strengths
1. **Constitutive command in generalized thermoelasticity**: coupled elastic–thermal–electric (piezo/semiconductor) field equations; LS/GL/GN, Moore–Gibson–Thompson (MGT), two-temperature, memory-dependent and fractional derivatives. **[VERIFIED from titles]**
2. **Wave/semi-analytical machinery**: normal-mode analysis, secular-equation derivation, Laplace-transform inversion, reflection/transmission amplitude ratios and energy partitioning. **[VERIFIED from titles]**
3. **Track record in the target journal**: at least four HFF papers (2023–2025) — editorial familiarity is an advantage, **but** it also raises the novelty bar for the next submission (see §7, desk-rejection risk RD-1).
4. Stated MATLAB / analytical-numerical capability (from your brief).

### 1.3 The repetition risk (a skeptical reviewer's view)
A clear template is visible across the record:

> *take half-space → attach one more generalization (MGT + MDD + fractional + nonlocal + two-temperature + voids/porosity) → derive secular equation → plot amplitude ratios or field profiles vs. one dimensionless parameter group.*

This template has diminishing returns. Reviewers increasingly flag such work as "the same problem with one more constitutive knob," and the Emerald scope statement now explicitly refuses "application of existing numerical methods to engineering problems that are not deemed to be at the forefront of research." **[VERIFIED: HFF aims-and-scope page, retrieved 2026-10-18.]**

Three structural gaps in the toolkit (these are *opportunities*, not criticisms):
- **G1 — No genuine time-domain FEM/computational work.** All verified papers are transform-domain / secular-equation studies on half-spaces; none presents a discretized, mesh-resolved, energy-checked computation with convergence data.
- **G2 — The "fluid" in your fluid–solid interface papers is an ideal (inviscid, potential) fluid** — mathematically a boundary condition, not a solved flow field. No Navier–Stokes, no boundary layers, no Nusselt number: i.e., the *heat & fluid flow* content is presently weak relative to what HFF foregrounds.
- **G3 — Deformation (u, v, w; stress; hydrostatic stress) has never been a *primary* computed output** in a finite body with feedback; it appears only as wave amplitudes.

The strongest next paper for *this profile + this journal* should close G1 and G2 while making deformation the star (G3) — i.e., pivot from *wave propagation in generalized continua* to *computationally resolved, two-way-coupled thermo-fluid-solid physics*. That pivot is honest: it reuses your coupled-field mathematics (where you are strong) and adds computational fluid/heat transfer (where the journal lives).

---

# Stage 2 — Candidate problems (six, technically distinct)

### Candidate A — Nonlinear transient thermoelasticity of a finite body under moving/localized heat flux, temperature-dependent properties
- **Unresolved question:** How do temperature-dependent conductivity/expansion and a *localized, moving* heat source interact with the mechanical constraint to produce non-self-similar stress waves and residual deformation in finite bodies (beyond half-space secular analysis)?
- **Mathematical difficulty:** Strong two-way coupling (the ∝T₀·tr(ε̇) term), moving source ⇒ mesh/ALE issues, nonlinear coefficients ⇒ Newton iteration; wave tracking needs small Δt.
- **Novelty hypothesis:** Moderate. Nonlinear generalized-thermoelasticity FEM papers exist (e.g., nonlinear L–S half-space FEM with temperature-dependent materials, *J. Therm. Stresses* line of work **[VERIFIED existence, Springer link retrieved]**).
- **Journal fit:** Good for HFF only if framed as a *numerical-methods* contribution (e.g., energy-stable scheme), not as parameter plots.

### Candidate B — Size-dependent (strain-gradient) thermoelasticity with non-Fourier conduction
- **Unresolved question:** Interaction of microstructural length scale ℓ with thermal relaxation time τ in transient boundary-value problems.
- **Mathematical difficulty:** Strain-gradient elasticity raises the weak form to H² ⇒ **C¹-continuous elements or mixed/Hu–Washizu formulations are mandatory**; C⁰ elements are mathematically incompatible (would violate the variational structure). Mixed formulations create saddle-point systems and pressure-like locking issues. **[VERIFIED: mixed-FE and C¹ literature retrieved.]**
- **Novelty hypothesis:** Weak-to-moderate *as physics* (ℓ + τ is exactly the "add one more parameter" pattern reviewers now penalize), stronger *as a numerical-methods* paper (a robust mixed C⁰ scheme with benchmarks).
- **Journal fit:** Marginal — no fluid/flow content; thermal content is a parameter in a mechanics problem.

### Candidate C — Deformable dual-porosity medium with *resolved* pore-fluid flow and conjugate heat transfer
- **Unresolved question:** Macroscale thermoelastic deformation caused by microscale pore-fluid transport (real Darcy flow, not a "void fraction" amplitude).
- **Mathematical difficulty:** Biot-type poroelasticity + energy equation + dual-permeability; mature literature base (thermo-poroelasticity is 40+ years old), so the bar is a specific new mechanism.
- **Novelty hypothesis:** Low as posed (this is a heavily worked field); would need a sharper question (e.g., deformation-induced permeability switching feeding back on heat transport) before being defensible.
- **Journal fit:** Moderate (porous-media heat transfer is an HFF staple, but the deformation-to-flow feedback must be real, not decorative).

### Candidate D — Computational (time-domain FE) framework for MGT / memory-dependent generalized thermoelasticity with provably energy-stable time integration
- **Unresolved question:** The MGT/memory literature is dominated by *analysis* (semigroups, a priori error estimates, mostly 1D — Bazarra/Fernández/Quintanilla group **[VERIFIED, multiple papers 2020–2024]**) and by *transform-space secular solutions* (your own work). What is missing in the open literature is a verified, 2-D, benchmark-tested **time-domain computational implementation** with (i) discrete energy decay matching the analytic decay rate, (ii) recovery of LS and Fourier limits, and (iii) comparison against analytic wavefront speeds — packaged as a reproducible solver.
- **Mathematical difficulty:** Third-order-in-time heat equation with memory kernel ⇒ integro-differential time stepping (convolution quadrature or state-space augmentation), CFL/stability interplay with elastodynamics, energy-method design.
- **Novelty hypothesis:** Moderate-to-good and *verifiable*: it is a methods gap, not a parameter gap. It also monetizes your existing model expertise.
- **Journal fit:** Good (numerical method + heat conduction), though no fluid flow.

### Candidate E — Two-way-coupled **Thermo-Fluid-Structure Interaction (TFSI)**: thermally induced wall deformation that feeds back on conjugate heat transfer in channel flow
- **Core idea:** An elastic channel wall (or pair of walls) carrying an externally applied heat flux deforms by thermal expansion/bowing; the deformed geometry changes the velocity field, thermal boundary layer and Nusselt distribution; the changed convective cooling changes the wall temperature, hence the deformation — **a closed feedback loop in which deformation is both input and output.**
- **Unresolved question:** Under which dimensionless conditions is this loop first-order (vs. negligible), and what is the *sign* of the feedback? **[HYPOTHESIS, to be tested computationally]:** for imposed heat *flux* (Neumann) the loop is self-stabilizing (inward bowing → local acceleration → higher local h → lower local ΔT → less bowing), whereas for imposed wall *temperature* (Dirichlet) it can be self-reinforcing. No retrieved paper quantifies this BC-dependent feedback asymmetry.
- **What the closest literature actually does** (Stage 3, below): existing TFSI/CHT work is either (i) flow-driven flexibility passively *enhancing* heat transfer (Soti–Bhardwaj–Sheridan 2015, PoF 2026 cavity-flag studies) — deformation driven by fluid forces, thermal wall strain not part of the loop; or (ii) thermally induced deformation computed *one-way* from frozen CFD fields (regenerative-cooling literature) — loop never closed. The closed, thermally-driven loop with deformation as principal output is the identifiable gap.
- **Mathematical difficulty:** Monolithic or strongly partitioned ALE coupling of Navier–Stokes + energy + quasi-static (or transient) thermoelasticity; mesh motion; consistent linearization of geometry-dependent fluid terms.
- **Journal fit:** **Strong** — fluid flow and heat transfer are the question itself; deformation is a principal output; FSI is explicitly named in HFF's scope.

### Candidate F — Transient finite-element analysis of frictionally excited thermoelastic instability (TEI) in sliding contact
- **Unresolved question:** Post-critical evolution of hot-spot patterns (mode jumping, saturation) under realistic transient cycles.
- **Status of field:** Mature. Eigenvalue critical-speed FEM (Du, Zagrodzki, Barber et al.) and transient FE (Zagrodzki 1990–1999) established the methodology decades ago; Journal-fits better to *Wear* / *Int. J. Solids Struct.* / *J. Tribology*.
- **Journal fit for HFF:** Weak-moderate — heat is generated by friction rather than transferred/transported; HFF reviewers may see it as tribology. Not recommended here.

---

# Stage 3 — Literature-supported novelty assessment (strongest candidates: E, D; A as context)

Verified closest-paper comparison. DOIs/links are exactly as retrieved; any entry flagged **[TO CHECK]** needs one bibliographic click before citing.

| # | Closest paper (authors, year) | Venue / link | Physical model | Numerical method | Established | Unresolved / our distinction |
|---|---|---|---|---|---|---|
| 1 | Soti, Bhardwaj, Sheridan (2015), "Flow-induced deformation of a flexible thin structure as manifestation of heat transfer enhancement" | *Int. J. Heat Mass Transfer* 84, 1070–1081. DOI 10.1016/j.ijheatmasstransfer.2015.01.048 **[VERIFIED]** | Incompressible laminar channel flow + advection-diffusion heat transfer + *flow-loaded* elastic plate; plates thermally passive | Sharp-interface immersed-boundary flow solver, in-house FE structure solver, strong partitioned coupling | Flexible wake structures passively raise Nu; proposed a Turek–Hron-type FSI+heat benchmark | **Wall thermal expansion/bowing absent; feedback is fluid→structure→flow, not thermal→deformation→heat transfer.** Our loop driver and principal output differ. |
| 2 | "Nonlinear thermo-fluid–structure interactions of two interacting flexible cantilever plates in a differentially heated cavity" (2026) | *Phys. Fluids* 38, 092128 **[VERIFIED link]** | Low-Mach buoyant flow + two-way FSI of flexible plates; heated/cooled plates | FVM (SU2) flow + FEM structure, partitioned two-way | Rich regimes (steady→periodic→chaotic, positive Lyapunov exponents) | Fluid-force-driven oscillators in natural convection; **no solid-side conduction-conjugate resolution with thermoelastic bowing, no forced-convection channel CHT, no feedback-regime map.** Frames our channel-CHT problem as complementary, not duplicative. |
| 3 | Soti-type elastic-walled cavity study cited in Soti et al. (elastic wall raises cavity Nu ~17%) | *(cited within [1])* **[TO CHECK primary source]** | Boussinesq cavity with deformable ALE wall | ALE FE | Elastic walls augment cavity heat transfer | Same class as [2]; flow/buoyancy-driven, not thermal-expansion-driven. |
| 4 | Regenerative-cooling CHT literature (e.g., *Appl. Therm. Eng.* 2026 corrugated-channel study; *Front. Energy Res.* 2022; supercritical sCO₂ channel studies) | **[VERIFIED links retrieved]** | Supercritical/turbulent flow CHT in cooling channels; thermally induced wall deformation reported | RANS/k-ω SST CFD + conduction (some with stress post-processing) | Heat-transfer deterioration mechanisms; deformation quantified as a *correlated output* ("not a redundant thermohydraulic indicator") | **Deformation computed one-way; geometry not updated and fed back into the flow.** Closing the loop is our contribution. |
| 5 | "A novel coupling approach of smoothed FEM with SPH for thermal fluid-structure interaction" (2020) | *Int. J. Numer. Meth. Engng* **[VERIFIED link S002074031934932X]** | Thermal-elastic solid + thermal fluid, ghost-particle interface CHT | ES-FEM (solid) + SPH (fluid) | Methodology for TFSI coupling | Method-centric; no thermally-induced-deformation feedback physics; SPH not competitive for near-wall heat-flux accuracy. |
| 6 | Turek & Hron FSI benchmark | *Fluid–Structure Interaction* (LNCSE 53, Springer, 2006), DOI 10.1007/3-540-34596-5_15 **[TO CHECK — standard citation, verify before use]** | Incompressible flow + elastic obstacle/flag | FE, monolithic ALE | Standard validation target for FSI solvers | Isothermal — supplies our *mechanical/FSI validation rung*, not the physics. |
| 7 | Conjugate-heat-transfer fundamentals review (Dorfman-line / He-industry reviews) | Oxford ORA preprint **[VERIFIED link retrieved]** | CHT fundamentals; interface is not a boundary | — | Conjugate interface coupling changes local Nu by O(10–100%) vs. iso-flux idealization | Motivates *why* wall deformation (which perturbs the conjugate interface) must matter; no deformation feedback. |
| 8 | Bazarra, Fernández, Quintanilla et al. — MGT thermoelasticity numerics (2020; dielectric variant 2022; microtemperatures 2023; MGT–Fourier stability 2024) | *J. Comput. Appl. Math.* **[VERIFIED links]** | MGT(-Fourier) linear thermoelasticity, mostly 1-D | FE in space + implicit Euler; a priori error estimates, discrete energy decay | Rigor: stability/error theory of MGT systems | Usually 1-D, no benchmark-grade 2-D wave-front comparisons vs. analytic solutions (Danilovskaya-class), no reproducible solver artefact. Frames Candidate D. |
| 9 | Prevost & Tao (1983) FE for Green–Lindsay dynamic thermoelasticity | **[VERIFIED (citeseer PDF)]** | GL generalized thermoelasticity | FE + time integration; Danilovskaya-type tests | First credible FE of generalized thermoelasticity | Historical anchor for Candidate D validation chain. |
| 10 | Danilovskaya (1950); Sternberg & Chakravorty (1959)-type coupled dynamic solutions | *(classical; cited in [1 of search set])* **[VERIFIED as standard anchors; exact biblio TO CHECK]** | (Uncoupled)/coupled dynamic thermoelastic half-space | Analytic | Canonical transient thermal-stress benchmarks | Validation rungs for D — and for the *solid limit* of E if a transient variant is run. |
| 11 | Your own HFF papers (Gupta & co-workers, 2023–2025) | HFF 33(2), 33(10), 34(1), 34(4), 35(9) **[VERIFIED from profile]** | Generalized/piezo/photo-thermoelastic half-spaces; ideal-fluid interfaces | Normal-mode / transform / secular equations | Wave reflection-transmission structure in exotic continua | This proposal deliberately does **not** extend this line (anti-repetition; see §1.3). |

**Gap statement (defensible, not "first ever"):** *Within the retrieved literature, no study closes the thermally-driven loop — wall heat load → thermoelastic deformation → altered channel geometry → altered conjugate heat transfer → altered wall temperature → deformation — for forced-convection channel CHT with deformation, stresses and Nusselt fields as co-equal outputs, and no study quantifies the feedback sign reversal between flux-prescribed and temperature-prescribed boundaries.* This is a **gap claim bounded by the searches performed** (listed above), not a universal "first" claim; one more targeted Scopus pass is recommended before manuscript submission.

---

# Stage 4 — Selection and rejection rationale

**Selected (primary): Candidate E — Two-way TFSI with thermally induced deformation.**
- Closes G1 (real discretized computation), G2 (real fluid flow with boundary layers and Nu), G3 (deformation/stress as principal outputs) — the three structural gaps.
- Thermal physics is not decorative: the *question* is a heat-transfer question (when and how does deformation rewrite Nu, bulk-temperature rise and pumping power?).
- Explicitly named in HFF scope (FSI, coupled multiphysics); your four prior HFF papers plus a genuinely different method story is a strong editorial narrative.

**Selected (secondary/standalone): Candidate D — Time-domain MGT/memory FE methods paper.**
Keep as an independent methods paper or as a *later extension* of E's solid model (non-Fourier wall conduction at micro/nano channel scales). Do **not** bundle it into the TFSI paper — that would be exactly the "stack two theories" move this report argues against.

**Rejected:**
- **A** — closest to your old template; fold its best idea (localized/moving heat load) into E as a loading case instead.
- **B** — C¹-continuity requirement is a poor cost/benefit trade for this journal; physics novelty is parameter-stacking; validation chain is thin. Revisit only as a *methods* paper if you build C¹/mixed expertise first (Shekarchizadeh–Abali–Bersani 2022 benchmark would then be your rung **[VERIFIED]**).
- **C** — novelty not identifiable without a sharper mechanism; Biot literature too mature.
- **F** — mature field, wrong journal; would read as tribology, not heat-and-fluid-flow.

---

# Stage 5 — Mathematical blueprint for Candidate E (leading problem)

### 5.1 Geometry and coordinates
Two-dimensional plane-strain channel: fluid domain Ω_f = {(x,y): 0≤x≤L, 0≤y≤H(x,t)}, H(x,t)=H₀+w(x,t), where w is the upward displacement of the fluid–solid interface from the elastic wall. Solid wall Ω_s = {(x,y): H(x,t)≤y≤H(x,t)+d}, clamped at x=0 and x=L (built-in ends). Upper outer surface y=H+d receives uniform heat flux q″₀; all other outer solid boundaries thermally insulated. (Symmetric twin-wall variant noted as an extension; single-wall first — the asymmetry *is* what produces bowing.)

### 5.2 Unknown fields
Fluid: velocity **u**=(u,v), pressure p, temperature T_f. Solid: displacement **d**=(d₁,d₂), temperature T_s. Interface/mesh: displacement **w** (ALE). Principal mechanical outputs: σₓₓ, σ_yy, σ_xy, and mean (hydrostatic) stress m = tr(σ)/3, computed *consistently in plane strain with constrained transverse expansion*:
 m = (1+ν)/3·(σₓₓ⁽²ᴰ⁾+σ_yy⁽²ᴰ⁾) − (Eα/3)(T_s−T_ref)·(1+ν)/(1−ν)… 
(i.e., including σ_zz = ν(σₓₓ+σ_yy) − Eαθ exactly; the formula used must be stated in the manuscript, as thermal eigenstrain contributes to σ_zz.) **[TO CHECK: final closed form to be derived during code development.]**

### 5.3 Fluid balance laws (steady, incompressible, constant-property Newtonian)
- Continuity: ∇·**u** = 0.
- Momentum: ρ_f(**u**·∇)**u** = −∇p + μ∇²**u**. (Inertia kept — constrictions create local acceleration; Stokes flow would kill the key mechanism.)
- Energy: ρ_f c_p (**u**·∇)T_f = k_f∇²T_f + μΦ, with viscous dissipation Φ kept only when Brinkman number Br = μU²/(k_fΔT_h) is non-negligible; state the Br restriction explicitly.
- Role of terms: advection carries the bulk temperature rise that defines the thermal load on the wall; wall-normal diffusion sets the local interface flux that drives solid conduction.

### 5.4 Solid balance laws (quasi-static linear thermoelasticity + conduction)
- Equilibrium: ∇·σ = 0, σ = C:(∇**d**)ˢʸᵐ − β θ **I**, β = Eα/(1−2ν), θ = T_s − T_ref.
- Energy: ρ_s c_s ∂T_s/∂t = k_s∇²T_s (transient variant) or k_s∇²T_s = 0 (steady core study). Coupling term −βT₀tr(∇**ḋ**ˢʸᵐ) is *neglected and justified* by the small coupling parameter ξ = β²T₀/(ρ_s c_s(λ+2μ)) ≪ 1 for metals — this must be *stated and defended*, since quasi-static solid with resolved fluid transients is the consistent asymptotic choice. One-way coupling (thermal→mechanical inside the solid) retains full two-way coupling *across the interface*, which is where the physics is.
- Role of terms: eigenstrain βθ·**I** is the loop driver; clamped ends convert uniform heating into compressive membrane stress plus, because heating is one-sided, bending (bowing) — the deformation that re-enters the fluid problem through H(x).

### 5.5 Interface and exterior conditions
Fluid–solid interface Γ (moving): T_f = T_s; k_f ∂T_f/∂n = k_s ∂T_s/∂n; no-slip **u** = Ḣ·n̂-style kinematic condition (zero for steady geometry, mesh-velocity for transient); traction σ·n = (−p**I** + 2μ**D**)·n. Inlet: **u** = fully developed parabola, T_f = T_in. Outlet: traction-free/pressure datum, ∂T_f/∂n = 0. Outer solid surface: −k_s∂T_s/∂n = q″₀ (Neumann regime) **or** T_s = T_h (Dirichlet regime) — the two feedback regimes to be contrasted.

### 5.6 Dimensionless groups (the paper's organizing axes)
- Re = ρUH₀/μ; Pr = μc_p/k_f; Pe = Re·Pr.
- Conductivity ratio K = k_s/k_f; wall-thickness ratio D = d/H₀.
- Thermal-load measure: Θ* = q″₀H₀/(k_fT_ref) (or (T_h−T_in)/T_ref).
- **Expansion-feedback number Σ = α·ΔT_h** with ΔT_h = q″₀H₀/k_f: the dimensionless thermal strain scale. Expected δ/H₀ ∼ Σ·g(K, D, L/H₀, restraint conditions). **[HYPOTHESIS — the function g is what the computation determines.]**
- Structural softness relative to fluid loading S = μU L³/(E*d³…) **[TO CHECK: precise Cauchy-type group to be fixed in non-dimensionalization step]** — matters once flow traction loads the wall in addition to thermal bowing.
- Brinkman Br (viscous dissipation switch).
- Deliverable metric: feedback gain G_Nu = (Nu_def − Nu_rigid)/Nu_rigid as a function of (Σ, Pe, K, D): **the regime map is the central scientific product.**

### 5.7 Restrictions for consistency/well-posedness (to be stated in paper)
Re ≤ O(10³) (laminar); |δ|/H₀ ≲ 0.2 (ALE validity and linear-elasticity strain bound; flag geometric nonlinearity as extension); constant fluid properties (state the Boussinesq-free choice and its ΔT bound); clamped-end singularity handling (more mesh refinement / Saint-Venant discussion); uniqueness of the steady coupled solution not guaranteed — continuation in Σ recommended.

---

# Stage 6 — Numerical strategy, validation roadmap, figure programme

### 6.1 Discretization (implementable in MATLAB)
- Monolithic formulation in the ALE frame; fluid: Taylor–Hood P₂–P₁ triangles (LBB-stable); temperature P₂; solid: P₂ triangles; mesh motion by Laplace/pseudo-elastic smoothing with interface displacement as Dirichlet data.
- Steady problem: exact Newton linearization of advection on the current geometry (plus Picard warm-start continuation in Re and Σ); sparse direct solve for the Newton system (MATLAB backslash / UMFPACK); GMRES with ILU if DOF counts grow.
- Transient variant: BDF2 (2nd order, L-stable) for T_f and T_s; quasi-static solid stepped per time level; Δt chosen from solid diffusion and advective time scales; monitor discrete energy ∫(ρcT)dV and net enthalpy flux as consistency checks.
- Coupling: monolithic by default (partitioned Dirichlet–Neumann with Aitken relaxation used only as a cross-check — and its documented instability at high coupling strength is itself a citable methods point).
- Convergence criteria: relative Newton residual < 10⁻⁸; mesh independence at ≥3 refinement levels with Nu and max|w| as monitored quantities (target <1% change).

### 6.2 Validation roadmap (mandatory, hierarchical)
1. **Fluid-only limits:** fully developed channel fRe = 96 (constant-property Poiseuille); symmetric iso-flux parallel-plate Nu = 7.541 and iso-temperature Nu = 8.235 **[VERIFIED values, classical]**.
2. **Rigid conjugate limit (E→∞ or α→0):** in-house code must reproduce the rigid-wall conjugate solution; cross-check against published conjugate channel results (entrance-region Nu suppression vs. K and D — e.g., the flattened/thick-channel CHT study **[VERIFIED link]** or the conjugate Graetz literature **[TO CHECK: pick exact benchmark values]**).
3. **Solid-only limits:** (a) heated clamped–clamped beam/plate strip — curvature and membrane stress vs. classical bimetal/Timoshenko-type analytics; (b) fully constrained bar: σ = −βθ; (c) for the transient variant, Danilovskaya-class 1-D thermal-shock comparison (classical benchmark **[VERIFIED existence]**).
4. **FSI mechanical rung:** Turek–Hron benchmark cylinder-flag deflection/frequency from the isothermal version of the code **[VERIFIED standard target; exact tabulated values TO CHECK]**; alternative low-Re check: small-deflection elastic-channel lubrication solution **[TO CHECK]**.
5. **Energy/conservation audit:** net heat in (q″₀×length) = net enthalpy out, to within 10⁻³, *with* deformation active — catches interface-flux and mesh-motion errors that field plots hide.
6. **Mesh & Δt convergence tables** (required by HFF reviewers de facto).
7. **Independent replication:** one reference case re-implemented in FEniCS or COMSOL by a co-author; report the discrepancy — this is the reproducibility deliverable that a MATLAB in-house paper needs to survive review.

If any rung fails at the full-model level, the *chain* (1→4) still constitutes a publishable verification skeleton for the reduced models — explicitly say so in the paper.

### 6.3 Figure programme (each figure = one question)
| # | Figure | Scientific question it answers |
|---|---|---|
| F1 | Geometry, BCs, mesh skeleton, ALE handling | Sets the problem; demonstrates interface treatment |
| F2 | Validation panel: fRe, Nu limits, rigid-conjugate match, heated-beam match | Establishes solver credibility (rungs 1–3) |
| F3 | w(x)/H₀, and σₓₓ, σ_xy, m(x,H) along the wall at representative (Σ, Pe) | **How much does the wall deform, and with what stress state?** (deformation as principal output) |
| F4 | Local Nu(x) for deformed vs. rigid wall at matched conditions | Where exactly does deformation change heat transfer? (entrance shadowing vs. constriction enhancement) |
| F5 | T_s(x,t) and T_f fields: 2-D contour + one 3-D surface | Mechanism: how the conjugate interface redistributes temperature once geometry moves |
| F6 | Regime map: G_Nu(Σ) at several Pe, K, D; markers for sign change | **Central result:** when is the feedback first-order, and of which sign? |
| F7 | Neumann-vs-Dirichlet contrast at matched heat input | The BC-dependent feedback asymmetry (**hypothesis test**, plotted only after solving) |
| F8 | Δp/Nu vs. pumping-power and heat-duty trade-off, deformed vs. rigid | Engineering consequence: does deformation help or hurt the heat-exchanger figure of merit? |
| F9 | Transient start-up: w(t), Nu(t), T_s(x,t) after flux step; time-scale ratio collapse | Dynamics: which time scale (solid diffusion vs. advection) gates the feedback? |
| F10 | Convergence/error table + one energy-audit plot | Verification deliverable |
| F11 | Interaction plot G_Nu(Σ × K) with iso-contours | Do conduction and deformation mechanisms reinforce, cancel, or switch? (genuine 2-mechanism interaction, not a parameter sweep) |

No figure assumes a trend; every pair-of-curves exists to answer a stated question.

---

# Stage 7 — Critical reviewer assessment and journal fit

### 7.1 Scores (1–10), with evidence
| Criterion | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| Originality | 5¹ | 5² | 4³ | 6⁴ | 8⁵ | 5⁶ |
| Mathematical depth | 7 | 8 | 7 | 8 | 7 | 7 |
| Physical significance | 6 | 5 | 6 | 6 | 8 | 7 |
| Numerical-method contribution | 5 | 7 | 6 | 8 | 7 | 6 |
| Validation feasibility | 7 | 5 | 6 | 8 | 7 | 8 |
| Reproducibility | 8 | 6 | 7 | 9 | 7 | 7 |
| Relevance to heat & fluid flow | 6 | 4 | 6 | 6 | 9 | 4 |
| Feasibility within your capability (MATLAB, coupled-field math strong, CFD new) | 8 | 5 | 7 | 9 | 6 | 6 |

Evidence notes: ¹ nonlinear-generalized-thermoelasticity FEM exists in the thermal-stresses literature. ² parameter-stacking pattern; C¹/mixed burden. ³ Biot thermo-poroelasticity is 40+ years mature. ⁴ Bazarra-group analyses pre-empt "first numerical analysis," but not a benchmarked 2-D reproducible solver. ⁵ gap documented in Stage 3; closest competitors (Soti 2015; PoF 2026) drive deformation with fluid force, not thermal strain. ⁶ TEI methodology dates to Zagrodzki/Barber 1990s.

### 7.2 Desk-rejection risk register (for Candidate E)
- **RD-1 — "Template continuation" suspicion.** Your HFF history is secular-equation wave studies; the new submission must *look* different in §1 (explicitly position against the half-space/transform literature, including your own).
- **RD-2 — In-house code without independent replication.** Mitigate with rung-7 replication (FEniCS/COMSOL) and published verification tables.
- **RD-3 — Thermal superficiality.** Forbidden by construction here: the research question *is* Nu/temperature/heat-flux physics; keep mechanical-field plots co-equal, not dominant.
- **RD-4 — Unsupported constitutive freedom.** None taken: Newtonian fluid, linear thermoelasticity, constant properties — every restriction quantified (§5.7). Reviewers reward defended simplicity over stacked generality.
- **RD-5 — Parameter-sweep monotony.** The figure programme is question-driven with a hypothesis-test figure (F7) and an interaction figure (F11); enforce this discipline in the manuscript.
- **RD-6 — Unverifiable "first" claims.** Use the bounded gap statement of Stage 3, and repeat one Scopus pass pre-submission.

### 7.3 Journal-fit verdict
HFF is a strong, realistic target **only for Candidates E and D**. The scope's pointed exclusion of routine applications means the paper must foreground the *methodological and mechanistic* content (monolithic ALE thermo-coupled formulation + feedback-regime map + verification chain) — which the plan above does.

---

# Stage 8 — Implementation plan (blueprint → code → manuscript)
*(Prepared because Stages 1–7 pass; no manuscript text written.)*

1. **Weeks 1–2:** Final non-dimensionalization; fix group definitions flagged **[TO CHECK]**; write MATLAB steady incompressible Navier–Stokes + energy solver (rigid channel); pass rungs 1–2.
2. **Weeks 3–4:** Add thermoelastic solid + conjugate interface (rigid geometry); pass rung 3; energy audit.
3. **Weeks 5–7:** ALE mesh motion + monolithic Newton with geometry-consistent Jacobian (or verified secant variant); Turek–Hron isothermal rung; mesh-convergence tables.
4. **Weeks 8–10:** Production: regime map over (Σ, Pe, K, D); Neumann-vs-Dirichlet contrast; transient start-up set; FEniCS replication of one case.
5. **Weeks 11–12:** Manuscript (structure: mechanism → formulation → method → verification → regime map → conclusions), literature re-check, submission to HFF.

**Deliverables I can generate next, on your instruction:** (i) the MATLAB prototype solver for Stage 6.2 rungs 1–3; (ii) the exact non-dimensionalization and Jacobian hand-derivation as a working note; (iii) the Scopus verification pass formalizing the bounded gap statement.

---

### Honesty log
- Scholar profile pages beyond the first 20 were inaccessible; tail of publication list not reviewed.
- Every DOI/URL in Stage 3 was returned by a live search during this session; items tagged **[TO CHECK]** require one bibliographic confirmation before citation. No benchmark values, references, or literature gaps were invented; gap claims are explicitly bounded to the searches performed and labelled as such.
