"""MANDATE 3 — pointed diagnostic of the 47 EXCLUSION-DEPENDENT hypotheses. Measurement only.
(1) Subtype of each excluded trade: same-bar-ambiguous (both stop & target reachable on entry bar)
    vs gap_stop (floored stop hit on entry bar, target NOT reachable = execution failure) vs target_only
    vs risk<=0 (never after floor). (2) Exclusion fraction per hyp vs the 1972 median.
Uses existing D2 artifacts; instrumented replica on the 47 (research). No campaign re-run, no holdout."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = pd.read_parquet(os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet")).set_index('id')
new  = pd.read_parquet(os.path.join(ROOT, "results", "reproduction_d2", "FAMILY_RESULTS.parquet")).set_index('id')
brk  = pd.read_parquet(os.path.join(ROOT, "results", "reproduction_d2", "bracket_69.parquet"))
the47 = sorted(brk[brk['excl_creates']]['id'].tolist())
idmap = {}
for fam in MS.REGISTRY:
    for h in MS.REGISTRY[fam][0](): idmap[h['id']] = h
TICK=MS.TICK; CFG=MS.CFG; C_SPREAD=2*CFG['spread_ticks']*TICK; C_TICK=5*TICK
d=MS.load(); a=int(len(d)*0.6); res=d.iloc[:a].copy()
o=res['open'].values;hi=res['high'].values;lo=res['low'].values;cl=res['close'].values;atr=res['m_atr'].values;n=len(res)

def excluded_subtypes(h):
    """Replicate simulate (stop-first, mark_invalid) and classify each EXCLUDED trade."""
    setups=MS.setups(res,h); last=-1
    c=dict(ambiguous=0, gap_stop=0, target_only=0, neg_risk=0, other=0); n_excl=0; n_kept=0
    for s in sorted(setups,key=lambda x:x['ei']):
        ei=s['ei']; si=s['si']
        if ei<=last or ei>=n-1 or ei<1: continue
        dirn=s['dir']; entry=o[ei]; stop=s['stop']; risk=abs(entry-stop)
        if not np.isfinite(risk) or np.isnan(atr[si]) or atr[si]<=0: continue
        me=max(C_SPREAD,C_TICK,0.10*atr[si]); widened=False
        if risk<me: risk=me; stop=entry-dirn*risk; widened=True
        if risk<=0:
            if widened: c['neg_risk']+=1; n_excl+=1
            continue
        ek=s['exit_kind']; ep=s.get('exit_param'); trail=(ek=='trailing'); to=int(ep) if ek=='time' else 48
        tgt=(entry+dirn*ep*risk) if ek=='rr' else (ep if ek in('opp_liq','opp_struct') else None)
        ex=None;xi=None;best=entry
        for j in range(ei,min(ei+to,n)):
            if trail:
                best=max(best,hi[j]) if dirn>0 else min(best,lo[j]); ts=best-dirn*1.5*atr[si]; stop=max(stop,ts) if dirn>0 else min(stop,ts)
            hitS=(lo[j]<=stop) if dirn>0 else (hi[j]>=stop)
            hitT=(tgt is not None and np.isfinite(tgt)) and ((hi[j]>=tgt) if dirn>0 else (lo[j]<=tgt))
            if hitS: ex=stop;xi=j;break
            if hitT: ex=tgt;xi=j;break
        if ex is None: xi=min(ei+to,n-1)
        if widened and xi==ei:   # EXCLUDED
            n_excl+=1
            hitS0=(lo[ei]<=stop) if dirn>0 else (hi[ei]>=stop)
            hitT0=(tgt is not None and np.isfinite(tgt)) and ((hi[ei]>=tgt) if dirn>0 else (lo[ei]<=tgt))
            if hitS0 and hitT0: c['ambiguous']+=1
            elif hitS0 and not hitT0: c['gap_stop']+=1
            elif hitT0 and not hitS0: c['target_only']+=1
            else: c['other']+=1
        else:
            n_kept+=1
        last=xi
    return c, n_excl, n_kept

# --- exclusion fraction over ALL 1972 (from the two parquets) ---
excl_frac_all = ((base['n']-new.loc[base.index,'n']) / base['n'].replace(0,np.nan))
med_frac = float(np.nanmedian(excl_frac_all))
print(f"exclusion fraction (excluded/baseline_n) over 1972: median={med_frac:.4f}  p90={float(np.nanquantile(excl_frac_all,0.9)):.4f}  max={float(np.nanmax(excl_frac_all)):.4f}")

rows=[]
agg=dict(ambiguous=0,gap_stop=0,target_only=0,neg_risk=0,other=0); tot_excl=0
for hid in the47:
    c,ne,nk=excluded_subtypes(idmap[hid])
    for k in agg: agg[k]+=c[k]
    tot_excl+=ne
    ef=float((base.loc[hid,'n']-new.loc[hid,'n'])/base.loc[hid,'n']) if base.loc[hid,'n']>0 else np.nan
    dom=max(c,key=c.get) if ne>0 else 'none'
    rows.append(dict(id=hid,fam=idmap[hid]['family'],base_n=int(base.loc[hid,'n']),new_n=int(new.loc[hid,'n']),
                     excl=ne,excl_frac=round(ef,4), ambiguous=c['ambiguous'],gap_stop=c['gap_stop'],
                     target_only=c['target_only'],neg_risk=c['neg_risk'],dom_subtype=dom))
m=pd.DataFrame(rows)
print(f"\n=== 47 EXCLUSION-DEPENDENT: subtype of EXCLUDED trades (aggregate {tot_excl} excluded) ===")
for k in ('ambiguous','gap_stop','target_only','neg_risk','other'):
    print(f"  {k:12s}: {agg[k]:6d}  ({100*agg[k]/max(tot_excl,1):.1f}%)")
print("  dominant subtype per hyp (count of hyps):", dict(m['dom_subtype'].value_counts()))
print(f"\n=== exclusion fraction of the 47 vs body median {med_frac:.4f} ===")
print(f"  47 excl_frac: median={m['excl_frac'].median():.4f}  min={m['excl_frac'].min():.4f}  max={m['excl_frac'].max():.4f}")
print(f"  of 47 with excl_frac > body median: {int((m['excl_frac']>med_frac).sum())}/47  | > 5x median: {int((m['excl_frac']>5*med_frac).sum())}/47")
print("\nsample:")
print(m[['id','fam','base_n','excl','excl_frac','ambiguous','gap_stop','target_only','dom_subtype']].head(12).to_string(index=False))
m.to_parquet(os.path.join(ROOT,"results","reproduction_d2","mandate3_47.parquet"))
json.dump(dict(body_median_excl_frac=med_frac, total_excluded=tot_excl,
               subtype_agg=agg, subtype_pct={k:round(100*agg[k]/max(tot_excl,1),1) for k in agg},
               n47_above_median=int((m['excl_frac']>med_frac).sum()),
               n47_above_5x_median=int((m['excl_frac']>5*med_frac).sum()),
               median_excl_frac_47=float(m['excl_frac'].median())),
          open(os.path.join(ROOT,"results","reproduction_d2","mandate3_47_summary.json"),"w"),indent=1)
print("\nwrote mandate3_47.parquet + summary.json")
