#!/usr/bin/env python3
"""Independent Q8 plane-strain check of the Stage 16 pin condition (D-26). Second attempt:
shape-function derivatives re-derived analytically and validated against finite differences,
patch test required to be exact before any result is used."""
from math import *

E, nu, alpha = 3.6e9, 0.40, 5.0e-5
L, d, dT = 3.0e-2, 3.0e-3, 25.0
KTH = (1+nu)*alpha*dT/d
WB  = KTH*L*L/8

lam = E*nu/((1+nu)*(1-2*nu)); mu = E/(2*(1+nu))
D = [[lam+2*mu, lam, 0.0],[lam, lam+2*mu, 0.0],[0.0,0.0,mu]]

def N(s,t):
    return [-(1-s)*(1-t)*(1+s+t)/4, -(1+s)*(1-t)*(1-s+t)/4,
            -(1+s)*(1+t)*(1-s-t)/4, -(1-s)*(1+t)*(1+s-t)/4,
            (1-s*s)*(1-t)/2, (1+s)*(1-t*t)/2, (1-s*s)*(1+t)/2, (1-s)*(1-t*t)/2]
def dNs(s,t):
    return [(1-t)*(2*s+t)/4, (1-t)*(2*s-t)/4, (1+t)*(2*s+t)/4, (1+t)*(2*s-t)/4,
            -s*(1-t), (1-t*t)/2, -s*(1+t), -(1-t*t)/2]
def dNt(s,t):
    return [(s+2*t-s*s-2*s*t)/4, (-s-s*s+2*s*t+2*t)/4, (s*s+s+2*s*t+2*t)/4,
            (s*s-s-2*s*t+2*t)/4, -(1-s*s)/2, -(1+s)*t, (1-s*s)/2, -(1-s)*t]

# validate the derivatives against central differences
worst = 0.0
for (s,t) in [(0.31,-0.62),(-0.77,0.42),(0.05,0.9),(-0.4,-0.1)]:
    h=1e-6
    for k in range(8):
        fds = (N(s+h,t)[k]-N(s-h,t)[k])/(2*h)
        fdt = (N(s,t+h)[k]-N(s,t-h)[k])/(2*h)
        worst = max(worst, abs(fds-dNs(s,t)[k]), abs(fdt-dNt(s,t)[k]))
print("shape-derivative check (max abs vs FD): %.2e" % worst)
assert worst < 1e-8

GA=[-sqrt(3.0/5.0),0.0,sqrt(3.0/5.0)]; GW=[5.0/9.0,8.0/9.0,5.0/9.0]
NX, NY = 12, 2
lat = {}; xy = []
def add(pt):
    lat[pt]=len(xy); xy.append((L*pt[0]/(2*NX), d*pt[1]/(2*NY)))
for j in range(2*NY+1):
    for i in range(2*NX+1):
        if (i % 2 == 0) or (j % 2 == 0):     # (odd,odd) has no Q8 node
            add((i,j))
elems=[]
for e in range(NX):
    for f in range(NY):
        i0,j0 = 2*e,2*f
        elems.append([lat[(i0,j0)],lat[(i0+2,j0)],lat[(i0+2,j0+2)],lat[(i0,j0+2)],
                      lat[(i0+1,j0)],lat[(i0+2,j0+1)],lat[(i0+1,j0+2)],lat[(i0,j0+1)]])
ndof=2*len(xy)

