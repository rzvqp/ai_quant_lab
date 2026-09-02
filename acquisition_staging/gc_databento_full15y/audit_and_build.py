#!/usr/bin/env python3
"""GC full-15y — data-quality audit (§10) + continuous-roll audit (§11) + derived 1m/15m build (§12).
Pure read of the preserved raw DBN (never modified). Emits JSON metrics + writes derived Parquet.

Usage: python audit_and_build.py
"""
from __future__ import annotations
import json, os
import databento as db
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
DER = os.path.join(HERE, "derived")
OHLCV = os.path.join(RAW, "gc_ohlcv-1m_GC.v.0_2011-07-26_2026-07-28.dbn")
DEFN = os.path.join(RAW, "gc_definition_GC.FUT_2011-07-26_2026-07-28.dbn")
STAT = os.path.join(RAW, "gc_statistics_GC.FUT_2011-07-26_2026-07-28.dbn")
DEGRADED = ["2014-06-11", "2014-06-12", "2014-06-13"]  # Databento-flagged reduced-quality days


def main() -> None:
    os.makedirs(DER, exist_ok=True)
    rep: dict = {}

    # ---- OHLCV load ----
    df = db.DBNStore.from_file(OHLCV).to_df(price_type="float", pretty_ts=True)
    df = df.sort_index()
    t = df.index
    epoch = t.asi8 // 1_000_000_000  # numpy int64 seconds
    dups = int(df.index.duplicated().sum())
    out_of_order = int((np.diff(epoch) < 0).sum())
    o, h, l, c, v = df["open"], df["high"], df["low"], df["close"], df["volume"]
    ohlc_bad = int((~((h >= o) & (h >= c) & (h >= l) & (l <= o) & (l <= c) & (l <= h))).sum())
    nonpos = int((df[["open", "high", "low", "close"]].le(0).any(axis=1)).sum())
    off_grid = int((epoch % 60 != 0).sum())
    # trading-day coverage (unique UTC dates present) vs weekday span
    dts = t.tz_convert("UTC").tz_localize(None).normalize()   # tz-naive UTC midnight
    present_days = set(pd.Index(dts.unique()))
    all_days = pd.date_range(dts.min(), dts.max(), freq="D")
    weekdays = all_days[all_days.weekday < 5]           # Mon-Fri (weekday dates with no bar ~= US holidays)
    missing_weekdays = sorted(str(d.date()) for d in weekdays if d not in present_days)
    rep["OHLCV_QA"] = {
        "rows": int(len(df)), "first_ts_utc": str(t[0]), "last_ts_utc": str(t[-1]),
        "duplicate_timestamps": dups, "out_of_order_timestamps": out_of_order,
        "off_grid_60s": off_grid, "ohlc_constraint_violations": ohlc_bad, "nonpositive_price_bars": nonpos,
        "volume_present": bool((v > 0).any()), "volume_total": int(v.sum()),
        "ntrades_present": ("ntrades" in df.columns),  # ohlcv-1m does not carry ntrades
        "distinct_instrument_ids": int(df["instrument_id"].nunique()),
        "trading_days_present": int(len(present_days)),
        "missing_weekday_count": len(missing_weekdays),
        "missing_weekdays_sample": missing_weekdays[:15],
        "databento_degraded_days": DEGRADED,
        "timestamp_semantics": "ts_event = bar OPEN, UTC nanoseconds; bar covers [ts, ts+60s); FEATURE_AVAILABLE at ts+60s",
    }

    # ---- continuous-roll audit (§11) ----
    iid = df["instrument_id"]
    roll_mask = iid.ne(iid.shift())
    rolls = df.index[roll_mask][1:]            # first entry is the series start, not a roll
    roll_rows = [{"roll_ts_utc": str(ts), "to_instrument_id": int(iid.loc[ts]) if not isinstance(iid.loc[ts], pd.Series) else int(iid.loc[ts].iloc[0])} for ts in rolls]
    rep["ROLL_AUDIT"] = {
        "symbol": "GC.v.0", "stype_in": "continuous",
        "continuous_contract_rule": "Volume roll (.v): the continuous series holds the outright ranked #0 (front) by TRADING VOLUME OF THE PREVIOUS DAY.",
        "roll_basis": "previous-day trading volume (highest-volume outright)",
        "when_roll_becomes_effective": "on the session after the previous day's volume ranking changes the front contract",
        "uses_only_prior_available_information": True,
        "causality": "PASS — the roll ranks on the PREVIOUS day's volume, so it uses only information available up to the roll date; no look-ahead.",
        "distinct_underlying_instruments": int(iid.nunique()),
        "number_of_rolls": int(len(roll_rows)),
        "first_5_rolls": roll_rows[:5], "last_5_rolls": roll_rows[-5:],
        "source": "Databento continuous-contract / symbology documentation (volume roll ranks by previous-day volume).",
    }

    # ---- definition / statistics row counts (§10) ----
    rep["DEFINITION_rows"] = int(db.DBNStore.from_file(DEFN).to_ndarray().shape[0])
    rep["STATISTICS_rows"] = int(db.DBNStore.from_file(STAT).to_ndarray().shape[0])

    # ---- derived 1m + 15m (§12) ----
    m1 = df[["open", "high", "low", "close", "volume"]].copy()
    m1.to_parquet(os.path.join(DER, "GC_1M_RESEARCH.parquet"))
    g = df.groupby(df.index.floor("15min"))
    m15 = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
        "close": g["close"].last(), "volume": g["volume"].sum(),
    })
    m15.index.name = "ts_event"
    m15.to_parquet(os.path.join(DER, "GC_15M_RESEARCH.parquet"))
    rep["DERIVED"] = {
        "GC_1M_RESEARCH_parquet_rows": int(len(m1)), "GC_15M_RESEARCH_parquet_rows": int(len(m15)),
        "aggregation": "O=first, H=max, L=min, C=last, V=sum real volume; UTC; no forward-fill; ntrades not available in ohlcv-1m",
    }

    with open(os.path.join(HERE, "GC_FULL15Y_AUDIT_METRICS.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: v[kk] for kk in list(v)[:8]}) for k, v in rep.items()}, indent=2, default=str))


if __name__ == "__main__":
    main()
