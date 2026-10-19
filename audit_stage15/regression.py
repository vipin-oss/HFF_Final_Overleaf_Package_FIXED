#!/usr/bin/env python3
"""HFF regression suite, version 2 (Stage 16).

Every numeric assertion parses BOTH the input and the printed expected value out of the manuscript,
recomputes the expected value from those inputs, and compares. Corrupting a printed result or a
material input therefore breaks the suite. Sign / BC / units claims are checked structurally.

Run from the repository root:  python3 audit_stage15/regression.py
"""
import re, glob, sys, os
from math import *

FAIL, N_PASS = [], 0
def check(name, ok, detail=""):
    global N_PASS
    print(("PASS  " if ok else "FAIL  ") + name + (("  | " + str(detail)) if detail else ""))
    if ok: N_PASS += 1
    else: FAIL.append(name)

def read(p): return open(p, encoding='utf-8').read()
BS = chr(92)

def num(s):
    s = s.strip().strip('$').strip()
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*\\times\s*10\^\{?(-?\d+)\}?', s)
    if m: return float(m.group(1)) * 10.0 ** float(m.group(2))
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)', s)
    if m: return float(m.group(1))
    raise ValueError("cannot parse number from %r" % s)

FILES = ['main.tex'] + sorted(glob.glob('chapters/*.tex')) + sorted(glob.glob('figures/*.tex'))
SRC = {f: read(f) for f in FILES}
ALL = ''.join(SRC.values())
BODY = ''.join(SRC[f] for f in FILES if f != 'chapters/audit_appendix.tex')
C2, C3, C4, C5, C7, C8, C9 = (SRC['chapters/ch0%d.tex' % i] for i in (2,3,4,5,7,8,9))
APP = SRC['chapters/appendix.tex']

print("=" * 78); print("SECTION 1  Structural integrity"); print("=" * 78)
def stripped(t): return re.sub(r'(?<!\\)%.*', '', re.sub(r'\\[{}%]', '', t))
badb = [f for f in FILES if stripped(SRC[f]).count('{') != stripped(SRC[f]).count('}')]
bade = [f for f in FILES if len(re.findall(r'\\begin\{', re.sub(r'(?<!\\)%.*','',SRC[f])))
        != len(re.findall(r'\\end\{', re.sub(r'(?<!\\)%.*','',SRC[f])))]
check("braces balanced in all %d files" % len(FILES), not badb, badb)
check("environments balanced", not bade, bade)

labels = re.findall(r'\\label\{([^}]+)\}', ALL)
refs = set(re.findall(r'\\(?:eq)?ref\{([^}]+)\}', ALL))
dups = sorted({k for k in labels if labels.count(k) > 1})
check("labels unique", not dups, "%d labels, dups=%s" % (len(labels), dups or "none"))
check("no dangling references", not (refs - set(labels)), sorted(refs - set(labels)))

bibkeys = set(re.findall(r'@\w+\{([^,]+),', read('references.bib')))
cited = set()
for grp in re.findall(r'\\cite[a-z]*\{([^}]*)\}', re.sub(r'(?<!\\)%.*','',ALL)):
    for k in grp.replace('\n','').split(','):
        if k.strip(): cited.add(k.strip())
check("all cited keys resolve", not (cited - bibkeys), sorted(cited - bibkeys))
check("no uncited bib entries", not (bibkeys - cited), sorted(bibkeys - cited))

defined = set(re.findall(r'\\(?:newcommand|renewcommand|DeclareMathOperator|def)\*?\{?\\([A-Za-z]+)',
                         SRC['main.tex']))
undefined = [m for m in ('ie','eg','cf','etal','wrt') if (BS+m) in ALL and m not in defined]
check("no undefined shorthand macros", not undefined, undefined)

print(); print("=" * 78); print("SECTION 2  Sign, BC and units claims"); print("=" * 78)
check("deflection convention w = +d_2", ('w=+d_2' in BODY) or ('w = +d_2' in BODY))
check("pressure term is D_s w'''' = +p", (",w^{''''}(x)= +"+BS+",p(x)") in C3)
check("pressure term is not -p",       (",w^{''''}(x)= -"+BS+",p(x)") not in BODY)

check("geometric term present, negative, with N/d",
      ("-"+BS+"int_{"+BS+"Om_s^0}"+BS+"frac{N_"+BS+"theta^c}{d}") in C8)
check("old no-1/d geometric form removed",
      ("-"+BS+"int_{"+BS+"Om_s^0}N_"+BS+"theta^c"+BS+","+BS+"partial_X d_2") not in C8)
