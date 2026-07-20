"""E009 -- Change of Character (CHoCH) Retest -- Discovery-stage analysis (Flow A).

V0 (frozen, verbatim, EDGE_DISCOVERY_REGISTRY_v1.md): "After a Change of Character (CHoCH) signals a
possible trend shift, price frequently retests the CHoCH level before continuing in the new direction."

Run under the post-remediation regime (EDGE_RESEARCH_PROTOCOL.md SS8) -- data loads exclusively via
`_common.load()`, no direct CSV read anywhere in this file.

Method (disclosed, exploratory -- Discovery stage only, no tuning/optimization):
1. Swing (fractal) detection, same disclosed k=5 method already used for E017/E028 (reproduced from
   scratch here -- each edge script is self-contained), producing a strictly-alternating zigzag of
   swing highs/lows.
2. Standard, mechanical BOS/CHoCH classification over the zigzag sequence: maintain a trend state
   ('up'/'down'), bootstrapped once 2 confirmed highs and 2 confirmed lows exist (HH+HL -> 'up';
   LH+LL -> 'down'). Thereafter:
   - trend='up', new low breaks BELOW the immediately preceding low -> **CHoCH-down** (the uptrend's
     protective swing low is violated; trend flips to 'down'). The broken low is the "CHoCH level."
   - trend='down', new high breaks ABOVE the immediately preceding high -> **CHoCH-up** (symmetric;
     trend flips to 'up').
   - trend='up', new high breaks ABOVE the immediately preceding high -> **BOS-up** (ordinary
     trend-following continuation; trend unchanged). The broken high is the "BOS level."
   - trend='down', new low breaks BELOW the immediately preceding low -> **BOS-down** (symmetric).
   A swing that does not break the relevant reference point (e.g. a lower high forming inside an
   uptrend) produces no event -- it is neither a break nor part of this test.
3. **The natural, on-topic control for "is CHoCH-ness special" is BOS**: both CHoCH and BOS are real,
   confirmed structural breaks of a real swing level -- the ONLY difference is whether the break agrees
   with (BOS) or contradicts (CHoCH) the immediately preceding trend context. Grouping by the level TYPE
   broken (a low broken downward = "low-break", tested identically whether CHoCH-down or BOS-down; a
   high broken upward = "high-break", tested identically whether CHoCH-up or BOS-up) keeps the retest/
   continuation mechanics identical across the CHoCH-vs-BOS comparison -- the only thing that varies is
   the `kind` label.
4. A second, stronger control -- **RANDOM-MATCHED-DISTANCE**: for a sample of purely random bar
   locations (seed=42, no swing/structure at all), a synthetic level is placed at a distance (in ATR
   units) resampled with replacement from the CHoCH group's own empirical distance distribution --
   tests whether the retest rate is just "a level this close, given this much time, usually gets
   touched anyway," independent of any real structural-break mechanism.
5. For every event: `retested` = whether price ever touches/exceeds the broken level within a horizon
   (96/480/1920 M15 bars ~ 1/5/20 trading days -- horizon sensitivity, not optimized to one value).
   `continued` = whether price, after the retest (or from the break itself if no retest occurred),
   makes a NEW EXTREME beyond the original break price within a further horizon -- V0's own
   "continuing in the new direction" claim, tested directly and separately from the retest itself.
6. Both level types (low-break / high-break) run independently and are compared for asymmetry. A
   fractal-k sensitivity sweep (k in {3,5,8}) re-runs the primary CHoCH-vs-BOS retest-rate comparison to
   check robustness to swing-detection granularity, without picking a favorable k.
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from _common import load, vol_regime, summarize, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID

HORIZONS = [96, 480, 1920]
PRIMARY_HORIZON = 480
RNG_SEED = 42
K_SWEEP = [3, 5, 8]
PRIMARY_K = 5


def detect_swings(m, k):
    h = m["high"].values
    l = m["low"].values
    n = len(m)
    is_high = np.zeros(n, dtype=bool)
    is_low = np.zeros(n, dtype=bool)
    for i in range(k, n - k):
        window_h = h[i - k:i + k + 1]
        if h[i] == window_h.max() and (window_h == h[i]).sum() == 1:
            is_high[i] = True
        window_l = l[i - k:i + k + 1]
        if l[i] == window_l.min() and (window_l == l[i]).sum() == 1:
            is_low[i] = True
    candidates = sorted(
        [(i, "high", h[i]) for i in np.where(is_high)[0]] + [(i, "low", l[i]) for i in np.where(is_low)[0]],
        key=lambda x: x[0])
    swings = []
    cur_type = cur_price = cur_idx = None
    for idx, typ, price in candidates:
        if cur_type is None:
            cur_type, cur_price, cur_idx = typ, price, idx
            continue
        if typ == cur_type:
            if (typ == "high" and price > cur_price) or (typ == "low" and price < cur_price):
                cur_price, cur_idx = price, idx
        else:
            swings.append((cur_idx, cur_type, cur_price))
            cur_type, cur_price, cur_idx = typ, price, idx
    swings.append((cur_idx, cur_type, cur_price))
    return swings


def detect_choch_bos(swings):
    highs, lows = [], []
    trend = None
    events = []
    for idx, typ, price in swings:
        if typ == "high":
            if highs:
                prev_idx, prev_price = highs[-1]
                if trend == "up" and price > prev_price:
                    events.append(dict(kind="BOS", direction="up", level=float(prev_price),
                                        level_idx=int(prev_idx), confirm_idx=int(idx),
                                        confirm_price=float(price)))
                elif trend == "down" and price > prev_price:
                    events.append(dict(kind="CHOCH", direction="up", level=float(prev_price),
                                        level_idx=int(prev_idx), confirm_idx=int(idx),
                                        confirm_price=float(price)))
                    trend = "up"
            highs.append((idx, price))
        else:
            if lows:
                prev_idx, prev_price = lows[-1]
                if trend == "down" and price < prev_price:
                    events.append(dict(kind="BOS", direction="down", level=float(prev_price),
                                        level_idx=int(prev_idx), confirm_idx=int(idx),
                                        confirm_price=float(price)))
                elif trend == "up" and price < prev_price:
                    events.append(dict(kind="CHOCH", direction="down", level=float(prev_price),
                                        level_idx=int(prev_idx), confirm_idx=int(idx),
                                        confirm_price=float(price)))
                    trend = "down"
            lows.append((idx, price))
        if trend is None and len(highs) >= 2 and len(lows) >= 2:
            if highs[-1][1] > highs[-2][1] and lows[-1][1] > lows[-2][1]:
                trend = "up"
            elif highs[-1][1] < highs[-2][1] and lows[-1][1] < lows[-2][1]:
                trend = "down"
    return events


def event_stats(e, m, horizon, group_type):
    idx = e["confirm_idx"]
    level = e["level"]
    confirm_price = e["confirm_price"]
    high = m["high"].values
    low = m["low"].values
    close = m["close"].values
    atr = m["atr14"].values
    n = len(m)
    end = min(idx + 1 + horizon, n)
    if end <= idx + 1:
        return None
    if group_type == "low_break":
        seg = high[idx + 1:end]
        retested_mask = seg >= level
    else:
        seg = low[idx + 1:end]
        retested_mask = seg <= level
    retested = bool(retested_mask.any())
    ttr = int(np.argmax(retested_mask)) if retested else None

    start_cont = idx + 1 + ttr if retested else idx + 1
    end_cont = min(start_cont + horizon, n)
    if group_type == "low_break":
        seg2 = low[start_cont:end_cont]
        continued = bool((seg2 <= confirm_price).any()) if len(seg2) else False
    else:
        seg2 = high[start_cont:end_cont]
        continued = bool((seg2 >= confirm_price).any()) if len(seg2) else False

    a = atr[idx]
    dist = None
    if np.isfinite(a) and a > 0:
        dist = (level - close[idx]) / a if group_type == "low_break" else (close[idx] - level) / a

    row = dict(e)
    row.update(group_type=group_type, horizon=horizon, retested=retested, ttr_bars=ttr,
               continued=continued, dist=dist, session=str(m["session"].iloc[idx]),
               dow=str(m["dow"].iloc[idx]), vol_regime=str(m["vol_regime"].iloc[idx]))
    return row


def random_matched_control(real_events, m, group_type, n_events, horizon, rng):
    close = m["close"].values
    atr = m["atr14"].values
    n = len(m)
    dists = np.array([e["dist"] for e in real_events if e["dist"] is not None])
    max_start = n - horizon - 2
    valid_idx = np.where(np.isfinite(atr[:max_start]) & (atr[:max_start] > 0))[0]
    valid_idx = valid_idx[valid_idx > 10]
    chosen = rng.choice(valid_idx, size=min(n_events, len(valid_idx)), replace=False)
    sampled_dist = rng.choice(dists, size=len(chosen), replace=True)
    out = []
    for idx, d in zip(chosen, sampled_dist):
        a = atr[idx]
        level = close[idx] + d * a if group_type == "low_break" else close[idx] - d * a
        end = min(idx + 1 + horizon, n)
        if group_type == "low_break":
            reached = bool((m["high"].values[idx + 1:end] >= level).any())
        else:
            reached = bool((m["low"].values[idx + 1:end] <= level).any())
        out.append(dict(idx=int(idx), reached=reached))
    return out


def summarize_group(rows):
    n = len(rows)
    if n == 0:
        return dict(n=0)
    retested = [r["retested"] for r in rows]
    continued = [r["continued"] for r in rows]
    ttrs = [r["ttr_bars"] for r in rows if r["ttr_bars"] is not None]
    out = dict(n=n, retest_rate=float(np.mean(retested)), continuation_rate=float(np.mean(continued)))
    if ttrs:
        out["median_ttr_bars"] = float(np.median(ttrs))
    both = [1 for r in rows if r["retested"] and r["continued"]]
    out["retest_then_continue_rate"] = float(len(both) / n)
    no_retest = [1 for r in rows if not r["retested"]]
    out["no_retest_rate"] = float(len(no_retest) / n)
    retest_no_cont = [1 for r in rows if r["retested"] and not r["continued"]]
    out["retest_then_fail_rate"] = float(len(retest_no_cont) / n)
    return out


def chi2_p(rate1, n1, rate2, n2):
    s1, s2 = round(rate1 * n1), round(rate2 * n2)
    try:
        _, p, _, _ = chi2_contingency([[s1, n1 - s1], [s2, n2 - s2]])
        return float(p)
    except Exception:
        return None


def run_group_type(m, events, group_type):
    choch = [e for e in events if e["kind"] == "CHOCH"]
    bos = [e for e in events if e["kind"] == "BOS"]

    result = {"n_choch": len(choch), "n_bos": len(bos), "by_horizon": {}}
    for hz in HORIZONS:
        choch_rows = [r for r in (event_stats(e, m, hz, group_type) for e in choch) if r]
        bos_rows = [r for r in (event_stats(e, m, hz, group_type) for e in bos) if r]
        c_sum, b_sum = summarize_group(choch_rows), summarize_group(bos_rows)
        p = chi2_p(c_sum.get("retest_rate", 0), c_sum.get("n", 0), b_sum.get("retest_rate", 0), b_sum.get("n", 0)) \
            if c_sum.get("n", 0) > 20 and b_sum.get("n", 0) > 20 else None
        result["by_horizon"][str(hz)] = dict(choch=c_sum, bos=b_sum, retest_rate_chi2_p=p)

    # primary: full detail + random-matched control + slices
    choch_rows = [r for r in (event_stats(e, m, PRIMARY_HORIZON, group_type) for e in choch) if r]
    bos_rows = [r for r in (event_stats(e, m, PRIMARY_HORIZON, group_type) for e in bos) if r]
    rng = np.random.default_rng(RNG_SEED)
    rand_events = random_matched_control(choch_rows, m, group_type, len(choch_rows), PRIMARY_HORIZON, rng)
    rand_rate = float(np.mean([r["reached"] for r in rand_events])) if rand_events else None

    c_sum, b_sum = summarize_group(choch_rows), summarize_group(bos_rows)
    p_choch_vs_bos = chi2_p(c_sum.get("retest_rate", 0), c_sum["n"], b_sum.get("retest_rate", 0), b_sum["n"])
    p_choch_vs_rand = chi2_p(c_sum.get("retest_rate", 0), c_sum["n"], rand_rate or 0, len(rand_events)) \
        if rand_events else None

    result["primary"] = dict(horizon=PRIMARY_HORIZON, choch=c_sum, bos=b_sum,
                              random_matched_retest_rate=rand_rate, n_random=len(rand_events),
                              p_choch_vs_bos=p_choch_vs_bos, p_choch_vs_random=p_choch_vs_rand)

    slices = {}
    for sess in ["asia", "london", "ny", "late"]:
        cs = [r for r in choch_rows if r["session"] == sess]
        bs = [r for r in bos_rows if r["session"] == sess]
        slices[f"session_{sess}"] = dict(choch=summarize_group(cs), bos=summarize_group(bs))
    for vr in ["low", "mid", "high"]:
        cv = [r for r in choch_rows if r["vol_regime"] == vr]
        bv = [r for r in bos_rows if r["vol_regime"] == vr]
        slices[f"vol_{vr}"] = dict(choch=summarize_group(cv), bos=summarize_group(bv))
    result["slices"] = slices

    return result


def main():
    m, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["vol_regime"] = vol_regime(m)

    results = {"edge": "E009", "run_id": "discovery_pass_1_2026-07-21",
               "split_metadata": meta, "n_bars": int(len(m)),
               "date_range": [str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
               "params": dict(K_SWEEP=K_SWEEP, PRIMARY_K=PRIMARY_K, HORIZONS=HORIZONS,
                              PRIMARY_HORIZON=PRIMARY_HORIZON, RNG_SEED=RNG_SEED)}

    swings_primary = detect_swings(m, PRIMARY_K)
    events_primary = detect_choch_bos(swings_primary)
    print("n_swings(primary k)", len(swings_primary), "n_events", len(events_primary),
          "n_CHOCH", sum(1 for e in events_primary if e["kind"] == "CHOCH"),
          "n_BOS", sum(1 for e in events_primary if e["kind"] == "BOS"))

    for group_type in ["low_break", "high_break"]:
        results[group_type] = run_group_type(m, events_primary, group_type)

    # k-sensitivity: primary retest-rate comparison only, both group types
    k_sensitivity = {}
    for k in K_SWEEP:
        sw = detect_swings(m, k)
        ev = detect_choch_bos(sw)
        row = {}
        for group_type in ["low_break", "high_break"]:
            choch = [e for e in ev if e["kind"] == "CHOCH" and e["direction"] == ("down" if group_type == "low_break" else "up")]
            bos = [e for e in ev if e["kind"] == "BOS" and e["direction"] == ("down" if group_type == "low_break" else "up")]
            choch_rows = [r for r in (event_stats(e, m, PRIMARY_HORIZON, group_type) for e in choch) if r]
            bos_rows = [r for r in (event_stats(e, m, PRIMARY_HORIZON, group_type) for e in bos) if r]
            c_sum, b_sum = summarize_group(choch_rows), summarize_group(bos_rows)
            p = chi2_p(c_sum.get("retest_rate", 0), c_sum.get("n", 0), b_sum.get("retest_rate", 0), b_sum.get("n", 0)) \
                if c_sum.get("n", 0) > 20 and b_sum.get("n", 0) > 20 else None
            row[group_type] = dict(n_choch=c_sum.get("n", 0), n_bos=b_sum.get("n", 0),
                                    choch_retest_rate=c_sum.get("retest_rate"),
                                    bos_retest_rate=b_sum.get("retest_rate"), p=p)
        k_sensitivity[str(k)] = row
    results["k_sensitivity"] = k_sensitivity

    with open("e009_choch_retest_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("split_metadata", json.dumps(meta, indent=2, default=str))
    for group_type in ["low_break", "high_break"]:
        p = results[group_type]["primary"]
        print(f"=== {group_type} === n_choch={p['choch']['n']} n_bos={p['bos']['n']}")
        print(" choch:", p["choch"])
        print(" bos:", p["bos"])
        print(" random_matched_retest_rate:", p["random_matched_retest_rate"], "n_random:", p["n_random"])
        print(" p_choch_vs_bos:", p["p_choch_vs_bos"], "p_choch_vs_random:", p["p_choch_vs_random"])


if __name__ == "__main__":
    main()
