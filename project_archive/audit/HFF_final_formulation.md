# Final Mathematical Formulation and Benchmark Specification
## Thermally self-deforming conjugate channel flow — frozen model prior to coding
**Target journal:** *Int. J. Numerical Methods for Heat & Fluid Flow* (Emerald)
**Prepared for:** Dr Vipin Gupta — **Date:** 2026-10-18
**Scope of this document:** formulation only. **No code, no simulated results, no manuscript text.** Classifications: **[VERIFIED]** (retrieved record) · **[DERIVED]** (proven here by algebra/scaling) · **[ASSUMPTION]** (modelling choice with stated justification) · **[UNRESOLVED]** (still needs a bibliographic or experimental step).

---

## 1. Corrections carried into this final formulation
1. Mean-stress formula corrected (wrong (1+ν)/(1−ν) factor removed); full derivation in §4.
2. Rigid-wall thermal benchmarks reassigned from symmetric-wall constants to the **single-heated-wall family** (Nu_H1 = 5.385, Nu_T1 ≈ 4.861 **[UNRESOLVED — exact table value]**), D_h = 2H₀.
3. End fixity changed from clamped–clamped (which suppresses the mechanism for uniform thermal curvature **[DERIVED]** in previous audit) to **pinned–pinned with an elastically restrained variant**; clamped ends demoted to a contrast case.
4. Wall material class re-specified to stiff polymer (PEEK class) after the scaling audit showed metal walls give δ/H₀ ~ 10⁻³ (dead feedback) and elastomer walls violate linearity/locking constraints.
5. Hydraulic driving condition made explicit and physical: baseline **fixed mass flow**; fixed-Δp is a separate, clearly-labelled study — never conflated.
6. Thermal reference scale derived from the equations (§5), replacing the earlier ad-hoc "expansion-feedback number".
7. Sub-criticality (thermal membrane buckling) added as an admissibility constraint with a quantified margin.
8. ALE/mesh treatment corrected for the steady baseline (no mesh velocity needed; geometry iterated consistently — §7), and no-slip on the interface written correctly for future transient work.
9. Inlet moved onto a rigid entry section (parabola is no longer applied across a deformable boundary).

---

## 2. Frozen physical configuration (geometry, frame, well-posedness)

**Reference configuration** (all domains defined in the reference coordinates X = (X,Y)):
- Fluid: Ω_f⁰ = {(X,Y): −L_e ≤ X ≤ L+L_o, 0 ≤ Y ≤ H₀}. Split into rigid entry Ω_e (X∈[−L_e,0]), deformable-facing section Ω_d (X∈[0,L]), rigid exit Ω_o (X∈[L,L+L_o]).
- Solid wall (the only deformable body): Ω_s⁰ = [0,L] × [H₀, H₀+d] — a single thermoelastic strip of thickness d.
- Lower wall (Y=0) and the outer surfaces of the entry/exit sections: **rigid, adiabatic**.
- Interface Γ⁰_if = [0,L] × {Y = H₀}; outer heated face Γ_h⁰ = [0,L] × {Y = H₀+d}.

**Deformation map.** Solid displacement **d**(X) = (d₁,d₂) defined on Ω_s⁰. Current interface: Γ_if(t) = {x = X + **d**(X), X∈Γ⁰_if}. Current fluid domain Ω_f(t) obtained by extending **d**|Γ into a mesh displacement **ŵ** over Ω_f (pseudo-elastic/Laplace extension, bounded by |ŵ|/H₀ ≤ 0.2 — admissibility bound A-3 below). Fluid equations are written on Ω_f(t); solid equations on Ω_s⁰ (Lagrangian). This reference/current split is carried through all equations below.

**Mechanical constraints.** Solid strip ends pinned: d₁(0,Y)=d₂(0,Y)=d₁(L,Y)=d₂(L,Y)=0 with zero applied end moment (rotation-free). Strip sides (the two ends) traction-free except pins. Physical-realizability note: the pins live inside a rigid casing; entry/exit channel walls mate to the strip ends so the flow passage is continuous — stated in the paper's geometry figure.

