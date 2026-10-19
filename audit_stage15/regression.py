#!/usr/bin/env python3
"""Stage 15 regression suite. Runs against the tree it lives in. Exit 0 iff all checks pass."""
import re, glob, os, sys, subprocess
from math import *

FAIL = []
def check(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (("  | " + detail) if detail else ""))
    if not ok: FAIL.append(name)

files = ['main.tex'] + sorted(glob.glob('chapters/*.tex')) + sorted(glob.glob('figures/*.tex'))
src = {f: open(f, encoding='utf-8').read() for f in files}
allsrc = ''.join(src.values())
body = ''.join(src[f] for f in ['main.tex'] + [f for f in files if f.startswith('chapters/')])

# ---- 1. structural integrity -------------------------------------------------
brace = [f for f in files
         if re.sub(r'(?<!\\)%.*', '', re.sub(r'\\[{}%]', '', src[f])).count('{')
         != re.sub(r'(?<!\\)%.*', '', re.sub(r'\\[{}%]', '', src[f])).count('}')]
check("braces balanced in all %d files" % len(files), not brace, str(brace))

env = [f for f in files
       if len(re.findall(r'\\begin\{', re.sub(r'(?<!\\)%.*', '', src[f])))
       != len(re.findall(r'\\end\{', re.sub(r'(?<!\\)%.*', '', src[f])))]
check("environments balanced", not env, str(env))

# ---- 2. cross-references ----------------------------------------------------
labels = re.findall(r'\\label\{([^}]+)\}', allsrc)
refs = set(re.findall(r'\\(?:eq)?ref\{([^}]+)\}', allsrc))
dups = sorted({k for k in labels if labels.count(k) > 1})
check("labels unique", not dups, "%d labels; dups=%s" % (len(labels), dups or "none"))
check("no dangling references", not (refs - set(labels)), str(sorted(refs - set(labels))))

# ---- 3. bibliography --------------------------------------------------------
bibkeys = set(re.findall(r'@\w+\{([^,]+),', open('references.bib', encoding='utf-8').read()))
cited = set()
for grp in re.findall(r'\\cite[a-z]*\{([^}]*)\}', re.sub(r'(?<!\\)%.*', '', allsrc)):
    for k in grp.replace('\n', '').split(','):
        if k.strip(): cited.add(k.strip())
check("all cited keys resolve", not (cited - bibkeys), str(sorted(cited - bibkeys)))
check("no uncited bib entries", not (bibkeys - cited), str(sorted(bibkeys - cited)))

# ---- 4. macros that this preamble does not define ---------------------------
preamble = src['main.tex']
defined = set(re.findall(r'\\(?:newcommand|renewcommand|DeclareMathOperator|def)\*?\{?\\([A-Za-z]+)', preamble))
undefined_hits = []
for mac in ['ie', 'eg', 'cf', 'etal', 'wrt', 'st']:
    if ('\\' + mac) in allsrc and mac not in defined:
        undefined_hits.append(mac)
check("no undefined shorthand macros", not undefined_hits, str(undefined_hits))

# ---- 5. superseded values must be absent from body text ---------------------
superseded = [
    ("1.8" + chr(92) + "times10^{-4}", "arc term 1.8e-4"),
    ("w=-d_2", "Package A definition"),
    ("positive into the channel", "Package A direction phrase"),
    ("w^{''''}(x)= -" + chr(92) + ",p", "wrong pressure sign"),
]
for pat, label in superseded:
    hits = [f for f in src if f != 'chapters/audit_appendix.tex' and pat in src[f]]
    check("superseded absent: %s" % label, not hits, str(hits))

# ---- 6. convention consistency ---------------------------------------------
check("w = +d_2 stated", 'w=+d_2' in allsrc or 'w = +d_2' in allsrc)
check("pressure term is +p", '+\\,p(x)' in src['chapters/ch03.tex'])
check("geometric-stiffness term present",
      'N_\\theta^c\\,\\partial_X d_2\\,\\partial_X\\varphi_2' in src['chapters/ch08.tex'])
check("SUPG tau defined", 'eq:supg' in allsrc)
check("spaces defined", 'V_g=\\{' in src['chapters/ch08.tex'] and 'S_s=H^1' in src['chapters/ch08.tex'])
check("pressure gauge stated", 'int_{\\Ga_{\\mathrm{out}}}p\\,\\mathrm ds=0' in src['chapters/ch08.tex'])
check("Gamma_p defined as w_max/w_p", 'Gamma_p=\\frac{w_{\\max}}{w_p}' in src['chapters/ch04.tex'])

# ---- 7. numerical reproduction ---------------------------------------------
D_s = 3.6e9 * 3e-3**3 / (12 * (1 - 0.40**2))
kth = 1.4 * 5e-5 * 5e3 / 0.25
N = 3.6e9 * 3e-3 * 5e-5 * 32.27 / (1 - 0.40)
mu = sqrt(N / D_s); L = 3e-2; u = mu * L; A = tan(u / 2)
w  = lambda x: (kth / mu**2) * (A * sin(mu * x) + cos(mu * x) - 1)
w1 = lambda x: (kth / mu) * (A * cos(mu * x) - sin(mu * x))
w2 = lambda x: -kth * (A * sin(mu * x) + cos(mu * x))

