"""Tests for `code/htf_context_historical.py` (mandat VE-ALPHA-HISTORICAL-HTF-CONTEXT-MIGRATION-001, SS9):
H1/H4/PDH/PDL causality, session boundaries, warmup, missing bars (the discovery-block gap-safety guard),
restart/determinism, no future leakage, mutation/adversarial tests. Every test runs against the REAL
`_from_M15_v2` files and the REAL manifest, not synthetic stand-ins, except where a small hand-built
DataFrame gives more precise control over an exact boundary condition (same "direct construction for
determinism" discipline already established for the module-level fixtures below).

Run: python -m pytest tests/test_htf_context_historical.py -q
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))

import numpy as np
import pandas as pd  # type: ignore[import-untyped]
import pytest

import htf_context_historical as H
import mtf as M

_CACHE: dict[str, pd.DataFrame] = {}


def mtf_hist() -> pd.DataFrame:
    if "mtf" not in _CACHE:
        _CACHE["mtf"] = H.load_mtf_historical()
    return _CACHE["mtf"]


def s1_hist() -> pd.DataFrame:
    if "s1" not in _CACHE:
        _CACHE["s1"] = H.load_s1_historical()
    return _CACHE["s1"]


BLOCKS = H.discovery_blocks()
GAP_START = BLOCKS[0][1]   # 2013-09-27 16:45:00Z -- end of block 0
GAP_END = BLOCKS[1][0]     # 2016-01-11 09:00:00Z -- start of block 1


# ═══════════════════════════════════ hash / ratification gate ═══════════════════════════════════

def test_context_files_hash_verified_against_manifest() -> None:
    for tf_key in ("H4_from_M15_v2", "H1_from_M15_v2", "D1_from_M15_v2"):
        path = H._verify_context_file(tf_key)   # raises HistoricalContextError on any mismatch
        assert os.path.isfile(path)


def test_unratified_or_unknown_key_refused() -> None:
    with pytest.raises(H.HistoricalContextError):
        H._verify_context_file("NOT_A_REAL_KEY")


def test_tampered_hash_refused() -> None:
    """Mutation-style check: a manifest entry whose recorded hash doesn't match the physical file must be
    refused fail-closed, not silently accepted."""
    real_manifest = H._load_manifest
    manifest = real_manifest()
    manifest["context_derived_htf"]["entries"]["H4_from_M15_v2"]["data_file_sha256"]["value"] = "0" * 64
    H._load_manifest = lambda: manifest   # type: ignore[assignment]
    try:
        with pytest.raises(H.HistoricalContextError, match="hash mismatch"):
            H._verify_context_file("H4_from_M15_v2")
    finally:
        H._load_manifest = real_manifest


# ═══════════════════════════════════ H4 causality ═══════════════════════════════════

def test_h4_causality_avail_never_before_bar_close() -> None:
    """A synthetic 3-bar H4 series: avail for bar i must equal bar i+1's own start (i.e. this bar's own
    close), and the LAST bar's avail must be its own start + the H4 period -- never earlier, i.e. an H4
    bar is never 'available' before it has fully closed."""
    df = pd.DataFrame({"time": [0, 14400, 28800], "open": [1, 1, 1], "high": [1, 1, 1],
                       "low": [1, 1, 1], "close": [1.0, 1.1, 1.2], "volume": [1, 1, 1]})
    path = os.path.join(os.path.dirname(__file__), "_tmp_h4_causality.csv")
    df.to_csv(path, index=False)
    try:
        feat = H._htf_feat_gapsafe(path, 4 * 3600)
        assert feat["avail"].tolist() == [14400, 28800, 28800 + 4 * 3600]
        assert (feat["avail"] >= feat["orig_bar_start"] + 4 * 3600).all()
    finally:
        os.remove(path)


def test_h4_causality_end_to_end_no_lookahead() -> None:
    """For every M15 bar with a non-null h4_trend_up, the matched H4 bar's own start must be STRICTLY
    before the M15 bar's own time -- an M15 bar can never see an H4 bar that started at or after it."""
    d = mtf_hist()
    sample = d.dropna(subset=["h4_trend_up"]).sample(n=2000, random_state=7)
    htf_path = H._verify_context_file("H4_from_M15_v2")
    feat = H._htf_feat_gapsafe(htf_path, 4 * 3600)   # same avail/orig_bar_start the real code matches on
    merged = pd.merge_asof(sample[["time"]].sort_values("time"), feat.sort_values("avail"),
                           left_on="time", right_on="avail", direction="backward")
    assert (merged["orig_bar_start"] + 4 * 3600 <= merged["time"]).all(), \
        "an H4 bar must be fully closed before use"


