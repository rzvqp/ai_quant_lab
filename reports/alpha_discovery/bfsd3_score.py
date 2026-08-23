"""bfsd3_score.py — SECONDARY stage (post-reading): score the frozen top-down READING ledger, CALIBRATE entry-readiness against
outcomes, and let MORPHOLOGY EMERGE by clustering the frozen canonical signatures (NOT imposed). Outcomes touched ONLY here.
For each frozen record: P(reach +2R before invalidation) within K bars, +1R, MFE/MAE, TTR. Readiness calibration = P(win) by
readiness bin (is the top-down readiness score predictive?). Emergent morphology = cluster by canonical SIG, conditional P(win)
by N1 regime (regime specialists valid; per-era n for transparency, stability NOT required). Baseline = overall + analytic null
0.333 (2R:1R). DISCOVERY ONLY -> preregister -> mechanize -> full quant gate (§12/§13). Reads reading_ledger.jsonl."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
K=192
def score_one(entry,inval,side,seg_h,seg_l):
    risk=abs(entry-inval)
    if risk<=0 or len(seg_h)<10: return None
    if side==1:
        mfe=(np.max(seg_h)-entry)/risk; mae=(entry-np.min(seg_l))/risk
        ti=np.where(seg_l<=inval)[0]; t1=np.where(seg_h>=entry+risk)[0]; t2=np.where(seg_h>=entry+2*risk)[0]
    else:
        mfe=(entry-np.min(seg_l))/risk; mae=(np.max(seg_h)-entry)/risk
        ti=np.where(seg_h>=inval)[0]; t1=np.where(seg_l<=entry-risk)[0]; t2=np.where(seg_l<=entry-2*risk)[0]
    fi=ti[0] if len(ti) else 10**9; f1=t1[0] if len(t1) else 10**9; f2=t2[0] if len(t2) else 10**9
    return dict(mfe=mfe,mae=mae,w1=f1<fi,w2=f2<fi,ttr=int(min(f2,fi)) if min(f2,fi)<10**9 else -1)
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    P=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\reading_ledger.jsonl"
    recs=[json.loads(x) for x in open(P,encoding="utf-8")]
    out=[]
    for r in recs:
        T=r["T"]; s=r["EXP_DIR"]
        sc=score_one(r["ENTRY"],r["INVALIDATION"],s,h[T+1:T+1+K],l[T+1:T+1+K])
        if sc: q=dict(r); q.update(sc); out.append(q)
    N=len(out); rate=lambda rows,k:(np.mean([x[k] for x in rows]) if rows else float('nan'))
    print(f"BFSD3-SCORE: scored {N}/{len(recs)} frozen reading records. Null P2R=0.333, P1R=0.5.")
    print(f"OVERALL: P2R={rate(out,'w2'):.3f} P1R={rate(out,'w1'):.3f} MFE_med={np.median([x['mfe'] for x in out]):.2f} MAE_med={np.median([x['mae'] for x in out]):.2f}")
    for s,nm in [(1,"BUY"),(-1,"SELL")]:
        rr=[x for x in out if x["EXP_DIR"]==s]
        if rr: print(f"  {nm}: n={len(rr)} P2R={rate(rr,'w2'):.3f} P1R={rate(rr,'w1'):.3f}")
    # ---- readiness calibration (is the top-down readiness score predictive?) ----
    print("\nREADINESS CALIBRATION (P2R by ENTRY_READINESS bin):")
    for lo,hi in [(50,60),(60,70),(70,80),(80,101)]:
        rr=[x for x in out if lo<=x["ENTRY_READINESS"]<hi]
        if len(rr)>=25: print(f"  readiness[{lo},{hi}): n={len(rr):4d} P2R={rate(rr,'w2'):.3f} P1R={rate(rr,'w1'):.3f}")
        else: print(f"  readiness[{lo},{hi}): n={len(rr)} (thin)")
    # ---- emergent morphology: cluster by canonical SIG, conditional P2R by N1 regime ----
    from collections import defaultdict
    cl=defaultdict(list)
    for x in out: cl[x["SIG"]].append(x)
    base=rate(out,'w2')
    print(f"\nEMERGENT MORPHOLOGY (cluster by canonical SIG, n>=25), ranked by |P2R-base| (base={base:.3f}):")
    rows=[]
    for k,v in cl.items():
        if len(v)<25: continue
        ec={e:sum(1 for x in v if x["ERA"]==e) for e in ["D","C","O"]}
        rows.append((k,len(v),rate(v,'w2'),rate(v,'w2')-base,ec))
    for k,nn,p,d,ec in sorted(rows,key=lambda x:-abs(x[3]))[:20]:
        print(f"  {k:52s} n={nn:4d} P2R={p:.3f} d={d:+.3f} era(D{ec['D']}/C{ec['C']}/O{ec['O']})")
    print("\nDISCOVERY ONLY. A SIG cluster (regime specialist) with material d + adequate n across >=50-100 obs -> PREREGISTER ->")
    print("mechanize -> full quant-falsification. Readiness is calibrated ONLY here (post-outcome), never during the reading walk.")
if __name__=="__main__": main()
