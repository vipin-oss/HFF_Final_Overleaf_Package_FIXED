# HFF Stage 10 — build environment investigation and package verification

**Date:** 19 October 2026
**Repository:** `vipin-oss/HFF_Final_Overleaf_Package_FIXED` (private)
**Branch:** `arena/c875f9b3-hff-final-overleaf-package-fix`
**HEAD at start of stage:** `37123ec61e809fa019ea9ddd059a89e8b31f2759`
**`origin/main`:** `5a255212a51374f7eb178647eb12b0a9c2b67ded` — unchanged, not merged
**Working tree at start:** clean
**Source changes in this stage:** **none**

> **Outcome in one line:** there is no TeX toolchain in this sandbox and no route to one, so the
> pdfLaTeX → BibTeX → pdfLaTeX → pdfLaTeX sequence **could not be run**; compilation remains
> **NOT VERIFIED**. The reported `bibtex: Permission denied` **cannot have come from this
> environment** — see §4, where the evidence is that `bibtex` here fails with *command not found*
> (exit 127), not with a permission error.

---

## 1. Repository and source state

| Check | Command / evidence | Result |
|---|---|---|
| Branch | `git branch --show-current` | `arena/c875f9b3-hff-final-overleaf-package-fix` |
| HEAD | `git rev-parse HEAD` | `37123ec61e809fa019ea9ddd059a89e8b31f2759` |
| Working tree | `git status --short` | clean |
| `origin/main` | `git ls-remote origin refs/heads/main` | `5a25521…` unchanged |
| Branch on remote | `git ls-remote origin refs/heads/arena/…` | `37123ec…`, in sync |

### 1.1 The bibliography escape is already correct and was **not** modified in this stage

```
$ grep -o 'D\\_h based on the wetted perimeter' references.bib
D\_h based on the wetted perimeter
$ grep -c 'D_h based' references.bib
0
```

Line 77 (`shah1978laminar`, `note`) contains the escaped form; the bare form occurs nowhere. No edit
was made to `references.bib` in Stage 10, and `git status --short` is empty for every source file.
The same escaped form is present in the packaged copy inside `HFF_Stage9_Overleaf_Source.zip`
(checked by reading `references.bib` out of the archive).

---

## 2. Stage-9 package re-verified (it is still the package it claims to be)

| Property | Observed |
|---|---|
| Path | `/home/user/HFF_Final_Overleaf_Package_FIXED/HFF_Stage9_Overleaf_Source.zip` |
| Bytes | 103,062 |
| SHA-256 | `cbed50183679c48f7cef679ca5df2cb1c6c61a75f3c29880e7358e7fae396953` |
| Entries | 24, `testzip()` → `None` (no corrupt entry) |
| Escape inside archive | present |

Hash and size are identical to the values recorded at Stage 9 — the archive has not drifted.
No new package was built in this stage, because no source file changed.

---

## 3. TeX toolchain audit

### 3.1 What exists

| Item | Result |
|---|---|
| `pdflatex`, `pdftex`, `latex`, `bibtex`, `bibtex8`, `biber`, `latexmk`, `tex`, `kpsewhich`, `mktexlsr`, `tlmgr`, `lualatex`, `xelatex`, `tectonic` | **all absent** (`command -v` returns nothing for each) |
| `/usr/local/texlive`, `/opt/texlive` | do not exist |
| `find / -xdev -name 'bibtex*' -o -name 'pdflatex*'` | returns **only** `/usr/local/lib/python3.11/dist-packages/bibtexparser` and its `.dist-info` — a Python *parsing library*, not an executable |
| `PATH` | `/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games` — all present and readable (11, 635, 635 entries) |
| Build artifacts anywhere in the workspace (`*.aux`, `*.log`, `*.bbl`, `*.blg`, `*.toc`, `*.out`) | **none** |
| Shell history, build scripts, cached `.deb` files | none |

The absence of *any* `.aux`/`.log` is itself evidence: no LaTeX run has ever been executed in this
workspace, by me or by anything else.

### 3.2 Exact behaviour when the sequence is attempted here

```
$ bibtex main
/bin/bash: line 1: bibtex: command not found
exit=127
$ which -a bibtex pdflatex latex
(no output)
```

`127` means *not found*. A permission problem produces `126` and the words `Permission denied`.

### 3.3 Routes to obtain an engine that were actually tried, and why each failed

