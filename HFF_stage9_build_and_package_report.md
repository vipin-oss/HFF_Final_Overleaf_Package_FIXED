# HFF Stage 9 — build and package report

**Date:** 19 October 2026
**Repository:** `vipin-oss/HFF_Final_Overleaf_Package_FIXED` (private)
**Branch:** `arena/c875f9b3-hff-final-overleaf-package-fix`
**Starting HEAD for this stage:** `d52aeb181ecaf999017ffdfae006fefa46e0ca39`
**`origin/main`:** `5a255212a51374f7eb178647eb12b0a9c2b67ded` — unchanged, not merged, not pushed to
**Source commit created in this stage:** `e76cc6043c22759a8cc5cdf05ae0199ba0b3ab36`
**Packaging commit:** see §7

---

## 1. Deliverables

| Deliverable | Path | Size | SHA-256 |
|---|---|---:|---|
| Overleaf package | `/home/user/HFF_Final_Overleaf_Package_FIXED/HFF_Stage9_Overleaf_Source.zip` | **103,062 bytes** | `cbed50183679c48f7cef679ca5df2cb1c6c61a75f3c29880e7358e7fae396953` |
| This report | `/home/user/HFF_Final_Overleaf_Package_FIXED/HFF_stage9_build_and_package_report.md` | 11,964 B at the packaging commit | `44c83537efd59959bd3b3ae7184bac61b4d62c018e5b66b836f492a3d7cac3f0` (that commit; this closing revision adds §7 only) |

**File count:** 24 entries, 0 directory entries, 244,992 bytes uncompressed.
Deterministic build: fixed 2026-10-19 timestamps, sorted entry names, mode 0644, deflate level 9.

---

## 2. Source state verified before any edit

| Check | Result |
|---|---|
| Branch is `arena/c875f9b3-hff-final-overleaf-package-fix` | **PASS** |
| HEAD before work | `d52aeb181ecaf999017ffdfae006fefa46e0ca39` |
| Working tree clean | **PASS** |
| `origin/main` at `5a25521` (measured with `git ls-remote`, not assumed) | **PASS** |
| Stage-7 C‑1 present: `a_T(\bu;T_f,\chi)` in `ch08` | **PASS** |
| Stage-7 C‑3 present: "admissible test functions vanish there" in `ch08` | **PASS** |
| Stage-7 C‑4 present: `ch02` bookkeeping wording, "does not cancel" | **PASS** |
| Stage-7 audit, correction log, sign-off checklist, diff patch all present and untouched | **PASS** |
| `.tex` and `.bib` files are pure ASCII (no undeclared UTF-8 input errors) | **PASS** — 0 non-ASCII bytes in all 16 `.tex` and in `references.bib` |

---

## 3. The actual LaTeX error and the minimal correction

### 3.1 Diagnosis

`references.bib`, line 77, `shah1978laminar`, `note` field:

```
... Nu uses D_h based on the wetted perimeter. ...
```

The underscore was **not** escaped in the starting commit. `plainnat` copies a `note` field verbatim into the `.bbl`, where `_` is a subscript character and is illegal in text mode; pdfLaTeX stops with `Missing $ inserted` / `Extra }, or forgotten $`.

The error class was then searched for exhaustively across the whole tree, so that the same fix would not be applied twice and no second instance would be missed:

| Search | Result |
|---|---|
| `D_h` in `references.bib` | exactly 1 occurrence, the one above |
| `D\_h` in `references.bib` | 0 occurrences before the edit (so nothing was double-escaped) |
| All bare `_` in `references.bib` | 2: line 77 (text, fixed) and line 92 (`doi = {10.1007/3-540-34596-5_15}`, see §3.3) |
| Bare `_` / `^` outside math and outside command arguments, all 16 `.tex` | 0 — heuristic scan stripping comments, math environments, `$…$`, `\[…\]`, `\(…\)` and the arguments of `\label \ref \eqref \cite \input \include \url \path \begin \end …` |
| Bare `&` outside tables/math | 1, a false positive: `sort&compress` in the `natbib` package options |
| `% & # $ ^ ~` unescaped inside `.bib` fields | 0 other than the two underscores |

