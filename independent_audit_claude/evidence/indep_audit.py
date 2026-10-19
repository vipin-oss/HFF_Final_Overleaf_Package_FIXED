#!/usr/bin/env python3
"""Independent audit computations (Claude). Inputs are the PRINTED design-point values only
(ch02 tables, ch07 Table baseline). No value from Arena's scripts/reports is used as an input."""
import sympy as sp
import mpmath as mp
import numpy as np
from scipy.integrate import solve_bvp
from scipy.optimize import brentq

mp.mp.dps = 40

# ---------------- printed inputs (ch02 Table geometry/props; ch07 Table baseline) -----------------
H0, L, d, Lo = mp.mpf('5e-4'), mp.mpf('3e-2'), mp.mpf('3e-3'), mp.mpf('2e-2')
U, q = mp.mpf('5e-2'), mp.mpf('5e3')
E, nu, al, ks = mp.mpf('3.6e9'), mp.mpf('0.4'), mp.mpf('5e-5'), mp.mpf('0.25')
kf, mu_f, cp, rho = mp.mpf('0.6'), mp.mpf('1e-3'), mp.mpf('4180'), mp.mpf('1e3')

print("=" * 78); print("S1  SYMBOLIC DERIVATION OF THE PHYSICAL FIRST MOMENT (from source eq:widebeam)")
y, d_, E_, nu_, al_, G, th0, eps0, kap = sp.symbols('y d E nu alpha Gamma theta0 epsilon0 kappa', real=True)
# source: sigma_xx = E/(1-nu^2) [eps_xx - (1+nu) alpha theta],  eps_xx = eps0 + kap*y,  theta = th0 + G*y,
# y measured from mid-plane, heated face is the OUTER face at y=+d/2 (ch02:12-14: solid occupies [H0,H0+d]; top face loaded)
sig = E_ / (1 - nu_**2) * ((eps0 + kap * y) - (1 + nu_) * al_ * (th0 + G * y))
N_ = sp.integrate(sig, (y, -d_ / 2, d_ / 2))
M1 = sp.integrate(sig * y, (y, -d_ / 2, d_ / 2))
print("  axial resultant  N  =", sp.simplify(N_))
print("  first moment  int(sigma_xx*y) =", sp.factor(sp.simplify(M1)))
kth_sym = sp.solve(sp.Eq(M1, 0), kap)[0]
print("  zero-moment curvature  kappa_th =", kth_sym, " (Gamma=Delta T_t/d >0 for heated TOP face)")
# kinematics: vertical displacement v(x) (up positive) gives eps_xx = eps0 - y v''  =>  kap = -v''
# => kap_kin = -d2''.  With w = +d2: kap_kin = -w''.  With old w = -d2: kap_kin = +w''.
Ds_sym = E_ * d_**3 / (12 * (1 - nu_**2))
print("  M1 = -D_s (w'' + kappa_th) [w=+d2]  check:",
      sp.simplify(M1.subs(kap, -sp.Symbol('wpp')) + Ds_sym * (sp.Symbol('wpp') + kth_sym.subs(G, G))) == 0)

Ds = E * d**3 / (12 * (1 - nu**2))
kth = (1 + nu) * al * q / ks
print("  D_s = %s N m ;  kappa_th = %s 1/m ;  Delta T_t = %s K" % (mp.nstr(Ds, 12), mp.nstr(kth, 12), mp.nstr(q * d / ks, 8)))
# physical first moment at the pin under each pairing (pin condition printed as w'' = -kappa_th in BOTH)
M1_new = -Ds * (-kth + kth)           # w=+d2 :  kap_kin=-w'' = +kth -> M1 = Ds(kap_kin-kth)=0
M1_old = Ds * (+(-kth) - kth)         # w=-d2 :  kap_kin=+w'' = -kth -> M1 = Ds(-kth-kth) = -2 Ds kth
print("  physical first moment at pin, selected convention (w=+d2): %s N m" % mp.nstr(M1_new, 6))
print("  physical first moment at pin, OLD convention   (w=-d2): %s N m   (-2*Ds*kth)" % mp.nstr(M1_old, 10))

# ---------------- physical direction argument, independent of algebra ----------------------------
print("\nS2  DIRECTION CHECK: hot face = outer top face; hot fibre elongates -> hot face convex -> mid-span moves toward heater")
print("    heater side = away from channel  =>  w_max > 0 (away).  Selected convention agrees; old prose ('into the channel') does not.")

