# Analytical upgrade — what is proved, what is computed, what is verified

Date: 21 October 2026. Supersedes the "computational only" character of v2/v3: the paper now
derives the model rather than postulating it, and closes as much of it as possible in closed
form.

## 1. New mathematical content

| Where | Content |
|---|---|
| §2.3 | Two-field functional `Π[u₀,w]` obtained from the three-dimensional virtual work; the beam–column equation and the axial-compatibility condition are derived as its two Euler–Lagrange equations (previously they were asserted). Three discarded terms bounded: transverse shear 4.0 %, finite strain 1.4×10⁻⁴, stress recovery (error measured in §5.10). |
| §4.1.1 | Closed-form deflection for constant curvature and membrane force, with the pressure particular integral; Euler load and critical temperature as limits. |
| §4.1.2 | **Theorem 1** — the axial-compatibility map `F(N)=N_θ−c⟨w′²⟩` is a contraction for `N_θ<N_cr/3`, with explicit rate `q=2N_θ/(N_cr−N_θ)=0.757` and the geometric error bound `|N_k−N*| ≤ q^k/(1−q)|N_1−N_0|`. Proof in Appendix D.1. |
| §4.1.3 | **Theorem 2** — the hydraulic resistance of the bowed passage is `Δp = Δp₀ ₂F₁(3,½;1;a)`, with its power series `1 + 3a/2 + 27a²/8 + 75a³/16 + …`; proof by the Euler beta integral (Appendix D.2), plus the weak-inertia balance showing the inertial term is 1.2×10⁻³ Pa. |
| §4.1.4 | **Theorem 3** — Sturm–Liouville eigenfunction solution of the thermal-entry problem, `ψ″+λ²·6Y(1−Y)ψ=0` with Neumann data, coefficients `A_n=−⟨f,ψ_n⟩_w`, and `Nu(X)→70/13`, the classical 5.385. Eigenvalues `λ₁=3.6956`, `λ₂=7.0010`, `λ₃=10.2841`. |
| §4.1.5 | Five particular cases with their closed-form limits. |
| §5.2 | Comparison of the semi-analytical model with the coupled finite-element solution; scaling law `Nu/Nu_Graetz ≈ (H₀/H)^p`, `p = 0.79 ± 0.03` (`R² = 0.81`), bracketed by the two limiting exponents ½ and 1. |
| Appendix D | Proofs of Theorems 1–3. |

## 2. Verification of the new content

| Check | Result |
|---|---|
| `Nu_∞ = 2/f(1) = 70/13` | 5.38461 against the classical 5.385 |
| Eigenvalue problem | `λ₁ = 3.6956`; Neumann condition satisfied to 5×10⁻³ |
| Hypergeometric vs its series | first Taylor coefficient 1.5 (exact), `₂F₁(0.2) = 1.4237464` |
| Δp, closed form with the computed shape | 314.604 Pa against 314.508 Pa computed (**+0.03 %**) |
| Δp, closed form with `sin²` shape | −15.08 % at `a = 0.441`; error law in Figure 14b |
| `w_max`, closed form, frozen force | 2.1886×10⁻⁴ m against 2.2074×10⁻⁴ m (−0.85 %) |
| `θ̄`, series + one-dimensional wall | 32.10 K against 34.26 K (−6.3 %, attributed to two-dimensional wall conduction) |
| Contraction | bound `q = 0.757 < 1`; measured `|F′| = 1.6×10⁻⁵` |
| Test suite | 36 tests pass (`program/tests/test_asymptotics.py` adds 6) |

## 3. Reproduction

```bash
cd program
./.venv/bin/python tools/asymptotics_report.py      # writes outputs/data/asymptotics.json
./.venv/bin/python tools/asymptotic_figures.py      # writes fig13, fig14 and the comparison table
./.venv/bin/python -m pytest -q                     # 36 passed
```

The comparison table `tables/table_asymptotics.tex` and both figures are generated from
`outputs/data/asymptotics.json` and the saved finite-element results; no number in §5.2 is
typed by hand.

## 4. What is still not claimed

* The Graetz series is the **straight-passage** reference; it is not a prediction for the bowed
  passage, and §5.2 says so explicitly. The measured excess is reported with its fitted
  exponent and its bracket, not presented as a derived law.
* Transverse shear is excluded from the structural model; its 4 % estimate is stated in
  §2.3, §5.2 and §7 rather than hidden.
* The `θ̄` gap of 6.3 % is left visible: the reduced model cannot close it without abandoning
  its one-dimensional structure.
* No PDF was compiled here (no TeX engine in the environment). Validation is structural:
  `python3 tools/check_tex.py` reports 157 labels, 112 references, 0 duplicate, 0 unresolved,
  55 citations against 55 keys, 14 figures and 10 table fragments resolved.