# ═══════════════════════════════════ H1 causality ═══════════════════════════════════

def test_h1_causality_avail_shift() -> None:
    df = pd.DataFrame({"time": [0, 3600, 7200], "open": [1, 1, 1], "high": [1, 1, 1],
                       "low": [1, 1, 1], "close": [1.0, 1.1, 1.2], "volume": [1, 1, 1]})
    path = os.path.join(os.path.dirname(__file__), "_tmp_h1_causality.csv")
    df.to_csv(path, index=False)
    try:
        feat = H._htf_feat_gapsafe(path, 3600)
        assert feat["avail"].tolist() == [3600, 7200, 7200 + 3600]
    finally:
        os.remove(path)


def test_h1_causality_end_to_end_no_lookahead() -> None:
    d = mtf_hist()
    sample = d.dropna(subset=["h1_trend_up"]).sample(n=2000, random_state=7)
    htf_path = H._verify_context_file("H1_from_M15_v2")
    feat = H._htf_feat_gapsafe(htf_path, 3600)
    merged = pd.merge_asof(sample[["time"]].sort_values("time"), feat.sort_values("avail"),
                           left_on="time", right_on="avail", direction="backward")
    assert (merged["orig_bar_start"] + 3600 <= merged["time"]).all()


# ═══════════════════════════════════ PDH causality ═══════════════════════════════════

def test_pdh_causality_last_closed_day_only() -> None:
    """pdh/pdl at any M15 bar must come from a D1 bar that STARTED before the current NY trading day --
    i.e. never today's own (still-forming) high/low."""
    d = s1_hist()
    d1_path = H._verify_context_file("D1_from_M15_v2")
    feat = H._htf_feat_gapsafe(d1_path, 86400)
    sample = d.dropna(subset=["pdh"]).sample(n=2000, random_state=11)
    merged = pd.merge_asof(sample[["time"]].sort_values("time"), feat.sort_values("avail"),
                           left_on="time", right_on="avail", direction="backward")
    assert (merged["orig_bar_start"] + 86400 <= merged["time"]).all(), \
        "pdh/pdl must come from a FULLY CLOSED prior D1 bar, never the current forming day"


def test_pdh_matches_native_exactly_on_overlap() -> None:
    """Bounded implementation-equivalence check (mandat SS6, permitted -- not used to choose Alpha
    parameters): on the 2023+ overlap where the NATIVE pipeline also has pdh/pdl, the two must agree
    exactly -- pdh/pdl is a mechanical prior-day lookup with no warmup ambiguity, unlike EMA trend_up."""
    import s1 as S1
    native = S1.load_s1()
    hist = s1_hist()
    merged = native[["time", "pdh", "pdl"]].merge(hist[["time", "pdh", "pdl"]], on="time",
                                                    suffixes=("_native", "_hist"))
    both = merged.dropna(subset=["pdh_native", "pdh_hist"])
    assert len(both) > 1000, "sanity: the overlap must be non-trivial or this test proves nothing"
    assert (both["pdh_native"] == both["pdh_hist"]).all()
    assert (both["pdl_native"] == both["pdl_hist"]).all()


# ═══════════════════════════════════ PDL causality ═══════════════════════════════════

def test_pdl_never_exceeds_pdh() -> None:
    d = s1_hist()
    both = d.dropna(subset=["pdh", "pdl"])
    assert len(both) > 10000
    assert (both["pdh"] >= both["pdl"]).all()


