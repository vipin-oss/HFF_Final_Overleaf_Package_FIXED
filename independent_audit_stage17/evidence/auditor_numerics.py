#!/usr/bin/env python3
"""Auditor's independent recomputation of the Stage 17 numerical chain.

Inputs are parsed out of the manuscript (ch02 Table tab:geometry, ch02 Table tab:props,
ch09 V-B2 for the Nusselt coefficient used by the manuscript's own theta-bar estimate).
Nothing is imported from audit_stage15/regression.py: the formulas below are written from
the manuscript's equations (ch04 eq:nthet, eq:wmax, eq:beamcolsol, eq:gammap) and the
printed values are scraped from the text.  Read-only.
"""
import re, math

def read(p): return open(p, encoding='utf-8').read()
C2 = read('chapters/ch02.tex'); C4 = read('chapters/ch04.tex')
C7 = read('chapters/ch07.tex'); APP = read('chapters/appendix.tex'); C9 = read('chapters/ch09.tex')

def si(label):
    for line in C2.split('\n'):
        if line.startswith(label):
            return float(re.search(r'\\SI\{([0-9.eE+-]+)\}', line).group(1))
def row(label):
    m = re.search(re.escape(label) + r'[^&]*&[^&]*&\s*([^&]+?)&', C2)
    s = m.group(1).strip()
    m2 = re.fullmatch(r'\$?(-?[0-9.]+)\\times10\^\{?(-?\d+)\}?\$?', s)
    if m2: return float(m2.group(1)) * 10.0**int(m2.group(2))
    m2 = re.fullmatch(r'\$?(-?[0-9.]+)\$?', s)
    if m2: return float(m2.group(1))
    raise ValueError(s)

E = row("PEEK Young's modulus"); nu = row("PEEK Poisson ratio")
alpha = row("PEEK expansion coefficient"); ks = row("PEEK conductivity")
rho = row("Water density"); muf = row("Water dynamic viscosity")
cp = row("Water specific heat"); kf = row("Water conductivity")
H0 = si("Channel height"); d = si("Wall thickness"); L = si("Heated, deformable length")
U = si("Mean inlet velocity"); q = si("Imposed heat flux")
L_o = float(re.search(r'Entrance / exit lengths.*?\\SI\{[0-9.eE+-]+\}\{[^}]*\}; \\SI\{([0-9.eE+-]+)\}', C2).group(1))
Nu = float(re.search(r'\\mathrm\{Nu\}_\{H1\}=([0-9.]+)', C9).group(1))

Dh = 2*H0; h = Nu*kf/Dh
dTt = q*d/ks; dTb = q*L/(rho*U*H0*cp)
thbar = dTt/2 + q/h + dTb/2
Ds = E*d**3/(12*(1-nu**2)); kth = (1+nu)*alpha*dTt/d
N0 = E*d*alpha*thbar/(1-nu)
mu = math.sqrt(N0/Ds); uL = mu*L; A = math.tan(uL/2)
w = lambda x: (kth/mu**2)*(A*math.sin(mu*x) + math.cos(mu*x) - 1)
wmax = w(L/2); kgeo = kth/math.cos(uL/2); Mmid = Ds*(kgeo - kth)
sig_bend = 6*abs(Mmid)/d**2/1e6
dp = 12*muf*U*(L+L_o)/H0**2; p0 = dp; pL = dp*L_o/(L+L_o); pbar = (p0+pL)/2
wp = 5*pbar*L**4/(384*Ds)
wp_bc = -pbar*L**2/(8*N0) + (pbar*Ds/N0**2)*(1/math.cos(mu*L/2) - 1)
Gp_mixed = wmax/wp; Gp_lfl = wmax/wp_bc
Ncr = math.pi**2*Ds/L**2
Tcr = 12*alpha*(1+nu)*L**2*Ncr/(math.pi**2*E*d**3/(12*(1-nu**2)) ) if False else None
sig_fr = (N0/d + 6*abs(Mmid)/d**2)/1e6
e0 = (1+nu)*alpha*thbar
# arc term: 0.5 * mean(w'^2)
NS = 200001; hh = L/(NS-1)
s = 0.0
for i in range(NS):
    x = i*hh; wp_ = (kth/mu)*(A*math.cos(mu*x) - math.sin(mu*x))
    c = 1 if i in (0, NS-1) else (4 if i % 2 else 2)
    s += c*wp_*wp_
