"""WAVE-1 DRIVER — runs EXP-01..EXP-06 exactly as frozen in WAVE_1_SPEC.md, using code/wave1_harness.py.
Order of operations: (1) pre-register everything to results/experiments/wave1/wave1_prereg.json BEFORE any
p is computed; (2) run the six experiments (all execution via MS.simulate / MN.matched_null_p on the
research segment; OOS reported on the validation segment; holdout SEALED); (3) apply ONE Wave-1 family-wise
correction (Holm-Bonferroni) across the six PRIMARY contrasts — NOT the global S1-S51 FDR; (4) assign a
status from the ALLOWED set via a FROZEN decision function; (5) write per-experiment + summary artifacts.

  usage:  python run_wave1.py            # full frozen run
          python run_wave1.py --dry      # reduced B/K wiring check, NO verdicts, NO family correction
"""
import os, sys, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS, mstrat_ext as MSX
import wave1_harness as W

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "experiments", "wave1"); os.makedirs(OUT, exist_ok=True)
ALPHA = 0.05
P = W.PREREG

def _mirror(h, key='side'):
    m = dict(h); m[key] = {'low': 'high', 'high': 'low', 'up': 'down', 'down': 'up'}[h[key]]; return m

def _straddles(ci, x):
    return ci is not None and ci[0] is not None and ci[0] <= x <= ci[1]

# ------------------------------ FROZEN STATUS DECISION FUNCTION ------------------------------
# Declared BEFORE any result is read. adj_p = Holm-adjusted primary p. Effect signs/CIs from the harness.
def decide(kind, rec, adj_p):
    if rec.get('primary_n', 0) < P['min_trades'] or adj_p is None:
        return 'UNRESOLVED'
    if kind == 'mechanism_paired':          # EXP-01: eff = confirmed - raw
        eff = rec['delta']; dci = rec['delta_ci']
        if adj_p < ALPHA and eff > 0:            return 'SUPPORTS CLAIM'
        if dci[1] < 0:                           return 'CONTRADICTS CLAIM'
        if eff < 0:                              return 'WEAKENS CLAIM'
        return 'NO DIFFERENCE DETECTED'
    if kind == 'mechanism_selection':       # EXP-02: gated vs ungated
        eff = rec['delta']; on_ci = rec['mean_on_ci']; moff = rec['mean_off']
        if adj_p < ALPHA and eff > 0:            return 'SUPPORTS CLAIM'
        if on_ci[1] < moff:                      return 'CONTRADICTS CLAIM'
        if eff < 0:                              return 'WEAKENS CLAIM'
        return 'NO DIFFERENCE DETECTED'
    if kind == 'beta_matched':              # EXP-03/04: claim = survives beta-matched null (timing-alpha)
        if _straddles(rec['p_ci'], ALPHA):       return 'UNRESOLVED'
        if adj_p < ALPHA:                        return 'SUPPORTS CLAIM'
        return 'WEAKENS CLAIM'                   # fails to beat beta/regime-matched null -> consistent with beta
    if kind == 'placebo':                   # EXP-05/06: claim = the level identity carries the edge
        if _straddles(rec['p_ci'], ALPHA):       return 'UNRESOLVED'
        if adj_p < ALPHA:                        return 'SUPPORTS CLAIM'
        # CONTRADICTS only if REAL is SIGNIFICANTLY WORSE than the placebo (lower-tail test) — per Codex review,
        # p>0.5 alone is merely 'no support', not evidence the level is spurious.
        if rec.get('raw_p_low') is not None and rec['raw_p_low'] < ALPHA:  return 'CONTRADICTS CLAIM'
        return 'NO DIFFERENCE DETECTED'
    return 'INVALID EXPERIMENT'

