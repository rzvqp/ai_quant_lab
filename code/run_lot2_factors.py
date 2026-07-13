import numpy as np, pandas as pd, json, time
import mstrat as MS, run_lot
d=MS.load(); n=len(d); a=int(n*0.6); b=int(n*0.8)
res=d.iloc[:a].copy(); val=d.iloc[a:b].copy()
# ---- LOT 2 pipeline ----
run_lot.run_lot(['S6','S7','S8','S9','S10'],"LOT 2 (S6-S10)")
# ---- FACTOR ANALYSIS over all 10 families: best hyp per family + monthly R series ----
print("\n\n===== ALPHA-FACTOR ANALYSIS (S1-S10) =====")
fams=['S1','S2','S3','S4','S5','S6','S7','S8','S9','S10']
best={}; series={}
for fam in fams:
    hs=MS.REGISTRY[fam][0](); pick=None
    for h in hs:
        v=run_lot.statistician(res,val,h); m=v['m']
        if m['n']>=MS.CFG['MINTR'] and m['exp']>0:
            score=v['p'] if v['passed'] else 1.0
            key=(0 if v['passed'] else 1, score, -m['exp'])
            if pick is None or key<pick[0]: pick=(key,h,v)
    best[fam]=pick
    if pick:
        h=pick[1]; tr=MS.backtest(res,h)
        mon=pd.to_datetime(res['time'].values[tr['ei'].astype(int).values],unit='s').to_period('M')
        series[fam]=pd.Series(tr['R'].values).groupby(mon).sum()
# correlation matrix of monthly R across families with signal
sig_fams=[f for f in fams if f in series]
if len(sig_fams)>=2:
    M=pd.DataFrame({f:series[f] for f in sig_fams}).fillna(0.0)
    corr=M.corr()
    print("\nmonthly-R correlation between family factors (research):")
    print(corr.round(2).to_string())
else: corr=pd.DataFrame()
# ALPHA_REGISTRY
reg=[]
for fam in fams:
    p=best[fam]
    if not p: reg.append(dict(alpha_id=f"A_{fam}",family_id=fam,econ=MS.ECON[fam],status="PROVISIONAL NO SIGNAL",n=0)); continue
    h=p[1]; v=p[2]; m=v['m']; stt_tr=MS.backtest(res,h)
    dirs=set(s['dir'] for s in MS.setups(res,h)); side='both' if len(dirs)>1 else ('long' if 1 in dirs else 'short')
    nov=1.0
    if fam in sig_fams and len(sig_fams)>1: nov=float(1-corr.loc[fam,[x for x in sig_fams if x!=fam]].abs().max())
    reg.append(dict(alpha_id=f"A_{fam}",family_id=fam,econ=MS.ECON[fam],
        primitives={k:val for k,val in h.items() if k not in('id','family')},
        side=side,expectancy=round(m['exp'],3),pf=round(m['pf'],2),dd=round(m['dd'],1),
        n=m['n'],p=f"{v['p']:.2e}",passed_stat=v['passed'],
        novelty=round(nov,2),status="PROVISIONAL NO CANDIDATE" if not v['passed'] else "PROVISIONAL SUB-FDR"))
# write registry files
with open("ALPHA_REGISTRY.md","w",encoding="utf-8") as f:
    f.write("# ALPHA_REGISTRY (provisional, holdout SEALED)\n\nUnit = alpha FACTOR (economic mechanism). Portfolio objective = max expectancy at min inter-factor correlation.\n\n")
    f.write("| alpha_id | family | economic_hypothesis | side | exp(R) | PF | maxDD | n | p | passed_stat | novelty | status |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n")
    for r in reg:
        f.write(f"| {r['alpha_id']} | {r['family_id']} | {r['econ']} | {r.get('side','-')} | {r.get('expectancy','-')} | {r.get('pf','-')} | {r.get('dd','-')} | {r['n']} | {r.get('p','-')} | {r.get('passed_stat','-')} | {r.get('novelty','-')} | {r['status']} |\n")
    f.write("\n## Inter-factor monthly-R correlation (research)\n\n```\n"+(corr.round(2).to_string() if not corr.empty else "n/a")+"\n```\n")
print("\n--- ALPHA_REGISTRY (S1-S10) ---")
for r in reg: print(f"  {r['alpha_id']} [{r['econ']}] exp={r.get('expectancy','-')}R n={r['n']} p={r.get('p','-')} nov={r.get('novelty','-')} -> {r['status']}")
json.dump({'lots_done':['LOT1','LOT2'],'families_done':fams,'holdout':'SEALED','next':'S11-S20 Lots 3-4'},open("PROJECT_STATE_v1.0.json","w"),indent=1)
print("\nwrote ALPHA_REGISTRY.md, PROJECT_STATE_v1.0.json")
