# Critical Audit and Scientifically Validated Redesign
## Revision of the TFSI Research Proposal for *Int. J. Numerical Methods for Heat & Fluid Flow*
**Prepared for:** Dr Vipin Gupta — **Date:** 2026-10-18
**Verdict up front (Stage 8, argued below): Decision B — retain the central idea, redesign the physical and numerical formulation.** The previous report had one outright algebraic error (mean stress), one physically wrong mechanism claim (end fixity), one benchmark misassignment (Nusselt values), and one unexamined feasibility risk (deformation magnitude). All four are corrected here, and the corrections make the paper *stronger*: they convert the proposal from a plausible-sounding coupling study into a mechanism-specific, testable problem.

Tag convention: **[VERIFIED]** = confirmed from a retrieved primary/publisher record; **[DERIVED]** = proven by algebra/scaling in this document; **[TO CHECK]** = needs one more bibliographic step; **[HYPOTHESIS]** = computable conjecture, not a result.

---

# Stage 1 — Audit of the previous report

### 1.1 Correction table

| # | Original claim / equation / recommendation | Issue | Why it matters | Correction | Verification |
|---|---|---|---|---|---|
| A1 | Mean stress: m = (1+ν)/3·(σ_xx+σ_yy) − (Eαθ/3)·(1+ν)/(1−ν) | **Algebraically wrong second term.** | The (1+ν)/(1−ν) factor corrupts every reported mean-stress plot quantitatively and would be caught by any careful reviewer. | m = (1+ν)/3·(σ_xx+σ_yy) − Eαθ/3; equivalently m = K(e_v − 3αθ), derived in §1.2. | **[DERIVED]** §1.2; standard isotropic thermoelasticity. |
| A2 | σ_zz = ν(σ_xx+σ_yy) − Eαθ stated without derivation | Correct, but must be *derived* from ε_zz = 0 with thermal strain, and its role inside m must be shown. | Reviewers expect the plane-strain closure to be exhibited, especially when mean stress is a headline output. | Full derivation given in §1.2, with plane-strain constitutive matrix stated. | **[DERIVED]** §1.2. |
| A3 | "Clamped ends convert uniform heating into compressive membrane stress **plus, because heating is one-sided, bending (bowing)**" | **Physically wrong for the spatially uniform component.** A clamped–clamped plate/beam under a *uniform* through-thickness thermal gradient has its thermal moment fully reacted by end moments; transverse deflection is identically zero (proof in §2.2). Simply-supported ends bow freely. | The entire proposed mechanism (bowing of a one-sided heated wall) depends on end fixity, axial non-uniformity of the thermal load, or buckling — none of which was analysed. The mechanism is real, but only in well-defined configurations. | New formulation (§2, §4): elastic segment with **rotation-free or elastically restrained supports**, embedded between rigid channel sections; bowing driven by (i) free curvature κ_th(x) = α ΔT_t(x)/d·g(ν) and (ii) its axial non-uniformity from the *developing* conjugate temperature field. End-condition sensitivity becomes a documented result, not an oversight. | **[DERIVED]** §2.2; elementary beam/plate eigen-curvature theory. |
| A4 | Validation values: "iso-flux parallel-plate Nu = 7.541; iso-temperature Nu = 8.235" | **Values assigned to the wrong boundary conditions**, and both belong to *symmetrically* heated slits, whereas the proposed geometry has **one** heated wall. | Using a wrong rigid-wall limit invalidates the whole validation chain and misstates the conjugate baseline by ~40–60%. | Correct pairs (Shah & London, laminar forced convection in ducts): both walls uniform T: Nu = 7.541; both walls equal uniform flux: Nu = 8.235; **one wall uniform flux, other adiabatic: Nu = 5.385**; one wall uniform T, other adiabatic: Nu ≈ 4.861 **[TO CHECK last value]**, all with Nu based on D_h = 2H. Our rigid limit is the **single-wall (H1) family**. | Shah & London (1978) **[TO CHECK exact table]**; values 7.541/8.235/5.385 **[VERIFIED standard]**. fRe = 96 for the slit **[VERIFIED standard]**. |
| A5 | "Quasi-static solid, transient fluid" as default | Incomplete: valid for **mechanics** (solid wave time ≪ everything), but the **solid thermal field** need not be faster than the fluid. | Decides which time integrators and which transient study are defensible. | Mechanics quasi-static always (t_wave = d√(ρ/E) ~ 10⁻⁸–10⁻⁶ s). Thermal fields: retain transient terms in *both* Ω_f and Ω_s in the start-up study, or run the steady core problem; decide per study using the time-scale map in §2.4. | **[DERIVED]** §2.4. |
| A6 | Neglect of solid coupling term −βT₀tr(ε̇) justified by "coupling parameter ξ ≪ 1" only | Justification incomplete but easily repaired. | At steady state the term vanishes *identically* (ε̇ ≡ 0); in transients both ξ and the rate scale matter. | Two-part justification in §4.13: (i) ξ = β²T₀/((λ+2μ)ρc) ≲ 10⁻³–10⁻² for metals and for stiff polymers **[DERIVED for PEEK ≈ 5×10⁻³]**; (ii) in the steady core study the term is exactly zero. Note: ξ is *not* small for very soft elastomers at fast rates — one more reason (see N1) to avoid ν≈0.5 walls in the core study. | **[DERIVED]**; classical thermoelastic coupling-number argument (e.g., text of Nowacki/Boley-Weiner) **[TO CHECK citation]**. |
| A7 | Interface traction σ·n = (−pI + 2μD)·n; "no-slip u = 0 at moving boundary"; "u = Ḣ·n̂-style kinematic condition" | Sign/normal conventions not fixed; the transient no-slip condition was hand-wavy and is wrong as written (wall motion ≠ Ḣ·n̂ on an arbitrarily shaped interface). | Sign errors at the interface silently poison both momentum and energy coupling — the highest-risk bug class in in-house coupling codes. | Fixed conventions in §4.7: common normal **n** (fluid→solid); t_f = (−pI+2μD_f)·**n**, t_s = σ_s·**n**, t_s = t_f on referral to the same normal; kinematic condition **u**_f = ∂**d**/∂t on Γ_t (material interface), which reduces to **u**_f = 0 in the steady core study. | **[DERIVED]** §4.7; standard ALE-FSI references (Donea; Turek–Hron benchmark formulation **[VERIFIED existence]**). |
| A8 | Heat-flux continuity "k_f∂_nT_f = k_s∂_nT_s" without flux-sign audit | Incomplete: must be stated as equality of normal flux vectors −k_f∇T_f·**n** = −k_s∇T_s·**n** with the same **n**, plus a discrete interface jump metric as a verification output. | Interface flux mismatch is the classic silent failure of partitioned/monolithic CHT implementations. | Exact condition + post-processing metric ‖[k∂nT]_Γ‖/‖q̄_Γ‖ < 10⁻³ as a reported verification number; global identity ∫Γ q″dΓ = ṁc_p(T_b,out − T_b,in) to 10⁻³. | **[DERIVED]**; conservation audit standard in CHT practice. |
| A9 | "Inlet: fully developed parabola" on a channel whose wall deforms | Inconsistent where the deformable segment reaches the inlet plane. | A parabola imposed on a deformed inlet cross-section violates mass conservation subtly. | Rigid entry length upstream of the elastic segment (§4.1); inlet condition applied on the rigid section; alternative constant-flow-rate constraint stated. | **[DERIVED]** design change. |
| A10 | Hydraulic driving condition left implicit (mass-flow inlet suggested) | **The driving condition is part of the physics**, not a technicality: fixed-Q and fixed-Δp channels have *opposite* feedback characters (§2.3). | Omitting it discards the sharpest testable hypothesis available to this problem. | Core study at fixed mass flow (Ġ prescribed at inlet, pressure datum at outlet); second study at fixed Δp (pressure-driven Poiseuille inlet via pressure boundary or iterated flow rate). Feedback-sign contrast becomes the central figure. | **[DERIVED]** §2.3; collapsible-channel literature documents driving-condition dependence for isothermal FSI **[VERIFIED existence, PoF/Glasgow eprints retrieved]**. |
| A11 | ALE moving mesh "pseudo-elastic smoothing", BDF2 transient | Missing the **discrete geometric conservation law (GCL)** and the geometric terms of the Newton Jacobian. | A moving-mesh transient scheme that violates the GCL manufactures spurious sources — fatal in a paper whose claim is subtle feedback physics. And without geometry-consistent Jacobian terms, Newton stalls at quadratic → linear convergence. | GCL-compliant mesh-velocity evaluation (mesh velocity computed from the same BDF2 stencil as the field); monolithic Jacobian including shape-derivative terms for interface-adjacent elements, or a documented quasi-Newton/secant treatment; both stated in §4.11. | **[DERIVED]**; GCL is standard (Lesoinne–Farhat lineage) **[TO CHECK citation]**. |
| A12 | Structural softness group "S = μU L³(E d³…) (TO CHECK)" | Left undefined in the previous report. | Cannot size the benchmark nor state admissible regimes without it. | Proper groups derived in §4.11: bending stiffness D_s = Ed³/(12(1−ν²)); traction-deflection scale δ_p = p*L⁴/(384D_s); thermal-curvature deflection scale δ_th = κ_th L²/8; ratio δ_th/δ_p as the mechanism-purity number; **thermal post-buckling admissibility bound** ΔT̄ < ΔT_cr = π²d²/(3α(1+ν)L²) **[DERIVED in §2.5]**. | **[DERIVED]** §2.5, §4.11. |
| A13 | No check that thermal bowing is *macroscopically significant* in the proposed regime | Major feasibility gap. Scaling (§2.1): for thin metal walls at moderate flux, δ/H ~ 10⁻³–10⁻² — the mechanism is **negligible**; feedback loop quantitatively dead. The previous report did not perform this estimate. | If the loop is O(10⁻³), the paper has results that are formally correct and scientifically empty — worse than a desk rejection risk, it is a *substantive* risk discovered only after months of coding. | Regime redesign (§2.1): stiff-polymer wall (PEEK/PMMA class; k_s ≈ 0.25, α ≈ 5×10⁻⁵, E ≈ 3.6 GPa, ν = 0.4) at q″ ~ 10⁴–10⁵ W/m² gives ΔT_t = q″d/k_s = 20–200 K and δ/H ~ 0.1–0.3 with δ_th/δ_p ≫ 1. High-flux metal (regenerative-cooling) regime is real but already occupied by the literature. | **[DERIVED]** order-of-magnitude analysis, §2.1. |
| A14 | Isothermal FSI benchmark list incomplete | The journal itself recently published exactly-adjacent work; the audit must position against it, not around it. | Reviewers will cite the journal's own papers back at the manuscript. | Added to the closest-work set (Stage 3): Saleh et al., HFF 35(4), 1484–1511 (2025), DOI 10.1108/HFF-01-2025-0045 **[VERIFIED full record]**; Alsabery-group HFF 29(10), 3756–3780 (2019), DOI 10.1108/HFF-10-2018-0593 **[VERIFIED]**. Distinct from our problem (natural-convection cavity, traction-driven wavy/flexible wall, no wall thermal strain, no forced-convection conjugate channel) — see Stage 3 table. | **[VERIFIED DOIs]**. |
| A15 | Convergence criterion "relative Newton residual < 10⁻⁸; monitored Nu, max|w| < 1% change" | Reasonable but missing: increment norms, interface consistency, and a *fixed* refinement path; also missing Δt-convergence for the transient runs. | "Mesh and time-step refinement" was a headline requirement of the brief. | §6/Stage 5: 3-level nested refinement with estimated convergence order (GCI-style reporting), BDF2 Δt-halving series, Newton residual + increment ‖Δx‖∞ < 10⁻⁷·(1+‖x‖∞). | Standard practice; stated, not yet computed **[HYPOTHESIS-free — procedural]**. |

