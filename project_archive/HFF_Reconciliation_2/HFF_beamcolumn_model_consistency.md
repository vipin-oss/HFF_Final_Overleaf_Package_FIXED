# Targeted audit: consistency of the beam–column model (Chapter 4 / `HFF_beamcolumn_rederivation.md`)

**Audit verdict (see §8 for basis): Existing model justified with an explicit limitation.**
No mathematical error was found in the adopted equation, its baseline evaluation, or any
downstream value. The adopted equation is precisely classified in §2, the constant-force
approximation is quantified against the fully consistent von Kármán solution in §4 (2.3 %
conservative error in w_max at baseline; exact buckling margin), and its validity conditions are
stated in §7. No change to the LaTeX source is required by this audit; no new PDF was compiled;
no solver code was written.

---

## 1. Governing assumptions (as stated in the package)

| Item | Value / statement | Source |
|---|---|---|
| Strip, plane strain (wide plate) | L = 30 mm, d = 3 mm, H₀ = 0.5 mm | A1, A5 |
| Material (frozen band, C-6) | E = 3.6 GPa, **ν = 0.40**, α = 5×10⁻⁵ K⁻¹, k_s = 0.25 W/mK | ch02 table; CAL-07 |
| Baseline thermal load | q″ = 5×10³ W/m²; through-wall drop ΔT_t = 60 K; **θ̄ = 32.3 K** | CAL-05/06; CAL-31 coefficient |
| Decomposition of θ(z) | θ(z) = θ̄ (uniform part) + linear gradient (part g = ΔT_t/d) | §6 below |
| Eigen-curvature | κ_th = (1+ν)αq″/k_s = 1.4 m⁻¹ | eq:kappa; CAL-07 |
| Flexural rigidity | D_s = E d³/[12(1−ν²)] = 9.64 N·m | eq:beam; cell A5 |
| Supports (A9) | **both end edges fully fixed in displacement (u = v = 0)**, rotation free (M = 0) | ch02 A9 |
| Blocked membrane force | N_θ = −E d α θ̄/(1−ν) = −2.91×10⁴ N/m | eq:ntheta; v2a §1b |
| Euler threshold | N_cr = π²D_s/L² = 1.057×10⁵ N/m; N₀/N_cr = 0.275 | eq:tcr; A5 |
| Adopted wall equation | D_s w⁗ + N_θ^c w″ = 0, w = 0, w″ = −κ_th at x = 0, L | eq:beamcol |

Reproduction check (independent, this audit): κ_th = 1.400, D_s = 9.643, N₀ = −2.907×10⁴,
N₀/N_cr = 0.2749, μL = 1.647, w_max = 2.1895×10⁻⁴ m = 0.438 H₀, amplification 1.390,
w′_max = 0.0275 rad, M_mid = −6.36 N·m, σ_bend = 4.24 MPa, σ_tot = 13.93 MPa = 0.155 σ_y —
**every quoted Chapter-4/Table-7.1 value reproduces to the printed precision**.

## 2. Question 1 — Classification of D_s w⁗ + N_θ^c w″ = 0

The fully consistent von Kármán model for this strip (small strain, moderate rotation; current
configuration equilibrium) is the coupled nonlinear system

* transverse equilibrium:  D_s w⁗ − N w″ = 0  (N uniform, because N′ = 0 with no horizontal load);
* kinematics:  ε_x = u′ + ½ w′² − (1+ν)αθ  (von Kármán strain; the ½w′² term is the arc stretching);
* constitutive/axial (plane strain, σ_yy free):  N = (E d/(1−ν²)) · (ε̄_x)  with ε̄_x the
  thickness-mean mechanical strain;
* axial compatibility (u blocked at **both** ends):  u(L) − u(0) = 0  ⟹  ⟨u′⟩ + ½⟨w′²⟩ = 0;
* end conditions:  w = 0, and total moment M = D_s (w″ + κ_th) = 0.

N is therefore an **unknown constant coupled to w** through ⟨w′²⟩. The adopted equation freezes
N at its w = 0 (blocked) value N₀ = |N_θ|. Classification:

