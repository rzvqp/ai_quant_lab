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

# =====================================================================================
# ================================  TIER B  (existing data, T0)  ======================
# =====================================================================================

# S22 — Round-number magnet / rejection (Class I). Psychological $ levels attract limit orders/stops;
# reactions (reject) and clean breaks. Objective levels = price rounded to $step.
# step 10/25 excluded on SELECTIVITY grounds (not PnL): at gold ~$2000-4000, $10-$25 is 0.3-0.6% -> tagged
# every few bars (non-selective). $50/$100 are the meaningful psychological round levels here.
S22_DIMS = dict(step=[50, 100], mode=['reject', 'breakout'], stop=['atr', 'level'], exit=['rr2', 'rr3', 'time'])
def s22_grammar(): return _grid('S22', S22_DIMS)
def s22_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; step = float(h['step']); n = len(d)
    lvl_up = np.ceil(cl / step) * step; lvl_dn = np.floor(cl / step) * step
    if h['mode'] == 'reject':
        s_raw = (hi >= lvl_up) & (cl < lvl_up)                    # tested round resistance, rejected -> short
        l_raw = (lo <= lvl_dn) & (cl > lvl_dn)                    # tested round support, rejected -> long
    else:  # breakout = the integer band floor(close/step) changes between bars (crossed a round level)
        fl = np.floor(cl / step); fl_prev = np.concatenate([[np.nan], fl[:-1]])
        l_raw = fl > fl_prev                                     # crossed UP through a round level
        s_raw = fl < fl_prev                                     # crossed DOWN through a round level
    longsig = l_raw & ~np.concatenate([[False], l_raw[:-1]]); shortsig = s_raw & ~np.concatenate([[False], s_raw[:-1]])
    out = []
    for t in np.flatnonzero((longsig | shortsig) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if longsig[t] else -1; ei = t + 1; lvl = lvl_dn[t] if dirn > 0 else lvl_up[t]
        stop = (o[ei] - dirn * 1.5 * atr[t]) if h['stop'] == 'atr' else ((lvl - 2 * TICK) if dirn > 0 else (lvl + 2 * TICK))
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S24 — Overnight variance / session carry (Class IV). Does the PRIOR session's structure condition the next?
# At the target session's early bar, take a carry/fade bias from where the prior session closed in its range.
S24_DIMS = dict(sess=['london', 'ny'], mode=['carry', 'fade'], entry_bar=[1, 2], exit=['rr2', 'rr3', 'time'])
def s24_grammar(): return _grid('S24', S24_DIMS)
def s24_setups(d, h):
    o = d['open'].values; atr = d['m_atr'].values; bis = d['bar_in_sess'].values; sess = d['session'].values
    psh = d['prev_sess_high'].values; psl = d['prev_sess_low'].values; psc = d['prev_sess_close'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d); eb = int(h['entry_bar'])
    mid = (psh + psl) / 2.0; bias_up = psc > mid                  # prior session closed in upper half
    trig = (sess == h['sess']) & (bis == eb) & np.isfinite(mid)
    out = []
    for t in np.flatnonzero(trig & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        bu = bool(bias_up[t]); dirn = (1 if bu else -1) if h['mode'] == 'carry' else (-1 if bu else 1)
        ei = t + 1; stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S25 — Volatility-regime ONSET (Class II). Trades the TRANSITION (m_atr vs atr_ma crossing), NOT a squeeze
# breakout (distinct from S23): expand-onset -> momentum in the move's direction; contract-onset -> revert to mean.
S25_DIMS = dict(mode=['expand', 'contract'], stop=['atr', 'swing'], exit=['rr2', 'rr3', 'time'])
def s25_grammar(): return _grid('S25', S25_DIMS)
def s25_setups(d, h):
    cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values; ama = d['atr_ma'].values
    sma = d['m_sma'].values; roc = d['roc3'].values; r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d)
    high_vol = atr > ama
    if h['mode'] == 'expand':
        ons = high_vol & ~np.concatenate([[False], high_vol[:-1]])   # low->high vol onset
    else:
        ons = (~high_vol) & np.concatenate([[False], high_vol[:-1]])  # high->low vol onset
    out = []
    for t in np.flatnonzero(ons & np.isfinite(atr) & (atr > 0) & np.isfinite(ama)):
        if t >= n - 1 or t < 1:
            continue
        if h['mode'] == 'expand':
            dirn = 1 if roc[t] > 0 else -1                            # ride the move that spiked vol
        else:
            dirn = -1 if (cl[t] > sma[t]) else 1                      # revert toward mean as vol calms
        ei = t + 1
        stop = (o[ei] - dirn * 1.5 * atr[t]) if h['stop'] == 'atr' else ((r20n[ei] - 2 * TICK) if dirn > 0 else (r20x[ei] + 2 * TICK))
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S27 — VWAP reclaim in trend (Class III). Distinct from S26 (value-area excursion): S27 trades the RECLAIM of
# session VWAP in the HTF trend direction (mean-revert to VWAP then continue). Lookahead-safe (vwap known at close t).
S27_DIMS = dict(htf=['h4', 'h1'], band_k=[1.0, 2.0], stop=['atr', 'vwap'], exit=['rr2', 'rr3', 'time'])
def s27_grammar(): return _grid('S27', S27_DIMS)
def s27_setups(d, h):
    cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values; vwap = d['vwap'].values; sd = d['m_std'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; htf = d[h['htf'] + '_trend_up'].values; n = len(d); bk = float(h['band_k'])
    up = htf > 0.5; above = cl > vwap
    recl_long = up & above & ~np.concatenate([[False], above[:-1]])       # uptrend, close reclaims above VWAP
    below = cl < vwap
    recl_short = (~up) & below & ~np.concatenate([[False], below[:-1]])   # downtrend, close breaks below VWAP
    out = []
    for t in np.flatnonzero((recl_long | recl_short) & np.isfinite(vwap) & np.isfinite(sd) & (sd > 0) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if recl_long[t] else -1; ei = t + 1
        stop = (o[ei] - dirn * 1.5 * atr[t]) if h['stop'] == 'atr' else float(vwap[t] - dirn * 0.25 * sd[t])
        ex = h['exit']
        if ex == 'time':
            ek, ep = 'time', 24
        else:
            ek, ep = 'opp_struct', float(vwap[ei] + dirn * bk * sd[ei])   # target the far VWAP band
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

def _anchored_vwap(d, anchor):
    tp = (d['high'].values + d['low'].values + d['close'].values) / 3; vol = d['volume'].values.astype(float); t = d['time'].values
    if anchor == 'day':
        seg = (t // 86400)
    elif anchor == 'week':
        seg = ((t - 345600) // 604800)                                    # epoch 0 = Thursday; shift to Monday weeks
    elif anchor == 'month':
        dt = pd.to_datetime(t, unit='s', utc=True)
        seg = (dt.year * 12 + dt.month).values
    elif anchor == 'swing':
        r20x = d['rmax20'].values; r20n = d['rmin20'].values; cl = d['close'].values
        seg = np.cumsum(((cl > r20x) | (cl < r20n)).astype(int))          # new anchor at each structure break
    else:  # impulse
        seg = np.cumsum((d['disp'].values > 0.5).astype(int))             # new anchor at each displacement bar
    seg = pd.Series(seg)
    cpv = pd.Series(tp * vol).groupby(seg).cumsum(); cv = pd.Series(vol).groupby(seg).cumsum().replace(0, np.nan)
    return (cpv / cv).values

# S28 — Anchored VWAP reaction (Class III). Objective, time-available anchors. day/swing/impulse EXCLUDED on
# selectivity grounds (not PnL): they reset so often the anchored VWAP hugs price (av crosses price every few
# bars -> non-selective) and does not form a stable institutional cost basis on M15. week/month are stable.
S28_DIMS = dict(anchor=['week', 'month'], mode=['reclaim', 'bounce'], exit=['rr2', 'rr3', 'time'])
def s28_grammar(): return _grid('S28', S28_DIMS)
def s28_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; av = _anchored_vwap(d, h['anchor']); n = len(d)
    # a REACTION requires a genuine prior DEPARTURE from the anchor (not micro-oscillation): price must have
    # been >= 0.75*ATR away from the anchored VWAP within the last 8 bars. This is the definition of a retest.
    dist = np.abs(cl - av) / np.where(atr > 0, atr, np.nan)
    departed = pd.Series(dist).rolling(8).max().shift(1).values >= 0.75
    above = cl > av
    if h['mode'] == 'reclaim':
        l_raw = above & ~np.concatenate([[False], above[:-1]]); s_raw = (~above) & np.concatenate([[False], above[:-1]])
    else:  # bounce: tag anchor and hold on the same side (support/resistance)
        l_raw = (lo <= av) & (cl > av); s_raw = (hi >= av) & (cl < av)
        l_raw = l_raw & ~np.concatenate([[False], l_raw[:-1]]); s_raw = s_raw & ~np.concatenate([[False], s_raw[:-1]])
    l_raw = l_raw & departed; s_raw = s_raw & departed
    out = []
    for t in np.flatnonzero((l_raw | s_raw) & np.isfinite(av) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if l_raw[t] else -1; ei = t + 1; stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

def _dt(d): return pd.to_datetime(d['time'].values, unit='s', utc=True)
def _new_day(d):
    date = d['time'].values // 86400
    return date != np.concatenate([[date[0] - 1], date[:-1]])

# S29 — Day-of-week effect (Class IV). Enter at each day's first bar on a given weekday, directional; hold.
# Bounded grammar (5 weekdays x 2 sides) — multiple-testing acknowledged, to be FDR-controlled later.
S29_DIMS = dict(dow=[0, 1, 2, 3, 4], side=['up', 'down'], exit=['rr2', 'time'])
def s29_grammar(): return _grid('S29', S29_DIMS)
def s29_setups(d, h):
    o = d['open'].values; atr = d['m_atr'].values; r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d)
    wd = _dt(d).dayofweek.values; nd = _new_day(d); dirn = 1 if h['side'] == 'up' else -1
    trig = nd & (wd == int(h['dow']))
    out = []
    for t in np.flatnonzero(trig & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        ei = t + 1; stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S30 — Kill-zone / time-window effect (Class IV). Pre-registered UTC windows (London 07-10, NY 12-15);
# breakout of the prior 4-bar range DURING the window -> continuation or reversal. Fixed clock (not S5's
# session-open-relative range, not arbitrary optimized hours).
S30_DIMS = dict(zone=['london_kz', 'ny_kz'], mode=['continuation', 'reversal'], stop=['atr'], exit=['rr2', 'rr3', 'time'])
def s30_grammar(): return _grid('S30', S30_DIMS)
def s30_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; hour = _dt(d).hour.values; n = len(d)
    kz = (hour >= 7) & (hour < 10) if h['zone'] == 'london_kz' else (hour >= 12) & (hour < 15)
    rhi = pd.Series(hi).rolling(4).max().shift(1).values; rlo = pd.Series(lo).rolling(4).min().shift(1).values
    bu = kz & (cl > rhi); bd = kz & (cl < rlo)
    bu = bu & ~np.concatenate([[False], bu[:-1]]); bd = bd & ~np.concatenate([[False], bd[:-1]])
    out = []
    for t in np.flatnonzero((bu | bd) & np.isfinite(rhi) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        raw = 1 if bu[t] else -1; dirn = raw if h['mode'] == 'continuation' else -raw; ei = t + 1
        stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S31 — Month-end / month-start effect (Class IV). Fixed pre-registered windows around the month change:
# month_end = day-of-month >= 27; month_start = day-of-month <= 2. Enter at the day's first bar, directional.
S31_DIMS = dict(window=['month_end', 'month_start'], side=['up', 'down'], exit=['rr2', 'rr3', 'time'])
def s31_grammar(): return _grid('S31', S31_DIMS)
def s31_setups(d, h):
    o = d['open'].values; atr = d['m_atr'].values; r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d)
    dom = _dt(d).day.values; nd = _new_day(d); dirn = 1 if h['side'] == 'up' else -1
    inwin = (dom >= 27) if h['window'] == 'month_end' else (dom <= 2)
    trig = nd & inwin
    out = []
    for t in np.flatnonzero(trig & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        ei = t + 1; stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# =====================================================================================
# ============  MECHANISM-DIVERSITY BATCH 1 (S41-S46) — genuinely NEW ingredients  ====
# NEW classes not present in S1-S40: (A) volume MAGNITUDE, (B) short-term RETURN reversal,
# (C) momentum DIVERGENCE, (D) intrabar PRESSURE (order-flow proxy), (E) streak/sequence, (F) volume-gated breakout.
# =====================================================================================

# S41 — Volume-climax REVERSAL. NEW ingredient: volume MAGNITUDE (m_volrank). A participation spike at a price
# extreme = capitulation/blow-off; forced flow exhausts -> reversal. Differs from ALL S1-S40 (only VWAP used
# volume, never volume magnitude as a trigger) and from S14 exhaustion (which used ROC stall, not volume).
S41_DIMS = dict(vthr=[0.90, 0.95], stop=['bar', 'atr'], exit=['rr2', 'rr3', 'time'])
def s41_grammar(): return _grid('S41', S41_DIMS)
def s41_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    vr = d['m_volrank'].values; r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d); vt = float(h['vthr'])
    top = (vr >= vt) & (hi >= r20x)          # climactic volume at a 20-bar high -> blow-off top -> short
    bot = (vr >= vt) & (lo <= r20n)          # climactic volume at a 20-bar low  -> capitulation -> long
    top = top & ~np.concatenate([[False], top[:-1]]); bot = bot & ~np.concatenate([[False], bot[:-1]])
    out = []
    for t in np.flatnonzero((top | bot) & np.isfinite(atr) & (atr > 0) & np.isfinite(vr)):
        if t >= n - 1 or t < 1:
            continue
        dirn = -1 if top[t] else 1; ei = t + 1
        stop = ((hi[t] + 2 * TICK) if dirn < 0 else (lo[t] - 2 * TICK)) if h['stop'] == 'bar' else (o[ei] - dirn * 1.5 * atr[t])
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S42 — Short-term RETURN reversal (overreaction). NEW ingredient: return-magnitude ranking / serial dependence.
# The largest recent mover reverses (liquidity providers absorb overreaction). Differs from S8 (distance-from-
# SMA) — S42 uses the L-bar RETURN itself, the classic short-term-reversal anomaly, untested so far.
S42_DIMS = dict(L=[3, 6], thr=[0.006, 0.012], stop=['atr'], exit=['rr2', 'rr3', 'time'])
def s42_grammar(): return _grid('S42', S42_DIMS)
def s42_setups(d, h):
    c = d['close']; cl = c.values; o = d['open'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d); L = int(h['L']); thr = float(h['thr'])
    roc = (c / c.shift(L) - 1).values
    over = roc > thr; undr = roc < -thr        # overbought -> fade short ; oversold -> fade long
    short = over & ~np.concatenate([[False], over[:-1]]); long = undr & ~np.concatenate([[False], undr[:-1]])
    out = []
    for t in np.flatnonzero((short | long) & np.isfinite(roc) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if long[t] else -1; ei = t + 1; stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S43 — Momentum DIVERGENCE (RSI vs price). NEW ingredient: oscillator/price divergence. Price makes a new
# extreme while RSI does NOT -> momentum weakening -> reversal. Differs from S14 (ROC stall, no price-extreme
# reference) and from all level mechanisms — this is a divergence between price and an oscillator.
S43_DIMS = dict(rsi_tf=['m', 'h1'], lb=[14, 20], stop=['bar', 'atr'], exit=['rr2', 'time'])
def s43_grammar(): return _grid('S43', S43_DIMS)
def s43_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    rsi = d[('m_rsi' if h['rsi_tf'] == 'm' else 'h1_rsi')].values; lb = int(h['lb']); n = len(d)
    ph = pd.Series(hi).rolling(lb).max().shift(1).values; pl = pd.Series(lo).rolling(lb).min().shift(1).values
    rmaxv = pd.Series(rsi).rolling(lb).max().shift(1).values; rminv = pd.Series(rsi).rolling(lb).min().shift(1).values
    bear = (hi > ph) & (rsi < rmaxv)         # new price high but RSI below its recent high -> bearish divergence
    bull = (lo < pl) & (rsi > rminv)         # new price low but RSI above its recent low  -> bullish divergence
    bear = bear & ~np.concatenate([[False], bear[:-1]]); bull = bull & ~np.concatenate([[False], bull[:-1]])
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; out = []
    for t in np.flatnonzero((bear | bull) & np.isfinite(rsi) & np.isfinite(atr) & (atr > 0) & np.isfinite(ph)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if bull[t] else -1; ei = t + 1
        stop = ((hi[t] + 2 * TICK) if dirn < 0 else (lo[t] - 2 * TICK)) if h['stop'] == 'bar' else (o[ei] - dirn * 1.5 * atr[t])
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S44 — Intrabar PRESSURE / close-location (order-flow proxy from OHLC). NEW ingredient: intrabar buying/selling
# pressure via close-location-value CLV=((C-L)-(H-C))/(H-L). Persistent pressure -> continuation; extreme -> exhaust.
# Differs from all S1-S40 (none use intrabar close position as an order-flow proxy).
S44_DIMS = dict(N=[3, 5], mode=['continue', 'exhaust'], stop=['atr'], exit=['rr2', 'rr3', 'time'])
def s44_grammar(): return _grid('S44', S44_DIMS)
def s44_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    rng = np.where((hi - lo) > 0, hi - lo, np.nan); clv = ((cl - lo) - (hi - cl)) / rng
    N = int(h['N']); mclv = pd.Series(clv).rolling(N).mean().values; n = len(d)
    r20x = d['rmax20'].values; r20n = d['rmin20'].values
    strong_buy = mclv > 0.5; strong_sell = mclv < -0.5
    if h['mode'] == 'continue':
        lo_ev = strong_buy & ~np.concatenate([[False], strong_buy[:-1]]); sh_ev = strong_sell & ~np.concatenate([[False], strong_sell[:-1]])
        long_ev, short_ev = lo_ev, sh_ev
    else:  # exhaust: extreme buying pressure -> fade short, extreme selling -> fade long
        sh_ev = strong_buy & ~np.concatenate([[False], strong_buy[:-1]]); lo_ev = strong_sell & ~np.concatenate([[False], strong_sell[:-1]])
        long_ev, short_ev = lo_ev, sh_ev
    out = []
    for t in np.flatnonzero((long_ev | short_ev) & np.isfinite(mclv) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if long_ev[t] else -1; ei = t + 1; stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S45 — Consecutive-bar STREAK. NEW ingredient: sequential run-length. N consecutive same-direction closes ->
# reverse (overextension) or continue (momentum). Differs from all (none use raw close-streak length).
# k=3 excluded on selectivity grounds (pre-PnL): a 3-bar run occurs ~1/8 of bars = not an "extended" streak.
S45_DIMS = dict(k=[4, 5, 6], mode=['reverse', 'continue'], stop=['atr'], exit=['rr2', 'time'])
def s45_grammar(): return _grid('S45', S45_DIMS)
def s45_setups(d, h):
    c = d['close']; cl = c.values; o = d['open'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d); k = int(h['k'])
    up = (np.diff(cl, prepend=cl[0]) > 0).astype(int); dn = (np.diff(cl, prepend=cl[0]) < 0).astype(int)
    up_streak = pd.Series(up).groupby((up != pd.Series(up).shift()).cumsum()).cumsum().values * up
    dn_streak = pd.Series(dn).groupby((dn != pd.Series(dn).shift()).cumsum()).cumsum().values * dn
    up_ev = up_streak == k; dn_ev = dn_streak == k          # exactly k in a row (onset of the k-streak)
    out = []
    for t in np.flatnonzero((up_ev | dn_ev) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        base = 1 if up_ev[t] else -1                        # base direction of the streak
        dirn = -base if h['mode'] == 'reverse' else base; ei = t + 1; stop = o[ei] - dirn * 1.5 * atr[t]
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S46 — Volume-CONFIRMED breakout. NEW ingredient: participation gate on breakouts. Breakout of a level ONLY
# when volume expands (conviction). Directly tests whether VOLUME is the missing ingredient that made the
# volume-blind breakouts (S3/S23) fail. Differs from S3/S23 by the m_volrank confirmation.
S46_DIMS = dict(vthr=[0.70, 0.85], lb=[20, 50], stop=['level', 'atr'], exit=['rr2', 'rr3', 'trailing'])
def s46_grammar(): return _grid('S46', S46_DIMS)
def s46_setups(d, h):
    cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values; vr = d['m_volrank'].values
    lb = int(h['lb']); rmx = d[f'rmax{lb}'].values; rmn = d[f'rmin{lb}'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d); vt = float(h['vthr'])
    up = (cl > rmx) & (vr >= vt); dn = (cl < rmn) & (vr >= vt)
    up = up & ~np.concatenate([[False], up[:-1]]); dn = dn & ~np.concatenate([[False], dn[:-1]])
    out = []
    for t in np.flatnonzero((up | dn) & np.isfinite(rmx) & np.isfinite(atr) & (atr > 0) & np.isfinite(vr)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if up[t] else -1; ei = t + 1
        stop = ((rmn[t] - 2 * TICK) if dirn > 0 else (rmx[t] + 2 * TICK)) if h['stop'] == 'level' else (o[ei] - dirn * 1.5 * atr[t])
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# =====================================================================================
# ============  MECHANISM-DIVERSITY BATCH 2 (S47-S51)  ================================
# NEW ingredients: weekend gap, consolidation DURATION, narrowest-range pattern, engulfing, range-position.
# =====================================================================================

# S47 — Weekend-gap fill/continuation (Monday). NEW: weekend-specific gap (Fri-close -> Mon-open). Differs from
# S19 (intraday session gaps) — this is the weekend liquidity gap only.
S47_DIMS = dict(mode=['fill', 'continue'], thr=[0.3, 0.6], exit=['rr2', 'rr3', 'time'])
def s47_grammar(): return _grid('S47', S47_DIMS)
def s47_setups(d, h):
    o = d['open'].values; atr = d['m_atr'].values; gap = d['gap'].values; pc = d['prev_sess_close'].values
    bis = d['bar_in_sess'].values; r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d)
    wd = _dt(d).dayofweek.values; thr = float(h['thr'])
    mon_open = (wd == 0) & (bis == 0) & np.isfinite(gap)
    gu = mon_open & (gap > thr * atr); gd = mon_open & (gap < -thr * atr)
    out = []
    for t in np.flatnonzero((gu | gd) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        up_gap = bool(gu[t])
        dirn = (-1 if up_gap else 1) if h['mode'] == 'fill' else (1 if up_gap else -1); ei = t + 1
        stop = o[ei] - dirn * 1.5 * atr[t]
        if h['mode'] == 'fill':
            ek, ep = 'opp_struct', float(pc[t])         # fill targets the prior close
        else:
            ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S48 — Consolidation-DURATION breakout. NEW ingredient: TIME spent compressed (run-length of compression),
# not the compression level. Longer coil -> larger expansion. Differs from S23 (compress level + HTF) which
# ignores duration.
S48_DIMS = dict(D=[6, 12], stop=['range', 'atr'], exit=['rr2', 'rr3', 'trailing'])
def s48_grammar(): return _grid('S48', S48_DIMS)
def s48_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    comp = d['compress'].values; r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d); D = int(h['D'])
    coil = pd.Series(comp).rolling(D).sum().shift(1).values >= D      # D consecutive compressed bars (prior)
    band_hi = pd.Series(hi).rolling(D).max().shift(1).values; band_lo = pd.Series(lo).rolling(D).min().shift(1).values
    up = coil & (cl > band_hi); dn = coil & (cl < band_lo)
    up = up & ~np.concatenate([[False], up[:-1]]); dn = dn & ~np.concatenate([[False], dn[:-1]])
    out = []
    for t in np.flatnonzero((up | dn) & np.isfinite(band_hi) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if up[t] else -1; ei = t + 1
        stop = ((band_lo[t] - 2 * TICK) if dirn > 0 else (band_hi[t] + 2 * TICK)) if h['stop'] == 'range' else (o[ei] - dirn * 1.5 * atr[t])
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S49 — Narrowest-range (NR) bar breakout. NEW ingredient: the NR-N compression PATTERN (smallest range of last
# N bars) as the breakout trigger. Differs from S23/S48 (ATR-level / duration) — this is a single-bar range pattern.
S49_DIMS = dict(N=[4, 7], mode=['breakout', 'fade'], stop=['bar', 'atr'], exit=['rr2', 'time'])
def s49_grammar(): return _grid('S49', S49_DIMS)
def s49_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d); N = int(h['N']); rng = hi - lo
    is_nr = rng <= pd.Series(rng).rolling(N).min().values                  # narrowest range of last N (inclusive)
    nrh = np.where(is_nr, hi, np.nan); nrl = np.where(is_nr, lo, np.nan)
    nrh = pd.Series(nrh).ffill().shift(1).values; nrl = pd.Series(nrl).ffill().shift(1).values  # last NR bar's H/L (prior)
    # a true NR breakout is the expansion within a few bars OF the NR bar, not any later crossing (selectivity)
    recent = pd.Series(is_nr.astype(int)).rolling(3).max().shift(1).values >= 1
    up = (cl > nrh) & recent; dn = (cl < nrl) & recent
    up = up & ~np.concatenate([[False], up[:-1]]); dn = dn & ~np.concatenate([[False], dn[:-1]])
    out = []
    for t in np.flatnonzero((up | dn) & np.isfinite(nrh) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        raw = 1 if up[t] else -1; dirn = raw if h['mode'] == 'breakout' else -raw; ei = t + 1
        stop = ((nrl[t] - 2 * TICK) if dirn > 0 else (nrh[t] + 2 * TICK)) if h['stop'] == 'bar' else (o[ei] - dirn * 1.5 * atr[t])
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S50 — Outside-bar / engulfing reversal. NEW ingredient: the engulfing (outside) candle pattern (range
# expansion that engulfs the prior bar) as a control-shift signal. Differs from all (candlestick pattern).
S50_DIMS = dict(mode=['reversal', 'continuation'], stop=['bar', 'atr'], exit=['rr2', 'rr3', 'time'])
def s50_grammar(): return _grid('S50', S50_DIMS)
def s50_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    r20x = d['rmax20'].values; r20n = d['rmin20'].values; n = len(d)
    ph = np.concatenate([[np.nan], hi[:-1]]); pl = np.concatenate([[np.nan], lo[:-1]])
    # meaningful engulfing = outside bar that is also a genuine range EXPANSION (range > ATR), a real control shift
    outside = (hi > ph) & (lo < pl) & ((hi - lo) > atr)
    bull = outside & (cl > o); bear = outside & (cl < o)                    # bullish / bearish engulfing
    out = []
    for t in np.flatnonzero((bull | bear) & np.isfinite(ph) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        base = 1 if bull[t] else -1                                         # engulfing direction
        dirn = base if h['mode'] == 'continuation' else -base; ei = t + 1
        stop = ((lo[t] - 2 * TICK) if dirn > 0 else (hi[t] + 2 * TICK)) if h['stop'] == 'bar' else (o[ei] - dirn * 1.5 * atr[t])
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# S51 — Intraday range-position reversion. NEW ingredient: position within the developing SESSION range. Near
# the top/bottom of the session range -> revert toward the middle. Differs from S8 (SMA distance) / S26 (VWAP band).
S51_DIMS = dict(thr=[0.85, 0.95], stop=['atr', 'edge'], exit=['rr2', 'time'])
def s51_grammar(): return _grid('S51', S51_DIMS)
def s51_setups(d, h):
    hi = d['high'].values; lo = d['low'].values; cl = d['close'].values; o = d['open'].values; atr = d['m_atr'].values
    sh = d['sess_high'].values; sl = d['sess_low'].values; bis = d['bar_in_sess'].values; n = len(d); thr = float(h['thr'])
    width = sh - sl; pos = np.where(width > 0, (cl - sl) / width, np.nan)
    r20x = d['rmax20'].values; r20n = d['rmin20'].values
    devd = bis >= 8                                                         # only after the session range has formed
    hi_ev = (pos >= thr) & devd; lo_ev = (pos <= (1 - thr)) & devd          # near top -> short ; near bottom -> long
    hi_ev = hi_ev & ~np.concatenate([[False], hi_ev[:-1]]); lo_ev = lo_ev & ~np.concatenate([[False], lo_ev[:-1]])
    out = []
    for t in np.flatnonzero((hi_ev | lo_ev) & np.isfinite(pos) & np.isfinite(atr) & (atr > 0)):
        if t >= n - 1 or t < 1:
            continue
        dirn = 1 if lo_ev[t] else -1; ei = t + 1
        stop = (o[ei] - dirn * 1.5 * atr[t]) if h['stop'] == 'atr' else ((sl[t] - 2 * TICK) if dirn > 0 else (sh[t] + 2 * TICK))
        ek, ep = _exitmap(h['exit'], dirn, r20n, r20x, ei, r20x, r20n)
        out.append(dict(si=int(t), ei=ei, dir=dirn, stop=float(stop), exit_kind=ek, exit_param=ep))
    return out

# ------------- extension registry (mirrors MS.REGISTRY shape) -------------
EXT_REGISTRY = {
    'S21': (s21_grammar, s21_setups),
    'S22': (s22_grammar, s22_setups),
    'S47': (s47_grammar, s47_setups),
    'S48': (s48_grammar, s48_setups),
    'S49': (s49_grammar, s49_setups),
    'S50': (s50_grammar, s50_setups),
    'S51': (s51_grammar, s51_setups),
    'S41': (s41_grammar, s41_setups),
    'S42': (s42_grammar, s42_setups),
    'S43': (s43_grammar, s43_setups),
    'S44': (s44_grammar, s44_setups),
    'S45': (s45_grammar, s45_setups),
    'S46': (s46_grammar, s46_setups),
    'S29': (s29_grammar, s29_setups),
    'S30': (s30_grammar, s30_setups),
    'S31': (s31_grammar, s31_setups),
    'S24': (s24_grammar, s24_setups),
    'S25': (s25_grammar, s25_setups),
    'S27': (s27_grammar, s27_setups),
    'S28': (s28_grammar, s28_setups),
    'S23': (s23_grammar, s23_setups),
    'S26': (s26_grammar, s26_setups),
    'S38': (s38_grammar, s38_setups),
    'S39': (s39_grammar, s39_setups),
    'S40': (s40_grammar, s40_setups),
}
EXT_ECON = {
    'S21': 'equal-highs/lows liquidity-pool raid',
    'S22': 'round-number magnet/rejection',
    'S24': 'overnight variance / session carry',
    'S25': 'volatility-regime onset',
    'S27': 'VWAP reclaim in trend',
    'S28': 'anchored-VWAP reaction',
    'S29': 'day-of-week effect',
    'S30': 'kill-zone time-window effect',
    'S31': 'month-end/month-start effect',
    'S23': 'squeeze breakout + HTF filter',
    'S26': 'value-area rejection/acceptance',
    'S38': 'patient pullback-into-zone (trend continuation)',
    'S39': 'trend-efficiency-gated continuation',
    'S40': 'regime router (trend-continuation / range-reversion)',
    'S41': 'volume-climax reversal',
    'S42': 'short-term return reversal (overreaction)',
    'S43': 'momentum divergence (RSI/price)',
    'S44': 'intrabar pressure / close-location (order-flow proxy)',
    'S45': 'consecutive-bar streak',
    'S46': 'volume-confirmed breakout',
    'S47': 'weekend-gap fill/continuation',
    'S48': 'consolidation-duration breakout',
    'S49': 'narrowest-range (NR) breakout',
    'S50': 'outside-bar / engulfing reversal',
    'S51': 'intraday range-position reversion',
}
def ext_setups(d, h): return EXT_REGISTRY[h['family']][1](d, h)
def ext_backtest(d, h): return MS.simulate(d, EXT_REGISTRY[h['family']][1](d, h), MS.CFG)