# ---------------- thermal state / membrane force (theta_bar from source's own components) ---------
Nu_H1 = mp.mpf('5.385')
h = Nu_H1 * kf / (2 * H0)
dTb = q * L / (rho * U * H0 * cp)
thbar = q * d / ks / 2 + q / h + dTb / 2
print("\nS3  theta_bar = dT_t/2 + q/h + dT_b/2 = %s + %s + %s = %s K" %
      (mp.nstr(q * d / ks / 2, 6), mp.nstr(q / h, 6), mp.nstr(dTb / 2, 6), mp.nstr(thbar, 8)))
Nth = E * d * al * thbar / (1 - nu)          # compressive magnitude
Ncr = mp.pi**2 * Ds / L**2
mu_ = mp.sqrt(Nth / Ds); uL = mu_ * L
Tcr = mp.pi**2 * d**2 / (12 * al * (1 + nu) * L**2)
print("  N_c = %s N/m ; N_cr = %s N/m ; N_c/N_cr = %s ; Tcr = %s K ; M_b = %s" %
      (mp.nstr(Nth, 8), mp.nstr(Ncr, 8), mp.nstr(Nth / Ncr, 6), mp.nstr(Tcr, 6), mp.nstr(Tcr / thbar, 5)))
print("  mu L = %s ;  1/(1-N/Ncr) = %s" % (mp.nstr(uL, 10), mp.nstr(1 / (1 - Nth / Ncr), 6)))

# ---------------- beam-column: closed form  vs  independent BVP solve ------------------------------
def closed(mu, kt):
    A = mp.tan(mu * L / 2)
    w = lambda x: kt / mu**2 * (A * mp.sin(mu * x) + mp.cos(mu * x) - 1)
    w1 = lambda x: kt / mu * (A * mp.cos(mu * x) - mp.sin(mu * x))
    w2 = lambda x: -kt * (A * mp.sin(mu * x) + mp.cos(mu * x))
    return w, w1, w2

w, w1, w2 = closed(mu_, kth)
wmax = w(L / 2); wlin = kth * L**2 / 8
print("\nS4  BEAM-COLUMN (frozen force)")
print("  closed form  w_max = %s m = %s H0 ; linear = %s m ; amplification = %s" %
      (mp.nstr(wmax, 12), mp.nstr(wmax / H0, 9), mp.nstr(wlin, 10), mp.nstr(wmax / wlin, 10)))

# independent method: solve the 2nd-order moment form  D w'' + N w = -D kth*... via scipy BVP
# From D w'''' + N w'' = 0 with w''(0)=w''(L)=-kth: integrate twice -> w'' + mu^2 w = -kth  (since w(0)=0, w''(0)=-kth).
Dsf, Ncf, ktf, Lf = float(Ds), float(Nth), float(kth), float(L)
m2 = Ncf / Dsf
def rhs(x, Y): return np.vstack([Y[1], -m2 * Y[0] - ktf])
def bc(a, b): return np.array([a[0], b[0]])
xs = np.linspace(0, Lf, 2001)
sol = solve_bvp(rhs, bc, xs, np.zeros((2, xs.size)), tol=1e-12, max_nodes=200000)
wb = sol.sol(Lf / 2)[0]
print("  independent BVP  w'' + mu^2 w = -kth,  w(0)=w(L)=0:  w_max = %.12e   (rel. diff to closed form %.2e)" %
      (wb, abs(wb - float(wmax)) / float(wmax)))
# and verify 4th-order eq + BCs symbolically on the closed form
x_, mus, kts, Ls = sp.symbols('x mu kth L', positive=True)
As = sp.tan(mus * Ls / 2)
ws = kts / mus**2 * (As * sp.sin(mus * x_) + sp.cos(mus * x_) - 1)
print("  sympy (exact): ODE  w'''' + mu^2 w'' == 0  ->", sp.simplify(sp.diff(ws, x_, 4) + mus**2 * sp.diff(ws, x_, 2)) == 0)
_v = {mus: 55.0, kts: 1.4, Ls: 0.03}   # sympy does not auto-simplify the tan half-angle identity, so BCs are checked by substitution
print("  BC residuals (numeric substitution): w(0)=%.1e  w(L)=%.1e  w''(0)+k=%.1e  w''(L)+k=%.1e" % (
      float(ws.subs(x_, 0).subs(_v)), float(ws.subs(x_, Ls).subs(_v)),
      float((sp.diff(ws, x_, 2) + kts).subs(x_, 0).subs(_v)), float((sp.diff(ws, x_, 2) + kts).subs(x_, Ls).subs(_v))))

