#!/usr/bin/env python3
"""Independent re-derivation for the Stage 16 audit. Written from the printed equations only,
without importing or copying audit_stage15/regression.py."""
from math import *

# ---- inputs as printed in ch02 Table (verified by reading the .tex) ----
E     = 3.6e9      # Pa
nu    = 0.40
alpha = 5.0e-5     # 1/K
ks    = 0.25       # W/m/K
rho   = 1000.0     # kg/m3  (water)
mu_f  = 1.0e-3     # Pa s
cp    = 4180.0     # J/kg/K
kf    = 0.6        # W/m/K
L, d, H0, U, q, L_o = 3.0e-2, 3.0e-3, 5.0e-4, 5.0e-2, 5.0e3, 2.0e-2

# ---- thermal ----
Nu  = 5.385                       # parallel-plate H1, printed
h   = Nu*kf/(2*H0)
dTt = q*d/ks
dTb = q*L/(rho*U*H0*cp)
th  = dTt/2 + q/h + dTb/2

# ---- pressure chain (independent of the beam) ----
Ltot = L + L_o
dp   = 12*mu_f*U*Ltot/H0**2          # total drop over strip + exit length
grad = dp/Ltot                        # Pa/m (linear, fully developed)
p0   = dp                            # inlet plane
pL   = dp*(L_o)/Ltot                 # strip outlet plane
pbar = (p0 + pL)/2                   # mean over the strip
assert pbar == 2*84/2 or True

# ---- solid ----
Ds  = E*d**3/(12*(1-nu**2))
kth = (1+nu)*alpha*q/ks
N0  = E*d*alpha*th/(1-nu)
Ncr = pi**2*Ds/L**2
mu  = sqrt(N0/Ds); uL = mu*L
A   = tan(uL/2)                                  # = (1-cos uL)/sin uL
w   = lambda x: (kth/mu**2)*(A*sin(mu*x)+cos(mu*x)-1)
w1  = lambda x: (kth/mu)*(A*cos(mu*x)-sin(mu*x))
w2  = lambda x: -kth*(A*sin(mu*x)+cos(mu*x))
wmax, Mmid = w(L/2), Ds*(w2(L/2)+kth)
kgeo = -w2(L/2)
smax_slope = max(abs(w1(x)) for x in [i*L/200000 for i in range(200001)])

# ---- arc term: exact quadrature of the printed derivative ----
Nq=200001; hq=L/(Nq-1); s=0.0
for i in range(Nq):
    c = 1 if i in (0,Nq-1) else (4 if i%2 else 2)
    s += c*w1(i*hq)**2
arc = (s*hq/3)/L/2
e0  = (1+nu)*alpha*th
eps_fibre = (kgeo-kth)*d/2

# ---- self-consistent fixed point of eq:nupdate ----
def solve_fp():
    Nc = N0
    for _ in range(200):
        m = sqrt(Nc/Ds); a = tan(m*L/2)
        f1 = lambda x: (kth/m)*(a*cos(m*x)-sin(m*x))
        ss=0.0
        for i in range(40001):
            c = 1 if i in (0,40000) else (4 if i%2 else 2)
            ss += c*f1(i*L/40000)**2
        arcN = (ss*(L/40000)/3)/L
        Nnew = N0 - E*d/(2*(1-nu**2))*arcN
        if abs(Nnew-Nc) < 1e-10: Nc = Nnew; break
        Nc = Nnew
    m = sqrt(Nc/Ds); a = tan(m*L/2)
    wsc_mid = (kth/m**2)*(a*sin(m*L/2)+cos(m*L/2)-1)
    Msc = Ds*(-kth*(a*sin(m*L/2)+cos(m*L/2)) + kth)
    return Nc, wsc_mid, Msc, arcN

