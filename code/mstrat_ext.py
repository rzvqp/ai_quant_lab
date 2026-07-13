"""STRATEGY FAMILY EXTENSION S21-S40 (branch family-implementation-s21-s40).
NEW families ONLY. Reuses the OFFICIAL engine unchanged: MS.simulate (execution + v2 stop-floor + costs +
overlap), MS.load (feature frame), MS._grid (grammar), MS._exitmap (exit mapping), MS.CFG, MS.TICK.
mstrat.py is FROZEN (byte-identical to baseline 1bc0ffb) — this module does NOT modify the engine, the
screen, the pipeline, or S1-S20. Each family provides grammar()+setups(d,h)->[setup dicts] exactly like
S1-S20; execution is always MS.simulate. Lookahead-safe (entry at bar-open AFTER the signal).
See docs/STRATEGY_FAMILY_LIBRARY_S21_S40.md for the mechanism designs."""
import numpy as np, pandas as pd
import mstrat as MS
TICK = MS.TICK
_grid = MS._grid
_exitmap = MS._exitmap

# =====================================================================================
# S21 — Equal-highs / equal-lows liquidity-pool RAID (Class I, resting liquidity, refined)
# Mechanism: breakout/stop orders pool at CLUSTERS of equal highs/lows (a level tested >=2x).
# Larger players push through the pool to fill, then price reverses. Distinct from S1 (single sweep):
# S21 REQUIRES a multi-touch pool (min_touches) before the raid — a stronger, rarer signal.
# =====================================================================================
S21_DIMS = dict(side=['high', 'low'], lb=[20, 50], min_touches=[2, 3],
                stop=['beyond_raid', 'structural'], exit=['rr2', 'rr3', 'time'])