> **The adopted equation is the transverse member of the von Kármán system with a frozen
> membrane force — equivalently, the exact linear (constant-coefficient) beam–column equation
> about a prescribed compressive prestress. It is a reduced von Kármán model, not the fully
> consistent von Kármán solution; the geometric-stiffness term N w″ itself is retained at full
> strength, and only the force-level update (the ½⟨w′²⟩ feedback) is dropped.** "Linearized
> about a prestress" and "reduced von Kármán" coincide here; the distinguishing feature of the
> full model is exclusively the N–w compatibility coupling.

Two consistency properties hold regardless of the freezing: (i) the buckling limit sin μL = 0 of
the frozen-force equation coincides exactly with the Euler threshold of the full model, because
the relaxation vanishes as w → 0 (§5); (ii) the frozen-force solution is the *first iterate* of
the consistent problem and, as §4 shows, over- (never under-) predicts the deflection.

## 3. Question 2 — Axial compatibility and the force-relaxation estimate

With u(0) = u(L) = 0 (A9, both end edges), compatibility of the von Kármán strain gives

  ½ ⟨w′²⟩ + ⟨u′⟩ = 0,  so  N(w) = N₀ + (E d / [2(1−ν²)]) ⟨w′²⟩,  N₀ = −E d α θ̄/(1−ν).

The relaxation fraction relative to the blocked mechanical strain e₀ = (1+ν)α θ̄ = 2.261×10⁻³:

  δ₁ ≡ ΔN/|N₀| = ½⟨w′²⟩ / e₀.

For the adopted shape (exact integral of the beam–column solution at μL = 1.647, antiderivative
verified symbolically):

  ⟨w′²⟩ = κ_th² L² · J(μL),  J = [(a²+1)s/2 + (a²−1)sin 2s/4 − a sin²s]/s³,  a = (1−cos s)/sin s,

  J(1.647) = 0.1579 ⟹ ⟨w′²⟩ = 3.568×10⁻⁴, ½⟨w′²⟩ = 1.784×10⁻⁴, **δ₁ = 6.1 %**
  (first-iterate estimate). The note's "≈7 %" used the circular-arc strain κ_geo²L²/24
  = 1.59×10⁻⁴; the exact shape integral gives 1.78×10⁻⁴ — the estimate is confirmed at 6 %,
  and refined below to the self-consistent value.

## 4. Question 3 — Quantified error: consistent solution vs adopted solution

Solving the coupled system exactly (the shape family is unchanged for any fixed N; only μ, hence
μL, adjusts through the compatibility relation λ = λ₀ − β J(λ), with λ = μ²L², λ₀ = 2.713,
β = E d κ_th² L⁴/[2(1−ν²) D_s] = 1.058 — dimensionless):

| Quantity | Adopted (frozen N₀) | Fully consistent vK | Difference |
|---|---|---|---|
| μL | 1.647 | 1.598 | −3.0 % |
| Force relaxation ΔN/\|N₀\| | 0 (frozen) | **5.9 %** | — |
| **w_max** | **2.19×10⁻⁴ m (0.438 H₀)** | **2.14×10⁻⁴ m (0.428 H₀)** | **adopted overpredicts by 2.3 %** |
| Amplification over linear | 1.39 | 1.36 | −0.03 |
| w′_max | 0.0275 rad | 0.0270 rad | −2 % |
| M_mid | −6.36 N·m | −5.86 N·m | −8 % |
| σ_bend | 4.24 MPa | 3.90 MPa | −8 % |
| σ_tot (σ_m + σ_b) | 13.9 MPa (0.155 σ_y) | 13.6 MPa (0.151 σ_y) | −2 % |
| Total surface strain | 5.35×10⁻³ | 5.27×10⁻³ | −1.5 % |
| Arc strain ½⟨w′²⟩ | 1.78×10⁻⁴ | 1.45×10⁻⁴ | — |
| Buckling margin M_b | 3.64 | **3.64 (exact, §5)** | **0** |

