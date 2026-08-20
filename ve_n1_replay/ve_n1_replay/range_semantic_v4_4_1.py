"""RANGE HIERARCHICAL V4.4.1 -- T-STALE implementation (mandat VE-RANGE-V4_4_1-STALE-IMPLEMENTATION-001).

Converts the frozen T-STALE mechanism (`VE_RANGE_V4_4_1_T_STALE_DESIGN_FREEZE.md`, `e2b65bf`) and the
calibrated parameter registry (`VE_RANGE_V4_4_1_STALE_CALIBRATION_RESULTS.md`, `9116c2b`) into code, without
semantic deviation. Fully additive over `range_semantic_v4_4.py` -- that file is byte-untouched by this work
(`V4_4_BYTE_UNTOUCHED`, verified in the delivery report by `git diff`), and over `range_semantic_v4_3.py`
(also byte-untouched, inherited transitively).

**Architecture, disclosed**: unlike V4.4's own relationship to V4.3 (a fresh, non-subclassing producer,
because V4.4 needed a materially different `_step_macro`/type system for MACRO), V4.4.1 changes only two
orchestration methods (`_offer_swing_everywhere` to record rejected touches, `_step_macro` to add one new
priority-ordered check) plus the snapshot/restore identity boundary -- everything else (`_step_internal`,
`_evaluate_macro_formation`, `observe`, WEAKENING, episode identity, promotion, reversal-watch, ~20 other
methods) needs *zero* behavioral change. Python inheritance is the correct tool for exactly this shape, and
was verified safe here, not assumed: `ConfigV441(ConfigV44)` and `StructureV441(StructureV44)` are TRUE
subclasses (frozen-slotted-dataclass inheritance confirmed clean on this Python version via a standalone
probe -- fields merge correctly, `frozen`/`slots` both hold, no `__dict__` fallback -- before committing to
this shape; the original V4.3-vs-V4.4 config relationship avoided subclassing citing this exact class of risk,
so it was verified rather than re-assumed safe or unsafe here). `RangeSemanticProducerV441
(RangeSemanticProducerV44)` narrows its inherited `self._cfg`/`self._active_macro` attribute types in its own
`__init__` (a standard, mypy-clean subclass-attribute-narrowing idiom, also verified via the same probe before
use) so its own overridden methods can access V4.4.1-only fields, while every inherited, unmodified method
(`observe`, `_evaluate_macro_formation`, `_step_internal`, ...) keeps working correctly against the wider
`ConfigV44`/`StructureV44` interface it was written against -- Liskov substitution, not a trick.

**Two methods needed a full override beyond the two originally scoped, found while re-reading the frozen V4.4
source line-by-line before writing any V4.4.1 code (not assumed from the design doc alone)**: `snapshot_state`/
`restore_state` reference `RANGE_HIERARCHICAL_V4_4_IMPLEMENTATION_FINGERPRINT` and construct
`RangeSemanticProducerV44`/`StructureV44` instances directly by name inside their own bodies (free-variable/
module-global references, not `self.`-based) -- Python's scoping rules mean these would resolve to the V4.4
module's own globals even if inherited unchanged by a subclass, silently embedding the wrong identity and the
wrong structure type on every snapshot. Both are therefore overridden here with V4.4.1-correct references;
recorded as a disclosed implementation finding, not a design-freeze gap (the freeze's own snapshot/versioning
plan, `e2b65bf` §13, already anticipated new identities were needed -- this is the mechanical consequence of
that plan meeting the actual code, not a new requirement).
"""
from __future__ import annotations

import dataclasses as _dc
from collections import deque
from typing import Any, cast

from .range_semantic_v4_3 import (
    BETWEEN_EPISODES,
    BREAKOUT_ACCEPTED,
    ContractErrorV43,
    Depth,
    Excursion,
    NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT,
    OK_RANGE_MACRO,
    RangeEventV43,
    Registry,
    SNAPSHOT_CONTRACT_MISMATCH,
    Structure,
    SWEEP_CONFIRMED,
    SWING_OUTSIDE_CLUSTER,
    ZONES_DEGENERATE,
    ZONES_INVERTED,
    assign_level,
    degeneracy_check,
    offer_swing,
)
from .range_semantic_v4_4 import (
    ConfigV44,
    EPISODE_CONTINUATION,
    EPISODE_MERGED,
    EPISODE_REPLACEMENT,
    RANGE_WEAKENING,
    REASONS_V44,
    RangeSemanticProducerV44,
    StructureV44,
    WEAKENING_PERSISTENCE_TERMINATED,
    WEAKENING_RECOVERED,
    _as_v43_cfg,
    efficiency_ratio,
    relative_net_displacement,
)