# ------------------------------ EXPERIMENTS ------------------------------
def exp01(res, val, B):
    """Confirmation contribution in liquidity sweeps (S1 confirmed vs raw, paired identical sample)."""
    h = P['reps']['S1']['h']
    conf_su, conf_meta = W.sweep_setups(res, h, confirm=True)
    raw_su, raw_meta = W.sweep_setups(res, h, confirm=False)
    Rc, sic = W.sim_R(res, conf_su); Rr, sir = W.sim_R(res, raw_su)
    prim = W.paired_timing_contrast(res, Rc, sic, Rr, sir, B, P['seeds']['exp01'], P['margin'])
    # ---- CEO-mandated decomposition: is any difference from confirmation, or from delay/price/count? ----
    conf_t0 = set(m['t0'] for m in conf_meta)
    raw_all_n = len(raw_su); raw_conf_only = [s for s in raw_su if s['si'] in conf_t0]
    Rr_confonly, _ = W.sim_R(res, raw_conf_only)
    o = res['open'].values
    # entry-price change on the paired (same t0) events
    conf_entry = {m['t0']: o[m['ei']] for m in conf_meta}; raw_entry = {m['t0']: o[m['ei']] for m in raw_meta}
    dirn = conf_su[0]['dir'] if conf_su else 1
    paired_t0 = sorted(conf_t0 & set(raw_entry))
    dprice = float(np.mean([dirn * (conf_entry[t] - raw_entry[t]) for t in paired_t0])) if paired_t0 else float('nan')
    decomp = dict(
        sweeps_total=raw_all_n, confirmed=len(conf_su), confirm_rate=(len(conf_su) / raw_all_n if raw_all_n else float('nan')),
        mean_delay_bars=float(np.mean([m['delay'] for m in conf_meta])) if conf_meta else float('nan'),
        mean_entry_price_shift_dir=dprice,
        raw_all_exp=W.metrics_R(Rr)['exp'], raw_confirmed_only_exp=W.metrics_R(Rr_confonly)['exp'],
        confirmed_exp=W.metrics_R(Rc)['exp'],
        selection_effect_note='raw_all vs raw_confirmed_only isolates confirmation-as-SELECTION; '
                              'confirmed vs raw_confirmed_only isolates confirmation-as-TIMING(delay+price).',
        exposure_duration='NOT MEASURED — MS.simulate returns (R,si,ei) only; exit index is not exposed by the '
                          'frozen engine, so holding time is not reported without an engine change (out of scope).')
    Rc_oos, _ = W.sim_R(val, W.sweep_setups(val, h, confirm=True)[0])
    return dict(exp='EXP-01', kind='mechanism_paired', hypothesis='HGv1-042', rep_id=P['reps']['S1']['id'],
                arms=dict(confirmed=W.metrics_R(Rc), raw=W.metrics_R(Rr)),
                primary=prim, primary_n=prim['paired_n'], raw_p=prim['p'], p_ci=prim.get('p_ci'),
                delta=prim.get('delta'), delta_ci=prim.get('delta_ci'),
                oos=dict(confirmed_exp=W.metrics_R(Rc_oos)['exp'], confirmed_n=W.metrics_R(Rc_oos)['n']),
                decomposition=decomp)