### 1.2 Derivation audit — plane-strain thermoelasticity and the mean stress

With θ = T − T_ref, isotropic linear thermoelasticity in 3-D reads
σ_ij = λ e δ_ij + 2μ ε_ij − β θ δ_ij,  e = tr ε,  β = (3λ+2μ)α = Eα/(1−2ν) = 3Kα.

**Out-of-plane stress (plane strain closure).** Plane strain imposes ε_zz = (σ_zz − ν(σ_xx+σ_yy))/E + αθ = 0, hence
σ_zz = ν(σ_xx+σ_yy) − Eαθ.  (Check in strain form: σ_zz = λe − βθ, e = ε_xx+ε_yy; both agree after substituting λ, μ in E, ν.)

**Mean stress — correct derivation.** The constitutive object is the full tensor σ; the mean stress is a post-processed invariant, m = tr σ/3:
3m = σ_xx + σ_yy + σ_zz = (1+ν)(σ_xx+σ_yy) − Eαθ … (stress form).
Using σ_xx+σ_yy = 2(λ+μ)e − 2βθ and 2(1+ν)(λ+μ) = E/(1−2ν) = 3K (verified algebraically):
m = Ke − βθ = K(e − 3αθ) = K·e_v^mech … (strain form).
Interpretation: **mean stress equals bulk modulus times the mechanical (non-thermal) volumetric strain** — clean, dimensionally consistent, and easy to verify against analytic rungs (e.g., the axially restrained strip below gives e = 0 ⇒ m = −βθ = −3Kαθ, matching the direct trace of its stress tensor). The previous report's factor (1+ν)/(1−ν) multiplies Eαθ/3 only in erroneous intermediate manipulations; it is wrong in both forms.

