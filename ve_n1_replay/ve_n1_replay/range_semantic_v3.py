"""RANGE SEMANTIC V3 (0.4.0) — redesign LONGITUDINAL, spațiu de nume PROPRIU `range-semantic-v3.0`.

Sursă normativă: Statistician STAT-RANGE-SEMANTIC-SPEC-V3-v1.0 @`bf9f780`, manifest v2.7.84 @`db098ed`,
fingerprint `cddaab381f0132eac025e9fcad3454d54fca78dc1abab6bc8b3cea05e5951233` (verificat exact). Consumă
lotul `RANGE_HUMAN_LABEL_BATCH_01` — proveniență **CEO_ASSISTED**, **construction-only PERMANENT** (NU
blind, NU independent, NU OOS, NU validare). NU reutilizează și NU reinterpretează `StructBand.RANGE` sau
enumurile din `range_state_v2*.py` (0.2.0/0.3.x, NEATINSE, păstrate pentru audit).

**Cele patru defecte structurale închise aici** (măsurate de Statistician, nu doar presupuse):
  D1  ancora se calcula pe `range_window=512` bare, mărginind un range minim de `d_min=96` — 5,3× prea larg.
      FIX: ancora e calculată EXCLUSIV din swing-urile acumulate DIN structural_start-ul SEGMENTULUI curent,
      niciodată dintr-o fereastră fixă externă segmentului.
  D2  `anchor_upper` putea ajunge SUB `anchor_lower` — nicio gardă. FIX: geometria degenerată e
      STRUCTURAL IMPOSIBILĂ de reprezentat ca validă — segmentul nu poate ajunge ESTABLISHED cât timp
      `anchor_upper <= anchor_lower` SAU zonele s-ar suprapune (`ZONES_DEGENERATE`, fail-closed prin tip).
  D3  `bars_in_state` satura la ~508 (peste `d_min`), deci `TOO_SHORT` nu putea fi emis NICIODATĂ — o
      cerință care nu poate eșua nu e o cerință. FIX: durata se măsoară de la `structural_start` AL
      SEGMENTULUI (nu vârsta celui mai vechi swing reținut într-un buffer extern) — real, demonstrabil.
  D4  o rupere acceptată ȘTERGEA episodul (76,65% din bare) — aceeași CLASĂ de defect ca V1 (regula
      proprie distruge precondiția alteia). FIX: `S2` — acceptarea ÎNCHEIE segmentul (`TERMINATED_BY_
      BREAKOUT`), NU îl șterge; segmentul rămâne în ISTORIC ca un range confirmat care S-A ÎNTÂMPLAT,
      succesorul poartă `predecessor_id`.

**S1 — segmentare longitudinală**: o fereastră NU are o stare, are o SECVENȚĂ de segmente cu tranziții
explicite (17/24 ferestre HBL sunt multi-regim). **S3 — sweep cauzal**: breach-ul se detectează pe MEȘĂ
(high/low față de zonă — un wick-sweep dintr-o SINGURĂ bară trebuie să fie reprezentabil, semnătura D6
reutilizată din 0.3.x), NU pe close — deschide `BREACH_PENDING` (stare AMBIGUĂ prin contract, NU o
clasificare). Rezoluția se decide pe CLOSE, cursă între două praguri asupra ACELUIAȘI contor
(`pending_consec_outside`, bare de la breach încoace, breach = bara 1): reintrare cu `bars_pending <= K` →
`LIQUIDITY_SWEEP_*` (confirm_ts = bara reintrării, NICIODATĂ bara breach-ului); `bars_pending >= N` fără
reintrare → `BREAKOUT_ACCEPTANCE_*` (segmentul SE TERMINĂ); reintrare REALĂ dar cu `bars_pending > K` →
`SWEEP_WINDOW_EXPIRED` (nici sweep, nici breakout — revine la evaluare normală). Invariantul **`K<=N`** e
OBLIGATORIU: dacă `K>N`, segmentul ar muri deja prin breakout la bara N (N<=K) înainte ca fereastra K să
poată vreodată expira — exact defectul "parametru neutilizabil prin construcție" pe care mandatul îl
interzice. Reprodus exact pe fixture-ul HBL-20 (bara 52 breach pe low, bara 56 reintrare/confirm pe close,
bara 63 markup) — construction-only, nu blind, nu profitabilitate.

**Parametrii `K`/`N`/`w_atr` sunt NEIDENTIFICAȚI** (§6.4 din spec) — `RangeConfigV3` îi CERE explicit, fără
default ascuns, și refuză construcția fără `acknowledge_construction_only=True` — suprafața de producție
refuză configurația neratificată PRIN CONSTRUCȚIE, nu doar prin documentație.
"""
from __future__ import annotations

import dataclasses as _dc
import hashlib
import heapq
import math
from collections import deque
from enum import Enum
from typing import Any

from .version import (
    RANGE_SEMANTIC_CONTRACT_VERSION_V3, RANGE_STATE_MACHINE_VERSION_V3, RANGE_EVENT_CONTRACT_VERSION_V3,
    RANGE_CONFIG_SCHEMA_VERSION_V3, RANGE_PRODUCER_VERSION_V3, RANGE_V3_STATISTICIAN_SPEC_COMMIT,
    RANGE_V3_MANIFEST_COMMIT, RANGE_V3_MANIFEST_FINGERPRINT, RANGE_V3_HBL_PROVENANCE,
    BARS_PER_DAY_M15, BARS_PER_INTRADAY_SESSION_M15,
    RANGE_V3_K_STATUS, RANGE_V3_N_ACCEPTANCE_STATUS, RANGE_V3_W_ATR_STATUS, RANGE_V3_ANCHOR_WINDOW_RULE,
)

_K_FRACTAL: int = 2   # k-ul fractalilor de swing (identic cu N1/V1/V2 — K_DEFAULT din market_structure)


# ═══════════════════════════════════ excepții ═══════════════════════════════════
class ConfigNotRatifiedError(Exception):
    """Refuz fail-closed: `RangeConfigV3` construit fără confirmarea explicită `acknowledge_construction_only`,
    sau cu un parametru NEIDENTIFICAT lipsă. NU există default ascuns pentru K/N/w_atr."""


