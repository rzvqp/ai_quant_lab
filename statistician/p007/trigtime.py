"""AT_TRIGGER-ONLY features: what a classifier could actually know at the moment the break happens."""
import sys, os, csv, json
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
RM=r"C:\Users\MEDION GAMING\ai_quant_lab-research-main"; T=r"C:\Users\MEDION~1\AppData\Local\Temp\p7"
FIX=os.path.join(RM,"ai_trader","csv_causal_replay","fixtures","data","Q4_SEALED_1_5932.csv")
raw=list(csv.reader(open(FIX)))[1:]
ts=np.array([int(float(r[0])) for r in raw]); o=np.array([float(r[1]) for r in raw])
hi=np.array([float(r[2]) for r in raw]); lo=np.array([float(r[3]) for r in raw])
cl=np.array([float(r[4]) for r in raw]); vol=np.array([float(r[5]) for r in raw])
G=pd.read_csv(os.path.join(T,"q4_episodes.csv"))
rows=[]
for _,r in G.iterrows():
    tb=int(r.trigger)
    w=slice(max(0,tb-96),tb)                       # trailing 24h, strictly BEFORE the trigger bar
    tr=np.maximum(hi[w]-lo[w], np.abs(hi[w]-np.roll(cl[w],1)))
    atr=float(np.nanmean(tr[1:])) if len(tr)>2 else np.nan
    vb=float(vol[w].mean()); rng=float(hi[tb]-lo[tb])
    rows.append(dict(id=r.id,label=r.label,
        t_break_atr=float((cl[tb-1]-cl[tb])/atr) if atr and atr>0 else np.nan,
        t_bar_range_atr=float(rng/atr) if atr and atr>0 else np.nan,
        t_body_frac=float(abs(cl[tb]-o[tb])/rng) if rng>1e-9 else np.nan,
        t_vol_rel=float(vol[tb]/vb) if vb>0 else np.nan,
        t_vol_rel_3=float(vol[max(0,tb-2):tb+1].mean()/vb) if vb>0 else np.nan,
        t_fresh_low_24h=float(lo[tb]<lo[w].min()),
        t_dist_from_high24=float((hi[w].max()-cl[tb])/atr) if atr and atr>0 else np.nan))
X=pd.DataFrame(rows)
print("="*100); print("  AT_TRIGGER-ONLY SEPARATION (nothing after the trigger bar is used)"); print("="*100)
print(f"  episodes {len(X)}  ({X.label.value_counts().to_dict()})\n")
def auc(a,b):
    a=np.asarray(a); b=np.asarray(b)
    comb=np.concatenate([a,b]); rk=pd.Series(comb).rank().to_numpy()
    U=rk[:len(a)].sum()-len(a)*(len(a)+1)/2
    return U/(len(a)*len(b))
res={}
for nm in [c for c in X.columns if c.startswith("t_")]:
    a=X.loc[X.label=="SUPPORT",nm].dropna(); b=X.loc[X.label=="REJECTED",nm].dropna()
    if len(a)<5 or len(b)<5: continue
    v=auc(a,b); res[nm]=v
    print(f"    {nm:18} SUPPORT med {np.median(a):8.3f}   REJECTED med {np.median(b):8.3f}   AUC {v:.3f}  |dev| {abs(v-0.5):.3f}")
best=max(res.items(), key=lambda kv: abs(kv[1]-0.5))
print(f"\n  best AT_TRIGGER separator : {best[0]}  AUC {best[1]:.3f}  (|deviation from 0.5| = {abs(best[1]-0.5):.3f})")
print(f"  compare with RESOLUTION-time quantities: duration AUC 0.931 - decline 0.908 - vol_isolation 0.917")
print(f"                                          fresh_extreme 0.862 - round_trip 0.309 (=0.691 inverted)")
X.to_csv(os.path.join(T,"q4_trigger_features.csv"),index=False)
json.dump({k:float(v) for k,v in res.items()}, open(os.path.join(T,"trig.json"),"w"), indent=1)