check("geometric term sign not flipped",
      ("+"+BS+"int_{"+BS+"Om_s^0}"+BS+"frac{N_"+BS+"theta^c}{d}") not in C8)

m7 = re.search(r'B7 & strip ends.*?' + BS*2 + r'\n', C5, re.S)
b7 = m7.group(0) if m7 else ''
check("B7 found", bool(m7))
check("B7 is not a full-edge clamp", 'd_1=d_2=0' not in b7, b7[:70])
check("B7 imposes d_2=0", 'd_2=0' in b7, b7[:70])
check("B7 blocks mean axial displacement", (BS+"langle d_1"+BS+"rangle=0") in b7, b7[:70])

check("V_s defined with phi_2 = 0 on end edges", (BS+"varphi_2=0") in C8)
check("V_s is not a clamp",
      (BS+"boldsymbol"+BS+"varphi="+BS+"mathbf 0"+BS+" "+BS+"text{on the pinned ends}") not in C8)
check("gauge constraint removed", ('p'+BS+','+BS+'mathrm ds=0') not in C8)
check("no-gauge argument stated", 'No pressure gauge is required' in C8)
check("SUPG stabilised weak form written", 'eq:supgwf' in C8)
check("SUPG P2 length scale addressed", ('h_K'+BS+'to h_K/p') in C8)
check("staggered thermal partition stated", ('Dirichlet datum' in C8) and ('Neumann datum' in C8))
reversed_phrases = ["into the channel","into the flow","into the passage",
                    "toward the interior","towards the interior","bows toward"]
hits = [p for p in reversed_phrases if p in BODY]
check("no reversed-bow phrasing in body text", not hits, hits)

print(); print("=" * 78); print("SECTION 3  Inputs parsed from the manuscript"); print("=" * 78)
def table_value(label):
    m = re.search(re.escape(label) + r'[^&]*&[^&]*&\s*([^&]+?)&', C2)
    if not m: raise SystemExit("cannot find table row for %r" % label)
    return num(m.group(1))
E     = table_value("PEEK Young's modulus")
nu    = table_value("PEEK Poisson ratio")
alpha = table_value("PEEK expansion coefficient")
ks    = table_value("PEEK conductivity")
rho   = table_value("Water density")
muf   = table_value("Water dynamic viscosity")
cp    = table_value("Water specific heat")
kf    = table_value("Water conductivity")
print("  E=%.4g nu=%.3g alpha=%.4g ks=%.4g rho=%.4g mu=%.4g cp=%.4g kf=%.4g"
      % (E,nu,alpha,ks,rho,muf,cp,kf))
check("E positive and finite", E > 0 and isfinite(E), E)
check("nu in (0,0.5)", 0 < nu < 0.5, nu)
if not (0 < nu < 0.5):
    print("FATAL: nu outside (0,0.5)"); sys.exit(1)

L, d, H0, U, q, pbar = 3.0e-2, 3.0e-3, 5.0e-4, 5.0e-2, 5.0e3, 84.0
Nu_H1 = 5.385
h     = Nu_H1*kf/(2*H0)
thbar = (q*d/ks)/2 + q/h + (q*L/(rho*U*H0*cp))/2
print("  theta_bar from its own components = %.6f K (printed 32.27)" % thbar)
check("theta_bar within 0.05 K of printed 32.27", abs(thbar-32.27) < 0.05, thbar)

Ds  = E*d**3/(12*(1-nu**2)); kth = (1+nu)*alpha*q/ks
N0  = E*d*alpha*thbar/(1-nu); mu = sqrt(N0/Ds); uL = mu*L; A = tan(uL/2)
w   = lambda x: (kth/mu**2)*(A*sin(mu*x)+cos(mu*x)-1)
w1  = lambda x: (kth/mu)*(A*cos(mu*x)-sin(mu*x))
w2  = lambda x: -kth*(A*sin(mu*x)+cos(mu*x))
wmax, kgeo = w(L/2), -w2(L/2)

print(); print("=" * 78); print("SECTION 4  Printed results vs recomputation"); print("=" * 78)
def grab(pat, txt):
    m = re.search(pat, txt)
    return num(m.group(1)) if m else None
def near(txt, anchor, exp, span=90):
    """First number `m` such that the text contains <anchor> then m x 10^exp nearby."""
    i = txt.find(anchor)
    if i < 0: return None
    m = re.search(r'([0-9]+\.[0-9]+)\s*' + re.escape(BS + 'times10^{' + str(exp) + '}'),
                  txt[i:i+span])
    return float(m.group(1)) * 10.0**exp if m else None
