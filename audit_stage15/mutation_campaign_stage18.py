#!/usr/bin/env python3
"""Stage 18 mutation campaign: 34 retained Stage 17 mutants + 8 new ones + 1 proof case.

Every case is applied to a FRESH ISOLATED COPY under /tmp; the repository is never modified and
the clean baseline is run first.  A case counts as DETECTED only when

  (i)  the mutated copy runs the suite to completion (no traceback, no syntax error),
  (ii) the suite exits non-zero, and
  (iii) the declared INTENDED assertion is among the failing checks.

Anything else is reported as ESCAPED, WRONG-FAILURE (a failure that is not the intended one,
e.g. a syntax error or a missing file) or ANCHOR (the mutation could not be applied).  Detection
by an equation fingerprint alone is reported separately: a fingerprint shows that text changed,
never that a mathematical condition is false, so a fingerprint-only kill is not evidence that the
substantive layer works.

Retained Stage 17 cases are imported from mutation_campaign_stage17.M, so they are byte-identical
to the permanent Stage 17 record.  Three of them (A8, A15, A17) are re-anchored, as recorded there.

Run from the repository root:  python3 audit_stage15/mutation_campaign_stage18.py
Raw per-case evidence is written to audit_stage15/stage18_mutation_results.txt.
"""
import os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import mutation_campaign_stage17 as S17

BS = chr(92)
ROOT = os.path.abspath('.')
BASE = '/tmp/hff_mut18'
RESULTS = os.path.join('audit_stage15', 'stage18_mutation_results.txt')
BASE_PASSES = 0

FINGERPRINT_CHECKS = {"no display equation has changed", "no register row has changed",
                      "no equation or register row removed"}

# ---- intended assertion for every retained Stage 17 case (the check that targets its defect) ----
EXPECT17 = {
    "A1": "no display equation has changed",   # fingerprint-only: see the summary
    "A2": "no display equation has changed",   # fingerprint-only: see the summary
    "A3": "no display equation has changed",   # fingerprint-only: see the summary
    "A4": "the eq:wmax denominator reproduces the printed linear w_max (appendix A3)",
    "A5": "printed theta-bar equals the recomputed value",
    "A6": "ch04 Gamma_p = w_max/w_p matches",
    "A7": "printed theta-bar equals the recomputed value",
    "A8": "a pressure normalisation occurs only as an explicitly rejected counterfactual",
    "A9": "V_s integral condition is homogeneous",
    "A10": "no display equation has changed",  # fingerprint-only: see the summary
    "A11": "no register row has changed",      # fingerprint-only: see the summary
    "A12": "ch07 table Gamma_p matches",
    "A13": "appendix sigma_bend frozen matches",
    "A14": "appendix circular-arc estimate matches",
    "A15": "ch04 has no stale few-per-cent stiffening claim",
    "A16": "ch08 writes the geometric stress with 1/d",
    "A17": "the loop closes on the extracted interface temperature",
    "A18": "no display equation has changed",  # fingerprint-only: see the summary
    "A19": "every stress quoted in ch07 prose is one of the recomputed values",
    "A20": "appendix M_mid matches",
    "A21": "A9 states the pin, not a clamp",
    "A22": "no display equation has changed",  # fingerprint-only: see the summary
    "A23": "ch04 critical load is the pinned eigenvalue",
    "A24": "appendix mu*L matches",
    "A25": "ch09 V-C3 amplification matches",
    "B1": "step 1 gives the solid T_s = T_Gamma^{(k)} on the interface",
    "B2": "the kernel/compatibility argument is spelled out",
    "B3": "ch05 and ch08 agree that a solid flux datum is inadmissible",
    "B4": "ch04 states the measured 0.2 % with its Q8 evidence",
    "B5": "ch07 table labels Gamma_p mixed",
    "B6": "appendix A8 like-for-like Gamma_p matches",
    "B7": "no equation or register row removed",  # fingerprint-only: see the summary
    "B8": "geometric term present, negative, with N/d",
    "B9": "ch05 and ch08 agree that a solid flux datum is inadmissible",
}