class RangeSemanticContractErrorV3(Exception):
    """Tranziție interzisă / geometrie degenerată prezentată ca validă — fail-closed."""


# ═══════════════════════════════════ enums — spațiu de nume PROPRIU ═══════════════════════════════════
class SegmentEventKindV3(Enum):
    """Exact cele 14 stări/evenimente din SPEC V3 §6.2 @bf9f780 — nicio reconstrucție din conversație."""
    RANGE_ESTABLISHING = "RANGE_ESTABLISHING"
    RANGE_ESTABLISHED = "RANGE_ESTABLISHED"
    RANGE_MID = "RANGE_MID"
    BOUNDARY_TEST_UPPER = "BOUNDARY_TEST_UPPER"
    BOUNDARY_TEST_LOWER = "BOUNDARY_TEST_LOWER"
    LIQUIDITY_SWEEP_UP = "LIQUIDITY_SWEEP_UP"
    LIQUIDITY_SWEEP_DOWN = "LIQUIDITY_SWEEP_DOWN"
    BREAKOUT_ACCEPTANCE_UP = "BREAKOUT_ACCEPTANCE_UP"
    BREAKOUT_ACCEPTANCE_DOWN = "BREAKOUT_ACCEPTANCE_DOWN"
    RANGE_FAILED = "RANGE_FAILED"
    CHANNEL_UP = "CHANNEL_UP"
    CHANNEL_DOWN = "CHANNEL_DOWN"
    TRANSITION = "TRANSITION"
    UNAVAILABLE = "UNAVAILABLE"


class SegmentLifecycleV3(Enum):
    """Starea internă a mașinii — mai fină decât cele 14 evenimente publice (un ESTABLISHING poate emite
    BOUNDARY_TEST_*/RANGE_MID la fel ca un ESTABLISHED; evenimentul public descrie BARA, starea descrie
    SEGMENTUL)."""
    NONE = "NONE"                       # niciun segment activ — TRANSITION sau UNAVAILABLE
    ESTABLISHING = "ESTABLISHING"
    ESTABLISHED = "ESTABLISHED"
    BREACH_PENDING = "BREACH_PENDING"   # depășire deschisă — cursă sweep-vs-breakout


# reason codes (spec §6.2 + §6.3, spațiu de nume v3, distinct de v2)
OK_RANGE = "OK_RANGE"
RANGE_FORMING = "RANGE_FORMING"
ESTABLISHING_FEW_SWINGS = "ESTABLISHING_FEW_SWINGS"
ATR_UNAVAILABLE = "ATR_UNAVAILABLE"
FEW_TOUCHES = "FEW_TOUCHES"
TOO_SHORT = "TOO_SHORT"
IS_CHANNEL = "IS_CHANNEL"
ZONES_DEGENERATE = "ZONES_DEGENERATE"
BETWEEN_SEGMENTS = "BETWEEN_SEGMENTS"
TERMINATED_BY_BREAKOUT = "TERMINATED_BY_BREAKOUT"
RANGE_FAILED_PRECONDITION = "RANGE_FAILED_PRECONDITION"
SWEEP_WINDOW_EXPIRED = "SWEEP_WINDOW_EXPIRED"   # reintrare reală, dar prea târzie (>K bare) ca să conteze sweep curat

# `not_yet_available` — cursa sweep-vs-breakout e explicit AMBIGUĂ între breach și rezoluție (S3: pe bara
# breach-ului informația "e sweep" încă NU există) — un marcaj distinct, nu unul din reason codes de mai sus.
NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT = "sweep_or_breakout_undetermined"

REASON_CODES_V3: tuple[str, ...] = (
    OK_RANGE, RANGE_FORMING, ESTABLISHING_FEW_SWINGS, ATR_UNAVAILABLE, FEW_TOUCHES, TOO_SHORT, IS_CHANNEL,
    ZONES_DEGENERATE, BETWEEN_SEGMENTS, TERMINATED_BY_BREAKOUT, RANGE_FAILED_PRECONDITION, SWEEP_WINDOW_EXPIRED,
)

# F7 SAFETY_GUARD — neschimbat semantic (manifest v2.7.84: „F7 SAFETY_GUARD" rămâne în invarianții neatinși)
SAFETY_GUARD_RANGE_MID_NO_ENTRY = "RANGE_MID_NO_ENTRY"
SAFETY_GUARDS_REGISTER: tuple[str, ...] = (SAFETY_GUARD_RANGE_MID_NO_ENTRY,)


@_dc.dataclass(frozen=True, slots=True)
class EntryDecisionV3:
    permitted: bool
    guard: str | None
    reason: str


def entry_decision_v3(event: "RangeEventV3 | None") -> EntryDecisionV3:
    if event is not None and event.kind == SegmentEventKindV3.RANGE_MID.value:
        return EntryDecisionV3(permitted=False, guard=SAFETY_GUARD_RANGE_MID_NO_ENTRY, reason="RANGE_MID_NO_ENTRY")
    return EntryDecisionV3(permitted=True, guard=None, reason="")