arc = (s*hh/3)/L/2

print("parsed: E=%.3g nu=%.3g alpha=%.3g ks=%.3g rho=%.4g mu=%.3g cp=%.4g kf=%.3g" % (E,nu,alpha,ks,rho,muf,cp,kf))
print("parsed: H0=%.3g d=%.3g L=%.3g U=%.3g q=%.3g Lo=%.3g Nu_H1=%.4g" % (H0,d,L,U,q,L_o,Nu))
print()
rows = [
 ("theta-bar (K)", thbar, 32.3, 0.05, "0.05 K = last printed digit"),
 ("N_theta (N/m)", N0, 2.91e4, 0.005*2.91e4, "printed 2 s.f."),
 ("N_cr (N/m)", Ncr, 1.057e5, 0.0005*1.057e5, "printed 4 s.f."),
 ("mu (1/m)", mu, 55.0, 0.5, "printed 2 s.f."),
 ("mu L", uL, 1.65, 0.005, "printed 3 s.f."),
 ("w_max (m)", wmax, 2.19e-4, 0.005*2.19e-4, "printed 3 s.f."),
 ("w_max/H0", wmax/H0, 0.438, 0.0005, "printed 3 s.f."),
 ("kappa_geo (1/m)", kgeo, kth/math.cos(uL/2), 0.0, "definition check"),
 ("M_mid (N m/m)", -abs(Mmid), -6.4, 0.05, "printed 2 s.f."),
 ("sigma_bend (MPa)", sig_bend, 4.2, 0.05, "printed 2 s.f."),
 ("w_p (m)", wp, 9.2e-8, 0.005*9.2e-8, "printed 2 s.f."),
 ("Gamma_p mixed", Gp_mixed, 2.4e3, 0.01*2.4e3, "printed 2 s.f."),
 ("w_p(N_theta^c) (m)", wp_bc, 1.27e-7, 0.005*1.27e-7, "printed 3 s.f."),
 ("Gamma_p like-for-like", Gp_lfl, 1.73e3, 0.005*1.73e3, "printed 3 s.f."),
 ("sigma_max frozen (MPa)", sig_fr, 13.9, 0.05, "printed 3 s.f."),
 ("e_0", e0, 2.26e-3, 0.005*2.26e-3, "printed 3 s.f."),
 ("arc term", arc, 1.39e-4, 0.005*1.39e-4, "printed 3 s.f."),
 ("arc/L^2*24 (upper bound)", 12*arc/L**2*24/24*1, kgeo**2*L**2/24, 0.0, "compare below"),
]
print("%-24s %14s %12s %10s" % ("quantity", "recomputed", "printed", "rel. dev"))
for name, val, pr, tol, note in rows:
    if tol == 0.0 and name.startswith("kappa"):
        print("%-24s %14.6g %12s %10s" % (name, val, "-", "identity")); continue
    if name.startswith("arc/L^2"):
        print("%-24s %14.6g %12.6g %9.2f%%" % ("kgeo^2 L^2/24", val, pr, 100*(val/pr-1))); continue
    print("%-24s %14.6g %12.6g %9.2f%%   %s" % (name, val, pr, 100*(val/pr-1), note))

print()
print("pressure chain: dp=%.1f Pa  p0=%.1f  pL=%.1f  pbar=%.1f" % (dp, p0, pL, pbar))
print("beam-column identities: kgeo/kth=%.12f  sec(muL/2)=%.12f" % (kgeo/kth, 1/math.cos(uL/2)))
print("ODE residual check at three stations:")
for x in (0.3*L, 0.5*L, 0.77*L):
    wpp = -kth*(A*math.sin(mu*x) + math.cos(mu*x))
    res = Ds*(-kth*mu**2*(A*math.sin(mu*x)+math.cos(mu*x))) + N0*wpp
    print("   x=%.4f  residual=%.3e" % (x, res))
print("BCs: w(0)=%.3e w(L)=%.3e w''(0)+kth=%.3e w''(L)+kth=%.3e"
      % (w(0), w(L), (-kth*(A*math.sin(0)+math.cos(0)))+kth, (-kth*(A*math.sin(mu*L)+math.cos(mu*L)))+kth))