### 3.2 Correction applied

One line, one character:

```diff
-Nu uses D_h based on the wetted perimeter.
+Nu uses D\_h based on the wetted perimeter.
```

`git diff d52aeb1 e76cc60 -- references.bib` is exactly `1 file changed, 1 insertion(+), 1 deletion(-)`, and the word diff is `-D_h` / `+D\_h`.

Nothing else in the bibliography was touched: authors, titles, journals, volumes, pages, years, publishers, series and the DOI field are byte-identical to the starting commit.

### 3.3 The second underscore, deliberately left alone

`turek2006proposal` contains `doi = {10.1007/3-540-34596-5_15}`. This was **not** changed:

- the DOI is metadata and must remain byte-exact; escaping it would corrupt the identifier for any consumer that reads the field;
- `plainnat` does not emit a `doi` field, so it never reaches LaTeX and cannot produce the error;
- if a DOI-printing style is adopted later, that field must be escaped or emitted through `\url` at that point. This is recorded here rather than silently "fixed".

### 3.4 Source diff for the whole stage

```
HFF_stage9_package_README.md | 149 +++++  (new, package documentation)
references.bib               |   2 +-    (the underscore)
```

`chapters/ch02.tex` and `chapters/ch08.tex` are **unchanged** from the starting commit
(`git diff --quiet d52aeb1 e76cc60 -- chapters/ch02.tex chapters/ch08.tex` returns 0). No equation,
boundary condition, material parameter, geometry, operating point, dimensionless group, tolerance or
research objective was touched.

---

## 4. Compilation status — NOT CHECKED

**Compilation was not performed and is not claimed.** A real attempt was made to obtain a toolchain; every route failed for environmental reasons:

| Route | Outcome |
|---|---|
| `which pdflatex latex bibtex latexmk tectonic xelatex lualatex` | none found |
| `/usr/local/texlive`, `/opt/texlive` | do not exist |
| `apt` / `deb.debian.org` | no connectivity (`curl` exit 35 / HTTP 000), package install not possible |
| Debian bookworm base image | confirmed, but repositories unreachable |
| `tectonic` from PyPI | no such distribution |
| `tectonic` release asset from GitHub | the `302` redirect points at `objects.githubusercontent.com`, which is unreachable from this sandbox (HTTP 000) |
| Tectonic support bundle relay (`relay.fullyjustified.net`) | unreachable (HTTP 000), so even a staged binary could not fetch its bundle |
| npm `swiftlatex`, `texlive.js`, `node-texlive` | not published; npm `tectonic` is an unrelated React data-loading package; npm `latex.js` is an HTML renderer, not a TeX engine, and cannot execute pdfLaTeX or BibTeX |

Consequently:

- no `pdflatex` exit status exists;
- no BibTeX run exists;
- no `.log`, `.aux`, `.bbl` or `.blg` exists;
- no warnings were produced, and therefore **none were suppressed**;
- no PDF was generated, so the archive contains none, and the repository's `main.pdf` (49 pages) remains the stale **Stage-4** build and was **not** used or shipped.

Standing on the record: the structural checks in §5 are *not* a build. They cannot detect an
undefined control sequence, a missing package, a `Missing $ inserted`, a TeX capacity problem or a
bad interaction between packages.

---

## 5. Package verification — extracted archive, fresh directory