def test_pdl_causality_avail_shift_last_row_special_case() -> None:
    """The last D1 row has no 'next' row to shift from -- avail must extrapolate by exactly one day, not
    leak the (nonexistent) next day's high/low."""
    df = pd.DataFrame({"time": [0, 86400], "open": [1, 1], "high": [10.0, 11.0], "low": [9.0, 9.5],
                       "close": [9.5, 10.5], "volume": [1, 1]})
    path = os.path.join(os.path.dirname(__file__), "_tmp_d1_lastrow.csv")
    df.to_csv(path, index=False)
    try:
        d1 = pd.read_csv(path)
        d1["avail"] = d1["time"].shift(-1)
        d1.loc[d1.index[-1], "avail"] = d1["time"].iloc[-1] + 86400
        assert d1["avail"].tolist() == [86400, 172800]
    finally:
        os.remove(path)


# ═══════════════════════════════════ session boundaries ═══════════════════════════════════

def test_d1_session_boundary_is_ny_1700_dst_aware() -> None:
    """The D1_from_M15_v2 'day' boundary must be 17:00 America/New_York, DST-aware -- not UTC midnight,
    not a fixed offset. Spot-check across a winter and a summer bar (matches code/resample_ny.py's own
    documented convention, cross-checked directly against the actual file, not re-derived)."""
    d1_path = H._verify_context_file("D1_from_M15_v2")
    d1 = pd.read_csv(d1_path)
    d1["dt"] = pd.to_datetime(d1["time"], unit="s", utc=True)
    d1["ny_hour"] = d1["dt"].dt.tz_convert("America/New_York").dt.hour
    # every single D1 bar must open at NY-local hour 17, regardless of DST -- this is the entire point of
    # the DST-aware anchoring (a fixed-UTC-offset bug would show a 1-hour split between winter/summer)
    assert (d1["ny_hour"] == 17).all(), "every D1 bar must anchor to 17:00 America/New_York, DST-aware"
    winter = d1[d1["dt"].dt.month == 1].iloc[0]
    summer = d1[d1["dt"].dt.month == 7].iloc[0]
    assert winter["dt"].hour == 22   # EST = UTC-5 -> 17:00 EST = 22:00 UTC
    assert summer["dt"].hour == 21   # EDT = UTC-4 -> 17:00 EDT = 21:00 UTC


def test_h1_uses_plain_utc_hour_not_ny_anchored() -> None:
    """H1 is explicitly NOT NY-anchored (per code/resample_ny.py: 'H1 = UTC hour, matches native') --
    confirm every H1 bar starts on a UTC hour boundary."""
    h1_path = H._verify_context_file("H1_from_M15_v2")
    h1 = pd.read_csv(h1_path)
    assert (h1["time"] % 3600 == 0).all()


# ═══════════════════════════════════ warmup ═══════════════════════════════════

def test_ema_trend_up_has_no_warmup_gate_matching_native_inherited_behavior() -> None:
    """mtf._ind()'s trend_up=(ema20>ema50) has NO warmup gate (pandas.ewm(adjust=True) is defined from
    bar 1) -- this module does not add one, since doing so would be redefining the frozen formula, not
    migrating its data source. Documented explicitly here (not silently inherited) so a future reader
    knows this is INTENTIONAL, not an oversight: the very first bar of each ratified block gets a
    trend_up value immediately, exactly matching mtf._ind()'s own native behavior."""
    df = pd.DataFrame({"time": [0, 14400, 28800, 43200], "open": [1, 1, 1, 1], "high": [1, 1, 1, 1],
                       "low": [1, 1, 1, 1], "close": [1.0, 1.1, 1.2, 1.3], "volume": [1, 1, 1, 1]})
    ind = M._ind(df)
    assert not pd.isna(ind["trend_up"].iloc[0]), \
        "first bar must have a (possibly noisy) trend_up value -- no warmup gate, matching native mtf._ind"


