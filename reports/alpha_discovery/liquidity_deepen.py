"""liquidity_deepen.py — deepen the 2 mode-conditional liquidity leads (§14/§18/§20/§21/§22).
Leads: (A) BEAR_CORRECTION + sell-sweep+reclaim+displacement -> LONG ; (B) BULL_CORRECTION + buy-sweep+reclaim+
displacement -> SHORT. Per era (b0/b1/2021/2022/2023): §14 winner-vs-loser (no-reclaim vs reclaim vs reclaim+disp),
§18 full labels + MFE/MAE/adverse-first, §20 event-N honesty (raw/effective/unique-days/independent-H4-episodes),
§21-22 tradeability with STRUCTURAL stop = swept swing extreme (event bar low for long / high for short), small
predeclared rr family. Causal, price-only, STRESS.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
from liquidity_event import events, align_mode, W, COOL, H

def lead_masks(m, regc, uniq, modename, side):
    E=events(m); ev,rc,dp,_=E["sell" if side=='L' else "buy"]
    if modename not in uniq: return None
    code=uniq.index(modename); base=(regc==code)
    ev=np.nan_to_num(ev.astype(float),nan=0).astype(bool); rc=np.nan_to_num(rc.astype(float),nan=0).astype(bool); dp=np.nan_to_num(dp.astype(float),nan=0).astype(bool)
    return dict(mode=base, ev=base&ev, no_rcl=base&ev&~rc, rcl_only=base&ev&rc&~dp, rcl_disp=base&ev&rc&dp)

def winner_loser(ou,od,mk,side,mask):
    def P(cond,lab):
        mm=mask&cond; dd=mm&dedup(mm,COOL); n=int(dd.sum())
        return (Pm(ou,od,lab[0],lab[1],side,H,dd)[0], n) if n>=25 else (None,n)
    b=Pm(ou,od,70,50,side,H,mask&mk["mode"]&dedup(mask&mk["mode"],COOL))[0]
    return b, P(mk["no_rcl"],(70,50)), P(mk["rcl_only"],(70,50)), P(mk["rcl_disp"],(70,50))

def tradeable(m, ev_idx, side, tag):
    o=m["open"].to_numpy(); hi=m["high"].to_numpy(); lo=m["low"].to_numpy()
    ev_idx=ev_idx[ev_idx<len(m)-1]; entry=o[ev_idx+1]
    sl=(entry-lo[ev_idx]) if side==1 else (hi[ev_idx]-entry)   # STRUCTURAL: swept extreme of the event bar
    ok=np.isfinite(sl)&(sl>0); ev_idx=ev_idx[ok]; sl=sl[ok]
    if len(ev_idx)<25: print(f"     [{tag}] tradeable events={len(ev_idx)} (thin)"); return
    print(f"     [{tag}] tradeable events={len(ev_idx)}  structural SL med={np.median(sl)/0.10:.0f}p")
    for rr in (1.0,1.5,2.0):
        tr=sb.simulate(m, ev_idx, side, sl, rr=rr, horizon=H, scenario="STRESS")
        if len(tr): mm=sb.metrics(tr,m,rr); print(f"        struct-SL rr{rr}: avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best10={mm['best10']:+.3f} medSL={mm['med_sl_pips']:.0f}p tpm={mm['trades_per_month']:.1f}")

def run_lead(name, modename, side_ch, side_num):
    print(f"\n===== LEAD {name}: {modename} + {'sell' if side_ch=='L' else 'buy'}-sweep+reclaim+disp -> {side_ch} =====")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    eras=[("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy()),("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())]
    eras+=[(str(y),sm,sh4,sb.align_context,dev&(yr==y)) for y in (2021,2022,2023)]
    for tag,m,h4,af,mask in eras:
        regc,uniq=align_mode(m,h4,af); ou,od,mfe,mae=passage_m15(m); mk=lead_masks(m,regc,uniq,modename,side_ch)
        if mk is None: print(f"  [{tag}] mode absent"); continue
        b,(pnr,nnr),(pro,nro),(prd,nrd)=winner_loser(ou,od,mk,side_ch,mask)
        f=lambda x:(f"{x:.2f}" if x is not None else "na")
        # event-N honesty on the full event
        dd=mask&mk["rcl_disp"]; raw=int(dd.sum()); eff=int((dd&dedup(dd,COOL)).sum())
        dt=(m["dt"] if "dt" in m.columns else pd.to_datetime(m["time"],unit="s",utc=True))
        days=len(set(dt[dd&dedup(dd,COOL)].dt.floor("D"))) if eff else 0
        print(f"  [{tag}] mode base P70/50={b:.2f} | WINNER-LOSER: no_rcl={f(pnr)}(n{nnr}) rcl_only={f(pro)}(n{nro}) rcl+disp={f(prd)}(n{nrd}) | full-event raw={raw}/eff={eff}/days={days}")
        if prd is not None:
            fm=mask&mk["rcl_disp"]&dedup(mask&mk["rcl_disp"],COOL); idx=np.where(fm)[0]
            print(f"     full-event MFE med/P75={np.median(mfe[idx]):.0f}/{np.percentile(mfe[idx],75):.0f}p MAE med/P75={np.median(mae[idx]):.0f}/{np.percentile(mae[idx],75):.0f}p")
            tradeable(m, idx, side_num, tag)

def main():
    run_lead("A", "BEAR_CORRECTION", 'L', 1)
    run_lead("B", "BULL_CORRECTION", 'S', -1)

if __name__=="__main__":
    main()