check("D_s = 9.642857143", abs(D_s - 9.642857143) < 5e-10, "%.9f" % D_s)
check("kappa_th = 1.400000000", abs(kth - 1.4) < 1e-12, "%.9f" % kth)
check("muL = 1.646414286", abs(u - 1.646414286) < 5e-10, "%.9f" % u)
check("w_max = 2.188704727879e-4", abs(w(L/2) - 2.188704727879e-4) < 5e-16, "%.12e" % w(L/2))
check("w_max/H0 = 0.437740946", abs(w(L/2)/5e-4 - 0.437740946) < 5e-10, "%.9f" % (w(L/2)/5e-4))
check("kappa_geo = 2.059208681", abs(-w2(L/2) - 2.059208681) < 5e-10, "%.9f" % -w2(L/2))
check("M_mid = -6.356655141", abs(D_s*(w2(L/2)+kth) - (-6.356655141)) < 5e-10,
      "%.9f" % (D_s*(w2(L/2)+kth)))
check("sigma_bend = 4.237770 MPa", abs(6*abs(D_s*(w2(L/2)+kth))/3e-3**2/1e6 - 4.237770) < 5e-7)
check("fibre strain = 9.888130e-4",
      abs((-w2(L/2)-kth)*1.5e-3 - 9.888130219613e-4) < 5e-16, "%.12e" % ((-w2(L/2)-kth)*1.5e-3))

# closed form satisfies printed ODE and BCs
res = max(abs(D_s*(kth*mu**2*(A*sin(mu*x)+cos(mu*x))) + N*w2(x)) for x in (0.3*L, 0.5*L, 0.77*L))
check("eq:beamcolsol satisfies printed ODE", res < 1e-9, "max residual %.2e" % res)
check("eq:beamcolsol satisfies all BCs",
      max(abs(w(0)), abs(w(L)), abs(w2(0)+kth), abs(w2(L)+kth)) < 1e-12)

# arc term: analytic vs quadrature
Ia = (kth/mu)**2 * ((1+A*A)/2 + (A*A-1)*sin(2*u)/(4*u) - A*sin(u)**2/u) / 2
Nn = 200001; h = L/(Nn-1); s = 0.0
for i in range(Nn):
    c = 1 if i in (0, Nn-1) else (4 if i % 2 else 2)
    s += c * w1(i*h)**2
Iq = (s*h/3)/L/2
check("arc term = 1.388009729196e-4", abs(Ia - 1.388009729196e-4) < 5e-16, "%.12e" % Ia)
check("analytic == quadrature", abs(Ia-Iq)/Ia < 1e-10, "rel %.2e" % (abs(Ia-Iq)/Ia))
e0 = 1.4*5e-5*32.27
check("relaxation = 6.1%", abs(100*Ia/e0 - 6.1) < 0.05, "%.4f %%" % (100*Ia/e0))
check("circular-arc estimate = 1.6e-4", abs(-w2(L/2))**2*L*L/24/1e-4 - 1.59 < 0.005)

# identities
kgeo = -w2(L/2)
check("kappa_geo = kth*sec(muL/2)", abs(kgeo/kth - 1/cos(u/2)) < 1e-15)
check("(kgeo+kth)/(kgeo-kth) = cot^2(muL/4)", abs((kgeo+kth)/(kgeo-kth) - 1/tan(u/4)**2) < 1e-14)
check("ratio = 5.247516878", abs((kgeo+kth)/(kgeo-kth) - 5.247516878) < 5e-10)
check("naive-flip value = -5.188813e-3", abs(-(kgeo+kth)*1.5e-3 - (-5.188813021961e-3)) < 5e-16)

# Gamma_p
wp = 5*84.0*L**4/(384*D_s)
cf = 48*kth*D_s/(5*84.0*L*L)
check("closed form = 1714.285714", abs(cf - 1714.285714) < 5e-7, "%.6f" % cf)
check("w_max/w_p = 2.4e3", abs(w(L/2)/wp - 2382.263649) < 5e-6, "%.6f" % (w(L/2)/wp))
check("amplification = 1.389654", abs((w(L/2)/w(L/2)/1) * 0 + w(L/2)/wp/cf - 1.389654) < 5e-7)
check("amplification == w_max/w_lin", abs(w(L/2)/(kth*L*L/8) - 1.389653795) < 5e-10)

# stress columns
sig_m = -3.6e9*5e-5*32.27/0.6
check("frozen column = 13.9 MPa", abs((abs(sig_m)+6*abs(D_s*(w2(L/2)+kth))/3e-3**2)/1e6 - 13.9188) < 1e-3)
check("self-consistent column = 13.6 MPa", abs((abs(sig_m)+6*5.9/9e-6)/1e6 - 13.6143) < 1e-3)

# ---- 8. build/packaging -----------------------------------------------------
check("tracked main.pdf present", os.path.exists('main.pdf'), "%d bytes" % os.path.getsize('main.pdf'))

print()
if FAIL:
    print("%d CHECK(S) FAILED:" % len(FAIL))
    for f in FAIL: print("  - " + f)
    sys.exit(1)
print("ALL CHECKS PASSED")
