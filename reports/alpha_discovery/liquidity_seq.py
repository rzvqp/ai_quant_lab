"""liquidity_seq.py — MULTI-BAR liquidity SEQUENCE reformulation (one predeclared change, §12-13; faithful to the
inherently multi-bar sweep->reclaim->displacement->path). Sweep on bar t (penetrate recent 20-bar swing); within
a 6-bar window a bar j reclaims (close back inside) AND displaces (strong opposite body >0.6 ATR); decision = j,
entry = j+1 open, STRUCTURAL stop = swept extreme over [t..j] (now with room). Conditioned on frozen H4 mode.
Tradeability net STRESS per mode x side x era (small predeclared rr). Causal, price-only, scan-level dedup.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_m15_discover import dedup
from market_mode import mode, MODES
from liquidity_event import align_mode
W=20; WIN=6; H=32

def scan(m, side):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); o=m["open"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    swL=pd.Series(l).rolling(W).min().shift(1).to_numpy(); swH=pd.Series(h).rolling(W).max().shift(1).to_numpy()
    dec=[]; stop=[]; used=-1
    for t in range(n):
        if side=='L':
            if not (np.isfinite(swL[t]) and l[t]<swL[t]) or t<=used: continue
            lvl=swL[t]; ext=l[t]
            for j in range(t, min(t+1+WIN,n)):
                ext=min(ext,l[j])
                if c[j]>lvl and (c[j]-o[j])>0.6*atr[j]:
                    dec.append(j); stop.append(ext); used=j; break
        else:
            if not (np.isfinite(swH[t]) and h[t]>swH[t]) or t<=used: continue
            lvl=swH[t]; ext=h[t]
            for j in range(t, min(t+1+WIN,n)):
                ext=max(ext,h[j])
                if c[j]<lvl and (o[j]-c[j])>0.6*atr[j]:
                    dec.append(j); stop.append(ext); used=j; break
    return np.array(dec,dtype=int), np.array(stop,dtype=float)

def trade(m, dec, stop, side_num, mask, tag):
    o=m["open"].to_numpy(); dec2=dec[(dec<len(m)-1)]; stp=stop[(dec<len(m)-1)]
    keep=mask[dec2]; dec2=dec2[keep]; stp=stp[keep]
    if len(dec2)<25: print(f"     [{tag}] events={len(dec2)}(thin)"); return None
    entry=o[dec2+1]; sl=np.abs(entry-stp); ok=np.isfinite(sl)&(sl>0); dec2=dec2[ok]; sl=sl[ok]
    dt=(m["dt"] if "dt" in m.columns else pd.to_datetime(m["time"],unit="s",utc=True))
    days=len(set(dt.iloc[dec2].dt.floor("D"))); tpm_days=days
    print(f"     [{tag}] events={len(dec2)} uniqueDays={days} structSL med={np.median(sl)/0.10:.0f}p")
    best=None
    for rr in (1.0,1.5,2.0):
        tr=sb.simulate(m, dec2, side_num, sl, rr=rr, horizon=H, scenario="STRESS")
        if len(tr):
            mm=sb.metrics(tr,m,rr); print(f"        rr{rr}: avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best10={mm['best10']:+.3f} medSL={mm['med_sl_pips']:.0f}p tpm={mm['trades_per_month']:.1f}")
            if best is None or mm['avgR']>best[1]: best=(rr,mm['avgR'])
    return best

def run(side_ch, side_num):
    lab={'L':'sellside-sweep->LONG','S':'buyside-sweep->SHORT'}[side_ch]
    print(f"\n===== MULTI-BAR SEQUENCE: {lab} (structural stop=swept extreme over [t..displacement]) =====")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    eras=[("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy()),("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())]
    eras+=[(str(y),sm,sh4,sb.align_context,dev&(yr==y)) for y in (2021,2022,2023)]
    # scan once per frame
    scans={}
    for key,m in (("hist",hm),("gated",sm)): scans[key]=scan(m,side_ch)
    for md in MODES:
        printed=False
        for tag,m,h4,af,mask in eras:
            dec,stop=scans["hist" if tag in ("b0","b1") else "gated"]
            regc,uniq=align_mode(m,h4,af)
            if md not in uniq: continue
            code=uniq.index(md); modemask=mask&(regc==code)
            # keep only decision bars whose mode==md and in era
            keep=np.zeros(len(m),bool); keep[dec]=True; cell=keep&modemask
            di=np.where(cell)[0]
            if len(di)<25: continue
            if not printed: print(f"  --- H4={md} ---"); printed=True
            # map di back to stop
            pos={d:s for d,s in zip(dec,stop)}; st=np.array([pos[d] for d in di])
            trade(m, di, st, side_num, np.ones(len(m),bool), f"{md[:10]} {tag}")

def main():
    run('L',1); run('S',-1)

if __name__=="__main__":
    main()
