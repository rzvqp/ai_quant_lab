"""Synthetic PRICE-series generator for matched-null validation (docs/MATCHED_NULL_SPEC.md,
docs/SYNTHETIC_PRICE_GENERATOR.md). Produces OHLC+m_atr frames that flow through mstrat.simulate
UNCHANGED, plus helper columns (session, month, atrq) for stratified nulls. Ground truth is KNOWN:
an edge exists iff inject_edge() was called with edge>0. All randomness is seeded and reproducible.

NOTE: this is NOT a backtester and NOT part of the official engine. It only manufactures price frames
and signal sets; execution is always done by mstrat.simulate."""
import numpy as np, pandas as pd

TICK = 0.1
BAR_SECONDS = 900          # 15-minute bars, matching the real M15 grid
ATR_WIN = 14

def _true_range(o, h, l, c):
    pc = np.concatenate([[c[0]], c[:-1]])
    return np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))

def _atr(o, h, l, c, win=ATR_WIN):
    tr = _true_range(o, h, l, c)
    atr = pd.Series(tr).rolling(win, min_periods=1).mean().values
    # guard: strictly positive finite (engine skips atr<=0 / nan)
    atr = np.where(np.isfinite(atr) & (atr > 0), atr, np.nanmedian(tr[tr > 0]) if (tr > 0).any() else TICK)
    return atr

def gen_series(n=6000, seed=0, p0=2000.0, vol_base=0.0009, vol_clustering=0.0, ar1=0.0,
               drift=0.0, regimes=None, gap_rate=0.0, gap_size=3.0, t0_epoch=1_600_000_000):
    """Generate a synthetic OHLC+m_atr frame.
    vol_base       : baseline per-bar log-return sd.
    vol_clustering : GARCH-like persistence in [0,1); 0 = homoskedastic, ~0.9 = strong clustering.
    ar1            : AR(1) coefficient on returns (momentum/mean-rev in returns).
    drift          : constant per-bar log drift.
    regimes        : optional list of (start_frac, vol_mult, drift_add) segments.
    gap_rate       : prob per bar of an overnight-style gap on the open.
    gap_size       : gap magnitude in units of local sd.
    Returns df with columns time,open,high,low,close,volume,m_atr,session,month,atrq and attr .seed.
    """
    rng = np.random.default_rng(seed)
    # --- conditional volatility (GARCH(1,1)-lite) ---
    vol = np.empty(n); vol[0] = vol_base
    z = rng.standard_normal(n)
    for t in range(1, n):
        if vol_clustering > 0:
            vol[t] = np.sqrt((1 - vol_clustering) * vol_base**2 + vol_clustering * (vol[t-1]**2) * (0.4 + 0.6*z[t-1]**2))
        else:
            vol[t] = vol_base
    # --- regime overlays ---
    dr = np.full(n, drift)
    if regimes:
        for (sf, vm, da) in regimes:
            i0 = int(sf * n); vol[i0:] *= vm; dr[i0:] += da
    # --- returns with optional AR(1) ---
    eps = z * vol
    r = np.empty(n); r[0] = eps[0] + dr[0]
    for t in range(1, n):
        r[t] = dr[t] + ar1 * (r[t-1] - dr[t-1]) + eps[t]
    close = p0 * np.exp(np.cumsum(r))
    # --- opens with optional gaps ---
    openp = np.empty(n); openp[0] = p0
    gaps = (rng.random(n) < gap_rate)
    for t in range(1, n):
        g = (gap_size * vol[t] * close[t-1] * rng.standard_normal()) if gaps[t] else 0.0
        openp[t] = close[t-1] + g
    # --- intrabar high/low bracketing open&close with vol-scaled wicks ---
    body_hi = np.maximum(openp, close); body_lo = np.minimum(openp, close)
    wick = np.abs(rng.standard_normal((n, 2))) * (vol * close)[:, None]
    high = body_hi + wick[:, 0]
    low  = np.maximum(body_lo - wick[:, 1], 1e-6)
    vol_shares = (1e4 * (1 + np.abs(z))).astype(int)
    time = t0_epoch + np.arange(n) * BAR_SECONDS
    atr = _atr(openp, high, low, close)
    df = pd.DataFrame({'time': time, 'open': openp, 'high': high, 'low': low,
                       'close': close, 'volume': vol_shares, 'm_atr': atr})
    # helper strata (session by synthetic hour, calendar month, ATR quintile)
    dt = pd.to_datetime(df['time'], unit='s', utc=True)
    hr = dt.dt.hour.values
    df['session'] = np.select([hr < 8, hr < 16], ['asia', 'london'], 'ny')
    df['month'] = dt.dt.tz_convert(None).dt.to_period('M').astype(str).values
    df['atrq'] = pd.qcut(df['m_atr'], 5, labels=False, duplicates='drop')
    df.attrs['seed'] = seed
    return df