**Analytic solid rungs used later (all **[DERIVED]**):** (i) Axially restrained plane-strain strip, σ_yy = 0 faces, uniform θ: ε_xx = 0 ⇒ σ_xx = −Eαθ/(1−ν), σ_zz = νσ_xx − Eαθ = −Eαθ(1+ν)·ν/(1−ν) − Eαθ…(evaluated in §5 directly from the tensor), m = −3Kαθ. (ii) Free plate with linear through-thickness gradient ΔT_t over thickness d: pure curvature κ_th = αΔT_t/d (plane-stress) or (1+ν)αΔT_t/d (plane-strain), stress-free. (iii) Simply-supported beam strip under uniform thermal curvature: w(x) = κ_th x(L−x)/2, w_max = κ_th L²/8. (iv) Membrane force under full restraint: N_θ = E d·αθ̄/(1−ν).

---

# Stage 2 — Reconsideration of the physical model

### 2.1 Magnitude audit (the decisive calculation)
In steady state with the outer surface carrying flux q″ and the inner surface convecting into the fluid, the through-thickness drop across the wall is exactly ΔT_t = q″d/k_s (all flux crosses the wall; axial conduction modifies this locally at segment ends). Free-plate thermal curvature κ_th ≈ αΔT_t/d; supported-segment deflection δ ~ κ_thL²/8. Therefore
δ/H ~ αq″L²/(8k_sH), independent of d.