kgeo = -w2(L / 2)
M_mid = Ds * (w2(L / 2) + kth)
print("  kappa_geo = %s ;  kth*sec(uL/2) = %s" % (mp.nstr(kgeo, 10), mp.nstr(kth / mp.cos(uL / 2), 10)))
print("  M_mid = %s N m ; sigma_bend = %s MPa ; fibre strain (kgeo-kth)d/2 = %s ; max|w'| = %s rad" %
      (mp.nstr(M_mid, 9), mp.nstr(6 * abs(M_mid) / d**2 / 1e6, 8), mp.nstr((kgeo - kth) * d / 2, 9), mp.nstr(abs(w1(0)), 6)))
print("  factor (kgeo+kth)/(kgeo-kth) = %s ; cot^2(uL/4) = %s" %
      (mp.nstr((kgeo + kth) / (kgeo - kth), 10), mp.nstr(1 / mp.tan(uL / 4)**2, 10)))

# ---------------- arc term: quadrature vs closed form -------------------------------------------
arc_q = mp.quad(lambda x: w1(x)**2, [0, L / 2, L]) / L / 2
Aa = mp.tan(uL / 2);
x = sp.symbols('x', positive=True)
arc_sym_expr = sp.integrate(((kts / mus) * (As * sp.cos(mus * x_) - sp.sin(mus * x_)))**2, (x_, 0, Ls)) / Ls / 2
arc_c = sp.N(arc_sym_expr.subs({kts: sp.Float(str(kth), 30), mus: sp.Float(str(mu_), 30), Ls: sp.Float(str(L), 30)}), 20)
e0 = (1 + nu) * al * thbar
print("\nS5  ARC TERM   quadrature = %s ;  sympy closed-form integral = %s" % (mp.nstr(arc_q, 14), arc_c))
print("    circular-arc estimate kgeo^2 L^2/24 = %s ;  e0 = %s ; relaxation arc/e0 = %s %% ; with 1.8e-4: %s %%" %
      (mp.nstr(kgeo**2 * L**2 / 24, 10), mp.nstr(e0, 8), mp.nstr(100 * arc_q / e0, 6), mp.nstr(100 * mp.mpf('1.8e-4') / e0, 6)))

# ---------------- self-consistent fixed point (eq:nupdate) ---------------------------------------
def solve_sc():
    def F(Nc):
        mu = mp.sqrt(Nc / Ds); _, w1_, _ = closed(mu, kth)
        I = mp.quad(lambda x: w1_(x)**2, [0, L / 2, L]) / L
        return Nc - (Nth - E * d / (2 * (1 - nu**2)) * I)       # compressive magnitude: N_c = N_c0 - Ed/(2(1-nu^2))<w'^2>
    Nsc = mp.findroot(F, Nth * 0.95)
    return Nsc
Nsc = solve_sc(); musc = mp.sqrt(Nsc / Ds); wsc, w1sc, w2sc = closed(musc, kth)
Msc = Ds * (w2sc(L / 2) + kth)
relax = 1 - Nsc / Nth
print("\nS6  SELF-CONSISTENT FIXED POINT:  N_c(sc) = %s  ->  relaxation = %s %% ; w_max(sc) = %s m (= %s H0); frozen overpredicts by %s %%" %
      (mp.nstr(Nsc, 8), mp.nstr(100 * relax, 5), mp.nstr(wsc(L / 2), 8), mp.nstr(wsc(L / 2) / H0, 6),
       mp.nstr(100 * (wmax / wsc(L / 2) - 1), 4)))
