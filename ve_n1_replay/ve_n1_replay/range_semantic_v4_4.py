"""RANGE HIERARCHICAL V4.4 -- implementation (mandat VE-RANGE-V4_4-IMPLEMENTATION-001).

Converts the frozen mechanism (`VE_RANGE_V4_4_DESIGN_FREEZE.md`, `c57d103`) and the calibrated parameter
registry (`VE_RANGE_V4_4_CALIBRATION_RESULTS.md`, `898f149`) into code, without semantic deviation. Additive
over `range_semantic_v4_3.py` -- that file is byte-untouched by this work; every pure function/class that is
semantically identical for V4.4 (`Cluster`, `Excursion`, `Registry`, `degeneracy_check`,
`evaluate_candidate_with_n_touch`, `offer_swing`, `assign_level`, `promotion_check`,
`sweep_reversal_confirmed`, `Depth`, `MacroState`, `InternalState`, `ROLES_V43`, `Structure`, the 29 existing
reason codes, `ContractErrorV43`, `ConfigNotRatifiedErrorV43`, `RangeEventV43`) is imported and reused
directly, never re-implemented. INTERNAL-depth handling in `observe()` below mirrors V4.3's own orchestration
line-for-line (mandate §19: F4/INTERNAL is out of scope, must not be recoupled into the MACRO release) --
`tests/test_v4_4_internal_parity.py` proves this empirically (byte-identical INTERNAL output vs. V4.3 on
shared bars), not just by code inspection.

MACRO gains: a four-signal discrimination gate at confirmation (T3), a new `WEAKENING` lifecycle state
(T4/T5/T6/T7/T8/T9), and episode continuation/replacement identity -- exactly the transition table in
`VE_RANGE_V4_4_CONVERGENCE_AND_REVIEW_PACKAGE.md` §3, reproduced in the transition docstrings below.

**Implementation-detail resolution, disclosed (mandate's own "resolve genuine ambiguity" allowance, matching
the same discipline already used to resolve the WEAKENING dual-trigger and episode-identity priority
ambiguities in the convergence package)**: the design chain's implementation-plan sketch (`f241698` §13)
named a fixed `c0` (structure-inception close) as the RND reference. The *frozen calibration* (`898f149`),
which is the artifact whose exact numeric values (`RND_max=1.0` etc.) this mandate must reproduce byte-
faithfully, computed RND using the **trailing-window** reference (`closes[0]` of the bounded window, not the
structure's true inception close) -- this matches T3's own text ("RND <= RND_max ... all over trailing window
W"). Implementing a fixed-`c0` RND here would silently change the semantics `RND_max=1.0` was actually
calibrated against. This file therefore uses the trailing-window reference throughout, matching the
calibration exactly; no separate `c0` field exists (the trailing-window deque already provides it as its own
oldest element). Recorded here, not hidden, and restated in the delivery report.

**MERGE-branch reachability, disclosed**: episode identity's priority order (§6 of `f241698`) checks `MERGE`
against any *currently live* macro structure before `CONTINUATION`/`REPLACEMENT`. Because MACRO remains
single-active-at-a-time by construction (`forming_macro = self._active_macro is None`, unchanged from V4.3,
preserved per the freeze's own preservation matrix), a second, concurrently-live MACRO candidate can never
exist to merge against -- `MERGE`/`EPISODE_MERGED` is implemented (not dead code, in case a future
architectural change ever allows concurrent candidates) but is structurally unreachable via the public
`observe()` API today. Proven, not asserted, by `tests/test_v4_4_transitions.py::test_episode_merge_is_structurally_unreachable`.

**Alternation wiring, a real gap found and fixed before freeze**: `alternation_rate()`/`ALT_MIN`/
`touches_in_window()` were initially written but never actually invoked from `_evaluate_macro_formation` --
`INSUFFICIENT_ALTERNATION_EVIDENCE` would have been a defined-but-unreachable reason code, exactly what
mandate §13 prohibits. Fixed: T3 now computes alternation over the trailing window at the moment of
confirmation and, if evidence is `None` or below `ALT_MIN`, emits an *additional* `INSUFFICIENT_ALTERNATION_
EVIDENCE` event alongside (not instead of) `OK_RANGE_MACRO` -- alternation remains SUPPORTING_ONLY (mandat
§5: never promoted to a hard gate; confirmation still proceeds), but weak supporting evidence is now
disclosed rather than silently discarded, and the code is reachable.
"""
from __future__ import annotations

import dataclasses as _dc
import hashlib
import json
from collections import deque
from typing import Any, Literal, cast

from .range_semantic_v4_3 import (
    ATR_UNAVAILABLE,
    BETWEEN_EPISODES,
    BREAKOUT_ACCEPTED,
    ConfigNotRatifiedErrorV43,
    ConfigV43,
    ContractErrorV43,
    Cluster,
    Depth,
    ESTABLISHING_FEW_SWINGS,
    Excursion,
    InternalState,
    IS_TREND_MACRO,
    LIQUIDITY_SWEEP_REVERSAL,
    MacroState,
    NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT,
    OK_RANGE_INTERNAL,
    OK_RANGE_MACRO,
    REASONS_V43,
    Registry,
    ROLES_V43,
    RangeEventV43,
    Structure,
    SWEEP_CONFIRMED,
    SWING_OUTSIDE_CLUSTER,
    SNAPSHOT_CONTRACT_MISMATCH,
    TOO_SHORT_INTERNAL,
    TOO_SHORT_MACRO,
    ZONES_DEGENERATE,
    ZONES_INVERTED,
    assign_level,
    degeneracy_check,
    evaluate_candidate_with_n_touch,
    offer_swing,
    promotion_check,
    sweep_reversal_confirmed,
)

__all__ = [
    # re-exportate din V4.3 -- necesare pt. `range_engine_v4_4.py` (mypy --strict --no-implicit-reexport,
    # aceeasi conventie ca `range_semantic_v4_3.__all__`)
    "ConfigNotRatifiedErrorV43", "ContractErrorV43", "RangeEventV43", "SNAPSHOT_CONTRACT_MISMATCH",
    # V4.4, proprii
    "RANGE_HIERARCHICAL_V4_4_CONTRACT_VERSION",
    "INSUFFICIENT_EFFICIENCY", "INSUFFICIENT_TRAVERSAL", "INSUFFICIENT_ALTERNATION_EVIDENCE",
    "EXCESSIVE_NET_DISPLACEMENT", "RANGE_CANDIDATE_PRESENT", "RANGE_WEAKENING", "WEAKENING_RECOVERED",
    "WEAKENING_PERSISTENCE_TERMINATED", "EPISODE_CONTINUATION", "EPISODE_MERGED", "EPISODE_REPLACEMENT",
    "REASONS_V44", "MacroStateV44", "WeakeningReason", "EpisodeAction",
    "ConfigV44", "RANGE_HIERARCHICAL_V4_4_NORMATIVE_CONFIG_ID",
    "efficiency_ratio", "relative_net_displacement", "traversal_count", "alternation_rate",
    "StructureV44", "RangeSemanticResultV44", "RangeSemanticProducerV44",
    "RANGE_HIERARCHICAL_V4_4_IMPLEMENTATION_FINGERPRINT",
]

# ═══════════════════════════════════ identitate ═══════════════════════════════════

RANGE_HIERARCHICAL_V4_4_CONTRACT_VERSION = "range-hierarchical-v4.4"

# ── 11 coduri de motiv noi, aditive -- cele 29 din V4.3 raman valide, nerenumerotate (identity plan, f241698 §12) ──
INSUFFICIENT_EFFICIENCY = "INSUFFICIENT_EFFICIENCY"
INSUFFICIENT_TRAVERSAL = "INSUFFICIENT_TRAVERSAL"
INSUFFICIENT_ALTERNATION_EVIDENCE = "INSUFFICIENT_ALTERNATION_EVIDENCE"
EXCESSIVE_NET_DISPLACEMENT = "EXCESSIVE_NET_DISPLACEMENT"
RANGE_CANDIDATE_PRESENT = "RANGE_CANDIDATE_PRESENT"
RANGE_WEAKENING = "RANGE_WEAKENING"
WEAKENING_RECOVERED = "WEAKENING_RECOVERED"
WEAKENING_PERSISTENCE_TERMINATED = "WEAKENING_PERSISTENCE_TERMINATED"
EPISODE_CONTINUATION = "EPISODE_CONTINUATION"
EPISODE_MERGED = "EPISODE_MERGED"
EPISODE_REPLACEMENT = "EPISODE_REPLACEMENT"