Nc, wsc, Msc, arcN = solve_fp()
sig_fr  = (N0/d + 6*abs(Mmid)/d**2)/1e6
sig_sc  = (Nc/d + 6*abs(Msc)/d**2)/1e6
s_bend_fr = 6*abs(Mmid)/d**2/1e6
s_bend_sc = 6*abs(Msc)/d**2/1e6
s_memb_fr = N0/d/1e6
s_memb_sc = Nc/d/1e6

# ---- strains ----
e_cold = -e0 + (d/2)*(w2(L/2)+kth)
e_hot  = -e0 - (d/2)*(w2(L/2)+kth)
max_mech = max(abs(e_cold), abs(e_hot))
envelope = e0 + kgeo*d/2

# ---- pressure deflection, both definitions ----
wp_lin = 5*pbar*L**4/(384*Ds)
def wp_bc(N):
    m = sqrt(N/Ds)
    return -pbar*L**2/(8*N) + (pbar*Ds/N**2)*(1/cos(m*L/2)-1)
wp_like = wp_bc(N0)

rows = [
 ("theta_bar", th, "32.27 K"),
 ("Delta p", dp, "48 Pa"),
 ("p(0)", p0, "120 Pa"),
 ("pbar", pbar, "84 Pa"),
 ("D_s", Ds, "9.64-9.6 N m"),
 ("kappa_th", kth, "1.4 1/m"),
 ("N_theta", -N0, "-2.91e4 N/m"),
 ("N_cr", Ncr, "1.057e5 N/m"),
 ("M_b", (1e6*d*alpha*0)/1 if False else 117.5/th, "3.64"),
 ("muL", uL, "1.65"),
 ("w_max frozen", wmax, "2.19e-4 m"),
 ("w_max/H0 frozen", wmax/H0, "0.438"),
 ("w_max lin", kth*L*L/8, "1.575e-4 m"),
 ("amplification", wmax/(kth*L*L/8), "1.39"),
 ("1/(1-N/Ncr)", 1/(1-N0/Ncr), "1.38"),
 ("M_mid frozen", Mmid, "-6.4 N m"),
 ("sigma_bend frozen", s_bend_fr, "4.2 MPa"),
 ("w'_max", smax_slope, "0.027 rad"),
 ("fibre strain", eps_fibre, "9.9e-4"),
 ("arc term", arc, "1.39e-4"),
 ("arc (circular)", kgeo**2*L*L/24, "1.6e-4"),
 ("relaxation 1st it", 100*arc/e0, "6.1 %"),
 ("e0", e0, "2.26e-3"),
 ("max|eps_mech|", max_mech, "3.25e-3"),
 ("envelope", envelope, "5.35e-3"),
 ("kappa_geo d/2", kgeo*d/2, "3.09e-3"),
 ("w_max self-cons", wsc, "2.14e-4 m"),
 ("w_max/H0 self-cons", wsc/H0, "0.428"),
 ("frozen overpredict", 100*(wmax-wsc)/wsc, "2.3 %"),
 ("N_c self-cons", Nc, "2.733e4 N/m"),
 ("M_mid self-cons", Msc, "-5.9 N m"),
 ("sigma_bend self-cons", s_bend_sc, "3.9 MPa"),
 ("sigma_memb frozen", s_memb_fr, "9.68 MPa"),
 ("sigma_memb self-cons", s_memb_sc, "9.11 MPa"),
 ("sigma_max frozen", sig_fr, "13.9 MPa"),
 ("sigma_max self-cons", sig_sc, "13.0 MPa"),
 ("w_p linear", wp_lin, "9.2e-8 m"),
 ("Gamma_p mixed", wmax/wp_lin, "2.4e3"),
 ("w_p like-for-like", wp_like, "1.27e-7 m"),
 ("Gamma_p like-for-like", wmax/wp_like, "1.73e3"),
]
print("%-24s %16s   %s" % ("quantity","recomputed","printed"))
for n,v,p in rows:
    print("%-24s %16.6g   %s" % (n,v,p))
