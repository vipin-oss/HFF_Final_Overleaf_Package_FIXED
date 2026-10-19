# Stage 15 — Master issue ledger

**Tree:** `arena/c875f9b3-hff-final-overleaf-package-fix`
**Baseline at start of Stage 15:** `9066c3b`
**Correction commit:** `e8ef0d7`
**Register:** Appendix B of the manuscript now carries D-1 … D-25.

Status vocabulary. `CLOSED` — corrected in source at `e8ef0d7` and re-verified against source.
`CLOSED (no action)` — verified correct, no change needed. `OPEN-AD` — author decision required;
work that does not depend on it has proceeded. `OPEN-TECH` — technical blocker not yet resolvable
in this environment. `CARRIED` — accepted limitation, correctly disclosed in the manuscript.

Priority tiers: **RB** = required before coding; **CC** = claim-check (verify, usually no edit);
**RU** = requires author resolution; **B** = blocker.

---

## 1. Required-before-coding (RB)

| ID | Location | Defect | Action taken | Status |
|---|---|---|---|---|
| RB-01 | `ch02:129–133` | `w = −d₂`, "positive into the channel" | `w = +d₂`, "away from the channel" | **CLOSED** |
| RB-02 | `appendix` glossary | same definition, second wording | aligned | **CLOSED** |
| RB-03 | `ch02:27` figure caption | "positive into the channel" | "away from the channel" | **CLOSED** |
| RB-04 | `ch02:131` | "bows into the channel" | "bows away"; `κ=−w''` unchanged | **CLOSED** |
| RB-05 | `ch03:140` | `D_s w'''' = −p` — sole A-consistent equation | `D_s w'''' = +p` | **CLOSED** |
| RB-06 | `ch03:144` | "`w` measured positive into the channel" | "away from" | **CLOSED** |
| RB-07 | `ch04` pin relation | phrase only | aligned; equation unchanged | **CLOSED** |
| RB-08 | `ch04:190–192` | `M` unnamed, equals `−M_phys` | declared sagging-positive, `M = −∫σ_xx y dy` | **CLOSED** |
| RB-09 | `ch04:296` | load "opposing" the bow | "acting in the same sense" | **CLOSED** |
| RB-10 | `ch04:309–310` | "thermally **rather than** hydraulically driven" | ratio of co-directional contributions | **CLOSED** |
| RB-11 | `ch01:10` | "bows toward the interior" | "away from the interior" | **CLOSED** |
| RB-12 | `main.tex:54` | "deflects **into** the flow passage" | "away from"; "widened passage" | **CLOSED** |
| RB-13 | `fig_geometry.tex:18–22, 36–38` | bow drawn 6 pt **into** the fluid; outer face straight; arrow 11 pt against a 6 pt bow | bow reversed, **both faces** displaced by the same amount, flux arrows lifted clear, `w` arrow spans the drawn bow | **CLOSED**; conformal redraw to a real measured profile remains **OPEN-AD** under RU-01 |
| RB-14 | `ch09` V-C2, V-C3 | expectations carried no sign | `κ > 0` (hot face convex); `w_max > 0` away from the channel | **CLOSED** |
| RB-15 | six sites | `½⟨w'²⟩ = 1.8×10⁻⁴` not reproducible | `1.39×10⁻⁴`; recomputed `1.388009729196×10⁻⁴` | **CLOSED** |
| RB-16 | `appendix:130` | row printed `2.4×10³` against a closed form that evaluates to `1.714×10³` (+40.00 %) | row re-expressed as `w_max/w_p` | **CLOSED** |
| RB-17 | `ch04:299–308`, `ch06:83` | sentence named `w_th` of `eq:beamcolbase` but equated `Γ_p` to the *linear* closed form | `Γ_p = w_max/w_p` with the linear limit and the amplification `1.389654` shown explicitly | **CLOSED** |

**RB-15 provenance (closes B-11).** The error is isolated: it is a single transcription, propagating
verbatim through six sites, of the value that a *different* formula would give. The printed
first-iterate relaxation of `6.1 %` is exactly `1.388×10⁻⁴ / e₀ = 6.1446 %`, whereas `1.8×10⁻⁴`
would give `7.968 %`. So `1.8×10⁻⁴` was never a later revision of the model — it is inconsistent
with a number in the same paragraph. B-11 is therefore **CLOSED**, not merely displaced.

## 2. Claim-checks (CC) — verified against source, no edit