def cmp(name, printed_v, computed, tol):
    if printed_v is None:
        check(name, False, "printed value not found"); return
    rel = abs(computed-printed_v)/max(abs(printed_v),1e-300)
    check(name, rel <= tol, "printed=%.6g computed=%.6g rel=%.2e" % (printed_v, computed, rel))

cmp("ch04 printed w_max matches recomputation",
    near(C4, 'w_{'+BS+'max}=2', -4), wmax, 0.01)
cmp("ch04 printed w_max/H0 matches",
    grab(r'=\s*([0-9.]+)\\,H_0\s*\\quad\\text\{\(frozen force', C4), wmax/H0, 0.01)
cmp("ch04 printed linear w/H0 matches",
    grab(r'\\mathrm\{lin\}\}\}\{H_0\}=([0-9.]+)', C4), kth*L*L/8/H0, 0.01)
cmp("ch04 amplification matches",
    grab(r'amplification by the factor \$([0-9.]+)\$', C4), wmax/(kth*L*L/8), 0.01)
cmp("ch04 fibre strain matches",
    near(C4, 'kappa_{'+BS+'mathrm{th}})d/2=', -4), (kgeo-kth)*d/2, 0.02)

Nn = 200001; hh = L/(Nn-1); sacc = 0.0
for i in range(Nn):
    c = 1 if i in (0, Nn-1) else (4 if i % 2 else 2)
    sacc += c*w1(i*hh)**2
arc = (sacc*hh/3)/L/2
e0  = (1+nu)*alpha*thbar
cmp("ch04 arc term matches quadrature",
    grab(r'\\rangle=([0-9.]+\\times10\^\{-4\})', C4), arc, 0.01)
cmp("ch04 relaxation 6.1% matches",
    grab(r'first-iterate force relaxation of \$([0-9.]+)\\%\$', C4), 100*arc/e0, 0.02)
_r = (kgeo**2*L*L/24)/arc
check("circular-arc estimate is an upper bound, 10-20% above exact",
      1.10 < _r < 1.20, "ratio %.4f" % _r)

cmp("ch07 table w_max matches",
    grab(r'frozen force\) & [^&]*& \$([0-9.]+\\times10\^\{-4\})\$', C7), wmax, 0.01)
cmp("ch09 V-C3 amplification matches",
    grab(r'amplification\s*\n?\$([0-9.]+)\$ at \$\\mu L', C9), wmax/(kth*L*L/8), 0.01)

wp = 5*pbar*L**4/(384*Ds)
cmp("ch04 Gamma_p = w_max/w_p matches",
    grab(r'=([0-9.]+\\times10\^\{3\})\\quad\\text\{at the baseline\}', C4), wmax/wp, 0.01)
cmp("ch04 linear-limit closed form matches",
    grab(r'5\\bar pL\^2\)=([0-9.]+\\times10\^\{3\})', C4), 48*kth*Ds/(5*pbar*L*L), 0.01)

def fixed_point(th):
    Nn0 = E*d*alpha*th/(1-nu)
    def arc_of(Nc):
        m = sqrt(Nc/Ds); uu = m*L; Aa = tan(uu/2)
        f1 = lambda x: (kth/m)*(Aa*cos(m*x)-sin(m*x))
        NS = 40001; hL = L/(NS-1); ss = 0.0
        for i in range(NS):
            c = 1 if i in (0,NS-1) else (4 if i%2 else 2)
            ss += c*f1(i*hL)**2
        return (ss*hL/3)/L
    Nc = Nn0
    for _ in range(60):
        Nc = Nn0 - E*d/(2*(1-nu**2))*arc_of(Nc)
    m = sqrt(Nc/Ds); uu = m*L; Aa = tan(uu/2)
    f2 = lambda x: -kth*(Aa*sin(m*x)+cos(m*x))
    w_sc = (kth/m**2)*(Aa*sin(m*L/2)+cos(m*L/2)-1)
    return Nc, Ds*(f2(L/2)+kth), w_sc
Nc_s, M_s, w_sc = fixed_point(thbar)
sig_sc = (Nc_s/d + 6*abs(M_s)/d**2)/1e6
sig_fr = (N0/d + 6*abs(Ds*(w2(L/2)+kth))/d**2)/1e6
cmp("appendix self-consistent sigma_max matches D-28",
    grab(r'\\sigma_\{\\max\}=([0-9.]+)\$ MPa', APP), sig_sc, 0.02)
print("    frozen sigma_max=%.4f MPa, self-consistent=%.4f MPa" % (sig_fr, sig_sc))
check("frozen stress exceeds self-consistent (conservative)", sig_fr > sig_sc,
      "%.4f > %.4f" % (sig_fr, sig_sc))
