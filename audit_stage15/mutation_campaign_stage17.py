#!/usr/bin/env python3
"""Stage 17 mutation campaign for regression.py v3.

Two groups, both applied to ISOLATED COPIES under /tmp; the repository is never modified.

  A1..A25  the 25 adversarial mutants of the Stage 16 independent audit, re-run unchanged where
           their anchor text still exists and RE-ANCHORED (three of them: A8, A15, A17) where the
           Stage 17 repair removed or rewrote the sentence they attacked.  A re-anchored mutant
           attacks the same mathematical defect at its new location and is marked as such.
  B1..B9   new mutants that attack the Stage 17 repairs themselves (thermal well-posedness /
           D-32, the 0.2 % end-effect / NEW-05, the Gamma_p labelling / I-11, the pressure gauge).

A mutant counts as DETECTED when regression.py exits non-zero.  Survivors are listed explicitly;
no suite is "robust" while a semantic mutant survives.

Run:  python3 audit_stage15/mutation_campaign_stage17.py
"""
import os, shutil, subprocess, sys

BS = chr(92)
ROOT = os.path.abspath('.')
BASE = '/tmp/hff_mut17'

M = [
    # ---------------- the 25 independent Stage 16 mutants ----------------
    ("A1", "chapters/ch04.tex",
     "w^{''}(0)=w^{''}(L)=-" + BS + "kappa_{\\" + "mathrm{th}},",
     "w^{''}(0)=w^{''}(L)=-" + BS + "frac{" + BS + "kappa_{\\" + "mathrm{th}}}{2},",
     "moment BC: half the thermal curvature at the pins", ""),
    ("A2", "chapters/ch04.tex",
     BS + "frac{1-" + BS + "cos" + BS + "mu L}{" + BS + "sin" + BS + "mu L}",
     BS + "frac{1-" + BS + "cos" + BS + "mu L}{2" + BS + "sin" + BS + "mu L}",
     "closed-form solution: particular integral halved", ""),
    ("A3", "chapters/ch04.tex",
     BS + "frac{Ed}{2(1-" + BS + "nu^2)}" + BS + ",",
     BS + "frac{Ed}{(1-" + BS + "nu^2)}" + BS + ",",
     "compatibility update: factor 2 lost", ""),
    ("A4", "chapters/ch04.tex",
     BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{8} .",
     BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{12} .",
     "linear bow formula: 1/8 -> 1/12", ""),
    ("A5", "chapters/appendix.tex",
     "$" + BS + "bar" + BS + "theta=32.3$ K",
     "$" + BS + "bar" + BS + "theta=34.3$ K",
     "printed mean temperature", ""),
    ("A6", "chapters/ch02.tex",
     "$1.0" + BS + "times10^{-3}$ & " + BS + "si{" + BS + "pascal" + BS + "second}",
     "$2.0" + BS + "times10^{-3}$ & " + BS + "si{" + BS + "pascal" + BS + "second}",
     "water viscosity (feeds the whole pressure chain)", ""),
    ("A7", "chapters/ch02.tex",
     BS + "SI{5.0e3}{" + BS + "watt" + BS + "per" + BS + "square" + BS + "metre}",
     BS + "SI{6.0e3}{" + BS + "watt" + BS + "per" + BS + "square" + BS + "metre}",
     "imposed heat flux (feeds every thermal result)", ""),
    ("A8", "chapters/ch08.tex",
     "inject a spurious outlet mass source (register D-25, corrected in D-30).",
     "inject a spurious outlet mass source; the level is fixed by imposing "
     "$" + BS + "int_{" + BS + "Ga_" + BS + "mathrm{out}}p" + BS + "," + BS + "mathrm dY=0$.",
     "reintroduces a gauge constraint in different notation", "re-anchored: the D-25 sentence now "
     "carries the 'corrected in D-30' phrasing"),
    ("A9", "chapters/ch08.tex",
     BS + "int_{" + BS + "Ga_{" + BS + "mathrm{end}}}" + BS + "varphi_1" + BS + "," + BS + "mathrm dY=0",
     BS + "int_{" + BS + "Ga_" + BS + "mathrm{end}}" + BS + "varphi_1" + BS + "," + BS + "mathrm dY=1",
     "function space: non-homogeneous integral condition (not a subspace)", ""),
    ("A10", "chapters/ch08.tex",
     "+" + BS + "sum_{K}" + BS + "int_{K}" + BS + "tau_K",
     "-" + BS + "sum_{K}" + BS + "int_{K}" + BS + "tau_K",
     "SUPG term sign", ""),
    ("A11", "chapters/audit_appendix.tex",
     "The ``total mechanical surface strain $5.4" + BS + "times10^{-3}$'' was undefined and did not "
     "correspond to any strain in the model",
     "The ``total mechanical surface strain $5.4" + BS + "times10^{-3}$'' is the stress-producing "
     "surface strain",
     "register D-31 reverts to the withdrawn false claim", ""),
    ("A12", "chapters/ch07.tex",
     "$2.19" + BS + "times10^{-4}/9.2" + BS + "times10^{-8}=2.4" + BS + "times10^{3}$",
     "$2.19" + BS + "times10^{-4}/9.2" + BS + "times10^{-8}=2.9" + BS + "times10^{3}$",
     "table value of Gamma_p", ""),
    ("A13", "chapters/appendix.tex",
     "$" + BS + "sigma_{" + BS + "mathrm{bend}}=6|M|/d^2=4.2$ MPa",
     "$" + BS + "sigma_{" + BS + "mathrm{bend}}=6|M|/d^2=5.2$ MPa",
     "frozen bending stress in their own arithmetic appendix", ""),
    ("A14", "chapters/appendix.tex",
     "circular-arc estimate $1.6" + BS + "times10^{-4}$",
     "circular-arc estimate $1.9" + BS + "times10^{-4}$",
     "circular-arc estimate inside a loose tolerance band", ""),
    ("A15", "chapters/ch04.tex",
     "$0.2" + BS + "%$ at the baseline aspect ratio",
     "a few per cent at the baseline aspect ratio",
     "restores the withdrawn few-per-cent stiffening claim", "re-anchored: the original 'few per "
     "cent' sentence was withdrawn in Stage 17 (D-26 / NEW-05)"),
    ("A16", "chapters/ch08.tex",
     "written as a " + BS + "emph{stress} $N_" + BS + "theta^c/d$",
     "written as a " + BS + "emph{stress} $N_" + BS + "theta^c/(2d)$",
     "explanatory 1/d becomes 1/(2d) while eq:weaks is untouched", ""),
    ("A17", "chapters/ch08.tex",
     "|_{" + BS + "Ga_{" + BS + "mathrm{if}}}$, which closes the thermal loop",
     "|_{" + BS + "Ga_{" + BS + "mathrm{if}}}$ (the extracted flux), the loop instead being closed on "
     "an assumed wall temperature",
     "loop closure removed while both Dirichlet/Neumann keywords survive", "re-anchored: the loop "
     "sentence was rewritten in Stage 17"),
    ("A18", "chapters/ch04.tex",
     "D_s" + BS + ",w^{''''}(x)+N_" + BS + "theta^c" + BS + ",w^{''}(x)=0,",
     "D_s" + BS + ",w^{''''}(x)-N_" + BS + "theta^c" + BS + ",w^{''}(x)=0,",
     "beam-column ODE sign (buckling term becomes stiffening)", ""),
    ("A19", "chapters/ch07.tex",
     "the frozen-force value $13.9$~MPa",
     "the frozen-force value $14.9$~MPa",
     "the conservative stress value in the design chapter", ""),
    ("A20", "chapters/appendix.tex",
     "$M_{" + BS + "mathrm{mid}}=-6.4$ N" + BS + ",m per unit depth",
     "$M_{" + BS + "mathrm{mid}}=-8.4$ N" + BS + ",m per unit depth",
     "mid-span moment in the arithmetic appendix", ""),
    ("A21", "chapters/ch02.tex",
     "the conditions are therefore $d_2=0$, $" + BS + "langle d_1" + BS + "rangle=0$ taken as the",
     "the conditions are therefore $d_2=0$, $d_1=0$ taken as the",
     "pin reverted to a clamp in Assumption A9 only (B7 untouched)", ""),
    ("A22", "chapters/ch08.tex",
     "b(" + BS + "mathbf v,p)+c(" + BS + "bu;" + BS + "bu," + BS + "mathbf v)",
     "b(" + BS + "mathbf v,p)-c(" + BS + "bu;" + BS + "bu," + BS + "mathbf v)",
     "convective term sign in the momentum weak form", ""),
    ("A23", "chapters/ch04.tex",
     "N_{" + BS + "mathrm{cr}}=" + BS + "pi^2D_s/L^2",
     "N_{" + BS + "mathrm{cr}}=4" + BS + "pi^2D_s/L^2",
     "critical load: clamped eigenvalue substituted for the pinned one", ""),
    ("A24", "chapters/appendix.tex",
     "$" + BS + "mu=55$ " + BS + "si{" + BS + "per" + BS + "metre}, $" + BS + "mu L=1.65$",
     "$" + BS + "mu=55$ " + BS + "si{" + BS + "per" + BS + "metre}, $" + BS + "mu L=2.65$",
     "printed beam-column parameter", ""),
    ("A25", "chapters/ch09.tex",
     "amplification\n$1.39$",
     "amplification\n$1.29$",
     "benchmark acceptance value", ""),

    # ---------------- Stage 17 mutants ----------------
    ("B1", "chapters/ch08.tex",
     "$T_s=T_" + BS + "Gamma^{(k)}$ on $" + BS + "Ga_{" + BS + "mathrm{if}}$",
     "$k_s" + BS + "nabla T_s" + BS + "cdot" + BS + "bn=q_" + BS + "Gamma^{(k)}$ on $"
     + BS + "Ga_{" + BS + "mathrm{if}}$",
     "reverts step 1 to the flux datum the audit rejected (D-32)", ""),
    ("B2", "chapters/ch08.tex",
     "A pure-Neumann problem of this kind has the constant\nin its kernel",
     "A pure-Neumann problem of this kind has\nno constant in its kernel",
     "deletes the kernel/compatibility argument", ""),
    ("B3", "chapters/ch05.tex",
     "pure-Neumann",
     "well posed as a Neumann problem",
     "data-model paragraph claims the flux datum is admissible", ""),
    ("B4", "chapters/ch04.tex",
     "$0.2" + BS + "%$",
     "$2" + BS + "%$",
     "end-effect magnitude changed by a factor of ten (NEW-05)", ""),
    ("B5", "chapters/ch07.tex",
     "(mixed)",
     "(as measured)",
     "removes the mixed/like-for-like label from the Gamma_p table row (I-11)", ""),
    ("B6", "chapters/appendix.tex",
     "and $" + BS + "Gamma_p=1.73" + BS + "times10^3$ (register D-29)",
     "and $" + BS + "Gamma_p=1.93" + BS + "times10^3$ (register D-29)",
     "like-for-like Gamma_p in A8", ""),
    ("B7", "chapters/audit_appendix.tex",
     "D-32 & The staggered iteration",
     "D-33 & The staggered iteration",
     "renumbers the D-32 register row (breaks the pointer from ch05/ch08)", ""),
    ("B8", "chapters/ch08.tex",
     BS + "frac{N_" + BS + "theta^c}{d}",
     BS + "frac{2N_" + BS + "theta^c}{d}",
     "geometric stiffness doubled inside eq:weaks (display equation)", ""),
    ("B9", "chapters/ch05.tex",
     "register D-32",
     "register D-31",
     "dangling register pointer from the data-model paragraph", ""),
]

