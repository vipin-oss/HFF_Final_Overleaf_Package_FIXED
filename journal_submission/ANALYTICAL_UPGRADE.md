# Analytical upgrade — what is proved, what is computed, what is verified

Date: 21 October 2026 (v4). The paper derives the model rather than postulating it, closes as
much of it as possible in closed form, **separates its closed forms from the shapes they are
fed**, and attributes the residual of every comparison to a named mechanism rather than to
"two-dimensional effects".

## 1. Mathematical content

| Where | Content |
|---|---|
| §2.3 | Two-field functional `Π[u₀,w]` obtained from the three-dimensional virtual work; the beam–column equation and the axial-compatibility condition are derived as its two Euler–Lagrange equations. Three discarded terms bounded: transverse shear 4.0 %, finite strain 1.4×10⁻⁴, stress recovery (measured in §5.10). |
| §5.1.1 | Closed-form deflection for constant curvature and membrane force, with the pressure particular integral; Euler load `N_cr=π²D_s/L²` and critical temperature as limits. |
| §5.1.2 | **Theorem** — the axial-compatibility map `𝓕(N)=N_θ−c⟨w′²⟩` is a contraction for `N_θ<N_cr/3`, with rate `q=2N_θ/(N_cr−N_θ)=0.757` and `|N_k−N*| ≤ q^k/(1−q)|N_1−N_0|`. Proof: Appendix D.1. |
| §5.1.3 | **Theorem** — hydraulic resistance of the bowed passage, `Δp=Δp₀ ₂F₁(3,½;1;a)`, with `Δp₀[1+3a/2+9a²/4+25a³/8+525a⁴/128+…]`. Proof by the Euler beta integral (D.2). *(The v3 draft printed the coefficients 27/8 and 75/16; they are 9/4 and 25/8, as the Taylor series of `₂F₁` requires and as `2F1(0.2)=1.4237464` confirms.)* |
| §5.1.4 | **Theorem (self-similar reduction)** — for any admissible `ŵ`, `Π(a;ŵ)=∫₀¹dξ/(1−aŵ)³ = Σ C_k a^k`, `C_k=(k+1)(k+2)c_k/2`, `c_k=⟨ŵ^k⟩`; radius exactly 1 (D.4). **Corollary** — `ŵ=sin²πξ` gives `c_k=C(2k,k)/4^k` and recovers Theorem 5.1.3. **Corollary** — a priori truncation bound `0 ≤ Π−S_N ≤ 1/(1−a)³ − Σ_{k<N}(k+1)(k+2)a^k/2` (D.5). **Lemma** — shape stability `|Π(ŵ₁)−Π(ŵ₂)| ≤ 3a(1−a)⁻⁴‖ŵ₁−ŵ₂‖∞` (D.5). |
| §5.1.5 | **Theorem (thermal closure)** — Sturm–Liouville eigenfunction solution of the thermal entry problem (`Nu→70/13=5.3846`), followed by an exact statement for the wall: with uniform outer flux, arbitrary interface shape and arbitrary interface temperature, the horizontal mean `Θ(y)` is affine with slope `−q″/k_s` (D.6). Consequences: exact 1-D closure in the flat limit; the **deformed** closure `θ̄=θ_i+q″[d+w]/2k_s`, whose deficit against the reference-thickness closure is exactly `q″w/2k_s`, i.e. the relative amount `w/d`. |
| §5.1.6 | Five particular cases with their closed-form limits. |
| §5.2 | Comparison with the coupled finite-element solution, resolved into **law / shape / truncation** for the hydraulics and **path / mid-surface convention** for the wall temperature.
| §5.3 | **Collapse across the parameter space.** One shape integral, evaluated once on the design-point profile and containing no fitted coefficient, reproduces the strip resistance of all 19 distinct parameter sets of the five sweeps to 0.40 % (mean 0.14 %); the same runs depart from the `sin²` law by up to 19.7 %. `Nu/Nu_Graetz ≈ (H₀/H)^p`, `p = 0.79` (`R² = 0.81`), bracketed by ½ and 1. Table `tab:collapse`, Figure 16. |
| §5.3 | **Certificate, not assertion.** |Π(a;ŵ) − Π(a;ŵ₀)| ≤ ∫₀¹ 3a(1−a·max(ŵ,ŵ₀))⁻⁴|ŵ−ŵ₀| dξ, evaluated on every run from the two profiles alone: bound ≤ 1.17 %, observed ≤ 0.40 %, bound sharp to 0.5 %. Substituting each run's own bow reproduces its coupled Δp to 0.085 %. Table `tab:certificate`. |
| §5.7.1 | **Neumann-wall benchmark** — the one test whose answer needs no modelling assumption: `θ̄=q″d/2k_s=30 K`, `Γ=q″/k_s=20 000 K/m`, `Q′=150 W/m`, reproduced to round-off. |
| Appendix D | Proofs D.1–D.6. |