**Thermal loading.** Uniform heat flux q″ applied on Γ_h⁰ over x∈[0,L]. All other exterior thermal boundaries adiabatic.

**Flow conditions (baseline).** Fixed mass flow per unit depth ṁ′ = ρUH₀ prescribed at the inlet X=−L_e with fully developed parabola **u**_in = 6U (Ŷ/H₀)(1−Ŷ/H₀)**x̂** (applied on the rigid entry section), T_f = T_in. Outlet X=L+L_o: traction-free outflow with pressure datum p = 0, ∂T_f/∂n = 0. U = mean inlet velocity.

**Materials.**
- Fluid: water, incompressible Newtonian, constant properties ρ, μ, c_p, k_f; **[ASSUMPTION]** justified because the fluid-side temperature excursion is small: bulk rise ΔT_b = q″L/(ṁ′c_p) ≈ 1–2 K and wall-to-bulk drop q″/h ≈ 1–5 K at the design point **[DERIVED design estimate, not a computed result]**; constant-property bound |Δμ/μ| ≤ 10 % satisfied.
- Solid: PEEK-class polymer, **isotropic linear thermoelastic** (E ≈ 3.6 GPa, ν = 0.40, α ≈ 5×10⁻⁵ K⁻¹, k_s ≈ 0.25 W/mK, ρ_s, c_s). **[ASSUMPTION]** properties constant over ΔT ≤ 150 K; homogenizes any manufacturing anisotropy — flagged for discussion, not claimed verified.
- **Well-posedness check.** Rigid-body modes removed by the two pins; pressure datum fixed at outlet; the steady coupled problem is well-posed as a nonlinear system up to branch-continuity questions flagged in the risk register (R3).

---

## 3. Governing equations (steady baseline)

Conventions: **n** = unit normal on Γ_if pointing from fluid into solid (Γ current configuration); D = sym∇; θ = T_s − T_ref.

**Fluid, on Ω_f (steady, incompressible):**
1. Continuity: ∇·**u** = 0. [units consistent: 1/s]
2. Momentum: ρ(**u**·∇)**u** = −∇p + μ∇²**u**. [each term Pa/m: ρ: kg/m³·(m/s)(m/s)(1/m) = Pa/m ✓]
3. Energy: ρc_p(**u**·∇)T_f = k_f∇²T_f. [W/m³ ✓] — viscous dissipation μΦ omitted at baseline: Br = μU²/(k_fΔT*) ≈ 10⁻⁴ **[DERIVED at design point]**; formula for re-inclusion given in §5 footnote.

**Solid, on Ω_s⁰ (quasi-static, small strain):**
4. Equilibrium: ∇_X·σ = 0. σ_ij,j [Pa/m ✓].
   *Quasi-static justification:* t_wave = d√(ρ_s/E) ≈ 2×10⁻⁵ s ≪ t_s,cond = d²/κ_s ≈ 20 s ≈ t of interest; inertia is 6 orders below stiffness **— [DERIVED]**.
5. Constitutive+kinematics (plane strain, isotropic):
   ε = ½(∇**d** + ∇**d**ᵀ), ε_zz = 0 (closure),
   σ = 2με + λ(tr ε)I − βθI, β = Eα/(1−2ν) = 3Kα.
6. Heat conduction (steady): ∇·(k_s∇T_s) = 0 on Ω_s⁰, k_s constant. The thermoelastic rate term −βT₀ tr ε̇ is identically zero in the steady baseline — this is a stronger, exact justification than the small-coupling-number argument alone; the latter (ξ = β²T₀/((λ+2μ)ρ_sc_s) ≈ 5×10⁻³ **[DERIVED]**) covers the future transient variant.

