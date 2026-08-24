"""cur_verify.py — SKEPTICISM GATE for the current-regime short survivor candidate (SHORT_wide 4ATR rr3 H96).
Checks: per-YEAR avgR within current-like (episode concentration), best-1%/10%-removed (tail), no-filter variant
(is the ema20 entry doing real work vs pure regime-short), S5 same-day overlap (independence). STRESS. Before freezing.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at, _load
from batch_a import orb

def trades(sigfn, side, rr, H, cool):
    m,_=_load(); idx,sl=sigfn(m); idx=np.asarray(idx); sl=np.asarray(sl,float)
    o=np.argsort(idx); idx=idx[o]; sl=sl[o]; dd=sb.dedup_events(idx,cool); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]
    ok=np.isfinite(sl)&(sl>0); idx=idx[ok]; sl=sl[ok]
    tr=sb.simulate(m,idx,side,sl,rr=rr,horizon=H,scenario="STRESS")
    te=tr["t_entry"].to_numpy(); tr=tr.assign(cl=like_at(te),yr=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.year.to_numpy())
    return tr[tr["cl"]]  # current-like only

def sw(fr,katr=4.0,ctx=True):
    c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); n=len(fr); e20=fr["ema20"].to_numpy()
    ev=(np.isfinite(atr))&(atr>0);
    if ctx: ev=ev&(c<e20)
    idx=np.where(ev)[0]; idx=idx[idx<n-1]; return idx,katr*atr[idx]

def main():
    tr=trades(lambda f:sw(f,4.0,True),-1,3.0,96,24); r=tr["R"].to_numpy(); yr=tr["yr"].to_numpy()
    print(f"SHORT_wide 4ATR rr3 H96 (current-like): N={len(r)} avgR={r.mean():+.3f}")
    print("  per-year (current-like):", {int(y):(round(float(r[yr==y].mean()),3),int((yr==y).sum())) for y in sorted(set(yr))})
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    print(f"  best-1%-removed={sr[:-k1].mean():+.3f}  best-10%-removed={sr[:-k10].mean():+.3f}  maxWin={r.max():.2f} PF={sb._pf(r):.2f} WR={(r>0).mean():.2f}")
    # no-filter (pure regime short, wide stop)
    tr2=trades(lambda f:sw(f,4.0,False),-1,3.0,96,24); r2=tr2["R"].to_numpy(); yr2=tr2["yr"].to_numpy()
    print(f"\n  NO-FILTER (pure regime short) N={len(r2)} avgR={r2.mean():+.3f} DISC(<=2021)={r2[yr2<=2021].mean():+.3f} CONF(22-24)={r2[(yr2>=2022)&(yr2<=2024)].mean():+.3f} OOS(25+)={r2[yr2>=2025].mean():+.3f}")
    # S5 overlap (same-day)
    s5=trades(lambda f:orb(f,13,21,1),1,3.0,48,8)
    d=lambda tt: set(pd.to_datetime(tt["t_entry"],unit="s",utc=True).dt.floor("D").astype("int64"))
    ov=len(d(tr)&d(s5))/max(len(d(tr)),1)
    print(f"  S5 same-day overlap: {ov:.0%} (S5 is long/NY-breakout; this is wide-stop regime-short -> direction-opposite)")

if __name__=="__main__":
    main()
