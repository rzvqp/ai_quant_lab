"""F3-TEMPORAL — calendar/temporal information class (NOT price-structural). DEV selection.
  1) Day-of-week drift (descriptive): mean D1 open->close R-normalized return + up-rate by UTC weekday.
  2) Weekly-open gap: gap = first-D1-open-of-week minus prior-week-last-close. Continuation vs fade, H4 path screen.
  3) New-week first-day-range carry: break of day-1 range -> hold to week end.
Firewall via swing_base.
"""
import numpy as np, pandas as pd
import swing_base as sb

H = 30  # ~5 trading days (H4 bars)

def dow_drift(d1):
    dev = d1[d1["is_dev"]].copy()
    ret = (dev["close"] - dev["open"]).to_numpy()
    atr = dev["atr"].to_numpy()
    rn = ret/atr
    wd = dev["dt"].dt.dayofweek.to_numpy()  # 0=Mon
    names=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    print("  DOW drift (D1 open->close, normalized by ATR):")
    for w in range(7):
        sel=wd==w
        if sel.sum()<10: continue
        print(f"    {names[w]}: n={int(sel.sum())} meanR={np.nanmean(rn[sel]):+.3f} upRate={(ret[sel]>0).mean():.2f}")

def weekly_gap(d1, h4, dev_mask):
    d1=d1.sort_values("time").reset_index(drop=True)
    iso = d1["dt"].dt.isocalendar()
    d1=d1.assign(wk=iso["year"].astype(int)*100+iso["week"].astype(int))
    first_idx = d1.groupby("wk").head(1).index.to_numpy()
    cl=d1["close"].to_numpy(); op=d1["open"].to_numpy(); t=d1["time"].to_numpy()
    # gap at first day of week = open[first] - close[first-1]
    gaps=[]
    for fi in first_idx:
        if fi==0: continue
        gaps.append((fi, op[fi]-cl[fi-1], t[fi]))
    gaps=[(fi,g,tt) for fi,g,tt in gaps if abs(g)>0]
    garr=np.array([g for _,g,_ in gaps]); tarr=np.array([tt for _,_,tt in gaps])
    print(f"  weekly gaps: n={len(gaps)} med|gap|={np.median(np.abs(garr)):.2f}USD "
          f"upgaps={(garr>0).mean():.2f}")
    # map each week-open day time to first H4 bar at/after that time; trade continuation & fade
    h4t=h4["time"].to_numpy(); o=h4["open"].to_numpy(); h=h4["high"].to_numpy(); l=h4["low"].to_numpy()
    atr=h4["atr"].to_numpy()
    ev=[]; gsign=[]
    for fi,g,tt in gaps:
        j=int(np.searchsorted(h4t, tt, side="left"))
        if j>=len(h4t)-1 or not dev_mask[j]: continue
        ev.append(j); gsign.append(np.sign(g))
    ev=np.array(ev); gsign=np.array(gsign)
    # structural stop = 1.0*ATR at the week-open H4 bar (temporal signal has no price structure -> ATR stop)
    risk=np.array([atr[j] for j in ev]); ok=np.isfinite(risk)&(risk>0)
    ev,gsign,risk=ev[ok],gsign[ok],risk[ok]
    for mode,dirn in (("CONTINUATION",+1),("FADE",-1)):
        for rr in (1.0,1.5):
            sides=(gsign*dirn).astype(int)  # per-event side
            # simulate per side group
            trs=[]
            for s in (+1,-1):
                m=sides==s
                if m.sum()==0: continue
                tr=sb.simulate(h4, ev[m], s, risk[m], rr=rr, horizon=H, scenario="STRESS")
                trs.append(tr)
            if not trs: continue
            tr=pd.concat(trs, ignore_index=True)
            mt=sb.metrics(tr,h4,rr)
            py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(mt["per_year"].items()))
            print(f"  gap {mode} rr={rr}: N={mt['N']} WRt={mt['WR_target']:.2f} avgR={mt['avgR']:+.3f} "
                  f"PF={mt['PF']:.2f} best10={mt['best10']:+.3f} advFirst={ (tr['mae_R']>=1.0).mean():.2f} "
                  f"medSL={tr['sl_pips'].median():.0f}p | {py}")

def main():
    tfs=sb.build_frames(); d1,h4=tfs["D1"],tfs["H4"]; dev_mask=h4["is_dev"].to_numpy()
    print(f"F3-TEMPORAL  D1 DEV days={int(d1['is_dev'].sum())}")
    dow_drift(d1)
    weekly_gap(d1,h4,dev_mask)

if __name__=="__main__":
    main()