def _sha(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


# ═══════════════════════════════════ configurație — NIMIC ascuns ═══════════════════════════════════
@_dc.dataclass(frozen=True, slots=True)
class RangeConfigV3:
    """`K`, `N`, `w_atr` sunt NEIDENTIFICATE de lotul `CEO_ASSISTED` — CERUTE explicit, FĂRĂ default. Nu se
    transportă automat valorile 0.3.1 (ancora s-a schimbat de la fereastră fixă la segment-locală ⇒ `w_atr`
    ratificat SUB ancora veche NU e valabil sub cea nouă — trebuie reidentificat). Construcția REFUZĂ fără
    `acknowledge_construction_only=True` — suprafața de producție refuză configurația neratificată prin TIP,
    nu doar prin documentație."""
    K: int                              # fereastra de reintrare pt. sweep — NEIDENTIFICAT, CERUT explicit
    N: int                              # închideri consecutive pt. acceptare — NEIDENTIFICAT, CERUT explicit
    w_atr: float                        # semilățime zonă (ATR) — NEIDENTIFICAT SUB noua ancoră, CERUT explicit
    acknowledge_construction_only: bool = False   # TREBUIE True — altfel refuz fail-closed la __post_init__
    n_touch: int = 2                    # MOȘTENIT (nemarcat NEIDENTIFICAT în spec)
    d_min_bars: int = BARS_PER_DAY_M15  # MOȘTENIT; implicit MULTIDAY — vezi .intraday()/.multiday()
    duration_class: str = "MULTIDAY_RANGE"
    timeframe: str = "15m"
    swing_k: int = _K_FRACTAL
    atr_window: int = 14
    max_duration_bars: int | None = None          # opțional, plasă de siguranță — NU cerut de spec
    segment_history_limit: int = 64               # segmente CONFIRMATE păstrate pt. audit (mărginit, nu tot istoricul)

    def __post_init__(self) -> None:
        if not self.acknowledge_construction_only:
            raise ConfigNotRatifiedError(
                "RangeConfigV3 refuzat: configurația e CONSTRUCTION_ONLY/NERATIFICATĂ (K/N/w_atr "
                "NEIDENTIFICATE de lotul CEO_ASSISTED) — construcția cere acknowledge_construction_only=True "
                "explicit; nu există default ascuns care să ocolească această confirmare")
        if self.K > self.N:
            raise RangeSemanticContractErrorV3(
                f"K={self.K} > N={self.N}: un segment NU poate supraviețui dincolo de a N-a închidere "
                f"consecutivă în afară (BREAKOUT_ACCEPTANCE termină segmentul la bara N) — dacă K > N, "
                f"fereastra de reintrare K nu ar putea NICIODATĂ expira înainte ca segmentul să fi murit deja "
                f"prin breakout, făcând K structural inaccesibil (LA FEL ca defectul autoprins la 0.3.1: un "
                f"parametru NEUTILIZABIL prin construcție). K<=N e necesar ca AMBELE rezoluții — reintrare "
                f"curată (j<=K) și expirare tardivă fără breakout încă (K<j<=N) — să fie simultan accesibile.")
        if self.K <= 0 or self.N <= 0 or self.w_atr <= 0:
            raise RangeSemanticContractErrorV3("K, N, w_atr trebuie să fie strict pozitive")

    @property
    def s_max(self) -> float:
        """Cuplarea `s_max = 2×w_atr` rămâne (structura ratificată la V2), valoarea urmează `w_atr` NEIDENTIFICAT."""
        return 2.0 * self.w_atr

    @classmethod
    def intraday(cls, *, K: int, N: int, w_atr: float, acknowledge_construction_only: bool = False,
                **kw: Any) -> "RangeConfigV3":
        kw.setdefault("d_min_bars", BARS_PER_INTRADAY_SESSION_M15)
        kw.setdefault("duration_class", "INTRADAY_RANGE")
        return cls(K=K, N=N, w_atr=w_atr, acknowledge_construction_only=acknowledge_construction_only, **kw)

    @classmethod
    def multiday(cls, *, K: int, N: int, w_atr: float, acknowledge_construction_only: bool = False,
                **kw: Any) -> "RangeConfigV3":
        kw.setdefault("d_min_bars", BARS_PER_DAY_M15)
        kw.setdefault("duration_class", "MULTIDAY_RANGE")
        return cls(K=K, N=N, w_atr=w_atr, acknowledge_construction_only=acknowledge_construction_only, **kw)

    def provenance(self) -> dict[str, Any]:
        return {
            "K": self.K, "N": self.N, "w_atr": self.w_atr, "derived_s_max": self.s_max,
            "K_status": RANGE_V3_K_STATUS,
            "N_status": RANGE_V3_N_ACCEPTANCE_STATUS,
            "w_atr_status": RANGE_V3_W_ATR_STATUS,
            "anchor_window_rule": RANGE_V3_ANCHOR_WINDOW_RULE,
            "provenance": RANGE_V3_HBL_PROVENANCE,
            "statistician_spec_commit": RANGE_V3_STATISTICIAN_SPEC_COMMIT,
            "statistician_manifest_commit": RANGE_V3_MANIFEST_COMMIT,
            "statistician_manifest_fingerprint": RANGE_V3_MANIFEST_FINGERPRINT,
        }

    def range_spec_id(self) -> str:
        return _sha(
            f"K={self.K}", f"N={self.N}", f"w_atr={self.w_atr}", f"n_touch={self.n_touch}",
            f"d_min_bars={self.d_min_bars}", f"duration_class={self.duration_class}",
            f"timeframe={self.timeframe}", f"swing_k={self.swing_k}", f"atr_window={self.atr_window}",
            f"range_semantic_contract_version={RANGE_SEMANTIC_CONTRACT_VERSION_V3}",
            f"range_config_schema_version={RANGE_CONFIG_SCHEMA_VERSION_V3}",
            f"producer_version={RANGE_PRODUCER_VERSION_V3}",
        )

    def config_hash(self) -> str:
        return _sha(
            self.range_spec_id(), f"max_duration_bars={self.max_duration_bars}",
            f"segment_history_limit={self.segment_history_limit}",
        )

    def run_hash(self, data_identity: str) -> str:
        return _sha(self.config_hash(), _sha(data_identity), self.range_spec_id())


# ═══════════════════════════════════ rezultat + eveniment ═══════════════════════════════════
@_dc.dataclass(frozen=True, slots=True)
class RangeSemanticResultV3:
    """Contract Ok/Unavailable. Câmpuri de audit conform mandatului §6 — episode/segment ID, ceasuri duale,
    limite, atingeri, pending/confirmed event, sursă/țintă de tranziție, reason codes, `range_spec_id`."""
    available: bool
    reason: str
    range_spec_id: str
    bar_index: int
    ts_close: int
    segment_id: int | None = None
    predecessor_id: int | None = None
    transition_reason: str | None = None
    lifecycle: str | None = None
    structural_start_ts: int | None = None
    confirm_ts: int | None = None
    bars_in_segment: int | None = None
    anchor_lower: float | None = None
    anchor_upper: float | None = None
    range_mid: float | None = None
    w: float | None = None
    touches_upper: int | None = None
    touches_lower: int | None = None
    pending_event: str | None = None
    confirmed_event: str | None = None
    slope: float | None = None
    trend_context: str | None = None
    reason_codes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


@_dc.dataclass(frozen=True, slots=True)
class RangeEventV3:
    kind: str
    confirm_ts: int
    bar_index: int
    segment_id: int | None
    boundary: str | None
    reason_codes: tuple[str, ...]
    not_yet_available: tuple[str, ...]
    event_contract_version: str
    range_spec_id: str
    safety_guard: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return _dc.asdict(self)


@_dc.dataclass(frozen=True, slots=True)
class ConfirmedSegmentRecordV3:
    """Un rând de istoric AUDITABIL pt. un segment ÎNCHEIAT — păstrat mărginit (`segment_history_limit`)."""
    segment_id: int
    predecessor_id: int | None
    end_reason: str
    structural_start_ts: int
    confirm_ts: int | None
    end_ts: int
    bars_in_segment: int
    anchor_lower: float | None
    anchor_upper: float | None
    reached_established: bool


class _Swing:
    __slots__ = ("idx", "price", "is_high", "ts")

    def __init__(self, idx: int, price: float, is_high: bool, ts: int) -> None:
        self.idx = idx; self.price = price; self.is_high = is_high; self.ts = ts


class _RunningMedian:
    """Mediană incrementală (două heap-uri) — O(log m) la inserare, O(1) la citire. Ancora unui segment e
    NEMĂRGINITĂ pe durata vieții segmentului (D1: nicio fereastră fixă externă) — dacă am re-sorta lista
    completă de swing-uri la fiecare bară (`_median` de mai sus), un segment lung ar deveni O(n²) pe durata
    lui de viață. Ordinea de inserare NU afectează valoarea finală a medianei (doar layout-ul intern al
    heap-urilor) — sigur pt. reconstrucție la restore prin reluarea `add()`-urilor din swing-urile salvate."""
    __slots__ = ("_lo", "_hi")

    def __init__(self) -> None:
        self._lo: list[float] = []    # max-heap (valori negate) -- jumătatea inferioară (+ mijlocul, la n impar)
        self._hi: list[float] = []    # min-heap -- jumătatea superioară

    def add(self, x: float) -> None:
        if not self._lo or x <= -self._lo[0]:
            heapq.heappush(self._lo, -x)
        else:
            heapq.heappush(self._hi, x)
        if len(self._lo) > len(self._hi) + 1:
            heapq.heappush(self._hi, -heapq.heappop(self._lo))
        elif len(self._hi) > len(self._lo):
            heapq.heappush(self._lo, -heapq.heappop(self._hi))

    def median(self) -> float:
        if not self._lo:
            raise ValueError("mediană incrementală pe set gol")
        if len(self._lo) > len(self._hi):
            return -self._lo[0]
        return (-self._lo[0] + self._hi[0]) / 2.0

    def __len__(self) -> int:
        return len(self._lo) + len(self._hi)


class _Segment:
    """Starea unui SINGUR segment (candidat sau stabilit) — swing-uri/atingeri/pantă TOATE locale segmentului."""

    def __init__(self, *, segment_id: int, predecessor_id: int | None, transition_reason: str | None,
                config: RangeConfigV3) -> None:
        self.segment_id = segment_id
        self.predecessor_id = predecessor_id
        self.transition_reason = transition_reason
        self._cfg = config
        self.lifecycle = SegmentLifecycleV3.ESTABLISHING
        self.structural_start_idx: int | None = None
        self.structural_start_ts: int | None = None
        self.confirm_ts: int | None = None
        self.was_confirmed = False
        self.establishing_emitted = False     # RANGE_ESTABLISHING e emis O SINGURĂ dată — la prima geometrie
        self.highs: list[_Swing] = []
        self.lows: list[_Swing] = []
        self._high_median = _RunningMedian()  # O(log m) — vezi _RunningMedian; highs/lows rămân pt. audit
        self._low_median = _RunningMedian()
        self.anchor_upper: float | None = None
        self.anchor_lower: float | None = None
        self.touches_upper = 0
        self.touches_lower = 0
        self.closes: deque[float] = deque(maxlen=config.d_min_bars)
        self.n: int = 0                       # bare observate DE ACEST SEGMENT
        # cursă sweep-vs-breakout
        self.pending_side: str | None = None
        self.pending_breach_idx: int | None = None
        self.pending_consec_outside: int = 0
        self.pending_zone_edge: float | None = None
        self.ended = False
        self.end_reason: str | None = None
        self.reached_established = False

    def add_swing(self, sw: _Swing) -> None:
        (self.highs if sw.is_high else self.lows).append(sw)
        (self._high_median if sw.is_high else self._low_median).add(sw.price)
        if self.structural_start_idx is None or sw.idx < self.structural_start_idx:
            self.structural_start_idx = sw.idx
            self.structural_start_ts = sw.ts

    def update_anchors(self) -> None:
        """O(1) — citește medianele incrementale (vezi `_RunningMedian`). NU re-sortează `highs`/`lows` la
        fiecare bară: cu ancora nemărginită pe durata segmentului (D1), un re-sort complet per bară ar fi
        O(n²) pe viața unui segment lung — verificat empiric (0,04ms/bară la 31 swing-uri → 0,62ms/bară la
        525), corectat aici."""
        if len(self._high_median):
            self.anchor_upper = self._high_median.median()
        if len(self._low_median):
            self.anchor_lower = self._low_median.median()

    def geometry_valid(self, w: float) -> bool:
        if self.anchor_upper is None or self.anchor_lower is None:
            return False
        if not (math.isfinite(self.anchor_upper) and math.isfinite(self.anchor_lower)):
            return False
        if self.anchor_upper <= self.anchor_lower:
            return False
        return (self.anchor_upper - self.anchor_lower) > 2.0 * w

    def bars_in_segment(self, current_idx: int) -> int:
        if self.structural_start_idx is None:
            return 0
        return current_idx - self.structural_start_idx + 1

    def slope(self) -> float:
        n = len(self.closes)
        if n < 2:
            return 0.0
        sx = sy = sxy = sxx = 0.0
        for x, y in enumerate(self.closes):
            fx = float(x); sx += fx; sy += y; sxy += fx * y; sxx += fx * fx
        denom = n * sxx - sx * sx
        if denom == 0.0:
            return 0.0
        return (n * sxy - sx * sy) / denom

    # ── snapshot / restore ──
    def snapshot(self) -> dict[str, Any]:
        return {
            "segment_id": self.segment_id, "predecessor_id": self.predecessor_id,
            "transition_reason": self.transition_reason, "lifecycle": self.lifecycle.value,
            "structural_start_idx": self.structural_start_idx, "structural_start_ts": self.structural_start_ts,
            "confirm_ts": self.confirm_ts, "was_confirmed": self.was_confirmed,
            "establishing_emitted": self.establishing_emitted,
            "highs": [[s.idx, s.price, s.is_high, s.ts] for s in self.highs],
            "lows": [[s.idx, s.price, s.is_high, s.ts] for s in self.lows],
            "anchor_upper": self.anchor_upper, "anchor_lower": self.anchor_lower,
            "touches_upper": self.touches_upper, "touches_lower": self.touches_lower,
            "closes": list(self.closes), "n": self.n,
            "pending_side": self.pending_side, "pending_breach_idx": self.pending_breach_idx,
            "pending_consec_outside": self.pending_consec_outside, "pending_zone_edge": self.pending_zone_edge,
            "ended": self.ended, "end_reason": self.end_reason, "reached_established": self.reached_established,
        }

    @classmethod
    def restore(cls, st: dict[str, Any], config: RangeConfigV3) -> "_Segment":
        seg = cls(segment_id=st["segment_id"], predecessor_id=st["predecessor_id"],
                  transition_reason=st["transition_reason"], config=config)
        seg.lifecycle = SegmentLifecycleV3(st["lifecycle"])
        seg.structural_start_idx = st["structural_start_idx"]; seg.structural_start_ts = st["structural_start_ts"]
        seg.confirm_ts = st["confirm_ts"]; seg.was_confirmed = st["was_confirmed"]
        seg.establishing_emitted = st["establishing_emitted"]
        seg.highs = [_Swing(a, b, c, d) for a, b, c, d in st["highs"]]
        seg.lows = [_Swing(a, b, c, d) for a, b, c, d in st["lows"]]
        for s in seg.highs:   # reconstrucție O(m log m), o SINGURĂ dată la restore -- nu per-bară
            seg._high_median.add(s.price)
        for s in seg.lows:
            seg._low_median.add(s.price)
        seg.anchor_upper = st["anchor_upper"]; seg.anchor_lower = st["anchor_lower"]
        seg.touches_upper = st["touches_upper"]; seg.touches_lower = st["touches_lower"]
        seg.closes = deque(st["closes"], maxlen=config.d_min_bars); seg.n = st["n"]
        seg.pending_side = st["pending_side"]; seg.pending_breach_idx = st["pending_breach_idx"]
        seg.pending_consec_outside = st["pending_consec_outside"]; seg.pending_zone_edge = st["pending_zone_edge"]
        seg.ended = st["ended"]; seg.end_reason = st["end_reason"]; seg.reached_established = st["reached_established"]
        return seg


# ═══════════════════════════════════ producătorul incremental V3 ═══════════════════════════════════
class RangeSemanticProducerV3:
    """Producător INCREMENTAL segment-locală. `observe(...)` întoarce `(RangeSemanticResultV3, list[RangeEventV3])`.
    Fiecare bară depinde EXCLUSIV de bare `<= i` (zero lookahead)."""

    def __init__(self, config: RangeConfigV3) -> None:
        self._cfg = config
        self._spec_id = config.range_spec_id()
        self._n = 0
        self._last_atr: float = 0.0
        self._last_close: float | None = None
        self._wh: deque[float] = deque(maxlen=2 * config.swing_k + 1)
        self._wl: deque[float] = deque(maxlen=2 * config.swing_k + 1)
        self._wts: deque[int] = deque(maxlen=2 * config.swing_k + 1)
        self._next_segment_id = 1
        self._active: _Segment | None = None
        self._last_ended_id: int | None = None
        self._last_ended_reason: str | None = None
        self._history: deque[ConfirmedSegmentRecordV3] = deque(maxlen=config.segment_history_limit)

    @property
    def history(self) -> tuple[ConfirmedSegmentRecordV3, ...]:
        return tuple(self._history)

    def _detect_confirmed_swing(self, i: int) -> _Swing | None:
        k = self._cfg.swing_k
        if len(self._wh) < 2 * k + 1:
            return None
        c = k
        ch = self._wh[c]; cl = self._wl[c]; idx = i - k; cts = self._wts[c]
        if all(ch > self._wh[j] for j in range(2 * k + 1) if j != c):
            return _Swing(idx=idx, price=ch, is_high=True, ts=cts)
        if all(cl < self._wl[j] for j in range(2 * k + 1) if j != c):
            return _Swing(idx=idx, price=cl, is_high=False, ts=cts)
        return None

    def _new_segment(self, predecessor_id: int | None, transition_reason: str | None) -> _Segment:
        seg = _Segment(segment_id=self._next_segment_id, predecessor_id=predecessor_id,
                       transition_reason=transition_reason, config=self._cfg)
        self._next_segment_id += 1
        return seg

    def _end_segment(self, seg: _Segment, i: int, end_ts: int, end_reason: str) -> None:
        seg.ended = True; seg.end_reason = end_reason
        self._history.append(ConfirmedSegmentRecordV3(
            segment_id=seg.segment_id, predecessor_id=seg.predecessor_id, end_reason=end_reason,
            structural_start_ts=seg.structural_start_ts or end_ts, confirm_ts=seg.confirm_ts, end_ts=end_ts,
            bars_in_segment=seg.bars_in_segment(i), anchor_lower=seg.anchor_lower,
            anchor_upper=seg.anchor_upper, reached_established=seg.reached_established))
        self._last_ended_id = seg.segment_id
        self._last_ended_reason = end_reason
        self._active = None
        # fereastra de swing-uri e PARTAJATĂ la nivel de producător — golită la fiecare tranziție ca
        # NICIUN swing să nu poată "scurge" dintr-un segment mort în succesorul lui (S1: fără amestec
        # automat de regimuri). Segmentul nou reface fereastra din propriile 2k+1 bare, de la zero.
        self._wh.clear(); self._wl.clear(); self._wts.clear()

    def observe(self, *, ts_close: int, open_: float, high: float, low: float,
                close: float, atr: float | None, trend_context: str | None
               ) -> tuple[RangeSemanticResultV3, list[RangeEventV3]]:
        """`i` (indexul bării) e EXCLUSIV contorul intern al producătorului — nu un parametru al apelantului
        — producătorul e chunk-invariant prin construcție (vede o bară deodată, indiferent cum le grupează
        apelantul; vezi testele de chunk-invariance din mandatul §8)."""
        cfg = self._cfg
        i = self._n
        self._n += 1
        self._wh.append(high); self._wl.append(low); self._wts.append(ts_close)
        self._last_atr = atr if atr is not None else 0.0
        self._last_close = close

        def unavailable(reason: str, *, segment_id: int | None = None, predecessor_id: int | None = None,
                        transition_reason: str | None = None, extra: list[RangeEventV3] | None = None
                       ) -> tuple[RangeSemanticResultV3, list[RangeEventV3]]:
            ev = self._mk_event(SegmentEventKindV3.UNAVAILABLE, ts_close, i, segment_id, None, (reason,), ())
            events_out = (extra or []) + [ev]
            return (RangeSemanticResultV3(available=False, reason=reason, range_spec_id=self._spec_id,
                                          bar_index=i, ts_close=ts_close, segment_id=segment_id,
                                          predecessor_id=predecessor_id, transition_reason=transition_reason,
                                          reason_codes=(reason,)), events_out)

        if atr is None:
            if i < cfg.atr_window or i < 2 * cfg.swing_k + 1:
                return unavailable(ATR_UNAVAILABLE)
            if self._active is not None:
                ended_id = self._active.segment_id
                ended_pred = self._active.predecessor_id
                ended_transition = self._active.transition_reason
                self._end_segment(self._active, i, ts_close, RANGE_FAILED_PRECONDITION)
                failed_ev = self._mk_event(SegmentEventKindV3.RANGE_FAILED, ts_close, i, ended_id, None,
                                           (RANGE_FAILED_PRECONDITION,), ())
                return unavailable(ATR_UNAVAILABLE, segment_id=ended_id, predecessor_id=ended_pred,
                                   transition_reason=ended_transition, extra=[failed_ev])
            return unavailable(ATR_UNAVAILABLE)

        sw = self._detect_confirmed_swing(i)

        # niciun segment activ ⇒ acumulează spre un candidat nou (TRANSITION structural, nu input lipsă)
        if self._active is None:
            self._active = self._new_segment(self._last_ended_id, self._last_ended_reason)
            self._last_ended_id = None; self._last_ended_reason = None
        seg = self._active
        if sw is not None:
            seg.add_swing(sw)
        seg.n += 1
        if cfg.max_duration_bars is not None and seg.structural_start_idx is not None:
            if (i - seg.structural_start_idx + 1) > cfg.max_duration_bars:
                ended_id = seg.segment_id
                self._end_segment(seg, i, ts_close, RANGE_FAILED_PRECONDITION)
                res = RangeSemanticResultV3(available=True, reason=RANGE_FAILED_PRECONDITION,
                                            range_spec_id=self._spec_id,
                                            bar_index=i, ts_close=ts_close, segment_id=ended_id,
                                            predecessor_id=seg.predecessor_id,
                                            transition_reason=seg.transition_reason, trend_context=trend_context,
                                            confirmed_event=SegmentEventKindV3.RANGE_FAILED.value,
                                            reason_codes=(RANGE_FAILED_PRECONDITION,))
                return res, [self._mk_event(SegmentEventKindV3.RANGE_FAILED, ts_close, i, ended_id, None,
                                            (RANGE_FAILED_PRECONDITION,), ())]

        if not seg.highs or not seg.lows:
            res = RangeSemanticResultV3(
                available=True, reason=SegmentEventKindV3.TRANSITION.value, range_spec_id=self._spec_id,
                bar_index=i, ts_close=ts_close,
                segment_id=seg.segment_id, predecessor_id=seg.predecessor_id,
                transition_reason=seg.transition_reason, lifecycle=seg.lifecycle.value,
                structural_start_ts=seg.structural_start_ts, bars_in_segment=seg.bars_in_segment(i),
                trend_context=trend_context, confirmed_event=SegmentEventKindV3.TRANSITION.value,
                reason_codes=(ESTABLISHING_FEW_SWINGS,))
            return res, [self._mk_event(SegmentEventKindV3.TRANSITION, ts_close, i, seg.segment_id, None,
                                        (ESTABLISHING_FEW_SWINGS,), ())]

        seg.update_anchors()
        seg.closes.append(close)
        events: list[RangeEventV3] = []
        assert seg.anchor_upper is not None and seg.anchor_lower is not None
        w = cfg.w_atr * self._last_atr

        if not seg.establishing_emitted:   # o singură dată — prima bară cu geometrie (highs+lows) validă
            seg.establishing_emitted = True
            events.append(self._mk_event(SegmentEventKindV3.RANGE_ESTABLISHING, ts_close, i, seg.segment_id,
                                         None, (ESTABLISHING_FEW_SWINGS,), ()))

        if seg.lifecycle == SegmentLifecycleV3.BREACH_PENDING:
            self._resolve_pending(seg, i, ts_close, high, low, close, events)
        else:
            self._evaluate_active(seg, i, ts_close, high, low, close, w, events)

        confirmed = events[-1].kind if events else None
        pending = (f"BOUNDARY_BREACH_PENDING_{seg.pending_side.upper()}" if seg.pending_side else None)
        slope = seg.slope()
        reasons = self._reasons_for(seg, i, w)
        primary_reason = OK_RANGE if seg.lifecycle == SegmentLifecycleV3.ESTABLISHED else reasons[0]
        result = RangeSemanticResultV3(
            available=True, reason=primary_reason,
            range_spec_id=self._spec_id, bar_index=i, ts_close=ts_close,
            segment_id=seg.segment_id, predecessor_id=seg.predecessor_id, transition_reason=seg.transition_reason,
            lifecycle=seg.lifecycle.value, structural_start_ts=seg.structural_start_ts, confirm_ts=seg.confirm_ts,
            bars_in_segment=seg.bars_in_segment(i), anchor_lower=seg.anchor_lower, anchor_upper=seg.anchor_upper,
            range_mid=(seg.anchor_upper + seg.anchor_lower) / 2.0, w=w,
            touches_upper=seg.touches_upper, touches_lower=seg.touches_lower,
            pending_event=pending, confirmed_event=confirmed, slope=slope, trend_context=trend_context,
            reason_codes=reasons)
        return result, events

    def _reasons_for(self, seg: _Segment, i: int, w: float) -> tuple[str, ...]:
        cfg = self._cfg
        reasons: list[str] = []
        if not seg.geometry_valid(w):
            reasons.append(ZONES_DEGENERATE)
        if seg.touches_upper < cfg.n_touch or seg.touches_lower < cfg.n_touch:
            reasons.append(FEW_TOUCHES)
        if seg.structural_start_idx is not None and seg.bars_in_segment(i) < cfg.d_min_bars:
            reasons.append(TOO_SHORT)
        drift = abs(seg.slope()) * cfg.d_min_bars
        if drift > cfg.s_max * self._last_atr:
            reasons.append(IS_CHANNEL)
        if seg.lifecycle == SegmentLifecycleV3.ESTABLISHED:
            reasons.append(OK_RANGE)
        elif not reasons:
            reasons.append(RANGE_FORMING)
        return tuple(reasons)

    def _touch_zone(self, lo_bar: float, hi_bar: float, anchor: float, w: float) -> bool:
        return hi_bar >= anchor - w and lo_bar <= anchor + w

    def _evaluate_active(self, seg: _Segment, i: int, ts: int, high: float, low: float, close: float,
                         w: float, events: list[RangeEventV3]) -> None:
        cfg = self._cfg
        assert seg.anchor_upper is not None and seg.anchor_lower is not None
        anchor_upper: float = seg.anchor_upper
        anchor_lower: float = seg.anchor_lower

        # CHANNEL_UP / CHANNEL_DOWN — clasificare pe pantă (D1×D4: rădăcina comună era scara ancorei;
        # aici ancora e segment-locală și formula s_max=2×w_atr e reutilizată neschimbată, NU un nou prag
        # inventat). Se evaluează DOAR pt. segmente ne-stabilite încă — un RANGE deja ESTABLISHED e guvernat
        # de mecanismul sweep/breakout, NU reclasificat retroactiv (S2: acceptance ≠ invalidation).
        if seg.lifecycle != SegmentLifecycleV3.ESTABLISHED and seg.bars_in_segment(i) >= cfg.d_min_bars:
            slope = seg.slope()
            drift = abs(slope) * cfg.d_min_bars
            if drift > cfg.s_max * self._last_atr:
                kind = SegmentEventKindV3.CHANNEL_UP if slope > 0 else SegmentEventKindV3.CHANNEL_DOWN
                events.append(self._mk_event(kind, ts, i, seg.segment_id, None, (IS_CHANNEL,), ()))
                self._end_segment(seg, i, ts, IS_CHANNEL)
                return

        upper_edge = anchor_upper + w
        lower_edge = anchor_lower - w
        touched_upper = self._touch_zone(low, high, anchor_upper, w)
        touched_lower = self._touch_zone(low, high, anchor_lower, w)
        if touched_upper:
            seg.touches_upper += 1
        if touched_lower:
            seg.touches_lower += 1

        # breach CAUZAL pe MEȘĂ (high/low) — NU pe close: un wick-sweep dintr-o SINGURĂ bară (depășire +
        # reclaim în ACEEAȘI bară) trebuie să fie reprezentabil (D6, semnătura wick-sweep reutilizată din
        # 0.3.x). Close-ul decide DOAR rezoluția (sweep vs. expirat vs. încă în cursă), în `_resolve_pending`.
        if high > upper_edge or low < lower_edge:
            side = 'upper' if high > upper_edge else 'lower'
            edge = upper_edge if side == 'upper' else lower_edge
            seg.lifecycle = SegmentLifecycleV3.BREACH_PENDING
            seg.pending_side = side; seg.pending_breach_idx = i; seg.pending_zone_edge = edge
            seg.pending_consec_outside = 0     # _resolve_pending îl duce la 1 chiar pe bara asta (breach = bara 1)
            self._resolve_pending(seg, i, ts, high, low, close, events)
            return

        if touched_upper:
            events.append(self._mk_event(SegmentEventKindV3.BOUNDARY_TEST_UPPER, ts, i, seg.segment_id,
                                         'upper', (OK_RANGE,), ()))
        elif touched_lower:
            events.append(self._mk_event(SegmentEventKindV3.BOUNDARY_TEST_LOWER, ts, i, seg.segment_id,
                                         'lower', (OK_RANGE,), ()))
        else:
            events.append(self._mk_event(SegmentEventKindV3.RANGE_MID, ts, i, seg.segment_id, None, (OK_RANGE,), ()))

        self._confirm_establish(seg, i, ts, w, events)

    def _confirm_establish(self, seg: _Segment, i: int, ts: int, w: float, events: list[RangeEventV3]) -> None:
        cfg = self._cfg
        if not seg.geometry_valid(w):
            return
        confirmed_now = seg.touches_upper >= cfg.n_touch and seg.touches_lower >= cfg.n_touch
        if confirmed_now and not seg.was_confirmed:
            seg.was_confirmed = True
            seg.confirm_ts = ts
        if not seg.was_confirmed:
            return
        bars = seg.bars_in_segment(i)
        if bars < cfg.d_min_bars:
            return
        drift = abs(seg.slope()) * cfg.d_min_bars
        if drift > cfg.s_max * self._last_atr:
            return
        if seg.lifecycle != SegmentLifecycleV3.ESTABLISHED:
            seg.lifecycle = SegmentLifecycleV3.ESTABLISHED
            seg.reached_established = True
            events.append(self._mk_event(SegmentEventKindV3.RANGE_ESTABLISHED, ts, i, seg.segment_id, None,
                                         (OK_RANGE,), ()))

    def _resolve_pending(self, seg: _Segment, i: int, ts: int, high: float, low: float, close: float,
                         events: list[RangeEventV3]) -> None:
        """Cursa sweep-vs-breakout. Apelat ATÂT pe bara breach-ului (imediat, din `_evaluate_active` — permite
        un wick-sweep dintr-o SINGURĂ bară) CÂT ȘI pe fiecare bară de continuare (din `observe()`, cât timp
        `lifecycle == BREACH_PENDING`) — `pending_consec_outside` numără bare de la breach ÎNCOACE (breach =
        bara 1) și servește DUAL: prag pt. reintrare curată (`<= K`) ȘI prag pt. breakout (`>= N`). Cele două
        nu pot intra în conflict pe ACEEAȘI bară — `back_inside` e verificat ÎNAINTE de pragul N, deci breakout
        nu poate "fura" o bară care de fapt reintră; iar `K<=N` garantează că reintrarea (dacă apare vreodată)
        e mereu văzută înainte ca segmentul să fi murit deja prin breakout la bara N."""
        cfg = self._cfg
        assert seg.pending_zone_edge is not None and seg.pending_side is not None
        edge = seg.pending_zone_edge
        side = seg.pending_side
        back_inside = (close <= edge) if side == 'upper' else (close >= edge)
        seg.pending_consec_outside += 1
        bars_pending = seg.pending_consec_outside

        if back_inside:
            if bars_pending <= cfg.K:
                kind = (SegmentEventKindV3.LIQUIDITY_SWEEP_UP if side == 'upper'
                       else SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN)
                events.append(self._mk_event(kind, ts, i, seg.segment_id, side, (OK_RANGE,), ()))
            else:
                # reintrare REALĂ, dar prea târzie (>K bare de la breach) ca să conteze sweep curat — segmentul
                # NU moare (N încă neatins, altfel breakout ar fi confirmat deja la o bară <= K <= N anterioară)
                # și NU se declară sweep — revine pur și simplu la evaluare normală.
                events.append(self._mk_event(SegmentEventKindV3.TRANSITION, ts, i, seg.segment_id, side,
                                             (SWEEP_WINDOW_EXPIRED,), ()))
            seg.lifecycle = SegmentLifecycleV3.ESTABLISHED if seg.reached_established else SegmentLifecycleV3.ESTABLISHING
            seg.pending_side = None; seg.pending_breach_idx = None
            seg.pending_consec_outside = 0; seg.pending_zone_edge = None
            return

        if bars_pending >= cfg.N:
            kind = (SegmentEventKindV3.BREAKOUT_ACCEPTANCE_UP if side == 'upper'
                   else SegmentEventKindV3.BREAKOUT_ACCEPTANCE_DOWN)
            events.append(self._mk_event(kind, ts, i, seg.segment_id, side, (TERMINATED_BY_BREAKOUT,), ()))
            self._end_segment(seg, i, ts, TERMINATED_BY_BREAKOUT)
            return
        # încă în cursă — nici reintrare, nici N atins
        events.append(self._mk_event(SegmentEventKindV3.TRANSITION, ts, i, seg.segment_id, side,
                                     (BETWEEN_SEGMENTS,), (NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT,)))

    def _mk_event(self, kind: SegmentEventKindV3, ts: int, i: int, segment_id: int | None, boundary: str | None,
                 reasons: tuple[str, ...], nya: tuple[str, ...]) -> RangeEventV3:
        guard = SAFETY_GUARD_RANGE_MID_NO_ENTRY if kind is SegmentEventKindV3.RANGE_MID else None
        return RangeEventV3(kind=kind.value, confirm_ts=ts, bar_index=i, segment_id=segment_id, boundary=boundary,
                            reason_codes=reasons, not_yet_available=nya,
                            event_contract_version=RANGE_EVENT_CONTRACT_VERSION_V3, range_spec_id=self._spec_id,
                            safety_guard=guard)

    # ── snapshot / restore integral ──
    def snapshot_state(self) -> dict[str, Any]:
        return {
            "n": self._n, "wh": list(self._wh), "wl": list(self._wl), "wts": list(self._wts),
            "last_atr": self._last_atr, "last_close": self._last_close,
            "next_segment_id": self._next_segment_id,
            "active": (self._active.snapshot() if self._active is not None else None),
            "last_ended_id": self._last_ended_id, "last_ended_reason": self._last_ended_reason,
            "history": [
                {"segment_id": r.segment_id, "predecessor_id": r.predecessor_id, "end_reason": r.end_reason,
                 "structural_start_ts": r.structural_start_ts, "confirm_ts": r.confirm_ts, "end_ts": r.end_ts,
                 "bars_in_segment": r.bars_in_segment, "anchor_lower": r.anchor_lower,
                 "anchor_upper": r.anchor_upper, "reached_established": r.reached_established}
                for r in self._history],
        }

    def restore_state(self, st: dict[str, Any]) -> None:
        k = self._cfg.swing_k
        self._n = st["n"]
        self._wh = deque(st["wh"], maxlen=2 * k + 1); self._wl = deque(st["wl"], maxlen=2 * k + 1)
        self._wts = deque(st["wts"], maxlen=2 * k + 1)
        self._last_atr = st["last_atr"]; self._last_close = st["last_close"]
        self._next_segment_id = st["next_segment_id"]
        self._active = _Segment.restore(st["active"], self._cfg) if st["active"] is not None else None
        self._last_ended_id = st["last_ended_id"]; self._last_ended_reason = st["last_ended_reason"]
        self._history = deque(
            (ConfirmedSegmentRecordV3(**r) for r in st["history"]), maxlen=self._cfg.segment_history_limit)