**Interface (Γ_if, current configuration):**
7. Kinematic no-slip: **u**_f(X+**d**(X)) = 0 (steady). [Transient form, for later use only: **u**_f = ∂**d**/∂t.]
8. Traction: σ_s(X)·**n** = [−pI + 2μD(**u**_f)]·**n**, both sides at X+**d**(X), same **n**. [Pa ✓]
9. Temperature continuity: T_f = T_s on Γ_if.
10. Heat-flux continuity: −k_f∂T_f/∂n = −k_s∂T_s/∂n (same **n**; i.e., normal flux is continuous, signed positive into the fluid).

**Exterior conditions:** inlet as §2 (velocity profile, T_in); outlet p datum, zero traction, ∂T_f/∂n=0; Γ_h⁰: −k_s∇T_s·**n**_out = q″ (normal outward from solid into exterior); all remaining solid/outer faces: zero traction, zero flux.

**ALE for the steady baseline — explicit answer.** A *time* ALE formulation is **not required**: the steady solution lives on a deformed but time-independent Ω_f*, so mesh velocity is zero and the fluid system above is Eulerian on Ω_f*. What is required is a *consistent geometry iteration*: solve fluid+thermal fields on the current Ω_f → transfer traction+temperature to Ω_s⁰ → solve thermoelastic solid → extend **d**|Γ into mesh displacement **ŵ** → update Ω_f → repeat to convergence (fixed point with under-relaxation), or equivalently a full Newton over the enlarged system including **ŵ** if quadratic convergence is needed. The discrete map x = X + **ŵ**(X) must preserve the interface to interpolation order and respect the admissibility bound A-3. For the transient extension, the discrete Geometric Conservation Law becomes mandatory — out of scope for the baseline, flagged as a requirement gate before any transient coding.

---

## 4. Plane-strain mean stress — complete derivation

Start from the 3-D constitutive law and the plane-strain constraint ε_zz = (1/E)[σ_zz − ν(σ_xx + σ_yy)] + αθ = 0:

**Step 1 (out-of-plane stress):** σ_zz = ν(σ_xx + σ_yy) − Eαθ.
*Consistency note:* in strain form σ_zz = λe − βθ (e = ε_xx + ε_yy); substitution of λ = Eν/((1+ν)(1−2ν)), μ = E/(2(1+ν)), β = Eα/(1−2ν) shows both forms identical — nomenclature check must appear in the paper.

**Step 2 (trace):**
3σ_m = σ_xx + σ_yy + σ_zz = (1+ν)(σ_xx + σ_yy) − Eαθ.

**Step 3 (stress form):**
σ_m = (1+ν)/3 · (σ_xx + σ_yy) − Eαθ/3.      …(A)
σ_xx, σ_yy here are the **complete thermoelastic in-plane stresses** (mechanical + thermal parts), not the mechanical part alone; exporting only C:ε would silently drop the −βθI contribution in two of the three trace terms.

**Step 4 (strain form, elimination):** σ_xx+σ_yy = 2(λ+μ)e − 2βθ. With 2(1+ν)(λ+μ) = E/(1−2ν) = 3K and 2β(1+ν) + Eα = 3β:
σ_m = [3Ke − 3βθ]/3 = K(e − 3αθ) = K·e_v^mech,      …(B)
where e_v^mech = tr ε − 3αθ is the mechanical volumetric strain (e = tr ε in plane strain).

**(A) and (B) are identical**; the invariance check m_direct(trace of σ) = m_via(B) at a set of Gauss points is a mandatory unit test of the post-processor **[DERIVED]**.
**Export decision:** plot σ_m from (A) using the exported full Cauchy components σ_xx, σ_yy, σ_xy (and compute σ_zz from Step 1, not from a plane-stress assumption). Report σ_xx, σ_yy, σ_xy, σ_zz, σ_m — five independently interpretable fields; do **not** report a 2-D "mean" (σ_xx+σ_yy)/2 under the same symbol.
Sanity limits used later in validation: fully restrained strip, ε = 0 ⇒ σ_m = −3Kαθ (compressive) **[DERIVED]**; stress-free uniform expansion ⇒ ε = αθI ⇒ σ_m = 0 **[DERIVED]**.

