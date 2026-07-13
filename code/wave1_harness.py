"""WAVE-1 HARNESS — Experiment Planner v1, Wave 1 (EXP-01..EXP-06).  FROZEN SPEC:
knowledge/experiments/WAVE_1_SPEC.md + WAVE1_HANDOFF.md + EXPERIMENT_PRIORITY_MATRIX.md.

This module builds the two shared harnesses the spec asks for (a paired mechanism contrast, a
beta/regime-matched null, and a level-label-shuffle placebo) and NOTHING ELSE. Hard rules honoured:

  * NO parallel backtester. Every arm's per-trade R is produced by MS.simulate (ENGINE v2: v2 stop-floor,
    the shared cost model, the overlap rule, the R calculation). Matched-null arms route through
    MN.matched_null_p, which itself calls MS.simulate. This module only (a) constructs setup dicts
    (the same {si,ei,dir,stop,exit_kind,exit_param} contract every S1-S51 family uses) and
    (b) computes permutation / bootstrap p-values on the R vectors the engine returns.
  * The control-arm setup builders below are PARITY-LOCKED: with the treatment toggle ON they must
    reproduce MS.s1_setups / MSX.s39_setups byte-for-byte (asserted in tests/test_wave1_harness.py).
    The control arm therefore differs from the treatment arm in EXACTLY ONE dimension (the toggle).
  * mstrat.py / mstrat_ext.py / matched_null.py are NOT imported-and-modified; they are imported and
    CALLED. mstrat.py is frozen; s1_setups etc. are read, never patched.
  * Splits: research = first 60% M15, OOS = next 20% (a=int(n*0.6), b=int(n*0.8)) — identical to
    run_full_campaign.py / run_matched_null_pilot.py. Terminal holdout d[b:] is NEVER loaded here.
  * All randomization seeds, B, K, margins, min-trades and the multiplicity method are frozen in PREREG
    below, BEFORE any result is read. No post-hoc reinterpretation, no parameter optimisation.

Allowed experiment statuses (spec): SUPPORTS CLAIM / WEAKENS CLAIM / NO DIFFERENCE DETECTED /
CONTRADICTS CLAIM / UNRESOLVED / INVALID EXPERIMENT. This module NEVER emits VALIDATED ALPHA /
PRODUCTION READY / FINAL STRATEGY.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import mstrat as MS
import mstrat_ext as MSX
import matched_null as MN

TICK = MS.TICK
CFG = MS.CFG

# ============================== FROZEN PRE-REGISTRATION ==============================
# Representative hypotheses selected by the SAME deterministic rule used in the matched-null pilot
# (research_worthy -> largest n; fallback hist_prof -> largest n; resolved from the frozen result
# parquets). Ids are pinned here so the run is reproducible and pre-registered.
PREREG = dict(
    split=(0.6, 0.8),                       # research [:a], OOS [a:b]; holdout [b:] SEALED
    min_trades=30,                          # per arm; below -> UNRESOLVED (spec)
    margin=0.0,                             # H1 margin on the primary contrast (mean expectancy, R/trade)
    B_perm=20000,                           # permutation replicates for EXP-01/02 paired/selection tests
    B_matched=20000,                        # matched-null replicates for EXP-03/04 (fixed B, no adaptive refine)
    K_shuffle=500,                          # level-label-shuffle replicates for EXP-05/06
    placebo_window_days=30,                 # donor day drawn from +/- this many calendar days (proximity kept)
    multiplicity='holm-bonferroni',         # Wave-1 family-wise correction across the 6 primary p's (FWER)
    reps=dict(
        S1=dict(id='f34e8d2827c3', h={'side':'low','liq_ref':'pdh_pdl','liq_lb':50,'confirm':'consecutive2',
                                       'imb':'none','stop':'beyond_sweep','exit':'rr2','window':8,'family':'S1'}),
        S2=dict(id='959581cbcdb3', h={'ref':'pdh_pdl','lb':20,'fail_within':4,'stop':'atr','exit':'rr2',
                                      'side':'low','family':'S2'}),
        S5=dict(id='3a9d271b56b8', h={'session':'ny','mode':'breakout','stop':'atr','exit':'rr2',
                                      'side':'up','family':'S5'}),
        S39=dict(id='13752e544049', h={'L':20,'er_thr':0.5,'stop':'swing','exit':'rr2','family':'S39'}),
    ),
    seeds=dict(exp01=0x1E01, exp02=0x1E02, exp03=0x1E03, exp04=0x1E04, exp05=0x1E05, exp06=0x1E06,
               matched_research=0xA11CE, matched_val=0xB0B),
)
ALLOWED_STATUS = ('SUPPORTS CLAIM', 'WEAKENS CLAIM', 'NO DIFFERENCE DETECTED',
                  'CONTRADICTS CLAIM', 'UNRESOLVED', 'INVALID EXPERIMENT')

# ============================== SEGMENTS (frozen split; holdout excluded) ==============================
_CACHE = {}
def load_segments(with_strata=True):
    """MS.load() -> research/OOS segments (holdout SEALED, never returned). Adds regime strata columns
    used by the beta/regime-matched null (EXP-03/04). Cached within a process."""
    if 'seg' in _CACHE:
        return _CACHE['seg']
    d = MS.load()
    n = len(d); a = int(n * PREREG['split'][0]); b = int(n * PREREG['split'][1])
    res = d.iloc[:a].copy(); val = d.iloc[a:b].copy()      # d.iloc[b:] is the SEALED terminal holdout — untouched
    if with_strata:
        for seg in (res, val):
            _add_strata(seg)
    _CACHE['seg'] = (res, val, dict(n=n, a=a, b=b, holdout_bars=n - b))
    return _CACHE['seg']

def _add_strata(seg):
    """Regime/session/trend context columns for the beta-matched null. Lookahead-safe (all derived from
    features already in the frame). session already exists; vol regime = m_atr vs its 50-bar mean;
    trend = h4 trend sign (the 'gold beta' proxy the beta diagnostic conditions on). We build a SINGLE
    composite string column `strat_combo` and pass it as a one-element strata list to matched_null_p: the
    frozen matched_null.eligibility_pool/_strata_key has a latent bug with multi-column strata (equal-length
    key tuples collapse to a 2-D ndarray -> unhashable keys), so a single composite column is the correct,
    frozen-engine-preserving way to get session x vol x trend stratification."""
    seg['strat_sess'] = seg['session'].astype(str).values
    atr = seg['m_atr'].values; ama = seg['atr_ma'].values if 'atr_ma' in seg else pd.Series(atr).rolling(50).mean().values
    seg['strat_vol'] = np.where(np.isfinite(ama) & (atr > ama), 'hi', 'lo')
    seg['strat_trend'] = np.where(seg['h4_trend_up'].values > 0.5, 'up', 'dn')
    seg['strat_combo'] = (pd.Series(seg['strat_sess'].astype(str)) + '|' +
                          pd.Series(seg['strat_vol'].astype(str)) + '|' +
                          pd.Series(seg['strat_trend'].astype(str))).values

# ============================== METRICS (summary stats on engine output; NOT execution) ==============================
def metrics_R(R):
    R = np.asarray(R, dtype=float)
    if len(R) == 0:
        return dict(n=0, exp=float('nan'), pf=float('nan'), maxdd_R=float('nan'), win=float('nan'), sumR=0.0)
    eq = np.cumsum(R); peak = np.maximum.accumulate(eq); dd = float(np.max(peak - eq)) if len(eq) else 0.0
    gp = R[R > 0].sum(); gl = -R[R < 0].sum()
    pf = float(gp / gl) if gl > 0 else (float('inf') if gp > 0 else 0.0)
    return dict(n=int(len(R)), exp=float(R.mean()), pf=pf, maxdd_R=dd, win=float((R > 0).mean()), sumR=float(R.sum()))

def _wilson(k, nB, z=1.959963985):
    if nB <= 0:
        return (0.0, 1.0)
    phat = k / nB; denom = 1 + z * z / nB
    center = (phat + z * z / (2 * nB)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / nB + z * z / (4 * nB * nB))) / denom
    return (float(max(0.0, center - half)), float(min(1.0, center + half)))

# ============================== PARITY-LOCKED CONTROL-ARM BUILDERS ==============================
# sweep_setups: faithful reproduction of mstrat.s1_setups with a `confirm` toggle. confirm=True MUST
# reproduce MS.s1_setups(d,h) exactly (parity test). confirm=False = the RAW arm: enter at t0+1 with NO
# confirmation stage, holding the sweep-event definition, stop rule and exit rule identical. Returns
# (setups, meta) where meta[i] carries t0 and the confirmation index so EXP-01 can DECOMPOSE the effect
# into selection / entry-delay / entry-price without re-running execution.
def sweep_setups(d, h, confirm=True):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values
    rmax = d['rmax20'].values; rmin = d['rmin20'].values; fb = d['fvg_bull'].values; fr = d['fvg_bear'].values
    disp = d['disp'].values; bc = d['bear_close'].values; uc = d['bull_close'].values
    lb = int(h['liq_lb']) if h['liq_ref'] == 'swing' else 20
    if h['liq_ref'] == 'swing':
        refH = d[f'rmax{lb}'].values; refL = d[f'rmin{lb}'].values
    elif h['liq_ref'] == 'session':
        refH = d['sess_high'].values; refL = d['sess_low'].values
    else:
        refH = d['pdh'].values; refL = d['pdl'].values
    side = h['side']; dirn = -1 if side == 'high' else 1; W = int(h['window']); n = len(d)
    sweep = ((hi > refH) & (cl < refH) & np.isfinite(refH)) if side == 'high' else ((lo < refL) & (cl > refL) & np.isfinite(refL))
    out = []; meta = []
    for t0 in np.flatnonzero(sweep):
        if confirm:
            conf = None
            for t1 in range(t0 + 1, min(t0 + W + 1, n)):
                k = h['confirm']
                ok = (disp[t1] > 0 and ((bc[t1] > 0) if dirn < 0 else (uc[t1] > 0))) if k == 'displacement' else \
                     ((cl[t1] < refL[t1]) if dirn < 0 else (cl[t1] > refH[t1])) if k == 'close_beyond' else \
                     ((bc[t1] > 0 and bc[t1 - 1] > 0) if dirn < 0 else (uc[t1] > 0 and uc[t1 - 1] > 0))
                if ok:
                    conf = t1; break
            if conf is None:
                continue
        else:
            conf = t0                                       # RAW: no confirmation, enter next bar
        if h['imb'] == 'fvg':
            has = (fr[t0:conf + 1].any()) if dirn < 0 else (fb[t0:conf + 1].any())
            if not has:
                continue
        ei = conf + 1
        stop = (hi[t0] + 2 * TICK) if dirn < 0 else (lo[t0] - 2 * TICK)
        if h['stop'] == 'structural':
            stop = (rmax[ei] + 2 * TICK) if dirn < 0 else (rmin[ei] - 2 * TICK)
        ek, ep = MS._exitmap(h['exit'], dirn, refL, refH, ei, rmax, rmin)
        out.append(dict(si=int(t0), ei=int(ei), dir=int(dirn), stop=float(stop), exit_kind=ek, exit_param=ep))
        meta.append(dict(t0=int(t0), conf=int(conf), ei=int(ei), delay=int(conf - t0)))
    return out, meta

# cont_setups: faithful reproduction of mstrat_ext.s39_setups with a `gate` toggle. gate=True MUST
# reproduce MSX.s39_setups(d,h) exactly (parity test). gate=False = the GATE-OFF arm: the identical
# expansion-continuation signal WITHOUT the trend-efficiency (er>=thr) condition. The gate is a SELECTION
# operator (it changes WHICH events, not entry timing), so the two arms are compared as subset-vs-superset.
def cont_setups(d, h, gate=True):
    c = d['close'].values; o = d['open'].values; hi = d['high'].values; lo = d['low'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; mtu = d['m_trend_up'].values; n = len(d)
    L = int(h['L']); thr = float(h['er_thr']); er = MSX._efficiency_ratio(c, L)
    rng = hi - lo; up = mtu > 0.5
    gate_up = (er >= thr) if gate else np.ones(n, dtype=bool)
    exp_up = (rng > 1.5 * atr) & (c > o) & up & gate_up
    exp_dn = (rng > 1.5 * atr) & (c < o) & (~up) & gate_up
    ev_up = exp_up & ~np.concatenate([[False], exp_up[:-1]])
    ev_dn = exp_dn & ~np.concatenate([[False], exp_dn[:-1]])
    # er finiteness gate: keep it identical to S39 (which filters np.isfinite(er)); with gate OFF we still
    # require finite er so the ONLY difference vs treatment is the er>=thr threshold, nothing else.
    out = []
    for t in np.flatnonzero((ev_up | ev_dn) & np.isfinite(er) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if ev_up[t] else -1; ei = t + 1
        if h['stop'] == 'swing':
            stop = (r20n[ei] - 2 * TICK) if dirn > 0 else (r20x[ei] + 2 * TICK)
        else:
            stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = MS._exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=int(ei), dir=int(dirn), stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# ============================== EXECUTION WRAPPER (always MS.simulate) ==============================
def sim_R(seg, setups):
    """Route setups through the FROZEN engine and return (R_array, si_array). No execution logic here."""
    if not setups:
        return np.array([]), np.array([], dtype=int)
    tr = MS.simulate(seg, setups, CFG)
    return tr['R'].values.astype(float), tr['si'].values.astype(int)

# ============================== CONTRAST 1: paired timing (EXP-01) ==============================
def paired_timing_contrast(seg, R_treat, si_treat, R_ctrl, si_ctrl, B, seed, margin):
    """Pair treatment (confirmed) vs control (raw) on the sweep events (si=t0) EXECUTED in BOTH arms —
    robust to the engine's overlap suppression differing between arms. H0: mean(treat-ctrl) <= margin
    (one-sided). Null = sign-flip permutation of the per-event difference (exchangeable arm labels)."""
    mt = {int(s): r for s, r in zip(si_treat, R_treat)}
    mc = {int(s): r for s, r in zip(si_ctrl, R_ctrl)}
    common = sorted(set(mt) & set(mc))
    d = np.array([mt[s] - mc[s] for s in common], dtype=float)
    k = len(d)
    if k < PREREG['min_trades']:
        return dict(paired_n=k, delta=float(np.mean(d)) if k else float('nan'), p=None, ci=(None, None),
                    note='paired_n<min_trades')
    obs = float(np.mean(d)) - margin
    rng = np.random.default_rng(seed)
    signs = rng.integers(0, 2, size=(B, k)) * 2 - 1
    perm_means = (signs * (d - margin)).mean(axis=1)
    k_ge = int(np.sum(perm_means >= obs)); p = (k_ge + 1) / (B + 1)
    # percentile bootstrap CI on the effect Delta itself (for the CI-straddle status rule)
    bidx = rng.integers(0, k, size=(min(B, 10000), k))
    boot = d[bidx].mean(axis=1)
    delta_ci = (float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975)))
    return dict(paired_n=k, delta=float(np.mean(d)), delta_minus_margin=obs, p=float(p), k_ge=k_ge, B=B,
                p_ci=_wilson(k_ge, B), delta_ci=delta_ci,
                mean_treat=float(np.mean([mt[s] for s in common])),
                mean_ctrl=float(np.mean([mc[s] for s in common])))

# ============================== CONTRAST 2: selection null (EXP-02) ==============================
def selection_contrast(R_on, R_off_all, B, seed, margin):
    """Gate-ON is a SUBSET of gate-OFF. H0: the gated subset's mean expectancy is not above what a random
    subset of the same size drawn from the ungated population would give (i.e. the gate does not select
    better-than-random events; equivalently gated <= gate-off). Null = random size-n_on subsets of R_off_all."""
    n_on = len(R_on); n_off = len(R_off_all)
    if n_on < PREREG['min_trades'] or n_off < PREREG['min_trades'] or n_on > n_off:
        return dict(n_on=n_on, n_off=n_off, delta=float('nan'), p=None, ci=(None, None), note='n gate')
    obs = float(np.mean(R_on)) - margin
    rng = np.random.default_rng(seed)
    Roff = np.asarray(R_off_all, dtype=float)
    means = np.empty(B)
    for bnum in range(B):
        idx = rng.choice(n_off, size=n_on, replace=False)
        means[bnum] = Roff[idx].mean()
    k_ge = int(np.sum(means >= obs)); p = (k_ge + 1) / (B + 1)
    # bootstrap CI on the gated-subset mean (vs the ungated mean, which is fixed) for the straddle rule
    Ron = np.asarray(R_on, dtype=float)
    bidx = rng.integers(0, n_on, size=(min(B, 10000), n_on))
    boot_on = Ron[bidx].mean(axis=1)
    on_ci = (float(np.quantile(boot_on, 0.025)), float(np.quantile(boot_on, 0.975)))
    return dict(n_on=n_on, n_off=n_off, mean_on=float(np.mean(R_on)), mean_off=float(np.mean(Roff)),
                delta=float(np.mean(R_on) - np.mean(Roff)), p=float(p), k_ge=k_ge, B=B, p_ci=_wilson(k_ge, B),
                mean_on_ci=on_ci, null_mean=float(means.mean()),
                null_q=[float(np.quantile(means, q)) for q in (0.5, 0.95, 0.99)])

# ============================== CONTRAST 3: beta/regime-matched null (EXP-03/04) ==============================
def matched_contrast(seg, setups, B, seed, strata):
    """Observed vs a null matched on trade direction + realised (risk/ATR, exit) profile + (optionally)
    session/vol/trend regime, via the VALIDATED engine MN.matched_null_p. strata=None reproduces the
    calibration-validated unstratified config; strata=[...] is the beta/regime-matched (diagnostic) null."""
    rec = MN.matched_null_p(seg, setups, cfg=CFG, B=B, seed=seed, strata=strata, min_k=PREREG['min_trades'])
    return rec

# ============================== CONTRAST 4: level-label-shuffle placebo (EXP-05/06) ==============================
def _day_index(seg):
    return (seg['time'].values // 86400).astype(np.int64)

def placebo_level_frame(seg, ref_cols, seed, window_days):
    """Return a COPY of seg with ref_cols (e.g. pdh,pdl) replaced by a level-label shuffle that:
      PRESERVES  daily persistence (level constant within a day), the level's relative distance from
                 price (transplanted from a donor day), and hence signal geometry/frequency;
      DESTROYS   the economic identity of the level (it is a NEARBY OTHER day's level, not this day's).
    Donor day drawn uniformly from +/- window_days around each day (proximity => same price regime =>
    frequency preserved). Anchor = the day's first-bar close (the realtime price when the level activates).
    Frozen, seeded, lookahead-neutral (this is a negative control, not a tradable signal)."""
    seg2 = seg.copy()
    days = _day_index(seg)
    uniq = np.unique(days)
    day_first = {int(dd): int(np.flatnonzero(days == dd)[0]) for dd in uniq}
    close = seg['close'].values
    rng = np.random.default_rng(seed)
    # donor day per day (uniform in a local window, excluding self)
    donor = {}
    for dd in uniq:
        lo = np.searchsorted(uniq, dd - window_days, 'left'); hi = np.searchsorted(uniq, dd + window_days, 'right')
        cand = uniq[lo:hi]; cand = cand[cand != dd]
        donor[int(dd)] = int(rng.choice(cand)) if len(cand) else int(dd)
    for col in ref_cols:
        real = seg[col].values.astype(float)
        fake = real.copy()
        for dd in uniq:
            i0 = day_first[int(dd)]; dj = donor[int(dd)]; j0 = day_first[dj]
            # transplant donor's level-relative-to-its-anchor onto this day's anchor -> same distance geometry
            offset = real[j0] - close[j0]
            fake[days == dd] = close[i0] + offset
        seg2[col] = fake
    return seg2

def label_shuffle_placebo(seg, setup_fn, ref_cols, K, seed, window_days):
    """Real vs K shuffled-level replicates. setup_fn(frame)->setups. H0 (placebo): shuffled ~ real.
    p = P(shuffled_mean >= real_mean). Small p => real >> shuffled => the level identity carries the edge."""
    R_real, _ = sim_R(seg, setup_fn(seg))
    real = metrics_R(R_real)
    if real['n'] < PREREG['min_trades']:
        return dict(real=real, K=K, p=None, ci=(None, None), shuffled_means=[], shuffled_ns=[], note='real n<min_trades')
    rng = np.random.default_rng(seed)
    seeds = rng.integers(0, 2**31 - 1, size=K)
    sh_means = []; sh_ns = []
    for s in seeds:
        segS = placebo_level_frame(seg, ref_cols, int(s), window_days)
        Rs, _ = sim_R(segS, setup_fn(segS))
        sh_means.append(float(np.mean(Rs)) if len(Rs) else float('nan')); sh_ns.append(int(len(Rs)))
    sh = np.array([m for m in sh_means if np.isfinite(m)])
    Keff = len(sh)
    # upper tail p (does REAL exceed shuffled? -> level carries the edge) and lower tail p_low (is REAL
    # significantly WORSE than shuffled? -> level identity actively hurts -> contradicts the positive claim).
    k_ge = int(np.sum(sh >= real['exp'])); p = (k_ge + 1) / (Keff + 1) if Keff else None
    k_le = int(np.sum(sh <= real['exp'])); p_low = (k_le + 1) / (Keff + 1) if Keff else None
    return dict(real=real, K=K, Keff=Keff, p=(float(p) if p is not None else None), k_ge=k_ge,
                p_low=(float(p_low) if p_low is not None else None), k_le=k_le,
                ci=_wilson(k_ge, Keff) if Keff else (None, None),
                shuffled_mean_of_means=float(sh.mean()) if Keff else float('nan'),
                shuffled_n_median=float(np.median(sh_ns)) if sh_ns else float('nan'),
                real_n=real['n'], freq_ratio=(float(np.median(sh_ns)) / real['n']) if real['n'] else float('nan'))

# ============================== MULTIPLICITY (Wave-1 family-wise; NOT global S1-S51 FDR) ==============================
def holm_bonferroni(pvals):
    """Holm-Bonferroni step-down FWER control across the Wave-1 primary p's. Returns adjusted p's aligned
    to input order. This is the pre-registered Wave-1 correction; the global S1-S51 FDR is NOT run here."""
    items = [(i, p) for i, p in enumerate(pvals) if p is not None]
    m = len(items)
    adj = [None] * len(pvals)
    order = sorted(items, key=lambda x: x[1])
    running = 0.0
    for rank, (i, p) in enumerate(order):
        a = min(1.0, (m - rank) * p)
        running = max(running, a)                          # enforce monotonicity
        adj[i] = running
    return adj

def bh_fdr(pvals, q=0.10):
    """Benjamini-Hochberg FDR across the Wave-1 primary p's (SECONDARY report only)."""
    items = [(i, p) for i, p in enumerate(pvals) if p is not None]
    m = len(items); passed = {i: False for i, _ in items}
    order = sorted(items, key=lambda x: x[1])
    kmax = -1
    for rank, (i, p) in enumerate(order, start=1):
        if p <= rank / m * q:
            kmax = rank
    for rank, (i, p) in enumerate(order, start=1):
        if rank <= kmax:
            passed[i] = True
    return [passed.get(i, None) for i in range(len(pvals))]