Extraction: `unzip -q HFF_Stage9_Overleaf_Source.zip -d /tmp/stage9`. Every check below reads the extracted files.

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | ZIP integrity | **PASS** | `unzip -t`: "No errors detected"; `zipfile.testzip()` returned `None`; all 24 entries byte-identical when re-read from the archive and compared with the extracted files |
| 2 | `\input`/`\include` paths resolve | **PASS** | 15/15: 13 chapter inputs from `main.tex` (`ch01`–`ch11`, `appendix`, `audit_appendix`) + 2 TikZ inputs from `ch02` (`figures/fig_geometry`, `figures/fig_signs`) |
| 3 | Cited keys exist in `references.bib` | **PASS** | 18 cited, 18 defined, 0 missing, 0 uncited |
| 4 | `references.bib` parseable | **PASS** | `bibtexparser` 2.1.0: 18 entries, 0 failed blocks; `shah1978laminar` note contains `D\_h` and no bare `D_h` |
| 5 | Duplicate labels | **PASS** | 86 labels, 0 duplicates |
| 6 | Undefined references | **PASS** | 73 `\ref`/`\eqref` targets, 0 undefined |
| 7 | Braces and environments balanced | **PASS** | all 16 `.tex` files |
| 8 | Required figures/assets present | **PASS** | both `figures/*.tex` present; no `\includegraphics` anywhere, so no external asset is required |
| 9 | Bibliography correction present | **PASS** | `D\_h based on the wetted perimeter` present; `D_h based` absent |
| 10 | Stage-7 corrections present in packaged chapters | **PASS** | C‑1, C‑3, C‑4 markers all found in the extracted `ch08`/`ch02` |
| 11 | Stage-7 audit records present | **PASS** | audit, correction log, sign-off checklist, diff patch — 4/4, non-empty, hashes match the Stage-7 commit |
| 12 | Stage-8 verification report present | **PASS** | `HFF_stage8_package_verification.md`, 9,587 B |
| 13 | Packaged sources match the Git tree | **PASS** | 22/22 files identical to commit `e76cc60` by `git hash-object` vs `git rev-parse` (16 `.tex`, `references.bib`, 4 Stage-7 documents, Stage-8 report, Stage-5 checklist) |
| 14 | `main.tex` and source directories at ZIP root | **PASS** | roots: `main.tex`, `references.bib`, `README.md`, `chapters/`, `figures/`, 7 top-level `.md`/`.patch` files; no enclosing folder, no directory entries |
| 15 | No stale PDF shipped | **PASS** | 0 files ending `.pdf` in the archive |
| 16 | Root README with instructions and sequence | **PASS** | `README.md`, 7,459 B, byte-identical to `HFF_stage9_package_README.md` in the repository; states the pdfLaTeX → BibTeX → pdfLaTeX → pdfLaTeX sequence, the Overleaf upload steps, and that validation is incomplete |
| 17 | LaTeX compilation | **NOT CHECKED** | no TeX engine (§4) |
| 18 | BibTeX execution | **NOT CHECKED** | no BibTeX binary (§4) |
| 19 | PDF generated from this exact source | **NOT CHECKED** | requires compilation |
| 20 | Visual inspection of typeset output | **NOT CHECKED** | requires a PDF |
| 21 | Overleaf upload | **NOT CHECKED** | requires the user's account |

---

## 6. What this stage does and does not establish

**Establishes:** the one identified LaTeX error class — a bare underscore in a `note` field that `plainnat` typesets — was fixed in exactly one place, is not double-escaped, and no second instance exists anywhere in the sources under a documented heuristic scan. The archive is intact, self-contained, cites only defined keys, has no duplicate labels or dangling references, balances its braces and environments, and its sources are byte-identical to commit `e76cc60`. The Stage-7 corrections and all audit records travel with it.

**Does not establish:** that the document compiles. The sandbox has no TeX engine and no route to one, so the build remains unexecuted. Equally, nothing here bears on whether the equations are correct, whether the formulation is well posed, or whether any physical result is valid. **A package check is not a compilation, and neither is scientific validation.**

---

## 7. Commits in this stage

