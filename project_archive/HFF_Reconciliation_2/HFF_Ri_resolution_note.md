# Resolution note: Richardson number and the H₀ ↔ D_h length basis

**Status:** resolved (second reconciliation pass). Recorded as D-8/D-14 in the document register
and as R-02 in `HFF_discrepancy_reconciliation.csv`.

## 1. The defect chain

| Stage | Value printed | Definition actually evaluated | Defect |
|---|---|---|---|
| Original draft | Ri = 0.43 | Gr(H₀)/Re(D_h)² with Gr mis-transcribed as 1.1×10³ (true 1.07) | mixed length basis **and** powers-of-ten error: 1.07/2500 = 4.3×10⁻⁴, not 0.43 |
| First audit | Ri = 4.3×10⁻⁴ | same mixed division, arithmetic corrected | arithmetic right, definition still mixes bases: Gr built on H₀ divided by Re built on D_h = 2H₀ |
| Final (adopted) | **Ri = 1.7×10⁻³** | Gr(H₀)/Re(H₀)² | none — single length basis, stated on the group |

## 2. What a "length basis" change means: two distinct cases

A basis change is ambiguous until one states what happens to the temperature difference. Two
well-defined cases exist and must not be mixed (the previous revision of this note mixed them,
writing ΔT*(ℓ) while asserting ℓ¹ scaling).

**Case A — same physical ΔT held fixed, only the length ℓ changes.**
Gr(ℓ) = gβΔT ℓ³/ν² ∝ ℓ³, Re(ℓ) = Uℓ/ν ⟹ Re² ∝ ℓ², so

  Ri(ℓ) = Gr(ℓ)/Re(ℓ)² = gβΔT ℓ/U² **∝ ℓ¹**.

Moving H₀ → D_h = 2H₀ at fixed ΔT **doubles** Ri.

**Case B — the temperature scale is redefined with the length, ΔT*(ℓ) = q″ℓ/k_f.**
Substituting the per-length scale:

  Ri(ℓ) = gβΔT*(ℓ)ℓ/U² = (gβq″/k_f) ℓ²/U² **∝ ℓ²**.

Moving H₀ → D_h then **quadruples** Ri (Gr picks up ℓ⁴ = ×16, Re² only ℓ² = ×4).

Any statement of a "D_h-basis Ri" must say which case it means; the two differ by a factor 2 at
D_h = 2H₀ (and coincide only at the length where the two ΔT conventions agree).

## 3. Convention adopted by the formulation, and the reported values

The formulation carries one fixed temperature scale throughout its dimensionless groups:
ΔT* = q″H₀/k_f = 4.17 K — the same ΔT* appears in Gr and in Br. For the fixed baseline operating
point this is a *fixed physical ΔT*, so a basis re-expression of Ri follows **Case A**:

* **H₀ basis (adopted):** Gr = 1.07, Re(H₀) = ρUH₀/μ = 25, Ri = 1.07/625 = **1.7×10⁻³**
  (closed form Ri = gβΔT*H₀/U², document eq. 6.3).
* **D_h basis (Case A: same ΔT* = 4.17 K, ℓ = D_h):** Gr(D_h) = 8×1.07 = 8.6, Re(D_h) = 50,
  Ri = 8.6/2500 = **3.4×10⁻³** — exactly 2× the H₀ value, the factor being D_h/H₀.
* *(For completeness, the Case-B variant at D_h would use ΔT*(D_h) = q″D_h/k_f = 8.34 K, giving
  Gr = 17.1 and Ri = 17.1/2500 = 6.9×10⁻³.)* All three values are ≪ 1 by two to three orders of
  magnitude; the buoyancy disposition is insensitive to the choice, and the document quotes the
  Case-A pair, consistent with its fixed ΔT*.

Relation to the historical defects: the mixed division Gr(H₀)/Re(D_h)² = 1.07/2500 =
4.3×10⁻⁴ equals Ri(H₀)/(D_h/H₀)², i.e. a factor 4 *below* the true H₀ value — it corresponds to
no consistent basis (Case A gives ×2, Case B gives ×4). The original 0.43 was that same mixed
division with an additional ×10³ transcription error.

## 4. Consequence for the model

At Ri = O(10⁻³) the buoyant forcing is three orders of magnitude below inertial: the
constant-density equations are adopted on the standard order-of-magnitude argument, without
recourse to stratification stability. Provisions retained: (i) a dormant Boussinesq term in the
weak form; (ii) a regime guard — any parameter point with Ri > 10⁻² re-opens the question and
requires a Boussinesq-enabled case; (iii) Ri recomputed from computed fields in every reported
run. The Draskic et al. (2025) stratification reference is retained as the marker of the opposite
limit (Ri = O(10)); it no longer carries the argument. The previous audit's mandatory B-1
Boussinesq check at the baseline is thereby closed; the item survives only as the regime guard.

## 5. Acceptance rationale (why neither prior value was adopted)

* 0.43 (original): rejected — the definition mixes bases and the arithmetic mis-transcribes
  powers of ten; the value would place the problem at the mixed-convection threshold, reversing
  the modelling disposition.
* 4.3×10⁻⁴ (first audit): arithmetically correct for the (defective) mixed definition and
  correctly implies excludability, but the definition itself is dimensionally inconsistent for a
  similarity group; adopting it would have propagated a mixed-basis definition into the
  parameter study.
* 1.7×10⁻³ (adopted): single-basis, closed-form definition; both conventions documented; disposition
  (exclusion by three orders) insensitive to the choice between the two consistent values.