| Regime (L=30 mm, H=0.5–2 mm, q″=5×10⁴ W/m²) | ΔT_t (d=1 mm) | δ/H | Verdict |
|---|---|---|---|
| Stainless steel (k=16, α=1.2×10⁻⁵) | 3.1 K | ~10⁻³–10⁻² | **Dead loop** — previous report's silent parameter choice |
| Aluminum (k=160, α=2.3×10⁻⁵) | 0.3 K | ~10⁻⁴ | Dead loop |
| PDMS (k=0.15, α=3×10⁻⁴) | 330 K | ≫ 1 (invalid linearity, collapse) | Mechanism real but needs geometric nonlinearity, and fluid traction dominates (E ~ 1 MPa); also ν≈0.5 → locking |
| **PEEK/PMMA-class stiff polymer (k≈0.25, α≈5×10⁻⁵, E≈3.6 GPa, ν=0.4)** | 200 K (at 5×10⁴); 20 K (at 5×10³) | **0.1–0.3 at 10⁴–10⁵ W/m²** | **Sweet spot** — thermal ≫ traction, linear kinematics admissible |
| High-flux metal, q″ ~ 1 MW/m² (regenerative cooling) | ~125 K (d=2 mm) | ~0.05–0.1 | Real but literature-occupied, turbulent RANS required |

**Design conclusion [DERIVED]:** the feedback mechanism is first-order only in low-conductivity, high-expansion, moderately stiff walls — the class of additive-manufactured/polymer micro-heat-exchanger and microreactor walls, which is also a defensible application anchor **[TO CHECK — motivation citations to be finalized pre-submission]**. Metal walls join the study only as the α→0 / K→large rigidizing limits.

### 2.2 End-fixity audit (mechanism existence)
For a beam strip with built-in (clamped) ends under a *spatially uniform* thermal curvature κ_th, the equilibrium equation D_s w⁗ = 0 with all four boundary conditions w = w′ = 0 has the unique solution w ≡ 0: the thermal moment is entirely reacted and **there is no bowing** **[DERIVED]**. Bowing appears from (i) rotation-free supports (w_max = κ_th L²/8), or (ii) **axially non-uniform** thermal curvature κ_th(x) — which occurs naturally at the thermal entrance, at the start of the heated segment, and wherever the conjugate interface temperature is non-uniform — or (iii) thermal post-buckling of a clamped, membrane-compressed wall.
**Redesign:** the elastic segment is **pinned–pinned (rotation-free, displacement-restrained)** with a documented elastically-restrained variant; clamped ends are retained only as a contrast case showing mechanism suppression. This converts an error into a *result* (F7 in the figure programme).

### 2.3 Hydraulic driving condition is physics
**[DERIVED reasoning]:** with fixed mass flow, local constriction raises local velocity and local h(x), lowering local wall temperature — a **bounded, self-limiting** loop. With fixed Δp, constriction raises hydraulic resistance, *reducing* total flow, raising mean wall temperature, deepening deformation — a **self-reinforcing** loop arrested only by material/geometric nonlinearities ("thermal-elastic choking"). Isothermal analogues (driving-condition dependence of deformable-channel steady states) exist in the collapsible-channel literature **[VERIFIED existence]**, but no thermal conjugate version is known from the searches. This becomes the central hypothesis (§8), tested — not assumed — by paired simulations.

### 2.4 Steady vs. transient decisions
Time scales **[DERIVED example, PEEK wall d=2 mm, κ_s ≈ 2×10⁻⁷ m²/s; water, H=0.5 mm, κ_f ≈ 1.4×10⁻⁷; L=30 mm, U=0.05 m/s]:**
- solid mechanics: t_wave = d√(ρ_s/E) ≈ 2.5×10⁻⁵ s → **quasi-static mechanics, always**;
- solid thermal: t_s = d²/κ_s ≈ 20 s; fluid thermal: t_f = H²/κ_f ≈ 1.8 s; advective: t_adv = L/U ≈ 0.6 s.
Ordering t_adv ≲ t_f ≪ t_s ⇒ the *approach* to the deformed steady state is **gated by the solid's thermal inertia**; a transient study with quasi-steady fluid (t_s/t_f large ⇒ dropping ∂_tT_f is defensible at leading order) and transient solid conduction is asymptotically consistent. **Decisions:** (1) core study: fully steady coupled problem; (2) start-up study: quasi-steady fluid + transient solid conduction + quasi-static mechanics, with the dropped fluid-transient term quantified a posteriori. No simulated figure may mix the two framings silently.

### 2.5 Geometric nonlinearity and buckling admissibility
Linear thermoelasticity + ALE is admissible while δ/H ≲ 0.2 and the membrane stress stays sub-critical. Restrained thermal expansion of a clamped segment generates membrane force N_θ = Ed·αθ̄/(1−ν); Euler threshold N_cr = 4π²D_s/L² ⇒ **sub-criticality bound** θ̄ < ΔT_cr = π²d²/(3α(1+ν)L²) **[DERIVED]** (≈ 42 K for PEEK d = 2 mm, L = 25 mm, α = 5×10⁻⁵, ν = 0.4). Design the parameter table so that max θ̄ ≤ ½ΔT_cr (safety factor 2), and run one Green–Lagrange-kinematics check case. Post-buckled thermal deformation is *not* in the main scope (it is a different paper); it is listed as an explicit extension.

### 2.6 Separation of thermal vs. traction deformation
Because solid mechanics is linear, σ and **d** superpose. Protocol: (R1) full coupling; (R2) α := 0 (traction-only deformation); (R3) release fluid traction on Γ (thermal-only deformation). Report the decomposition w = w_th + w_p (verified to machine precision in the linearized regime) — this *is* the answer to "can the two be distinguished." **[DERIVED protocol]**