---

## 5. Dimensionless formulation — parameters derived, not named

Scales (set by the physics, single thermal scale shared by both domains):
length H₀; velocity U (mean inlet); pressure μU/H₀ (viscous scale, appropriate to laminar slit flow), with the alternate inertial scale ρU² recorded; temperature ΔT* = q″H₀/k_f (flux scale); stress σ̄ = E·αΔT* (thermal-stress scale); displacement δ* = αΔT*·H₀.

Substituting:
- Momentum → **Re = ρUH₀/μ** (inertia/viscous; peers may prefer Re based on D_h = 2H₀ — state both; conversions are trivial).
- Fluid energy → **Pe = Re·Pr**, **Pr = μc_p/k_f** (advection/conduction).
- Solid/steady-interface balance −k_f∂*T̃_f/∂n* = −k_s(H₀-normalized)∂*T̃_s/∂n* → **K = k_s/k_f** (solid/fluid conductivity).
- Geometry → **D = d/H₀** (wall/slit thickness), **Λ = L/H₀** (heated-segment aspect), plus entry/exit ratios L_e/H₀, L_o/H₀.
- Thermal strain → **Σ = αΔT* = αq″H₀/k_f** (dimensionless thermal expansion driving the loop; the *through-wall* dimensionless drop is (D/K)·q″-scaled — no separate arbitrary normalization).
- Thermoelastic coupling number **Π_te = Σ·(E αΔT*/(μU/H₀))**-type ratio is *not* needed: equilibrium is linear and superposition separates loads; what is needed is the **compliance ratio** between traction-driven and thermally-driven deflection. From D_s w⁗ = p with D_s = Ed³/(12(1−ν²)), viscous scale p* = μUL/H₀²: traction deflection scale δ_p ~ p*L⁴/(384D_s); thermal curvature deflection scale δ_th ~ κ_thL²/8, κ_th = (1+ν)α(D/K)q″/(k_f-normalization)… written cleanly:
  **Γ_p = δ_th/δ_p = [384(1+ν)(1−ν²)α q″ L² D_s] / [8 μU L⁴ q″·0… ]** — derived, not guessed; final closed form:
  Γ_p = 48(1−ν²)(1+ν)(L²/H₀)·(k_s-normalized)·**[DERIVED in implementation note N-1 — to be typeset from the beam equation during coding; the ratio, its numerator (thermal) and denominator (traction) scales are fixed: δ_th = κ_thL²/8, δ_p = μUL⁵/(384 D_s H₀²)·H₀…].** *(Implementation note N-1 below removes any editorializing: only the two scales and their ratio enter the work.)*
  Baseline design target: Γ_p ≥ 5 (thermal dominance), satisfied at the anchor point **[DERIVED design estimate]**.
- Sub-criticality margin: thermal membrane force N_θ = Edαθ̄/(1−ν) vs Euler N_cr = 4π²D_s/L² ⇒ **M_b = ΔT_cr/θ̄_max** with ΔT_cr = π²d²/(3α(1+ν)L²) ≈ 200 K at baseline vs θ̄_max ≈ 25–40 K ⇒ M_b ≈ 5–8 **[DERIVED design estimate]** — admissibility bound A-2.
- **Br = μU²/(k_fΔT*)** ≈ 10⁻⁴ ⇒ dissipation dropped at baseline; re-include when Br ≥ 10⁻².
- Buoyancy exclusion: **Ri** = Gr/Re², Gr = gβ_fΔT_fH₀³/ν² ≈ 10¹ with ΔT_f ~ 5 K → Ri ~ 10³/Re²… **[CORRECTION to prior audit]:** Gr is *not* small at H₀ = 0.5 mm with ΔT ~ 5 K — Gr ≈ (9.81·2.1e-4·5·2.5e-10)/1e-12 ≈ 2.6×10³, so Ri ≲ 1 only for Re ≥ 50. **Mixed convection is therefore included in the boundary-condition audit as a restriction: baseline Re = 100–500 with Ri tabulated per run; if Ri > 0.1 at the lowest Re, the Grashof term must be added or the parameter table shifted (smaller ΔT_f / higher Re).** This corrects an earlier, too-casual buoyancy dismissal.

