"""chrono_checkpoint.py — CHRONOLOGICAL_MARKET_LEARNING quarterly checkpoints + FORWARD TEST (CEO mandate 2026-08-24).
Walk-forward discipline: for each quarter Q (in chronological order), form hypotheses using ONLY readings whose 2R:1R outcome
RESOLVED by the end of Q (no future leakage), then FORWARD-TEST the PREVIOUS quarter's frozen hypotheses on Q's readings. Hypotheses
are versioned; survival across multiple future quarters is tracked. NO retrospective editing. Outputs CHRONO_CHECKPOINTS.md (per-quarter
12-item checkpoint) + chrono_hypotheses.json (lineage). Cost STRESS 0.24 R for net expectancy; P2R is cost-free. null P2R=0.333."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
NULL=0.333; COST=0.24; HMAX=300; MIN_N=40; PROMISE=0.40
def qkey(y,mo): return f"{y}-Q{(mo-1)//3+1}"
def qnext(q):
    y,qq=int(q[:4]),int(q[-1]); return f"{y+1}-Q1" if qq==4 else f"{y}-Q{qq+1}"
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); n=len(m); yq=m["dt"].dt.year.to_numpy(); mq=m["dt"].dt.month.to_numpy()
    R=[json.loads(x) for x in open(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\reading_chrono.jsonl",encoding="utf-8")]
    # score each reading: bracket outcome + resolution quarter
    out=[]
    for r in R:
        T=r["T"]; ei=T+1; side=r["EXP_DIR"]; entry=r["ENTRY"]; inval=r["INVALIDATION"]; risk=abs(entry-inval)
        if risk<=0 or ei>=n-2: continue
        tgt=entry+2*risk*side
        seg_l=l[ei:ei+HMAX]; seg_h=h[ei:ei+HMAX]
        if side==1: fs=np.where(seg_l<=inval)[0]; ft=np.where(seg_h>=tgt)[0]
        else: fs=np.where(seg_h>=inval)[0]; ft=np.where(seg_l<=tgt)[0]
        fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
        if fstop==ftgt==10**9: continue
        res_off=min(fstop,ftgt); res_i=ei+int(res_off)
        Rr=2.0 if ftgt<fstop else -1.0
        q=dict(r); q["R"]=Rr; q["WIN"]=Rr>0; q["RES_Q"]=qkey(yq[res_i],mq[res_i]); out.append(q)
    quarters=sorted(set(r["QUARTER"] for r in out))
    def cells(rows,minn=MIN_N):
        from collections import defaultdict
        d=defaultdict(list)
        for r in rows: d[r["SIG"]].append(r)
        return {k:v for k,v in d.items() if len(v)>=minn}
    P2=lambda rows: (np.mean([r["WIN"] for r in rows]) if rows else float('nan'))
    NET=lambda rows: (np.mean([r["R"]-COST for r in rows]) if rows else float('nan'))
    lines=["# CHRONO_CHECKPOINTS — chronological market learning (walk-forward, forward-tested)\n",
           "Each quarter: hypotheses from readings RESOLVED by quarter-end (no leakage); previous quarter's hypotheses FORWARD-TESTED here.\n"]
    hyp_lineage={}  # sig -> list of (quarter_discovered, p2r, n)
    prev_hyps={}    # sig -> (p2r, n) frozen at previous checkpoint
    survival={}     # sig -> consecutive forward-quarters holding above base
    for q in quarters:
        inq=[r for r in out if r["QUARTER"]==q]
        # discovery uses only readings RESOLVED by end of q (RES_Q <= q)
        disc=[r for r in inq if r["RES_Q"]<=q]
        base=P2(disc); nb=len(disc)
        lines.append(f"\n## Checkpoint {q}  (frozen readings in-quarter={len(inq)}, resolved-by-Q={nb}, base P2R={base:.3f} net={NET(disc):+.3f})")
        # (11) regime behavior
        from collections import Counter,defaultdict
        reg=defaultdict(list)
        for r in disc: reg[r["N1_DIR"]].append(r)
        lines.append("  - regime P2R: "+" ".join(f"{k}={P2(v):.2f}(n{len(v)})" for k,v in sorted(reg.items(),key=lambda x:-len(x[1])) if len(v)>=15))
        # (1-3) morphologies + conditional prob; (4-5) BUY/SELL conditions
        cl=cells(disc,minn=max(20,MIN_N//2))
        buys=sorted([(k,len(v),P2(v)) for k,v in cl.items() if "BULLISH" in k],key=lambda x:-x[2])[:4]
        sells=sorted([(k,len(v),P2(v)) for k,v in cl.items() if "BEARISH" in k],key=lambda x:-x[2])[:4]
        lines.append("  - BUY cells (top): "+("; ".join(f"{k} P2R={p:.2f}(n{nn})" for k,nn,p in buys) if buys else "none n>=20"))
        lines.append("  - SELL cells (top): "+("; ".join(f"{k} P2R={p:.2f}(n{nn})" for k,nn,p in sells) if sells else "none n>=20"))
        # (10) promising hypotheses (this quarter) -> versioned
        newhyps={}
        for k,v in cl.items():
            if len(v)>=MIN_N and P2(v)>=PROMISE:
                newhyps[k]=(P2(v),len(v)); hyp_lineage.setdefault(k,[]).append((q,round(P2(v),3),len(v)))
        lines.append(f"  - promising hypotheses (P2R>={PROMISE}, n>={MIN_N}): "+("; ".join(f"{k}={p:.2f}(n{nn})_V[{q}]" for k,(p,nn) in newhyps.items()) if newhyps else "NONE"))
        # (9) failed ideas
        fails=[(k,len(v),P2(v)) for k,v in cl.items() if P2(v)<=NULL-0.03 and len(v)>=MIN_N]
        lines.append(f"  - failed cells (P2R<=~null, n>={MIN_N}): "+(f"{len(fails)} cells (e.g. "+", ".join(f'{k}={p:.2f}' for k,_,p in sorted(fails,key=lambda x:x[2])[:3])+")" if fails else "none"))
        # (8) readiness calibration proxy: P2R by N1_STRENGTH + near-zone (in-quarter)
        strong=[r for r in disc if r.get("N1_STRENGTH",0)>=1.0]; weak=[r for r in disc if r.get("N1_STRENGTH",0)<1.0]
        lines.append(f"  - readiness proxy: N1_strong P2R={P2(strong):.2f}(n{len(strong)}) vs N1_weak P2R={P2(weak):.2f}(n{len(weak)})")
        # (12) FORWARD TEST previous quarter's hypotheses on THIS quarter's readings
        if prev_hyps:
            ft=[]
            for k,(p_prev,n_prev) in prev_hyps.items():
                cur=[r for r in inq if r["SIG"]==k]
                if len(cur)>=15:
                    pf=P2(cur); held=pf>=base and pf>=NULL
                    survival[k]=survival.get(k,0)+ (1 if held else 0)
                    ft.append(f"{k}: prevP2R={p_prev:.2f}->fwdP2R={pf:.2f}(n{len(cur)}) {'HOLD' if held else 'DECAY'}")
                else:
                    ft.append(f"{k}: fwd n={len(cur)}(thin)")
            lines.append("  - FORWARD-TEST of previous checkpoint hyps: "+("; ".join(ft) if ft else "no testable"))
        else:
            lines.append("  - FORWARD-TEST: (no previous checkpoint)")
        prev_hyps=newhyps
    # survivors across multiple quarters
    lines.append("\n## Multi-quarter survival (forward-quarters a hypothesis held above base)")
    surv=sorted(survival.items(),key=lambda x:-x[1])
    for k,cntq in surv[:15]:
        lines.append(f"  {k}: held {cntq} forward-quarter(s); lineage {hyp_lineage.get(k,[])}")
    if not surv: lines.append("  (no hypotheses forward-tested yet / none held)")
    open(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\CHRONO_CHECKPOINTS.md","w",encoding="utf-8").write("\n".join(lines))
    json.dump({"lineage":hyp_lineage,"survival":survival},open(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\chrono_hypotheses.json","w"),indent=1)
    print(f"CHRONO-CHECKPOINT: quarters={len(quarters)} scored_readings={len(out)} hypotheses={len(hyp_lineage)} survivors_tracked={len(survival)}")
    print("  wrote CHRONO_CHECKPOINTS.md + chrono_hypotheses.json")
    print("  quarters:",quarters[:4],"...",quarters[-2:] if len(quarters)>4 else "")
    # brief: any hyp holding >=2 forward quarters?
    strong=[(k,v) for k,v in survival.items() if v>=2]
    print(f"  hypotheses holding >=2 forward quarters: {len(strong)}"+(": "+", ".join(f'{k}({v})' for k,v in strong[:6]) if strong else " (none)"))
if __name__=="__main__": main()