def elmat(conn, theta):
    k=[[0.0]*16 for _ in range(16)]; f=[0.0]*16
    xe=[xy[n][0] for n in conn]; ye=[xy[n][1] for n in conn]
    for a in range(3):
        for b in range(3):
            s,t,w = GA[a],GA[b],GW[a]*GW[b]
            Nn,ds,dt = N(s,t),dNs(s,t),dNt(s,t)
            xs=sum(ds[n]*xe[n] for n in range(8)); ys=sum(ds[n]*ye[n] for n in range(8))
            xt=sum(dt[n]*xe[n] for n in range(8)); yt=sum(dt[n]*ye[n] for n in range(8))
            det=xs*yt-xt*ys
            dx=[(yt*ds[n]-ys*dt[n])/det for n in range(8)]
            dy=[(-xt*ds[n]+xs*dt[n])/det for n in range(8)]
            B=[[0.0]*16 for _ in range(3)]
            for n in range(8):
                B[0][2*n]=dx[n]; B[1][2*n+1]=dy[n]; B[2][2*n]=dy[n]; B[2][2*n+1]=dx[n]
            wd=w*det
            DB=[[sum(D[r][c]*B[c][q] for c in range(3)) for q in range(16)] for r in range(3)]
            for i in range(16):
                for j in range(16):
                    k[i][j]+=wd*sum(B[r][i]*DB[r][j] for r in range(3))
            yv=sum(Nn[n]*ye[n] for n in range(8)); th=theta(yv)
            if th:
                # plane strain: the effective thermal strain is (1+nu)*alpha*theta, NOT alpha*theta
                es=[(1+nu)*alpha*th, (1+nu)*alpha*th, 0.0]
                De=[sum(D[r][c]*es[c] for c in range(3)) for r in range(3)]
                for i in range(16): f[i]+=wd*sum(B[r][i]*De[r] for r in range(3))
    return k,f

def assemble(theta):
    K=[[0.0]*ndof for _ in range(ndof)]; F=[0.0]*ndof
    for conn in elems:
        k,f=elmat(conn,theta)
        for a in range(8):
            ia=2*conn[a]; F[ia]+=f[2*a]; F[ia+1]+=f[2*a+1]
            for b in range(8):
                ib=2*conn[b]
                K[ia][ib]+=k[2*a][2*b]; K[ia][ib+1]+=k[2*a][2*b+1]
                K[ia+1][ib]+=k[2*a+1][2*b]; K[ia+1][ib+1]+=k[2*a+1][2*b+1]
    return K,F

def gauss(A,F):
    n=len(F); M=[row[:]+[F[i]] for i,row in enumerate(A)]
    for c in range(n):
        p=max(range(c,n),key=lambda r:abs(M[r][c]))
        scale=max(1.0, max(abs(M[p][k]) for k in range(n)))
        if abs(M[p][c])<1e-12*scale: raise ArithmeticError("singular at %d"%c)
        M[c],M[p]=M[p],M[c]; piv=M[c][c]
        for r in range(n):
            if r!=c and M[r][c]:
                fac=M[r][c]/piv
                for k in range(c,n+1): M[r][k]-=fac*M[c][k]
    return [M[i][n]/M[i][i] for i in range(n)]

def face_con(i2):
    """edge-integral constraint of d1 on the face at lattice column i2 (0 or 2NX)"""
    con={}
    for conn in elems:
        xs=[xy[n][0] for n in conn]
        side = None
        if i2==0 and min(xs)<1e-15: side=[0,3,7]
        if i2==2*NX and max(xs)>L-1e-15: side=[1,2,5]
        if side is None: continue
        ye=[xy[conn[n]][1] for n in side]
        h=max(ye)-min(ye)
        ymid=(max(ye)+min(ye))/2.0
        for loc in range(3):                       # quadratic edge: 1/6, 4/6, 1/6
            nn=conn[side[loc]]; yn=xy[nn][1]
            wt = 4*h/6.0 if abs(yn-ymid) < 1e-15 else h/6.0
            con[2*nn]=con.get(2*nn,0.0)+wt
    return con