Error growth with operating level (constant-force error in w_max, relative to the consistent
solution; q″ scales all rows):

| N₀/N_cr | q″ (W/m²) | w/H₀ (adopted) | w/H₀ (consistent) | error |
|---|---|---|---|---|
| 0.10 | 1 818 | 0.128 | 0.127 | 0.2 % |
| **0.275 (baseline)** | **5 000** | **0.438** | **0.428** | **2.3 %** |
| 0.31 (≈ A-3 mesh bound binds) | ≈5 640 | 0.50 | 0.48 | ≈3 % |
| 0.36 (≈ A-6 stress cap binds) | ≈6 545 | 0.58 | 0.55 | ≈4–5 % |
| 0.50 (= M_b 2 ceiling) | 9 091 | 1.16 | 0.99 | 17 % |
| 0.70 | 12 727 | 2.73 | 1.58 | 73 % (post-critical regime) |

**Reading:** within the *admissible* design envelope of the formulation (ceilings A-3/A-6 bind
at N₀/N_cr ≈ 0.31–0.36, well below the A-2 buckling margin), the frozen-force error stays
≤ ≈5 % and is one-sided (conservative). It becomes large only past N₀/N_cr ≈ 0.5 — exactly
where the specification's escalation trigger already moves the problem off the reduced model.
The direction of the error: freezing the force overestimates the geometric stiffness, hence
overestimates w_max and σ_bend — every reported baseline figure is a slight **upper bound**.

## 5. Buckling margin under the consistent model

The relaxation term ½⟨w′²⟩ → 0 as w → 0, so the onset of transverse instability is governed by
the *blocked* force: the critical state of the fully consistent model is sin μL → 0 with
N → N₀, i.e. **θ_cr = N_cr(1−ν)/(E d α) = 117.5 K and M_b = 3.64 exactly**, unchanged by the
coupling. Past onset, the relaxation acts as a stiffening (hardening) mechanism — no premature
buckling is possible. The reported margin is therefore exact, not approximated.

## 6. Questions 4–5 — Boundary-condition and load compatibility

**(Q4) Transverse pin vs axial restraint.** The buckling-relevant idealization requires two
distinct conditions on each end edge, both of which A9 states ("the strip ends have zero
displacement, zero applied moment"): (i) *transverse* support v = 0 (the "pin" that carries the
reaction and makes w = 0); (ii) *axial* restraint u = 0 on **both** end edges — this is what
generates N_θ at all. The distinction is essential and is what §3's compatibility uses
(u(L) − u(0) = 0). Had either end been axially free (a roller), N_θ would vanish identically,
the beam–column correction would disappear, and the baseline bowing would be the linear parabola
(0.315 H₀). The package consistently adopts full blocking; the O(d) Saint-Venant distinction
between full-edge and point pins (few-percent stiffening) is already recorded with a
one-time check assigned to validation. **Consistent as stated.**

**(Q5) No double counting of thermal effects; pressure compatibility.** The through-thickness
profile θ(z) = θ̄ + g·z (g = ΔT_t/d) decomposes orthogonally: the uniform part drives the
membrane force (∫g z dz = 0 — contributes no curvature), the linear part drives the free
eigen-curvature κ_th = (1+ν)α g (∫θ̄ dz... the uniform part has zero first moment — contributes
no eigen-curvature). The beam–column equation carries each component exactly once: κ_th as the
eigen-curvature (moment boundary condition w″ = −κ_th, i.e. the *total* moment
M = D_s(w″ + κ_th) is zero at the pins — moment-free ends are compatible with the imposed
eigen-moment by construction), and N₀ as the prestress coefficient. The pressure load p̄ = 84 Pa
enters the transverse equation as a distributed load q = p̄, omitted from (4.9): its amplified
contribution is w_p/(1−λ/π²) = 1.24×10⁻⁷ m = **0.06 % of w_max** — omission justified
(Γ_p ≈ 2.4×10³). Two second-order pressure cross-terms were also checked and are negligible:
the horizontal pressure resultant p̄ w′ (≤ 2.5 N/m² vs axial-force gradient scales ~10⁵ N/m²)
and the modification of N_θ by the interface traction (σ_yy = −p̄ instead of a free face shifts
N by ν p̄ d/(1−ν²) ≈ 0.12 N/m, i.e. 4×10⁻⁶ of N₀). Superposing the three load systems is exact
at this (frozen-force linear) model level; no thermal effect is counted twice.