def exp02(res, val, B):
    """Efficiency-gate contribution in continuation (S39). 'Same universe' design (per spec): execute the
    UNGATED generic-continuation universe ONCE through MS.simulate, then partition the EXECUTED trades by the
    trend-efficiency label (er>=thr) at each trade's signal bar. gate-ON arm = efficient partition; gate-OFF
    arm = whole universe. This makes the gate a pure SELECTION operator on one common backtest and avoids the
    onset-timing mismatch that arises if the gated and ungated onsets are executed as separate strategies."""
    h = P['reps']['S39']['h']; L = int(h['L']); thr = float(h['er_thr'])
    off_su = W.cont_setups(res, h, gate=False)
    Roff, si_off = W.sim_R(res, off_su)
    er = MSX._efficiency_ratio(res['close'].values, L)
    eff_mask = er[si_off] >= thr                                   # efficiency label at each EXECUTED trade's signal bar
    R_on = Roff[eff_mask]
    prim = W.selection_contrast(R_on, Roff, B, P['seeds']['exp02'], P['margin'])
    # context: S39 exactly as registered (its own onset), for cross-reference (small onset-timing difference)
    Rs39, _ = W.sim_R(res, W.cont_setups(res, h, gate=True))
    # decomposition — align to the EXECUTED trades (si_off), not the raw setups (overlap suppression differs)
    cost = 2 * CFG_spread(); o = res['open'].values
    by_si = {int(s['si']): s for s in off_su}
    risk_off = np.array([abs(o[by_si[int(s)]['ei']] - by_si[int(s)]['stop']) for s in si_off], dtype=float)
    dir_off = np.array([by_si[int(s)]['dir'] for s in si_off]); dir_on = dir_off[eff_mask]; risk_on = risk_off[eff_mask]
    decomp = dict(
        universe='ungated generic continuation (executed once); gate-ON = efficient partition of it',
        n_off=int(len(Roff)), n_on=int(eff_mask.sum()),
        frequency_ratio=float(eff_mask.mean()),
        all_trends_exp=W.metrics_R(Roff)['exp'], efficient_subset_exp=W.metrics_R(R_on)['exp'],
        s39_as_registered_exp=W.metrics_R(Rs39)['exp'], s39_as_registered_n=W.metrics_R(Rs39)['n'],
        long_share_on=float(np.mean(dir_on > 0)) if len(dir_on) else float('nan'),
        long_share_off=float(np.mean(dir_off > 0)) if len(dir_off) else float('nan'),
        cost_drag_R_on=float(cost / np.mean(risk_on)) if len(risk_on) else float('nan'),
        cost_drag_R_off=float(cost / np.mean(risk_off)) if len(risk_off) else float('nan'),
        retrospective_selection_note='the null draws random size-n_on subsets of the WHOLE executed continuation '
                                     'universe; if the efficient partition sits inside that null (large p) the gate '
                                     'does NOT select better-than-random trends (no genuine efficiency edge).')
    off_val = W.cont_setups(val, h, gate=False); Roff_v, si_v = W.sim_R(val, off_val)
    er_v = MSX._efficiency_ratio(val['close'].values, L); R_on_v = Roff_v[er_v[si_v] >= thr]
    return dict(exp='EXP-02', kind='mechanism_selection', hypothesis='HGv1-043', rep_id=P['reps']['S39']['id'],
                arms=dict(gate_on=W.metrics_R(R_on), gate_off=W.metrics_R(Roff)),
                primary=prim, primary_n=prim['n_on'], raw_p=prim['p'], p_ci=prim.get('p_ci'),
                delta=prim.get('delta'), mean_on_ci=prim.get('mean_on_ci'), mean_off=prim.get('mean_off'),
                oos=dict(gate_on_exp=W.metrics_R(R_on_v)['exp'], gate_on_n=W.metrics_R(R_on_v)['n']),
                decomposition=decomp)

def CFG_spread():
    return (MS.CFG['spread_ticks'] + MS.CFG['slip_ticks']) * MS.TICK