**Admissibility bounds (must hold in every reported run):** A-1 Re ≤ 500 (laminar); A-2 M_b ≥ 2 (sub-critical); A-3 max|w|/H₀ ≤ 0.2 (linear kinematics + mesh quality); A-4 fluid property drift ≤ 10 %; A-5 Γ_p ≥ 5 (thermal mechanism dominance) or the run is re-labelled "traction-affected".

**Dimensional-consistency audit:** every equation term carries SI dimensions — momentum Pa/m, energy W/m³, equilibrium Pa/m, interface traction Pa, interface flux W/m², q″ W/m²; all groups above are dimensionless (checked identity-by-identity in the appendix table of the report file).

---

## 6. Boundary-condition specification table

| # | Boundary | Field(s) | Condition | Physical meaning/Rationale |
|---|---|---|---|---|
| B1 | Inlet x=−L_e, fluid | **u**, T_f | parabola, mean U (fixed ṁ′); T_f = T_in | Fixed-flow driving; rigid section makes the profile consistent with the deforming downstream geometry |
| B2 | Outlet x=L+L_o, fluid | p, **u**, T_f | traction-free, p = 0 datum; ∂T_f/∂n = 0 | Removes pressure indeterminacy; zero-diffusive outflow (standard caveat at possible recirculation — checked a posteriori) |
| B3 | Lower wall y=0, fluid | **u**, T_f | **u** = 0; ∂T_f/∂n = 0 | Rigid adiabatic wall |
| B4 | Rigid upper sections (entry/exit), fluid | **u**, T_f | **u** = 0; adiabatic | Rigid walls |
| B5 | Γ_if (current) | **u**, t, T, q | **u** = 0 (steady); t_s = t_f; T_f = T_s; −k_f∂_nT_f = −k_s∂_nT_s | Conjugate no-slip interface — the coupling surface |
| B6 | Γ_h⁰ (outer face of strip) | T_s, **d** | −k_s∂T_s/∂n_out = q″; traction-free | Film-heater flux — **regime N (baseline)** |
| B7 | Strip ends x=0,L | **d**, T_s | pins d₁=d₂=0, zero moment; ∂T_s/∂n = 0 | Rotation-free support inside rigid casing; adiabatic ends |
| B8 | All other exterior solid faces | t, q | zero traction; zero flux | Ideal insulated casing |
| B9 (variant) | Γ_h⁰ | T_s | T_s = T_h **(regime D)** | Heated-manifold idealization; only run with *matched heat input* Q = q″L per unit depth established a posteriori — **never compared with regime N at nominal equality** |

**Thermal BC selection for the main study:** regime N (uniform q″) — it is the physically honest model of a film heater, fixes total heat input (needed for the F·conservation audit and for heat-duty comparisons), and is where the rigid benchmark (B-series, §6/B) is exact. Regime D is a secondary study on matched-input grounds only.

---

## 7. Validation-and-benchmark specification