### 2.7 Boundary conditions that isolate the feedback
Film-heater flux on the outer face (Neumann, q″ uniform over the heated segment, zero elsewhere), all other outer surfaces adiabatic; Dirichlet variant (outer face at imposed T_h, e.g., wall embedded in a heated manifold) as the second regime. Buoyancy excluded a priori: Richardson number Ri = gβ_fΔTH²/(νU)… stated as Gr/Re² ≪ 1 with numbers in the appendix **[DERIVED bound to be tabled]**.

---

# Stage 3 — Novelty re-verification

Closest-work set (every DOI/link below was retrieved this session; **[VERIFY]**-tags as noted):

| Paper (authors, year) | Venue / DOI | Configuration, coupling direction | Method | Established | Distinction from redesigned proposal |
|---|---|---|---|---|---|
| Saleh, Alsabery, Sheremet, Ghalambaz, Hashim (2025), "Impact of FSI on unsteady flow within wavy-heated wall cavity" | HFF 35(4), 1484–1511. DOI 10.1108/HFF-01-2025-0045 **[VERIFIED full record]** | Natural convection in wavy cavity; flexible right wall deforms under fluid forces; wall has no thermal eigenstrain | ALE + FEM (unstructured), transient | Wall flexibility modulates buoyant flow and heat transfer; published *in the target journal* | Traction-driven, buoyant, cavity — not forced-convection channel CHT; no wall thermal strain; no feedback-sign analysis vs. driving conditions. **This is the paper the manuscript will be compared to by reviewers — the introduction must cite and distinguish it explicitly.** |
| Alsabery-group (2019), "FSI analysis of transient convection… cavity containing inner solid cylinder and flexible right wall" | HFF 29(10), 3756–3780. DOI 10.1108/HFF-10-2018-0593 **[VERIFIED]** | Natural convection, S-shaped flexible wall, ~2% mean-Nu change | ALE FEM | Flexible-wall cavity benchmark lineage in HFF | Same distinction as above; quantifies how *small* traction-driven Nu effects can be — supports our δ/H design philosophy rather than weakening it. |
| "Numerical study of FSI for enhanced heat transfer in microchannels with an oscillating elastic wall" (2024) | **[VERIFIED existence via ResearchGate record; venue/DOI TO CHECK]** | *Prescribed* wall oscillation in microchannel; ~15% Nu gain | ALE FE | Passive/active wall motion enhances Nu | Motion is imposed, not thermally self-induced; no solid thermal field, no loop. |
| Soti, Bhardwaj, Sheridan (2015) | IJHMT 84, 1070–1081. DOI 10.1016/j.ijheatmasstransfer.2015.01.048 **[VERIFIED]** | Flow-loaded flexible plate behind cylinder in heated channel | IB + FE, strongly coupled | Flow-induced deformation raises Nu; proposed FSI+heat benchmark | Same as previous report: driver is fluid loading, not wall thermal strain. |
| PoF 38, 092128 (2026), two heated elastic cantilevers in differentially heated cavity | **[VERIFIED link]** | Buoyant cavity, two-way nonlinear FSI | FVM(SU2)+FEM | Chaos/route-to-chaos under strong heating | Driver is hydrodynamic; our loop is thermal-strain-driven in forced convection. |
| Thermal-flow-force-electrical coupling in high-flux chip microchannels (2024) | *J. Appl. Phys.* 135, 215103 **[VERIFIED link]** | Chip microchannel cooling; thermal deformation of chip | ANSYS Fluent one-way multifield | Deformation and temperature cross-sensitivity quantified | Deformation does not update the flow domain — one-way post-processing. |
| Static response of deformable microchannels (comparative modelling; Christov-group lineage) | **[VERIFIED existence via NSF PURL record; exact refs TO CHECK]** | Pressure-driven bulging of PDMS microchannel, no heat | Theory + experiments | Soft-hydraulics Q–Δp relations | Isothermal; supplies our elastic-channel validation rung (Stage 5, L5b). |
| Collapsible-channel FSI (Heil/Hazel lineage; LBM, beam-wall variants) | **[VERIFIED existence, multiple records]** | Elastic segment in channel flow, self-excited oscillation, fixed-flow/fixed-pressure dependence | Monolithic/partitioned FSI | Driving-condition-dependent stability of elastic channel flow | Isothermal; motivates our fixed-Q vs fixed-Δp contrast rather than duplicating it. |
| Esfahani-type flattened/thick-wall conjugate channel CHT (2023) | **[VERIFIED link]** | Rigid thick-wall conjugate channel | FVM | Wall/thickness/conductivity effects on entrance Nu | Rigid wall; supplies rigid-conjugate comparison data (Stage 5, L4). |

**Bounded gap statement (defensible):** *Among the records retrieved — including the target journal's own 2019–2025 flexible-wall FSI papers — we found no study of forced-convection conjugate heat transfer in a channel where wall deformation is produced by the wall's own thermal strain and fed back into the flow, and none analysing how the sign/magnitude of that loop depends on the hydraulic driving condition (fixed-Q vs fixed-Δp) and thermal boundary type (Neumann vs Dirichlet).* This is a bounded claim tied to the listed searches; one formal Scopus pass remains mandatory before submission. The gap is narrower than the previous report claimed — but it is also sharper and more defensible.