# ---------- signal templates (return signal_bars, dirs) ----------
def exo_signals(df, n_sig=200, seed=1, side='long'):
    """Exogenous (price-independent) signals — cleanest ground truth. Random bars, fixed direction."""
    rng = np.random.default_rng(seed + 777)
    n = len(df); pool = np.arange(ATR_WIN + 2, n - 60)
    bars = np.sort(rng.choice(pool, size=min(n_sig, len(pool)), replace=False))
    dirn = 1 if side == 'long' else (-1 if side == 'short' else 0)
    dirs = np.full(len(bars), dirn) if dirn != 0 else rng.choice([-1, 1], size=len(bars))
    return bars, dirs

def breakout_signals(df, lb=20, side='long', **_):
    c = df['close'].values; n = len(df)
    roll = pd.Series(c).rolling(lb).max().shift(1).values if side == 'long' else pd.Series(c).rolling(lb).min().shift(1).values
    trig = (c > roll) if side == 'long' else (c < roll)
    trig = trig & ~np.concatenate([[False], trig[:-1]]) & np.isfinite(roll)
    bars = np.flatnonzero(trig); bars = bars[(bars > ATR_WIN + 2) & (bars < n - 60)]
    return bars, np.full(len(bars), 1 if side == 'long' else -1)

def sweep_signals(df, lb=20, side='long', **_):
    c = df['close'].values; h = df['high'].values; l = df['low'].values; n = len(df)
    rmin = pd.Series(l).rolling(lb).min().shift(1).values; rmax = pd.Series(h).rolling(lb).max().shift(1).values
    if side == 'long':   # sweep low then close back above
        trig = (l < rmin) & (c > rmin) & np.isfinite(rmin)
    else:
        trig = (h > rmax) & (c < rmax) & np.isfinite(rmax)
    trig = trig & ~np.concatenate([[False], trig[:-1]])
    bars = np.flatnonzero(trig); bars = bars[(bars > ATR_WIN + 2) & (bars < n - 60)]
    return bars, np.full(len(bars), 1 if side == 'long' else -1)

def timeofday_signals(df, hour=8, side='long', **_):
    dt = pd.to_datetime(df['time'], unit='s', utc=True); n = len(df)
    trig = (dt.dt.hour.values == hour) & (dt.dt.minute.values == 0)
    bars = np.flatnonzero(trig); bars = bars[(bars > ATR_WIN + 2) & (bars < n - 60)]
    return bars, np.full(len(bars), 1 if side == 'long' else -1)

def inject_edge(df, signal_bars, dirs, edge_atr=0.0, horizon=8, seed=2):
    """Add a forward directional bump of total size ~edge_atr*ATR spread over `horizon` bars after each
    signal, in the signal's direction. edge_atr=0 => returns df unchanged (null). Rebuilds OHLC & m_atr.
    Ground truth: an alpha exists at these signals iff edge_atr>0."""
    if edge_atr == 0.0:
        return df.copy()
    df = df.copy(); n = len(df)
    c = df['close'].values.astype(float); atr = df['m_atr'].values
    add = np.zeros(n)
    for t, dpos in zip(signal_bars, dirs):
        bump = dpos * edge_atr * atr[t] / max(horizon, 1)
        j1 = min(t + 1 + horizon, n)
        add[t+1:j1] += bump
    new_close = c + np.cumsum(add)          # persistent level shift after each signal
    shift = new_close - c
    o = df['open'].values + np.concatenate([[0.0], shift[:-1]])
    hi = df['high'].values + shift; lo = df['low'].values + shift
    hi = np.maximum(hi, np.maximum(o, new_close)); lo = np.minimum(lo, np.minimum(o, new_close))
    df['open'] = o; df['high'] = hi; df['low'] = np.maximum(lo, 1e-6); df['close'] = new_close
    df['m_atr'] = _atr(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    return df

def make_setups(df, signal_bars, dirs, risk_kind='atr', risk_mult=1.5, exit_kind='rr', exit_param=2.0):
    """Build engine-compatible setups from signal bars (entry at next open, ATR- or structural stop)."""
    o = df['open'].values; h = df['high'].values; l = df['low'].values; atr = df['m_atr'].values; n = len(df)
    out = []
    for t, dpos in zip(signal_bars, dirs):
        if t + 1 >= n - 1 or not np.isfinite(atr[t]) or atr[t] <= 0:
            continue
        ei = int(t) + 1; entry = o[ei]
        if risk_kind == 'atr':
            stop = entry - dpos * risk_mult * atr[t]
        else:  # structural: beyond the signal bar extreme
            stop = (l[t] - 2*TICK) if dpos > 0 else (h[t] + 2*TICK)
        out.append(dict(si=int(t), ei=ei, dir=int(dpos), stop=float(stop),
                        exit_kind=exit_kind, exit_param=exit_param))
    return out