__all__ = [
    "RANGE_HIERARCHICAL_V4_4_1_CONTRACT_VERSION",
    "STALE_CANDIDATE_ABANDONED",
    "REASONS_V441",
    "ConfigV441",
    "RANGE_HIERARCHICAL_V4_4_1_NORMATIVE_CONFIG_ID",
    "StructureV441",
    "RangeSemanticProducerV441",
    "RANGE_HIERARCHICAL_V4_4_1_IMPLEMENTATION_FINGERPRINT",
]

# ═══════════════════════════════════ identitate ═══════════════════════════════════

RANGE_HIERARCHICAL_V4_4_1_CONTRACT_VERSION = "range-hierarchical-v4.4.1"

# ── 1 cod de motiv nou, aditiv -- cele 40 din V4.4 raman valide, nerenumerotate (freeze e2b65bf §14) ──
STALE_CANDIDATE_ABANDONED = "STALE_CANDIDATE_ABANDONED"

REASONS_V441: tuple[str, ...] = REASONS_V44 + (STALE_CANDIDATE_ABANDONED,)
assert len(REASONS_V441) == 41, f"40 V4.4 + 1 V4.4.1 = 41 asteptat, avut {len(REASONS_V441)}"
assert len(set(REASONS_V441)) == 41, "coduri de motiv duplicate intre V4.4 si V4.4.1"


# ═══════════════════════════════════ configuratie ═══════════════════════════════════

@_dc.dataclass(frozen=True, slots=True)
class ConfigV441(ConfigV44):
    """Subclaseaza `ConfigV44` (verificat sigur -- vezi docstring-ul modulului) -- cele 26 campuri mostenite
    (9 V4.3 + `contract_version` + 10 V4.4 + `atr_source`/`atr_provenance_wheel_sha256`) raman NESCHIMBATE
    (doar `contract_version` isi schimba valoarea implicita), plus cele 4 campuri T-STALE, toate rezolvate in
    `9116c2b` (registrul normativ final). `config_id()` e MOSTENIT NEMODIFICAT -- `self.__dataclass_fields__`
    pe o instanta `ConfigV441` include deja toate campurile parinte+copil (verificat empiric inainte de a ne
    baza pe asta), deci formula existenta acopera automat setul COMPLET V4.4.1 fara nicio suprascriere."""
    contract_version: str = RANGE_HIERARCHICAL_V4_4_1_CONTRACT_VERSION
    # -- V4.4.1, calibrate in 9116c2b (T-STALE) --
    STALE_WINDOW: int = 29
    STALE_MIN_REJECTIONS: int = 4
    STALE_MIN_ALTERNATION: int = 3
    STALE_MIN_AGE: int = 12

    def validate(self) -> None:
        super().validate()
        if self.STALE_WINDOW < 1:
            raise ContractErrorV43(f"STALE_WINDOW_NON_POSITIVE: {self.STALE_WINDOW}")
        if self.STALE_MIN_REJECTIONS < 1:
            raise ContractErrorV43(f"STALE_MIN_REJECTIONS_NON_POSITIVE: {self.STALE_MIN_REJECTIONS}")
        if self.STALE_MIN_ALTERNATION < 1:
            raise ContractErrorV43(f"STALE_MIN_ALTERNATION_NON_POSITIVE: {self.STALE_MIN_ALTERNATION}")
        if self.STALE_MIN_REJECTIONS < self.STALE_MIN_ALTERNATION + 1:
            # podeaua matematica din calibrare (9116c2b §5.2): K alternante cer STRICT cel putin K+1 elemente
            # -- o valoare mai mica ar face poarta de alternanta IMPOSIBIL de satisfacut, dezactivand T-STALE
            # silentios (niciodata nu ar putea trage), nu doar mai stricta
            raise ContractErrorV43(
                f"STALE_MIN_REJECTIONS_BELOW_ALTERNATION_FLOOR: {self.STALE_MIN_REJECTIONS} < "
                f"{self.STALE_MIN_ALTERNATION} + 1")
        if self.STALE_MIN_AGE < 1:
            raise ContractErrorV43(f"STALE_MIN_AGE_NON_POSITIVE: {self.STALE_MIN_AGE}")


