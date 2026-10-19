# Pre-Coding Checklist (ordered)
**Status derived from `HFF_independent_audit.md` (2026-10-18).** Complete items in order; a check is only "done" when its evidence artefact exists.

## Gate 0 — before ANY coding
- [ ] **0.1** Read correction table C-1…C-12 of the audit; acknowledge ownership of each item.

## Gate 1 — fluid solver (V-A / V-B) — GO after these
- [ ] **1.1** Code comment + output header convention fixed: Darcy fRe = 96 (Fanning 24); Re basis (Re_H vs Re_Dh = 2Re_H) printed on every plot/table. (C-7)
- [ ] **1.2** Boussinesq body-force term implemented but left **deactivated** (one-line weak-form term; needed later for C-8 check run).
- [ ] **1.3** V-A pass recorded: velocity profile L² error and fRe on 3 nested meshes.
- [ ] **1.4** V-B pass recorded: Nu → 7.541 / 8.235 / 5.385 for the three slit configurations (H1 last, since V-D conjugate uses it); developing Nu(x) curve compared qualitatively to Graetz-family shape.

## Gate 2 — solid/post-processor (V-C) — GO after these
- [ ] **2.1** Unit-test expectation table **corrected** per C-2: restrained strip σ_xx = −Eαθ/(1−ν), σ_m = −3Kαθ; **free uniform strip σ_m = −Eαθ/3 (not 0)**; free gradient strip κ = (1+ν)αΔT_t/d; pinned–pinned strip w_max = κ_thL²/8 (specimen L/d = 25).
- [ ] **2.2** Runtime assertion implemented: σ_m from stress form (A) equals K(e−3αθ) form (B) at all Gauss points.
- [ ] **2.3** V-C1–V-C3 passes recorded with error norms.

## Gate 3 — coupled-model authorisation (all six required)
- [ ] **3.1** (C-3, C-4, C-10) One-page retable memo: pinned–pinned ΔT_cr = π²d²/(12α(1+ν)L²); Γ_p = 48κ_thD_s/(p̄L²) tabulated at every anchor; every anchor shows M_b ≥ 2 **and** Γ_p ≥ 5 (reference: auditor anchor d = 3 mm, q″ = 5×10³ W/m²).
- [ ] **3.2** (C-8) Boussinesq check run executed at the weakest-Ri anchor; Nu difference documented and disposition (include/exclude body force) decided with numbers, not prose.
- [ ] **3.3** (C-5) V-E replacement fixed: steady compliant-channel bulge benchmark dataset identified (geometry, BCs, tabulated deflections); Turek–Hron reassigned to future transient gate only.
- [ ] **3.4** (C-1, C-6) Primary benchmark digits procured (Shah & London tables; V-D conjugate data series) **and** property datasheet table finalised (water β_f; PEEK E, α, k_s, ρ_s, c_s bands; T_ref).
- [ ] **3.5** (C-11) Scopus/WoS novelty pass completed; gap statement re-baselined; no "first-ever" wording anywhere.
- [ ] **3.6** (C-12) Independent replication platform committed (FEniCS minimally) and one anchor case chosen for the replication overlay.

## Blocking rule
No coupled (fluid–thermal–structural) production run may be reported until **all of Gate 3** is complete. A run that violates an admissibility bound (A-1…A-5, with the corrected ΔT_cr formula) must be re-labelled or discarded, never post-hoc justified.
