import numpy as np, pandas as pd, time, sys
from collections import Counter
import alpha_lab as A, s1, run_mtf
from alpha_lab import bh_fdr
from campaign import full_stats
run_mtf.M = s1                      # point frozen campaign helpers at the S1 engine
st=run_mtf.statistician; wf=run_mtf.walk_forward; rt=run_mtf.red_team; met=run_mtf.metrics

if __name__=="__main__":
    print("loading S1 data (M15 + context + sweep/FVG primitives)...")
    d=s1.load_s1(); n=len(d); a=int(n*0.6); b=int(n*0.8)
    res=d.iloc[:a].copy(); val=d.iloc[a:b].copy()   # holdout d.iloc[b:] SEALED, untouched
    nonhold=d.iloc[:b].copy()
    hyps=s1.generate(None); Q=A.CFG['FDR_Q']
    print(f"S1 grammar: {len(hyps)} valid combinations  | M15 bars={n}  research={a} val={b-a} holdout(SEALED)={n-b}")
    t0=time.time(); reg=[]
    for h in hyps:
        v=st(res,val,h); v['h']=h; reg.append(v)
    N=len(reg); deaths={}
    for v in reg:
        if not v['passed']: deaths[v['stage']]=deaths.get(v['stage'],0)+1
    statpass=[v for v in reg if v['passed']]
    pvec=np.array([v['p'] for v in reg]); keep=bh_fdr(pvec,Q)
    fdr=[reg[i] for i in range(N) if keep[i] and reg[i]['passed']]
    wfs=[v for v in fdr if wf(nonhold,v['h'])]
    cands=[]
    for v in wfs:
        ok,att=rt(res,v['h'])
        if ok: v['att']=att; cands.append(v)
    dt=time.time()-t0

    print(f"\n===== S1 FAMILY — DISCOVERY REPORT (holdout SEALED) =====")
    print(f"hypotheses generated: {N}")
    print(f"eliminated per stage: {dict(sorted(deaths.items(),key=lambda x:-x[1]))}")
    print(f"passed Statistician(expectancy+PF+maxDD+param+OOS): {len(statpass)}")
    print(f"passed GLOBAL FDR: {len(fdr)} | walk-forward: {len(wfs)} | Red Team -> CANDIDATES: {len(cands)}")
    print(f"throughput {N/dt*3600:,.0f} hyp/hr ({dt:.0f}s)")

    # primitive frequency among most-promising (Statistician-passers) vs base rate
    prims=['side','liq_ref','confirm','imb','entry','stop','exit','window','liq_lb']
    print("\n--- primitive frequency in PROMISING hypotheses (Statistician-passers) vs base rate ---")
    if statpass:
        for p in prims:
            base=Counter(str(v['h'].get(p)) for v in reg)
            prom=Counter(str(v['h'].get(p)) for v in statpass)
            tot_b=sum(base.values()); tot_p=sum(prom.values())
            rows=[]
            for val_ in sorted(prom, key=lambda x:-prom[x]):
                br=base[val_]/tot_b; pr=prom[val_]/tot_p; rows.append(f"{val_}={pr:.2f}(x{pr/br:.1f})")
            print(f"  {p:8s}: "+"  ".join(rows[:6]))
    else:
        print("  (no Statistician-passers)")

    # top promising by p
    statpass.sort(key=lambda v:v['p'])
    print("\n--- top 8 promising hypotheses by significance p (research) ---")
    for v in statpass[:8]:
        h=v['h']; m=v['m']
        print(f"  p={v['p']:.2e} exp={m['exp']:.3f}R pf={m['pf']:.2f} n={m['n']} | side={h['side']} liq={h['liq_ref']} conf={h['confirm']} imb={h['imb']} entry={h['entry']} stop={h['stop']} exit={h['exit']}")

    print("\n--- S candidates (survived global FDR + walk-forward + Red Team) ---")
    if not cands: print("  NONE")
    for i,v in enumerate(cands,1):
        h=v['h']; stt=full_stats(s1.backtest(res,h))
        print(f"  S1.{i} [{h['id']}] side={h['side']} liq={h['liq_ref']} conf={h['confirm']} imb={h['imb']} entry={h['entry']} stop={h['stop']} exit={h['exit']} win={h['window']}")
        print(f"       n={stt['n']} win_rate={stt['win_rate']:.3f} exp={stt['expectancy_R']:.3f}R PF={stt['profit_factor']:.2f} maxDD={stt['max_dd_R']:.1f}R longestLoss={stt['longest_losing_streak']} RedTeam={v['att']}")

    print("\n===== VERDICT =====")
    if cands: print(f"S1 CONTAINS a statistical edge: {len(cands)} candidate(s) survived Expectancy->PF->OOS->global-FDR->walk-forward->Red Team. Holdout NOT opened (CEO gate).")
    else: print("S1 does NOT contain a robust statistical edge: hypotheses were eliminated before surviving global multiple-testing + walk-forward + Red Team. (Holdout untouched.)")
