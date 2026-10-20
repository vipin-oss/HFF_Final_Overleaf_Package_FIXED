#!/usr/bin/env python3
"""Discrete checks for audit items 3 and 4.

(1) GAUGE: is the constant pressure in the kernel of b(.,1)?   b(v,p) = -int p div v.
    For a piecewise-constant pressure vector p=1, (B^T 1)_j = sum_e int_e div(phi_j) = oint phi_j.n ds.
    If that is nonzero for test functions with outflow support, constants are NOT in the kernel.
(2) GEOMETRIC TERM: int_{Omega_s} (N/d) dX(d2) dX(phi2) dA  ==  N int_0^L dX(d2) dX(phi2) dX.
"""
from math import *
GA=[-sqrt(3.0/5.0),0.0,sqrt(3.0/5.0)]; GW=[5.0/9.0,8.0/9.0,5.0/9.0]

def N(s,t):
    return [-(1-s)*(1-t)*(1+s+t)/4, -(1+s)*(1-t)*(1-s+t)/4, -(1+s)*(1+t)*(1-s-t)/4,
            -(1-s)*(1+t)*(1+s-t)/4, (1-s*s)*(1-t)/2, (1+s)*(1-t*t)/2, (1-s*s)*(1+t)/2, (1-s)*(1-t*t)/2]
def dNs(s,t):
    return [(1-t)*(2*s+t)/4,(1-t)*(2*s-t)/4,(1+t)*(2*s+t)/4,(1+t)*(2*s-t)/4,
            -s*(1-t),(1-t*t)/2,-s*(1+t),-(1-t*t)/2]
def dNt(s,t):
    return [(s+2*t-s*s-2*s*t)/4,(-s-s*s+2*s*t+2*t)/4,(s*s+s+2*s*t+2*t)/4,
            (s*s-s-2*s*t+2*t)/4,-(1-s*s)/2,-(1+s)*t,(1-s*s)/2,-(1-s)*t]

L,d,NX,NY = 3e-2,3e-3,12,2
lat={}; xy=[]
def add(pt): lat[pt]=len(xy); xy.append((L*pt[0]/(2*NX), d*pt[1]/(2*NY)))
for j in range(2*NY+1):
    for i in range(2*NX+1):
        if (i%2==0) or (j%2==0): add((i,j))
elems=[]
for e in range(NX):
    for f in range(NY):
        i0,j0=2*e,2*f
        elems.append([lat[(i0,j0)],lat[(i0+2,j0)],lat[(i0+2,j0+2)],lat[(i0,j0+2)],
                      lat[(i0+1,j0)],lat[(i0+2,j0+1)],lat[(i0+1,j0+2)],lat[(i0,j0+1)]])

def dNxy(conn,s,t):
    Nn,ds,dt=N(s,t),dNs(s,t),dNt(s,t)
    xe=[xy[n][0] for n in conn]; ye=[xy[n][1] for n in conn]
    xs=sum(ds[n]*xe[n] for n in range(8)); ys=sum(ds[n]*ye[n] for n in range(8))
    xt=sum(dt[n]*xe[n] for n in range(8)); yt=sum(dt[n]*ye[n] for n in range(8))
    det=xs*yt-xt*ys
    return [(yt*ds[n]-ys*dt[n])/det for n in range(8)],[(-xt*ds[n]+xs*dt[n])/det for n in range(8)],det,Nn

# ---- (1) constant-pressure functional ----
bvx=[0.0]*len(xy); bvy=[0.0]*len(xy)
for conn in elems:
    for a in range(3):
        for b in range(3):
            s,t,w=GA[a],GA[b],GW[a]*GW[b]
            dx,dy,det,_=dNxy(conn,s,t)
            for n in range(8):
                bvx[conn[n]] += w*det*dx[n]
                bvy[conn[n]] += w*det*dy[n]
mx=max(max(abs(v) for v in bvx), max(abs(v) for v in bvy))
print("max |(B^T 1)| over all nodes = %.6e  (element size %.3e m)" % (mx, L/NX))
inflow = [n for n,(x,y) in enumerate(xy) if x < 1e-15]
outflow= [n for n,(x,y) in enumerate(xy) if x > L-1e-15]
walls  = [n for n,(x,y) in enumerate(xy) if y < 1e-15 or y > d-1e-15]
print("  inflow nodes: max|(B^T1).n| = %.4e" % max(abs(bvx[n]) for n in inflow))
print("  outflow nodes: max|(B^T1).n| = %.4e" % max(abs(bvx[n]) for n in outflow))
print("  values at the outflow nodes (== edge flux weights):", ["%.3e"%bvx[n] for n in sorted(set(outflow))][:5])
interior=[n for n in range(len(xy)) if n not in inflow+outflow+walls]
print("  interior nodes: max |(B^T 1)| = %.3e  (cancellation of interior element integrals)"
      % max(max(abs(bvx[n]),abs(bvy[n])) for n in interior))
print("  -> constant pressure is NOT annihilated by b(.,1): the outflow test functions see it.")
print("  -> if Gamma_out were Dirichlet, every test function would vanish there and the")
print("     outflow weights above would be zero, i.e. constants WOULD be in the kernel.")

# ---- (2) 1-D / 2-D reduction of the geometric term ----
kap=1.0
def d2(x):   return sin(pi*x/L)
def phi2(x): return x*(L-x)
Nforce = 2.9e4
I2d=0.0
for conn in elems:
    for a in range(3):
        for b in range(3):
            s,t,w=GA[a],GA[b],GW[a]*GW[b]
            dx,dy,det,Nn=dNxy(conn,s,t)
            x=sum(Nn[n]*xy[conn[n]][0] for n in range(8))
            # interpolate d2 and phi2 nodal values
            d2n=[d2(xy[c][0]) for c in conn]; phin=[phi2(xy[c][0]) for c in conn]
            d2x=sum(dx[n]*d2n[n] for n in range(8)); phix=sum(dx[n]*phin[n] for n in range(8))
            I2d += w*det*(Nforce/d)*d2x*phix
I1d=0.0
for a in range(3):
    s=GA[a]; w=GW[a]
    # 1-D Gauss on each element in x
    pass
# 1-D reference by high-order Simpson along x (d2, phi2 analytic)
n=200000; h=L/n; acc=0.0
for i in range(n+1):
    x=i*h
    c=1 if i in (0,n) else (4 if i%2 else 2)
    acc += c*(pi/L*cos(pi*x/L))*(L-2*x)
I1d=Nforce*(acc*h/3)
print()
print("geometric term: 2-D assembly = %.8e   N * 1-D integral = %.8e   ratio = %.10f"
      % (I2d, I1d, I2d/I1d))
print("  -> the /d factor is exactly what makes the 2-D term equal N times the 1-D term")
print("     (without it the 2-D term would be d = %.1e times the intended value, i.e. the")
print("      geometric stiffness would be lost)")