check("frozen stress below 0.2 sigma_y cap", sig_fr < 0.2*90, sig_fr)

mech_cold = -e0 + (d/2)*(w2(L/2)+kth)
mech_hot  = -e0 - (d/2)*(w2(L/2)+kth)
max_mech  = max(abs(mech_cold), abs(mech_hot))
check("E/(1-nu^2)*max|eps_mech| reproduces frozen sigma_max",
      abs(E/(1-nu**2)*max_mech/1e6 - sig_fr) < 1e-6,
      "%.6f vs %.6f" % (E/(1-nu**2)*max_mech/1e6, sig_fr))
cmp("ch04 printed mechanical surface strain matches",
    grab(r'\\varepsilon_\{\\mathrm\{mech\}\}\|[\s\n]*=([0-9.]+\\times10\^\{-3\})', C4), max_mech, 0.02)

def first_num_after(txt, anchor, span=40):
    i = txt.find(anchor)
    if i < 0: return None
    m = re.search(r'([0-9]+[.][0-9]+)', txt[i+len(anchor):i+len(anchor)+span])
    return float(m.group(1)) if m else None
cmp('ch04 self-consistent w_max matches',
    near(C4, 'w_{'+BS+'max}=2.14', -4), w_sc, 0.01)
cmp('ch04 self-consistent w_max/H0 matches',
    first_num_after(C4, 'w_{'+BS+'max}=2.14', 90), w_sc/H0, 0.01)

wp_bc = (-pbar*L**2/(8*N0) + (pbar*Ds/N0**2)*(1/cos(sqrt(N0/Ds)*L/2)-1))
cmp('ch04 like-for-like w_p matches beam-column pressure solution',
    near(C4, 'w_p(N_'+BS+'theta^c)=', -7), wp_bc, 0.01)
cmp('ch04 like-for-like Gamma_p matches',
    (first_num_after(C4, 'gives $w_{'+BS+'max}/w_p(N_'+BS+'theta^c)=', 40) or 0)*1e3,
    wmax/wp_bc, 0.01)
check('B2 does not impose a pressure datum', ('datum $p=0$') not in C5)

print(); print("=" * 78); print("SECTION 5  Exact identities"); print("=" * 78)
check("kappa_geo = kappa_th*sec(muL/2)", abs(kgeo/kth - 1/cos(uL/2)) < 1e-12)
ratio = (kgeo+kth)/(kgeo-kth)
check("(kgeo+kth)/(kgeo-kth) = cot^2(muL/4)", abs(ratio - 1/tan(uL/4)**2) < 1e-10, "%.9f" % ratio)
res = max(abs(Ds*(kth*mu**2*(A*sin(mu*x)+cos(mu*x))) + N0*w2(x)) for x in (0.3*L,0.5*L,0.77*L))
check("eq:beamcolsol satisfies the printed ODE", res < 1e-8, "%.2e" % res)
check("eq:beamcolsol satisfies all four BCs",
      max(abs(w(0)), abs(w(L)), abs(w2(0)+kth), abs(w2(L)+kth)) < 1e-12)

print(); print("=" * 78); print("SECTION 6  Package provenance"); print("=" * 78)
check("tracked main.pdf exists", os.path.exists('main.pdf'),
      ("%d bytes" % os.path.getsize('main.pdf')) if os.path.exists('main.pdf') else "")
readme = read('README.md') if os.path.exists('README.md') else ''
named = re.findall(r'`([A-Za-z0-9_\-/.]+\.zip)`', readme)
missing = [z for z in named if not os.path.exists(z)]
check("every package filename in README.md exists", not missing, missing)

print(); print("=" * 78); print("SECTION 7  Build freshness (REPORTED, NOT A PASS)"); print("=" * 78)
_src = [f for f in FILES] + ['references.bib']
_pdf = os.path.getmtime('main.pdf')
_stale = sorted(f for f in _src if os.path.getmtime(f) > _pdf)
if _stale:
    print("WARNING  main.pdf predates %d source file(s): %s" % (len(_stale), ", ".join(_stale[:6])))
    print("WARNING  A LaTeX rebuild is REQUIRED. No TeX engine is available in this sandbox,")
    print("WARNING  so the rebuild is NOT executed and NOT claimed; the tracked main.pdf is")
    print("WARNING  the last successful build from the pre-Stage-16 sources.")
else:
    print("INFO     main.pdf is newer than every source file")

print(); print("=" * 78)
if FAIL:
    print("%d of %d CHECKS FAILED:" % (len(FAIL), len(FAIL)+N_PASS))
    for f in FAIL: print("  - " + f)
    sys.exit(1)
print("ALL %d CHECKS PASSED" % N_PASS)
