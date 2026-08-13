"""Nivelul 2 — bias_h1.py: FACTORII de bias pe H1 (STAT-LEVEL2-BIAS-H1-SPEC-v1.0, `1b2933c`).

NU EMITE PROBABILITATE. Emite FACTORI. Probabilitatea vine de la nivelul 6, condiționată pe ei —
un clasificator determinist nu poate emite o probabilitate prospectivă, iar două estimatoare pe
aceleași date ori sunt redundante, ori unul greșește (spec §1).

CAUZALITATE, mai strictă decât la nivelul 1: factorii la bara `i` citesc EXCLUSIV bare `<= i-1`.
Funcția taie ea însăși seriile la `[0, i)`, deci bara `i` nu poate fi citită — non-lookahead prin
CONSTRUCȚIE, nu prin convenție. Rezultatul e disponibil la bara următoare (spec §7.1).

CONSTANTE, RE-DERIVATE în unități H1 (moștenirea 1; eroarea 460 a demonstrat costul):
    ZI = 23 bare, SĂPTĂMÂNĂ = 115 bare. Măsurat 23,08 / 115,30 pe `H1_from_M15_v2`.
    NIMIC transplantat din M15 (92/460) sau H4 (5,98/29,84).
    `h1_trend_up` NU se folosește: binar, fără magnitudine, fără status (spec §5).

SEMANTICĂ DIRECȚIONALĂ (STAT-SPEC3-N2-DIRECTIONAL-SEMANTICS-v1.0, doc 404b6c8, manifest v2.7.61). Corecția
defectului de ROL: N2 emitea numere brute cu semn (`structure_run_h1 = −7,0`), lăsând N6 să ghicească ce înseamnă
semnul — semantica trăia doar în capul cititorului. ACUM fiecare factor emite `FactorDirection` cu un enum
`Direction ∈ {LONG, SHORT, UNKNOWN}`, sub contract `LevelOutput`. `UNKNOWN` (măsurat, fără direcție) și `Unavailable`
(necalculabil) rămân stări DIFERITE prin TIP — niciodată `0 = unknown`, niciodată `neutral = unavailable`.

CEI PATRU FACTORI (spec §5 + SPEC3 §2) — se calculează EXACT ca înainte; se schimbă DOAR tipul de ieșire:
    structure_run_h1  run cu semn (detect_breaks). >0→LONG, <0→SHORT, ==0→UNKNOWN. Semn INTRINSEC. MULȚIMEA NECESARĂ.
    displacement_h1   expansion cu direcția corpului. +1→LONG, −1→SHORT, 0,0→UNKNOWN (0,0 e REZULTAT → Ok, nu absență).
    liquidity_above   bazine ABOVE NECONSUMATE sub pragul k×ATR14. >0→SHORT prin POLARITATE DECLARATĂ (§3, o TEZĂ,
                      nu o măsurătoare: `assumption=True`, `assumption_id=LIQ-ABOVE-POLARITY-v1`, în schema_hash),
                      ==0→UNKNOWN; contor negativ→Unavailable. Marcajul nu rezolvă asumpția — o face ATACABILĂ.
    momentum          ABSENT_NO_RATIFIED_PRIMITIVE → `Unavailable`, PERMANENT, ÎN AFARA mulțimii necesare — altfel
                      N2 n-ar fi disponibil niciodată (fail-mort). NU zero, NU „neutru" (spec §6).

SATURAȚIA, măsurată de Statistician înainte de propunere: 474 bazine ABOVE deasupra prețului la
bara mediană, max 2.916, doar 5,1% dintre bare fără vreunul la 1×ATR ⇒ „există lichiditate
deasupra" e adevărat pe 94,9% din bare, NEFALSIFICABIL prin saturație. Remediul din spec §3, aplicat
aici VERBATIM: (1) doar bazine neconsumate (`detect_sweeps`, D7); (2) filtru de PRAG pe distanță,
nu de rang — un rang nu poate returna mulțimea vidă, deci nu poate reface falsificabilitatea.
`K_ATR = 1.0` e valoarea de laborator deja ratificată la v2.7.41, REUTILIZATĂ, nu aleasă aici.
Fracția rezultată se MĂSOARĂ și se raportează (`zero_eligible_fraction`); nu se ajustează `k` ca să
treacă criteriul — asta ar fi tuning, iar VE nu are discreție.

REDUNDANȚĂ: atașată MECANIC prin inspecție statică a apelurilor (`redundancy_by_static_inspection`),
nu dintr-o listă întreținută de mână (spec §7.4). Zero dintre cei patru factori sunt complet
independenți de primitivele pe care candidații declanșează; singura axă genuin independentă din
sistem rămâne ȘTIRILE (spec §4).
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence

import numpy as np

from level_output import LevelOutput, Ok, Unavailable
from liquidity_mechanics import LiquidityPool, PoolSide, PoolTier, build_pools, detect_sweeps
from market_state import atr14, expansion
from market_structure import Block, BreakKind, detect_breaks, detect_swings, label_structure

# ── constante, în unități H1 (măsurate, nu transplantate) ────────────────────────────────────
DAY_H1: int = 23           # media empirică măsurată 23,08 bare
WEEK_H1: int = 115         # media empirică măsurată 115,30 bare
K_SWING_DEFAULT: int = 2   # k pentru detect_swings — default de laborator, identic nivelului 1
K_ATR: float = 1.0         # prag de distanță în ATR14; valoarea ratificată la v2.7.41, reutilizată
N_MIN_BARS: int = WEEK_H1  # sub o săptămână completă de bare închise, factorii nu se emit

SCHEMA_VERSION: str = "STAT-LEVEL2-BIAS-H1-SPEC-v1.0"

# primitivele ratificate din care derivă fiecare factor — folosite ȘI ca vocabular pentru
# inspecția statică; declarate aici, dar VERIFICATE contra sursei reale de test.
_RATIFIED_MODULES: tuple[str, ...] = ("market_structure", "market_state", "liquidity_mechanics")


class Status(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class Direction(Enum):
    """Direcția utilizabilă de N6 — enum, NU un număr cu semn. Semantica trăiește în TIP, nu în capul cititorului."""
    LONG = "long"
    SHORT = "short"
    UNKNOWN = "unknown"        # MĂSURAT fără direcție (run nul / nicio expansiune) — distinct de Unavailable


ASSUMPTION_LIQ_ABOVE: str = "LIQ-ABOVE-POLARITY-v1"   # polaritatea lui liquidity_above: TEZĂ, nu măsurătoare (§3)


@dataclass(frozen=True)
class FactorDirection:
    """Ce emite N2 per factor (SPEC3 §4). `direction` e DIRECȚIA (nu un număr brut); `raw` e valoarea sub contract,
    pentru AUDIT, nu pentru decizie. `assumption=True` DOAR pentru liquidity_above (polaritate declarată, §3)."""
    name: str
    direction: Direction
    raw: LevelOutput[float]                  # valoarea, sub contract — audit, nu decizie
    primitive: str
    assumption: bool                         # True doar pentru liquidity_above
    assumption_id: str | None = None         # LIQ-ABOVE-POLARITY-v1 când assumption; intră în schema_hash


@dataclass(frozen=True)
class BiasState:
    """Payload-ul din `Ok`. FĂRĂ `status` (constructorul Ok/Unavailable e sursa de adevăr). NU emite procent/scor/
    agregare — aceea e a lui N6. Mulțimea necesară a lui N2 = {structure_run_h1}; displacement și liquidity sunt
    opționale; momentum e OBLIGATORIU în afara ei (permanent Unavailable), altfel N2 e permanent indisponibil."""
    factors: tuple[LevelOutput[FactorDirection], ...]   # ordonat: structure, displacement, liquidity, momentum
    direction_share_long: float | None      # DESCRIPTIV pe [i-WEEK_H1, i-1]; `share`, NU o previziune
    direction_share_short: float | None
    as_of_index: int                        # bara pentru care e valabil; citește doar `<= as_of_index-1`
    n_closed_bars: int                      # câte bare ÎNCHISE au fost citite
    zero_eligible_fraction: float | None    # criteriul de falsificabilitate (§7.2), raportat nu ajustat


def _direction_from_sign(x: float) -> Direction:
    """Semnul → direcție. INTRINSEC primitivei pentru structură/displacement; 0 = UNKNOWN MĂSURAT (nu absență)."""
    return Direction.LONG if x > 0.0 else Direction.SHORT if x < 0.0 else Direction.UNKNOWN


def _run_series(close: Sequence[float], high: Sequence[float], low: Sequence[float], k: int) -> list[int]:
    """`run` cu semn, propagat bară cu bară din fluxul `detect_breaks` ratificat. Identic nivelului 1:
    CHoCH răstoarnă (reset la ±1); BOS de același semn incrementează; BOS opus resetează la ±1."""
    n = len(close)
    if n == 0:
        return []
    blocks = [Block(0, n)]
    breaks = sorted(detect_breaks(close, label_structure(detect_swings(high, low, blocks)), blocks),
                    key=lambda b: b.idx)
    out = [0] * n
    run = 0
    bi = 0
    for i in range(n):
        while bi < len(breaks) and breaks[bi].idx == i:
            kind = breaks[bi].kind
            if kind is BreakKind.BOS_BULL:
                run = run + 1 if run > 0 else 1
            elif kind is BreakKind.BOS_BEAR:
                run = run - 1 if run < 0 else -1
            elif kind is BreakKind.CHOCH_BULL:
                run = 1 if run <= 0 else run
            elif kind is BreakKind.CHOCH_BEAR:
                run = -1 if run >= 0 else run
            bi += 1
        out[i] = run
    return out


def _unswept_above_pools(
    high: Sequence[float], low: Sequence[float], close: Sequence[float], k: int,
) -> list[LiquidityPool]:
    """Bazinele ABOVE care NU au fost măturate în fereastra citită. D7: un bazin măturat e consumat și
    nu mai e lichiditate în repaus (spec §3). Cauzal: se citesc doar barele date."""
    n = len(close)
    blocks = [Block(0, n)]
    swings = label_structure(detect_swings(high, low, blocks))
    pools = [p for p in build_pools(swings, PoolTier.INTERNAL) if p.side is PoolSide.ABOVE]
    swept = {(ev.pool.price, ev.pool.formed_idx) for ev in detect_sweeps(high, low, close, pools, blocks)}
    return [p for p in pools if (p.price, p.formed_idx) not in swept]


def _eligible_above(
    pools: Sequence[LiquidityPool], ref_price: float, atr_ref: float, upto_idx: int, k_atr: float,
) -> int:
    """Bazine ABOVE neconsumate, încă deasupra prețului, în interiorul pragului `k_atr × ATR`.
    PRAG, nu rang — un rang returnează întotdeauna N, deci nu poate produce mulțimea vidă (v2.7.41)."""
    if not np.isfinite(atr_ref) or atr_ref <= 0.0:
        return -1
    band = k_atr * atr_ref
    return sum(1 for p in pools
               if p.available_idx <= upto_idx and p.price > ref_price and (p.price - ref_price) <= band)


def compute_bias(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    i: int, *, regime_axes_status: Sequence[str] | None = None,
    k: int = K_SWING_DEFAULT, k_atr: float = K_ATR,
) -> LevelOutput[BiasState]:
    """Factorii de bias VALABILI LA BARA `i`, calculați EXCLUSIV din bare `<= i-1`. Ieșirea sub CONTRACT:
    `Ok(BiasState)` când mulțimea necesară {structure_run_h1} e disponibilă; `Unavailable` la cascadă/fereastră.

    Seriile se taie intern la `[0, i)`, deci bara `i` nu poate fi citită nici accidental — non-lookahead
    prin construcție. PURĂ: fără I/O, fără stare globală, fără date reale.

    `regime_axes_status`: statusurile axelor `RegimeState` de la nivelul 1. Dacă TOATE sunt UNAVAILABLE,
    regimul e indisponibil și ieșirea devine `Unavailable` prin cascadă (spec §6). O axă indisponibilă
    izolată se EXCLUDE din cheie, nu invalidează starea.
    """
    n_avail = max(0, min(i, len(close)))

    if regime_axes_status is not None and len(regime_axes_status) > 0:
        if all(s == Status.UNAVAILABLE.value for s in regime_axes_status):
            return Unavailable(reason="cascade_regime_all_axes_unavailable", as_of=i)   # cascadă de la nivelul 1

    if n_avail < N_MIN_BARS:
        return Unavailable(reason="incomplete_window", as_of=i)   # fereastră incompletă → fail-closed

    o = list(open_[:n_avail])
    h = list(high[:n_avail])
    lo = list(low[:n_avail])
    c = list(close[:n_avail])
    last = n_avail - 1                                            # ultima bară ÎNCHISĂ

    def _raw(x: float) -> Ok[float]:
        return Ok(value=x, as_of=last, valid_until=last + 1, schema_hash=_SCHEMA_HASH)

    def _ok_factor(fd: FactorDirection) -> Ok[FactorDirection]:
        return Ok(value=fd, as_of=i, valid_until=i + 1, schema_hash=_SCHEMA_HASH)

    # ── factor 1: structura (mulțimea necesară) — semnul e INTRINSEC ──
    runs = _run_series(c, h, lo, k)
    run_last = runs[last]
    f_struct: LevelOutput[FactorDirection] = _ok_factor(FactorDirection(
        "structure_run_h1", _direction_from_sign(float(run_last)), _raw(float(run_last)),
        "market_structure.detect_breaks", assumption=False))

    # ── factor 2: displacement — semn INTRINSEC; 0,0 e REZULTAT → Ok(UNKNOWN), NU Unavailable (Z4-L1) ──
    exp_series = expansion(o, h, lo, c)
    disp = (1.0 if c[last] > o[last] else -1.0) if exp_series[last] else 0.0
    f_disp: LevelOutput[FactorDirection] = _ok_factor(FactorDirection(
        "displacement_h1", _direction_from_sign(disp), _raw(disp), "market_state.expansion", assumption=False))

    # ── factor 3: lichiditate deasupra (neconsumată, sub prag) — polaritate SHORT prin ASUMPȚIE DECLARATĂ (§3) ──
    atr = atr14(h, lo, c)
    pools = _unswept_above_pools(h, lo, c, k)
    n_elig = _eligible_above(pools, c[last], atr[last], last, k_atr)
    f_liq: LevelOutput[FactorDirection]
    if n_elig < 0:                                                # contor negativ → n-am-putut-măsura
        f_liq = Unavailable(reason="liquidity_above_negative_counter", as_of=last)
    else:
        liq_dir = Direction.SHORT if n_elig > 0 else Direction.UNKNOWN   # ⚠ SHORT = TEZĂ, nu măsurătoare
        f_liq = _ok_factor(FactorDirection(
            "liquidity_above", liq_dir, _raw(float(n_elig)), "liquidity_mechanics.build_pools",
            assumption=True, assumption_id=ASSUMPTION_LIQ_ABOVE))

    # falsificabilitate: fracția barelor din fereastra citită cu ZERO bazine eligibile (§7.2)
    zero_hits = 0
    counted = 0
    for j in range(N_MIN_BARS - 1, n_avail):
        cnt = _eligible_above(pools, c[j], atr[j], j, k_atr)
        if cnt >= 0:
            counted += 1
            if cnt == 0:
                zero_hits += 1
    zero_frac = (zero_hits / counted) if counted > 0 else None

    # ── factor 4: momentum — ABSENT, PERMANENT Unavailable, ÎN AFARA mulțimii necesare (altfel N2 = fail-mort) ──
    f_mom: LevelOutput[FactorDirection] = Unavailable(reason="ABSENT_NO_RATIFIED_PRIMITIVE", as_of=i)

    # ── share-uri DESCRIPTIVE pe fereastra de o săptămână H1 (NU o previziune) ──
    window = runs[last - WEEK_H1 + 1:last + 1]
    long_share = float(np.mean([1.0 if r > 0 else 0.0 for r in window]))
    short_share = float(np.mean([1.0 if r < 0 else 0.0 for r in window]))

    state = BiasState(
        factors=(f_struct, f_disp, f_liq, f_mom),
        direction_share_long=long_share, direction_share_short=short_share,
        as_of_index=i, n_closed_bars=n_avail, zero_eligible_fraction=zero_frac,
    )
    return Ok(value=state, as_of=i, valid_until=i + 1, schema_hash=_SCHEMA_HASH)


# ── redundanță prin INSPECȚIE STATICĂ (spec §7.4) ────────────────────────────────────────────

def _called_primitives(source: str, func_prefixes: tuple[str, ...]) -> dict[str, set[str]]:
    """Numele apelate în fiecare funcție de nivel superior al cărei nume începe cu un prefix dat.
    Pur sintactic: nu importă, nu execută, nu presupune. Așa se atașează avertismentul MECANIC."""
    tree = ast.parse(source)
    out: dict[str, set[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith(func_prefixes):
            continue
        names: set[str] = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                fn = sub.func
                if isinstance(fn, ast.Name):
                    names.add(fn.id)
                elif isinstance(fn, ast.Attribute):
                    names.add(fn.attr)
        out[node.name] = names
    return out


def ratified_vocabulary() -> frozenset[str]:
    """Numele publice exportate de modulele RATIFICATE, obținute prin introspecție.

    Fără această restricție, inspecția statică ar raporta drept „primitivă partajată" orice
    `float`/`len`/`max` — un avertisment de redundanță adevărat dar vid, care ar dilua exact
    semnalul pe care §7.4 îl cere. Vocabularul se derivă din module, nu se enumeră de mână, deci
    rămâne corect când modulele se schimbă.
    """
    import importlib
    import inspect

    vocab: set[str] = set()
    for mod_name in _RATIFIED_MODULES:
        mod = importlib.import_module(mod_name)
        for name in dir(mod):
            if name.startswith("_"):
                continue
            obj = getattr(mod, name, None)
            # FUNCȚII, nu clase: `Block`, `PoolSide`, `BreakKind` sunt STRUCTURI DE DATE. A le
            # trata drept primitive ar declara redundanți toți candidații care folosesc blocuri,
            # adică toți — un avertisment adevărat și vid. Distincția e mecanică, nu o listă.
            if inspect.isfunction(obj) and getattr(obj, "__module__", "") == mod_name:
                vocab.add(name)
    return frozenset(vocab)


def _module_level_primitives(source: str, vocabulary: frozenset[str]) -> set[str]:
    """Primitive ratificate apelate ORIUNDE în modul, inclusiv în afara generatoarelor.

    Necesar pentru că un generator poate PRIMI rezultatul unei primitive ca parametru — cazul real
    `gen_cand0002`, care primește `exp` calculat de runner. Inspecția intra-funcție nu vede muchia;
    inspecția la nivel de modul o vede. Se raportează SEPARAT, ca să nu se confunde cu apelul direct.
    """
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                names.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                names.add(fn.attr)
    return names & vocabulary


def redundancy_by_static_inspection(
    factor_module_path: str, candidate_module_path: str, vocabulary: frozenset[str] | None = None,
) -> dict[str, tuple[str, ...]]:
    """Mapează fiecare primitivă ratificată folosită aici la candidații al căror DECLANȘATOR o apelează.

    Ambele muchii sunt derivate din sursă, nu dintr-o listă: factor→primitivă prin inspecția acestui
    modul, primitivă→candidat prin inspecția generatoarelor `gen_cand*`. Rezultatul rămâne corect pe
    măsură ce se adaugă candidați, ceea ce o listă întreținută de mână nu ar face (spec §7.4).

    Se păstrează DOAR numele din vocabularul ratificat (`ratified_vocabulary`); restul sunt funcții
    de bibliotecă standard, nu primitive, și nu constituie redundanță.
    """
    vocab = ratified_vocabulary() if vocabulary is None else vocabulary
    with open(factor_module_path, "r", encoding="utf-8") as fh:
        here = _called_primitives(fh.read(), ("compute_bias", "_run_series", "_unswept_above_pools"))
    with open(candidate_module_path, "r", encoding="utf-8") as fh:
        cand_src = fh.read()
    cands = _called_primitives(cand_src, ("gen_cand",))
    module_level = _module_level_primitives(cand_src, vocab)

    mine: set[str] = set()
    for names in here.values():
        mine |= names
    mine &= vocab

    out: dict[str, tuple[str, ...]] = {}
    for prim in sorted(mine):
        direct = sorted(cn for cn, names in cands.items() if prim in names)
        if direct:
            out[prim] = tuple(direct)
        elif prim in module_level:
            # INJECTAT: primitiva e apelată în modul și PASATĂ generatorului ca parametru
            # (ex. `expansion` calculat de runner și dat lui gen_cand0002). Inspecția
            # intra-funcție e OARBĂ la asta; se marchează explicit, nu se pierde.
            out[prim] = ("MODULE_LEVEL_INJECTED:all_gen_cand_receiving_it",)
    return out


# NOTĂ (SPEC3 §4): `FactorDirection` NU are câmp `redundant_with` — tipul de ieșire e exact cel din §4. Dezvăluirea
# §7.4 rămâne DISPONIBILĂ mecanic prin `redundancy_by_static_inspection` (sursă, nu listă), ca interogare de sine
# stătătoare; nu se mai ștampilează per instanță de factor. Fostul `attach_redundancy` s-a eliminat (nu mai are câmp).


def schema_payload(k: int = K_SWING_DEFAULT, k_atr: float = K_ATR) -> dict[str, Any]:
    """Corpul care intră în `schema_hash`, pre-înregistrat ÎNAINTE de prima decizie (moștenirea 2).
    Lista ORDONATĂ a factorilor, primitiva fiecăruia, pragurile, ferestrele și versiunea."""
    return {
        "schema_version": SCHEMA_VERSION,
        "level": 2,
        "timeframe": "H1_from_M15_v2",
        "factors_ordered": [
            {"name": "structure_run_h1", "primitive": "market_structure.detect_breaks", "params": {"k": k}},
            {"name": "displacement_h1", "primitive": "market_state.expansion", "params": {}},
            {"name": "liquidity_above", "primitive": "liquidity_mechanics.build_pools",
             "params": {"k_atr": k_atr, "unswept_only": True, "filter": "threshold_not_rank",
                        "polarity": "SHORT", "assumption": True, "assumption_id": ASSUMPTION_LIQ_ABOVE}},
            {"name": "momentum", "primitive": "ABSENT_NO_RATIFIED_PRIMITIVE", "params": {},
             "in_required_set": False},
        ],
        "required_set": ["structure_run_h1"],
        "directional_semantics": {"enum": ["long", "short", "unknown"], "zero_is": "unknown_measured"},
        "windows_h1_units": {"day": DAY_H1, "week": WEEK_H1, "n_min_bars": N_MIN_BARS},
        "emits_probability": False,
        "ratified_modules": list(_RATIFIED_MODULES),
    }


# schema_hash pre-înregistrat: include polaritatea DECLARATĂ a lui liquidity_above (assumption=True) — o face
# ATACABILĂ (Red Team țintește eticheta), nu o rezolvă. Lazy la nivel de modul; folosit de `compute_bias`.
_SCHEMA_HASH: str = hashlib.sha256(
    json.dumps(schema_payload(), sort_keys=True).encode("utf-8")).hexdigest()[:16]


def default_paths() -> tuple[str, str]:
    """Căile folosite de inspecția statică, relative la acest fișier. Fără cale absolută hardcodată."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "bias_h1.py"), os.path.join(here, "phase1_screening.py")
