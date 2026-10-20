#!/usr/bin/env python3
"""Non-vacuity probes for suite v4 (commit 5741d36).

Each probe applies one edit to a FRESH copy of the committed tree and asks two questions:
  (a) does the suite still run to completion, and
  (b) does it exit non-zero for a reason that names the edited object?
A probe that passes would show a check that cannot fail on the object it claims to test.
Run from anywhere:  python3 nonvacuity_probe.py <path-to-clean-checkout>
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

CLEAN = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
BS = chr(92)

PROBES = [
    ("required file deleted", "chapters/ch07.tex", None, None,
     "delete chapters/ch07.tex"),
    ("table row for theta-bar blanked", "chapters/ch07.tex",
     "$" + BS + "bar" + BS + "theta$ (mean wall rise) & $" + BS + "Delta T_t/2+q^{''}/h+" +
     BS + "Delta T_b/2$ & $30.0+1.55+0.72" + BS + "approx32.3$ K & estimate; see text",
     "$" + BS + "bar" + BS + "theta$ (mean wall rise) & $" + BS + "Delta T_t/2+q^{''}/h+" +
     BS + "Delta T_b/2$ & $99.9$ K & estimate; see text",
     "theta-bar cell total replaced by an unrelated number"),
    ("eq:tcr coefficient made unparseable", "chapters/ch04.tex",
     BS + "bar T_{" + BS + "mathrm{cr}}=" + BS + "frac{" + BS + "pi^2d^2}{12" + BS + "," + BS
     + "alpha(1+" + BS + "nu)L^2}",
     BS + "bar T_{" + BS + "mathrm{cr}}=" + BS + "frac{" + BS + "pi^2d^2}{" + BS
     + "alpha(1+" + BS + "nu)L^2}",
     "eq:tcr loses its 12 coefficient entirely"),
    ("eq:wmax denominator made unparseable", "chapters/ch04.tex",
     "w_{" + BS + "max}=" + BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{8}",
     "w_{" + BS + "max}=" + BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{2(1-"
     + BS + "nu)}",
     "eq:wmax replaced by a non-integer denominator"),
    ("imposed pressure normalisation, no explanation", "chapters/ch04.tex",
     "with the datum $p=0$ at the outlet",
     "with the datum $p=0$ at the outlet and the normalisation $" + BS + "int_{" + BS + "Om_f}p"
     + BS + "," + BS + "mathrm dV=0$",
     "a gauge constraint added to the pressure section"),
    ("stress prose quotes an unrelated value", "chapters/ch07.tex",
     "frozen-force value $13.9$~MPa", "frozen-force value $17.9$~MPa",
     "ch07 stress prose changed without touching eq:beamcol"),
]


def run(copy):
    p = subprocess.run([sys.executable, 'audit_stage15/regression.py'], cwd=copy,
                       capture_output=True, text=True)
    fails = [l[6:].split('|')[0].strip() for l in p.stdout.splitlines() if l.startswith('FAIL')]
    return p.returncode, fails, p.stdout, p.stderr


def main():
    base = tempfile.mkdtemp(prefix='hff_nv_')
    print("clean checkout: %s" % CLEAN)
    print("%-42s %-5s %-6s %s" % ("probe", "exit", "PASS?", "first failures"))
    bad = 0
    for name, rel, old, new, desc in PROBES:
        dst = os.path.join(base, re.sub(r'\W+', '_', name))
        shutil.copytree(CLEAN, dst, ignore=shutil.ignore_patterns('.git', 'project_archive'))
        path = os.path.join(dst, rel)
        if old is None:
            os.remove(path)
        else:
            src = open(path, encoding='utf-8').read()
            n = src.count(old)
            if n != 1:
                print("%-42s ANCHOR %d -- not applied" % (name, n))
                bad += 1
                continue
            open(path, 'w', encoding='utf-8').write(src.replace(old, new, 1))
        rc, fails, out, err = run(dst)
        passed = 'ALL ' in out and rc == 0
        bad += 1 if passed else 0
        print("%-42s %-5d %-6s %s" % (name, rc, "yes" if passed else "no",
                                      (fails[:2] if fails else (err.strip().splitlines()[-1:] or ['-']))))
    print()
    print("vacuous probes: %d" % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