sm_frozen = Nth / d; sb_frozen = 6 * abs(M_mid) / d**2
sm_sc = Nsc / d;   sb_sc = 6 * abs(Msc) / d**2
print("    M_mid(sc) = %s N m" % mp.nstr(Msc, 6))
print("    FROZEN       : membrane %s + bending %s = %s MPa" % tuple(mp.nstr(v / 1e6, 7) for v in (sm_frozen, sb_frozen, sm_frozen + sb_frozen)))
print("    SELF-CONSIST.: membrane %s + bending %s = %s MPa   <-- relaxed N used for BOTH terms" % tuple(mp.nstr(v / 1e6, 7) for v in (sm_sc, sb_sc, sm_sc + sb_sc)))
print("    MIXED (frozen membrane + sc bending, i.e. the manuscript's '13.6'): %s MPa" % mp.nstr((sm_frozen + sb_sc) / 1e6, 7))

# ---------------- strain measures --------------------------------------------------------------
print("\nS7  STRAIN MEASURES at mid-span (y measured from mid-plane, top = heated face)")
eps0_frozen = 0;
for lab, ep0 in (("frozen (N_c blocked)", 0.0),):
    pass
# kinematic: eps_xx(y) = eps_mean + kap_kin*y with eps_mean = <u'> + 1/2<w'^2> = 1/2<w'^2> (ends fixed),  kap_kin = kgeo
mean_kin = arc_q
top_k = mean_kin + kgeo * d / 2; bot_k = mean_kin - kgeo * d / 2
# mechanical (stress-producing) strain = kinematic - thermal;  thermal = (1+nu) alpha (thbar + Gamma y), Gamma*d/2 = kth*d/2/((1+nu)alpha)->(1+nu)alpha Gamma = kth
top_m = mean_kin - e0 + (kgeo - kth) * d / 2
bot_m = mean_kin - e0 - (kgeo - kth) * d / 2
print("    kinematic strain  top = %s ; bottom = %s" % (mp.nstr(top_k, 6), mp.nstr(bot_k, 6)))
print("    mechanical strain top = %s ; bottom = %s   (max |.| = %s)" % (mp.nstr(top_m, 6), mp.nstr(bot_m, 6), mp.nstr(max(abs(top_m), abs(bot_m)), 6)))
print("    stress check bottom fibre = E/(1-nu^2)*eps_mech = %s MPa" % mp.nstr(E / (1 - nu**2) * bot_m / 1e6, 6))
print("    printed 'total mechanical surface strain' e0 + kgeo*d/2 = %s" % mp.nstr(e0 + kgeo * d / 2, 6))

# ---------------- pressure & Gamma_p ------------------------------------------------------------
dp = 12 * mu_f * U * L / H0**2
pL = 12 * mu_f * U / H0**2 * Lo; p0 = pL + dp; pbar = (p0 + pL) / 2
wp = 5 * pbar * L**4 / (384 * Ds)
print("\nS8  PRESSURE: dp = %s Pa ; p(L)=%s ; p(0)=%s ; pbar = %s Pa ; w_p = %s m" %
      tuple(mp.nstr(v, 8) for v in (dp, pL, p0, pbar, wp)))
cf = 48 * kth * Ds / (5 * pbar * L**2)
print("    48 kth Ds/(5 pbar L^2) = %s ;  w_lin/w_p = %s ;  w_max/w_p = %s ; cf*amplification = %s" %
      (mp.nstr(cf, 10), mp.nstr(wlin / wp, 10), mp.nstr(wmax / wp, 10), mp.nstr(cf * wmax / wlin, 10)))
print("    Gamma_p (self-consistent w) = %s" % mp.nstr(wsc(L / 2) / wp, 8))

# ---------------- geometry: mid-span passage height under each pairing -------------------------
print("\nS9  PASSAGE HEIGHT AT MID-SPAN")
print("    corrected (away): H = H0 + w_max = %s m = %s H0  (+%s %%)" % (mp.nstr(H0 + wmax, 8), mp.nstr(1 + wmax / H0, 6), mp.nstr(100 * wmax / H0, 4)))
print("    old (into)      : H = H0 - w_max = %s H0" % mp.nstr(1 - wmax / H0, 6))

# ---------------- sensitivity to theta_bar rounding (32 vs 32.27) ---------------------------------
def wm_for(th):
    N = E * d * al * th / (1 - nu); m = mp.sqrt(N / Ds); return closed(m, kth)[0](L / 2)
print("\nS10 SENSITIVITY  w_max(theta_bar=32.0) = %s ; (32.27) = %s ; rel diff %s %%" %
      (mp.nstr(wm_for(32), 8), mp.nstr(wm_for(thbar), 8), mp.nstr(100 * (wm_for(32) / wm_for(thbar) - 1), 3)))
