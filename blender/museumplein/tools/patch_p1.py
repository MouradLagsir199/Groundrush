import json, numpy as np, sys
sys.path.insert(0,'tools')
from contour_fit import normals
from robust_outline import robust_closed_spline, rdp_closed
from scipy.spatial import cKDTree
park=json.load(open('data/park.json'))
area=lambda P:0.5*abs(np.sum(P[:,0]*np.roll(P[:,1],-1)-np.roll(P[:,0],-1)*P[:,1]))
def dens(P,ds=0.05):
    seg=np.linalg.norm(np.diff(np.vstack([P,P[:1]]),axis=0),axis=1); cum=np.concatenate([[0],np.cumsum(seg)])
    ss=np.arange(0,cum[-1],ds); P2=np.vstack([P,P[:1]])
    return np.stack([np.interp(ss,cum,P2[:,0]),np.interp(ss,cum,P2[:,1])],1)
R=json.load(open('refs/edge_inner_lines.json'))
c=np.array(R['noord']['c']); d=np.array(R['noord']['d']); d=d if d[0]>0 else -d; nN=np.array([-d[1],d[0]])
def patch(P, inbox, newpts):
    m=np.array([inbox(x,y) for x,y in P])
    start=np.where(m & ~np.roll(m,1))[0]
    assert len(start)==1, f"run niet aaneengesloten: {len(start)}"
    s=start[0]; P=np.roll(P,-s,axis=0); m=np.roll(m,-s)
    e=np.where(~m)[0][0]
    return np.vstack([np.array(newpts),P[e:]])
inner=dens(np.array(park['slab']['inner'])); outer=dens(np.array(park['slab']['outer']))
xs=np.arange(8.6,19.4,0.25)
N_in=[c+((x-c[0])/d[0])*d for x in xs]
N_out=[p+0.40*nN for p in N_in]
NW_in=[(6.0,20.3),(6.5,20.97),(7.0,21.8),(7.27,22.07),(7.52,22.6),(7.6,22.73),(7.83,22.97),(8.17,23.17)]
NW_out=[(6.0,20.3),(6.5,20.97),(7.0,21.8),(7.2,22.05),(6.53,22.23),(6.57,22.6),(6.83,22.97),(7.17,23.23),(7.5,23.43),(7.83,23.53),(8.17,23.62)]
NE_in=[(19.6,20.1),(20.0,19.97),(20.5,19.8),(20.8,19.55),(21.0,19.3),(21.13,18.93),(21.1,18.73),(20.9,18.07),(20.63,17.3),(20.5,16.8)]
NE_out=[(19.6,20.53),(20.0,20.45),(20.5,20.23),(21.0,20.0),(21.5,19.7),(21.8,19.13),(21.83,18.47),(21.8,18.05),(20.9,18.0),(20.63,17.3),(20.5,16.8)]
def box(x,y): return (y>20.0 and 4.8<x<8.6) or (x>19.4 and y>16.6) or (8.6<=x<=19.4 and y>19.9)
inner2=patch(inner,box,NW_in+[tuple(p) for p in N_in]+NE_in)
outer2=patch(outer,box,NW_out+[tuple(p) for p in N_out]+NE_out)
O=dens(outer2,0.05); nrmO=normals(O)
I=dens(inner2,0.05)
mS=np.array([(-11.0<x<11.0 and y<-12.5) for x,y in I])
t=cKDTree(O)
for i in np.where(mS)[0]:
    dd,j=t.query(I[i]); I[i]=O[j]-0.50*nrmO[j]
for nm,P in [("inner",I),("outer",O)]:
    S,w,dv=robust_closed_spline(P,smooth_cm=0.6,thr_cm=4.0)
    Rr=rdp_closed(S,0.008)
    park['slab'][nm]=Rr.round(3).tolist()
    print(nm,"punten",len(Rr),"opp",round(area(Rr),1),"verwijderd",int((w==0).sum()))
json.dump(park,open('data/park.json','w'),indent=1)