def _beta_exp(tag, hyp, rep_key, res, val, B, seed):
    """Shared EXP-03/04 body: beta/regime-matched null on the representative (primary) + the opposite-side
    mirror (reported separately), plus the validated unstratified null as a calibration anchor."""
    h = P['reps'][rep_key]['h']; hm = _mirror(h)
    strata = ['strat_combo']            # single composite session|vol|trend column (see wave1_harness._add_strata)
    su = MS.setups(res, h) if h['family'] in MS.REGISTRY else MSX.ext_setups(res, h)
    su_m = MS.setups(res, hm) if h['family'] in MS.REGISTRY else MSX.ext_setups(res, hm)
    rec_strat = W.matched_contrast(res, su, B, seed, strata)         # PRIMARY: beta/regime-matched
    rec_unstr = W.matched_contrast(res, su, B, seed, None)           # validated-config anchor
    rec_mir = W.matched_contrast(res, su_m, B, seed + 1, strata)     # opposite-direction arm
    su_oos = MS.setups(val, h) if h['family'] in MS.REGISTRY else MSX.ext_setups(val, h)
    oos = W.metrics_R(W.sim_R(val, su_oos)[0])
    return dict(exp=tag, kind='beta_matched', hypothesis=hyp, rep_id=P['reps'][rep_key]['id'],
                primary=rec_strat, primary_n=rec_strat.get('k', 0), raw_p=rec_strat.get('p'),
                p_ci=rec_strat.get('ci'), obs_mean=rec_strat.get('obs_mean'), null_mean=rec_strat.get('null_mean'),
                side_primary=dict(side=h['side'], k=rec_strat.get('k'), p=rec_strat.get('p'),
                                  obs_mean=rec_strat.get('obs_mean')),
                side_mirror=dict(side=hm['side'], k=rec_mir.get('k'), p=rec_mir.get('p'),
                                 obs_mean=rec_mir.get('obs_mean')),
                unstratified_anchor=dict(p=rec_unstr.get('p'), obs_mean=rec_unstr.get('obs_mean'),
                                         null_mean=rec_unstr.get('null_mean'), ci=rec_unstr.get('ci')),
                oos=dict(exp=oos['exp'], n=oos['n']),
                caveat='PRIMARY p uses a session x vol x trend STRATIFIED (beta/regime-matched) null. The '
                       'stratified config is NOT separately calibration-validated (only the unstratified config '
                       'passed the matched-null battery), so EXP-03/04 are DIAGNOSTIC-grade; the unstratified '
                       'anchor p is reported alongside. Representatives are single-direction; the opposite side '
                       'is reported as side_mirror.')

def exp03(res, val, B):
    return _beta_exp('EXP-03', 'HGv1-048', 'S1', res, val, B, P['seeds']['exp03'])

def exp04(res, val, B):
    return _beta_exp('EXP-04', 'HGv1-049', 'S5', res, val, B, P['seeds']['exp04'])

def _placebo_exp(tag, hyp, rep_key, setup_fn, ref_cols, res, val, K, seed):
    prim = W.label_shuffle_placebo(res, setup_fn, ref_cols, K, seed, P['placebo_window_days'])
    oos = W.metrics_R(W.sim_R(val, setup_fn(val))[0])
    return dict(exp=tag, kind='placebo', hypothesis=hyp, rep_id=P['reps'][rep_key]['id'],
                primary=prim, primary_n=prim['real'].get('n', 0), raw_p=prim.get('p'), raw_p_low=prim.get('p_low'),
                p_ci=prim.get('ci'), real=prim['real'], shuffled_mean_of_means=prim.get('shuffled_mean_of_means'),
                freq_ratio=prim.get('freq_ratio'), shuffled_n_median=prim.get('shuffled_n_median'),
                oos=dict(exp=oos['exp'], n=oos['n']),
                geometry_note='Placebo transplants each day a NEARBY donor day\'s level-relative-to-price offset '
                              '(preserves daily persistence + distance geometry + signal frequency: freq_ratio '
                              'reported), while destroying the level\'s economic identity. K seeded shuffles.')

def exp05(res, val, K):
    h = P['reps']['S1']['h']
    fn = lambda frame: W.sweep_setups(frame, h, confirm=True)[0]
    return _placebo_exp('EXP-05', 'HGv1-050', 'S1', fn, ['pdh', 'pdl'], res, val, K, P['seeds']['exp05'])

def exp06(res, val, K):
    h = P['reps']['S2']['h']
    fn = lambda frame: MS.setups(frame, h)          # S2 uses pdh/pdl via ref='pdh_pdl'
    return _placebo_exp('EXP-06', 'HGv1-051', 'S2', fn, ['pdh', 'pdl'], res, val, K, P['seeds']['exp06'])