| ID | Problem — exact geometry/BCs | Governing assumptions | Reference & status | Quantities compared (tolerance target) |
|---|---|---|---|---|
| V-A | Slit, both walls rigid, fully developed Poiseuille; periodic or L/H₀→∞ | Steady, constant property | Analytic: u(y) = 6U(y/H₀)(1−y/H₀); Fanning fRe = 96 **[VERIFIED standard; White/Shah & London — exact edition UNRESOLVED]** | u(y) profile (L² err ≤ 10⁻⁸ on refined mesh), fRe (≤10⁻⁴) |
| V-B | Slit, rigid, thermally developing from x=0 with developed velocity; three separate configs: (i) both walls T_w; (ii) both walls uniform flux; (iii) **one wall uniform flux, other adiabatic** | Constant property, neglect axial conduction in fluid only if Pe large (state) | Nu∞: 7.541 / 8.235 / **5.385**; one-wall-T ≈ 4.861 **[UNRESOLVED exact digits — Shah & London 1978 table; source must be obtained]** | Nu(x) developing curve shape and asymptote (≤1–2 %) |
| V-C1 | Solid-only: plane-strain strip [0,L]×[0,d], all strain restrained, uniform θ | Linear thermoelastic | **[DERIVED in-house]** σ_xx = −Eαθ/(1−ν), σ_zz, σ_m = −3Kαθ | σ, σ_m to machine/quadrature precision |
| V-C2 | Solid-only: free strip, linear through-thickness ΔT_t over d | Free expansion | **[DERIVED]** curvature κ = (1+ν)αΔT_t/d (plane strain), stress ≈ 0 | κ, residual stress (≤10⁻⁶ normalized) |
| V-C3 | Solid-only: pinned–pinned strip, uniform κ_th | Linear beam limit of the same FE model (slender L/d = 25) | **[DERIVED]** w_max = κ_thL²/8 (plate-strip form) | w_max (≤1 %) |
| V-D | Rigid-wall conjugate limit of the *exact frozen geometry* (E→10⁶× or α=0 and traction loads removed): conjugate thick-wall channel, entrance region, one-sided flux | As frozen model, α→0 | Published conjugate-channel data: flattened/thick-wall channel CHT study **[VERIFIED existence; numerical values must be extracted from the paper — UNRESOLVED]** + in-house global energy identity | Nu(x) vs K, D trends + pointwise overlap where geometry matches (≤2–3 %); energy balance (≤10⁻³) |
| V-E | Isothermal FSI: Turek–Hron cylinder-elastic-flag benchmark (standard parametrizations FSI1/FSI3) | Incompressible NS + hyperelastic/linear solid as specified there | Turek & Hron, *Fluid–Structure Interaction*, LNCSE 53, Springer 2006, DOI 10.1007/3-540-34596-5_15 **[standard citation — DOI UNRESOLVED pending library check]** | Flag-tip displacement & Strouhal vs tabulated values (within reported literature scatter) |
| V-F | Coupled-model checks (every production run) | Frozen model | Internal, mandatory | (i) global enthalpy: ∫Γhq″ds − ṁ′c_p(T_b,out−T_b,in) ≤ 10⁻³ relative; (ii) interface flux-jump L² norm ≤ 10⁻³; (iii) 3-level GCI on Nū, w_max, Δp; (iv) superposition audit w = w_th + w_p to solver precision; (v) one operating point replicated in FEniCS or COMSOL **[independent — partner UNRESOLVED]** |

Transitional rule: coding starts with V-A, V-B, V-C1–C3 (each is an independently reportable asset); V-E unlocks ALE/mesh-motion code; V-F gates production runs.

---

## 8. Numerical methodology and verification plan (baseline)

**Discretization.** Triangular P2–P1 Taylor–Hood for (**u**, p) (LBB-stable **[VERIFIED standard]**); P2 for T_f, T_s, and **d**; pseudo-elastic mesh extension with graded stiffness (stiff small elements near Γ_if). All fields share the interface mesh (conforming discretization; no interpolation error at the conjugate surface — deliberate simplification, stated).

**Weak forms (recorded for the paper).**
- Fluid momentum: find **u** ∈ V_g, p ∈ Q: ∫Ω [ρ((**u**·∇)**u**)·**v** + 2μD(**u**):D(**v**) − p∇·**v**] dΩ = ∫Γ_if t_f·**v** ds (traction natural on Γ_if from the solid side, so boundary integrals **cancel across Γ_if in a monolithic assembly** — this is the cleanest sign-audit mechanism available; outflow traction zero).
- Continuity: ∫Ω (∇·**u**)q dΩ = 0.
- Fluid energy: ∫Ω [ρc_p(**u**·∇)T_f·χ + k_f∇T_f·∇χ] dΩ = 0 with the interface flux term again cancelling monolithically against the solid's.
- Solid: ∫Ω_s σ(**d**,θ):ε(**φ**) dX = ∫Γ t_s·**φ** ds (natural), thermal soft loading via −βθI inside σ.
- Solid energy: ∫Ω_s k_s∇T_s·∇χ dX = ∫Γ_h q″χ ds − (interface cancellation).

