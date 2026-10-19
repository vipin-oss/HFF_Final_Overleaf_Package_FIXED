# Source-to-PDF consistency report — Stage 4 (final package)

**Build:** pdfLaTeX (TeX Live 2026 engine, Overleaf-compatible) → bibtex8 (8-bit BibTeX,
interchangeable with `bibtex` for this all-ASCII bibliography) → pdfLaTeX ×2. **The shipped
`main.pdf` was compiled from exactly the sources contained in `HFF_Final_Overleaf_Package.zip`**
(the ZIP root is the compilation directory; the PDF is copied out of that same tree — no older
PDF reused). 49 pages.

## 1. Checks performed and results

| Check | Method | Result |
|---|---|---|
| Undefined citations / references | `grep -c undefined main.log`; PDF text `??` count | **0 / 0** |
| Missing figures or tables | compile log (both TikZ figures input from ch02; all longtables render) | none missing |
| Missing BibTeX records | every `\cite` key cross-checked against `references.bib` keys | 19 cited keys (one key split across a commented line-continuation) — **all resolve**; 0 bibtex errors in `.blg` |
| Duplicate bib keys | key frequency scan | none (18 entries, all cited, none unused) |
| Incomplete references | field scan | no invented fields; two noted residuals (Shah T1 digit → C-1; hood1974 page range) — carried as `note` fields, not silent |
| Unresolved placeholders | TODO/XXX/FIXME/TBD/`??` scan of sources and PDF text | none |
| Stale numerical values | PDF full-text sweep against the superseded-value list: Ri = O(1)/"forbids", "about 7 %", 1.0/1.2/1.6×10⁴ W m⁻² ceilings, (M_b = 2.8), 0.63, 117/32, 58.7 | **all clean** |
| Required current values present | 3.64, 58.8, 1.057×10⁵, frozen-force labelling, 0.428 H₀, 6.1 %, 5.9 % | **all present** |
| Chapter↔appendix consistency | table cells vs arithmetic cells vs register | **2 rounding discrepancies found and corrected** (see §2); remainder consistent within stated precision |
| Compilation warnings affecting presentation | log scan: 0 LaTeX warnings; Overfull boxes counted and attributed | 3 major overflows **found and fixed** (see §2); 16 minor residual boxes ≤ 44.8 pt (figure/tikz and longtable-rule slack), documented as cosmetic |

## 2. Discrepancies found and corrections applied (with justification)

1. **Buckling margin printed two ways.** Table 7.1 and appendix cell A5 printed
   `M_b = 117/32 = 3.7` (from rounded inputs) while the audit chain, D-15, and cell A9 carry
   the precise `117.5/32.3 = 3.64` (indeed 3.638, so "3.7" was not even its 2-s.f. rounding).
   **Correction:** all three locations harmonized to 3.64; dictionary row updated; A5's
   N_θ illustration recomputed at θ̄ = 32.3 K (−2.91×10⁴ N/m) and N_cr at D_s = 9.64
   (1.057×10⁵ N/m). No physical change — same inputs, honest rounding. (Reconciliation row
   R-14 annotated.)
2. **Ceiling temperature rounding.** θ̄ ceiling at M_b = 2 printed 58.7 K; exact value
   117.5/2 = 58.75 K → 58.8 K at one decimal. **Correction:** 58.8 K.
3. **Page-layout overflows (presentation only).** The boundary-condition table (ch05,
   `tab:bcs`) and the geometry table (ch02, `tab:geometry`) used fixed `llll` columns and
   overran the text block by up to 200 pt; an unbreakable `\texttt` archive path in
   Appendix B overran by 159 pt. **Correction:** p-column widths for both tables;
   `\path{...}` (breakable) for the path. Content unchanged.

## 3. Preserved (verified present and unchanged in the final PDF)

* Frozen-force beam–column formulation with `eq:nupdate`, the 2.3 % conservative limitation,
  6.1 %/5.9 % relaxation figures, exact ceilings (0.302/0.327/0.5), escalation linkage.
* Corrected dimensionless groups (Ri single-basis 1.7×10⁻³ with both documented conventions,
  Gr = 1.07, Br = 1.0×10⁻⁶, Re_H₀ = 25).
* Baseline operating point and all admissibility bounds A-1…A-6, D-1…D-20 register.

## 4. Statement of limitations

The bibliography verification consolidates the Crossref/DOI and publisher-page checks performed
during audit stages 1–2 (see `HFF_final_reference_status.csv`); **no new independent reference
verification was performed at Stage 4**, and the two carried actions (C-1 digit-level T1
confirmation; hood1974 page range) remain open. Compilation used the sandbox TeX Live 2026
toolchain (BusyTeX/wasm), which is feature-equivalent for this document's package set; Overleaf
should reproduce it with its default TeX Live and `bibtex`.
