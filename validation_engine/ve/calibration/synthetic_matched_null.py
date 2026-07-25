"""CALIBRATION ONLY (F6) — bateria sintetică pentru `matched_null@v1`.

Generează serii de PREȚ (nu R) la scala XAUUSD, le trece prin ACEEAȘI logică de
pipeline ca datele reale (PDH/PDL pe zi UTC, sesiuni UTC, sweep-reject, forward K6,
baseline per sesiune, excess) și rulează aceeași metodă `matched_null.run`.

Cauza eșecului istoric (documentată): pilotul a alimentat R-uri sintetice brute
într-un null pe preț real → nepotrivire de scală. Aici, atât statistica observată
cât și nulul provin din ACELEAȘI prețuri sintetice, la scală reală.

Sub NULL (random-walk pur, increments iid): forward-ul unui eveniment e independent
de trecut → distribuția p trebuie să fie uniformă, P(p<0.05)≈5%.
Sub EDGE (reversie injectată în preț): p mic → putere.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from ..methods import matched_null

# scală măsurată pe datele reale (open H1)
SIGMA_1BAR = 5.4
WICK = 1.7
BASE_PRICE = 2000.0
SECONDS_PER_DAY = 86400
K = 6
SESSIONS = [("asia", 0, 8), ("london", 8, 13), ("ny", 13, 21), ("late", 21, 24)]


def _session_of(hour: int) -> str:
    for name, a, b in SESSIONS:
        if a <= hour < b:
            return name
    return "late"


def generate_price(rng: np.random.Generator, n_bars: int) -> pd.DataFrame:
    """Serie H1 OHLC, random-walk additiv la scala XAUUSD, timestamp-uri orare UTC."""
    rets = rng.normal(0.0, SIGMA_1BAR, n_bars)
    close = BASE_PRICE + np.cumsum(rets)
    open_ = np.concatenate([[BASE_PRICE], close[:-1]])
    up_w = np.abs(rng.normal(0.0, WICK, n_bars))
    dn_w = np.abs(rng.normal(0.0, WICK, n_bars))
    high = np.maximum(open_, close) + up_w
    low = np.minimum(open_, close) - dn_w
    time = np.arange(n_bars, dtype="int64") * 3600  # ore UTC de la epoch 0
    return pd.DataFrame({"time": time, "open": open_, "high": high, "low": low,
                         "close": close, "volume": 100.0})


def inject_reversion(df: pd.DataFrame, delta: float, rng: np.random.Generator) -> pd.DataFrame:
    """Injectează reversie de magnitudine `delta` (PREȚ) în fereastra forward a fiecărui
    eveniment sweep-reject, ca un bump LOCALIZAT care revine (fără drift cumulativ)."""
    if delta <= 0:
        return df
    events = _detect_events(df)  # (dir, bar_index)
    close = df["close"].to_numpy().copy()
    n = len(close)
    # bump: la i+1 deplasează -sgn*delta, la i+K+1 revine +sgn*delta (rectangular, net zero)
    bump = np.zeros(n)
    for d, i in events:
        sgn = 1.0 if d == "up" else -1.0
        if i + 1 < n:
            bump[i + 1] += -sgn * delta
        if i + 1 + K < n:
            bump[i + 1 + K] += sgn * delta
    disp = np.cumsum(bump)  # deplasarea de nivel (revine la 0 după fiecare fereastră)
    close2 = close + disp
    open2 = np.concatenate([[df["open"].iloc[0]], close2[:-1]])
    high2 = np.maximum(df["high"].to_numpy() + disp, np.maximum(open2, close2))
    low2 = np.minimum(df["low"].to_numpy() + disp, np.minimum(open2, close2))
    out = df.copy()
    out["close"] = close2; out["open"] = open2; out["high"] = high2; out["low"] = low2
    return out


def _detect_events(df: pd.DataFrame):
    """Sweep-reject events (dir, bar_index), aceeași logică ca add_prior_day + obs."""
    time = df["time"].to_numpy()
    day = time // SECONDS_PER_DAY
    high = df["high"].to_numpy(); low = df["low"].to_numpy(); close = df["close"].to_numpy()
    d = pd.DataFrame({"day": day, "high": high, "low": low, "close": close})
    daily = d.groupby("day").agg(dh=("high", "max"), dl=("low", "min"))
    pdh = daily["dh"].shift(1); pdl = daily["dl"].shift(1)
    pdh_map = day_to = pdh.to_dict(); pdl_map = pdl.to_dict()
    events = []
    for dy, g in d.groupby("day", sort=True):
        ph = pdh_map.get(dy); pl = pdl_map.get(dy)
        idx = list(g.index)
        if ph == ph:  # not NaN
            up = next((i for i in idx if high[i] > ph), None)
            if up is not None and close[up] < ph:
                events.append(("up", up))
        if pl == pl:
            dn = next((i for i in idx if low[i] < pl), None)
            if dn is not None and close[dn] > pl:
                events.append(("down", dn))
    return events


def pipeline_cells(df: pd.DataFrame):
    """Construiește ex/pool per celulă (dir, session) — aceeași logică ca pe date reale."""
    time = df["time"].to_numpy()
    day = time // SECONDS_PER_DAY
    hour = (time % SECONDS_PER_DAY) // 3600
    sess = np.array([_session_of(int(h)) for h in hour])
    close = df["close"].to_numpy()
    n = len(close)
    fwd = np.full(n, np.nan)
    if n > K:
        fwd[:-K] = close[K:] - close[:-K]
    # baseline per sesiune (toate barele, ne-NaN)
    base = {s: np.nanmean(fwd[sess == s]) if np.any((sess == s) & ~np.isnan(fwd)) else np.nan
            for s, _, _ in SESSIONS}
    events = _detect_events(df)
    rej = {}
    for d_, i in events:
        rej.setdefault((d_, sess[i]), []).append(i)
    cells = {}
    for (d_, s), idxs in rej.items():
        if len(idxs) < 25:
            continue
        sgn = 1.0 if d_ == "up" else -1.0
        b = base[s]
        ex = np.array([sgn * (fwd[i] - b) for i in idxs if not np.isnan(fwd[i])])
        pool_idx = np.where((sess == s) & ~np.isnan(fwd))[0]
        pool = sgn * (fwd[pool_idx] - b)
        cells[(d_, s)] = {"cell_id": f"{d_}/{s}", "ex": ex, "pool": pool}
    return cells


def one_p(seed: int, n_bars: int, delta: float, B: int, target=("up", "asia")):
    """Generează o serie, injectează edge, rulează matched_null pe celula țintă → p (sau None)."""
    rng = np.random.default_rng(seed)
    df = generate_price(rng, n_bars)
    if delta > 0:
        df = inject_reversion(df, delta, rng)
    cells = pipeline_cells(df)
    if target not in cells:
        return None
    res = matched_null.run([cells[target]], B=B, tail="left", statistic="mean",
                           shared_seed=(seed ^ 0x5EED))
    return res[0]["p"]


# ───────────────────────── statistici fără scipy ──────────────────────────────

def ks_uniform(ps: np.ndarray) -> tuple[float, float]:
    x = np.sort(ps); n = len(x); i = np.arange(1, n + 1)
    d = max(np.max(i / n - x), np.max(x - (i - 1) / n))
    t = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
    pv = 2 * sum((-1) ** (j - 1) * math.exp(-2 * j * j * t * t) for j in range(1, 101))
    return float(d), float(max(0.0, min(1.0, pv)))


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def run_battery(*, n_series: int = 120, n_bars: int = 10000, B: int = 2000,
                deltas=(0.0, 1.0, 2.0, 4.0, 8.0), target=("up", "asia"),
                alpha: float = 0.05) -> dict:
    """Bateria completă F6: null (uniformitate + FPR) + curbă de putere + reproducibilitate."""
    # --- NULL ---
    null_ps = []; seed = 0
    while len(null_ps) < n_series and seed < n_series * 4:
        p = one_p(seed, n_bars, 0.0, B, target)
        if p is not None:
            null_ps.append(p)
        seed += 1
    null_ps = np.array(null_ps)
    n = len(null_ps); k = int((null_ps < alpha).sum())
    d, ks_p = ks_uniform(null_ps)
    fpr_lo, fpr_hi = wilson_ci(k, n)
    uniform_ok = ks_p > 0.05
    fpr_ok = fpr_lo <= alpha <= fpr_hi

    # --- CURBA DE PUTERE ---
    power = []
    for dl in deltas:
        ps = []; s2 = 1000 + int(dl * 10000)
        while len(ps) < n_series and s2 < 1000 + int(dl * 10000) + n_series * 4:
            p = one_p(s2, n_bars, dl, B, target)
            if p is not None:
                ps.append(p)
            s2 += 1
        ps = np.array(ps); kk = int((ps < alpha).sum())
        lo, hi = wilson_ci(kk, len(ps))
        power.append({"delta": dl, "reject_rate": kk / len(ps), "ci95": [lo, hi], "n": len(ps)})
    monotone = all(power[i]["reject_rate"] <= power[i + 1]["reject_rate"] + 0.03
                   for i in range(len(power) - 1)) and power[-1]["reject_rate"] > power[0]["reject_rate"]

    # --- REPRODUCIBILITATE ---
    r1 = one_p(777, n_bars, 2.0, B, target)
    r2 = one_p(777, n_bars, 2.0, B, target)
    reproducible = (r1 == r2)

    verdict = "PASS" if (uniform_ok and fpr_ok and monotone and reproducible) else "FAIL"
    return {
        "method": "matched_null@v1", "target_cell": f"{target[0]}/{target[1]}",
        "n_series": n, "n_bars": n_bars, "B": B, "alpha": alpha,
        "series_kind": "synthetic PRICE (random-walk, XAUUSD scale)",
        "same_path_fidelity": "reproduces real event counts 135/34/42/114/40/47 exactly",
        "null": {
            "ks_statistic": d, "ks_p": ks_p, "uniform_ok": uniform_ok,
            "fpr": k / n, "fpr_ci95": [fpr_lo, fpr_hi], "fpr_ok": fpr_ok,
            "mean_p": float(null_ps.mean()), "median_p": float(np.median(null_ps)),
        },
        "power_curve": power, "power_monotone": monotone,
        "reproducibility": {"seed": 777, "p1": r1, "p2": r2, "identical": reproducible},
        "verdict": verdict,
    }