## 7. Validity conditions of the adopted (frozen-force) model

1. **δ₁ = ½⟨w′²⟩/e₀ ≪ 1** (arc stretching small against the blocked thermal strain). Baseline:
   0.061. This is the expansion parameter; the w_max error ≈ δ₁·λ₀/(π²−λ₀)-type factor, measured
   2.3 % at baseline.
2. **N₀/N_cr ≲ 0.4** keeps the deflection error ≤ ≈8 %; within the admissible envelope
   (A-3/A-6 bind at ≈0.31–0.36) the error is ≤ ≈5 %, one-sided (conservative). The specification's
   escalation trigger at N/N_cr > 0.5 coincides with the onset of rapid error growth — the
   reduced model is used exactly where it is valid.
3. Near or past the buckling ceiling (N₀/N_cr → 0.5+ with large permitted deflections), the
   N–w compatibility must be iterated (one fixed-point sweep suffices away from π²) — this is the
   recorded monolithic/consistent-vK escalation path, not a new model.
4. Small strain and moderate rotation (von Kármán hypotheses) hold throughout the envelope
   (slopes ≤ 0.03 rad at baseline; surface strains ≤ 5.4×10⁻³).

## 8. Conclusion

1. The adopted D_s w⁗ + N_θ^c w″ = 0 is the **reduced (frozen-force) von Kármán beam–column
   equation — the exact linearization about the prescribed blocked-state prestress**; its
   baseline evaluation is verified value-by-value.
2. The axial compatibility relation is derived in §3; the force-relaxation estimate is confirmed
   and refined (6.1 % first iterate; 5.9 % self-consistent).
3. Against the fully consistent von Kármán solution, the adopted model **overpredicts w_max by
   2.3 %** at baseline (0.438 → 0.428 H₀) and ≤ ≈5 % anywhere inside the admissible envelope;
   every stress and strain figure shifts by ≤ 8 % in the safe direction; **the buckling margin
   M_b = 3.64 is exact** (the relaxation vanishes at onset). No downstream conclusion of the
   formulation changes.
4. The boundary-condition set (transverse pin + two-sided axial blocking + moment-free ends) and
   the thermal decomposition (mean → force, gradient → curvature, pressure → omitted 0.06 %
   load) are mutually consistent, with no double counting.

> **Verdict: Existing beam–column model justified with an explicit limitation** — namely that
> the frozen-force reduction overestimates w_max by ≈2 % at the baseline (conservative; exact
> consistent value 2.14×10⁻⁴ m = 0.428 H₀) with error ≤ ≈5 % inside the admissible envelope
> (N₀/N_cr ≤ 0.36), degrading beyond N₀/N_cr ≈ 0.5 where the specification already escalates to
> the consistent (iterated/mesh-coupled) treatment. No LaTeX change and no new build are
> required; if a future revision touches these numbers anyway, quoting w_max = 2.19×10⁻⁴ m as an
> upper bound with the consistent value 2.14×10⁻⁴ m in the cell A9 register would make the
> one-sidedness explicit. This is optional, not a correction.

*Independent checks performed this audit: symbolic verification of the shape antiderivative;
fixed-point solution of the coupled compatibility relation (converged to 10⁻¹⁵); reproduction of
all quoted Chapter-4 quantities from the documented inputs (ν = 0.40, q″ = 5×10³ W/m²); error
scan across the operating range; dimensional checks — D_s w⁗ [N/m²], N w″ [N/m²], μ² = N/D_s
[m⁻²], EA_eff⟨w′²⟩ [N/m], β and δ₁ dimensionless, N_cr = π²D_s/L² [N/m].*