REASONS_V44: tuple[str, ...] = REASONS_V43 + (
    INSUFFICIENT_EFFICIENCY, INSUFFICIENT_TRAVERSAL, INSUFFICIENT_ALTERNATION_EVIDENCE,
    EXCESSIVE_NET_DISPLACEMENT, RANGE_CANDIDATE_PRESENT, RANGE_WEAKENING, WEAKENING_RECOVERED,
    WEAKENING_PERSISTENCE_TERMINATED, EPISODE_CONTINUATION, EPISODE_MERGED, EPISODE_REPLACEMENT,
)
assert len(REASONS_V44) == 40, f"29 V4.3 + 11 V4.4 = 40 asteptat, avut {len(REASONS_V44)}"
assert len(set(REASONS_V44)) == 40, "coduri de motiv duplicate intre V4.3 si V4.4"

MacroStateV44 = Literal["CANDIDATE", "FORMING", "CONFIRMED", "WEAKENING", "TERMINATED"]
WeakeningReason = Literal["EXCURSION_PENDING", "TRAILING_DEGRADATION"]
EpisodeAction = Literal["MERGE", "CONTINUATION", "REPLACEMENT"]


# ═══════════════════════════════════ configuratie ═══════════════════════════════════

@_dc.dataclass(frozen=True, slots=True)
class ConfigV44:
    """Cele 9 campuri V4.3 nemodificate (portile MACRO/INTERNAL comune raman aceleasi) + 10 campuri noi,
    toate rezolvate in `898f149` (7 parametri + 2 ancore). Fisier de sine statator (nu subclaseaza
    `ConfigV43`) pt. ca `config_id()` trebuie sa acopere setul COMPLET V4.4 -- vezi §16 din pachetul de
    convergenta si §16 din raportul de calibrare pt. formula exacta reprodusa mai jos, caracter cu caracter."""
    # -- V4.3, RATIFICAT, nemodificat --
    d_macro: int = 29
    d_internal: int = 12
    n_touch: int = 2
    K_reentry: int = 22
    N_accept: int = 3
    K_struct: int = 2
    n_external_swings: int = 2
    atr_window: int = 14
    w_atr: float = 0.80
    atr_source: str = "ai_trader.structural_observer.vendor_bridge.atr14"
    atr_provenance_wheel_sha256: str = (
        "39673910666e13708b1d4cb7266d1730bb1c9ceea4e0b021a1bf3cfa1f8281f4")
    contract_version: str = RANGE_HIERARCHICAL_V4_4_CONTRACT_VERSION
    # -- V4.4, rezolvate in calibrare (898f149) --
    ER_max: float = 0.5
    RND_max: float = 1.0
    ALT_MIN: float = 0.5
    MIN_TRAVERSALS: int = 1
    W: int = 29
    ER_weakening: float = 0.75
    RND_weakening: float = 2.0
    WEAKENING_MAX_BARS: int = 22
    IOU_CONTINUE: float = 0.5
    GAP_MAX: int = 12

    def __post_init__(self) -> None:
        self.validate()

    @property
    def tol_cluster(self) -> float:
        return 2.0 * self.w_atr

    @property
    def w_atr_sanity_ceiling(self) -> float:
        return 1.3952

    def validate(self) -> None:
        if not (0 < self.w_atr < self.w_atr_sanity_ceiling):
            raise ContractErrorV43(f"W_ATR_OUT_OF_SANITY_RANGE: {self.w_atr}")
        if self.d_internal >= self.d_macro:
            raise ContractErrorV43("D_INTERNAL_NOT_BELOW_D_MACRO")
        if self.n_touch < 2:
            raise ContractErrorV43("N_TOUCH_BELOW_STRUCTURAL_FLOOR")
        if self.K_struct < 1 or self.n_external_swings < 1 or self.N_accept < 1 or self.K_reentry < 1:
            raise ContractErrorV43("NON_POSITIVE_STRUCTURAL_PARAMETER")
        if not (0.0 < self.ER_max < 1.0):
            raise ContractErrorV43(f"ER_MAX_OUT_OF_RANGE: {self.ER_max}")
        if self.RND_max <= 0:
            raise ContractErrorV43(f"RND_MAX_NON_POSITIVE: {self.RND_max}")
        if not (self.ER_max < self.ER_weakening <= 1.0):
            raise ContractErrorV43(f"ER_WEAKENING_NOT_ABOVE_ER_MAX: {self.ER_weakening}")
        if self.RND_weakening <= self.RND_max:
            raise ContractErrorV43(f"RND_WEAKENING_NOT_ABOVE_RND_MAX: {self.RND_weakening}")
        if self.MIN_TRAVERSALS < 1:
            raise ContractErrorV43(f"MIN_TRAVERSALS_BELOW_FLOOR: {self.MIN_TRAVERSALS}")
        if self.W < self.d_macro:
            raise ContractErrorV43(f"W_BELOW_D_MACRO: {self.W} < {self.d_macro}")
        if self.WEAKENING_MAX_BARS < 1:
            raise ContractErrorV43(f"WEAKENING_MAX_BARS_NON_POSITIVE: {self.WEAKENING_MAX_BARS}")
        if not (0.0 < self.IOU_CONTINUE <= 1.0):
            raise ContractErrorV43(f"IOU_CONTINUE_OUT_OF_RANGE: {self.IOU_CONTINUE}")
        if self.GAP_MAX < 0:
            raise ContractErrorV43(f"GAP_MAX_NEGATIVE: {self.GAP_MAX}")

    def config_id(self) -> str:
        """Formula IDENTICA cu `ConfigV43.config_id()` (sha256 peste campurile sortate + proprietati
        derivate, JSON `sort_keys=True`, separatori compacti) -- reprodusa aici caracter cu caracter din
        scriptul care a produs `23d98c07...` in raportul de calibrare (`898f149` §16), pt. ca acest
        `config_id()` sa reproduca EXACT acea valoare inghetata (mandat §4: `V4_4_CONFIG_ID_MISMATCH` daca nu)."""
        payload: dict[str, Any] = {k: getattr(self, k) for k in self.__dataclass_fields__}
        payload["_derived_tol_cluster"] = self.tol_cluster
        payload["_derived_s_max"] = self.tol_cluster
        payload["_derived_w_atr_sanity_ceiling"] = self.w_atr_sanity_ceiling
        payload["_derived_er_weakening_minus_er_max"] = self.ER_weakening - self.ER_max
        payload["_derived_rnd_weakening_over_rnd_max"] = self.RND_weakening / self.RND_max
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


RANGE_HIERARCHICAL_V4_4_NORMATIVE_CONFIG_ID = ConfigV44().config_id()


def _as_v43_cfg(cfg: ConfigV44) -> ConfigV43:
    """`ConfigV44` e structural compatibil cu `ConfigV43` pt. toate campurile pe care functiile PURE V4.3
    reutilizate aici (`offer_swing`, `assign_level`, `degeneracy_check`, `Excursion.observe`,
    `evaluate_candidate_with_n_touch`, `promotion_check`) le citesc -- cele 9 campuri V4.3 raman IDENTICE ca
    nume/tip (mandat §4). `ConfigV44` deliberat NU subclaseaza `ConfigV43` (vezi docstring-ul `ConfigV44`),
    deci cast explicit pt. mypy --strict, nu mostenire nominala -- adevarul de runtime e neschimbat."""
    return cast(ConfigV43, cfg)


# ═══════════════════════════════════ semnale directionale pure -- ferestre marginite, O(W) pe bara ═══════════════════════════════════

def efficiency_ratio(trailing_closes: "deque[float] | list[float]") -> float:
    """Kaufman ER peste fereastra marginita curenta -- constructie DIFERITA de `normalized_drift`-ul
    falsificat (fara ATR, foloseste lungimea CUMULATA a caii, nu o panta OLS). `f241698` §4.1."""
    closes = list(trailing_closes)
    if len(closes) < 2:
        return 0.0
    net = abs(closes[-1] - closes[0])
    path = sum(abs(closes[i] - closes[i - 1]) for i in range(1, len(closes)))
    return net / path if path > 0 else 0.0


def relative_net_displacement(trailing_closes: "deque[float] | list[float]",
                              boundary_upper: float | None, boundary_lower: float | None) -> float:
    """RND fata de PROPRIA latime a structurii, calculat peste fereastra marginita curenta (vezi nota de
    reconciliere din docstring-ul modulului -- NU fata de `c0` fix la inceputul structurii)."""
    closes = list(trailing_closes)
    if len(closes) < 2 or boundary_upper is None or boundary_lower is None:
        return 0.0
    width = boundary_upper - boundary_lower
    if width <= 0:
        return float("inf")
    net = abs(closes[-1] - closes[0])
    return net / width