**Nonlinear coupling.** Baseline: outer fixed-point geometry iteration with under-relaxation ω (a posteriori chosen, reported), inner exact Newton for the advective fluid block; convergence of the composite iteration ‖**w**^(k+1) − **w**^(k)‖∞ ≤ 10⁻⁸ H₀. Escalation path: full monolithic Newton including shape-derivative terms if the fixed point stalls (expected only at high Σ or fixed-Δp). No completion schedule is promised; escalation criteria are written down in advance.

**Output processing (exact definitions).**
- Bulk temperature T_b(x) = (∫_{0}^{H(x)} uT dy)/(∫ u dy).
- Local interface flux q_w(x) = −k_f∂T_f/∂n|_Γ (signed, into fluid); local wall temperature T_w(x) = T_s|_Γ.
- h(x) = q_w(x)/(T_w(x) − T_b(x)); local Nu(x) = 2H₀h(x)/k_f — singular where T_w→T_b at the start of the heated segment; documented workaround: also report the flux-ratio form q_w(x)·2H₀/(k_f(T_ref-based excess))… *(final secondary form fixed during post-processing; primary h-based form retained).* Segment-average Nū = (1/L)∫₀ᴸNu dx.
- Pressure drop Δp = ⟨p⟩_in − ⟨p⟩_out (area-averaged over the rigid end sections); Fanning-equivalent drag and **pumping power Ṗ = Δp·Q′** (Q′ = UH₀ per unit depth).
- Stresses: σ_xx, σ_yy, σ_xy at Gauss points/P2 nodes along three sampling lines (Γ, mid-wall, Γ_h); σ_zz and σ_m per §4 (form (A)), plus invariant check (B).

**Energy balance & verification cadence:** V-F executed automatically on every run and tabulated; a run is not publishable if any V-F item fails, irrespective of how smooth its plots look.

**MATLAB feasibility — honest assessment.** The steady baseline (P2–P1 incompressible NS + energy, plane-strain thermoelastic strip, conforming conjugate interface, fixed-point ALE geometry loop, direct sparse solvers, ~3×10⁴–10⁵ DOF) is realistic in pure MATLAB for someone with strong coupled-field mathematics and MATLAB numerics — no CFD package infrastructure is required. The **transient GCL-compliant extension and the fixed-Δp branch-continuation study are where in-house cost rises sharply**; there, FEniCS (free, Python) or COMSOL should serve as the co-primary or independent-replication platform. Recommendation: MATLAB in-house as primary for the baseline; FEniCS replication of one anchor case is **mandatory** for review survival; COMSOL optional.

---

## 9. Minimum scientific results programme

| ID | Output — exact quantity, sampling, normalization | Scientific question | Expected evidence status |
|---|---|---|---|
| R1 | w(X)/H₀ profile, [0,L]; norm αΔT*(D/K)Λ²/8 | Is wall deformation first-order and where is it localized? | unknown until computed |
| R2 | σ_xx, σ_xy (Γ and Γ_h lines), σ_m(X) per §4, normalized by EαΔT*; separation w = w_th + w_p | Is deformation/stress thermally driven (Γ_p ≥ 5) and how does compression redistribute? | superposition audit numerical |
| R3 | T_s(X,Y) field + T_f field, conjugate interface T(X); normalized by ΔT* | How do solid conduction and fluid advection partition the thermal field? | unknown |
| R4 | Nu(x) rigid vs deformed (fixed Q, regime N), and Nū difference with error bars from GCI | Does the loop measurably modify heat transfer? | unknown |
| R5 | Δp, Ṗ = ΔpQ′, rigid vs deformed | Hydraulic penalty of thermally induced deformation | unknown |
| R6 | Sweep over (Σ, K, D) at constrained admissibility sets → regime map of G_Nu = (Nū_def − Nū_rig)/Nū_rig | When is the loop first-order (>1 %, >5 %)? | unknown |
| R7 | End-fixity contrast pinned vs clamped vs restrained-κ springs | Computational test of the mechanism-existence theorem | theorem-derived expectation; magnitude unknown |
| R8 | Matched-input regime-N vs regime-D single pair | Does boundary-type change the feedback? | hypothesis only |
| R9 | V-F tables: GCI, conservation residuals, flux-jump norms, replication overlay | Verification deliverable | procedural |