---

# Stage 4 — Corrected mathematical formulation (redesigned Candidate E)

### 4.1 Geometry
2-D slit channel (plane flow, plane strain in solid). Rigid entry section x∈[−L_e,0]; elastic segment x∈[0,L] (wall thickness d, pinned–pinned at its ends within a rigid outer casing); rigid exit section x∈[L,L+L_o]. Fluid domain Ω_f (height H₀ undeformed); solid wall domain Ω_s above it; opposite (lower) wall rigid and adiabatic. Outer face of the elastic segment carries uniform flux q″ over x∈[0,L] (regime N), or imposed temperature T_h (regime D). All other exterior solid boundaries adiabatic. End-fixity variants: pinned–pinned (core), elastically restrained (sensitivity), clamped (contrast case — expected to suppress the mechanism, §2.2).

### 4.2 Unknowns
Fluid: **u**=(u,v) [m/s], p [Pa], T_f [K]. Solid: **d**=(d₁,d₂) [m], T_s [K]. Reference-state mesh displacement **ŵ** on Ω_f (ALE), equal to **d** at Γ.

### 4.3–4.5 Balance laws
Fluid (steady core; transient start-up variant per §2.4):
∇·**u** = 0;
ρ_f(**u**·∇)**u** = −∇p + μ∇²**u**;
ρ_f c_p(**u**·∇)T_f = k_f∇²T_f (+μΦ only if Br = μU²/(k_fΔT_h) ≳ 10⁻²; computed per case).
Solid:
∇·σ = 0 in Ω_s (quasi-static; justification §2.4);
σ = C:(∇**d**)ˢʸᵐ − βθI, β = Eα/(1−2ν), θ = T_s − T_ref;  (plane strain version of the above with σ_zz closed as in §1.2)
Steady core: ∇·(k_s∇T_s) = 0; start-up variant: ρ_sc_s∂_tT_s = k_s∇²T_s − βT₀tr(∇**ḋ**)ˢʸᵐ with the last term dropped under the documented ξ-argument (A6); k_s constant.
Transient start-up only: **u** = quasi-steady at each t; initial conditions T_s(x,0) = T_ref, T_f = T_ref everywhere, **u**(0) = developed profile.

### 4.7 Interface conditions (sign-audited)
Common normal **n** on Γ_t pointing from fluid into solid; F := x + **d** the current interface map.
Kinematic: **u**_f(F(**x**,t),t) = ∂**d**/∂t (steady: **u**_f = 0).
Traction: σ_s(**x**,t)·**n** = [−pI + 2μD_f](F(**x**,t),t)·**n** — both sides evaluated with the **same** normal; the solid problem sees t = −p**n** + τ_f·**n**.
Thermal: T_f = T_s; −k_f∇T_f·**n** = −k_s∇T_s·**n** (same **n**; flux conservation, no jump to within the reported tolerance).

### 4.8 Exterior boundary conditions
Inlet (rigid section): prescribed mass flow with developed profile (fixed-Q study) or prescribed pressure drop (fixed-Δp study); T_f = T_in. Outlet: traction-free flow, pressure datum p = 0, ∂T_f/∂n = 0. Solid segment ends: pinned (d₁ = d₂ = 0) with zero applied moment (core); outer face: −k_s∇T_s·**n** = q″ (regime N) or T_s = T_h (regime D); remaining outer faces: zero traction, adiabatic.

### 4.9 Mean stress (corrected)
m = tr σ/3 = (1+ν)(σ_xx+σ_yy)/3 − Eαθ/3 = K(e − 3αθ), with σ_zz = ν(σ_xx+σ_yy) − Eαθ (§1.2). Report whether plots show m or the in-plane mean (σ_xx+σ_yy)/2 — never conflate the two.

