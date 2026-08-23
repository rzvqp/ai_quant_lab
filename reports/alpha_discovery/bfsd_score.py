"""bfsd_score.py — BLIND_FORWARD_STRUCTURE_DISCOVERY_V1 POST-REPLAY OUTCOME SCORER (walled off from discovery).
Runs ONLY after bfsd_engine.py has frozen all predictions. Reads predictions.jsonl + candles, computes for each FROZEN setup:
MFE/MAE (in R), target-before-stop ordering (P reach +2R before -1R stop; also +1R,+3R), time-to-resolution, realized dir.
NO prediction is altered. Then clusters by MORPH, estimates conditional probabilities, checks ERA-stability, and does the §11
incremental-baseline ladder (H4-only random entry -> +H1 pullback -> +M15 zone reaction = the setups) using a nested-EMA H4 proxy.
DISCOVERY summary ONLY: a promising cluster becomes a PREREGISTERED hypothesis for mechanize + full quant-falsification (§12/§13);
it is NOT a validated edge. Analytic driftless null for a 2R-target/1R-stop bracket = 1/3.  Data: cur_data M15."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
H=192  # forward horizon to resolve a 2R:1R bracket (post-replay only)
def ema(x,span): return pd.Series(x).ewm(span=span,adjust=False).mean().to_numpy()
def bracket(entry,inval,side,seg_h,seg_l):
    risk=abs(entry-inval)
    if risk<=0: return None
    if side==1:
        mfe=(np.max(seg_h)-entry)/risk; mae=(entry-np.min(seg_l))/risk
        ti=np.where(seg_l<=inval)[0]; t1=np.where(seg_h>=entry+risk)[0]; t2=np.where(seg_h>=entry+2*risk)[0]; t3=np.where(seg_h>=entry+3*risk)[0]
    else:
        mfe=(entry-np.min(seg_l))/risk; mae=(np.max(seg_h)-entry)/risk
        ti=np.where(seg_h>=inval)[0]; t1=np.where(seg_l<=entry-risk)[0]; t2=np.where(seg_l<=entry-2*risk)[0]; t3=np.where(seg_l<=entry-3*risk)[0]
    fi=ti[0] if len(ti) else 10**9; f1=t1[0] if len(t1) else 10**9; f2=t2[0] if len(t2) else 10**9; f3=t3[0] if len(t3) else 10**9
    return dict(mfe=mfe,mae=mae,w1=f1<fi,w2=f2<fi,w3=f3<fi,ttr=int(min(f2,fi)) if min(f2,fi)<10**9 else -1)
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    preds=[json.loads(x) for x in open(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\predictions.jsonl",encoding="utf-8")]
    out=[]
    for p in preds:
        T=p["T"]; side=p["EXP_DIR"]; entry=p["ENTRY"]; inval=p["INVAL"]
        seg_h=h[T+1:T+1+H]; seg_l=l[T+1:T+1+H]
        if len(seg_h)<20: continue
        b=bracket(entry,inval,side,seg_h,seg_l)
        if b is None: continue
        q=dict(p); q.update(b); out.append(q)
    N=len(out)
    def rate(rows,k): return (np.mean([r[k] for r in rows]) if rows else float('nan'))
    print(f"BFSD-SCORE: scored {N} frozen setups (of {len(preds)}). Analytic driftless null: P2R=0.333, P1R=0.500.")
    print(f"OVERALL: P1R={rate(out,'w1'):.3f} P2R={rate(out,'w2'):.3f} P3R={rate(out,'w3'):.3f} MFE_med={np.median([r['mfe'] for r in out]):.2f} MAE_med={np.median([r['mae'] for r in out]):.2f}")
    # by side
    for s,nm in [(1,"LONG"),(-1,"SHORT")]:
        rr=[r for r in out if r["EXP_DIR"]==s]
        print(f"  {nm}: n={len(rr)} P2R={rate(rr,'w2'):.3f} P1R={rate(rr,'w1'):.3f} MFE={np.median([r['mfe'] for r in rr]):.2f} MAE={np.median([r['mae'] for r in rr]):.2f}")
    # era stability overall
    print("ERA stability (P2R): "+" ".join(f"{e}={rate([r for r in out if r['ERA']==e],'w2'):.3f}(n{sum(1 for r in out if r['ERA']==e)})" for e in ["D","C","O"]))
    # clusters by MORPH
    from collections import defaultdict
    cl=defaultdict(list)
    for r in out: cl[r["MORPH"]].append(r)
    print("\nMORPH clusters n>=20 by P2R (P2R | P1R | per-era P2R | MFE/MAE):")
    rows=[]
    for k,v in cl.items():
        if len(v)<20: continue
        rows.append((k,len(v),rate(v,'w2'),rate(v,'w1'),
                     {e:(rate([r for r in v if r['ERA']==e],'w2'),sum(1 for r in v if r['ERA']==e)) for e in ["D","C","O"]},
                     np.median([r['mfe'] for r in v]),np.median([r['mae'] for r in v])))
    for k,nn,p2,p1,era,mfe,mae in sorted(rows,key=lambda x:-x[2]):
        es=" ".join(f"{e}={era[e][0]:.2f}(n{era[e][1]})" if era[e][1]>=8 else f"{e}=--" for e in ["D","C","O"])
        print(f"  {k:44s} n={nn:3d} P2R={p2:.2f} P1R={p1:.2f} | {es} | MFE{mfe:.2f}/MAE{mae:.2f}")
    # coarse cluster by (H4trend|zone|side)
    print("\nCOARSE (side|zone) with per-era P2R:")
    cz=defaultdict(list)
    for r in out: cz[(r["SIDE"],r["ZONE"])].append(r)
    for k,v in sorted(cz.items(),key=lambda x:-len(x[1])):
        if len(v)<15: continue
        es=" ".join(f"{e}={rate([r for r in v if r['ERA']==e],'w2'):.2f}" if sum(1 for r in v if r['ERA']==e)>=8 else f"{e}=--" for e in ["D","C","O"])
        print(f"  {str(k):22s} n={len(v):3d} P2R={rate(v,'w2'):.2f} | {es}")
    # §11 incremental baseline ladder (nested-EMA H4 proxy; 2R:1R bracket, risk=1ATR)
    e20=m["ema20"].to_numpy(); e50=m["ema50"].to_numpy(); e320=ema(c,320); e800=ema(c,800)
    h4up=e320>e800; h4dn=~h4up
    rng=np.random.default_rng(20260823)
    def base_rate(mask,side,k=4000):
        idx=np.where(mask)[0]; idx=idx[(idx>800)&(idx<n-H-1)]
        if len(idx)==0: return float('nan'),0
        pick=rng.choice(idx,size=min(k,len(idx)),replace=False); w=0;tot=0
        for i in pick:
            if not np.isfinite(atr[i]) or atr[i]<=0: continue
            risk=atr[i]; entry=c[i]; inval=entry-side*risk
            b=bracket(entry,inval,side,h[i+1:i+1+H],l[i+1:i+1+H])
            if b: w+=b['w2']; tot+=1
        return (w/tot if tot else float('nan')),tot
    bl_long,nl=base_rate(h4up,1); bl_short,ns=base_rate(h4dn,-1)
    print("\n§11 INCREMENTAL BASELINE LADDER (P2R, 2R:1R, risk=1ATR):")
    print(f"  H4-context-only random entry: LONG(H4up)={bl_long:.3f}(n{nl}) SHORT(H4dn)={bl_short:.3f}(n{ns})  [analytic null 0.333]")
    setL=[r for r in out if r['EXP_DIR']==1]; setS=[r for r in out if r['EXP_DIR']==-1]
    print(f"  H4+H1pullback+M15 zone reaction (frozen setups): LONG={rate(setL,'w2'):.3f}(n{len(setL)}) SHORT={rate(setS,'w2'):.3f}(n{len(setS)})")
    print(f"  INCREMENTAL: LONG {rate(setL,'w2')-bl_long:+.3f} | SHORT {rate(setS,'w2')-bl_short:+.3f}  (positive => zone/structure adds info over H4-context-only)")
    print("\nDISCOVERY ONLY — no edge claimed. Clusters with era-stable P2R materially above baseline become PREREGISTERED hypotheses for §12 mechanize + §13 full quant-falsification.")
if __name__=="__main__": main()