| Route | Attempt | Blocker |
|---|---|---|
| `apt` / Debian mirror | `curl -sI http://deb.debian.org/debian/` | exit 35, HTTP 000 — no connectivity to the Debian archive |
| Static Tectonic release tarball (musl, no glibc dependency) | `gh release download tectonic@0.17.0 …` | redirects to `release-assets.githubusercontent.com`, which is unreachable here (EOF) |
| Tectonic binary from npm | `npm install node-tectonic-linux-x64` (1.0.0 **and** 1.1.0) — this **succeeded**, 55.8 MB binary installed | the binary itself will not start: `version 'GLIBC_2.38' not found`, `version 'GLIBC_2.39' not found` (image has **glibc 2.36**, Debian 12), and `libgraphite2.so.3 => not found` |
| Tectonic bundle relay | `curl -sI https://relay.fullyjustified.net/` | HTTP 000 — even with a working binary there is no way to fetch a TeX bundle |
| PyPI: `tectonic`, `pytectonic`, `tinytex`, `pdftex`, `latexmk` | package metadata queried | all are placeholders or unrelated (`tectonic` = "coming", `pdftex` = a matplotlib backend, `pytectonic` = real-estate modelling); none ships an engine |
| npm WASM engines: `@typeward/texlive-wasm`, `texlyre-busytex`, `@siglum/engine` | tarballs downloaded and inspected | packages are 150–900 kB; the TeX Live data/engine assets are fetched at runtime from GitHub releases or a CDN, both unreachable |
| Build from source (Rust crate, `tectonic_engine_bibtex`) | not attempted | no cargo toolchain, and crates.io is not reachable |

No security restriction was bypassed, and no bibliography output was fabricated. In particular, **no
`.bbl` was hand-written** and no static check in this report is presented as a substitute for BibTeX.

---

## 4. Why the reported `bibtex: Permission denied` did not come from here

The reported message and the observable behaviour are of different kinds:

| Reported | Observed here |
|---|---|
| `bibtex: Permission denied` — implies a `bibtex` file exists but cannot be executed (exit 126 class) | `bibtex: command not found` — no such file exists (exit 127 class) |

Corroborating facts: no `bibtex` binary anywhere on the filesystem, no TeX installation prefix, no
build artefacts, no shell history, and no script in the workspace that invokes a compiler. Therefore
the failing build was run in a **different environment** — most likely your local machine or another
sandbox image that *does* have TeX installed.

The four ordinary causes of `bibtex: Permission denied`, with the diagnostic for each:

| Cause | Diagnostic | Fix |
|---|---|---|
| The binary lost its execute bit (common after an unzip, a restore from backup, a copied TeX tree, or a Docker layer built with restrictive `umask`) | `ls -l "$(command -v bibtex)"` → mode `rw-` rather than `rwx` | `chmod +x` that file, or reinstall the TeX distribution |
| The TeX Live tree is on a filesystem mounted `noexec` (containers, some `/tmp` and network mounts) | `mount \| grep noexec` | move the TeX installation to an exec-capable mount |
| macOS quarantine / Gatekeeper on a downloaded binary | `xattr -l "$(command -v bibtex)"`, or Console shows a `kernel` denial | `xattr -d com.apple.quarantine …`, or reinstall via MacTeX |
| A directory earlier in `PATH` contains a **directory** named `bibtex`, or a PATH entry is unreadable | `type -a bibtex`, then `ls -ld` the hit | remove the shadowing entry |

Paste-ready check (POSIX shells):

```sh
command -v bibtex; ls -l "$(command -v bibtex)"; type -a bibtex
mount | grep noexec
# macOS only:
xattr -l "$(command -v bibtex)"
```

