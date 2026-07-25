"""STOP-FLOOR (D2) DIAGNOSTIC — measurement only. No matched-null, no holdout, no parquet change.
Instrumented faithful replica of mstrat.simulate (lines 44-74) that records, per EXECUTED trade:
requested risk (pre-floor), min_exec, which floor component was active, whether it was widened, and R.
Replica R is verified == MS.simulate R to 1e-12. Runs on the research segment (same basis as
FAMILY_RESULTS, re-verified). Reports the 5 requested measurements; draws no conclusion."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fr = pd.read_parquet(os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet"))
netinv = pd.read_parquet(os.path.join(ROOT, "results", "matched_null_validation", "net_concentration_inventory.parquet"))
net1 = dict(zip(netinv['id'], netinv['net1']))
idmap = {}
for fam in MS.REGISTRY:
    for h in MS.REGISTRY[fam][0](): idmap[h['id']] = h
TICK = MS.TICK; CFG = MS.CFG
C_SPREAD = 2*CFG['spread_ticks']*TICK   # 0.2
C_TICK   = 5*TICK                        # 0.5

d = MS.load(); n = len(d); a = int(n*0.6); res = d.iloc[:a].copy()   # research; holdout never loaded

def instr_simulate(d, setups, cfg=CFG):
    """Exact copy of mstrat.simulate loop + per-trade instrumentation."""
    o=d['open'].values;hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;atr=d['m_atr'].values
    nn=len(d); cost=(cfg['spread_ticks']+cfg['slip_ticks'])*TICK
    rec=[]; last=-1
    for s in sorted(setups,key=lambda x:x['ei']):
        ei=s['ei']; si=s['si']
        if ei<=last or ei>=nn-1 or ei<1: continue
        dirn=s['dir']; entry=o[ei]; stop=s['stop']; risk=abs(entry-stop)
        if not np.isfinite(risk) or np.isnan(atr[si]) or atr[si]<=0: continue
        c_atr=0.10*atr[si]
        min_exec=max(C_SPREAD, C_TICK, c_atr)
        req_risk=risk; widened=False
        if risk<min_exec: risk=min_exec; stop=entry-dirn*risk; widened=True
        if risk<=0: continue
        # active component of min_exec
        comp = 'atr' if c_atr>=C_TICK and c_atr>=C_SPREAD else ('tick' if C_TICK>=C_SPREAD else 'spread')
        ek=s['exit_kind']; ep=s.get('exit_param'); trail=(ek=='trailing')
        to=int(ep) if ek=='time' else 48
        if ek=='rr': tgt=entry+dirn*ep*risk
        elif ek in ('opp_liq','opp_struct'): tgt=ep
        else: tgt=None
        best=entry; ex=None; xi=None
        for j in range(ei,min(ei+to,nn)):
            if trail:
                best=max(best,hi[j]) if dirn>0 else min(best,lo[j]); ts=best-dirn*1.5*atr[si]
                stop=max(stop,ts) if dirn>0 else min(stop,ts)
            if dirn>0:
                if lo[j]<=stop: ex=stop;xi=j;break
                if tgt is not None and np.isfinite(tgt) and hi[j]>=tgt: ex=tgt;xi=j;break
            else:
                if hi[j]>=stop: ex=stop;xi=j;break
                if tgt is not None and np.isfinite(tgt) and lo[j]<=tgt: ex=tgt;xi=j;break
        if ex is None: xi=min(ei+to,nn-1); ex=cl[xi]
        R=(dirn*(ex-entry)-2*cost)/risk
        rec.append(dict(ei=ei, R=R, req_risk=req_risk, min_exec=min_exec, widened=widened,
                        comp=comp, req_over_floor=req_risk/min_exec, atr_si=atr[si]))
        last=xi
    return pd.DataFrame(rec)

hp = fr[fr.hist_prof].copy()
rows=[]; maxdiff=0.0; all_widened_ratio=[]; comp_counts={'atr':0,'tick':0,'spread':0}
best_widened_count=0
for _, r in hp.iterrows():
    hid=r['id']; h=idmap[hid]
    t=instr_simulate(res, MS.setups(res,h))
    ref=MS.simulate(res, MS.setups(res,h))
    maxdiff=max(maxdiff, float(np.abs(np.sort(t['R'].values)-np.sort(ref['R'].values)).max()) if len(t) else 0.0)
    nT=len(t); nw=int(t['widened'].sum())
    wtr=t[t['widened']]
    best_i=int(t['R'].idxmax()); best_widened=bool(t.loc[best_i,'widened'])
    if best_widened: best_widened_count+=1
    if nw>0:
        all_widened_ratio.extend(wtr['req_over_floor'].tolist())
        for c in comp_counts: comp_counts[c]+=int((wtr['comp']==c).sum())
    rows.append(dict(id=hid, fam=r['fam'], n=nT, n_widened=nw, pct_widened=nw/nT if nT else np.nan,
                     best_widened=best_widened, net1=net1.get(hid,np.nan), fragile=bool(r['fragile'])))
m=pd.DataFrame(rows)
print(f"=== BASIS: replica R vs MS.simulate max|diff| over 357 = {maxdiff:.2e}  (n match {int((m['n']==hp['n'].values).sum())}/357) ===")

print("\n=== 1. % of executed trades widened (per hypothesis), distribution over 357 ===")
print("pct_widened quantiles [p10,p25,p50,p75,p90,max]:", {k: round(float(np.nanquantile(m['pct_widened'],k)),3) for k in (.1,.25,.5,.75,.9,1.0)})
print("hyps with 0% widened:", int((m['n_widened']==0).sum()), " | >50% widened:", int((m['pct_widened']>0.5).sum()), " | >90%:", int((m['pct_widened']>0.9).sum()))
print("by stop regime: mean pct_widened where net1 defined; atr-stop vs structural — see per-family below")
fam_w = m.groupby('fam').agg(pct_widened=('pct_widened','mean'), n_hyp=('id','count')).sort_values('pct_widened',ascending=False)
print(fam_w.to_string())

print("\n=== 2. req_risk/min_exec for WIDENED trades (how far below the floor) ===")
wr=np.array(all_widened_ratio)
print(f"widened trades total: {len(wr)}")
if len(wr):
    print("req/floor quantiles [min,p10,p25,p50,p75,p90]:", {k: round(float(np.quantile(wr,k)),3) for k in (0.0,.1,.25,.5,.75,.9)})
    print("share of widened with req<10% of floor (order of magnitude below):", round(float((wr<0.10).mean()),3),
          " | req<50%:", round(float((wr<0.50).mean()),3), " | req in [50%,100%):", round(float(((wr>=0.5)&(wr<1.0)).mean()),3))

print("\n=== 3. correlation pct_widened vs net concentration (best/sumR) ===")
mm=m.dropna(subset=['net1','pct_widened'])
from numpy import corrcoef
pear=float(np.corrcoef(mm['pct_widened'], mm['net1'])[0,1])
rp=mm['pct_widened'].rank(); rn=mm['net1'].rank(); spear=float(np.corrcoef(rp,rn)[0,1])
print(f"Pearson(pct_widened, net1) = {pear:.3f}  | Spearman = {spear:.3f}  (n={len(mm)})")
# split by whether widening happens at all
print("mean net1 | hyps with 0% widened:", round(float(m[m.n_widened==0]['net1'].mean()),3), f"(n={int((m.n_widened==0).sum())})")
print("mean net1 | hyps with >0% widened:", round(float(m[m.n_widened>0]['net1'].mean()),3), f"(n={int((m.n_widened>0).sum())})")
print("mean net1 | hyps with >50% widened:", round(float(m[m.pct_widened>0.5]['net1'].mean()),3), f"(n={int((m.pct_widened>0.5).sum())})")

print("\n=== 4. was the BEST (concentration-driving) trade widened? ===")
print(f"hyps whose best trade was widened: {best_widened_count} / 357")
print("cross-tab with high net concentration:")
for thr in (0.30,0.50):
    hc=m[m.net1>thr]
    print(f"  net1>{thr:.0%}: {len(hc)} hyps, of which best-trade-widened: {int(hc['best_widened'].sum())}")

print("\n=== 5. active floor component among widened trades ===")
tot=sum(comp_counts.values())
print("counts:", comp_counts, f"(total widened {tot})")
if tot: print("shares:", {k: round(v/tot,3) for k,v in comp_counts.items()})

print("\n=== SPECIFIC: survivor + two h20-long ===")
for lab,hid in [('survivor h13-short time','ce76669a3b2a'),('h20-long time','2341cf9911de'),('h20-long rr2','00d840de0b48')]:
    row=m[m.id==hid].iloc[0]
    print(f"  {lab} ({hid}): n={row['n']} pct_widened={row['pct_widened']:.3f} best_widened={row['best_widened']} net1={row['net1']:.3f}")
m.to_parquet(os.path.join(ROOT,"results","matched_null_validation","stop_floor_diagnostic.parquet"))
print("\nwrote results/matched_null_validation/stop_floor_diagnostic.parquet")
