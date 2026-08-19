"""
CEO_ASSISTED_SYNTHETIC_CONSTRUCTION_ONLY
CIRCULAR_LABEL_DERIVED_BARS
ZERO_VALIDATION_WEIGHT

Teste pt. componenta A (reproducerea sintetică istorică) -- mandat "PACHET REPRODUCTIBIL", §11
item 1 ("reproducerea cifrelor sintetice")."""
from __future__ import annotations

import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PKG_DIR))

from run_construction import (  # noqa: E402
    FROZEN_CONFIG_ID, FROZEN_HASHES, REPORTED, check_historical_reproduction, run_all,
)


def test_frozen_hashes_match_current_files() -> None:
    """Prototipul importat de acest pachet e byte-identic cu f224e7d -- verificat direct, nu doar
    citat. Dacă acest test EȘUEAZĂ, detectorul a fost modificat de la înghețul citat de mandat."""
    import hashlib
    ve_dir = _PKG_DIR.parent / "ve_n1_replay"
    for fname, expected in FROZEN_HASHES.items():
        actual = hashlib.sha256((ve_dir / fname).read_bytes()).hexdigest()
        assert actual == expected, f"{fname}: {actual} != {expected} (detectorul a fost modificat)"


def test_config_id_matches_frozen() -> None:
    import sys as _s
    _s.path.insert(0, str(_PKG_DIR.parent))
    from ve_n1_replay.range_semantic_v4_3 import ConfigV43
    assert ConfigV43().config_id() == FROZEN_CONFIG_ID


def test_48_windows_13824_bars_correct_denominators() -> None:
    result = run_all()
    assert len(result["per_window"]) == 48
    total_bars = sum(pw["window_bars"] for pw in result["per_window"].values())
    assert total_bars == 13824
    assert result["macro_gt_count"] == 88
    assert result["internal_gt_count"] == 12
    assert result["unresolved_gt_count"] == 26
    assert result["macro_gt_count"] + result["unresolved_gt_count"] == 114


def test_046_047_048_window_lengths() -> None:
    from parse_windows import load_all_windows, normalized
    norm = normalized(load_all_windows())
    assert norm["BLIND-046"][0] == 288
    assert norm["BLIND-047"][0] == 96
    assert norm["BLIND-048"][0] == 480


def test_historical_synthetic_result_reproduced() -> None:
    """§9 mandat -- reproduce SAU explică diferența pt. cifrele VE deja raportate. Acest test
    EȘUEAZĂ dacă reproducerea nu (mai) e byte-identică cu ce s-a raportat -- fail-closed, nu
    ajustare tăcută a `REPORTED`."""
    result = run_all()
    reproduced, mismatches = check_historical_reproduction(result)
    assert reproduced, f"HISTORICAL_SYNTHETIC_RESULT_NOT_REPRODUCED: {mismatches}"


def test_deterministic_rerun_byte_identical() -> None:
    """Aceeași intrare -> output byte-identic (mandat §10)."""
    r1 = run_all()
    r2 = run_all()
    assert r1["macro_matches"] == r2["macro_matches"]
    assert r1["internal_matches"] == r2["internal_matches"]
    assert r1["counters"] == r2["counters"]
    assert r1["funnel"] == r2["funnel"]


def test_reported_figures_constant_is_exactly_what_was_delivered() -> None:
    """Ancorează `REPORTED` la cifrele EXACTE din RANGE_V4_3_REAL_PROTOTYPE_DELIVERY_REPORT.md §7 --
    dacă cineva schimbă `REPORTED` din greșeală, acest test documentează valorile corecte."""
    assert REPORTED["macro_matched"] == 57 and REPORTED["macro_gt"] == 88
    assert REPORTED["internal_matched"] == 2 and REPORTED["internal_gt"] == 12
    assert REPORTED["sweep_confirmed"] == 209
    assert REPORTED["breakout_accepted"] == 112
    assert REPORTED["liquidity_sweep_reversal"] == 21
    assert REPORTED["promo_count"] == 94
    assert REPORTED["funnel_total"] == 725
