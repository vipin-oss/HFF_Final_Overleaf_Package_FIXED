# Request for a fresh independent audit (Stage 16)

**Branch:** `arena/c875f9b3-hff-final-overleaf-package-fix`
**Commit under audit:** `8c3e716` (implementation `388688a`, hash record `0bc2888`)
**Baseline audited previously:** `7c9749f` — thank you; every finding below refers to it.

Please audit the **corrected sources**, not this summary. Nothing here is offered as evidence of
closure; the claims below are exactly what needs independent checking.

## 1. Please decide closure on these, against the source

| ID | Claim to check | Where to look | What would show it is still open |
|---|---|---|---|
| I-01 | The support is now a pin: `d₂=0` on the full end edge, `⟨d₁⟩=0` as an edge mean, zero moment natural; the clamp is explicitly excluded | `ch02` A9, `ch05` B7, `ch08` `V_s` | any remaining `d₁=d₂=0`, or a sentence implying a clamped end |
| I-03 | `−(N_θ^c/d)∂_X d₂` is dimensionally a stress and the `1/d` argument is correct | `ch08` `eq:weaks` and the paragraph after it | consistency of the 1-D reduction with `eq:beamcol` |
| I-04 | No gauge freedom exists (`b(v,1) ≠ 0`), the constraint is deleted, `B2` no longer reads as an imposed pressure datum | `ch08` spaces paragraph, `ch05` B2 | whether the pressure level is claimed twice, once as an output and once as a datum |
| I-05/I-06 | `eq:supgwf` is a correct SUPG statement and the `h_K→h_K/p` caveat is right | `ch08` | whether the residual/`τ` definitions are consistent with a `P2` space |
| I-08 | `13.0 MPa` (self-consistent) and `13.9 MPa` (frozen, conservative) are two declared states, `13.6` withdrawn | `ch04`, `ch07`, `appendix` | any place where the two are used interchangeably |
| I-09 | `3.25×10⁻³` mechanical and `5.35×10⁻³` envelope are the right quantities to distinguish | `ch02`, `ch04`, `ch07`, `ch08`, `appendix` | whether the `O(ε)` interface argument should use one or the other |
| I-11 | `Γ_p` is labelled mixed and a like-for-like value is added | `ch04` D-29 | whether `w_p(N_θ^c)=1.27×10⁻⁷ m` uses the same `N` as its label |
| I-13/I-12 | The ZIP exists under the documented name, with a manifest; the PDF is declared stale | `README.md`, `audit_stage15/package_manifest.txt` | whether any claim implies the PDF matches the sources |
| I-15 | Figure labels no longer collide | `figures/fig_geometry.tex` | — (visual; no renderer available here) |

## 2. Please attack the tests (I-07)

`audit_stage15/regression.py` v2 parses inputs *and* printed values from the sources and recomputes.
`audit_stage15/mutation_test.py` runs six mutants in isolated copies. My results: 56/56 pass,
baseline passes, all six caught. Please try to break that:

- a mutation that still passes (a vacuous check);
- a check whose anchor can silently fail to match (a mutation that changes what is parsed);
- any printed value the suite does **not** cover, especially in `ch06`, `ch09`, `ch10`, `ch11`;
- whether the suite's "no reversed-bow phrasing" list is broad enough.

## 3. Known limitations, stated rather than hidden

- No TeX engine in the environment: `main.pdf` **is not rebuilt** and predates these corrections.
  `regression.py` §7 reports this and asserts nothing.
- No figure renderer: the figure rewrite is verified structurally only.
- The physics questions below remain open and are **not** covered by any test: RU-01 casing
  clearance, vent vs sealed cavity, heater mounting, contact law, point-pin vs rigid end face,
  `Γ_p` headline definition, and the `1.4377 H₀` mid-span check (RU-03).

## 4. What I am not claiming

I am not claiming the audit items are closed. I am claiming they are implemented as described and
guarded by tests that fail when reverted. The coupled production solver remains **NOT READY**.
