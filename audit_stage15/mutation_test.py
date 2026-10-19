#!/usr/bin/env python3
"""Mutation tests for the Stage 16 regression suite.

Each mutation is applied to an ISOLATED COPY of the repository; the repository itself is never
modified. The baseline copy must PASS and every mutant must FAIL for the suite to be adequate.

Run from the repository root:  python3 audit_stage15/mutation_test.py
"""
import os, shutil, subprocess, sys, hashlib

BS = chr(92)
ROOT = os.path.abspath('.')
WORK = '/tmp/hff_mut'

MUTATIONS = [
    ("m1 corrupt printed w_max (2.19e-4 -> 2.29e-4)", 'chapters/ch04.tex',
     'w_{'+BS+'max}=2.19', 'w_{'+BS+'max}=2.29'),
    ("m2 flip geometric-stiffness sign", 'chapters/ch08.tex',
     '-'+BS+'int_{'+BS+'Om_s^0}'+BS+'frac{N_'+BS+'theta^c}{d}',
     '+'+BS+'int_{'+BS+'Om_s^0}'+BS+'frac{N_'+BS+'theta^c}{d}'),
    ("m3 reverse the bow direction", 'chapters/ch02.tex',
     'bows away from the channel', 'bows into the channel'),
    ("m4 change Poisson ratio 0.40 -> 0.30", 'chapters/ch02.tex',
     'Poisson ratio', None),      # handled specially below
    ("m5 drop the 1/d factor in the geometric term", 'chapters/ch08.tex',
     BS+'frac{N_'+BS+'theta^c}{d}'+BS+',', 'N_'+BS+'theta^c'+BS+','),
    ("m6 replace the pin by a full-edge clamp", 'chapters/ch05.tex',
     '$d_2=0$, $'+BS+'langle d_1'+BS+'rangle=0$', '$d_1=d_2=0$'),
]

def clone(dst):
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('.git', 'project_archive'))

def run(dst):
    p = subprocess.run([sys.executable, 'audit_stage15/regression.py'], cwd=dst,
                       capture_output=True, text=True)
    failed = [l.split('|')[0].replace('FAIL','').strip()
              for l in p.stdout.splitlines() if l.startswith('FAIL')]
    return p.returncode, failed

def apply_nu(dst):
    path = os.path.join(dst, 'chapters/ch02.tex')
    t = open(path, encoding='utf-8').read()
    i = t.find('PEEK Poisson ratio')
    assert i >= 0, "Poisson ratio row not found"
    j = t.find('0.40', i)
    assert j >= 0 and j - i < 200, "value 0.40 not found in the Poisson row"
    t = t[:j] + '0.30' + t[j+4:]
    open(path, 'w', encoding='utf-8').write(t)

results, ok_all = [], True
base = os.path.join(WORK, 'baseline')
clone(base)
rc, failed = run(base)
print("%-52s exit=%d  %s" % ("BASELINE (must pass)", rc, "PASS" if rc == 0 else "FAIL " + str(failed)))
if rc != 0: ok_all = False
results.append(("baseline", "pass" if rc == 0 else "fail", failed))

for name, relpath, old, new in MUTATIONS:
    dst = os.path.join(WORK, name.split()[0])
    clone(dst)
    if new is None:
        apply_nu(dst)
    else:
        path = os.path.join(dst, relpath)
        t = open(path, encoding='utf-8').read()
        n = t.count(old)
        assert n >= 1, "mutation anchor missing: %r in %s" % (old, relpath)
        open(path, 'w', encoding='utf-8').write(t.replace(old, new))
    rc, failed = run(dst)
    caught = rc != 0
    ok_all = ok_all and caught
    print("%-52s exit=%d  %s  %s" % (name, rc, "CAUGHT" if caught else "*** MISSED ***",
                                     "; ".join(failed[:3])))

print()
print("MUTATION ADEQUACY:", "ALL MUTANTS CAUGHT" if ok_all else "*** SUITE INADEQUATE ***")
sys.exit(0 if ok_all else 1)