def s21_grammar(): return _grid('S21', S21_DIMS)
def s21_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values
    lb = int(h['lb']); side = h['side']; dirn = -1 if side == 'high' else 1
    lvl = d[f'rmax{lb}'].values if side == 'high' else d[f'rmin{lb}'].values  # prior rolling extreme (lookahead-safe)
    tol = 0.20; M = 20; mt = int(h['min_touches']); n = len(d)
    # a bar "tags" the resting level if its extreme comes within tol*ATR of the prior rolling extreme
    if side == 'high':
        tag = (hi >= lvl - tol * atr) & np.isfinite(lvl) & np.isfinite(atr)
    else:
        tag = (lo <= lvl + tol * atr) & np.isfinite(lvl) & np.isfinite(atr)
    touches = pd.Series(tag.astype(float)).rolling(M).sum().shift(1).values  # prior touches only
    # raid + rejection: sweep beyond the pooled level, then close back inside
    if side == 'high':
        raid = (hi > lvl) & (cl < lvl)
    else:
        raid = (lo < lvl) & (cl > lvl)
    sig = raid & (touches >= mt) & np.isfinite(lvl) & np.isfinite(atr) & (atr > 0)
    out = []
    for t in np.flatnonzero(sig):
        if t >= n - 1 or t < 1:
            continue
        ei = t + 1
        stop = (hi[t] + 2 * TICK) if dirn < 0 else (lo[t] - 2 * TICK)          # beyond the raid extreme
        if h['stop'] == 'structural':
            stop = (r20x[ei] + 2 * TICK) if dirn < 0 else (r20n[ei] - 2 * TICK)
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# =====================================================================================
# S23 — Squeeze breakout WITH higher-timeframe directional filter (Class II)  [REDESIGN of failed S4]
# Mechanism: volatility compresses then expands (vol mean-reversion). S4 failed because expansion DIRECTION
# was random. Fix: take the squeeze breakout ONLY in the direction of the HTF trend (h4/h1). Loser = premium
# sellers / range faders caught at the regime change.
# =====================================================================================
S23_DIMS = dict(htf=['h4', 'h1'], min_sq=[3, 6], stop=['range_opp', 'atr'], exit=['rr2', 'rr3', 'trailing', 'time'])
def s23_grammar(): return _grid('S23', S23_DIMS)
def s23_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    comp = d['compress'].values; htf = d[h['htf'] + '_trend_up'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d); ms = int(h['min_sq'])
    sq_on = pd.Series(comp).rolling(ms).sum().shift(1).values >= ms         # sustained prior compression
    sq_hi = pd.Series(hi).rolling(ms).max().shift(1).values                 # squeeze range (prior)
    sq_lo = pd.Series(lo).rolling(ms).min().shift(1).values
    up = htf > 0.5
    long_brk = sq_on & (cl > sq_hi) & up
    short_brk = sq_on & (cl < sq_lo) & (~up)
    out = []
    for t in np.flatnonzero((long_brk | short_brk) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if long_brk[t] else -1; ei = t + 1
        stop = (sq_lo[t] - 2 * TICK) if dirn > 0 else (sq_hi[t] + 2 * TICK)   # opposite side of squeeze range
        if h['stop'] == 'atr':
            stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# =====================================================================================
# S26 — Developing value-area rejection / acceptance (Class III, auction/value)
# Mechanism: price spends most time inside a value area; excursions beyond the VA edge are either REJECTED
# (revert to value = fade) or ACCEPTED (value migrates = follow). Institutions anchor to value. VA proxy =
# session VWAP +/- k*rolling-sigma. Distinct from S8 (SMA/VWAP point + ATR extension) and S12 (raw range).
# =====================================================================================
# k = sigma-multiple for the value-area edge. 1.0 excluded: +/-1sigma IS the value area (~70%), so a 1sigma
# "excursion" is inside value and fails the discrete-setup selectivity gate. k>=2 = genuinely beyond value.
S26_DIMS = dict(mode=['reject', 'accept'], k=[2.0, 3.0], stop=['atr', 'edge'], exit=['rr2', 'rr3', 'vwap', 'time'])
def s26_grammar(): return _grid('S26', S26_DIMS)
def s26_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    vwap = d['vwap'].values; sd = d['m_std'].values; r20x = d['rmax20'].values; r20n = d['rmin20'].values
    k = float(h['k']); n = len(d); mode = h['mode']
    va_hi = vwap + k * sd; va_lo = vwap - k * sd
    if mode == 'reject':                                   # ONSET of excursion beyond edge, close back inside -> fade
        lraw = (lo < va_lo) & (cl > va_lo); sraw = (hi > va_hi) & (cl < va_hi)
        longsig = lraw & ~np.concatenate([[False], lraw[:-1]])
        shortsig = sraw & ~np.concatenate([[False], sraw[:-1]])
    else:                                                  # acceptance: close beyond the edge -> follow (onset only)
        lc = (cl > va_hi); sc = (cl < va_lo)
        longsig = lc & ~np.concatenate([[False], lc[:-1]])
        shortsig = sc & ~np.concatenate([[False], sc[:-1]])
    out = []
    for t in np.flatnonzero((longsig | shortsig) & np.isfinite(vwap) & np.isfinite(sd) & (sd > 0) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if longsig[t] else -1; ei = t + 1
        if h['stop'] == 'edge':
            stop = (lo[t] - 2 * TICK) if dirn > 0 else (hi[t] + 2 * TICK)
        else:
            stop = o[ei] - dirn * 1.5 * atr[t]
        ex = h['exit']
        if ex == 'vwap' and mode == 'reject':
            ek, ep = 'opp_struct', float(vwap[ei])         # revert to value (VWAP) as target
        elif ex == 'vwap':                                 # acceptance has no revert target -> default rr2
            ek, ep = 'rr', 2.0
        else:
            ek, ep = _exitmap(ex, dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# =====================================================================================
# S38 — Patient pullback-into-zone entry (Class VII)  [REDESIGN of failed S7/S10]
# Mechanism: in an established HTF trend, ENTER when price pulls back into a discount zone (EMA / mid-range),
# WITHOUT waiting for a confirmation close. S7/S10 failed by waiting for confirmation -> late, poor fill.
# Edge source = better fill than the market-order-on-confirmation crowd + trend persistence.
# NOTE: the official engine fills market-on-next-open (no limit orders), so this enters at the open of the bar
# after the zone is first touched — an approximation of a true limit fill (documented limitation).
# =====================================================================================
S38_DIMS = dict(htf=['h4', 'h1'], zone=['ema20', 'ema50', 'fib50'], stop=['swing', 'atr'], exit=['rr2', 'rr3', 'trailing'])
def s38_grammar(): return _grid('S38', S38_DIMS)
def s38_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; o = d['open'].values; atr = d['m_atr'].values
    ema20 = d['m_ema20'].values; ema50 = d['m_ema50'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; htf = d[h['htf'] + '_trend_up'].values; n = len(d)
    if h['zone'] == 'ema20':   lvl = ema20
    elif h['zone'] == 'ema50': lvl = ema50
    else:                      lvl = r20x - 0.5 * (r20x - r20n)          # mid of recent range (fib-0.5 proxy)
    up = htf > 0.5
    touch_long = up & (lo <= lvl)                                        # uptrend pullback DOWN into zone
    touch_short = (~up) & (hi >= lvl)                                    # downtrend pullback UP into zone
    onset_long = touch_long & ~np.concatenate([[False], touch_long[:-1]])
    onset_short = touch_short & ~np.concatenate([[False], touch_short[:-1]])
    out = []
    for t in np.flatnonzero((onset_long | onset_short) & np.isfinite(lvl) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if onset_long[t] else -1; ei = t + 1
        if h['stop'] == 'swing':
            stop = (r20n[ei] - 2 * TICK) if dirn > 0 else (r20x[ei] + 2 * TICK)
        else:
            stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

def _efficiency_ratio(c, L):
    """Kaufman efficiency ratio: |net move| / sum|per-bar move| over L bars (prior-inclusive, known at close t)."""
    net = np.abs(c - np.concatenate([np.full(L, np.nan), c[:-L]]))
    vol = pd.Series(np.abs(np.diff(c, prepend=c[0]))).rolling(L).sum().values
    with np.errstate(divide='ignore', invalid='ignore'):
        er = np.where(vol > 0, net / vol, np.nan)
    return er

# =====================================================================================
# S39 — Trend-efficiency-gated continuation (Class VII)  [REDESIGN of failed S15]
# Mechanism: S15 bought raw acceleration (bought local tops). Fix: take continuation ONLY when the trend is
# CLEAN (high Kaufman efficiency ratio = net move / path length), which empirically predicts persistence;
# skip noisy chop. Loser = counter-trend faders in efficient trends.
# =====================================================================================
S39_DIMS = dict(L=[10, 20], er_thr=[0.3, 0.5], stop=['atr', 'swing'], exit=['rr2', 'rr3', 'trailing'])
def s39_grammar(): return _grid('S39', S39_DIMS)
def s39_setups(d, h):
    c = d['close'].values; o = d['open'].values; hi = d['high'].values; lo = d['low'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; mtu = d['m_trend_up'].values; n = len(d)
    L = int(h['L']); thr = float(h['er_thr']); er = _efficiency_ratio(c, L)
    rng = hi - lo; up = mtu > 0.5
    # expansion-continuation bar (like S15) but GATED by trend efficiency
    exp_up = (rng > 1.5 * atr) & (c > o) & up & (er >= thr)
    exp_dn = (rng > 1.5 * atr) & (c < o) & (~up) & (er >= thr)
    ev_up = exp_up & ~np.concatenate([[False], exp_up[:-1]])
    ev_dn = exp_dn & ~np.concatenate([[False], exp_dn[:-1]])
    out = []
    for t in np.flatnonzero((ev_up | ev_dn) & np.isfinite(er) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if ev_up[t] else -1; ei = t + 1
        if h['stop'] == 'swing':
            stop = (r20n[ei] - 2 * TICK) if dirn > 0 else (r20x[ei] + 2 * TICK)
        else:
            stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# =====================================================================================
# S40 — Regime router (Class VIII, meta)  [addresses S11/S12 regime-blind failures]
# Mechanism: deploy each sub-edge ONLY where its mechanism holds. Classify regime by trend efficiency:
#   TREND regime (ER>=thr) -> efficient continuation (buy expansion in trend dir, like S39).
#   RANGE regime (ER<thr)  -> mean-reversion (fade rolling extremes back toward the middle, like S12 but
#                             conditioned on actually being in a range). Loser depends on the sub-edge.
# =====================================================================================
S40_DIMS = dict(er_thr=[0.3, 0.5], range_lb=[20, 50], stop=['atr', 'swing'], exit=['rr2', 'rr3'])
def s40_grammar(): return _grid('S40', S40_DIMS)
def s40_setups(d, h):
    c = d['close'].values; o = d['open'].values; hi = d['high'].values; lo = d['low'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; mtu = d['m_trend_up'].values; n = len(d)
    thr = float(h['er_thr']); lb = int(h['range_lb']); er = _efficiency_ratio(c, 20)
    rmx = d[f'rmax{lb}'].values; rmn = d[f'rmin{lb}'].values
    trend = er >= thr; rng = ~trend
    up = mtu > 0.5; bar = hi - lo
    # trend regime: efficient continuation (expansion bar in trend direction)
    tc_up = trend & up & (bar > 1.5 * atr) & (c > o)
    tc_dn = trend & (~up) & (bar > 1.5 * atr) & (c < o)
    # range regime: fade rolling extremes back to middle
    rf_up = rng & (lo < rmn) & (c > rmn)          # dip below range low, close back -> long
    rf_dn = rng & (hi > rmx) & (c < rmx)          # poke above range high, close back -> short
    long_ev = (tc_up | rf_up); short_ev = (tc_dn | rf_dn)
    onL = long_ev & ~np.concatenate([[False], long_ev[:-1]])
    onS = short_ev & ~np.concatenate([[False], short_ev[:-1]])
    out = []
    for t in np.flatnonzero((onL | onS) & np.isfinite(er) & np.isfinite(atr) & (atr > 0) & np.isfinite(rmn)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if onL[t] else -1; ei = t + 1; is_range = rng[t]
        if h['stop'] == 'swing':
            stop = (r20n[ei] - 2 * TICK) if dirn > 0 else (r20x[ei] + 2 * TICK)
        else:
            stop = o[ei] - dirn * 1.5 * atr[t]
        if is_range:                                  # range fade -> target the middle of the range
            mid = (rmx[t] + rmn[t]) / 2.0
            ek, ep = 'opp_struct', float(mid)
        else:
            ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# ------------- extension registry (mirrors MS.REGISTRY shape) -------------
EXT_REGISTRY = {
    'S21': (s21_grammar, s21_setups),
    'S23': (s23_grammar, s23_setups),
    'S26': (s26_grammar, s26_setups),
    'S38': (s38_grammar, s38_setups),
    'S39': (s39_grammar, s39_setups),
    'S40': (s40_grammar, s40_setups),
}
EXT_ECON = {
    'S21': 'equal-highs/lows liquidity-pool raid',
    'S23': 'squeeze breakout + HTF filter',
    'S26': 'value-area rejection/acceptance',
    'S38': 'patient pullback-into-zone (trend continuation)',
    'S39': 'trend-efficiency-gated continuation',
    'S40': 'regime router (trend-continuation / range-reversion)',
}
def ext_setups(d, h): return EXT_REGISTRY[h['family']][1](d, h)
def ext_backtest(d, h): return MS.simulate(d, EXT_REGISTRY[h['family']][1](d, h), MS.CFG)