| ID | Verdict |
|---|---|
| CC-01 | `κ_th>0 ⇒ w=κ_th x(L−x)/2 ≥ 0` — true under B; became correct with RB-04. **CLOSED** |
| CC-02 | "fixed so that the bowing is positive" — true under B. **CLOSED** |
| CC-03 | clamped strip: `D_s κ_th = 13.500000 N·m` — correct. **CLOSED (no action)** |
| CC-04 | `2.19×10⁻⁴`, `0.438 H₀`, `0.315` — all reproduced to 3 s.f. **CLOSED (no action)** |
| CC-05 | `(κ_geo−κ_th)d/2 = 9.8881×10⁻⁴` — correct under B; **must not be flipped**. Explains B-3 in closed form (§5 of `02_…`). **CLOSED** |
| CC-06 | `M = −6.356655 N·m`, `σ_bend = 4.237770 MPa`, `9.000 MPa` restrained scale — reproduced. **CLOSED (no action)** |
| CC-07 | `(1+ν)Σ_κΛ²/8 = 0.315` — exact. **CLOSED (no action)** |
| CC-08 | `ch07` magnitudes — correct; only the arc cell changed. **CLOSED** |
| CC-09 | appendix A3, A9 — correct once the arc term was fixed; **the arc formula `κ_geo²L²/24` is correct** (−0.62 %), not an error. **CLOSED** |
| CC-10 | `fig_signs.tex` has no `w`/`κ` content; is 20 lines, not 17. **CLOSED (no action)** |
| CC-11 | `ch10`, `ch11` direction-neutral. **CLOSED (no action)** |
| CC-12 | `eq:nupdate` carries `⟨w'²⟩` only — sign-invariant. **CLOSED (no action)** |
| CC-13 | slope `0.03` → `0.027` rad (precision drift, `0.027516`). **CLOSED** |
| CC-14 | "pressure dominates by about two orders": `84/0.6 = 140`. **CLOSED (no action)** |

## 3. Author-resolution items (RU)

| ID | Question | Status |
|---|---|---|
| RU-01 | Is the strip's outer face **free**, **backed by a vented cavity**, or **in contact** with the rigid casing? No standoff distance is stated anywhere in the source. Under the adopted convention the strip bows **towards** the casing by `0.4377 H₀ = 0.219 mm`, so this is now load-bearing. Three branches with distinct consequences are enumerated in `02_derivation_and_sign_convention.md` §4. | **OPEN-AD** |
| RU-02 | Report the sagging-positive `M` or the physical first moment `M_phys = −M`? Both vanish at the pins, so **no result changes**; only the mid-span sign convention is at stake. Disposition taken: keep `M` as printed and state `M_phys = −M` once (RB-08), so no reader can mis-sign it. | **CLOSED by disclosure** (author may still prefer the opposite label) |
| RU-03 | Should the mid-span passage height be stated? No gap sentence exists in the source. Under the adopted convention the mid-span height is `H₀ + w_max = 1.4377 H₀` (i.e. **the passage widens**), the mirror value being `0.5623 H₀`. | **OPEN-AD**, coupled to RU-01 |

## 4. Blockers (B)

| ID | Blocker | Status |
|---|---|---|
| B-1 | Function spaces and interface traces undefined (`ch08`) | **CLOSED** — `V_g, Q, S_f, V_s, S_s` defined with `H^{1/2}(Γ_if)` traces |
| B-2 | Pressure gauge unenforced | **CLOSED** — outlet mean-pressure datum stated and its algebraic form given |
| B-3 | Geometric stiffness missing from `eq:weaks` | **CLOSED** — `−∫ N_θ^c ∂_X d₂ ∂_X φ₂ dX` added, reduction to `eq:beamcol` stated |
| B-4 | Thermal data-flow contradiction | **CLOSED** — restated as a shared interface unknown carrying the flux balance; `ch08:108` governs and is now consistent with `ch05` |
| B-5 | Monolithic cancellation vs staggered iteration | **CLOSED** — assembled-system cancellation distinguished from its limit-wise recovery; V-B flux-jump norm cited as acceptance criterion |
| B-6 | SUPG `τ` unspecified | **CLOSED** — `τ_K` with `Pe_K`, units, and the `Pe≫1` limit written out as `eq:supg` |
| B-7 | Rigid casing / clearance / contact | **OPEN-AD** — same item as RU-01 |
| B-8 | LaTeX build of current source | **OPEN-TECH** — no engine in this environment (see `08_…`) |
| B-9 | Audit-artefact provenance | **CLOSED** — Stage 15 artefacts committed under `audit_stage15/`; earlier Stage 11–14 reports remain outside the tree and are cited as external, not claimed as present |
| B-10 | Reference/deformed interface `O(ε)` | **CLOSED (verified)** — the stated `5.4×10⁻³` is the total mechanical surface strain `e₀ + κ_geo d/2 = 5.347713×10⁻³`, recomputed. The disclosure is correct and appropriately placed |
| B-11 | Is the `1.8×10⁻⁴` error isolated? | **CLOSED** — see RB-15 provenance |

## 5. Tally

| Tier | Count | Closed | Open |
|---|---|---|---|
| RB | 17 | 17 | 0 (RB-13 has an author-gated remainder) |
| CC | 14 | 14 | 0 |
| RU | 3 | 1 (by disclosure) | 2 |
| B | 11 | 8 | 3 (B-7 = RU-01, B-8 toolchain) |

Two open items are **not** technical defects: RU-01/B-7 and RU-03 are unstated physical
configuration, and B-8 is the absence of a compiler. No item was closed by moving it into a report;
each `CLOSED` above was rechecked against the tree at `e8ef0d7`.