def _traversal_zone(price: float, boundary_upper: float, boundary_lower: float) -> str:
    width = boundary_upper - boundary_lower
    upper_zone = boundary_upper - width / 3.0
    lower_zone = boundary_lower + width / 3.0
    if price >= upper_zone:
        return "U"
    if price <= lower_zone:
        return "L"
    return "M"


def traversal_count(trailing_closes: "deque[float] | list[float]",
                    boundary_upper: float | None, boundary_lower: float | None) -> int:
    """Numarul de treceri complete UPPER<->LOWER (prin MID) peste fereastra marginita curenta -- distinge
    testarea genuina a ambelor parti de doua atingeri izolate ale marginilor in timpul unei derive."""
    if boundary_upper is None or boundary_lower is None or boundary_upper <= boundary_lower:
        return 0
    zones = [_traversal_zone(c, boundary_upper, boundary_lower) for c in trailing_closes]
    count = 0
    last_extreme: str | None = None
    for z in zones:
        if z in ("U", "L"):
            if last_extreme is not None and z != last_extreme:
                count += 1
            last_extreme = z
    return count


def alternation_rate(tags_in_window: list[str]) -> float | None:
    """SUPPORTING_ONLY -- nu conditioneaza nicio poarta. `None` daca dovada e insuficienta (<3 atingeri
    in fereastra), NU 0.0 (0.0 ar insemna "complet non-alternant", diferit de "nedeterminat")."""
    if len(tags_in_window) < 3:
        return None
    pairs = list(zip(tags_in_window, tags_in_window[1:]))
    flipped = sum(1 for a, b in pairs if a != b)
    return flipped / len(pairs)


