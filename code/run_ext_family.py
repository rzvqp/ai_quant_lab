"""Run ONE extension family (S21-S40) through the SAME pipeline as S1-S20: parity + smoke + full historical
backtest on the research segment (60%), validation (20%) for val_exp, holdout (20%) SEALED. Metric and screen
definitions are copied VERBATIM from the official run_full_campaign.py / run_lot.py so the new family is scored
identically to S1-S20. Usage: python code/run_ext_family.py S21"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS, mstrat_ext as EXT
from alpha_lab import CFG
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "ext_families"); os.makedirs(OUTDIR, exist_ok=True)

def parity_and_smoke(d, fam):
    """VERBATIM logic from run_lot.parity_and_smoke, restricted to one ext family."""
    gram, setf = EXT.EXT_REGISTRY[fam]
    print("--- BACKTEST PARITY AUDIT (fast vs reference engine) ---")
    ok_par = True
    g = gram()[:40]
    for h in g:
        if h.get('exit') in ('trailing',) or h.get('exit_kind') == 'trailing':
            continue
        su = [s for s in setf(d, h) if s['exit_kind'] in ('rr', 'time', 'opp_liq', 'opp_struct')]
        if len(su) < 3:
            continue
        a = MS.simulate(d, su, CFG)['R'].values; b = MS.simulate_ref(d, su, CFG)
        if len(a) != len(b) or (len(a) > 0 and np.max(np.abs(a - b)) > 1e-9):
            ok_par = False; print(f"  PARITY FAIL {fam} {h['id']}")
        break
    print(f"  parity: {'PASS' if ok_par else 'FAIL'}")
    print("--- SMOKE + LOOKAHEAD + LEDGER ---")
    nb = len(d); hs = gram(); sig = 0; la_ok = True; ledger_ok = True; selective = True
    for h in hs[:60]:
        su = setf(d, h)
        if su: sig += 1
        if len(su) > 0.10 * nb: selective = False
        for s in su[:200]:
            if not (s['ei'] > s['si']): la_ok = False
        if su and not set(['R', 'si', 'ei']).issubset(MS.simulate(d, su, CFG).columns): ledger_ok = False
    v = sig >= 1 and selective and la_ok and ledger_ok
    print(f"  {fam}: grammar={len(hs)} signal_hyps={sig} selective={selective} lookahead_safe={la_ok} ledger_ok={ledger_ok} -> {'OK' if v else 'FAIL'}")
    return ok_par and v

def run(fam):
    d = MS.load(); n = len(d); a = int(n * 0.6); b = int(n * 0.8)
    res = d.iloc[:a].copy(); val = d.iloc[a:b].copy()   # holdout d[b:] SEALED
    rt = res['time'].values
    print(f"ENGINE v2 (stop-floor). research={a} val={b-a} holdout(SEALED)={n-b}")
    if not parity_and_smoke(d, fam):
        print("PRECHECK FAIL"); return
    gram, setf = EXT.EXT_REGISTRY[fam]
    rows = []; t0 = time.time()
    for h in gram():
        tr = MS.simulate(res, setf(res, h), CFG); R = tr['R'].values; ei = tr['ei'].astype(int).values
        nn = len(R)
        if nn == 0:
            rows.append(dict(fam=fam, id=h['id'], h={k: v for k, v in h.items() if k not in ('id', 'family')}, n=0)); continue
        eq = np.cumsum(R); dd = float(np.max(np.maximum.accumulate(eq) - eq)); gp = R[R > 0].sum(); gl = -R[R < 0].sum()
        pf = float(gp / gl) if gl > 0 else np.inf; exp = float(R.mean())
        srt = np.sort(R)[::-1]; gpp = R[R > 0].sum() if (R > 0).any() else 1
        t1 = srt[:1].sum() / gpp; t3 = srt[:3].sum() / gpp; t5 = srt[:5].sum() / gpp
        wo1 = (R.sum() - srt[:1].sum()) / max(nn - 1, 1)
        lo, hi = np.percentile(R, [5, 95]); trim5 = R[(R >= lo) & (R <= hi)].mean()
        mon = pd.to_datetime(rt[ei], unit='s').to_period('M'); gm = pd.Series(R).groupby(mon).mean()
        yr = pd.to_datetime(rt[ei], unit='s').year; yrs = {int(Y): round(float(R[yr == Y].mean()), 3) for Y in sorted(set(yr))}
        mv = MS.simulate(val, setf(val, h), CFG); mvexp = float(mv['R'].mean()) if len(mv) >= 5 else np.nan
        dirs = set(s['dir'] for s in setf(res, h)); side = 'both' if len(dirs) > 1 else ('long' if 1 in dirs else 'short')
        rows.append(dict(fam=fam, id=h['id'], h={k: v for k, v in h.items() if k not in ('id', 'family')},
            n=nn, exp=exp, pf=pf, dd=dd, win=float((R > 0).mean()), sumR=float(R.sum()), val_exp=mvexp,
            median=float(np.median(R)), trim5=float(trim5), t1=float(t1), t3=float(t3), t5=float(t5), wo1=float(wo1),
            months=int(gm.shape[0]), pos_months=int((gm > 0).sum()), years=len(yrs), yrs=yrs, side=side))
    df = pd.DataFrame(rows)
    def hist_prof(r): return r['n'] > 0 and r['sumR'] > 0 and r['exp'] > 0 and r['pf'] > 1.00
    def research_worthy(r):
        return (r['n'] >= 25 and r['exp'] > 0 and r['pf'] >= 1.02 and r['dd'] <= 25 and (r['wo1'] > 0 or r['t1'] < 0.5) and (r['months'] >= 2 and r['years'] >= 2))
    df['hist_prof'] = df.apply(lambda r: hist_prof(r) if r['n'] > 0 else False, axis=1)
    df['research_worthy'] = df.apply(lambda r: research_worthy(r) if r['n'] > 0 else False, axis=1)
    df['fragile'] = df.apply(lambda r: (r['n'] > 0 and r['exp'] > 0 and (r['t1'] >= 0.5 or r['wo1'] <= 0)), axis=1)
    print(f"compute {time.time()-t0:.0f}s | total hyps={len(df)}")
    valid = int((df['n'] >= 25).sum()); prof = int(df['hist_prof'].sum()); rw = int(df['research_worthy'].sum())
    sp = df[df['n'] > 0]
    print(f"\nTOTALS {fam}: generated={len(df)} valid(n>=25)={valid} HIST_PROFITABLE={prof} RESEARCH_WORTHY={rw}")
    if len(sp):
        be = sp['exp'].max(); bp = sp[sp['pf'] < np.inf]['pf'].max() if len(sp[sp['pf'] < np.inf]) else np.nan
        print(f"  bestExp={be:.3f} bestPF={bp:.2f} | exp range [{sp['exp'].min():.3f},{sp['exp'].max():.3f}] | n range [{int(sp['n'].min())},{int(sp['n'].max())}]")
    df.drop(columns=['h', 'yrs']).to_parquet(os.path.join(OUTDIR, f"{fam}_results.parquet"))
    # top variants for the report
    pr = df[df.hist_prof].copy()
    if len(pr):
        print(f"\n--- {fam} profitable variants (by monthly stability, n>=25) ---")
        pr['stab'] = pr['pos_months'] / pr['months'].clip(lower=1)
        for _, r in pr[pr.n >= 25].sort_values(['stab', 'n'], ascending=False).head(12).iterrows():
            spec = {k: v for k, v in df[df.id == r['id']].iloc[0]['h'].items()}
            print(f"  [{r['id']}] {r['side']} n={r['n']} exp={r['exp']:.3f} pf={r['pf'] if r['pf']<np.inf else 99:.2f} dd={r['dd']:.1f} win={r['win']:.2f} posM={r['pos_months']}/{r['months']} yr={r['years']} t1={r['t1']:.2f} val={r['val_exp'] if not np.isnan(r['val_exp']) else float('nan'):.3f} RW={r['research_worthy']} :: {spec}")
    print("\nSTRICT VALIDATION: PENDING (matched-null validated but global-FDR CEO-gated). Holdout SEALED.")

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else 'S21')