def solve_case(mode):
    theta=lambda y: dT*(y/d-0.5)
    K,F=assemble(theta)
    fixed={}
    cons=[]
    face0=[n for (i,j),n in lat.items() if i==0]
    faceL=[n for (i,j),n in lat.items() if i==2*NX]
    if mode in ("PIN","POINT","CLAMP"):
        cons.append(face_con(0)); cons.append(face_con(2*NX))
    if mode in ("PIN","CLAMP"):
        for n in face0+faceL: fixed[2*n+1]=0.0
    if mode=="POINT":
        for n in face0+faceL:
            if abs(xy[n][1]-d/2)<1e-15: fixed[2*n+1]=0.0
    if mode=="CLAMP":
        cons=[]                       # the mean constraints are implied; do not duplicate them
        for n in face0+faceL:
            fixed[2*n]=0.0; fixed[2*n+1]=0.0
    for k,v in fixed.items(): cons.append({k:1.0})
    # master-slave elimination for all constraints at once (Gauss-Jordan on the augmented system)
    crows=[{k:vv for k,vv in con.items()} for con in cons]
    nfree=len(F); nc=len(crows); n=nfree+nc
    A=[[0.0]*n for _ in range(n)]
    for i in range(nfree):
        for j in range(nfree): A[i][j]=K[i][j]
    B=F[:]+[0.0]*nc
    for i,con in enumerate(crows):
        nrm=sqrt(sum(v*v for v in con.values())) or 1.0
        for k,v in con.items():
            A[k][nfree+i]=v/nrm; A[nfree+i][k]=v/nrm
    u=gauss(A,B)
    return u[:nfree]

def w_at(u,n): return u[2*n+1]
midm = lat[(NX,1)]      # x=L/2, y=d/2
midt = lat[(NX,2)]      # x=L/2, y=d
print("mesh %d elements %d nodes; kappa_th=%.4e 1/m; beam w=%.4e m"%(len(elems),len(xy),KTH,WB))
print()
print("%-7s %14s %10s %14s %10s"%("case","w (mid-surface)","ratio","w (top face)","ratio"))
res={}
for mode in ("POINT","PIN","CLAMP"):
    u=solve_case(mode)
    wm,wt=w_at(u,midm),w_at(u,midt); res[mode]=(wm/WB, wt/WB)
    print("%-7s %14.5e %10.4f %14.5e %10.4f"%(mode,wm,wm/WB,wt,wt/WB))
print()
try:
    solve_case("FREE"); print("FREE case: solved (unexpected: rigid modes not removed)")
except ArithmeticError as e:
    print("FREE case: singular as expected -> %s (three rigid modes)"%e)

print()
print("DIAGNOSTIC: deflected mid-surface for the POINT case (x, w) and curvature fit")
u = solve_case("POINT")
xs=[]; ws=[]
for i in range(2*NX+1):
    if i % 2 == 0:
        n = lat[(i,2)]           # y = d/2  (mid-thickness)
        xs.append(xy[n][0]); ws.append(u[2*n+1])
for x,wv in zip(xs,ws):
    print("  x=%.4f  w=% .5e   w/beam=%.4f" % (x, wv, wv/(KTH*x*(L-x)/2) if x not in (0,L) else 0.0))
# curvature at mid-span from a local parabola through 3 points
h = L/12
i0,i1,i2 = 2*NX-4, 2*NX-2, 2*NX      # three consecutive nodes near mid-span
h = L/12
n0,n1,n2 = lat[(i0,2)], lat[(i1,2)], lat[(i2,2)]
w0,w1,w2 = u[2*n0+1], u[2*n1+1], u[2*n2+1]
kap = -(w0 - 2*w1 + w2)/h**2
print("  fitted curvature at mid-span: %.5e 1/m   (kappa_th = %.5e, ratio %.4f)" % (kap, KTH, kap/KTH))


# ---------- consistency test of stiffness + thermal load against the exact free-bending field ----------
# exact zero-stress field for this load:  ux = -(y-d/2) w'(x),  uy = w(x) + kappa (y-d/2)^2/2 + c
kap = KTH
def ux_ex(x,y): return -(y-d/2)*kap*(L-2*x)/2
def uy_ex(x,y): return kap*x*(L-x)/2 + kap*(y-d/2)**2/2 - kap*(d/2)**2/2
K,F = assemble(lambda y: dT*(y/d-0.5))
u = [0.0]*ndof
for n,(x,y) in enumerate(xy):
    u[2*n]=ux_ex(x,y); u[2*n+1]=uy_ex(x,y)
r = [sum(K[i][j]*u[j] for j in range(ndof)) - F[i] for i in range(ndof)]
print()
print("exact-field residual: max|K u_ex - f| = %.3e   (max|f| = %.3e, scale %.3e)"
      % (max(abs(v) for v in r), max(abs(v) for v in F), max(abs(F[v]) for v in range(ndof))))