## 2. Verification

| Check | Result |
|---|---|
| `Nu_∞ = 2/f(1) = 70/13` | 5.38461 against the classical 5.385 |
| Eigenvalues | `λ₁=3.6956`, `λ₂=7.0010`, `λ₃=10.2841`; `ψ₁(1)=−1.506` |
| Hypergeometric vs its series | coefficients 1, 3/2, 9/4, 25/8; `₂F₁(0.2)=1.4237464` |
| Resistance, quadrature of the law with the computed shape | −0.05 % … +0.04 % over `a=0.067…0.4415` (7 sweep points; |error| ≤ 0.18 %) |
| Resistance, series truncated at `O(a³)` | −0.06 % at `a=0.067` → −14.74 % at `a=0.4415` |
| Resistance, `sin²` shape (frozen-shape error) | −15.08 % at `a=0.4415` |
| Shape moments of the computed bow | `c=(1, 0.6588, 0.5244, 0.4483)`; `C=(1, 1.976, 3.147, 4.483)` against `(1, 1.5, 2.25, 3.125)` for `sin²` |
| A priori truncation bound | 0.0017 at `a=0.1`, 0.033 at `a=0.2`, 1.39 at `a=0.4415` (usable below `a≈0.2` only) |
| `w_max`, closed form, frozen force | 2.1886×10⁻⁴ m against 2.2074×10⁻⁴ m (−0.85 %) |
| Wall rise, reference thickness `θ_i+q″d/2k_s` | 31.695 K against an exact thickness average of 33.140 K (**−4.36 %**) |
| Wall rise, deformed thickness `θ_i+q″(d+w)/2k_s` | 33.137 K against 33.140 K (**−0.0075 %**) |
| Least-squares mid-surface value used in the loop | 34.259 K (**+3.38 %** of the average; conservative for `N_θ`) |
| Path term `q″w/2k_s` / curvature residual | 1.442 K / 1.121 K; `w_max/d = 7.36 %` |
| 1-D Neumann benchmark | `θ̄=30.000000 K`, `Γ=20 000.00 K/m`, `Q′=150.000 W/m`, residual 5.2×10⁻¹⁴ |
| Collapse over the five sweeps (19 distinct parameter sets) | master integral: max 0.40 %, mean 0.14 %; `sin²` law: max 19.7 % (strip) / 15.1 % (total Δp); truncated series: max 15.2 % |
| Contraction | bound `q=0.757<1`; measured `|𝓕′|=1.6×10⁻⁵` |
| Test suite | **45 tests pass** (`test_asymptotics.py` 7, `test_thermal_path.py` 5, `test_collapse.py` 4 new) |

## 3. Reproduction

```bash
cd program
./.venv/bin/python tools/asymptotics_report.py     # outputs/data/asymptotics.json
./.venv/bin/python tools/asymptotic_figures.py     # fig13, fig14, fig15 + two tables
./.venv/bin/python tools/thermal_path_report.py    # outputs/data/thermal_path.json + table
./.venv/bin/python -m pytest -q                    # 41 passed
```

`tables/table_asymptotics.tex`, `table_pressure_series.tex`, `table_thermal_path.tex` and
`fig13`–`fig15` are generated from the saved numerical output; no number in §5 is typed by hand.

## 4. What is still not claimed

* The Graetz series is the **straight-passage** reference, not a prediction for the bowed passage;
  §5.2 says so and quotes the fitted exponent with its bracket.
* The deformed-wall closure `θ̄=θ_i+q″(d+w)/2k_s` is exact in the strip mean (0.0075 %) and carries
  an `O(h²θ_i″)` curvature residual that reaches 1.5 K at the inlet column; it is stated as a
  closure with a measured residual, not as an identity.
* Transverse shear (4 %) and the plane-strain idealisation are bounded, not eliminated.
* The collapse is verified over the five sweeps that exist; it is a statement about this
  geometry family (uniform curvature, pinned ends), not a proof for arbitrary load distributions.
* The mid-surface value of `θ̄` used inside the coupling exceeds the thickness average by 3.4 %.
  The difference is quantified and carried as a conservative margin; the loop itself was not
  re-run with the averaged quantity, and the paper says which of the two it reports.
* No PDF is compiled here (no TeX engine in the environment). Validation is structural:
  `python3 tools/check_tex.py` reports 180 labels, 132 references, 55 citations against 55 keys,
  16 figures and 19 tables.
