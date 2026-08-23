"""bfsd4_score.py — SECONDARY clustering/scoring for BROADENED Batch-2 (reading_ledger_b2.jsonl). Batch-1 stays FROZEN and is NOT
touched or pooled here (no retuning on Batch-1). Outcomes computed ONLY here. Clusters by TRIGGER (observed structural event) and by
full SIG, conditional by N1 regime (regime specialists valid). Emergent structural morphology = TRIGGER×context cells materially above
base at adequate n on OUT-OF-SAMPLE data. DISCOVERY ONLY."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
K=192
def score_one(entry,inval,side,seg_h,seg_l):
    risk=abs(entry-inval)
    if risk<=0 or len(seg_h)<10: return None
    if side==1:
        ti=np.where(seg_l<=inval)[0]; t1=np.where(seg_h>=entry+risk)[0]; t2=np.where(seg_h>=entry+2*risk)[0]
        mfe=(np.max(seg_h)-entry)/risk; mae=(entry-np.min(seg_l))/risk
    else:
        ti=np.where(seg_h>=inval)[0]; t1=np.where(seg_l<=entry-risk)[0]; t2=np.where(seg_l<=entry-2*risk)[0]
        mfe=(entry-np.min(seg_l))/risk; mae=(np.max(seg_h)-entry)/risk
    fi=ti[0] if len(ti) else 10**9; f1=t1[0] if len(t1) else 10**9; f2=t2[0] if len(t2) else 10**9
    return dict(mfe=mfe,mae=mae,w1=f1<fi,w2=f2<fi)
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); n=len(m)
    P=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\reading_ledger_b2.jsonl"
    recs=[json.loads(x) for x in open(P,encoding="utf-8")]
    seen=set(); dd=[]
    for r in recs:
        if r["T"] in seen: continue
        seen.add(r["T"]); dd.append(r)
    print(f"BFSD4 Batch-2 (OUT-OF-SAMPLE, Batch-1 frozen/untouched): {len(recs)} raw -> {len(dd)} unique")
    out=[]
    for r in dd:
        T=r["T"]; sc=score_one(r["ENTRY"],r["INVALIDATION"],r["EXP_DIR"],h[T+1:T+1+K],l[T+1:T+1+K])
        if sc: q=dict(r); q.update(sc); out.append(q)
    rate=lambda rows,k:(np.mean([x[k] for x in rows]) if rows else float('nan'))
    base=rate(out,'w2')
    print(f"scored {len(out)}. OVERALL P2R={base:.3f} (null 0.333) P1R={rate(out,'w1'):.3f}")
    for s,nm in [(1,"BUY"),(-1,"SELL")]:
        rr=[x for x in out if x["EXP_DIR"]==s]
        if rr: print(f"  {nm}: n={len(rr)} P2R={rate(rr,'w2'):.3f}")
    from collections import defaultdict
    # by TRIGGER (the broadened observation)
    print("\nBy observed TRIGGER (structural event), n>=30:")
    tg=defaultdict(list)
    for x in out: tg[x["TRIGGER"]].append(x)
    for k,v in sorted(tg.items(),key=lambda x:-rate(x[1],'w2')):
        if len(v)<30: continue
        print(f"  {k:10s} n={len(v):4d} P2R={rate(v,'w2'):.3f} d={rate(v,'w2')-base:+.3f}")
    # TRIGGER x regime (bias) x near-zone
    print("\nEMERGENT SIG clusters (bias|N1dir|trigger|zone|session), n>=25, by |d|:")
    cl=defaultdict(list)
    for x in out: cl[x["SIG"]].append(x)
    rows=[]
    for k,v in cl.items():
        if len(v)<25: continue
        ec={e:sum(1 for x in v if x["ERA"]==e) for e in ["D","C","O"]}
        rows.append((k,len(v),rate(v,'w2'),rate(v,'w2')-base,ec))
    for k,nn,p,d,ec in sorted(rows,key=lambda x:-abs(x[3]))[:20]:
        print(f"  {k:44s} n={nn:4d} P2R={p:.3f} d={d:+.3f} era(D{ec['D']}/C{ec['C']}/O{ec['O']})")
    print("\nDISCOVERY ONLY (out-of-sample). A TRIGGER×regime cell materially above base at n>=100 -> preregister -> mechanize -> falsify.")
if __name__=="__main__": main()
