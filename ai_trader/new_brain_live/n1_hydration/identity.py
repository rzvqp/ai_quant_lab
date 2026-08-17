"""N1 hydration snapshot identity -- RT-N1-HYDRATION-0001 section "IDENTITATE SNAPSHOT". Every field the
CEO's own list names, computed from real sources (never a literal a future change could silently outrun):
`n1_contract_version`/`router_version` from the installed `ve_brain` artifact itself, `implementation_
commit` from `git rev-parse` (reusing `entrypoint.current_git_commit`, the one place this repo already
reads it), `detector_configuration_fingerprint` from the vendored detectors' OWN tunables (re-exported by
`structural_observer.vendor_bridge`, RT-N1-HYDRATION-0001's own additive extension of that file), and
`bar_content_identity` from the actual bar sequence a snapshot carries.

Any mismatch on the STRUCTURAL fields (contract/router/commit/detector-fingerprint/symbol/timeframe/
schema) means the snapshot was produced under a different N1 definition than the one running now --
`identity_matches_for_restore` refuses it, fail-closed, rather than silently reusing axes state that might
not mean the same thing anymore. `data_range`/`bar_content_identity`/`watermark` are DELIBERATELY excluded
from that comparison -- those legitimately differ (and grow) across every restart of a healthy process;
comparing them would reject every snapshot ever written."""

from __future__ import annotations

import dataclasses
import hashlib

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_live.entrypoint import current_git_commit
from ai_trader.structural_observer.vendor_bridge import (
    ATR_WINDOW,
    BODY_FRAC,
    COMPRESSION_PCTL,
    COMPRESSION_WINDOW,
    DISP_MULT,
    K_DEFAULT,
)

SNAPSHOT_SCHEMA_VERSION = "n1-hydration-snapshot-v1"


def _fp(*parts: str) -> str:
    """Same generic sha256-truncate-16 convention already established in `bridge._fp`/`upstream_
    context._fp` -- a local copy so this package's dependency surface stays minimal, matching `upstream_
    context.py`'s own established precedent for the identical reason."""
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def required_bar_count() -> int:
    """The MINIMUM trailing bar count every vendored detector this builder calls actually needs before
    its own output is fully "warm" -- derived from the real constants, never a duplicated literal.
    `COMPRESSION_WINDOW` dominates today (see `vendor_bridge.py`), but this stays correct even if that
    ever changes: it is read fresh from `vendor_bridge` on every call, never cached at import time as a
    module-level literal."""
    return int(max(ATR_WINDOW, COMPRESSION_WINDOW, 2 * K_DEFAULT + 1))


def detector_configuration_fingerprint() -> str:
    """Fingerprint over the vendored detectors' own tunables (compression/ATR/swing/expansion) -- changes
    the moment the pinned submodule commit changes any of these, which is exactly what should invalidate
    an old snapshot: the axes it holds were computed under a different definition of "compressed"/
    "displaced"/"swing", not merely stale data."""
    return _fp(
        str(ATR_WINDOW), str(COMPRESSION_WINDOW), str(COMPRESSION_PCTL), str(K_DEFAULT),
        str(DISP_MULT), str(BODY_FRAC),
    )


def bar_content_identity(bars: tuple[Bar, ...]) -> str:
    """Order-sensitive hash over the FULL bar sequence a snapshot carries -- proves the exact bars, not
    merely a matching count or timestamp range."""
    parts: list[str] = []
    for bar in bars:
        parts.extend((
            bar.symbol, str(bar.ts_open), str(bar.ts_close), str(bar.open), str(bar.high),
            str(bar.low), str(bar.close), str(bar.volume),
        ))
    return _fp(*parts)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class N1SnapshotIdentity:
    n1_contract_version: str
    router_version: str
    implementation_commit: str
    detector_configuration_fingerprint: str
    symbol: str
    timeframe: str
    snapshot_schema_version: str
    first_bar_ts_open: int
    last_bar_ts_close: int
    bar_content_identity: str
    watermark_ts_open: int


_STRUCTURAL_FIELDS = (
    "n1_contract_version", "router_version", "implementation_commit",
    "detector_configuration_fingerprint", "symbol", "timeframe", "snapshot_schema_version",
)


def current_identity_for(*, symbol: str, timeframe: str, bars: tuple[Bar, ...]) -> N1SnapshotIdentity:
    if not bars:
        raise ValueError("current_identity_for: bars must be non-empty")
    return N1SnapshotIdentity(
        n1_contract_version=ve_brain.N1_CONTRACT_VERSION, router_version=ve_brain.ROUTER_VERSION,
        implementation_commit=current_git_commit(), detector_configuration_fingerprint=detector_configuration_fingerprint(),
        symbol=symbol, timeframe=timeframe, snapshot_schema_version=SNAPSHOT_SCHEMA_VERSION,
        first_bar_ts_open=bars[0].ts_open, last_bar_ts_close=bars[-1].ts_close,
        bar_content_identity=bar_content_identity(bars), watermark_ts_open=bars[-1].ts_open,
    )


def identity_matches_for_restore(candidate: N1SnapshotIdentity, *, symbol: str, timeframe: str) -> bool:
    """`True` only if EVERY structural field matches what would be computed right now for this
    `(symbol, timeframe)` -- `implementation_commit` in particular means a snapshot written by a DIFFERENT
    deployed commit is always refused, even if nothing else about N1 changed, since "the same code" is
    the only honest basis for reusing accumulated axes state across a restart."""
    if candidate.symbol != symbol or candidate.timeframe != timeframe:
        return False
    current = N1SnapshotIdentity(
        n1_contract_version=ve_brain.N1_CONTRACT_VERSION, router_version=ve_brain.ROUTER_VERSION,
        implementation_commit=current_git_commit(), detector_configuration_fingerprint=detector_configuration_fingerprint(),
        symbol=symbol, timeframe=timeframe, snapshot_schema_version=SNAPSHOT_SCHEMA_VERSION,
        first_bar_ts_open=candidate.first_bar_ts_open, last_bar_ts_close=candidate.last_bar_ts_close,
        bar_content_identity=candidate.bar_content_identity, watermark_ts_open=candidate.watermark_ts_open,
    )
    return all(getattr(candidate, field) == getattr(current, field) for field in _STRUCTURAL_FIELDS)
