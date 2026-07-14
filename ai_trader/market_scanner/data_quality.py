"""Data Quality & Sufficiency assessment (``MARKET_SCANNER_ARCHITECTURE.md`` §8, "never invent
prices; always disclose").

Turns the mechanical facts already recorded elsewhere (bar-store gaps/staleness, which declared
feature fields are still ``None``) into the two schema objects every ``MarketContext`` carries:
``data_quality`` (per-timeframe + overall) and ``sufficiency`` (whether the aggregated strategy
requirements can be met this cycle). Nothing here invents a value — it only classifies facts that
are already true.
"""

from __future__ import annotations

from typing import Any

from ai_trader.market_scanner.bar_store import Gap, TimeframeWindow
from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.types import DataQualityLevel, Requirements, SufficiencyLevel

#: Reported when a timeframe has never received a complete bar. Schema requires a non-negative
#: integer (no "unknown"/null representation exists), so an intentionally large sentinel is used —
#: any consumer thresholding staleness will correctly treat this as "not fresh".
UNKNOWN_STALENESS_MS = 2**31 - 1

_LEVEL_PRECEDENCE: dict[DataQualityLevel, int] = {
    DataQualityLevel.OK: 0,
    DataQualityLevel.DEGRADED: 1,
    DataQualityLevel.STALE: 2,
    DataQualityLevel.INSUFFICIENT: 3,
}


def _gap_to_dict(gap: Gap) -> dict[str, Any]:
    return {
        "from_ts": gap.from_ts,
        "to_ts": gap.to_ts,
        "bars_missing": gap.bars_missing,
        "cause": gap.cause,
    }


def assess(
    as_of: int,
    config: ScannerConfig,
    windows: dict[str, TimeframeWindow | None],
    features_by_timeframe: dict[str, dict[str, Any]],
    requirements: Requirements | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compute the ``data_quality`` and ``sufficiency`` schema objects for one symbol's context.

    Args:
        as_of: the evaluation instant.
        config: the scanner configuration (staleness/gap thresholds).
        windows: the tracked ``{timeframe: TimeframeWindow}`` for this symbol (a ``None`` value
            means that timeframe was required but never configured/ingested).
        features_by_timeframe: the already-assembled ``{timeframe: {field: value}}`` feature maps
            (base timeframe's full namespace + each context timeframe's minimal snapshot).
        requirements: the aggregated Strategy Manager requirement, or ``None`` if not yet
            registered (in which case every tracked timeframe/field is treated as required — the
            conservative default before any strategy has been loaded).

    Returns:
        ``(data_quality_dict, sufficiency_dict)``, each exactly matching its
        ``MARKET_CONTEXT_SCHEMA.json`` shape.
    """
    tracked = requirements.timeframes if requirements is not None else frozenset(windows)
    by_timeframe: dict[str, Any] = {}
    overall_levels: list[DataQualityLevel] = []
    missing_fields: list[str] = []
    missing_timeframes: list[str] = []

    for tf in sorted(tracked):
        window = windows.get(tf)
        if window is None:
            missing_timeframes.append(tf)
            by_timeframe[tf] = {
                "last_bar_complete": False,
                "warmup_satisfied": False,
                "staleness_ms": UNKNOWN_STALENESS_MS,
                "late_dropped": 0,
                "gaps": [],
            }
            overall_levels.append(DataQualityLevel.INSUFFICIENT)
            continue

        last_close = window.last_ingested_close
        staleness_ms = UNKNOWN_STALENESS_MS if last_close is None else max(0, int((as_of - last_close) * 1000))
        gaps = window.gaps()
        required_fields_tf = (
            requirements.fields_by_timeframe.get(tf, frozenset()) if requirements is not None else frozenset()
        )
        feats = features_by_timeframe.get(tf, {})
        missing_here = sorted(f for f in required_fields_tf if feats.get(f) is None)
        warmup_satisfied = (len(missing_here) == 0) if required_fields_tf else (last_close is not None)
        missing_fields.extend(f"{tf}.{f}" for f in missing_here)

        unexplained_gaps = [g for g in gaps if g.cause is None and g.bars_missing >= config.max_gap_bars_before_degraded]
        if last_close is None or not warmup_satisfied:
            tf_level = DataQualityLevel.INSUFFICIENT
        elif staleness_ms > config.staleness_threshold_ms:
            tf_level = DataQualityLevel.STALE
        elif unexplained_gaps:
            tf_level = DataQualityLevel.DEGRADED
        else:
            tf_level = DataQualityLevel.OK
        overall_levels.append(tf_level)

        by_timeframe[tf] = {
            "last_bar_complete": last_close is not None,
            "warmup_satisfied": warmup_satisfied,
            "staleness_ms": staleness_ms,
            "late_dropped": window.late_dropped,
            "gaps": [_gap_to_dict(g) for g in gaps],
        }

    overall = max(overall_levels, key=lambda lv: _LEVEL_PRECEDENCE[lv]) if overall_levels else DataQualityLevel.INSUFFICIENT
    data_quality = {"overall": overall.value, "by_timeframe": by_timeframe}

    if missing_fields or missing_timeframes:
        suff_overall = SufficiencyLevel.INSUFFICIENT if overall == DataQualityLevel.INSUFFICIENT else SufficiencyLevel.PARTIAL
    else:
        suff_overall = SufficiencyLevel.SUFFICIENT
    sufficiency = {
        "overall": suff_overall.value,
        "missing_fields": missing_fields or None,
        "missing_timeframes": missing_timeframes or None,
        "note": None if suff_overall == SufficiencyLevel.SUFFICIENT else "see missing_fields/missing_timeframes",
    }
    return data_quality, sufficiency