| Commit | Contents |
|---|---|
| `e76cc6043c22759a8cc5cdf05ae0199ba0b3ab36` | `references.bib` underscore fix + `HFF_stage9_package_README.md` |
| `d449bc7485092ff337772f0b726b827b6fcf16a2` | `HFF_Stage9_Overleaf_Source.zip` (103,062 B, SHA-256 `cbed5018…396953`) + this report |

This closing commit adjusts §1 and §7 only; the ZIP and every packaged source file are unchanged by it.

`main` was not touched, and the branch was not merged.

---

## 8. Remaining scientific sign-off gates

Unchanged from Stage 7 — packaging resolves none of them:

| Gate | Status |
|---|---|
| C‑3 / M4 — independent reviewer acceptance of the corrected mechanical interface statement | **OPEN** |
| P‑1 / M6 — trial and test function spaces `V_g, Q, V_s, S_f, S_s` undefined | **OPEN** |
| T7 — whether the interface temperature is a single shared unknown | **OPEN** |
| P‑2 / T8 — contradictory thermal data-flow directions, `ch05:70–72` vs `ch08:114` | **OPEN** |
| P‑4 / M8 — geometric stiffness claimed in `ch03`/`ch08` but absent from `\eqref{eq:weaks}` | **OPEN** |
| P‑5 / B7 — SUPG operator and time-scale `τ` unspecified | **OPEN** |
| Stage-5 items C‑2, C‑3, C‑6, C‑9, C‑12 | **OPEN** |
| Numerical verification | **NOT PERFORMED** — no solver exists |
| Validation | **NOT PERFORMED** — no benchmark comparison has been run |

Stage-7 audit totals, for the record: **19 PASS / 6 FAIL / 4 UNRESOLVED** across 29 findings.

---

## 10. Stage-10 addendum — build-environment re-investigation (19 October 2026)

Added in Stage 10; the body of this report above is left as it was written at Stage 9.

A reported `bibtex: Permission denied` was investigated. Findings:

1. **The message cannot originate in this environment.** No `bibtex`, `pdflatex`, `latexmk` or
   `tectonic` binary exists anywhere on the filesystem (`find / -xdev` returns only the Python
   `bibtexparser` library directory), `command -v bibtex` is empty, and running `bibtex main` here
   produces `/bin/bash: line 1: bibtex: command not found` with **exit 127** — not the exit-126
   class that a permission denial produces. There are no `.aux`, `.log`, `.bbl` or `.blg` files
   anywhere in the workspace, so no build has ever been executed here.
2. **A toolchain was still pursued further than at Stage 9.** The npm package
   `node-tectonic-linux-x64` (versions 1.0.0 and 1.1.0) installs a real 55.8 MB engine binary, but
   the binary will not start on this image: it requires `GLIBC_2.38` and `GLIBC_2.39` (image has
   glibc **2.36**, Debian 12) and is missing `libgraphite2.so.3`. The static musl build that would
   avoid both problems is served only from `release-assets.githubusercontent.com`, which is
   unreachable, and Tectonic's bundle relay `relay.fullyjustified.net` is unreachable as well.
   WASM engines (`@typeward/texlive-wasm`, `texlyre-busytex`, `@siglum/engine`) fetch their TeX Live
   data from GitHub releases or a CDN at runtime, equally unreachable.
3. **Build status is unchanged: NOT VERIFIED.** pdfLaTeX, BibTeX and both further passes were not
   run; no log, no warnings, no PDF. No bibliography output was fabricated and no `.bbl` was
   hand-written.

Because no source file changed, no new package was built: `HFF_Stage9_Overleaf_Source.zip` remains
current at 103,062 bytes, SHA-256
`cbed50183679c48f7cef679ca5df2cb1c6c61a75f3c29880e7358e7fae396953`, 24 entries, re-verified in Stage 10.

Full evidence, the diagnostic procedure for the permission error on a machine that does have TeX,
and 16 static build-risk checks are in **`HFF_stage10_build_environment_report.md`**.
