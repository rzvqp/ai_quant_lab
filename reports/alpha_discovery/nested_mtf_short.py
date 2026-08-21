"""ALPHA-XAUUSD-NESTED-MTF-SHORT-001. CROSS-TIMEFRAME CONDITIONAL SEQUENCES:
H4 context (state) -> H1 structural event -> M15 trigger -> [M5 optional]. Completed-bar causality
(HTF aligned by close_time <= trigger close_time, enforced H4.close<=H1evt.close<=M15.close). Directional
lift FIRST (common-parent attribution: parent -> +H1 -> +M15), discovery/confirmation split, matched controls.
Price-only, DEV-only. NO 2025+/CALIB/V1/N4/read_csv/exogenous. Outcome labels DIAGNOSTIC only."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10; L=2; H_M15=48   # forward horizon = 48 M15 bars (12h, == H4 12-bar horizon)
tfs,META=D.build()

def swings(h,l,L=2):
    n=len(h); sh=np.zeros(n,bool); sl=np.zeros(n,bool)
    for k in range(L,n-L):
        if h[k]==max(h[k-L:k+L+1]): sh[k]=True
        if l[k]==min(l[k-L:k+L+1]): sl[k]=True
    return sh,sl

def tf_pack(tf):
    x=tfs[tf]; d=dict(
        o=x["open"].to_numpy(),h=x["high"].to_numpy(),l=x["low"].to_numpy(),c=x["close"].to_numpy(),
        atr=x["atr"].to_numpy(),e20=x["ema20"].to_numpy(),e50=x["ema50"].to_numpy(),
        hh20=x["hh20"].to_numpy(),ll20=x["ll20"].to_numpy(),hh50=x["hh50"].to_numpy(),ll50=x["ll50"].to_numpy(),
        eff=x["effic"].to_numpy(),ama=x["atr_ma"].to_numpy(),
        ct=x["close_time"].to_numpy().astype("int64"),ot=x["time"].to_numpy().astype("int64"),
        dt=pd.to_datetime(x["time"],unit="s",utc=True),dev=x["is_dev"].to_numpy())
    d["reg"]=x["regime"].to_numpy() if "regime" in x else np.array(["NA"]*len(d["o"]),dtype=object)
    d["n"]=len(d["o"]); d["sh"],d["sl"]=swings(d["h"],d["l"],L); return d

H4=tf_pack("H4"); H1=tf_pack("H1"); M15=tf_pack("M15")

# ---------- H4 PARENT CONTEXTS (states on the H4 bar) ----------
def h4_ctx(P):
    o,h,l,c,atr,e20,e50,eff,ama,hh20,hh50,ll50,reg=(P[k] for k in
        ("o","h","l","c","atr","e20","e50","eff","ama","hh20","hh50","ll50","reg"))
    n=P["n"]; w=hh50-ll50; rangepos=np.where(w>0,(c-ll50)/w,0.5)
    ctx={}
    ctx["BULLISH_STATE"]=(e20>e50)
    ctx["UPPER_RANGE"]=(rangepos>0.75)
    ctx["SWINGHIGH_INTERACT"]=np.isfinite(hh20)&(h>=hh20*0.999)
    ctx["OVEREXT_UP"]=((c-e20)/atr>1.0)
    ctx["FAILED_CONT"]=(e20>e50)&(c<o)&((o-c)>0.5*atr)
    ctx["COMPRESSION"]=np.isfinite(ama)&(atr<0.8*ama)
    ctx["EXPANSION"]=np.isfinite(ama)&(atr>1.3*ama)
    ctx["TREND_UP"]=(reg=="TREND_UP"); ctx["RANGE"]=(reg=="RANGE"); ctx["TRANSITION"]=(reg=="TRANSITION")
    ctx["ANY"]=np.ones(n,bool)
    return ctx

# ---------- H1 / M15 EVENT ALPHABET (bearish structural events) ----------
def bear_events(P):
    o,h,l,c,atr,ama,hh20,ll20,sh=(P[k] for k in ("o","h","l","c","atr","ama","hh20","ll20","sh"))
    n=P["n"]; E={}; z=lambda:np.zeros(n,bool)
    for k in ("HIGH_SWEEP","FAILED_HH","BEAR_DISP","STRUCT_BREAK","FAILED_BULL_CONT","CLOSE_BELOW_LEVEL",
              "LOWER_HIGH","FAILED_RECLAIM","SECOND_BEAR","BREAK_RETEST","REJECT_RECOVERY","MICRO_BREAKDOWN",
              "COMPR_EXP_DOWN","FAILED_BULL_IMP","ANY"): E[k]=z()
    lastbreak=-99; brk=np.nan
    for i in range(L+6,n-1):
        if atr[i]!=atr[i]: continue
        E["ANY"][i]=True
        # high sweep: first breach of a prior unbroken confirmed swing high
        for k in range(i-L-1,max(L,i-60),-1):
            if sh[k] and h[i]>h[k] and h[i-1]<=h[k] and (i-1<k+1 or max(h[k+1:i])<=h[k]): E["HIGH_SWEEP"][i]=True; break
        E["FAILED_HH"][i]=np.isfinite(hh20[i]) and h[i]>hh20[i] and c[i]<hh20[i]        # failed breakout up
        E["BEAR_DISP"][i]=(o[i]-c[i])>1.0*atr[i] and c[i]<o[i]
        prelow=min(l[i-6:i]); E["STRUCT_BREAK"][i]=c[i]<prelow and c[i]<o[i]
        if E["STRUCT_BREAK"][i]: lastbreak=i; brk=prelow
        E["FAILED_BULL_CONT"][i]=((c[i-1]-o[i-1])>1.0*atr[i-1]) and c[i]<c[i-1] and c[i]<o[i]   # prior bull disp, this fails
        E["CLOSE_BELOW_LEVEL"][i]=np.isfinite(ll20[i]) and c[i]<ll20[i] and c[i]<o[i]
        E["LOWER_HIGH"][i]=h[i-1]<h[i-2] and h[i-2]<h[i-3]
        E["FAILED_RECLAIM"][i]=(i-lastbreak)<=8 and np.isfinite(brk) and h[i]>=brk and c[i]<brk and c[i]<o[i]
        E["SECOND_BEAR"][i]=E["BEAR_DISP"][i] and any(((o[j]-c[j])>1.0*atr[j] and c[j]<o[j]) for j in range(max(L+6,i-8),i))
        E["BREAK_RETEST"][i]=E["FAILED_RECLAIM"][i]   # break then retest fails == failed reclaim family
        E["REJECT_RECOVERY"][i]=(h[i]-max(o[i],c[i]))>0.5*atr[i] and c[i]<o[i] and c[i-1]>o[i-1]  # rejection after an up bar
        E["MICRO_BREAKDOWN"][i]=np.isfinite(ll20[i]) and l[i]<ll20[i] and c[i]<ll20[i]
        E["COMPR_EXP_DOWN"][i]=np.isfinite(ama[i]) and atr[i-1]<0.8*ama[i] and (o[i]-c[i])>1.0*atr[i] and c[i]<o[i]
        E["FAILED_BULL_IMP"][i]=((c[i-1]-o[i-1])>0.8*atr[i-1]) and c[i]<o[i] and c[i]<c[i-1]
    return E

H1E=bear_events(H1); M15E=bear_events(M15); H4C=h4_ctx(H4)

# ---------- label on M15 (forward H_M15 bars) ----------
def m15_label():
    o,h,l=M15["o"],M15["h"],M15["l"]; dev=M15["dev"]; atr=M15["atr"]; n=M15["n"]
    lab=np.full(n,-1)
    for i in range(L+6,n-H_M15-1):
        if not dev[i] or atr[i]!=atr[i]: continue
        entry=o[i+1]; be=(entry-min(l[i+1:i+1+H_M15]))/PIP; bu=(max(h[i+1:i+1+H_M15])-entry)/PIP
        lab[i]=int(be>=150 and be>bu)
    return lab
LAB=m15_label()

# ---------- completed-bar causal alignment (H1/H4 by close_time) ----------
m15_ct=M15["ct"]; h1_ct=H1["ct"]; h4_ct=H4["ct"]
idx_h1=np.searchsorted(h1_ct,m15_ct,side="right")-1     # latest completed H1 at each M15 trigger close
idx_h4=np.searchsorted(h4_ct,m15_ct,side="right")-1     # latest completed H4
# CAUSALITY ASSERTIONS (S10): aligned HTF bars must be COMPLETED at/before the M15 trigger close
ok=(idx_h1>=0)&(idx_h4>=0)
assert (h1_ct[idx_h1[ok]]<=m15_ct[ok]).all(), "H1 partial-bar leak"
assert (h4_ct[idx_h4[ok]]<=m15_ct[ok]).all(), "H4 partial-bar leak"
# H1 event within trailing window of W_H1 completed H1 bars
def h1_recent(evt, W=6):
    """boolean per M15 bar: required H1 event present in the last W completed H1 bars (<= trigger)."""
    ev=H1E[evt]; out=np.zeros(M15["n"],bool)
    # rolling any over last W H1 bars, indexed by H1 bar
    csum=np.concatenate([[0],np.cumsum(ev.astype(int))])
    for i in range(M15["n"]):
        k=idx_h1[i]
        if k<0: continue
        lo=max(0,k-W+1); out[i]=(csum[k+1]-csum[lo])>0
    return out

VALID=np.where(LAB>=0)[0]
cut_i=VALID[int(len(VALID)*0.6)]; CUT=M15["ct"][cut_i]
disc=VALID[M15["ct"][VALID]<CUT]; conf=VALID[M15["ct"][VALID]>=CUT]
BASE_D=LAB[disc].mean(); BASE_C=LAB[conf].mean()
print(f"M15 valid={len(VALID)} | DISC n={len(disc)} base={BASE_D:.3f} | CONF n={len(conf)} base={BASE_C:.3f} (cut {pd.to_datetime(CUT,unit='s',utc=True).date()}) H_M15={H_M15}")

def rate(mask_idx):
    m=[i for i in mask_idx if LAB[i]>=0]
    return (len(m), float(np.mean([LAB[i] for i in m])) if m else np.nan)

def attrib(name, h4ctx, h1evt, m15evt, W=6):
    """common-parent attribution on DISC and CONF: parent -> +H1 -> +M15, same population."""
    parent=H4C[h4ctx][idx_h4] & (idx_h4>=0) & (idx_h1>=0)
    h1m=parent & h1_recent(h1evt,W)
    fullm=h1m & M15E[m15evt]
    out={}
    for tag,sub in (("D",disc),("C",conf)):
        base=BASE_D if tag=="D" else BASE_C
        subset=set(sub.tolist())
        pi=[i for i in np.where(parent)[0] if i in subset]
        hi=[i for i in np.where(h1m)[0] if i in subset]
        fi=[i for i in np.where(fullm)[0] if i in subset]
        np_,rp=rate(pi); nh,rh=rate(hi); nf,rf=rate(fi)
        out[tag]=(np_,rp,nh,rh,nf,rf,base)
    return out

# ---------- curated nested hierarchies (mechanisms, not grids) ----------
HIER=[
 # id, H4 context, H1 event, M15 event   (themes S13/S14/S15/S16)
 ("N1 failbull",      "BULLISH_STATE","FAILED_BULL_CONT","FAILED_RECLAIM"),
 ("N2 failbull-LH",   "BULLISH_STATE","FAILED_HH","LOWER_HIGH"),
 ("N3 upper-failHH",  "UPPER_RANGE","FAILED_HH","FAILED_RECLAIM"),
 ("N4 swinghi-sweep", "SWINGHIGH_INTERACT","HIGH_SWEEP","FAILED_RECLAIM"),
 ("N5 swinghi-break", "SWINGHIGH_INTERACT","STRUCT_BREAK","FAILED_RECLAIM"),
 ("N6 overext-disp",  "OVEREXT_UP","BEAR_DISP","LOWER_HIGH"),
 ("N7 failcont-break","FAILED_CONT","STRUCT_BREAK","MICRO_BREAKDOWN"),
 ("N8 twostage",      "BULLISH_STATE","SECOND_BEAR","SECOND_BEAR"),
 ("N9 compr-hier",    "COMPRESSION","BEAR_DISP","COMPR_EXP_DOWN"),
 ("N10 trans-break",  "TRANSITION","STRUCT_BREAK","FAILED_RECLAIM"),
 ("N11 range-sweep",  "RANGE","HIGH_SWEEP","MICRO_BREAKDOWN"),
 ("N12 upper-closebl","UPPER_RANGE","CLOSE_BELOW_LEVEL","BEAR_DISP"),
]
print("\n=== COMMON-PARENT ATTRIBUTION (directional lift over base; incr over prior layer) ===")
print("fmt: PARENT(n,lift) -> +H1(n,lift,incr) -> +M15(n,lift,incr)   [DISC || CONF]")
surv=[]
for hid,h4c,h1e,m15e in HIER:
    a=attrib(hid,h4c,h1e,m15e)
    D_=a["D"]; C_=a["C"]
    def fmt(t):
        np_,rp,nh,rh,nf,rf,base=t
        lp=rp-base if np_ else np.nan; lh=rh-base if nh else np.nan; lf=rf-base if nf else np.nan
        ih=(rh-rp) if (nh and np_) else np.nan; imf=(rf-rh) if (nf and nh) else np.nan
        return f"P(n{np_},{lp:+.3f})->H1(n{nh},{lh:+.3f},i{ih:+.3f})->M15(n{nf},{lf:+.3f},i{imf:+.3f})"
    # survivor: full-seq CONF lift>0 AND full CONF > parent CONF AND M15 incr>0 on BOTH splits, nf>=15
    nfD,rfD=D_[4],D_[5]; nfC,rfC=C_[4],C_[5]; rpC=C_[1]; rhD=D_[3]; rhC=C_[3]
    gen = (nfC>=15 and rfC-C_[6]>0 and rfC>rpC and (rfD-rhD)>0 and (rfC-rhC)>0)
    flag="  <== GENERALIZES" if gen else ""
    print(f"  {hid:20s} DISC {fmt(D_)}\n  {'':20s} CONF {fmt(C_)}{flag}")
    if gen: surv.append((hid,h4c,h1e,m15e))
print(f"\nDirectional survivors: {len(surv)} -> {[s[0] for s in surv]}")
np.save(os.path.join(SP,"_nested_surv.npy"),np.array(surv,dtype=object),allow_pickle=True)