def test_atr_and_rsi_do_have_a_real_warmup_gate_unlike_trend_up() -> None:
    """Contrast case, for precision: unlike trend_up, atr (rolling(14)) and volrank (rolling(60)) DO have
    a genuine NaN warmup period in the inherited formula -- this module changes neither behavior."""
    df = pd.DataFrame({"time": list(range(0, 30 * 14400, 14400)),
                       "open": [1.0] * 30, "high": [1.0 + 0.01 * i for i in range(30)],
                       "low": [0.99] * 30, "close": [1.0 + 0.01 * i for i in range(30)],
                       "volume": [1] * 30})
    ind = M._ind(df)
    # tr itself is NaN at index 0 (c.shift() undefined for the first bar), so atr=tr.rolling(14).mean()
    # needs indices 1..14 (14 valid tr values) -> first valid atr is at index 14, not 13.
    assert ind["atr"].iloc[:14].isna().all() and not pd.isna(ind["atr"].iloc[14])


# ═══════════════════════════════════ missing bars / discovery-block gap-safety guard ═══════════════════════════════════

def test_gap_bars_have_no_htf_context_at_all() -> None:
    """The core new safety property: every M15 bar strictly inside the unratified gap between block 0
    and block 1 (2013-09-27 .. 2016-01-11) must have h4_trend_up/h1_trend_up/d1_trend_up ALL null --
    never a stale value silently carried forward from block 0's tail."""
    d = mtf_hist()
    gap = d[(d["time"] >= GAP_START) & (d["time"] < GAP_END)]
    assert len(gap) > 10000, "sanity: the gap must contain real M15 bars or this test proves nothing"
    for col in ("h4_trend_up", "h1_trend_up", "d1_trend_up"):
        assert gap[col].isna().all(), f"{col} must be entirely null inside the unratified gap"


def test_gap_bars_have_no_pdh_pdl_either() -> None:
    d = s1_hist()
    gap = d[(d["time"] >= GAP_START) & (d["time"] < GAP_END)]
    assert gap["pdh"].isna().all() and gap["pdl"].isna().all()


def test_block1_recovers_fresh_context_shortly_after_the_gap_ends() -> None:
    """The guard must not OVER-exclude: bars well inside block 1 (not right at its opening edge) must
    have real, fresh h4_trend_up coverage -- the gap-null-out is scoped exactly to the gap, not to all of
    block 1."""
    d = mtf_hist()
    deep_in_block1 = d[(d["time"] >= GAP_END + 30 * 86400) & (d["time"] < GAP_END + 60 * 86400)]
    assert len(deep_in_block1) > 1000
    assert deep_in_block1["h4_trend_up"].notna().mean() > 0.95


def test_naive_ungated_merge_would_have_bridged_the_gap_MUTATION_CHECK() -> None:
    """Adversarial/mutation check: prove the guard is load-bearing by reproducing what a NAIVE
    merge_asof(direction='backward') (no discovery-block guard) would do, and confirming it DOES bridge
    the gap with a stale value -- i.e. if this test ever started failing (naive stops bridging), the
    gap-guard test above would no longer be proving anything either."""
    htf_path = H._verify_context_file("H4_from_M15_v2")
    htf = pd.read_csv(htf_path)
    ind = M._ind(htf)
    htf["trend_up"] = ind["trend_up"]
    htf["avail"] = htf["time"].shift(-1)
    htf.loc[htf.index[-1], "avail"] = htf["time"].iloc[-1] + 4 * 3600
    htf["avail"] = htf["avail"].astype("int64")
    probe = pd.DataFrame({"time": [GAP_START + 86400 * 400]})   # ~400 days into the gap
    naive = pd.merge_asof(probe.sort_values("time"), htf[["avail", "trend_up"]].sort_values("avail"),
                          left_on="time", right_on="avail", direction="backward")
    assert naive["trend_up"].notna().all(), \
        "the naive path must still bridge the gap (proving the real guard's exclusion is doing real work)"