If `command -v bibtex` prints nothing on your machine either, the message you saw was almost
certainly produced by a wrapper (an editor's build chain or a CI step) that reports its own failure
in that wording; the underlying condition is then *missing toolchain*, and the remedy is to install
TeX Live and set the toolchain path.

**What I cannot do from here:** reproduce, confirm or clear the permission error, because the binary
does not exist in this environment. That is recorded as an unresolved environmental dependency, not
as a source-code defect.

---

## 5. Expanded static build-risk analysis (no compiler involved)

Because a real build is impossible, the source was subjected to a wider set of checks than any
previous stage, aimed specifically at error classes that only a compiler normally catches. All were
run on the current tree.

| # | Check | Method | Result |
|---|---|---|---|
| 1 | `$` parity | count unescaped `$` per file after removing `\$`, `\[…\]` | **PASS** — all 16 files even |
| 2 | `\left` / `\right` balance | regex count per file | **PASS** — equal in every file |
| 3 | Environment nesting | stack-based `\begin`/`\end` pairing per file, not just totals | **PASS** — no mismatched or unclosed environment |
| 4 | Package-provided commands | 29 commands mapped to their providing package, checked against `\usepackage` list in `main.tex` | **PASS** — no command used without its package |
| 5 | Bibliography machinery | `natbib` loaded, `\bibliographystyle{plainnat}`, `\bibliography{references}` present | **PASS** |
| 6 | BibTeX-required fields per entry type | `plainnat` requirements for `article` / `book` / `incollection` | **PASS** — 18 entries, none missing `author`/`title`/`journal`/`booktitle`/`publisher`/`year` |
| 7 | Duplicate bib keys | exact-set comparison | **PASS** — none |
| 8 | Custom macros | 14 `\newcommand` defined in `main.tex`; every short/uppercase macro used was traced | **PASS** — all defined and all used; the apparent unknowns in `figures/fig_geometry.tex` (`\Le`, `\L`, `\Lo`, `\Hf`, `\ds`) are `\def`'d locally at the top of that file, and `\p`, `\x` are `\foreach` loop variables |
| 9 | Citation forms | all `\cite…` variants collected | **PASS** — 66 uses, only `\cite`, which `natbib` provides |
| 10 | `.bib` parseability | `bibtexparser` 2.1.0 | **PASS** — 18 entries, 0 failed blocks |
| 11 | Escaped characters in text fields | scan of `_ ^ & % # $` inside all fields | **PASS** — the only `_` outside the escaped one is inside a `doi` field, which `plainnat` does not typeset |
| 12 | `\input` targets | all resolved relative to `main.tex` | **PASS** — 15/15 |
| 13 | Labels / references | 86 labels vs 73 `\ref`/`\eqref` targets | **PASS** — no duplicates, none undefined |
| 14 | Non-ASCII input | byte scan | **PASS** — 0 non-ASCII bytes, so no UTF-8/inputenc error is possible |
| 15 | Figures | two inline TikZ files, no `\includegraphics` | **PASS** — nothing external to find |
| 16 | Package inter­action risk reviewed by inspection | `xcolor[table]` with `booktabs`, `caption` with `longtable`, `hyperref` loaded **last**, `siunitx` v3 with the legacy `\SI` alias (8 uses, deprecation warning only, not an error) | **PASS (by inspection)** — no known incompatibility |

These sixteen checks raise confidence that the *bibliography error* and the common structural errors
are gone. They do **not** prove the document compiles: a compiler alone can reveal an undefined
control sequence from an omitted package not in the mapped list, a TeX capacity/register limit, a
`.bst`-specific formatting issue, or a font/encoding problem. **16 static passes ≠ 1 build.**

---

## 6. Status of the build

| Item | Status |
|---|---|
| pdfLaTeX pass 1 | **NOT RUN** — no engine |
| BibTeX | **NOT RUN** — no engine |
| pdfLaTeX passes 2 and 3 | **NOT RUN** |
| `.log`, `.aux`, `.bbl`, `.blg` produced | **none** |
| Warnings suppressed | **none** — no warnings were ever generated |
| PDF produced | **none**; the repository's `main.pdf` remains the stale Stage-4 build and is not used or shipped |
| Citations, cross-references, figure inclusion in a *typeset* document | **NOT CHECKED** — cannot be checked without a build, whatever the static counts say |
| **Overall build status** | **NOT VERIFIED** |

---

## 7. What would complete the build

Any one of these, none of which is available inside this sandbox:

1. **Overleaf** — upload `HFF_Stage9_Overleaf_Source.zip`, leave pdfLaTeX + BibTeX, recompile. This is the intended path and needs no installation.
2. **A local TeX Live** — run the documented sequence in the unpacked archive.
3. **A sandbox image with TeX pre-installed** — then the sequence can be executed here and the `.log` inspected.

If you run it yourself and it still fails, send the first error from the `.log` (or the console) and the
stage can be completed against the real output rather than against static checks.

---

## 8. Change control

- **No source file was modified in this stage.** `references.bib`, all 13 chapters, both figures and `main.tex` are byte-identical to `37123ec`.
- No equation, boundary condition, material parameter, geometry, operating point, dimensionless group, tolerance or research objective was touched.
- No Stage-7 proposal was resolved: P‑1 (function spaces), P‑2 (thermal data flow), P‑4 (solid model) and P‑5 (SUPG `τ`) remain exactly as recorded.
- No solver code was written; no simulation was run; nothing was merged into `main`.
- Files added by this stage: this report, and an addendum in `HFF_stage9_build_and_package_report.md`.

---

## 9. Remaining scientific sign-off gates (unchanged)

| Gate | Status |
|---|---|
| C‑3 / M4 — independent reviewer acceptance of the corrected mechanical interface statement | **OPEN** |
| P‑1 / M6 — function spaces `V_g, Q, V_s, S_f, S_s` undefined | **OPEN** |
| T7 — single shared interface temperature unknown not stated | **OPEN** |
| P‑2 / T8 — contradictory thermal data-flow directions (`ch05:70–72` vs `ch08:114`) | **OPEN** |
| P‑4 / M8 — geometric stiffness absent from `\eqref{eq:weaks}` | **OPEN** |
| P‑5 / B7 — SUPG operator and `τ` unspecified | **OPEN** |
| Stage-5 items C‑2, C‑3, C‑6, C‑9, C‑12 | **OPEN** |
| Numerical verification | **NOT PERFORMED** — no solver exists |
| Validation | **NOT PERFORMED** |

Stage-7 audit totals stand at **19 PASS / 6 FAIL / 4 UNRESOLVED** across 29 findings.
