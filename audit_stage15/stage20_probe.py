#!/usr/bin/env python3
"""Stage 20 targeted probe for findings F-1 to F-4.

Ten cases, each in a fresh copy of the repository, after a clean baseline:
  F2  the gauge explanation is deleted from the formulation        -> must FAIL
  F3a "on the outer face $\\Gamma_h^0$" (legitimate)               -> must PASS
  F3b fronted "On $\\Gamma_h^0$ the solid carries the flux"        -> must PASS
  F3c "is applied on the heated face" (legitimate, words)          -> must PASS
  F3d a solid flux datum placed on $\\Gamma_{if}$ in prose          -> must FAIL
  F3e a double thermal datum with no surface named                 -> must FAIL
  F4  w''=-kappa_th changed to -kappa_th/2 WITH fingerprint regen   -> must FAIL substantively
  F1a the mid-surface statement removed                            -> must FAIL
  F1b the withdrawn "shifts with the through-thickness" claim back  -> must FAIL
  E1  an extra & makes register row D-35 over-full, WITH regen      -> must FAIL

This is a probe of the four repaired findings, not a general mutation campaign.

Run from the repository root:  python3 audit_stage15/stage20_probe.py
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath('.')
BASE = '/tmp/hff_probe20'
BS = '\\'
FP_CHECKS = {'no display equation has changed', 'no register row has changed',
             'no equation or register row removed'}


def run(d, regen=False):
    cmd = [sys.executable, 'audit_stage15/regression.py'] + (['--update-fingerprints'] if regen else [])
    p = subprocess.run(cmd, cwd=d, capture_output=True, text=True)
    fails = [l[6:].split('|')[0].strip() for l in p.stdout.splitlines() if l.startswith('FAIL')]
    return p.returncode, fails, p.stdout, p.stderr


def clone(tag):
    d = os.path.join(BASE, tag)
    if os.path.exists(d):
        shutil.rmtree(d)
    shutil.copytree(ROOT, d, ignore=shutil.ignore_patterns('.git'))
    return d


def apply(d, rel, old, new):
    p = os.path.join(d, rel)
    t = open(p, encoding='utf-8').read()
    if t.count(old) != 1:
        return t.count(old)
    open(p, 'w', encoding='utf-8').write(t.replace(old, new, 1))
    return 1


CASES = [
    ('F2', 'F-2 gauge explanation deleted from the formulation', 'must fail', 'chapters/ch08.tex',
     ('\\emph{No pressure gauge is required.} The additive\n'
      'constant that afflicts a velocity-prescribed Stokes problem is removed here by the outflow condition\n'
      'B2: because $\\mathbf v$ is not divergence-free, $b(\\mathbf v,1)=-\\int_{\\Om_f}\\nabla\\cdot\\mathbf v\n'
      '\\,\\mathrm dx=-\\int_{\\Ga_{\\mathrm{out}}}\\mathbf v\\cdot\\bn\\,\\mathrm ds$ is not zero for every\n'
      'admissible test function, so constants are \\emph{not} in the kernel of $b(\\cdot,1)$ and $p$ is\n'
      'determined absolutely. The natural condition at $\\Ga_{\\mathrm{out}}$ together with a developed exit\n'
      'profile then leaves $p\\to0$ across that section. Constraining, say, $\\int_{\\Ga_{\\mathrm{out}}}p\\,\n'
      '\\mathrm ds=0$ as an extra equation would over-determine the system and, with a Lagrange multiplier,\n'
      'inject a spurious outlet mass source (register D-25, corrected in D-30).'),
     'The outflow condition of B2 fixes the level (register D-25, corrected in D-30).',
     'the formulation itself states why no pressure gauge is imposed'),

    ('F3a', 'F-3 legitimate: flux "on the outer face $Gamma_h^0$"', 'must pass', 'chapters/ch08.tex',
     'The level that results is reported with every',
     ('The solid carries $+k_s' + BS + 'nabla T_s' + BS + 'cdot' + BS + 'bn_{' + BS + 'mathrm{out}}=q^{'
      + "''" + '}$ on the outer face $' + BS + 'Ga_h^0$. The level that results is reported with every'),
     None),

    ('F3b', 'F-3 legitimate: fronted "On $Gamma_h^0$ the solid carries"', 'must pass', 'chapters/ch08.tex',
     'The level that results is reported with every',
     ('On $' + BS + 'Ga_h^0$ the solid carries the prescribed flux $+k_s' + BS + 'nabla T_s' + BS + 'cdot'
      + BS + 'bn_{' + BS + 'mathrm{out}}=q^{' + "''" + '}$. The level that results is reported with every'),
     None),

    ('F3c', 'F-3 legitimate: "is applied on the heated face" (words)', 'must pass', 'chapters/ch08.tex',
     'The level that results is reported with every',
     ('The prescribed flux $+k_s' + BS + 'nabla T_s' + BS + 'cdot' + BS + 'bn_{' + BS + 'mathrm{out}}=q^{'
      + "''" + '}$ is applied on the heated face. The level that results is reported with every'),
     None),

    ('F3d', 'F-3 NEGATIVE: solid flux datum on the interface in prose', 'must fail', 'chapters/ch08.tex',
     'The level that results is reported with every',
     ('The solid receives the interface flux $+k_s' + BS + 'nabla T_s' + BS + 'cdot' + BS + 'bn=q^{' + "''"
      + '}/k_s$ on $' + BS + 'Ga_{' + BS + 'mathrm{if}}$. The level that results is reported with every'),
     'no solid flux datum is imposed on Gamma_if anywhere in the formulation'),

    ('F3e', 'F-3 NEGATIVE: double thermal datum, no surface named', 'must fail', 'chapters/ch08.tex',
     'The level that results is reported with every',
     ('The solid is handed the interface temperature $T_s=T_' + BS + 'Gamma^{(k)}$ together with the '
      'interface flux $' + BS + 'partial_nT_s=q_' + BS + 'Gamma^{(k)}/k_s$. '
      'The level that results is reported with every'),
     'no prose datum gives the solid a temperature AND a non-heated-face heat flux in one sentence'),

    ('F4', 'F-4 eq:beamcol end moment halved, fingerprints REGENERATED', 'must fail', 'chapters/ch04.tex',
     'w^{' + "''" + '}(0)=w^{' + "''" + '}(L)=-@kappa_{@mathrm{th}},'.replace('@', BS),
     'w^{' + "''" + '}(0)=w^{' + "''" + '}(L)=-@tfrac12@kappa_{@mathrm{th}},'.replace('@', BS),
     'eq:beamcol states the zero total end moment'),

    ('F1a', 'F-1 the mid-surface statement is removed', 'must fail', 'chapters/ch04.tex',
     ', all sampled at the mid-surface of the strip ($y=d/2$)', '', 
     'ch04 states that the Q8 ratios are sampled at the mid-surface'),

    ('F1b', 'F-1 the withdrawn through-thickness claim returns', 'must fail', 'chapters/ch04.tex',
     'The clamp magnitude is not\nmesh-converged:',
     'The absolute ratios shift with the through-thickness discretisation. The clamp magnitude is not\nmesh-converged:',
     'the withdrawn claim that the Q8 ratios shift with the through-thickness mesh is absent'),

    ('E1', 'S20-E an extra & makes register row D-35 over-full', 'must fail', 'chapters/audit_appendix.tex',
     'resolved (Stage 20) ' + BS*2,
     'resolved (Stage 20) & overflow ' + BS*2,
     'every table row has exactly its declared number of cells'),
]


def main():
    os.makedirs(BASE, exist_ok=True)
    base = clone('baseline')
    rc, fails, out, err = run(base)
    print('BASELINE  exit %d, %d PASS, %d FAIL' % (rc, out.count('\nPASS'), len(fails)))
    if rc != 0:
        print('baseline fails; aborting')
        return 2
    ok = 0
    rows = []
    for tag, desc, expect, rel, old, new, want in CASES:
        d = clone(tag)
        n = apply(d, rel, old, new)
        if n != 1:
            rows.append((tag, desc, 'ANCHOR (%d)' % n, '', ''))
            print('%-5s %-56s ANCHOR not applied (%d)' % (tag, desc, n))
            continue
        rc, fails, out, err = run(d, regen=tag in ('F4', 'E1'))
        if expect == 'must pass':
            verdict = 'PASS' if rc == 0 else 'FALSE POSITIVE'
        else:
            hit = [f for f in fails if f.startswith(want)]
            substantive = [f for f in fails if f not in FP_CHECKS]
            if rc == 0:
                verdict = 'ESCAPED'
            elif not substantive:
                verdict = 'FINGERPRINT-ONLY'
            elif hit:
                verdict = 'DETECTED'
            else:
                verdict = 'WRONG FAILURE'
        good = (verdict == 'PASS' if expect == 'must pass' else verdict == 'DETECTED')
        ok += 1 if good else 0
        rows.append((tag, desc, verdict, rc, fails[0] if fails else '-'))
        print('%-5s %-56s %-14s exit %s | %s' % (tag, desc, verdict, rc, (fails[0][:60] if fails else '-')))
    print()
    print('%d of %d cases behaved as intended' % (ok, len(CASES)))
    with open('audit_stage15/stage20_probe_results.txt', 'w') as fh:
        fh.write('Stage 20 targeted probe of findings F-1 to F-4\n')
        fh.write('repository: %s\n' % ROOT)
        fh.write('baseline: exit 0, %d checks passed\n\n' % out.count('\nPASS'))
        for tag, desc, verdict, rc, f in rows:
            fh.write('%-5s %-56s %-14s exit %-3s %s\n' % (tag, desc, verdict, rc, f))
        fh.write('\n%d of %d cases behaved as intended\n' % (ok, len(CASES)))
    return 0 if ok == len(CASES) else 1


if __name__ == '__main__':
    sys.exit(main())