RANGE_HIERARCHICAL_V4_4_1_NORMATIVE_CONFIG_ID = ConfigV441().config_id()


# ═══════════════════════════════════ structura MACRO V4.4.1 -- extensie aditiva peste StructureV44 ═══════════════════════════════════

class StructureV441(StructureV44):
    """Adauga STRICT campul nou de care T-STALE are nevoie: o evidenta marginita a atingerilor RESPINSE
    (freeze `e2b65bf` §4) -- distincta de `_touch_tags` (atingeri ACCEPTATE, alimenteaza semnalul
    `SUPPORTING_ONLY` existent), pastrata separat ca sa nu corupa nici semnalul existent, nici pe cel nou.
    Marginita la `maxlen=64`, exact aceeasi conventie/valoare ca `_touch_tags` in `StructureV44` -- generos
    peste orice fereastra plauzibila de `STALE_WINDOW` bare (rejectiile, ca si acceptarile, sunt limitate de
    ritmul `_detect_confirmed_swings`)."""

    def __init__(self, *, structure_id: int, depth: Depth, parent_structure_id: int | None,
                start_ts: int, trailing_window: int) -> None:
        super().__init__(structure_id=structure_id, depth=depth, parent_structure_id=parent_structure_id,
                         start_ts=start_ts, trailing_window=trailing_window)
        self._rejected_touches: deque[tuple[int, str]] = deque(maxlen=64)

    def record_rejected_touch_v441(self, bar_index: int, is_high: bool) -> None:
        self._rejected_touches.append((bar_index, "H" if is_high else "L"))

    def rejected_touches_in_window(self, as_of_bar: int, window: int) -> list[str]:
        lo = as_of_bar - window
        return [tag for (b, tag) in self._rejected_touches if b > lo]

    def snapshot(self) -> dict[str, Any]:
        base = super().snapshot()
        base["v441_rejected_touches"] = [[b, t] for (b, t) in self._rejected_touches]
        return base

    @classmethod
    def restore(cls, st: dict[str, Any]) -> "StructureV441":
        # `super().restore(st)` dispatcheaza pe `cls` REAL (StructureV441, verificat empiric intr-o proba
        # separata inainte de folosire, nu presupus) -- construieste deja o instanta StructureV441 corecta
        # la RUNTIME; `cast` doar corecteaza tipul STATIC (mypy vede tipul declarat al parintelui,
        # `-> StructureV44`, nu poate deriva singur polimorfismul de tip `cls`) -- acelasi tipar deja folosit
        # de `_as_v43_cfg` (adevar de runtime sigur, indicat explicit lui mypy).
        s = cast(StructureV441, super().restore(st))
        s._rejected_touches = deque((tuple(x) for x in st["v441_rejected_touches"]), maxlen=64)
        return s


# ═══════════════════════════════════ producatorul V4.4.1 -- subclaseaza RangeSemanticProducerV44 ═══════════════════════════════════

