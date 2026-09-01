import sys; sys.path.insert(0,'.')
from engine import *
from scan import D6, D4, M, causal_pct
from post import crve_cov
print("="*112); print("  CONFOUND AUDIT OF D4-MAG-6 (the only phenomenon that survived the battery)"); print("="*112)
S=D6; x=D4(S); y=S.mag(); cl=MON[S.idx]
ar=a_rng[S.idx]; ac=S.acmp   # causal percentile of Asia range / 20d ATR
print(f"  is 'Asia closed at the edge of its range' just 'Asia range was small'?")
print(f"    mean Asia range when state=1 : {np.nanmean(ar[x==1]):.3f} USD")
print(f"    mean Asia range when state=0 : {np.nanmean(ar[x==0]):.3f} USD")
print(f"    mean Asia-range percentile   : state=1 {np.nanmean(ac[x==1]):.3f}   state=0 {np.nanmean(ac[x==0]):.3f}")
r0=crve(y,x,cl)
print(f"\n    raw                                        lift {r0['lift']:+8.3f}  z {r0['z']:+6.2f}")
r1=crve_cov(y,x,[ac],cl)
print(f"    + Asia-range percentile as covariate       lift {r1['lift']:+8.3f}  z {r1['z']:+6.2f}")
cov=[causal_pct(atr20d[S.idx]), causal_pct((np.abs(ret24)/atr20d)[S.idx]), S.clp, causal_pct(vol20[S.idx]), ac]
r2=crve_cov(y,x,cov,cl)
print(f"    + full control set INCLUDING Asia range    lift {r2['lift']:+8.3f}  z {r2['z']:+6.2f}")
print(f"\n  stratified by Asia-range tercile (does it hold where Asia range is NOT small?):")
q=np.nanquantile(ac,[1/3,2/3])
for nm,m in (("low  Asia range", ac<=q[0]), ("mid  Asia range",(ac>q[0])&(ac<=q[1])), ("high Asia range", ac>q[1])):
    r=crve(y[m],x[m],cl[m])
    print(f"    {nm:18} n_cond {r['n_cond']:5d}  base {r['base']:7.2f}  lift {r['lift']:+8.3f}  z {r['z']:+6.2f}" if r else f"    {nm}: n/a")
print(f"\n  and the direction companion, for the record:")
rd=crve(S.dir_(np.where(S.aclp>=.5,1.0,-1.0)), x, cl)
print(f"    D4 -> move toward the Asia-close edge, 6h : lift {rd['lift']:+8.3f}p  z {rd['z']:+6.2f}")