### 4.11 Dimensionless groups (corrected set)
Re = ρŪ(2H₀)/μ; Pr; Pe = Re·Pr; K = k_s/k_f; D = d/H₀; Λ = L/H₀; Θ = q″H₀/(k_fT_ref) (or (T_h−T_in)/T_ref); thermal-strain number Σ = αΔT_h with ΔT_h = q″d/k_s (note: ΔT_h uses the *through-wall* drop, which is what drives curvature — this corrects the earlier group's characteristic temperature); curvature-deflection scale δ̄ = ΣΛ²(H₀/d)/8·(H₀-normalized); bending-vs-traction purity number Π = δ_th/δ_p with δ_p = p*L⁴/(384D_s), p* = μŪL/H₀² (viscous scale) — Π ≳ 5 required for a "thermally driven" claim; sub-criticality margin M_b = ΔT_cr/θ̄_max ≥ 2 (§2.5); Br restricted; Ri ≪ 1 (forced convection).
**Nusselt definition (fixed convention):** bulk temperature T_b(x) = ∫ρc_p T_f u dy / ∫ρc_p u dy; local flux q_w(x) = −k_f∇T_f·**n**|_Γ (signed positive into the fluid); local h(x) = q_w(x)/(T_w(x) − T_b(x)); local Nu(x) = h(x)·2H₀/k_f; average Nū over the heated segment. All four quantities explicitly defined — the singular behaviour where T_w → T_b must be noted at the thermal entrance.

### 4.12 Governing PDE system (boxed summary)
The paper should display: the five-field monolithic system (u,v,p,T_f | d₁,d₂,T_s | mesh), weak forms, the ALE map ∇²_m**ŵ** = 0 with graded pseudo-elastic stiffness near Γ, GCL-consistent BDF2 mesh velocity, and the full interface set of §4.7.

### 4.13 Neglected terms and quantitative justifications
(i) −βT₀trε̇: zero identically at steady state; ξ ≈ 5×10⁻³ (PEEK) **[DERIVED]**; retained only in a sensitivity check. (ii) Fluid buoyancy: Ri bound tabulated. (iii) Viscous dissipation: Br computed per run. (iv) Temperature-dependence of all properties: excluded; ΔT_max bounded such that |Δk/k|, |Δμ/μ| ≲ 5–10% (water up to ~60 °C; PEEK α stable below 140 °C) **[TO CHECK final numbers]**. (v) Fluid transient term in the start-up study: t_f/t_s ≈ 0.1 ⇒ dropped at leading order, estimated a posteriori. (vi) Turbulence: Re ≤ 500 (slit transition far above).

---

# Stage 5 — Validation hierarchy (exact benchmarks)

| Level | Benchmark — exact problem and BCs | Type | Source |
|---|---|---|---|
| L1 fluid-only | Plane Poiseuille in slit of height H: u(y) = 6Ūy(H−y)/H², fRe = 96 (Darcy-free convention: Fanning f = τ_w/(½ρŪ²), state convention) | Analytic | Classical **[VERIFIED]** |
| L2 fluid-only thermal | Rigid slit, one wall uniform flux / other adiabatic, fully developed: Nu_H1 = 5.385; one wall uniform T: Nu_T1 ≈ 4.861 **[TO CHECK]**; thermally developing Graetz-family curves for reference | Analytic/tabulated | Shah & London 1978 **[TO CHECK exact table]** |
| L3 solid-only | (a) Axially restrained plane-strain strip: σ_xx = −Eαθ/(1−ν), m = −3Kαθ; (b) free plate, linear ΔT_t: κ = αΔT_t/d, zero stress; (c) pinned–pinned uniform-curvature strip: w_max = κ_thL²/8; (d) transient 1-D conduction in slab: series solution (Carslaw–Jaeger) **[TO CHECK citation]** | Analytic | **[DERIVED]** (a–c) |
| L4 rigid conjugate | Present code with E→10¹² Pa (or α=0): reproduce published rigid conjugate thick-wall channel entrance-region Nu vs K, D | Published numerical | Flattened/thick-channel CHT study **[VERIFIED link; values to extract]** + global enthalpy balance to 10⁻³ |
| L5 coupled FSI (isothermal) | (a) Turek–Hron FSI benchmark (standard tabulated deflections/frequencies) **[VERIFIED existence; values TO CHECK]**; (b) low-Re pressure-driven bulge of a compliant slit channel vs soft-hydraulics data **[VERIFIED existence of class; pick one dataset, TO CHECK]** | Published numerical / experimental | as cited |
| L6 full model | (i) Global energy identity ∫q″ = ṁc_pΔT_b (+losses) to ≤10⁻³ **with deformation active**; (ii) interface flux-jump metric to ≤10⁻³; (iii) Newton residual/increment, GCI on 3 nested meshes, Δt-halving; (iv) **independent replication of one operating point** (FEniCS or COMSOL), reporting field-level discrepancies; (v) R2/R3 superposition decomposition verified to solver precision | Internal + independent | this work |

No benchmark is "transferred" across heating configurations: the rigid limit of *this* geometry is the H1 (single-wall) family, not the symmetric-wall constants.

---

# Stage 6 — Numerical feasibility (pre-implementation assessment)

- **Method choice:** monolithic ALE FE in MATLAB with Taylor–Hood P2–P1 triangles (fluid), P2 (T_f, T_s, solid **d**), pseudo-elastic ALE mesh. LBB-stability argument **[VERIFIED standard]**. Mixed u–p or B-bar solid only if a ν≈0.49 wall is ever used — avoided by material choice in the core study (this is a deliberate scope decision, state it).
- **Newtonization:** full Newton for advection + conjugate coupling; geometry enters through ALE shape-derivative terms (or a documented Broyden/secant fallback). Continuation in Re, then Σ.
- **Main difficulties (honest list):** (1) saddle-point conditioning and solver design (direct sparse fine to ~10⁵ DOF); (2) GCL-compliant moving mesh for the transient runs; (3) interface flux accuracy (quadrature on curved P2 boundaries); (4) Jacobian consistency near Γ; (5) ensuring the steady coupled solution branch is the one computed (uniqueness not proven — continuation + fixed-point cross-check).
- **Independent verification:** FEniCS (free) or COMSOL replication of one case — mandatory, budget it from day one.
- **Burden estimate:** this is a multi-month solo development. No fixed completion time is promised; the de-risking order is L1→L3→L4 (a few weeks of code growth each, each independently useful) before any ALE work begins. The L1–L4 chain alone is citable verification capital even if the project scope is later cut.

---

# Stage 7 — Hypothesis-driven results programme (trimmed)

| # | Content | Question | Status |
|---|---|---|---|
| F1 | Validation panel (L1–L4) | Is the solver credible? | Procedural |
| F2 | w(x)/H₀ and {σ_xx, σ_xy, m} along the wall; R1–R3 decomposition | How large is the thermal deformation, and is it thermal rather than traction-driven? | **[HYPOTHESIS:]** w_th ≈ w, w_p ≪ w at designed Π |
| F3 | κ_th(x), T_s(x) through-wall, conjugate interface temperature | Where does the curvature come from (entrance non-uniformity vs. uniform core)? | open |
| F4 | Nu(x), rigid vs deformed wall, fixed-Q | Does the loop measurably change heat transfer, and where? | **[HYPOTHESIS:]** localized changes near developing region; bounded global change |
| F5 | Feedback contrast: fixed-Q vs fixed-Δp (regime N); Nū, Δp, w_max vs Σ | **Central question:** does the loop change sign/character with the driving condition? | **[HYPOTHESIS:]** bounded self-limiting at fixed Q; self-reinforcing "thermal-elastic choking" at fixed Δp — to be computed, not assumed |
| F6 | Regime map (Σ, Pe, K): G_Nu isolines | When is the feedback first-order (>1%, >5%)? | open |
| F7 | End-fixity contrast (pinned vs clamped), matched heat input | Verification of the §2.2 mechanism theorem in the computational model | expected suppression at clamped — compute |
| F8 | Start-up transients T_s(x,t), w(x,t), Nu(t) with time-scale collapse | Which time scale gates the loop's activation? | open |
| F9 | Engineering summary: heat duty vs pumping power at fixed Q and fixed Δp | Does deformation help, hurt, or re-rate the exchanger? | open |
| F10 | Convergence (GCI, Δt), conservation residuals, one-case replication overlay | Verification deliverable | Procedural |

No 3-D surface plots without a question; no parameter panels not linked to F5/F6.

---

# Stage 8 — Final decision

**Decision: B — retain the central idea (two-way thermally-induced-deformation TFSI in a conjugate channel), redesign the physical and numerical formulation.**

**Why not A (proceed as-is):** the as-is configuration (metal wall, clamped ends, implicit fixed-Q, no buckling constraint, wrong rigid-limit benchmarks) contains a wrong mean-stress formula (A1), a mechanism that fails under clamped, spatially uniform heating (A3), and a regime in which the feeding loop is O(10⁻³) (A13). Publishing that would produce formally smooth curves and empty physics.

**Why not C (reject):** no retrieved paper — including the target journal's own flexible-wall FSI line — closes this loop in forced-convection channel CHT, and the redesign (polymer-class wall, pinned segment, driving-condition contrast) restores the mechanism at O(10%) magnitude with linear kinematics intact. The idea survives its own audit.

### Final corrected problem statement
*A two-dimensional slit channel carries steady laminar forced convection of water past a single low-conductivity, high-expansion elastic wall segment (PEEK/PMMA-class, pinned–pinned), externally heated by uniform flux. Wall thermal curvature deforms the channel (δ/H₀ by design O(0.1–0.2)); the deformed geometry modifies the conjugate heat transfer; the modified wall temperature closes the loop. The study is monolithic ALE finite-element based, validated through the six-level hierarchy of Stage 5, and quantifies (i) the deformation–stress–mean-stress fields with source attribution (thermal vs traction), and (ii) how the sign and magnitude of the thermal-elastic feedback depend on the hydraulic driving condition (fixed-Q vs fixed-Δp) and thermal boundary type (flux vs temperature).*

**Central hypothesis [HYPOTHESIS — computable]:** the loop is self-limiting under fixed mass flow and self-reinforcing (bounded "thermal-elastic choking") under fixed pressure drop, with a quantified first-order regime in (Σ, Pe, K) space.

**Objectives (≤4):** O1 build/verify the monolithic ALE TFSI solver (hierarchy L1–L6); O2 quantify the deformation-driven modification of Nu(x), Nū, Δp and stress fields with mechanism attribution; O3 test the driving-condition feedback hypothesis (F5) and produce the regime map (F6); O4 deliver reproducibility artefacts (convergence, conservation audits, one-case independent replication).

**Claimed contribution (moderated, no "first-ever"):** a closed-loop computational treatment of thermo-elastically self-deforming conjugate channel flow with a bounded novelty claim (Stage 3), an explicit mechanism-existence analysis (end-fixity, sub-criticality, δ/H scaling), and a driving-condition feedback result that turns a cou pling exercise into identifiable physics.

### Unresolved risks (flagged, not concealed)
1. Scopus-grade novelty pass still outstanding (bounded claim only).
2. Exact H1 developing-flow reference data (**[TO CHECK]** Shah & London tables; Turek–Hron values) must be extracted before coding validation targets.
3. Solution-branch multiplicity at fixed Δp is plausible and could complicate continuation (this risk is physics, not a bug — budget for arc-length or pseudo-transient continuation).
4. If measured δ/H₀ at designed parameters lands below ~5%, the global feedback will be modest; the paper must then pivot its emphasis to local entrance effects or extend toward the post-buckling regime — decide only after O2 computations.
5. A COMSOL/FEniCS partner for replication is not yet confirmed; without L6(iv) the manuscript weakens.

**No manuscript text, code, or numerical result has been produced in this deliverable, per instruction.**
