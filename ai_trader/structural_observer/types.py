"""Types owned by `structural_observer` (Mandate 4, 2026-07-29). CEO instruction, verbatim: "Nu produce
semnale. Nu evalueaza. INREGISTREAZA" -- `StructuralObservation` is deliberately a plain fact record,
never a decision, never a recommendation, matching this codebase's own established discipline for
`RecognitionResult` (`recognition_engine_live`): "ALWAYS descriptive statistics... NEVER a trading
recommendation."

One generic envelope (`kind` + a JSON-serializable `detail` dict), not one dataclass per event shape --
matching the same convention `mt5_pnl_source`/`live_signal_source` already use for persistence
(serialize to a generic append-log row), so this package doesn't invent a new persistence idiom.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StructuralEventKind(str, Enum):
    """Every category the CEO named, verbatim: "swing-uri clasificate, BOS, CHoCH... bazine externe...
    FVG-uri deschise, atinse la CE-50, umplute, inversate... PDH/PDL si Weekly... regimul de stare."
    Only the categories this step actually wires appear here -- `liquidity_mechanics`/
    `institutional_levels` remain blocked (see the Step 3 report), so no POOL/LEVEL kind exists yet."""

    SWING = "SWING"
    STRUCTURE_BREAK = "STRUCTURE_BREAK"
    FVG_FORMED = "FVG_FORMED"
    FVG_REACTION = "FVG_REACTION"
    REGIME = "REGIME"
    ORDER_BLOCK_FORMED = "ORDER_BLOCK_FORMED"
    ORDER_BLOCK_BREAKER = "ORDER_BLOCK_BREAKER"
    ORDER_BLOCK_MITIGATION = "ORDER_BLOCK_MITIGATION"
    ORDER_BLOCK_REJECTION = "ORDER_BLOCK_REJECTION"


@dataclass(frozen=True, slots=True)
class StructuralObservation:
    """One recorded fact -- never a signal, never evaluated. `as_of` is the bar timestamp (`ts_close`)
    the observation is anchored to; `detail` carries whatever fields that specific `kind` needs (prices,
    labels, indices), always JSON-serializable primitives only."""

    symbol: str
    as_of: int
    kind: StructuralEventKind
    detail: dict[str, object]

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("StructuralObservation.symbol must not be empty")
