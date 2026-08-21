"""ALPHA-XAUUSD-BEARISH-MOVE-MECHANISM-MINING-001. DIAGNOSTIC phase: mine the anatomy of large bearish
moves vs controls, find PRE-ENTRY discriminators, path anatomy. Outcome labels DIAGNOSTIC ONLY (never a
feature). Gated M5 -> causal H1/H4. DEV-only. NO 2025+/N4/read_csv/V1/holdout."""
import sys, os, numpy as np, pandas as pd
from collections import defaultdict, Counter
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10
tfs,META=D.build()
print(f"loader sha={META['data_file_sha256'][:16]}")

def anat(tf, H):
    x=tfs[tf]; o=x["open"].to_numpy();h=x["high"].to_numpy();l=x["low"].to_numpy();c=x["close"].to_numpy()
    atr=x["atr"].to_numpy();e20=x["ema20"].to_numpy();e50=x["ema50"].to_numpy();hh20=x["hh20"].to_numpy();ll20=x["ll20"].to_numpy()
    hh50=x["hh50"].to_numpy();ll50=x["ll50"].to_numpy();eff=x["effic"].to_numpy();ama=x["atr_ma"].to_numpy()
    dev=x["is_dev"].to_numpy();yr=pd.to_datetime(x["time"],unit="s",utc=True).dt.year.to_numpy();n=len(o)
    rows=[]
    for i in range(55,n-H-1):
        if atr[i]!=atr[i] or not dev[i]: continue
        entry=o[i+1]; fh=h[i+1:i+1+H]; fl=l[i+1:i+1+H]
        bear=(entry-fl.min())/PIP; bull=(fh.max()-entry)/PIP
        # adverse path before the low: max high up to the bar of the min low (causal-outcome, DIAGNOSTIC)
        jlow=i+1+int(np.argmin(fl)); adv=(max(h[i+1:jlow+1])-entry)/PIP if jlow>=i+1 else 0
        reg=("TREND_UP" if (e20[i]>e50[i] and eff[i]==eff[i] and eff[i]>0.30) else ("TREND_DOWN" if (e20[i]<e50[i] and eff[i]<-0.30) else ("RANGE" if (eff[i]==eff[i] and abs(eff[i])<0.20) else "TRANSITION_OTHER")))
        # PRE-MOVE CAUSAL FEATURES (known at bar i)
        w=hh50[i]-ll50[i]
        feats=dict(
            rangepos = (c[i]-ll50[i])/w if w>0 else np.nan,          # 1=at range high
            dist_hh20_atr = (hh20[i]-c[i])/atr[i] if np.isfinite(hh20[i]) else np.nan,  # small=near recent high
            above_hh20 = float(np.isfinite(hh20[i]) and c[i]>hh20[i]),
            eff = eff[i],
            trend_up = float(e20[i]>e50[i]),
            atr_ratio = atr[i]/ama[i] if np.isfinite(ama[i]) and ama[i]>0 else np.nan,
            ext_ema20_atr = (c[i]-e20[i])/atr[i],                    # overextension above ema20
            consec_up = sum(1 for q in range(i,max(i-6,0),-1) if c[q]>c[q-1]),
            lower_high = float(h[i-1]<h[i-2] and h[i-2]<h[i-3]),
            bear_disp = float((o[i]-c[i])>1.0*atr[i]),
            bull_disp = float((c[i]-o[i])>1.0*atr[i]),
            upper_wick_atr = (h[i]-max(o[i],c[i]))/atr[i],           # rejection wick
            failed_new_high = float(h[i]>hh20[i] and c[i]<hh20[i]) if np.isfinite(hh20[i]) else 0.0,
        )
        rows.append(dict(i=i,yr=int(yr[i]),reg=reg,bear=bear,bull=bull,adv=adv,is_bear=(bear>=150 and bear>bull),**feats))
    return rows

for tf,H in (("H4",12),("H1",24)):
    R=anat(tf,H); nb=sum(r['is_bear'] for r in R)
    print(f"\n===== {tf} (forward {H} bars) — BEARISH-MOVE CATALOG (>=150p & bear>bull) =====")
    print(f"  total bars={len(R)} | bearish-move starts={nb} ({nb/len(R)*100:.1f}%)")
    for thr in (80,100,150,200,300,500):
        cnt=sum(1 for r in R if r['bear']>=thr and r['bear']>r['bull'])
        print(f"    net-bearish >= {thr}p: {cnt}")
    bg=[r for r in R if r['is_bear']]; cg=[r for r in R if not r['is_bear']]
    print(f"  REGIME of bearish-move starts: {dict(Counter(r['reg'] for r in bg))}")
    print(f"  REGIME of controls:            {dict(Counter(r['reg'] for r in cg))}")
    # PATH ANATOMY (S11): adverse excursion before the decline
    adv_b=np.array([r['adv'] for r in bg]); print(f"  PATH: adverse excursion before low (bearish grp) — median={np.median(adv_b):.0f}p P25={np.percentile(adv_b,25):.0f} P75={np.percentile(adv_b,75):.0f} | %adv<=30p={np.mean(adv_b<=30)*100:.0f}% <=50p={np.mean(adv_b<=50)*100:.0f}%")
    # FEATURE DISCRIMINATION (standardized mean diff bearish vs control) — S23.D
    feats=[k for k in bg[0] if k not in ("i","yr","reg","bear","bull","adv","is_bear")]
    print(f"  FEATURE DISCRIMINATION (bearish mean | control mean | std-diff), ranked:")
    disc=[]
    for f in feats:
        vb=np.array([r[f] for r in bg],float); vc=np.array([r[f] for r in cg],float)
        vb=vb[np.isfinite(vb)]; vc=vc[np.isfinite(vc)]
        if len(vb)<5 or len(vc)<5: continue
        sd=(vb.mean()-vc.mean())/(np.sqrt((vb.std()**2+vc.std()**2)/2)+1e-9)
        disc.append((f,vb.mean(),vc.mean(),sd))
    for f,mb,mc,sd in sorted(disc,key=lambda z:-abs(z[3])):
        print(f"    {f:18s}: {mb:+.3f} | {mc:+.3f} | std-diff {sd:+.3f}")