# ---- the eight Stage 18 mutants and one proof case for the removed `or True` ----
M18 = [
    ("G1", "chapters/ch08.tex",
     "inject a spurious outlet mass source (register D-25, corrected in D-30).",
     "inject a spurious outlet mass source; in practice the level is fixed by adding the "
     "normalisation $" + BS + "int_{" + BS + "Om_f}p" + BS + "," + BS + "mathrm dx=0$ to the system "
     "(register D-25, corrected in D-30).",
     "gauge constraint reinserted in the same sentence as its own explanation", "",
     "a pressure normalisation occurs only as an explicitly rejected counterfactual", "default"),
    ("G2", "chapters/ch05.tex",
     "Because no gauge freedom exists, nothing is imposed to fix it;",
     "Because no gauge freedom exists, nothing is imposed to fix the level, although the discrete "
     "pressure is normalised to a zero mean, $" + BS + "langle p" + BS + "rangle_{" + BS + "Om_f}=0$;",
     "equivalent reworded normalisation placed beside 'nothing is imposed'", "",
     "a pressure normalisation occurs only as an explicitly rejected counterfactual", "default"),
    ("G3", "chapters/ch05.tex",
     "B5 & $" + BS + "Ga_{" + BS + "mathrm{if}}$ & " + BS + "eqref{eq:ifkin}--" + BS + "eqref{eq:ifflux}",
     "B5 & $" + BS + "Ga_{" + BS + "mathrm{if}}$ & $T_s=T_" + BS + "Gamma^{(k)}$, "
     "$" + BS + "partial_nT_s=q^{''}/k_s$, " + BS + "eqref{eq:ifkin}--" + BS + "eqref{eq:ifflux}",
     "solid interface row carries a Dirichlet AND a Neumann temperature datum", "",
     "no Gamma_if row gives the solid a Dirichlet AND a Neumann temperature datum", "default"),
    ("T1", "chapters/ch07.tex",
     "$30.0+1.55+0.72" + BS + "approx32.3$ K",
     "$30.0+2.55+0.72" + BS + "approx33.3$ K",
     "theta-bar components and total no longer follow from their formula", "",
     "each component printed in the theta-bar cell is its recomputed value at 2 dp", "default"),
    ("T2", "chapters/ch04.tex",
     BS + "bar T_{" + BS + "mathrm{cr}}=" + BS + "frac{" + BS + "pi^2d^2}{12" + BS + ",",
     BS + "bar T_{" + BS + "mathrm{cr}}=" + BS + "frac{" + BS + "pi^2d^2}{24" + BS + ",",
     "T_cr halved in eq:tcr while every printed value is untouched", "",
     "bound A-2 (M_b >= 2) is met by the recomputed margin", "default"),
    ("N1", "chapters/appendix.tex",
     "$" + BS + "Gamma_p$ & deflection ratio $w_{" + BS + "max}/w_p$, " +
     BS + "eqref{eq:gammap}; mixed and like-for-like presentations & --",
     "$" + BS + "Gamma_p$ & thermal-to-pressure deflection ratio & --",
     "nomenclature entry reverted to the bare description (dictionary untouched)", "",
     "the Gamma_p nomenclature entry defines the labelled ratio", "default"),
    ("S1", "chapters/ch04.tex",
     "gives $1.0000$ of $" + BS + "kappa_{" + BS + "mathrm{th}}L^2/8$ for point pins",
     "gives, to within about two per cent, $1.0000$ of $" + BS + "kappa_{" + BS + "mathrm{th}}L^2/8$ "
     "for point pins",
     "reworded stale end-effect magnitude ('about two per cent')", "",
     "no stale end-effect percentage survives", "default"),
    ("S2", "chapters/ch04.tex",
     "gives $1.0000$ of $" + BS + "kappa_{" + BS + "mathrm{th}}L^2/8$ for point pins",
     "gives, to within a couple of per cent, $1.0000$ of $" + BS + "kappa_{" + BS + "mathrm{th}}L^2/8$ "
     "for point pins",
     "second reworded stale magnitude ('a couple of per cent')", "",
     "no stale end-effect percentage survives", "default"),
    ("F1", "chapters/ch04.tex",
     "w_{" + BS + "max}=" + BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{8}",
     "w_{" + BS + "max}=" + BS + "frac{" + BS + "kappa_{" + BS + "mathrm{th}}L^2}{16}",
     "eq:wmax corrupted and its fingerprint REGENERATED (--update-fingerprints)", "",
     "the eq:wmax denominator reproduces the printed linear w_max (appendix A3)", "regen"),
    ("V1", "chapters/ch09.tex",
     BS + "section{Benchmark hierarchy}",
     BS + "section{Benchmark hierarchy}\nFigures were visually verified against the source files.",
     "proof case for the removed `or True`: a positive claim of visual verification", "",
     "no chapter claims a visual verification of a figure", "default"),
]

CASES = []
for mid, rel, old, new, desc, note in S17.M:
    CASES.append((mid, rel, old, new, desc, note, EXPECT17[mid], "default"))
for mid, rel, old, new, desc, note, expect, mode in M18:
    CASES.append((mid, rel, old, new, desc, note, expect, mode))


def clone(dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('.git', 'project_archive'))


def run(dst, mode):
    cmd = [sys.executable, 'audit_stage15/regression.py']
    if mode == 'regen':
        cmd.append('--update-fingerprints')
    p = subprocess.run(cmd, cwd=dst, capture_output=True, text=True)
    fails = [l[6:].split('|')[0].strip() for l in p.stdout.splitlines() if l.startswith('FAIL')]
    return cmd, p.returncode, fails, p.stdout, p.stderr


