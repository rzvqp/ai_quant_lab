"""ALPHA-XAUUSD-PRICE-ONLY-BEARISH-SEQUENCE-001. Do ORDERED temporal price-event sequences discriminate
bearish departures where static features could not? Event alphabet -> ordered sequences (with window) ->
enrichment on DISCOVERY -> frozen test on CONFIRMATION -> common-prefix attribution. Price-only, DEV-only.
Outcome labels DIAGNOSTIC only. NO 2025+/N4/read_csv/V1/CALIB/exogenous."""
import sys, os, numpy as np, pandas as pd
from collections import Counter
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10; L=2
tfs,META=D.build()
def build_events(tf):
    x=tfs[tf]; o=x["open"].to_numpy();h=x["high"].to_numpy();l=x["low"].to_numpy();c=x["close"].to_numpy()
    atr=x["atr"].to_numpy();e20=x["ema20"].to_numpy();e50=x["ema50"].to_numpy();hh20=x["hh20"].to_numpy();ll20=x["ll20"].to_numpy()
    eff=x["effic"].to_numpy();ama=x["atr_ma"].to_numpy();dev=x["is_dev"].to_numpy();dt=pd.to_datetime(x["time"],unit="s",utc=True);n=len(o)
    is_sh=np.zeros(n,bool); is_sl=np.zeros(n,bool)
    for k in range(L,n-L):
        if h[k]==max(h[k-L:k+L+1]): is_sh[k]=True
        if l[k]==min(l[k-L:k+L+1]): is_sl[k]=True
    E={}
    def z(): return np.zeros(n,bool)
    E['HIGH_SWEEP']=z(); E['BEAR_DISP']=z(); E['BULL_DISP']=z(); E['BEAR_FOLLOW']=z(); E['STRUCT_BREAK_DOWN']=z()
    E['FAILED_RECLAIM_DOWN']=z(); E['LOWER_HIGH']=z(); E['REJECTION_FROM_HIGH']=z(); E['COMPRESSION']=z()
    E['EXPANSION_UP']=z(); E['EXPANSION_DOWN']=z(); E['TREND_UP']=z(); E['RANGE']=z(); E['FAILED_BREAKOUT_UP']=z()
    lastbreak=-99; broken_lvl=np.nan
    for i in range(L+5,n-1):
        if atr[i]!=atr[i]: continue
        # HIGH_SWEEP: first breach of a prior unbroken confirmed swing high
        for k in range(i-L-1,max(L,i-60),-1):
            if is_sh[k] and h[i]>h[k] and h[i-1]<=h[k] and (i-1<k+1 or max(h[k+1:i])<=h[k]): E['HIGH_SWEEP'][i]=True; break
        E['BEAR_DISP'][i]=(o[i]-c[i])>1.0*atr[i] and c[i]<o[i]
        E['BULL_DISP'][i]=(c[i]-o[i])>1.0*atr[i] and c[i]>o[i]
        E['BEAR_FOLLOW'][i]=((o[i-1]-c[i-1])>1.0*atr[i-1]) and c[i]<c[i-1]
        prelow=min(l[i-6:i]) if i>6 else l[i]
        E['STRUCT_BREAK_DOWN'][i]=c[i]<prelow and c[i]<o[i]
        if E['STRUCT_BREAK_DOWN'][i]: lastbreak=i; broken_lvl=prelow
        E['FAILED_RECLAIM_DOWN'][i]=(i-lastbreak)<=8 and np.isfinite(broken_lvl) and h[i]>=broken_lvl and c[i]<broken_lvl and c[i]<o[i]
        E['LOWER_HIGH'][i]=h[i-1]<h[i-2] and h[i-2]<h[i-3]
        E['REJECTION_FROM_HIGH'][i]=(h[i]-max(o[i],c[i]))>0.5*atr[i] and c[i]<o[i] and np.isfinite(hh20[i]) and h[i]>=hh20[i]*0.999
        E['COMPRESSION'][i]=np.isfinite(ama[i]) and atr[i-1]<0.8*ama[i]
        E['EXPANSION_UP'][i]=(c[i]-o[i])>1.0*atr[i]
        E['EXPANSION_DOWN'][i]=(o[i]-c[i])>1.0*atr[i]
        E['TREND_UP'][i]=e20[i]>e50[i]
        E['RANGE'][i]=eff[i]==eff[i] and abs(eff[i])<0.20
        E['FAILED_BREAKOUT_UP'][i]=np.isfinite(hh20[i]) and h[i]>hh20[i] and c[i]<hh20[i]
    # bearish label (forward 12 bars) + control; and split time
    H=12; lab=np.full(n,-1); bearpips=np.zeros(n)
    for i in range(L+5,n-H-1):
        if not dev[i] or atr[i]!=atr[i]: continue
        entry=o[i+1]; be=(entry-min(l[i+1:i+1+H]))/PIP; bu=(max(h[i+1:i+1+H])-entry)/PIP
        lab[i]=int(be>=150 and be>bu); bearpips[i]=be
    return dict(E=E,lab=lab,dev=dev,dt=dt,n=n,bearpips=bearpips)

