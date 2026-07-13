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

# ------------- extension registry (mirrors MS.REGISTRY shape) -------------
EXT_REGISTRY = {
    'S21': (s21_grammar, s21_setups),
    'S22': (s22_grammar, s22_setups),
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
}
def ext_setups(d, h): return EXT_REGISTRY[h['family']][1](d, h)
def ext_backtest(d, h): return MS.simulate(d, EXT_REGISTRY[h['family']][1](d, h), MS.CFG)
