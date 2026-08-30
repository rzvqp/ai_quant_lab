"""htf_setups.py — H1_H4_SETUP_M5_EXECUTION_V1: H1 structural setups selected by H4 context, with the §17 HTF-on/off contrast.

Setups detected on the H1 frame (causal), entered at the M15 close following H1 confirmation (baseline entry = next M15 decision-time).
For each family we report the SAME H1 setup WITH the H4-context/location filter vs WITHOUT it, to isolate whether HTF SELECTION creates
the asymmetry (that is the mandate's core question). Structural stop = opposite recent H1 swing (bounded [0.8,6]x M15 ATR). Target 2R.
Cost = per-trade price cost (0.419/risk) + flat-0.24R reported. Independent H4 episodes / H1 setups reported (no fake N).
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import htf_core as HC

def prep():
    m,H1,H4=HC.build()
    # map each H1 bar to last completed H4 bar
    h4ct=H4["close_time"].values.astype("int64")
    H1["h4i"]=np.searchsorted(h4ct, H1["close_time"].values.astype("int64"), side="right")-1
    # map each H1 bar -> first M15 bar whose close_time >= H1 close_time (entry bar)
    mct=m["ct"].values.astype("int64")
    H1["m15entry"]=np.searchsorted(mct, H1["close_time"].values.astype("int64"), side="left")
    m["atr"]=m["atr"].values
    return m,H1,H4

def detect(m,H1,H4,family,htf_on=True):
    """Return list of (m15_anchor_idx, side, stop_px) for a family. htf_on toggles the H4 context/location filter."""
    c=H1["close"].values; h=H1["high"].values; l=H1["low"].values
    emaf=H1["ema_f"].values; emas=H1["ema_s"].values; swH=H1["swH"].values; swL=H1["swL"].values
    hh=H1["hh"].values; ll=H1["ll"].values; h4i=H1["h4i"].values; ment=H1["m15entry"].values
    ctxH4=H4["ctx"].values; H4hi=H4["hh"].values; H4lo=H4["ll"].values; H4c=H4["close"].values
    n=len(H1); nm=len(m); out=[]
    for i in range(60,n):
        hi=h4i[i]
        if hi<0: continue
        ctx=ctxH4[hi]; ent=ment[i]
        if ent>=nm-1 or ent<400: continue
        px=c[i]
        # H4 leg location: discount/premium within [H4lo,H4hi]
        rngH4=H4hi[hi]-H4lo[hi]
        loc=(px-H4lo[hi])/rngH4 if rngH4>1e-9 else 0.5     # 0=at H4 low(discount),1=at H4 high(premium)
        if family=="PBK_TREND":
            # H1 pullback then turn-up in H4 uptrend & discount ; symmetric short
            up_turn = (c[i]>h[i-1]) and (l[i-1]<l[i-2]) and (c[i-2]<c[i-3])   # local dip then close>prior high
            dn_turn = (c[i]<l[i-1]) and (h[i-1]>h[i-2]) and (c[i-2]>c[i-3])
            if up_turn:
                if htf_on and not (ctx=="TREND_UP" and loc<0.55): continue
                stop=min(l[i-1],l[i-2]);
                if px-stop<=0: continue
                out.append((ent,+1,stop))
            elif dn_turn:
                if htf_on and not (ctx=="TREND_DOWN" and loc>0.45): continue
                stop=max(h[i-1],h[i-2])
                if stop-px<=0: continue
                out.append((ent,-1,stop))
        elif family=="RECLAIM":
            # local sweep-reclaim: bar i-1 sweeps below a 10-bar local support, bar i closes back above it -> long ; symmetric
            sup=np.min(l[i-11:i-1]); res=np.max(h[i-11:i-1])
            recl_up = (l[i-1]<sup) and (c[i]>sup)
            recl_dn = (h[i-1]>res) and (c[i]<res)
            swL=swL if False else swL  # (keep names)
            if recl_up:
                if htf_on and ctx=="TREND_DOWN": continue     # don't reclaim-long into H4 downtrend
                stop=min(l[i-1],l[i]);
                if px-stop<=0: continue
                out.append((ent,+1,stop))
            elif recl_dn:
                if htf_on and ctx=="TREND_UP": continue
                stop=max(h[i-1],h[i])
                if stop-px<=0: continue
                out.append((ent,-1,stop))
        elif family=="RANGE_FADE":
            # H4 BALANCE: H1 pokes 50-bar extreme then closes back inside -> fade to mid
            fade_dn = (h[i]>hh[i]) and (c[i]<hh[i])           # poked high, closed back below -> short
            fade_up = (l[i]<ll[i]) and (c[i]>ll[i])           # poked low, closed back above -> long
            if fade_dn:
                if htf_on and ctx!="BALANCE": continue
                stop=h[i];
                if stop-px<=0: continue
                out.append((ent,-1,stop))
            elif fade_up:
                if htf_on and ctx!="BALANCE": continue
                stop=l[i]
                if px-stop<=0: continue
                out.append((ent,+1,stop))
        elif family=="TGT_BREAK":
            # H1 breaks its swing extreme; take ONLY when H4 target space beyond is large (open room)
            brk_up=(c[i]>swH[i]) and (c[i-1]<=swH[i]); brk_dn=(c[i]<swL[i]) and (c[i-1]>=swL[i])
            atrH4=H4["atr"].values[hi]
            if brk_up:
                room=(H4hi[hi]-px)/atrH4 if atrH4>0 else 0     # room to prior H4 high
                if htf_on and not (ctx in ("TREND_UP","BALANCE") and room>1.0): continue
                stop=swL[i] if swL[i]<px else px-2*m["atr"].values[ent]
                if px-stop<=0: continue
                out.append((ent,+1,stop))
            elif brk_dn:
                room=(px-H4lo[hi])/atrH4 if atrH4>0 else 0
                if htf_on and not (ctx in ("TREND_DOWN","BALANCE") and room>1.0): continue
                stop=swH[i] if swH[i]>px else px+2*m["atr"].values[ent]
                if stop-px<=0: continue
                out.append((ent,-1,stop))
    return out

def evaluate(m, trades, tgtR=2.0, H=64):
    rows=[]
    for ent,side,stop in trades:
        # bound risk to [0.8,6] x M15 ATR
        atr=m["atr"].values[ent]; risk=abs(m["close"].values[ent]-stop)
        if not (0.8*atr<=risk<=6*atr): continue
        o=HC.outcome(m,ent,side,stop,tgtR,H)
        if o is None: continue
        o["ent"]=ent; o["side"]=side; rows.append(o)
    return rows

def summ(m, rows, label):
    if len(rows)<30: print(f"{label:34s} N={len(rows)} (too small)"); return None
    yr=m["dt"].dt.year.values; hr=m["dt"].dt.hour.values
    net=np.array([r["net_R"] for r in rows]); netf=np.array([r["net_R_flat"] for r in rows])
    g=np.array([r["gross_R"] for r in rows]); win=(g>0).mean()
    ent=np.array([r["ent"] for r in rows]); ey=yr[ent]
    era=np.where(ey<=2018,"D",np.where(ey<=2022,"C","O"))
    def m_(mask): return net[mask].mean() if mask.sum()>0 else np.nan
    # independent episodes: dedup entries within H bars
    from tsm_core import independent_episodes
    ie=len(independent_episodes(ent,H=64))
    mfe=np.median([r["mfe_pips"] for r in rows]); cap=np.median([r["captured_pips"] for r in rows])
    hold=np.median([r["hold"] for r in rows]); costpct=np.median([r["cost_pct_risk"] for r in rows])
    print(f"{label:34s} N={len(rows):5d} ie={ie:4d} | netR={net.mean():+.3f} flat={netf.mean():+.3f} WR={win:.3f} "
          f"D={m_(era=='D'):+.3f} C={m_(era=='C'):+.3f} O={m_(era=='O'):+.3f} | MFEpip={mfe:.0f} capPip={cap:+.0f} hold={hold:.0f} cost%R={costpct:.2f}")
    return dict(N=len(rows),ie=ie,net=net.mean(),netf=netf.mean(),wr=win)

def main():
    m,H1,H4=prep()
    print("=== §17 HTF-ON vs HTF-OFF baseline (net-R price-cost; flat=0.24R conservative) ===")
    for fam in ["PBK_TREND","RECLAIM","RANGE_FADE","TGT_BREAK"]:
        on=evaluate(m,detect(m,H1,H4,fam,htf_on=True))
        off=evaluate(m,detect(m,H1,H4,fam,htf_on=False))
        print(f"\n-- {fam} --")
        summ(m,on ,f"{fam}.HTF_ON")
        summ(m,off,f"{fam}.HTF_OFF(no H4 filter)")

if __name__=="__main__":
    main()