def seq_complete(G, seq, window=12):
    """bars i where ordered sequence completes with last event at i, prior events in order within `window`."""
    E=G['E']; n=G['n']; out=np.zeros(n,bool)
    last=seq[-1]
    for i in range(20,n-1):
        if not E[last][i] or G['lab'][i]<0: continue
        # walk backward matching seq[:-1] in reverse order within window
        need=list(seq[:-1]); j=i-1; lo=i-window; ok=(len(need)==0)
        while need and j>=lo:
            if E[need[-1]][j]: need.pop()
            j-=1
        if not need: out[i]=True
    return out

def enrich(G, mask, split):
    dt=G['dt']; lab=G['lab']; cut=G['_cut']
    idx=np.where(mask)[0]
    d=[i for i in idx if dt[i]<cut and lab[i]>=0]; c=[i for i in idx if dt[i]>=cut and lab[i]>=0]
    baseD=G['_baseD']; baseC=G['_baseC']
    rd=np.mean([lab[i] for i in d]) if d else np.nan; rc=np.mean([lab[i] for i in c]) if c else np.nan
    return (len(d), round(float(rd),3), round(float(rd-baseD),3) if d else np.nan,
            len(c), round(float(rc),3), round(float(rc-baseC),3) if c else np.nan)

for tf in ("H4","H1"):
    G=build_events(tf)
    lab=G['lab']; dt=G['dt']; valid=[i for i in range(G['n']) if lab[i]>=0]
    cut=dt[valid[int(len(valid)*0.6)]]; G['_cut']=cut
    G['_baseD']=np.mean([lab[i] for i in valid if dt[i]<cut]); G['_baseC']=np.mean([lab[i] for i in valid if dt[i]>=cut])
    print(f"\n===== {tf}: base bearish-rate DISC={G['_baseD']:.3f} CONF={G['_baseC']:.3f} (cut {cut.date()}) =====")
    # PRIORITY SEQUENCES (§12-§17) + common-prefix attribution (§27)
    SEQS={
      "A sweep":["HIGH_SWEEP"],
      "A->B sweep+beardisp":["HIGH_SWEEP","BEAR_DISP"],
      "A->B->C sweep+disp+break":["HIGH_SWEEP","BEAR_DISP","STRUCT_BREAK_DOWN"],
      "A->B->C->D +failed_reclaim":["HIGH_SWEEP","BEAR_DISP","STRUCT_BREAK_DOWN","FAILED_RECLAIM_DOWN"],
      "A->B->C->D->E +2nd_disp":["HIGH_SWEEP","BEAR_DISP","STRUCT_BREAK_DOWN","FAILED_RECLAIM_DOWN","BEAR_DISP"],
      "FBC trendup+sweep+disp+break":["TREND_UP","HIGH_SWEEP","BEAR_DISP","STRUCT_BREAK_DOWN"],
      "failed_breakout+beardisp":["FAILED_BREAKOUT_UP","BEAR_DISP"],
      "failed_breakout+disp+break":["FAILED_BREAKOUT_UP","BEAR_DISP","STRUCT_BREAK_DOWN"],
      "exhaustion rej+lowerhigh+break":["REJECTION_FROM_HIGH","LOWER_HIGH","STRUCT_BREAK_DOWN"],
      "compression+expUP+expDOWN":["COMPRESSION","EXPANSION_UP","EXPANSION_DOWN"],
      "compression+expDOWN":["COMPRESSION","EXPANSION_DOWN"],
      "twostage disp+reclaim+disp":["BEAR_DISP","FAILED_RECLAIM_DOWN","BEAR_DISP"],
    }
    print(f"  evaluated {len(SEQS)} sequences (bounded, interpretable). fmt: DISC(n,rate,lift) | CONF(n,rate,lift)")
    for name,seq in SEQS.items():
        m=seq_complete(G,seq,window=12); r=enrich(G,m,None)
        flag = "  <== GENERALIZES" if (r[3] and r[5]==r[5] and r[2]==r[2] and r[2]>0.05 and r[5]>0.05 and r[3]>=15) else ""
        print(f"    {name:34s}: DISC(n{r[0]},{r[1]},{r[2]:+.3f}) | CONF(n{r[3]},{r[4]},{r[5]:+.3f}){flag}")
