"""Historical HTF/PDH/PDL context migration (mandat VE-ALPHA-HISTORICAL-HTF-CONTEXT-MIGRATION-001).

PROBLEM: `mtf.load_mtf()`/`s1.load_s1()`/`mstrat.load()` source H4/H1/D1 context (`h4_trend_up`,
`h1_trend_up`, `pdh`, `pdl`) from `data/market/OANDA_XAUUSD_{H1,H4,D1}.csv` -- broker-native files that
only start 2023-01-02/03. Every M15 bar before that is NaN on these fields, so S9 (both variants), S20,
and S1-PDH/PDL (both variants) produce zero signals on the 2011-2018 DEVELOPMENT window (independently
confirmed: `ctx=(h4_trend_up>0.5)` is False either way when NaN; `np.isfinite(pdh)` gates the PDH/PDL
sweep condition to False when NaN).

FIX, additive only -- `mtf.py`/`s1.py`/`mstrat.py` are BYTE-UNTOUCHED by this module (verified via git
diff in the delivery report), and their EMA20>EMA50 trend_up formula / last-closed-D1-high-low PDH-PDL
formula are REUSED UNCHANGED (imported directly, not reimplemented -- `mtf._ind`, `mtf._htf_feat`) --
only the SOURCE FILES differ: `OANDA_XAUUSD_{H1,H4,D1}_from_M15_v2.csv`, Statistician-ratified
(`config/split_manifest.json` `context_derived_htf.entries`, status `CONTEXT_DERIVED_VALIDATED`,
hash-verified against the manifest by this module at load time, not merely referenced), covering
2011-07-26 onward instead of 2023-01-03+ (already built by Data Acquisition Mandate 2.7's
`generate_htf_context.py`; this module does not regenerate them).

CRITICAL ADDITIVE SAFETY GUARD, not present in `mtf.py`/`s1.py` (never needed there, since the native
files have no internal gaps): the `_from_M15_v2` files are built under Statistician's single-discovery-
block rule -- an HTF bar exists only if ALL its constituent M15 bars belong to ONE of the four ratified
`m15_v2_discovery_blocks` (2011-07-26..2013-09-27, 2016-01-11..2018-04-06, 2020-08-11..2021-09-05,
2022-12-16..2025-10-12) -- but that rule protects only the BAR ITSELF. A plain
`pandas.merge_asof(direction='backward')` JOIN, applied naively, would still silently BRIDGE across the
~2.3-year gap between block 0 and block 1: an M15 bar from, say, 2015 would match the stale H4 bar from
~2013-09 (the last one before the gap) via ordinary backward-asof, producing a `h4_trend_up` value ~1.5
years out of date -- not future leakage, but an equally-real silent-approximation failure this mandate's
"do not approximate silently" instruction forbids. This module adds an explicit SAME-DISCOVERY-BLOCK
guard on every join: an M15 (or D1-for-PDH/PDL) row's HTF context is used ONLY if the row's own timestamp
and the matched HTF bar's own bar-start timestamp fall in the SAME ratified discovery block; otherwise
the value is NaN. This is the same fail-closed/exclude-don't-approximate principle the manifest itself
states for bar construction (`context_derived_htf.principle`), applied here at the join boundary where it
was not yet applied.

SCOPE: only `h4_trend_up`/`h1_trend_up`/`d1_trend_up` (needed by S9 both variants + S20 for h4;
S9 `conf1h=align` variant only for h1) and `pdh`/`pdl` (needed by S1-PDH/PDL both variants) are
"strictly required" per mandate SS2 (confirmed by direct code reading of `s9_setups`/`s20_setups`/
`s1_setups` in `mstrat.py` -- S20 has NO h1 dependency despite loose report phrasing; S1-PDH/PDL has NO
h4/h1 dependency at all). `load_mstrat_historical()` additionally provides a full `mstrat.load()`-schema
drop-in (adding the same gap-safety guard to `pd_open`/`pd_close`/`pw_high`/`pw_low`, which are NOT
strictly required by S9/S20/S1 but are cheap to add consistently since they reuse the same D1 source and
the same guard function) for convenience -- everything else in that schema (`rmax`/`rmin`, `fvg_bull`/
`fvg_bear`, `disp`, session, `or_high`/`or_low`, `vwap`, etc.) is M15-only and was ALREADY fully available
back to 2011 with no migration needed; this module does not touch that logic at all, it flows through
unchanged from `s1.load_s1()`/`mstrat.load()`'s own bodies via direct reuse.

NOT authorized/attempted by this module: redefining S9/S20/S1 signal logic, inventing new indicators,
evaluating profitability, tuning on the 2023+ VALIDATION window, touching `config/split_manifest.json`."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

import mtf as M  # frozen, reused unmodified: _ind, _htf_feat (not called directly -- see _htf_feat_gapsafe), D
import s1 as _s1  # frozen, reused unmodified: for M15-only columns in load_s1_historical/load_mstrat_historical

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
_MANIFEST_PATH = _ROOT / "config" / "split_manifest.json"

_CONTEXT_KEYS = {
    "h4_": ("H4_from_M15_v2", 4 * 3600),
    "h1_": ("H1_from_M15_v2", 3600),
    "d1_": ("D1_from_M15_v2", 86400),
}
_RATIFIED_CONTEXT_STATUSES = ("VALIDATED", "CONTEXT_DERIVED_VALIDATED")


class HistoricalContextError(RuntimeError):
    """Raised fail-closed: unratified/hash-mismatched context file, or a malformed discovery-block plan."""


def _sha256_lf(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_manifest() -> dict[str, Any]:
    if not _MANIFEST_PATH.is_file():
        raise HistoricalContextError(f"split manifest not found at {_MANIFEST_PATH} -- fail-closed")
    return json.loads(_MANIFEST_PATH.read_bytes())


def discovery_blocks() -> list[tuple[int, int]]:
    """The four Statistician-ratified `m15_v2_discovery_blocks`, verbatim from the manifest -- the SAME
    canonical set `edge_research._common.load()` uses for M15_v2 gating (cross-checked this mandate)."""
    manifest = _load_manifest()
    blocks = manifest["context_derived_htf"]["m15_v2_discovery_blocks"]
    out = [(int(b["start_epoch"]), int(b["end_epoch"])) for b in blocks]
    if not out:
        raise HistoricalContextError("manifest m15_v2_discovery_blocks is empty -- fail-closed")
    return out


def _verify_context_file(tf_key: str) -> str:
    """Resolve+verify one `_from_M15_v2` context entry: status must be ratified, and the physical file's
    sha256 must match the manifest exactly -- fail-closed on any mismatch, missing entry, or missing file.
    Mirrors `edge_research.split_manifest.context_entry_file`+`verify_data_file`'s exact verification
    principle (status gate + byte-exact hash check), reimplemented locally (not cross-imported) to keep
    this module self-contained within the `code/` ecosystem `mtf.py`/`s1.py`/`mstrat.py` already live in --
    this is integrity-check boilerplate, not a reimplemented INDICATOR or SIGNAL."""
    manifest = _load_manifest()
    entries = manifest.get("context_derived_htf", {}).get("entries", {})
    entry = entries.get(tf_key)
    if not isinstance(entry, dict):
        raise HistoricalContextError(f"{tf_key!r} not found in context_derived_htf.entries -- fail-closed")
    status = entry.get("status")
    if status not in _RATIFIED_CONTEXT_STATUSES:
        raise HistoricalContextError(
            f"{tf_key!r} has status {status!r}, not ratified {_RATIFIED_CONTEXT_STATUSES} -- fail-closed")
    file_path = entry.get("file_path")
    expected = (entry.get("data_file_sha256") or {}).get("value")
    if not isinstance(file_path, str) or not isinstance(expected, str) or len(expected) != 64:
        raise HistoricalContextError(f"{tf_key!r} missing file_path/data_file_sha256 -- fail-closed")
    abspath = str(_ROOT / file_path)
    if not os.path.isfile(abspath):
        raise HistoricalContextError(f"{tf_key!r} data file not found at {abspath} -- fail-closed")
    got = _sha256_lf(abspath)
    if got != expected:
        raise HistoricalContextError(
            f"{tf_key!r} hash mismatch: manifest expects {expected}, file has {got} -- fail-closed "
            "(the manifest<->disk binding is broken; do not proceed)")
    return abspath


def _block_index_vec(epochs: np.ndarray, blocks: list[tuple[int, int]]) -> np.ndarray:
    """Vectorized discovery-block membership: block index per epoch, -1 if in no ratified block."""
    out = np.full(len(epochs), -1, dtype=np.int64)
    for i, (s, e) in enumerate(blocks):
        out[(epochs >= s) & (epochs < e)] = i
    return out


def _htf_feat_gapsafe(path: str, period: int) -> pd.DataFrame:
    """Mirrors `mtf._htf_feat` EXACTLY (same `mtf._ind()` call -> same EMA20>EMA50 trend_up formula, same
    `avail=time.shift(-1)` causal-availability convention, same last-row `avail=last_time+period`
    extrapolation) -- the ONLY addition is capturing each bar's own `time` (its true start, BEFORE any
    avail-shifting) as `orig_bar_start`, needed by the caller to apply the same-discovery-block join
    guard. `mtf._htf_feat` itself is called nowhere in this function; its formula is inlined via direct
    reuse of `mtf._ind` to avoid re-reading the CSV twice, but is otherwise byte-identical."""
    df = pd.read_csv(path)
    ind = M._ind(df)
    df["trend_up"] = ind["trend_up"]
    df["volrank"] = ind["volrank"]
    df["rsi"] = ind["rsi"]
    df["orig_bar_start"] = df["time"]
    df["avail"] = df["time"].shift(-1)
    df.loc[df.index[-1], "avail"] = df["time"].iloc[-1] + period
    df["avail"] = df["avail"].astype("int64")
    return df[["avail", "orig_bar_start", "trend_up", "volrank", "rsi"]]


def _merge_gapsafe(base: pd.DataFrame, htf: pd.DataFrame, value_cols: list[str],
                   blocks: list[tuple[int, int]]) -> pd.DataFrame:
    """`merge_asof(direction='backward')` on `time`<->`avail`, exactly like `mtf.load_mtf`/`s1.load_s1`,
    THEN nulls out every value column on any row where the base row's own discovery block differs from
    the matched HTF bar's own discovery block -- see module docstring for why this is required in
    addition to (not instead of) the single-discovery-block rule already applied when the `_from_M15_v2`
    files were built."""
    merged = pd.merge_asof(base.sort_values("time"), htf.sort_values("avail"),
                           left_on="time", right_on="avail", direction="backward")
    base_block = _block_index_vec(merged["time"].to_numpy(), blocks)
    orig = merged["orig_bar_start"].to_numpy()
    valid = ~np.isnan(orig)
    htf_block = np.full(len(merged), -1, dtype=np.int64)
    htf_block[valid] = _block_index_vec(orig[valid].astype("int64"), blocks)
    same_block = (base_block == htf_block) & (base_block >= 0)
    for col in value_cols:
        merged.loc[~same_block, col] = np.nan
    return merged.drop(columns=["avail", "orig_bar_start"])


def load_mtf_historical() -> pd.DataFrame:
    """Mirrors `mtf.load_mtf()` EXACTLY (same M15 load, same `mtf._ind()` M15-level indicators, same
    session bucketing) except the H4/H1/D1 loop sources `_from_M15_v2` (hash-verified, gap-safe-joined)
    instead of the native 2023+-only files."""
    blocks = discovery_blocks()
    m = pd.read_csv(M.D + r"\OANDA_XAUUSD_M15.csv").drop_duplicates("time").sort_values("time").reset_index(drop=True)
    ind = M._ind(m)
    for k in ["atr", "ema20", "ema50", "rsi", "sma", "std", "volrank", "trend_up"]:
        m["m_" + k] = ind[k]
    hh = pd.to_datetime(m["time"], unit="s", utc=True).dt.hour
    m["session"] = np.select([hh < 8, hh < 13, hh < 21], ["asia", "london", "ny"], default="late")
    for prefix, (tf_key, period) in _CONTEXT_KEYS.items():
        path = _verify_context_file(tf_key)
        htf = _htf_feat_gapsafe(path, period)
        htf = htf.rename(columns={"trend_up": prefix + "trend_up", "volrank": prefix + "volrank",
                                  "rsi": prefix + "rsi"})
        m = _merge_gapsafe(m, htf, [prefix + "trend_up", prefix + "volrank", prefix + "rsi"], blocks)
    return m.reset_index(drop=True)


def load_s1_historical() -> pd.DataFrame:
    """Mirrors `s1.load_s1()` EXACTLY -- same rmax/rmin/session-block/FVG/disp/roc3/bull-bear-close M15-
    only columns (all fully available back to 2011 already, untouched here) -- except `load_mtf_historical`
    supplies the base frame, and the PDH/PDL merge is gap-safe-joined against `D1_from_M15_v2`."""
    blocks = discovery_blocks()
    d = load_mtf_historical()
    d1_path = _verify_context_file("D1_from_M15_v2")
    d1 = pd.read_csv(d1_path)
    d1["orig_bar_start"] = d1["time"]
    d1["avail"] = d1["time"].shift(-1)
    d1.loc[d1.index[-1], "avail"] = d1["time"].iloc[-1] + 86400
    d1["avail"] = d1["avail"].astype("int64")
    d1r = d1[["avail", "orig_bar_start", "high", "low"]].rename(columns={"high": "pdh", "low": "pdl"})
    d = _merge_gapsafe(d, d1r, ["pdh", "pdl"], blocks)

    h, l, c, o = d["high"], d["low"], d["close"], d["open"]
    for L in (20, 50):
        d[f"rmax{L}"] = h.rolling(L).max().shift(1)
        d[f"rmin{L}"] = l.rolling(L).min().shift(1)
    sess = d["session"].values
    blk = np.concatenate([[0], np.cumsum(sess[1:] != sess[:-1])])
    d["blk"] = blk
    d["sess_high"] = h.groupby(d["blk"]).cummax().shift(1)
    d["sess_low"] = l.groupby(d["blk"]).cummin().shift(1)
    d["fvg_bull"] = (l > h.shift(2)).astype(float)
    d["fvg_bear"] = (h < l.shift(2)).astype(float)
    d["disp"] = ((h - l) > 1.5 * d["m_atr"]).astype(float)
    d["roc3"] = c / c.shift(3) - 1
    d["bear_close"] = (c < o).astype(float)
    d["bull_close"] = (c > o).astype(float)
    return d.reset_index(drop=True)


def load_mstrat_historical() -> pd.DataFrame:
    """Mirrors `mstrat.load()` EXACTLY -- `atr_ma`/`compress`/`or_high`/`or_low`/`bar_in_sess`/
    `prev_sess_high`/`prev_sess_low`/`vwap`/`prev_sess_close`/`gap` are M15-only (untouched here) --
    except `load_s1_historical` supplies the base frame, and the `pd_open`/`pd_close`/`pw_high`/`pw_low`
    D1-sourced merges (NOT strictly required by S9/S20/S1 -- see module docstring -- but cheap to make
    consistent since they reuse the same D1 source and the same gap-safety guard) are gap-safe-joined."""
    blocks = discovery_blocks()
    d = load_s1_historical()
    c, h, l = d["close"], d["high"], d["low"]
    d["atr_ma"] = d["m_atr"].rolling(50).mean()
    d["compress"] = (d["m_atr"] < 0.8 * d["atr_ma"]).astype(float)
    g = d.groupby("blk")
    d["or_high"] = g["high"].transform(lambda x: x.iloc[:4].max())
    d["or_low"] = g["low"].transform(lambda x: x.iloc[:4].min())
    d["bar_in_sess"] = g.cumcount()
    bh = g["high"].max()
    bl = g["low"].min()
    d["prev_sess_high"] = d["blk"].map(bh.shift(1))
    d["prev_sess_low"] = d["blk"].map(bl.shift(1))
    tp = (h + l + c) / 3
    pv = tp * d["volume"]
    d["vwap"] = pv.groupby(d["blk"]).cumsum() / d["volume"].groupby(d["blk"]).cumsum().replace(0, np.nan)

    d1_path = _verify_context_file("D1_from_M15_v2")
    d1 = pd.read_csv(d1_path)
    d1["orig_bar_start"] = d1["time"]
    d1["avail"] = d1["time"].shift(-1)
    d1.loc[d1.index[-1], "avail"] = d1["time"].iloc[-1] + 86400
    d1["avail"] = d1["avail"].astype("int64")
    d1r = d1[["avail", "orig_bar_start", "open", "close"]].rename(columns={"open": "pd_open", "close": "pd_close"})
    d = _merge_gapsafe(d, d1r, ["pd_open", "pd_close"], blocks)
    d["pd_mid"] = (d["pdh"] + d["pdl"]) / 2

    w = pd.read_csv(d1_path)
    w["dt"] = pd.to_datetime(w["time"], unit="s", utc=True)
    wk = w.set_index("dt").resample("W").agg(high=("high", "max"), low=("low", "min")).dropna().reset_index()
    wk["orig_bar_start"] = ((wk["dt"] - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)).astype("int64")
    wk["avail"] = wk["orig_bar_start"]
    wkr = wk[["avail", "orig_bar_start", "high", "low"]].rename(columns={"high": "pw_high", "low": "pw_low"})
    d = _merge_gapsafe(d, wkr, ["pw_high", "pw_low"], blocks)

    d["prev_sess_close"] = d["blk"].map(g["close"].last().shift(1))
    d["gap"] = np.where(d["bar_in_sess"] == 0, d["open"] - d["prev_sess_close"], np.nan)
    return d.reset_index(drop=True)