class RangeSemanticProducerV441(RangeSemanticProducerV44):
    """Mosteneste NESCHIMBAT: `_detect_confirmed_swings`, `_deepest_open`, `_clear_pending`,
    `_episode_identity_for_new_macro`, `_kill_internal`, `_close_internal_via_breakout`, `_kill_macro`,
    `_close_macro_via_breakout`, `_terminate_macro_weakening_persistence`,
    `_record_macro_termination_for_episode_identity`, `_end_ts_for`, `_check_reversal_watch`,
    `_resolve_role_if_watched`, `_maybe_promote`, `_state_label_internal`, `_channel_or_state_label`,
    `_macro_state_label`, `_step_internal`, `_evaluate_macro_formation`, `observe`, proprietatile
    `macro_history`/`internal_history` -- toate functioneaza corect nemodificate pe o instanta V4.4.1 prin
    dispatch dinamic (`s.snapshot()` in interiorul proprietatilor mostenite apeleaza automat
    `StructureV441.snapshot()` cand `s` e de fapt un `StructureV441`, exact acelasi mecanism deja dovedit
    pentru `Structure`/`StructureV44`).

    Suprascrie EXACT 5 lucruri: `__init__` (ingusteaza tipul static al `self._cfg`/`self._active_macro` pt.
    metodele proprii), `_offer_swing_everywhere` (adauga inregistrarea atingerilor respinse), `_step_macro`
    (adauga verificarea T-STALE, prioritate imediat dupa T-KILL si inainte de T2/T3, exact freeze `e2b65bf`
    §8), `snapshot_state`/`restore_state` (identitate V4.4.1 -- vezi docstring-ul modulului pt. de ce acestea
    nu pot fi mostenite nemodificate)."""

    def __init__(self, config: ConfigV441) -> None:
        super().__init__(config)
        self._cfg: ConfigV441 = config
        self._active_macro: StructureV441 | None = None
        # `_macro_history`/`_awaiting_role` raman la tipurile PARINTELUI (`deque[StructureV44]`,
        # `dict[int, Structure]`) -- containerele mutabile sunt INVARIANTE pt. mypy (verificat empiric: o
        # redeclarare `deque[StructureV441]` aici e o eroare de tip, spre deosebire de `self._cfg`/
        # `self._active_macro`, care sunt simple atribute de clasa, nu containere generice). Niciun cod
        # propriu nu are nevoie de ingustare aici -- `_kill_macro` (mostenit) doar ADAUGA in `_macro_history`
        # (sigur indiferent de tip), iar `.snapshot()` apelat pe elemente dispatch-eaza dinamic corect
        # (`StructureV441.snapshot()`), nu static.

    # ── T-STALE: pragul semantic (freeze e2b65bf §3/§5/§8, registru calibrat 9116c2b) ──
    def _t_stale_should_fire(self, st: StructureV441, i: int) -> bool:
        """Eligibil DOAR daca frontiera exista deja (altfel structural exclus -- nu exista inca ceva fata
        de care sa fie 'stale', freeze §2) si candidatul a depasit varsta minima (poarta, nu declansator).
        Trage doar cand evidenta de respingere din fereastra marginita arata AMBELE: numar minim de
        respingeri SI alternanta minima -- niciuna singura nu e suficienta (mandat §7: 'candidate age
        alone/touch scarcity alone/quiet market alone must NEVER be sufficient'). Reproduce exact logica
        deja testata in harness-ul de calibrare (`9116c2b`), acum peste campurile reale."""
        if st.boundary_upper is None or st.boundary_lower is None:
            return False
        if (i - st.start_ts) < self._cfg.STALE_MIN_AGE:
            return False
        in_window = st.rejected_touches_in_window(i, self._cfg.STALE_WINDOW)
        if len(in_window) < self._cfg.STALE_MIN_REJECTIONS:
            return False
        flips = sum(1 for a, b in zip(in_window, in_window[1:]) if a != b)
        return flips >= self._cfg.STALE_MIN_ALTERNATION

    # ── copie directa a V4.4 + inregistrarea atingerilor respinse (marcat mai jos) -- freeze e2b65bf §4 ──
    def _offer_swing_everywhere(self, i: int, price: float, is_high: bool, events: list[RangeEventV43]) -> None:
        side = "high" if is_high else "low"
        accepted_by_macro = False
        if self._active_macro is not None:
            ok_macro, reason_macro = offer_swing(self._active_macro, price, side, _as_v43_cfg(self._cfg))
            accepted_by_macro = ok_macro
            if ok_macro:
                self._active_macro.record_touch_v44(i, is_high)
            elif reason_macro == SWING_OUTSIDE_CLUSTER:
                # ▼▼▼ SINGURA schimbare semantica fata de V4.4 in aceasta metoda ▼▼▼
                self._active_macro.record_rejected_touch_v441(i, is_high)
                # ▲▲▲ doar respingerile GENUINE de geometrie conteaza -- nu si ATR_UNAVAILABLE (nu e vorba
                # de staleness fata de pret, ci de o stare tranzitorie fara ATR inca) ▲▲▲
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
            # ▼▼▼ singura ALTA schimbare fata de V4.4: StructureV441, nu StructureV44 ▼▼▼
            st_macro = StructureV441(structure_id=new_id, depth=depth, parent_structure_id=parent_id,
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

    # ── copie directa a V4.4 + verificarea T-STALE (marcata mai jos) -- freeze e2b65bf §8 ──
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
            # ▼▼▼ SINGURA insertie noua in aceasta metoda -- T-STALE, prioritate imediat dupa T-KILL,
            # inainte de T2/T3, doar pt. structuri neconfirmate (acelasi `zones is None` care garda T2/T3
            # deja garanteaza asta). Reutilizeaza `_kill_macro` NESCHIMBAT (generic pe `reason: str`) --
            # nicio metoda noua de terminare, aceeasi mecanica/bookkeeping de identitate de episod ca orice
            # alta terminare ▼▼▼
            if self._t_stale_should_fire(st, i):
                self._kill_macro(st, i, STALE_CANDIDATE_ABANDONED, events)
                return STALE_CANDIDATE_ABANDONED
            # ▲▲▲ sfarsit insertie ▲▲▲
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
                excursion_active_this_bar = False
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
            st.weakening_reason = "EXCURSION_PENDING"
            events.append(RangeEventV43(kind=RANGE_WEAKENING, bar_index=i, structure_id=st.structure_id,
                                        depth=Depth.MACRO.name, reason_codes=(RANGE_WEAKENING,),
                                        not_yet_available=()))
            if kind == BREAKOUT_ACCEPTED:
                self._close_macro_via_breakout(st, i, side, events)
                return BREAKOUT_ACCEPTED
            events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=st.structure_id,
                                        depth=Depth.MACRO.name, reason_codes=(), not_yet_available=nya,
                                        boundary=side))
            excursion_reported_reason = NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT

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

    # ── identitate V4.4.1 -- nu pot fi mostenite nemodificate (vezi docstring-ul modulului) ──
    def snapshot_state(self) -> dict[str, Any]:
        base = super().snapshot_state()
        base["contract_version"] = self._cfg.contract_version
        base["config_id"] = self._cfg.config_id()
        base["implementation_fingerprint"] = RANGE_HIERARCHICAL_V4_4_1_IMPLEMENTATION_FINGERPRINT
        return base

    def restore_state(self, st: dict[str, Any]) -> None:
        """Atomic, aceeasi disciplina ca `RangeSemanticProducerV44.restore_state` (constructie intr-o
        instanta SCRATCH separata, `self` neatins pana la swap-ul final) -- reprodusa aici (nu apelata prin
        `super()`) pt. ca parintele construieste explicit `RangeSemanticProducerV44`/`StructureV44` in
        interiorul propriului corp (nu prin `type(self)`), deci un apel `super()` ar reconstrui gresit o
        instanta V4.4, pierzand campurile `v441_*`."""
        if (st.get("contract_version") != self._cfg.contract_version
                or st.get("config_id") != self._cfg.config_id()
                or st.get("implementation_fingerprint") != RANGE_HIERARCHICAL_V4_4_1_IMPLEMENTATION_FINGERPRINT):
            raise ContractErrorV43(SNAPSHOT_CONTRACT_MISMATCH)
        fresh = RangeSemanticProducerV441(self._cfg)
        k = self._cfg.K_struct
        fresh._n = st["n"]
        fresh._wh = deque(st["wh"], maxlen=2 * k + 1)
        fresh._wl = deque(st["wl"], maxlen=2 * k + 1)
        fresh._last_atr = st["last_atr"]
        fresh._registry = Registry.restore(st["registry"])
        fresh._active_macro = StructureV441.restore(st["active_macro"]) if st["active_macro"] else None
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
        fresh._macro_history = deque((StructureV441.restore(s) for s in st["macro_history"]), maxlen=64)
        fresh._internal_history = deque((Structure.restore(s) for s in st["internal_history"]), maxlen=64)
        fresh._awaiting_role = {
            int(k2): (StructureV441.restore(v) if v.get("depth") == Depth.MACRO.value else Structure.restore(v))
            for k2, v in st["awaiting_role"].items()}
        fresh._last_ended_macro_id = st["last_ended_macro_id"]
        fresh._last_ended_internal_id = st["last_ended_internal_id"]
        fresh._last_terminated_macro_zone = (
            tuple(st["last_terminated_macro_zone"]) if st["last_terminated_macro_zone"] else None)
        fresh._last_terminated_macro_end_ts = st["last_terminated_macro_end_ts"]
        fresh._last_terminated_macro_id = st["last_terminated_macro_id"]
        fresh._last_terminated_macro_end_reason = st["last_terminated_macro_end_reason"]
        self.__dict__ = fresh.__dict__


# ═══════════════════════════════════ amprenta de implementare (calculata DUPA scrierea codului) ═══════════════════════════════════
# Placeholder pana la inghetul final -- procedura identica precedentului V4.4 (sha256 peste bytes-ul sursa
# FINALIZAT, eticheta umana descriptiva nu digest-ul brut, exact conventia deja folosita de V4.3 si V4.4).
RANGE_HIERARCHICAL_V4_4_1_IMPLEMENTATION_FINGERPRINT = "v4-4-1-implementation-freeze-2026-08-21"