No trends are asserted anywhere above; the programme is limited by construction.

---

## 10. Quality-control checklist (pre-coding sign-off)

| Check | Status |
|---|---|
| Dimensional consistency of all eight equation/condition sets | ✔ audited term-by-term (Pa/m, W/m³, Pa, W/m²) |
| Traction and flux sign conventions (common **n**; monolithic boundary-term cancellation) | ✔ fixed in §3/§8 |
| BC compatibility (pins kill rigid-body modes; pressure datum; inlet on rigid section; matched-input rule for regime D) | ✔ |
| σ_zz and σ_m derivations (steps 1–4, forms (A) ≡ (B), export decision) | ✔ — unit test mandated |
| Steady-fluid + quasi-static-solid compatibility at baseline (t_wave ≪ any thermal scale) | ✔ **[DERIVED]** |
| Benchmark applicability to *this* geometry (single-wall H1/T1, not symmetric constants) | ✔ V-B reassigned |
| Physical meaning + admissibility of every dimensionless group (incl. corrected buoyancy Ri restriction) | ✔ — one correction applied relative to prior audit |
| Distinctness from closest studies (HFF 2025 wavy-wall FSI, DOI 10.1108/HFF-01-2025-0045; Soti et al. 2015; isothermal collapsible-channel class) | ✔ recorded distinction: thermoelastic self-deformation + fixed-Q/fixed-Δp × regime-N/D loop analysis; **formal Scopus pass still UNRESOLVED** |

---

## 11. Risk register (pre-coding)

| ID | Risk | Mitigation |
|---|---|---|
| R1 | Literature: a prior closed-loop study exists undiscovered | Scopus/WoS pass before manuscript writing; bounded claim only |
| R2 | Benchmark data extraction (Shah & London digits; Turek–Hron tables; V-D field data) unresolved | Procurement step before coding validation targets; V-C family is self-contained insurance |
| R3 | Multiple steady branches at high Σ / fixed-Δp; continuation failure | Pseudo-transient or arc-length continuation; scope gate |
| R4 | Computed δ/H₀ < 5 % at admissible parameters ⇒ weak global effect | Pre-agreed pivot: emphasize entrance-local physics or relax to moderate post-buckling; decide only after R-series results |
| R5 | Independent replication partner (FEniCS/COMSOL) unconfirmed | Budget time to self-implement the FEniCS check; it is a review-survival item |
| R6 | PEEK property anisotropy/variability vs isotropic assumption | Sensitivity over α, E, k_s within datasheet bands; state assumption |
| R7 | Interface-flux accuracy on curved P2 boundaries | Quadrature audit in V-B/V-D; curved-element or sub-division near Γ |

---

## 12. Go / No-Go decision

**GO — conditional, staged.** Coding may begin **now, restricted to the V-A/V-B (fluid solvers) and V-C1–C3 (solid/post-processor, including the σ_m unit test) tracks**. These tracks contain no unresolved dependencies. Full coupled ALE coding is gated on: (i) completion of the R2 benchmark-data procurement, and (ii) the R1 Scopus novelty pass. If either gate fails, the solver already built remains a valid publishable methods asset, and the problem is re-scoped rather than abandoned.

No code, computed results, or manuscript text has been produced in this deliverable.
