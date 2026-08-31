"""htf_diag.py — decisive diagnostic on the only live lead (TGT_BREAK) + the bull-beta control.

Q: is TGT_BREAK's O-era (2023+) positivity a genuine target-space STRUCTURAL edge, or just beta to the 2023-26 gold bull (R20
era-trend artifact)? We split by DIRECTION x SESSION x ERA and compare each cell against a matched BULL-BETA CONTROL: random same-side
entries in the same era/session held the same horizon with the same structural-stop distribution. If TGT_BREAK longs don't beat random
longs in the same regime, the 'edge' is pure directional beta (already known non-generalizing per R20).
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import htf_core as HC
from htf_setups import prep, detect, evaluate

def cellstats(m, rows, mask):
    if mask.sum()<20: return None
    net=np.array([r["net_R"] for r in rows])[mask]; g=np.array([r["gross_R"] for r in rows])[mask]
    return net.mean(), (g>0).mean(), int(mask.sum())

def main():
    m,H1,H4=prep()
    tr=detect(m,H1,H4,"TGT_BREAK",htf_on=True)
    rows=evaluate(m,tr)
    ent=np.array([r["ent"] for r in rows]); side=np.array([r["side"] for r in rows])
    yr=m["dt"].dt.year.values[ent]; hr=m["dt"].dt.hour.values[ent]
    era=np.where(yr<=2018,"D",np.where(yr<=2022,"C","O"))
    def sess(h): return "AS" if h<8 else ("LN" if h<13 else ("NY" if h<20 else "LT"))
    ss=np.array([sess(x) for x in hr])
    net=np.array([r["net_R"] for r in rows]); risk=np.array([r["risk_px"] for r in rows])
    print(f"TGT_BREAK total N={len(rows)} netR={net.mean():+.3f}")
    print("\n-- direction x era --")
    for d,dn in [(+1,"LONG"),(-1,"SHORT")]:
        for e in ["D","C","O"]:
            st=cellstats(m,rows,(side==d)&(era==e))
            if st: print(f"  {dn:5s} {e}: netR={st[0]:+.3f} WR={st[1]:.3f} N={st[2]}")
    print("\n-- O-era direction x session --")
    for d,dn in [(+1,"LONG"),(-1,"SHORT")]:
        for s in ["AS","LN","NY","LT"]:
            st=cellstats(m,rows,(side==d)&(era=="O")&(ss==s))
            if st: print(f"  {dn:5s} O {s}: netR={st[0]:+.3f} WR={st[1]:.3f} N={st[2]}")
    # BULL-BETA CONTROL: for each era, random same-side entries with matched structural-stop dist, same horizon
    print("\n-- BULL-BETA CONTROL: random same-side entries (matched stop dist), by direction x era --")
    rng=np.random.RandomState(0); nm=len(m); catr=m["atr"].values; cpx=m["close"].values
    for d,dn in [(+1,"LONG"),(-1,"SHORT")]:
        for e,(y0,y1) in [("D",(2011,2018)),("C",(2019,2022)),("O",(2023,2026))]:
            pool=np.where((m["dt"].dt.year.values>=y0)&(m["dt"].dt.year.values<=y1)&(np.arange(nm)>400)&(np.arange(nm)<nm-70))[0]
            # sample matched risks from the actual TGT_BREAK trades of this side (fallback: 2xATR)
            rr=risk[(side==d)&(era==e)]
            if len(rr)<20 or len(pool)<200: continue
            samp=rng.choice(pool, size=2000, replace=True); rk=rng.choice(rr, size=2000, replace=True)
            R=[]
            for t,risk_i in zip(samp,rk):
                stop = cpx[t]-risk_i if d>0 else cpx[t]+risk_i
                o=HC.outcome(m,t,d,stop,2.0,64)
                if o: R.append(o["net_R"])
            R=np.array(R)
            print(f"  CONTROL {dn:5s} {e}: netR={R.mean():+.3f} WR={(R>0).mean():.3f} N={len(R)} (random {dn} in {e})")

if __name__=="__main__":
    main()
