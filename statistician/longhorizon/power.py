import sys, json; sys.path.insert(0,'.')
from engine import *
from scan import S6,S12,S24,S48,D6
print("="*112); print("  HOW BIG AN EFFECT COULD THIS SCAN HAVE SEEN?  (descriptive -- no new hypotheses)"); print("="*112)
print("  Absence of evidence is only evidence of absence if the scan was powered. Detectable lift at")
print("  alpha .05 / 80% power, for a state occurring at ~20% of episodes.\n")
print(f"  {'horizon':<10} {'episodes':>9} {'n_cond~20%':>11} {'sd(ret)':>9} {'sd(|ret|)':>10} {'min detectable DIR':>20} {'as % of base |move|':>21}")
rows=[]
for nm,S in (("6h",S6),("12h",S12),("24h",S24),("48h",S48)):
    t=targets(S.idx,S.h); r=t["ret"]; a=t["absret"]
    n=len(S.idx); n1=int(.2*n); n0=n-n1
    sd=np.nanstd(r); se=sd*math.sqrt(1/n1+1/n0); mdd=2.802*se
    sda=np.nanstd(a); sea=sda*math.sqrt(1/n1+1/n0); mdm=2.802*sea
    base=np.nanmean(a)
    print(f"  {nm:<10} {n:>9} {n1:>11} {sd:>9.1f} {sda:>10.1f} {mdd:>19.1f}p {100*mdd/base:>20.0f}%")
    rows.append((nm,n,base,mdd,mdm,np.nanmean(t['exc']),np.nanmean(t['mfe']),np.nanmean(t['mae'])))
print("\n  NATURAL PAYOFF GEOMETRY AT EACH HORIZON (unconditional, all episodes) -- for CEO question 4")
print(f"  {'horizon':<10} {'mean |net move|':>16} {'mean MFE':>10} {'mean MAE':>10} {'mean largest exc':>18} {'P(exc>=100p)':>14} {'P(exc>=300p)':>14}")
for nm,S in (("6h",S6),("12h",S12),("24h",S24),("48h",S48)):
    t=targets(S.idx,S.h)
    print(f"  {nm:<10} {np.nanmean(t['absret']):>15.0f}p {np.nanmean(t['mfe']):>9.0f}p {np.nanmean(t['mae']):>9.0f}p "
          f"{np.nanmean(t['exc']):>17.0f}p {np.nanmean(t['exc']>=100):>13.1%} {np.nanmean(t['exc']>=300):>13.1%}")
print("\n  DIRECTIONAL BASE RATE (is there any unconditional drift to exploit?)")
for nm,S in (("6h",S6),("24h",S24),("48h",S48)):
    t=targets(S.idx,S.h); r=t["ret"]
    rr=crve(r, np.ones(len(r)), MON[S.idx]) # not usable; do a simple clustered mean instead
    ok=np.isfinite(r); y=r[ok]; cl=MON[S.idx][ok]
    g=pd.DataFrame({'m':cl,'y':y}).groupby('m')['y'].agg(['sum','count'])
    mu=y.mean(); G=len(g); n=len(y)
    resid=g['sum'].to_numpy()-g['count'].to_numpy()*mu
    se=math.sqrt((resid**2).sum()/n**2*(G/(G-1)))
    print(f"    {nm:<5} mean net move {mu:+7.2f}p   clustered se {se:5.2f}   z {mu/se:+5.2f}   P(up) {np.mean(y>0):.3f}")

print("\n" + "="*112); print("  COMPARISON WITH THE M5 PROGRAM ON A LIKE-FOR-LIKE (INDEPENDENT-EPISODE) BASIS"); print("="*112)
print("  Scout V2's headline |z| values (up to 8.89) came from OVERLAPPING M5 bars. Its own non-overlap")
print("  check on the strongest lead (V2-4) gave z = -2.40 on 150-246 effective observations.")
print("  This scan's best surviving effect (D4-MAG-6) gives z = -2.72 on 1,455 independent episodes.")
print("  On the only comparable basis -- independent episodes -- long-horizon and M5 structure are the")
print("  SAME ORDER OF MAGNITUDE. The apparent M5 superiority was a pseudo-N artefact, not more signal.")
