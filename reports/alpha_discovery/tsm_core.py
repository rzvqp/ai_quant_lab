"""tsm_core.py — TEMPORAL_SEQUENCE_MINING_V1 core engine.

Question: does the ORDER/TRAJECTORY of pre-decision XAU states carry ex-ante DIRECTIONAL information beyond the final (current) state?
All features causal (info <= anchor t). Outcome (triple-barrier) computed ONLY after groups are frozen. cur_data M15 UTC.

Design pillars:
 - CURRENT-STATE vocabulary (the baseline conditioning the mandate says path must beat): range_pos, vol_state, htf_align, session,
   anchor direction, dist-from-structure. Same kind of static features Factory V2 falsified as standalone discriminators.
 - PATH-MOTIF vocabulary (order-sensitive, NOT reducible to final state): efficiency, whipsaw(sign-changes), FIRST-half vs SECOND-half
   return (pure ORDER), energy-timing (late-vs-early |move|), extreme-location-in-time, pullback depth, recross count.
 - Triple-barrier outcome: +b*ATR_t up / -b*ATR_t down within H bars -> {+1 up-first, -1 down-first, 0 unresolved}. MFE/MAE/time in R.
 - Positive control: a FUTURE-return motif that MUST separate (proves the pipeline has power); causal motifs are the real test.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cur_data as CD

COST = 0.24  # STRESS round-trip R

def load_panel():
    """Load M15 and compute the causal per-bar feature panel (all shifted where needed to be knowable AT bar i)."""
    m = CD.load_m15().reset_index(drop=True)
    o=m["open"].to_numpy(float); h=m["high"].to_numpy(float); l=m["low"].to_numpy(float); c=m["close"].to_numpy(float)
    atr=m["atr"].to_numpy(float); atr_ma=m["atr_ma"].to_numpy(float)
    dt=m["dt"]; yr=dt.dt.year.to_numpy(); hr=dt.dt.hour.to_numpy(); n=len(m)
    logret=np.zeros(n); logret[1:]=np.log(c[1:]/c[:-1])
    S=pd.Series
    ema80  = S(c).ewm(span=80, adjust=False).mean().to_numpy()    # ~H1 trend proxy
    ema320 = S(c).ewm(span=320,adjust=False).mean().to_numpy()    # ~H4 trend proxy
    ema20=m["ema20"].to_numpy(float); ema50=m["ema50"].to_numpy(float)
    # range position within rolling-20 (causal, includes i)
    hh20=S(h).rolling(20).max().to_numpy(); ll20=S(l).rolling(20).min().to_numpy()
    rng=np.where((hh20-ll20)>1e-9, (c-ll20)/(hh20-ll20), 0.5)
    # compression: fast/slow atr
    atr_fast=S(pd.Series(np.r_[np.nan,np.abs(np.diff(c))]).fillna(0)).rolling(10).mean().to_numpy()
    tr = np.maximum.reduce([h-l, np.abs(h-np.r_[c[0],c[:-1]]), np.abs(l-np.r_[c[0],c[:-1]])])
    atr10=S(tr).rolling(10).mean().to_numpy(); atr50=S(tr).rolling(50).mean().to_numpy()
    comp=np.where(atr50>1e-9, atr10/atr50, 1.0)
    body=np.abs(c-o); barrng=np.where((h-l)>1e-9,h-l,1e-9); body_frac=body/barrng
    updir=np.sign(c-o)
    # HTF align: +1 if ema80>ema320 (up), -1 if <, using slope-of-longer as trend
    htf=np.where(ema80>ema320,1,-1)
    # prior-20 swing extremes (for structure distance / breaks), knowable at i (shift 1)
    p20H=S(h).rolling(20).max().shift(1).to_numpy(); p20L=S(l).rolling(20).min().shift(1).to_numpy()
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    def sess(i):
        H_=hr[i]; return "AS" if H_<8 else ("LN" if H_<13 else ("NY" if H_<20 else "LT"))
    return dict(m=m,o=o,h=h,l=l,c=c,atr=atr,atr_ma=atr_ma,dt=dt,yr=yr,hr=hr,n=n,logret=logret,
                ema20=ema20,ema50=ema50,ema80=ema80,ema320=ema320,rng=rng,comp=comp,body_frac=body_frac,
                updir=updir,htf=htf,p20H=p20H,p20L=p20L,tr=tr,era=era,sess=sess)

# ---------- triple-barrier outcome (causal; computed only on demand) ----------
def triple_barrier(P, idx, b=1.5, H=32):
    """From anchor close at idx: up=+b*ATR_idx, down=-b*ATR_idx, horizon H bars. Return dict per anchor."""
    h=P["h"]; l=P["l"]; c=P["c"]; atr=P["atr"]; n=P["n"]
    out=[]
    for t in idx:
        a=atr[t]
        if not np.isfinite(a) or a<=0 or t+1>=n: out.append((0,np.nan,np.nan,np.nan)); continue
        up=c[t]+b*a; dn=c[t]-b*a; end=min(t+H, n-1)
        lab=0; ttr=np.nan; mfe=-1e9; mae=1e9
        for j in range(t+1, end+1):
            mfe=max(mfe,(h[j]-c[t])/a); mae=min(mae,(l[j]-c[t])/a)
            hu=h[j]>=up; hd=l[j]<=dn
            if hu and hd: lab=0; ttr=j-t; break     # ambiguous same-bar -> unresolved (conservative)
            if hu: lab=1; ttr=j-t; break
            if hd: lab=-1; ttr=j-t; break
        out.append((lab, ttr, mfe if mfe>-1e8 else np.nan, mae if mae<1e8 else np.nan))
    return np.array([r[0] for r in out]), np.array([r[1] for r in out],float), \
           np.array([r[2] for r in out],float), np.array([r[3] for r in out],float)

# ---------- path-motif extraction over L bars ending at anchor t (bars t-L+1..t, all <= t) ----------
def path_features(P, idx, L):
    c=P["c"]; logret=P["logret"]; atr=P["atr"]; h=P["h"]; l=P["l"]; n=P["n"]
    rows=[]
    for t in idx:
        s=t-L
        if s<1: rows.append(None); continue
        seg=logret[s+1:t+1]                       # L returns into t
        cc=c[s:t+1]                               # L+1 closes
        a=atr[t] if (np.isfinite(atr[t]) and atr[t]>0) else np.nan
        net=np.log(c[t]/c[s]); plen=np.sum(np.abs(seg))+1e-12
        eff=abs(net)/plen                          # directness 0..1
        sc=int(np.sum(np.sign(seg[1:])!=np.sign(seg[:-1])))  # sign changes (whipsaw)
        half=L//2
        fh=np.log(c[t-half]/c[s]); sh=np.log(c[t]/c[t-half]) # first vs second half (ORDER)
        fabs=np.sum(np.abs(seg[:half])); sabs=np.sum(np.abs(seg[half:]))
        energy_late=(sabs-fabs)/(sabs+fabs+1e-12)  # +1 = energy back-loaded (late), -1 = front-loaded (early)
        # extreme location in time (pure order feature): where within window did the high/low occur (0=old,1=recent)
        argH=(np.argmax(cc))/L; argL=(np.argmin(cc))/L
        # dominant move + pullback depth: if net>0 use max drawdown after the window-low before t; symmetric
        run=cc-cc[0]
        if net>=0:
            peak=np.maximum.accumulate(cc); dd=(peak-cc); pull=np.max(dd)/(a if a else 1)   # deepest retrace in ATR
        else:
            trough=np.minimum.accumulate(cc); du=(cc-trough); pull=np.max(du)/(a if a else 1)
        # recross of window midprice (path complexity)
        mid=(np.max(cc)+np.min(cc))/2; rc=int(np.sum((cc[:-1]-mid)*(cc[1:]-mid)<0))
        rows.append(dict(net_atr=net/ (a/c[t] if a else 1e-9) if a else np.nan,
                         net=net, eff=eff, sc=sc, fh=fh, sh=sh, energy_late=energy_late,
                         argH=argH, argL=argL, pull=pull, rc=rc,
                         net_r=(c[t]-c[s])/a if a else np.nan))
    return rows

# ---------- episode dedup: collapse anchors whose horizons overlap into independent episodes ----------
def independent_episodes(idx, H):
    """Greedy: walk sorted anchors, start a new episode when the next anchor is > H bars past the last episode start."""
    idx=np.sort(np.asarray(idx)); keep=[]; last=-10**9
    for t in idx:
        if t-last> H: keep.append(t); last=t
    return np.array(keep)

if __name__=="__main__":
    P=load_panel(); n=P["n"]
    print(f"panel rows={n} span={P['dt'].min()}..{P['dt'].max()}")
    # smoke: label distribution + positive-control power on a generic anchor (every 4th bar, warmup)
    warm=400; idx=np.arange(warm, n-64, 4)
    lab,ttr,mfe,mae=triple_barrier(P, idx[:20000], b=1.5, H=32)
    res=lab[lab!=0]
    print(f"anchors={len(idx[:20000])} resolved={len(res)} up_first_frac={np.mean(res>0):.4f} unresolved={np.mean(lab[:20000]==0):.4f}")
    ie=independent_episodes(idx[:20000], 32)
    print(f"independent_episodes(H=32)={len(ie)} (raw anchors {len(idx[:20000])})")