def _iou(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Reutilizeaza EXACT constructia IoU deja ratificata in scorer (`blind_runner/scoring.py::_iou`) --
    aceeasi conventie, nu inventata din nou (mandat §13: 'nu inventa o noua metrica de potrivire')."""
    s = max(a[0], b[0]); e = min(a[1], b[1])
    inter = max(0.0, e - s)
    union = (a[1] - a[0]) + (b[1] - b[0]) - inter
    return inter / union if union > 0 else 0.0


# ═══════════════════════════════════ structura MACRO V4.4 -- extensie aditiva peste `Structure` ═══════════════════════════════════

class StructureV44(Structure):
    """Doar structurile MACRO din V4.4 folosesc aceasta subclasa -- INTERNAL ramane `Structure` simplu,
    NEATINS, exact comportamentul V4.3 (mandat §19). Adauga STRICT campurile noi de la `f241698` §13
    (fereastra marginita e comuna pt. ER/RND/traversal -- nu exista `c0` separat, vezi nota din docstring-ul
    modulului)."""

    def __init__(self, *, structure_id: int, depth: Depth, parent_structure_id: int | None,
                start_ts: int, trailing_window: int) -> None:
        super().__init__(structure_id=structure_id, depth=depth, parent_structure_id=parent_structure_id,
                         start_ts=start_ts)
        self._trailing_closes: deque[float] = deque(maxlen=trailing_window)
        self._touch_tags: deque[tuple[int, str]] = deque(maxlen=64)   # (bar_index, "H"/"L"), marginit
        self.weakening_reason: WeakeningReason | None = None
        self._weakening_bars: int = 0
        self.continued_from_id: int | None = None
        self._candidate_present_emitted: bool = False   # T2 -> RANGE_CANDIDATE_PRESENT, o singura data

    def push_close_v44(self, bar_index: int, close: float) -> None:
        self.push_close(close)   # portie mostenita: _drift + n_bars, neschimbata (DIAGNOSTIC_ONLY la V4.4)
        self._trailing_closes.append(close)

    def record_touch_v44(self, bar_index: int, is_high: bool) -> None:
        self._touch_tags.append((bar_index, "H" if is_high else "L"))

    def touches_in_window(self, as_of_bar: int, window: int) -> list[str]:
        lo = as_of_bar - window
        return [tag for (b, tag) in self._touch_tags if b > lo]

    def snapshot(self) -> dict[str, Any]:
        base = super().snapshot()
        base.update({
            "v44_trailing_closes": list(self._trailing_closes),
            "v44_trailing_window_maxlen": self._trailing_closes.maxlen,
            "v44_touch_tags": [[b, t] for (b, t) in self._touch_tags],
            "v44_weakening_reason": self.weakening_reason,
            "v44_weakening_bars": self._weakening_bars,
            "v44_continued_from_id": self.continued_from_id,
            "v44_candidate_present_emitted": self._candidate_present_emitted,
        })
        return base

    @classmethod
    def restore(cls, st: dict[str, Any]) -> "StructureV44":
        s = cls(structure_id=st["structure_id"], depth=Depth(st["depth"]),
                parent_structure_id=st["parent_structure_id"], start_ts=st["start_ts"],
                trailing_window=st["v44_trailing_window_maxlen"])
        s.confirm_ts = st["confirm_ts"]; s.end_ts = st["end_ts"]; s.end_reason = st["end_reason"]
        state_val = st["state"]
        s.state = MacroState(state_val) if state_val in {e.value for e in MacroState} else InternalState(state_val)
        s.up = Cluster.restore(st["up_members"], st["up_frozen"])
        s.dn = Cluster.restore(st["dn_members"], st["dn_frozen"])
        s.atr_ref = st["atr_ref"]
        s.predecessor_id = st["predecessor_id"]; s.role = st["role"]; s.role_known_ts = st["role_known_ts"]
        s.breakout_side = st["breakout_side"]
        from .range_semantic_v4_3 import _UnboundedSlope
        s._drift = _UnboundedSlope.restore(st["drift_state"]); s.n_bars = st["n_bars"]
        s.reached_confirmed = st["reached_confirmed"]
        s._trailing_closes = deque(st["v44_trailing_closes"], maxlen=st["v44_trailing_window_maxlen"])
        s._touch_tags = deque((tuple(x) for x in st["v44_touch_tags"]), maxlen=64)
        s.weakening_reason = st["v44_weakening_reason"]
        s._weakening_bars = st["v44_weakening_bars"]
        s.continued_from_id = st["v44_continued_from_id"]
        s._candidate_present_emitted = st["v44_candidate_present_emitted"]
        return s


# ═══════════════════════════════════ rezultat / eveniment per bara V4.4 ═══════════════════════════════════

@_dc.dataclass(frozen=True, slots=True)
class RangeSemanticResultV44:
    available: bool
    bar_index: int
    ts_close: int
    macro_id: int | None
    macro_reason: str
    macro_state: str | None            # unul din CANDIDATE/FORMING/CONFIRMED/WEAKENING/TERMINATED/regim
    macro_weakening_reason: str | None
    macro_boundary_upper: float | None
    macro_boundary_lower: float | None
    macro_confirm_ts: int | None
    macro_role: str | None
    macro_continued_from_id: int | None
    regime: str | None
    internal_id: int | None
    internal_reason: str | None
    internal_state: str | None
    internal_boundary_upper: float | None
    internal_boundary_lower: float | None
    internal_role: str | None
    config_id: str
    contract_version: str


# ═══════════════════════════════════ producatorul V4.4 -- orchestrare per-bara ═══════════════════════════════════

class RangeSemanticProducerV44:
    """INTERNAL-depth handling below (`_step_internal`, the internal branches of `_offer_swing_everywhere`,
    `_kill_internal`, `_close_internal_via_breakout`, `_channel_or_state_label`) is a DIRECT, line-for-line
    copy of V4.3's own orchestration for that depth -- not refactored, not "improved," so that behavioral
    parity is a property of the code itself, not just an intention. `tests/test_v4_4_internal_parity.py`
    proves this empirically by running identical bars through both producers and diffing every INTERNAL
    field. MACRO-depth handling (`_step_macro`, episode identity) is new, implementing the T1-T9+T-KILL
    transition table from `f241698` §3 exactly."""

    def __init__(self, config: ConfigV44) -> None:
        self._cfg = config
        self._n = 0
        self._last_atr: float | None = None
        k = config.K_struct
        self._wh: deque[float] = deque(maxlen=2 * k + 1)
        self._wl: deque[float] = deque(maxlen=2 * k + 1)
        self._registry = Registry()
        self._active_macro: StructureV44 | None = None
        self._active_internal: Structure | None = None
        self._macro_excursion: Excursion | None = None
        self._internal_excursion: Excursion | None = None
        self._macro_reversal_watch: dict[str, Any] | None = None
        self._internal_reversal_watch: dict[str, Any] | None = None
        self._pending_up: tuple[int, float] | None = None
        self._pending_dn: tuple[int, float] | None = None
        self._promo_direction: int | None = None
        self._promo_broken_boundary: float | None = None
        self._promo_external_count = 0
        self._promo_original_id: int | None = None
        self._promo_fired = False
        self._regime: str | None = None
        self._macro_history: deque[StructureV44] = deque(maxlen=64)
        self._internal_history: deque[Structure] = deque(maxlen=64)
        self._awaiting_role: dict[int, Structure] = {}
        self._last_ended_macro_id: int | None = None
        self._last_ended_internal_id: int | None = None
        # V4.4-only: identitate de episod (mandat §9, f241698 §6)
        self._last_terminated_macro_zone: tuple[float, float] | None = None
        self._last_terminated_macro_end_ts: int | None = None
        self._last_terminated_macro_id: int | None = None
        self._last_terminated_macro_end_reason: str | None = None

    @property
    def macro_history(self) -> tuple[dict[str, Any], ...]:
        return tuple(s.snapshot() for s in self._macro_history)

    @property
    def internal_history(self) -> tuple[dict[str, Any], ...]:
        return tuple(s.snapshot() for s in self._internal_history)

    # ── detectie fractal -- copie byte-identica a V4.3 (nicio distinctie MACRO/INTERNAL aici) ──
    def _detect_confirmed_swings(self, i: int) -> list[tuple[int, float, bool]]:
        k = self._cfg.K_struct
        out: list[tuple[int, float, bool]] = []
        if len(self._wh) == 2 * k + 1:
            c = k
            ch = self._wh[c]
            if ch == max(self._wh) and list(self._wh).count(ch) == 1:
                out.append((i - k, ch, True))
            cl = self._wl[c]
            if cl == min(self._wl) and list(self._wl).count(cl) == 1:
                out.append((i - k, cl, False))
        return out

    def _deepest_open(self) -> Structure | None:
        if self._active_internal is not None:
            return self._active_internal
        return self._active_macro

    def _clear_pending(self) -> None:
        self._pending_up = None; self._pending_dn = None

    # ── identitate de episod la formarea unui candidat MACRO nou (f241698 §6, prioritate MERGE>CONTINUATION>REPLACEMENT) ──
    def _episode_identity_for_new_macro(self, candidate_zone: tuple[float, float], i: int
                                        ) -> tuple[EpisodeAction, int | None]:
        # MERGE: verificat pt. completitudine -- nu poate fi exercitat via observe() public, pt. ca
        # `forming_macro = self._active_macro is None` (mostenit neschimbat din V4.3) inseamna ca niciun
        # candidat nou nu poate incepe sa se formeze cat timp un MACRO e deja activ. Testat explicit ca
        # inaccesibil in `tests/test_v4_4_transitions.py`.
        if self._active_macro is not None:
            lz_lower, lz_upper = self._active_macro.boundary_lower, self._active_macro.boundary_upper
            if lz_lower is not None and lz_upper is not None:
                live_zone = (lz_lower, lz_upper)
                if _iou(candidate_zone, live_zone) >= self._cfg.IOU_CONTINUE:
                    return "MERGE", self._active_macro.structure_id
        if (self._last_terminated_macro_zone is not None
                and self._last_terminated_macro_end_reason != BREAKOUT_ACCEPTED
                and self._last_terminated_macro_end_ts is not None
                and (i - self._last_terminated_macro_end_ts) <= self._cfg.GAP_MAX):
            if _iou(candidate_zone, self._last_terminated_macro_zone) >= self._cfg.IOU_CONTINUE:
                return "CONTINUATION", self._last_terminated_macro_id
        return "REPLACEMENT", None

    def _offer_swing_everywhere(self, i: int, price: float, is_high: bool, events: list[RangeEventV43]) -> None:
        side = "high" if is_high else "low"
        # separat pe MACRO/INTERNAL (nu o bucla peste un tuplu eterogen) -- `record_touch_v44` exista doar
        # pe `StructureV44`, iar `self._active_macro`/`self._active_internal` au tipuri STATICE distincte;
        # comportament identic cu bucla originala (aceeasi ordine MACRO->INTERNAL, acelasi efect), doar
        # verificabil de mypy --strict fara `Any`/union-attr
        accepted_by_macro = False
        if self._active_macro is not None:
            ok_macro, _ = offer_swing(self._active_macro, price, side, _as_v43_cfg(self._cfg))
            accepted_by_macro = ok_macro
            if ok_macro:
                self._active_macro.record_touch_v44(i, is_high)   # V4.4: alternation evidence, SUPPORTING_ONLY
        if self._active_internal is not None:
            offer_swing(self._active_internal, price, side, _as_v43_cfg(self._cfg))
        if self._promo_direction is not None and self._promo_broken_boundary is not None:
            beyond = (price > self._promo_broken_boundary if self._promo_direction == 1
                     else price < self._promo_broken_boundary)
            if beyond:
                self._promo_external_count += 1
                self._maybe_promote(i, events)
        forming_internal = self._active_macro is not None and self._active_internal is None
        forming_macro = self._active_macro is None
        if not (forming_internal or forming_macro):
            return
        if forming_internal and accepted_by_macro:
            return
        if forming_internal and self._active_macro is not None:
            boundary = self._active_macro.up.center if is_high else self._active_macro.dn.center
            if boundary is not None and abs(price - boundary) <= self._cfg.tol_cluster:
                return
        if is_high:
            self._pending_up = (i, price)
        else:
            self._pending_dn = (i, price)
        if self._pending_up is None or self._pending_dn is None:
            return
        cand_start = min(self._pending_up[0], self._pending_dn[0])
        cand_end = i
        cand_hi = self._pending_up[1]
        cand_lo = self._pending_dn[1]
        parent = self._deepest_open() if forming_internal else None
        depth, refuse_reason, parent_id = assign_level(cand_start, cand_end, cand_lo, cand_hi, parent,
                                                       _as_v43_cfg(self._cfg))
        if depth is None:
            events.append(RangeEventV43(kind=refuse_reason or "LEVEL_ASSIGNMENT_UNRESOLVED", bar_index=i,
                                        structure_id=None, depth=None, reason_codes=(refuse_reason or "",),
                                        not_yet_available=()))
            self._clear_pending()
            return
        new_id = self._registry.new_id()
        if depth is Depth.MACRO:
            st_macro = StructureV44(structure_id=new_id, depth=depth, parent_structure_id=parent_id,
                                    start_ts=cand_start, trailing_window=self._cfg.W)
            st_macro.atr_ref = self._last_atr
            offer_swing(st_macro, self._pending_up[1], "high", _as_v43_cfg(self._cfg))
            offer_swing(st_macro, self._pending_dn[1], "low", _as_v43_cfg(self._cfg))
            self._clear_pending()
            st_macro.predecessor_id = self._last_ended_macro_id; self._last_ended_macro_id = None
            action, target_id = self._episode_identity_for_new_macro((cand_lo, cand_hi), i)
            if action == "CONTINUATION":
                st_macro.continued_from_id = target_id
                events.append(RangeEventV43(kind=EPISODE_CONTINUATION, bar_index=i,
                                            structure_id=new_id, depth=Depth.MACRO.name,
                                            reason_codes=(EPISODE_CONTINUATION,), not_yet_available=()))
            elif action == "MERGE":
                st_macro.continued_from_id = target_id
                events.append(RangeEventV43(kind=EPISODE_MERGED, bar_index=i,
                                            structure_id=new_id, depth=Depth.MACRO.name,
                                            reason_codes=(EPISODE_MERGED,), not_yet_available=()))
            else:
                events.append(RangeEventV43(kind=EPISODE_REPLACEMENT, bar_index=i,
                                            structure_id=new_id, depth=Depth.MACRO.name,
                                            reason_codes=(EPISODE_REPLACEMENT,), not_yet_available=()))
            self._active_macro = st_macro
            self._regime = None
        else:
            st_internal = Structure(structure_id=new_id, depth=depth, parent_structure_id=parent_id,
                                    start_ts=cand_start)
            st_internal.atr_ref = self._last_atr
            offer_swing(st_internal, self._pending_up[1], "high", _as_v43_cfg(self._cfg))
            offer_swing(st_internal, self._pending_dn[1], "low", _as_v43_cfg(self._cfg))
            self._clear_pending()
            st_internal.predecessor_id = self._last_ended_internal_id; self._last_ended_internal_id = None
            self._active_internal = st_internal

    # ── inchidere INTERNAL: KILL sau breakout acceptat -- copie byte-identica a V4.3 ──
    def _kill_internal(self, st: Structure, i: int, reason: str, events: list[RangeEventV43]) -> None:
        st.end_ts = i; st.end_reason = reason
        self._registry.kill(st.structure_id)
        self._internal_history.append(st)
        events.append(RangeEventV43(kind=reason, bar_index=i, structure_id=st.structure_id,
                                    depth=Depth.INTERNAL.name, reason_codes=(reason,), not_yet_available=()))
        self._last_ended_internal_id = st.structure_id
        self._active_internal = None; self._internal_excursion = None

    def _close_internal_via_breakout(self, st: Structure, i: int, side: str, events: list[RangeEventV43]) -> None:
        st.end_ts = i; st.end_reason = BREAKOUT_ACCEPTED; st.breakout_side = side
        self._internal_history.append(st)
        events.append(RangeEventV43(kind=BREAKOUT_ACCEPTED, bar_index=i, structure_id=st.structure_id,
                                    depth=Depth.INTERNAL.name, reason_codes=(BREAKOUT_ACCEPTED,),
                                    not_yet_available=(), boundary=side))
        self._last_ended_internal_id = st.structure_id
        self._active_internal = None; self._internal_excursion = None
        self._awaiting_role[st.structure_id] = st

    # ── inchidere MACRO: KILL, breakout acceptat, sau (nou) persistenta WEAKENING ──
    def _kill_macro(self, st: StructureV44, i: int, reason: str, events: list[RangeEventV43]) -> None:
        st.end_ts = i; st.end_reason = reason
        self._registry.kill(st.structure_id)
        self._macro_history.append(st)
        events.append(RangeEventV43(kind=reason, bar_index=i, structure_id=st.structure_id,
                                    depth=Depth.MACRO.name, reason_codes=(reason,), not_yet_available=()))
        self._last_ended_macro_id = st.structure_id
        self._record_macro_termination_for_episode_identity(st, reason)
        self._active_macro = None; self._macro_excursion = None

    def _close_macro_via_breakout(self, st: StructureV44, i: int, side: str, events: list[RangeEventV43]) -> None:
        st.end_ts = i; st.end_reason = BREAKOUT_ACCEPTED; st.breakout_side = side
        self._macro_history.append(st)
        events.append(RangeEventV43(kind=BREAKOUT_ACCEPTED, bar_index=i, structure_id=st.structure_id,
                                    depth=Depth.MACRO.name, reason_codes=(BREAKOUT_ACCEPTED,),
                                    not_yet_available=(), boundary=side))
        self._last_ended_macro_id = st.structure_id
        self._record_macro_termination_for_episode_identity(st, BREAKOUT_ACCEPTED)
        self._active_macro = None; self._macro_excursion = None
        self._promo_direction = 1 if side == "upper" else -1
        self._promo_broken_boundary = st.boundary_upper if side == "upper" else st.boundary_lower
        self._promo_fired = False
        self._promo_external_count = 0
        self._promo_original_id = st.structure_id
        self._awaiting_role[st.structure_id] = st

    def _terminate_macro_weakening_persistence(self, st: StructureV44, i: int, events: list[RangeEventV43]) -> None:
        st.end_ts = i; st.end_reason = WEAKENING_PERSISTENCE_TERMINATED
        self._macro_history.append(st)
        events.append(RangeEventV43(kind=WEAKENING_PERSISTENCE_TERMINATED, bar_index=i,
                                    structure_id=st.structure_id, depth=Depth.MACRO.name,
                                    reason_codes=(WEAKENING_PERSISTENCE_TERMINATED,), not_yet_available=()))
        self._last_ended_macro_id = st.structure_id
        self._record_macro_termination_for_episode_identity(st, WEAKENING_PERSISTENCE_TERMINATED)
        self._active_macro = None; self._macro_excursion = None

    def _record_macro_termination_for_episode_identity(self, st: StructureV44, reason: str) -> None:
        if st.boundary_upper is not None and st.boundary_lower is not None:
            self._last_terminated_macro_zone = (st.boundary_lower, st.boundary_upper)
        else:
            self._last_terminated_macro_zone = None
        self._last_terminated_macro_end_ts = st.end_ts
        self._last_terminated_macro_id = st.structure_id
        self._last_terminated_macro_end_reason = reason

    # ── ceas de reversal (sweep -> confirmare reversal) -- copie byte-identica a V4.3, functioneaza pt. ambele adancimi ──
    def _end_ts_for(self, depth: Depth, structure_id: int) -> int | None:
        active = self._active_macro if depth is Depth.MACRO else self._active_internal
        if active is not None and active.structure_id == structure_id:
            return None
        hist = self._macro_history if depth is Depth.MACRO else self._internal_history
        for s in hist:
            if s.structure_id == structure_id:
                return s.end_ts
        return None   # evacuat din istoricul marginit -- tratat fail-closed ca "expirat" de sweep_reversal_confirmed

    def _check_reversal_watch(self, depth: Depth, i: int, close: float, events: list[RangeEventV43]) -> None:
        watch = self._macro_reversal_watch if depth is Depth.MACRO else self._internal_reversal_watch
        if watch is None:
            return
        ex = Excursion.restore(watch["excursion"])
        episode_end_ts = self._end_ts_for(depth, watch["structure_id"])
        ok, reason = sweep_reversal_confirmed(
            ex, i, close, watch["ref_swing"], watch["ref_confirm_ts"], episode_end_ts)
        if ok:
            events.append(RangeEventV43(kind=LIQUIDITY_SWEEP_REVERSAL, bar_index=i,
                                        structure_id=watch["structure_id"], depth=depth.name,
                                        reason_codes=(LIQUIDITY_SWEEP_REVERSAL,), not_yet_available=()))
            if depth is Depth.MACRO:
                self._macro_reversal_watch = None
            else:
                self._internal_reversal_watch = None
        elif reason == "REVERSAL_WINDOW_EXPIRED":
            if depth is Depth.MACRO:
                self._macro_reversal_watch = None
            else:
                self._internal_reversal_watch = None

    # ── rol retrospectiv -- copie byte-identica a V4.3 ──
    def _resolve_role_if_watched(self, successor: Structure, i: int) -> None:
        pred_id = successor.predecessor_id
        if pred_id is None or pred_id not in self._awaiting_role:
            return
        pred = self._awaiting_role.pop(pred_id)
        if pred.structure_id == self._promo_original_id and self._promo_fired:
            promo_dir_upper = self._promo_direction == 1
            role = "TREND_CONTINUATION_CONFIRMED" if (successor.breakout_side == "upper") == promo_dir_upper \
                else "TREND_EXHAUSTION_CONFIRMED"
        else:
            role = "ACCUMULATION_CONFIRMED" if pred.breakout_side == "upper" else "DISTRIBUTION_CONFIRMED"
        pred.assign_role(role, i)

    # ── promovare -- copie byte-identica a V4.3 (semantica de promovare neatinsa, mandat §16) ──
    def _maybe_promote(self, i: int, events: list[RangeEventV43]) -> None:
        if self._promo_direction is None or self._promo_fired:
            return
        if self._promo_external_count < self._cfg.n_external_swings:
            return
        ok, reason = promotion_check(
            p1_left_frozen_boundary=True, p2_breakout_accepted=True,
            external_swings_confirmed=self._promo_external_count, p4_previous_closed_and_kept=True,
            cfg=_as_v43_cfg(self._cfg))
        if ok:
            self._promo_fired = True
            self._regime = "TREND_UP" if self._promo_direction == 1 else "TREND_DOWN"
            events.append(RangeEventV43(kind=IS_TREND_MACRO, bar_index=i, structure_id=self._promo_original_id,
                                        depth=Depth.MACRO.name, reason_codes=(IS_TREND_MACRO,),
                                        not_yet_available=()))

    @staticmethod
    def _state_label_internal(reason: str) -> str | None:
        if reason == BETWEEN_EPISODES:
            return None
        if reason in (ESTABLISHING_FEW_SWINGS, ATR_UNAVAILABLE, TOO_SHORT_MACRO, TOO_SHORT_INTERNAL):
            return MacroState.RANGE_FORMING.value
        if reason in (OK_RANGE_MACRO, OK_RANGE_INTERNAL):
            return MacroState.RANGE_CONFIRMED.value
        if reason == NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT:
            return MacroState.BOUNDARY_EXCURSION.value
        if reason == SWEEP_CONFIRMED:
            return MacroState.SWEEP_CONFIRMED.value
        if reason == BREAKOUT_ACCEPTED:
            return MacroState.EPISODE_CLOSED.value
        if reason in (ZONES_DEGENERATE, ZONES_INVERTED):
            return MacroState.EPISODE_CLOSED.value
        return None

    def _channel_or_state_label(self, st: Structure | None, reason: str) -> str | None:
        """INTERNAL-only -- copie byte-identica a V4.3 (mandat §19: F4/INTERNAL neatins)."""
        if st is None or st.depth is not Depth.INTERNAL or st.end_ts is not None:
            return self._state_label_internal(reason)
        if reason in (NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT, SWEEP_CONFIRMED, BREAKOUT_ACCEPTED):
            return self._state_label_internal(reason)
        if st.atr_ref is None or st.atr_ref <= 0 or st.n_bars < 2:
            return self._state_label_internal(reason)
        drift = st.normalized_drift(st.atr_ref)
        if drift > self._cfg.tol_cluster:   # `s_max` V4.3 == `tol_cluster` numeric (2*w_atr), neschimbat
            slope_sign = st._drift.slope()
            return InternalState.INT_CHANNEL_UP.value if slope_sign > 0 else InternalState.INT_CHANNEL_DOWN.value
        base = self._state_label_internal(reason)
        if base == MacroState.RANGE_CONFIRMED.value:
            return InternalState.INT_SUBRANGE.value
        if base == MacroState.RANGE_FORMING.value:
            return InternalState.INT_BALANCE.value
        return base

    def _macro_state_label(self, st: StructureV44 | None, reason: str) -> str | None:
        """NOU V4.4 -- 5 stari (CANDIDATE/FORMING/CONFIRMED/WEAKENING/TERMINATED), inlocuieste `MacroState`
        pt. raportarea MACRO (INTERNAL foloseste in continuare `MacroState`/`InternalState` V4.3 neschimbat,
        via `_channel_or_state_label` de mai sus)."""
        if reason == BETWEEN_EPISODES or st is None:
            return None
        if st.end_ts is not None:
            return "TERMINATED"
        if not st.reached_confirmed:
            if reason in (ESTABLISHING_FEW_SWINGS, ATR_UNAVAILABLE):
                return "CANDIDATE"
            return "FORMING"
        if st.weakening_reason is not None:
            return "WEAKENING"
        return "CONFIRMED"

    # ── pas INTERNAL: copie byte-identica a ramurii INTERNAL din `_step_depth` V4.3 ──
    def _step_internal(self, i: int, high: float, low: float, close: float, events: list[RangeEventV43]) -> str:
        st = self._active_internal
        if st is None:
            return BETWEEN_EPISODES
        kill = degeneracy_check(st, _as_v43_cfg(self._cfg))
        if kill in (ZONES_INVERTED, ZONES_DEGENERATE):
            self._kill_internal(st, i, kill, events)
            return kill
        zones = st.zones(self._cfg.w_atr) if st.reached_confirmed else None
        excursion = self._internal_excursion
        if excursion is not None and zones is not None:
            (up_lo, up_hi), (lo_lo, lo_hi) = zones
            side = "upper" if excursion.direction == 1 else "lower"
            outside = close > up_hi if side == "upper" else close < lo_lo
            kind, nya = excursion.observe(i, outside, _as_v43_cfg(self._cfg))
            if kind == BREAKOUT_ACCEPTED:
                self._close_internal_via_breakout(st, i, side, events)
                return BREAKOUT_ACCEPTED
            if kind == SWEEP_CONFIRMED:
                events.append(RangeEventV43(kind=SWEEP_CONFIRMED, bar_index=i, structure_id=st.structure_id,
                                            depth=Depth.INTERNAL.name, reason_codes=(SWEEP_CONFIRMED,),
                                            not_yet_available=(), boundary=side))
                ref_side = "upper" if excursion.direction == -1 else "lower"
                watch = {"excursion": excursion.snapshot(), "structure_id": st.structure_id,
                         "ref_side": ref_side,
                         "ref_swing": (st.up.center if ref_side == "upper" else st.dn.center),
                         "ref_confirm_ts": st.confirm_ts}
                self._internal_excursion = None
                self._internal_reversal_watch = watch
                return SWEEP_CONFIRMED
            events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=st.structure_id,
                                        depth=Depth.INTERNAL.name, reason_codes=(), not_yet_available=nya,
                                        boundary=side))
            return NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
        if zones is not None:
            (up_lo, up_hi), (lo_lo, lo_hi) = zones
            if close > up_hi or close < lo_lo:
                side = "upper" if close > up_hi else "lower"
                ex = Excursion(open_bar=i - 1, direction=1 if side == "upper" else -1)
                self._internal_excursion = ex
                kind, nya = ex.observe(i, True, _as_v43_cfg(self._cfg))
                if kind == BREAKOUT_ACCEPTED:
                    self._close_internal_via_breakout(st, i, side, events)
                    return BREAKOUT_ACCEPTED
                events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=st.structure_id,
                                            depth=Depth.INTERNAL.name, reason_codes=(), not_yet_available=nya,
                                            boundary=side))
                return NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
        reason = evaluate_candidate_with_n_touch(st, i, _as_v43_cfg(self._cfg))
        if reason in (OK_RANGE_MACRO, OK_RANGE_INTERNAL) and not st.reached_confirmed:
            st.reached_confirmed = True
            if st.confirm_ts is None:
                st.confirm_ts = i
            st.up.frozen = True
            st.dn.frozen = True
            events.append(RangeEventV43(kind=reason, bar_index=i, structure_id=st.structure_id,
                                        depth=Depth.INTERNAL.name, reason_codes=(reason,), not_yet_available=()))
            self._resolve_role_if_watched(st, i)
        return reason

    # ── formare MACRO: T2 (width+touch -> FORMING) si T3 (+durata+poarta de discriminare -> CONFIRMED) ──
    def _evaluate_macro_formation(self, st: StructureV44, i: int, events: list[RangeEventV43]) -> str:
        bu, bl = st.boundary_upper, st.boundary_lower
        if bu is None or bl is None or st.atr_ref is None:
            return ATR_UNAVAILABLE if st.atr_ref is None else ESTABLISHING_FEW_SWINGS
        if len(st.up.members) < self._cfg.n_touch or len(st.dn.members) < self._cfg.n_touch:
            return ESTABLISHING_FEW_SWINGS
        # T2: latime+atingeri satisfacute -- candidat "prezent", raportat o singura data (mandat §8 f241698,
        # distinge explicit RANGE PRESENT de RANGE FIRST CONFIRMED NOW)
        if not st._candidate_present_emitted:
            st._candidate_present_emitted = True
            events.append(RangeEventV43(kind=RANGE_CANDIDATE_PRESENT, bar_index=i, structure_id=st.structure_id,
                                        depth=Depth.MACRO.name, reason_codes=(RANGE_CANDIDATE_PRESENT,),
                                        not_yet_available=()))
        if i - st.start_ts < self._cfg.d_macro:
            return TOO_SHORT_MACRO
        # T3: poarta de discriminare, prioritate FIXA ER -> traversal -> RND (mandat §12 ordine determinista
        # cand mai multe porti esueaza simultan)
        er = efficiency_ratio(st._trailing_closes)
        if er > self._cfg.ER_max:
            return INSUFFICIENT_EFFICIENCY
        trav = traversal_count(st._trailing_closes, bu, bl)
        if trav < self._cfg.MIN_TRAVERSALS:
            return INSUFFICIENT_TRAVERSAL
        rnd = relative_net_displacement(st._trailing_closes, bu, bl)
        if rnd > self._cfg.RND_max:
            return EXCESSIVE_NET_DISPLACEMENT
        # alternation -- SUPPORTING_ONLY (mandat §5: nu promovata la hard-gate), deci NU blocheaza
        # confirmarea; dar dovada slaba/insuficienta tot trebuie RAPORTATA (eveniment separat, aditional,
        # nu inlocuieste OK_RANGE_MACRO) -- altfel codul e definit dar de neatins (bug real gasit si corectat
        # inaintea inghetului: `alternation_rate`/`ALT_MIN`/`touches_in_window` erau definite dar niciodata
        # cablate impreuna cu restul portii T3)
        alt = alternation_rate(st.touches_in_window(i, self._cfg.W))
        if alt is None or alt < self._cfg.ALT_MIN:
            events.append(RangeEventV43(kind=INSUFFICIENT_ALTERNATION_EVIDENCE, bar_index=i,
                                        structure_id=st.structure_id, depth=Depth.MACRO.name,
                                        reason_codes=(INSUFFICIENT_ALTERNATION_EVIDENCE,), not_yet_available=()))
        st.reached_confirmed = True
        if st.confirm_ts is None:
            st.confirm_ts = i
        st.up.frozen = True
        st.dn.frozen = True
        if self._promo_direction is not None:
            # copie a regulii V4.3 (mandat §8): un MACRO nou care CONFIRMA (nu doar se formeaza) inainte
            # ca fereastra de promovare sa se rezolve inchide acea fereastra -- piata s-a consolidat din
            # nou, nu a confirmat un trend
            self._promo_direction = None; self._promo_broken_boundary = None; self._promo_external_count = 0
        events.append(RangeEventV43(kind=OK_RANGE_MACRO, bar_index=i, structure_id=st.structure_id,
                                    depth=Depth.MACRO.name, reason_codes=(OK_RANGE_MACRO,), not_yet_available=()))
        self._resolve_role_if_watched(st, i)
        return OK_RANGE_MACRO

    # ── pas MACRO: T-KILL, T4-T9 (excursie/weakening/terminare) -- vezi tabelul de tranzitii f241698 §3 ──
    def _step_macro(self, i: int, high: float, low: float, close: float, events: list[RangeEventV43]) -> str:
        st = self._active_macro
        if st is None:
            return BETWEEN_EPISODES
        kill = degeneracy_check(st, _as_v43_cfg(self._cfg))
        if kill in (ZONES_INVERTED, ZONES_DEGENERATE):
            self._kill_macro(st, i, kill, events)
            return kill

        zones = st.zones(self._cfg.w_atr) if st.reached_confirmed else None
        if zones is None:
            return self._evaluate_macro_formation(st, i, events)

        (up_lo, up_hi), (lo_lo, lo_hi) = zones
        excursion = self._macro_excursion
        excursion_active_this_bar = False
        excursion_reported_reason: str | None = None

        if excursion is not None:
            side = "upper" if excursion.direction == 1 else "lower"
            outside = close > up_hi if side == "upper" else close < lo_lo
            kind, nya = excursion.observe(i, outside, _as_v43_cfg(self._cfg))
            excursion_active_this_bar = True
            if kind == BREAKOUT_ACCEPTED:
                self._close_macro_via_breakout(st, i, side, events)
                return BREAKOUT_ACCEPTED   # T8 -- terminare neconditionata, are prioritate absoluta
            if kind == SWEEP_CONFIRMED:
                events.append(RangeEventV43(kind=SWEEP_CONFIRMED, bar_index=i, structure_id=st.structure_id,
                                            depth=Depth.MACRO.name, reason_codes=(SWEEP_CONFIRMED,),
                                            not_yet_available=(), boundary=side))
                ref_side = "upper" if excursion.direction == -1 else "lower"
                self._macro_reversal_watch = {"excursion": excursion.snapshot(), "structure_id": st.structure_id,
                                              "ref_side": ref_side,
                                              "ref_swing": (st.up.center if ref_side == "upper" else st.dn.center),
                                              "ref_confirm_ts": st.confirm_ts}
                self._macro_excursion = None
                excursion_active_this_bar = False   # excursia s-a rezolvat -- T5 poate re-evalua chiar in aceasta bara
                if st.weakening_reason == "EXCURSION_PENDING":
                    st.weakening_reason = None
                    events.append(RangeEventV43(kind=WEAKENING_RECOVERED, bar_index=i, structure_id=st.structure_id,
                                                depth=Depth.MACRO.name, reason_codes=(WEAKENING_RECOVERED,),
                                                not_yet_available=()))
                    excursion_reported_reason = WEAKENING_RECOVERED   # T6
                else:
                    excursion_reported_reason = SWEEP_CONFIRMED
            else:
                events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=st.structure_id,
                                            depth=Depth.MACRO.name, reason_codes=(), not_yet_available=nya,
                                            boundary=side))
                excursion_reported_reason = NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
        elif close > up_hi or close < lo_lo:
            side = "upper" if close > up_hi else "lower"
            ex = Excursion(open_bar=i - 1, direction=1 if side == "upper" else -1)
            self._macro_excursion = ex
            excursion_active_this_bar = True
            kind, nya = ex.observe(i, True, _as_v43_cfg(self._cfg))
            # T4, prioritate NECONDITIONATA -- o excursie noua etichteaza structura EXCURSION_PENDING
            # indiferent de sub-starea TRAILING_DEGRADATION anterioara (disclosed edge-case simplification,
            # vezi docstring-ul modulului si raportul de livrare)
            st.weakening_reason = "EXCURSION_PENDING"
            events.append(RangeEventV43(kind=RANGE_WEAKENING, bar_index=i, structure_id=st.structure_id,
                                        depth=Depth.MACRO.name, reason_codes=(RANGE_WEAKENING,),
                                        not_yet_available=()))
            if kind == BREAKOUT_ACCEPTED:   # posibil doar daca N_accept==1
                self._close_macro_via_breakout(st, i, side, events)
                return BREAKOUT_ACCEPTED
            events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=st.structure_id,
                                        depth=Depth.MACRO.name, reason_codes=(), not_yet_available=nya,
                                        boundary=side))
            excursion_reported_reason = NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT

        # T5/T7/T9: degradare pe fereastra marginita -- ruleaza in fiecare bara, independent de excursie
        # (dar eticheta RAPORTATA respecta prioritatea T4, mai jos)
        er = efficiency_ratio(st._trailing_closes)
        rnd = relative_net_displacement(st._trailing_closes, st.boundary_upper, st.boundary_lower)
        trailing_reported_reason: str | None = None

        if st.weakening_reason == "TRAILING_DEGRADATION":
            st._weakening_bars += 1
            recovered = (er <= self._cfg.ER_max and rnd <= self._cfg.RND_max)
            if recovered:
                st.weakening_reason = None
                st._weakening_bars = 0
                events.append(RangeEventV43(kind=WEAKENING_RECOVERED, bar_index=i, structure_id=st.structure_id,
                                            depth=Depth.MACRO.name, reason_codes=(WEAKENING_RECOVERED,),
                                            not_yet_available=()))
                trailing_reported_reason = WEAKENING_RECOVERED   # T7
            elif st._weakening_bars >= self._cfg.WEAKENING_MAX_BARS:
                self._terminate_macro_weakening_persistence(st, i, events)
                return WEAKENING_PERSISTENCE_TERMINATED   # T9
            else:
                trailing_reported_reason = RANGE_WEAKENING
        elif not excursion_active_this_bar:
            degraded = (er > self._cfg.ER_weakening or rnd > self._cfg.RND_weakening)
            if degraded:
                st.weakening_reason = "TRAILING_DEGRADATION"
                st._weakening_bars = 1
                events.append(RangeEventV43(kind=RANGE_WEAKENING, bar_index=i, structure_id=st.structure_id,
                                            depth=Depth.MACRO.name, reason_codes=(RANGE_WEAKENING,),
                                            not_yet_available=()))
                trailing_reported_reason = RANGE_WEAKENING   # T5

        if excursion_reported_reason is not None:
            return excursion_reported_reason
        if trailing_reported_reason is not None:
            return trailing_reported_reason
        return OK_RANGE_MACRO

    # ── pas per bara -- structura identica cu `observe()` V4.3, MACRO deleaga la `_step_macro` ──
    def observe(self, *, ts_close: int, open_: float, high: float, low: float, close: float,
               atr: float | None, trend_context: str | None = None
              ) -> tuple[RangeSemanticResultV44, list[RangeEventV43]]:
        i = self._n
        self._n += 1
        self._wh.append(high); self._wl.append(low)
        self._last_atr = atr
        events: list[RangeEventV43] = []

        if atr is not None:
            if self._active_macro is not None:
                self._active_macro.atr_ref = atr
            if self._active_internal is not None:
                self._active_internal.atr_ref = atr

        for sw_bar, price, is_high in self._detect_confirmed_swings(i):
            self._offer_swing_everywhere(sw_bar, price, is_high, events)

        if self._active_macro is not None:
            self._active_macro.push_close_v44(i, close)
        if self._active_internal is not None:
            self._active_internal.push_close(close)

        macro_reason = self._step_macro(i, high, low, close, events)
        internal_reason = self._step_internal(i, high, low, close, events)
        self._check_reversal_watch(Depth.MACRO, i, close, events)
        self._check_reversal_watch(Depth.INTERNAL, i, close, events)

        m = self._active_macro
        n = self._active_internal
        macro_state = self._regime if (m is None and self._regime is not None) else self._macro_state_label(m, macro_reason)
        internal_state = self._channel_or_state_label(n, internal_reason)
        result = RangeSemanticResultV44(
            available=atr is not None, bar_index=i, ts_close=ts_close,
            macro_id=m.structure_id if m else None, macro_reason=macro_reason, macro_state=macro_state,
            macro_weakening_reason=m.weakening_reason if m else None,
            macro_boundary_upper=m.boundary_upper if m else None,
            macro_boundary_lower=m.boundary_lower if m else None,
            macro_confirm_ts=m.confirm_ts if m else None,
            macro_role=m.role if m else None,
            macro_continued_from_id=m.continued_from_id if m else None,
            regime=self._regime if m is None else None,
            internal_id=n.structure_id if n else None, internal_reason=internal_reason,
            internal_state=internal_state,
            internal_boundary_upper=n.boundary_upper if n else None,
            internal_boundary_lower=n.boundary_lower if n else None,
            internal_role=n.role if n else None,
            config_id=self._cfg.config_id(), contract_version=self._cfg.contract_version)
        return result, events

    # ── snapshot / restore integral -- fail-closed pe contract_version + config_id + implementation_fingerprint ──
    def snapshot_state(self) -> dict[str, Any]:
        return {
            "contract_version": self._cfg.contract_version, "config_id": self._cfg.config_id(),
            "implementation_fingerprint": RANGE_HIERARCHICAL_V4_4_IMPLEMENTATION_FINGERPRINT,
            "n": self._n, "wh": list(self._wh), "wl": list(self._wl), "last_atr": self._last_atr,
            "registry": self._registry.snapshot(),
            "active_macro": self._active_macro.snapshot() if self._active_macro else None,
            "active_internal": self._active_internal.snapshot() if self._active_internal else None,
            "macro_excursion": self._macro_excursion.snapshot() if self._macro_excursion else None,
            "internal_excursion": self._internal_excursion.snapshot() if self._internal_excursion else None,
            "macro_reversal_watch": self._macro_reversal_watch,
            "internal_reversal_watch": self._internal_reversal_watch,
            "pending_up": list(self._pending_up) if self._pending_up else None,
            "pending_dn": list(self._pending_dn) if self._pending_dn else None,
            "promo_direction": self._promo_direction, "promo_broken_boundary": self._promo_broken_boundary,
            "promo_external_count": self._promo_external_count, "promo_original_id": self._promo_original_id,
            "promo_fired": self._promo_fired, "regime": self._regime,
            "macro_history": [s.snapshot() for s in self._macro_history],
            "internal_history": [s.snapshot() for s in self._internal_history],
            "awaiting_role": {k: v.snapshot() for k, v in self._awaiting_role.items()},
            "last_ended_macro_id": self._last_ended_macro_id,
            "last_ended_internal_id": self._last_ended_internal_id,
            "last_terminated_macro_zone": list(self._last_terminated_macro_zone) if self._last_terminated_macro_zone else None,
            "last_terminated_macro_end_ts": self._last_terminated_macro_end_ts,
            "last_terminated_macro_id": self._last_terminated_macro_id,
            "last_terminated_macro_end_reason": self._last_terminated_macro_end_reason,
        }

    def restore_state(self, st: dict[str, Any]) -> None:
        """Atomic: construit integral intr-o instanta SCRATCH separata (niciodata `self`) si abia la final
        `self.__dict__` e inlocuit dintr-o singura mutare -- daca ORICE camp lipseste/e corupt/are tipul
        gresit, exceptia se ridica inainte ca `self` sa fie atins, deci `self` ramane COMPLET neschimbat
        (mandat §11: 'no partial state mutation on failed restore'). Imbunatatire deliberata fata de
        `RangeSemanticProducerV43.restore_state()` (care muteaza `self` direct, camp cu camp, si poate lasa
        stare mixta veche/noua la un esec la jumatate -- bug real, confirmat ca preexistent si in V4.3, gasit
        prin testare inaintea inghetului V4.4). V4.3 ramane byte-neatins (mandat §3); aceasta e o proprietate
        NOUA doar a fisierului V4.4, nu o modificare a celuilalt. Garantia publica de nivel motor
        (`RangeSemanticEngineV44.restore`, care oricum construia deja fresh-apoi-swap) era deja corecta --
        aceasta extinde aceeasi disciplina si la nivelul producatorului insusi, apelabil direct."""
        if (st.get("contract_version") != self._cfg.contract_version
                or st.get("config_id") != self._cfg.config_id()
                or st.get("implementation_fingerprint") != RANGE_HIERARCHICAL_V4_4_IMPLEMENTATION_FINGERPRINT):
            raise ContractErrorV43(SNAPSHOT_CONTRACT_MISMATCH)
        fresh = RangeSemanticProducerV44(self._cfg)
        k = self._cfg.K_struct
        fresh._n = st["n"]
        fresh._wh = deque(st["wh"], maxlen=2 * k + 1)
        fresh._wl = deque(st["wl"], maxlen=2 * k + 1)
        fresh._last_atr = st["last_atr"]
        fresh._registry = Registry.restore(st["registry"])
        fresh._active_macro = StructureV44.restore(st["active_macro"]) if st["active_macro"] else None
        fresh._active_internal = Structure.restore(st["active_internal"]) if st["active_internal"] else None
        fresh._macro_excursion = Excursion.restore(st["macro_excursion"]) if st["macro_excursion"] else None
        fresh._internal_excursion = (
            Excursion.restore(st["internal_excursion"]) if st["internal_excursion"] else None)
        fresh._macro_reversal_watch = st["macro_reversal_watch"]
        fresh._internal_reversal_watch = st["internal_reversal_watch"]
        fresh._pending_up = tuple(st["pending_up"]) if st["pending_up"] else None
        fresh._pending_dn = tuple(st["pending_dn"]) if st["pending_dn"] else None
        fresh._promo_direction = st["promo_direction"]; fresh._promo_broken_boundary = st["promo_broken_boundary"]
        fresh._promo_external_count = st["promo_external_count"]
        fresh._promo_original_id = st["promo_original_id"]
        fresh._promo_fired = st["promo_fired"]; fresh._regime = st["regime"]
        fresh._macro_history = deque((StructureV44.restore(s) for s in st["macro_history"]), maxlen=64)
        fresh._internal_history = deque((Structure.restore(s) for s in st["internal_history"]), maxlen=64)
        # `_awaiting_role` poate contine atat structuri MACRO post-breakout (StructureV44) cat si INTERNAL
        # (Structure simplu) -- discriminat pe `depth`, nu presupus uniform (bug real gasit si corectat
        # inainte de inghet: reconstructia UNIFORMA via `Structure.restore()` retrograda silentios orice
        # StructureV44 aflata in asteptarea rolului la un `Structure` simplu, pierzand campurile v44_*).
        fresh._awaiting_role = {
            int(k2): (StructureV44.restore(v) if v.get("depth") == Depth.MACRO.value else Structure.restore(v))
            for k2, v in st["awaiting_role"].items()}
        fresh._last_ended_macro_id = st["last_ended_macro_id"]
        fresh._last_ended_internal_id = st["last_ended_internal_id"]
        fresh._last_terminated_macro_zone = (
            tuple(st["last_terminated_macro_zone"]) if st["last_terminated_macro_zone"] else None)
        fresh._last_terminated_macro_end_ts = st["last_terminated_macro_end_ts"]
        fresh._last_terminated_macro_id = st["last_terminated_macro_id"]
        fresh._last_terminated_macro_end_reason = st["last_terminated_macro_end_reason"]
        self.__dict__ = fresh.__dict__


# ═══════════════════════════════════ amprenta de implementare (mandat §12 -- calculata DUPA scrierea codului) ═══════════════════════════════════
# Procedura identica cu precedentul `RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT` (`bc6b9dc`,
# remedierea F1-only): sha256 peste bytes-ul sursa FINALIZAT al ambelor fisiere V4.4 semnificative
# (`range_semantic_v4_4.py` + `range_engine_v4_4.py`) calculat DUPA ce codul a fost inghetat, valoarea hash
# reala inregistrata in raportul de livrare -- constanta de mai jos e o eticheta umana descriptiva
# (data+mandat), nu digest-ul hexazecimal brut, exact conventia deja folosita de precedentul V4.3 (eticheta
# lui e "f1-only-f5-deferred-2026-08-20", nu un hash). Orice schimbare semnificativa dupa acest inghet
# trebuie sa schimbe aceasta eticheta.
RANGE_HIERARCHICAL_V4_4_IMPLEMENTATION_FINGERPRINT = "v4-4-implementation-freeze-2026-08-20"
