"""htf_screen_A.py — ARCHITECTURE A: 4H EDGE -> 15m ENTRY/CONFIRMATION, at REAL costs. Pre-registered family set, FIXED governed params, scored
ONCE through the skepticism gate. Causal H4 context built HERE over full history (2011-2026) via completed-H4-bar asof (lookahead-free; the ratified
causal_bucket_asof pattern) because mstrat's precomputed h4_trend_up exists only from 2023. Entry = next-bar open. One active trade. Cost = real
round-turn (set COST_RT_USD from live-shadow). NO grid search, NO param invention. Skepticism gate: BASE>0, STRESS>0, >=2/3 eras positive,
drop-best-5%>0, N>=300, recent(2025-26)>=0, not outlier-carried."""
import os, sys, json, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); import mstrat as MS
# ---- COST (round-turn, price units). Placeholder until live-shadow confirmed; STRESS = 1.5x ----
COST_RT_USD = float(os.environ.get("COST_RT_USD", "0.50"))   # e.g. spread+commission+slippage round-turn in $ (gold price units)
STRESS_MULT = 1.5
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
V=d["volume"].to_numpy(float); ema20=d["m_ema20"].to_numpy(float); vwap=d["vwap"].to_numpy(float); sess=d["session"].to_numpy()
orh=d["or_high"].to_numpy(float); orl=d["or_low"].to_numpy(float); bis=d["bar_in_sess"].to_numpy(float)
psh=d["prev_sess_high"].to_numpy(float); psl=d["prev_sess_low"].to_numpy(float); pdh=d["pdh"].to_numpy(float); pdl=d["pdl"].to_numpy(float)
rmax20=d["rmax20"].to_numpy(float); rmin20=d["rmin20"].to_numpy(float); comp=d["compress"].to_numpy(float); disp=d["disp"].to_numpy(float)
mvol=d["m_volrank"].to_numpy(float); yr=pd.to_datetime(T,unit="s",utc=True).year.to_numpy()
# ---- causal H4 context (lookahead-free) ----
h4s=(T//14400)*14400
h4=pd.DataFrame({"h4s":h4s,"o":O,"h":H,"l":L,"c":C}).groupby("h4s").agg(o=("o","first"),h=("h","max"),l=("l","min"),c=("c","last")).reset_index()
h4["ema50"]=h4.c.ewm(span=50,adjust=False).mean(); h4["don_hi"]=h4.h.rolling(20).max().shift(1); h4["don_lo"]=h4.l.rolling(20).min().shift(1)
h4["atr"]=(h4.h-h4.l).rolling(14).mean(); h4["trend"]=(h4.c>h4.ema50).astype(int); h4["avail"]=h4.h4s+14400
m=pd.merge_asof(pd.DataFrame({"t":T}).sort_values("t"), h4[["avail","c","ema50","don_hi","don_lo","atr","trend"]].sort_values("avail"),
                left_on="t", right_on="avail", direction="backward")
H4T=m["trend"].to_numpy(); H4C=m["c"].to_numpy(); H4E=m["ema50"].to_numpy(); H4DH=m["don_hi"].to_numpy(); H4DL=m["don_lo"].to_numpy(); H4A=m["atr"].to_numpy()
h4up=(H4T==1); h4dn=(H4T==0); has_h4=np.isfinite(H4T)
print(f"causal H4 context defined on {100*np.isfinite(H4T).mean():.0f}% of bars (full history)")
# ---- simulator: one active trade, entry next open, cost round-turn, backstop bars ----
def sim(entries_long, entries_short, risk_arr, target_rr, cost, backstop=64, sess_exit=False):
    """entries_*: bool arrays (signal at bar i -> enter at open[i+1]). risk_arr: risk distance (price) per bar. target_rr: reward multiple."""
    trades=[]; open_until=-1
    sig=np.where(entries_long,1,np.where(entries_short,-1,0))
    for i in range(60,n-2):
        s=sig[i]
        if s==0 or i<=open_until: continue
        rk=risk_arr[i]
        if not (rk>0) or not np.isfinite(rk): continue
        ei=i+1; entry=O[ei]; risk=max(rk,2*cost,0.05); stop=entry-s*risk; tgt=entry+s*target_rr*risk
        end=min(ei+backstop,n-1); R=None; exit_i=end
        for k in range(ei,end+1):
            hs=(L[k]<=stop) if s>0 else (H[k]>=stop); ht=(H[k]>=tgt) if s>0 else (L[k]<=tgt)
            if hs and ht: R=-1.0; exit_i=k; break
            if hs: R=-1.0; exit_i=k; break
            if ht: R=float(target_rr); exit_i=k; break
            if sess_exit and sess[k]!=sess[ei]: R=s*(C[k]-entry)/risk; exit_i=k; break
        if R is None: R=s*(C[end]-entry)/risk; exit_i=end
        net=R-cost/risk
        trades.append(dict(i=int(i),dir=int(s),R=float(R),net=float(net),risk=float(risk),year=int(yr[i])))
        open_until=exit_i
    return pd.DataFrame(trades)
# ---- helpers ----
def cross_up(arr,i,lvl): return C[i-1]<=lvl and C[i]>lvl
brk_up=np.zeros(n,bool); brk_dn=np.zeros(n,bool)
# precompute simple breakout of prior-bar close vs level arrays handled inline per family
def lvlbreak(level, up=True):
    out=np.zeros(n,bool)
    for i in range(1,n):
        if not np.isfinite(level[i]): continue
        if up and C[i-1]<=level[i] and C[i]>level[i]: out[i]=True
        if (not up) and C[i-1]>=level[i] and C[i]<level[i]: out[i]=True
    return out
# ---- PRE-REGISTERED FAMILIES (fixed params) ----
A=1.0*ATR  # 1-ATR risk unit (default stop distance)
ny=(sess=="ny"); lon=(sess=="london"); afterOR=(bis>=4)  # OR = first 4 bars (1h); trade after
fam=[]
# A1 S5 baseline: NY OR-high breakout LONG, stop=or_low, target 3R (validated edge, reference)
s5l=ny&afterOR&lvlbreak(orh,True); s5risk=np.where((orh-orl)>0,orh-orl,np.nan)
fam.append(("A1_S5_NY_ORB_long_rr3", s5l, np.zeros(n,bool), s5risk, 3.0, True))
# A2 S5 + H4 trend filter (long only in H4 up)
fam.append(("A2_S5_ORB_H4up_rr3", s5l&h4up, np.zeros(n,bool), s5risk, 3.0, True))
# A3 Session ORB both sess + H4 aligned, stop=or opposite, rr2
orb_up=(ny|lon)&afterOR&lvlbreak(orh,True)&h4up; orb_dn=(ny|lon)&afterOR&lvlbreak(orl,False)&h4dn
fam.append(("A3_SessORB_H4aligned_rr2", orb_up, orb_dn, np.where((orh-orl)>0,orh-orl,np.nan), 2.0, True))
# A4 H4 trend + 15m Donchian20 breakout continuation, 1ATR stop, rr2
d4u=lvlbreak(rmax20,True)&h4up; d4d=lvlbreak(rmin20,False)&h4dn
fam.append(("A4_H4_15mDonch_rr2", d4u, d4d, A, 2.0, False))
# A5 H4 trend + 15m pullback to ema20 resumption, 1ATR stop, rr2
pbu=h4up&(L<=ema20)&(C>ema20)&(C>C-0); pbd=h4dn&(H>=ema20)&(C<ema20)
fam.append(("A5_H4_ema20pullback_rr2", pbu, pbd, A, 2.0, False))
# A6 H4 trend + prev-session H/L break, 1ATR, rr2
fam.append(("A6_H4_prevSessBreak_rr2", lvlbreak(psh,True)&h4up, lvlbreak(psl,False)&h4dn, A, 2.0, False))
# A7 compression -> displacement expansion in H4 direction, 1ATR, rr2
exu=(comp[np.maximum(np.arange(n)-1,0)]==1)&(disp==1)&(C>O)&h4up; exd=(comp[np.maximum(np.arange(n)-1,0)]==1)&(disp==1)&(C<O)&h4dn
fam.append(("A7_H4_compExpansion_rr2", exu, exd, A, 2.0, False))
# A8 VWAP reclaim in H4 direction, 1ATR, rr2
fam.append(("A8_H4_vwapReclaim_rr2", h4up&(L<=vwap)&(C>vwap), h4dn&(H>=vwap)&(C<vwap), A, 2.0, False))
# A9 PDH/PDL break H4 aligned, 1ATR, rr2
fam.append(("A9_H4_pdhpdlBreak_rr2", lvlbreak(pdh,True)&h4up, lvlbreak(pdl,False)&h4dn, A, 2.0, False))
# A10 H4 vol-expansion high + 15m displacement continuation, 1ATR, rr2
hv=mvol>=0.7
fam.append(("A10_H4volHi_disp_rr2", hv&(disp==1)&(C>O)&h4up, hv&(disp==1)&(C<O)&h4dn, A, 2.0, False))
# A11 CONTROL counter-trend: fade H4 extreme (H4 close far from ema50), rr2 — expected FAIL
far=np.abs(H4C-H4E)>1.5*np.where(H4A>0,H4A,np.nan)
fam.append(("A11_CONTROL_H4counter_rr2", far&h4dn&(C>O), far&h4up&(C<O), A, 2.0, False))
# ---- score ----
def metrics(TR,cost):
    if TR is None or len(TR)<50: return None
    r=TR.net.to_numpy(); N=len(r); wins=r[r>0]; los=r[r<=0]
    pf=wins.sum()/(abs(los.sum())+1e-9); eq=np.cumsum(r); dd=float((np.maximum.accumulate(eq)-eq).max())
    S=np.sort(r)[::-1]; k5=max(1,int(N*0.05)); db5=float((r.sum()-S[:k5].sum())/(N-k5))
    srt=TR.sort_values("i"); th=np.array_split(srt.net.to_numpy(),3); eras=[float(x.mean()) for x in th]; epos=sum(1 for x in th if x.mean()>0)
    rec=TR[TR.year>=2025].net; recm=float(rec.mean()) if len(rec)>=20 else np.nan
    return dict(N=N,tpy=round(N/15.05,0),WR=round(float((r>0).mean()),3),BASE=round(float(r.mean()),4),PF=round(pf,3),maxDD=round(dd,1),
                db5=round(db5,4),eras=[round(x,4) for x in eras],epos=epos,recent=round(recm,4) if np.isfinite(recm) else None,longpos=round(float(TR[TR.dir>0].net.mean()),4) if (TR.dir>0).any() else None)
rows=[]
for name,el,es,risk,rr,sx in fam:
    tb=sim(el,es,risk,rr,COST_RT_USD,sess_exit=sx); mb=metrics(tb,COST_RT_USD)
    ts=sim(el,es,risk,rr,COST_RT_USD*STRESS_MULT,sess_exit=sx); ms=metrics(ts,COST_RT_USD*STRESS_MULT)
    if mb is None: rows.append(dict(fam=name,N=0,note="thin")); continue
    stress=ms["BASE"] if ms else None
    survive = (mb["BASE"]>0) and (stress is not None and stress>0) and (mb["epos"]>=2) and (mb["db5"]>0) and (mb["N"]>=300) and (mb["recent"] is not None and mb["recent"]>=0)
    rows.append(dict(fam=name,**mb,STRESS=stress,SURVIVE=bool(survive)))
    if len(tb): tb.to_parquet(OUT+rf"\_htfA_{name}.parquet")
R=pd.DataFrame(rows); R.to_csv(OUT+r"\HTF_ARCH_A_SCREEN_RESULTS.csv",index=False)
pd.set_option("display.width",200,"display.max_columns",30)
print(f"\nCOST_RT_USD={COST_RT_USD} (stress x{STRESS_MULT})")
print(R.to_string(index=False))
surv=R[R.get("SURVIVE",False)==True] if "SURVIVE" in R else R.iloc[0:0]
print(f"\nSURVIVORS (profitable at real cost, gated): {list(surv.fam)}")
