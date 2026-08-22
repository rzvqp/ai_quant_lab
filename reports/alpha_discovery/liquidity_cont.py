"""liquidity_cont.py — CONTINUATION / acceptance branch of the liquidity family (§14 CASE B: event + NO reclaim).
Sweep beyond a recent 20-bar swing, then within 6 bars a bar j ACCEPTS beyond (close stays past the level) WITH
strong same-direction displacement -> CONTINUATION. sellside-sweep + accept-below + bearish displacement -> SHORT;
buyside-sweep + accept-above + bullish displacement -> LONG. Structural stop = OPPOSITE extreme over [t..j]
(continuation fails if reversed). Conditioned on frozen H4 mode; net STRESS per mode x era; cross-era. Causal.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from market_mode import mode, MODES
from liquidity_event import align_mode
W=20; WIN=6; H=32

def scan(m, side):   # side 'S' = sellside-sweep->short-continuation ; 'L' = buyside-sweep->long-continuation
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); o=m["open"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    swL=pd.Series(l).rolling(W).min().shift(1).to_numpy(); swH=pd.Series(h).rolling(W).max().shift(1).to_numpy()
    dec=[]; stop=[]; used=-1
    for t in range(n):
        if side=='S':
            if not (np.isfinite(swL[t]) and l[t]<swL[t]) or t<=used: continue
            lvl=swL[t]; opp=h[t]
            for j in range(t, min(t+1+WIN,n)):
                opp=max(opp,h[j])
                if c[j]<lvl and (o[j]-c[j])>0.6*atr[j]:      # accepted below + bearish displacement
                    dec.append(j); stop.append(opp); used=j; break
        else:
            if not (np.isfinite(swH[t]) and h[t]>swH[t]) or t<=used: continue
            lvl=swH[t]; opp=l[t]
            for j in range(t, min(t+1+WIN,n)):
                opp=min(opp,l[j])
                if c[j]>lvl and (c[j]-o[j])>0.6*atr[j]:      # accepted above + bullish displacement
                    dec.append(j); stop.append(opp); used=j; break
    return np.array(dec,dtype=int), np.array(stop,dtype=float)

def trade(m, di, st, side_num, tag):
    o=m["open"].to_numpy(); di=di[di<len(m)-1]; st=st[:len(di)] if len(st)!=len(di) else st
    entry=o[di+1]; sl=np.abs(entry-st); ok=np.isfinite(sl)&(sl>0); di=di[ok]; sl=sl[ok]
    if len(di)<25: print(f"     [{tag}] events={len(di)}(thin)"); return
    print(f"     [{tag}] events={len(di)} structSL med={np.median(sl)/0.10:.0f}p")
    for rr in (1.0,1.5,2.0):
        tr=sb.simulate(m, di, side_num, sl, rr=rr, horizon=H, scenario="STRESS")
        if len(tr): mm=sb.metrics(tr,m,rr); print(f"        rr{rr}: avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best10={mm['best10']:+.3f} medSL={mm['med_sl_pips']:.0f}p tpm={mm['trades_per_month']:.1f}")

def run(side_ch, side_num):
    lab={'S':'sellside-sweep+accept -> SHORT continuation','L':'buyside-sweep+accept -> LONG continuation'}[side_ch]
    print(f"\n===== CONTINUATION: {lab} =====")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    eras=[("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy()),("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())]
    eras+=[(str(y),sm,sh4,sb.align_context,dev&(yr==y)) for y in (2021,2022,2023)]
    scans={"hist":scan(hm,side_ch),"gated":scan(sm,side_ch)}
    for md in MODES:
        printed=False
        for tag,m,h4,af,mask in eras:
            dec,stop=scans["hist" if tag in ("b0","b1") else "gated"]
            regc,uniq=align_mode(m,h4,af)
            if md not in uniq: continue
            code=uniq.index(md); modemask=mask&(regc==code)
            keep=np.zeros(len(m),bool); keep[dec]=True; di=np.where(keep&modemask)[0]
            if len(di)<25: continue
            if not printed: print(f"  --- H4={md} ---"); printed=True
            pos={d:s for d,s in zip(dec,stop)}; st=np.array([pos[d] for d in di])
            trade(m, di, st, side_num, f"{md[:10]} {tag}")

def main():
    run('S',-1); run('L',1)

if __name__=="__main__":
    main()