def main():
    os.makedirs(BASE, exist_ok=True)
    out = []

    def say(s=""):
        print(s)
        out.append(s)

    base = os.path.join(BASE, 'baseline')
    clone(base)
    cmd, rc, fails, base_out, err = run(base, 'default')
    global BASE_PASSES
    m = re.search(r'ALL (\d+) CHECKS PASSED', base_out)
    BASE_PASSES = int(m.group(1)) if m else 0
    say("%-4s %-13s %s" % ("id", "result", "intended assertion / first failing check"))
    say("%-4s %-13s %s" % ("base", "PASS" if rc == 0 else "FAIL", "" if rc == 0 else str(fails[:3])))
    if rc != 0:
        say("BASELINE FAILS: campaign aborted")
        open(RESULTS, 'w').write("\n".join(out) + "\n")
        return 1

    tally = {"detected": 0, "escaped": 0, "wrong": 0, "anchor": 0}
    fponly, substantive, detail = 0, 0, []
    for mid, rel, old, new, desc, note, expect, mode in CASES:
        dst = os.path.join(BASE, mid)
        clone(dst)
        path = os.path.join(dst, rel)
        src = open(path, encoding='utf-8').read()
        n = src.count(old)
        detail.append("### %s  %s" % (mid, desc))
        detail.append("    file     %s" % rel)
        if note:
            detail.append("    note     %s" % note)
        if n != 1:
            say("%-4s %-13s ANCHOR COUNT %d -- not applied (%s)" % (mid, "not applied", n, desc))
            detail.append("    RESULT   not applied (anchor count %d)" % n)
            tally["anchor"] += 1
            continue
        open(path, 'w', encoding='utf-8').write(src.replace(old, new, 1))
        cmd, rc, fails, stdout, err = run(dst, mode)
        crash = ('Traceback' in err) or (rc != 0 and not fails)
        hit = [f for f in fails if expect in f]
        substantive_fails = [f for f in fails if f not in FINGERPRINT_CHECKS]
        if rc == 0:
            res = "ESCAPED"
        elif crash:
            res = "WRONG"
        elif hit:
            res = "detected"
        else:
            res = "WRONG"
        tally["wrong" if res == "WRONG" else res] += 1
        if res == "detected" and not substantive_fails:
            fponly += 1
            kind = "fingerprint-only"
        elif res == "detected":
            substantive += 1
            kind = "supported by " + ("a regenerated-fingerprint run" if mode == "regen" else "the substantive layer")
        else:
            kind = "not a valid detection"
        detail += ["    command  %s" % " ".join(cmd),
                   "    exit     %d" % rc,
                   "    intended %s" % expect,
                   "    fails    %s" % (fails if fails else "none"),
                   "    stderr   %s" % (err.strip().splitlines()[-1] if err.strip() else "empty"),
                   "    RESULT   %s (%s)" % (res, kind), ""]
        say("%-4s %-13s %-40s | %s" % (mid, res, (hit[0] if hit else (fails[0] if fails else "-")), desc))

    say("")
    n = len(CASES)
    say("TOTAL CASES %d: detected %d, escaped %d, invalid (wrong-failure) %d, anchor not applied %d"
        % (n, tally["detected"], tally["escaped"], tally["wrong"], tally["anchor"]))
    say("  of the %d detections, %d are supported by the substantive layer and %d are FINGERPRINT-ONLY"
        % (tally["detected"], substantive, fponly))
    say("  a fingerprint-only detection shows that text changed; it is NOT evidence that the")
    say("  substantive checks would notice a wrong expression, and it is not counted as one.")
    say("new Stage 18 cases: G1 G2 G3 T1 T2 N1 S1 F1 (F1 runs under --update-fingerprints) and S2;")
    say("V1 is the proof case for the removed `or True`.")
    with open(RESULTS, 'w') as fh:
        fh.write("Stage 18 mutation campaign -- raw results\n")
        fh.write("repository: %s\n" % ROOT)
        fh.write("suite: audit_stage15/regression.py (version 4, Stage 18)\n")
        fh.write("baseline: exit 0, %d checks passed in a fresh isolated copy\n\n" % BASE_PASSES)
        fh.write("summary\n-------\n")
        fh.write("\n".join(out) + "\n\n")
        fh.write("per-case evidence\n-----------------\n")
        fh.write("\n".join(detail) + "\n")
    say("raw evidence written to " + RESULTS)
    return 0 if (tally["escaped"] == 0 and tally["wrong"] == 0 and tally["anchor"] == 0) else 1


if __name__ == '__main__':
    sys.exit(main())