# ------------------------------ ORCHESTRATION ------------------------------
def to_jsonable(x):
    if isinstance(x, dict): return {k: to_jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [to_jsonable(v) for v in x]
    if isinstance(x, (np.floating,)): return float(x)
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, float) and (x != x): return None
    return x

def run(dry=False):
    B = 400 if dry else P['B_perm']; Bm = 400 if dry else P['B_matched']; K = 30 if dry else P['K_shuffle']
    res, val, meta = W.load_segments(with_strata=True)
    prereg = to_jsonable(dict(spec='knowledge/experiments/WAVE_1_SPEC.md', prereg=P, split_bars=meta,
                              alpha=ALPHA, status_rules='frozen in run_wave1.decide()',
                              note='ids/seeds/B/K/margins/multiplicity fixed BEFORE any p computed; holdout SEALED'))
    if not dry:
        json.dump(prereg, open(os.path.join(OUT, 'wave1_prereg.json'), 'w'), indent=1)
    print(f"[wave1] {'DRY-RUN (no verdicts)' if dry else 'FULL RUN'}  research={len(res)} oos={len(val)} "
          f"holdout(SEALED)={meta['holdout_bars']}  B={B} Bm={Bm} K={K}", flush=True)

    t0 = time.time(); recs = []
    for fn, arg in [(exp01, B), (exp02, B), (exp03, Bm), (exp04, Bm), (exp05, K), (exp06, K)]:
        r = fn(res, val, arg); recs.append(r)
        print(f"  {r['exp']} done  n={r.get('primary_n')} raw_p={r.get('raw_p')}  ({time.time()-t0:.0f}s)", flush=True)

    if dry:
        print("[wave1] dry-run complete — wiring OK, NO verdicts issued, NO family-wise correction applied.")
        return recs

    # ONE Wave-1 family-wise correction across the six PRIMARY p's (NOT global S1-S51 FDR)
    pvals = [r.get('raw_p') for r in recs]
    adj = W.holm_bonferroni(pvals); bh = W.bh_fdr(pvals, q=0.10)
    for r, ap, bp in zip(recs, adj, bh):
        r['adj_p_holm'] = ap; r['bh_fdr_pass_q0.10'] = bp
        r['status'] = decide(r['kind'], r, ap)
        assert r['status'] in W.ALLOWED_STATUS, r['status']
        json.dump(to_jsonable(r), open(os.path.join(OUT, f"{r['exp']}_result.json"), 'w'), indent=1)

    summ = pd.DataFrame([dict(exp=r['exp'], hypothesis=r['hypothesis'], kind=r['kind'], rep_id=r['rep_id'],
                              primary_n=r.get('primary_n'), raw_p=r.get('raw_p'), adj_p_holm=r.get('adj_p_holm'),
                              bh_pass=r.get('bh_fdr_pass_q0.10'), status=r['status'],
                              oos_exp=(r.get('oos') or {}).get('confirmed_exp', (r.get('oos') or {}).get('exp')))
                         for r in recs])
    summ.to_parquet(os.path.join(OUT, 'WAVE_1_SUMMARY.parquet'))
    json.dump(to_jsonable(dict(multiplicity=P['multiplicity'], alpha=ALPHA,
                               primary_pvals=pvals, holm_adj=adj, bh_pass=bh,
                               results=[dict(exp=r['exp'], status=r['status'], raw_p=r['raw_p'],
                                             adj_p_holm=r['adj_p_holm']) for r in recs],
                               note='Wave-1 family-wise correction ONLY; global S1-S51 FDR NOT run; holdout SEALED')),
              open(os.path.join(OUT, 'wave1_summary.json'), 'w'), indent=1)
    print("\n[wave1] STATUS (Holm-adjusted family of 6):")
    for r in recs:
        print(f"  {r['exp']}  {r['status']:<22} raw_p={r['raw_p']}  adj_p={r['adj_p_holm']}")
    print(f"[wave1] total {time.time()-t0:.0f}s")
    return recs

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--dry', action='store_true'); a = ap.parse_args()
    run(dry=a.dry)