SUMMARY = []

FINGERPRINT_CHECKS = {"no display equation has changed", "no register row has changed",
                      "no equation or register row removed"}


def clone(dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('.git', 'project_archive'))


def run(dst):
    p = subprocess.run([sys.executable, 'audit_stage15/regression.py'], cwd=dst,
                       capture_output=True, text=True)
    fails = [l[6:].split('|')[0].strip() for l in p.stdout.splitlines() if l.startswith('FAIL')]
    return p.returncode, fails, p.stderr


def main():
    os.makedirs(BASE, exist_ok=True)
    base = os.path.join(BASE, 'baseline')
    clone(base)
    rc, fails, err = run(base)
    print("%-4s %-9s %s" % ("id", "result", "first failing check / note"))
    print("%-4s %-9s %s" % ("base", "PASS" if rc == 0 else "FAIL", "" if rc == 0 else str(fails[:3])))
    if rc != 0:
        print("BASELINE FAILS: campaign aborted"); return 1

    detected = survived = 0
    for mid, relpath, old, new, desc, note in M:
        dst = os.path.join(BASE, mid)
        clone(dst)
        path = os.path.join(dst, relpath)
        t = open(path, encoding='utf-8').read()
        n = t.count(old)
        if n != 1:
            print("%-4s %-9s ANCHOR COUNT %d -- not applied (%s)" % (mid, "SKIP", n, desc))
            SUMMARY.append((mid, "skip", desc, note, "anchor count %d" % n, "none"))
            survived += 1
            continue
        open(path, 'w', encoding='utf-8').write(t.replace(old, new, 1))
        rc, fails, err = run(dst)
        if rc == 0:
            print("%-4s %-9s ESCAPED   -- %s" % (mid, "survived", desc))
            SUMMARY.append((mid, "survived", desc, note, "", "none"))
            survived += 1
        else:
            maths = [f for f in fails if f not in FINGERPRINT_CHECKS]
            kind = "maths" if maths else "fingerprint"
            print("%-4s %-9s %-11s %-44s | %s" % (mid, "detected", kind,
                                                  (fails[0] if fails else "?")[:44], desc))
            SUMMARY.append((mid, "detected", desc, note,
                            fails[0] if fails else "", kind))
            detected += 1

    print()
    maths = sum(1 for r in SUMMARY if r[5] == "maths")
    print("DETECTED %d / %d, SURVIVING %d  (caught by a numeric/identity check: %d; "
          "caught only by the equation fingerprint: %d)"
          % (detected, len(M), survived, maths, detected - maths))
    for mid, res, desc, note, first, kind in SUMMARY:
        if res != "detected":
            print("   %-4s %-9s %s %s" % (mid, res, desc, ("[" + note + "]") if note else ""))
    return 0 if survived == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
