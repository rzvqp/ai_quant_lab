"""
CEO_ASSISTED_SYNTHETIC_CONSTRUCTION_ONLY
CIRCULAR_LABEL_DERIVED_BARS
ZERO_VALIDATION_WEIGHT

Sintetizator generic: spans normalizate (v. parse_windows.py) -> bare OHLC continue.

Nu reprezinta bare reale. E o constructie MECANICA, UNIFORMA (aceleasi reguli simple pt. toate
cele 48 de ferestre, fara ajustare per-fereastra) menita sa exercite prototipul pe FORMA
structurala documentata (secventa RANGE/CHANNEL/breakout etc.), nu pe preturi reale -- de aceea
rezultatul acestei componente NU e si nu poate fi un BLIND PASS.

Foloseste EXACT tehnica de interpolare pe leg-uri validata in suita de teste unitare
(`legs_bars` din tests/test_range_semantic_v4_3.py) -- NU o sinusoida (o sinusoida esantionata la
bare intregi produce varfuri cu high IDENTIC pe doua bare consecutive -- vezi bara de varf +
bara imediat urmatoare, al carei open mosteneste exact inchiderea de varf -- ceea ce invalideaza
comparatia stricta de fractal K_struct=2 si suprima swing-urile la fiecare varf/vale)."""
from __future__ import annotations

import math

Bar = tuple[int, float, float, float, float]
Span = dict[str, object]

UNIT = 5.0            # jumatate-amplitudine tipica RANGE/CHANNEL (unitati de ATR sintetic=1.0)
LEG_BARS = 4          # bare per leg -- un ciclu complet (sus+jos) = 8 bare, ca in fixture-urile unitare
CHANNEL_DRIFT_FRAC = 0.8
NESTED_UNIT_FRAC = 0.35   # amplitudinea spans-urilor L2/INTERNAL, ca fractiune din UNIT-ul L1/MACRO
ENVELOPE_UNIT_FRAC = 1.6  # amplitudinea plicului L1/MACRO cand spans-urile interioare sunt L2/INTERNAL


def _envelope_offset(k: int, env_start: int, env_end: int) -> float:
    """Un singur ciclu (o urcare + o coborare) pe toata durata plicului -- swing sus/jos unic,
    fara ambiguitate, suficient pt. ca un candidat MACRO la scara plicului sa aiba sansa sa se
    confirme in jurul structurilor L2/INTERNAL imbracate in el."""
    span = max(env_end - env_start, 1)
    t = (k - env_start) / span
    return UNIT * ENVELOPE_UNIT_FRAC * math.sin(2 * math.pi * t)


def _legs_to_bars(legs: list[tuple[float, int]], start_idx: int) -> tuple[list[Bar], float]:
    """legs: [(target_price, n_bars), ...], primul element fiind ancora (n_bars ignorat).
    Interpolare identica cu `legs_bars` din suita de teste (validata acolo pe zeci de cazuri)."""
    bars: list[Bar] = []
    i = start_idx
    prev = legs[0][0]
    for target, n in legs[1:]:
        n = max(n, 1)
        for step in range(1, n + 1):
            frac = step / n
            c = prev + (target - prev) * frac
            o = c - (target - prev) / n * 0.4
            h = max(o, c) + 0.3
            lo = min(o, c) - 0.3
            bars.append((i, o, h, lo, c)); i += 1
        prev = target
    return bars, prev


def _fit_to_n(bars: list[Bar], start_idx: int, n: int) -> list[Bar]:
    """Garanteaza EXACT n bare, indexate start_idx..start_idx+n-1 -- plasa de siguranta pt. cazuri
    de leg-uri foarte scurte unde numarul de bare generate difera usor de `n`."""
    if not bars:
        bars = [(start_idx, 100.0, 100.2, 99.8, 100.0)]
    if len(bars) > n:
        bars = bars[-n:]
    elif len(bars) < n:
        bars = bars + [bars[-1]] * (n - len(bars))
    return [(start_idx + k, o, h, lo, c) for k, (_, o, h, lo, c) in enumerate(bars)]