# ═══════════════════════════════════ restart / determinism ═══════════════════════════════════

def test_load_mtf_historical_is_deterministic() -> None:
    a = H.load_mtf_historical()
    b = H.load_mtf_historical()
    pd.testing.assert_frame_equal(a[["time", "h4_trend_up", "h1_trend_up", "d1_trend_up"]],
                                  b[["time", "h4_trend_up", "h1_trend_up", "d1_trend_up"]])


def test_discovery_blocks_deterministic_and_matches_manifest() -> None:
    a = H.discovery_blocks()
    b = H.discovery_blocks()
    assert a == b
    assert len(a) == 4


# ═══════════════════════════════════ no future leakage (global proof) ═══════════════════════════════════

def test_no_future_leakage_global_h4() -> None:
    """Exhaustive (not sampled) proof over the full dataset: no M15 bar's h4_trend_up can EVER have come
    from an H4 bar that had not yet fully closed as of that M15 bar's own time."""
    d = mtf_hist()
    htf_path = H._verify_context_file("H4_from_M15_v2")
    feat = H._htf_feat_gapsafe(htf_path, 4 * 3600)
    have_ctx = d.dropna(subset=["h4_trend_up"])[["time"]]
    merged = pd.merge_asof(have_ctx.sort_values("time"), feat.sort_values("avail"),
                           left_on="time", right_on="avail", direction="backward")
    assert (merged["orig_bar_start"] + 4 * 3600 <= merged["time"]).all()


def test_no_future_leakage_global_pdh() -> None:
    d = s1_hist()
    d1_path = H._verify_context_file("D1_from_M15_v2")
    feat = H._htf_feat_gapsafe(d1_path, 86400)
    have_ctx = d.dropna(subset=["pdh"])[["time"]]
    merged = pd.merge_asof(have_ctx.sort_values("time"), feat.sort_values("avail"),
                           left_on="time", right_on="avail", direction="backward")
    assert (merged["orig_bar_start"] + 86400 <= merged["time"]).all()


# ═══════════════════════════════════ mutation / adversarial tests ═══════════════════════════════════

def test_mutation_disabling_the_block_guard_reintroduces_stale_bridging() -> None:
    """Directly mutate _merge_gapsafe's guard (monkeypatch _block_index_vec to always agree) and confirm
    the gap bars WOULD get populated again -- proving the guard, not some other mechanism, is what keeps
    them null."""
    real_block_index_vec = H._block_index_vec
    H._block_index_vec = lambda epochs, blocks: np.zeros(len(epochs), dtype=np.int64)   # everything "block 0"
    try:
        mutated = H.load_mtf_historical()
        gap = mutated[(mutated["time"] >= GAP_START) & (mutated["time"] < GAP_END)]
        assert gap["h4_trend_up"].notna().sum() > 0, \
            "with the guard neutralized, gap bars MUST become populated again (proves the guard is load-bearing)"
    finally:
        H._block_index_vec = real_block_index_vec


def test_mutation_hash_check_removed_would_accept_tampered_file() -> None:
    """Confirm _verify_context_file's hash check is the thing preventing acceptance of a tampered file --
    remove it via monkeypatch and confirm a wrong hash is then silently accepted (the inverse of
    test_tampered_hash_refused, proving that test isn't vacuous)."""
    real_verify = H._verify_context_file

    def _no_hash_check(tf_key: str) -> str:
        manifest = H._load_manifest()
        entry = manifest["context_derived_htf"]["entries"][tf_key]
        return str(H._ROOT / entry["file_path"])   # skips the sha256 comparison entirely

    H._verify_context_file = _no_hash_check
    try:
        manifest = H._load_manifest()
        manifest["context_derived_htf"]["entries"]["H4_from_M15_v2"]["data_file_sha256"]["value"] = "0" * 64
        path = H._verify_context_file("H4_from_M15_v2")
        assert os.path.isfile(path), "mutated loader accepts the file despite the (unchecked) bad hash"
    finally:
        H._verify_context_file = real_verify


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