def _regime_bars(start_idx: int, n: int, level: float, cls: str,
                 lower: object = None, upper: object = None, mid: object = None,
                 amp_scale: float = 1.0) -> tuple[list[Bar], float]:
    if lower is not None and upper is not None:
        try:
            lo_p = float(str(lower).split(chr(8211))[0].split("-")[0])
            hi_p = float(str(upper).split(chr(8211))[0].split("-")[0])
            level = (lo_p + hi_p) / 2.0
            amp = max((hi_p - lo_p) / 2.0, 1.5)
        except ValueError:
            amp = UNIT * amp_scale
    else:
        amp = UNIT * amp_scale
    drift_total = 0.0
    if cls == "CHANNEL_UP":
        drift_total = amp * CHANNEL_DRIFT_FRAC
    elif cls == "CHANNEL_DOWN":
        drift_total = -amp * CHANNEL_DRIFT_FRAC
    num_legs = min(max(2, round(n / LEG_BARS)), n)   # niciodata mai multe leg-uri decat bare disponibile
    bars_per_leg = [n // num_legs] * num_legs
    for k in range(n - sum(bars_per_leg)):
        bars_per_leg[k % num_legs] += 1
    legs: list[tuple[float, int]] = [(level, 0)]
    up_turn = True
    for k in range(num_legs):
        drift_here = drift_total * ((k + 1) / num_legs)
        target = level + drift_here + (amp if up_turn else -amp)
        legs.append((target, bars_per_leg[k]))
        up_turn = not up_turn
    bars, end_level = _legs_to_bars(legs, start_idx)
    return _fit_to_n(bars, start_idx, n), end_level


def _bridge_bars(start_idx: int, n: int, level: float, event: str | None) -> tuple[list[Bar], float]:
    event = event or ""
    direction = 1 if "UP" in event else (-1 if "DOWN" in event else 1)
    sustained = event.startswith("BREAKOUT")
    if sustained:
        legs = [(level, 0), (level + direction * UNIT * 2.2, n)]
        bars, end_level = _legs_to_bars(legs, start_idx)
    else:
        n1 = max(n // 2, 1)
        n2 = max(n - n1, 1)
        legs = [(level, 0), (level + direction * UNIT * 1.3, n1), (level, n2)]
        bars, _ = _legs_to_bars(legs, start_idx)
        end_level = level
    return _fit_to_n(bars, start_idx, n), end_level


def synthesize_window(window_bars: int, spans: list[Span], seed_level: float = 100.0,
                      macro_envelope: tuple[int, int] | None = None) -> list[Bar]:
    """Cand `macro_envelope`=(env_start,env_end) e dat (schema B -- spans-urile primite sunt deja
    la scara L2/INTERNAL, imbracate intr-un singur L1/MACRO care le contine pe toate), spans-urile
    din interiorul plicului se genereaza la amplitudine REDUSA (NESTED_UNIT_FRAC) si primesc apoi,
    intr-o a doua trecere, deriva lenta a plicului adaugata peste -- un candidat MACRO la scara
    plicului are sansa sa se formeze/confirme in jurul structurilor L2/INTERNAL imbracate in el,
    exact modelul ierarhic al mandatului V4.3 (§5: INTERNAL trebuie sa aiba parinte MACRO)."""
    bars: list[Bar] = []
    level = seed_level
    cursor = 0
    for span in spans:
        span_start = int(span["start"])   # type: ignore[arg-type]
        span_end = int(span["end"])       # type: ignore[arg-type]
        nested = macro_envelope is not None and macro_envelope[0] <= span_start < macro_envelope[1]
        if span_start > cursor:
            gap = span_start - cursor
            for k in range(gap):
                bars.append((cursor + k, level, level + 0.2, level - 0.2, level))
            cursor = span_start
        # limitele span-urilor umane sunt aproximative (v. "Limitele sunt aproximative" in notele
        # etichetarii) -- vecini adiacenti se pot suprapune cu 1-2 bare; portiunea deja acoperita
        # de span-ul anterior se sare, span-ul curent incepe de la `cursor`, nu de la propriul start.
        eff_start = max(span_start, cursor)
        n = span_end - eff_start
        if n <= 0:
            cursor = max(cursor, span_end)
            continue
        seg_bars: list[Bar]
        if span["kind"] == "bridge":
            seg_bars, level = _bridge_bars(eff_start, n, level, span.get("event"))  # type: ignore[arg-type]
        else:
            amp_scale = NESTED_UNIT_FRAC if nested else 1.0
            seg_bars, level = _regime_bars(eff_start, n, level, str(span["class"]),
                                           span.get("lower"), span.get("upper"), span.get("mid"),
                                           amp_scale=amp_scale)
        bars.extend(seg_bars)
        cursor = span_end
    while cursor < window_bars:
        bars.append((cursor, level, level + 0.2, level - 0.2, level))
        cursor += 1
    bars.sort(key=lambda b: b[0])
    if macro_envelope is not None:
        env_start, env_end = macro_envelope
        bars = [
            (idx, o + _envelope_offset(idx, env_start, env_end), h + _envelope_offset(idx, env_start, env_end),
             lo + _envelope_offset(idx, env_start, env_end), c + _envelope_offset(idx, env_start, env_end))
            if env_start <= idx < env_end else (idx, o, h, lo, c)
            for idx, o, h, lo, c in bars
        ]
    return bars
