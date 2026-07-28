"""Modulul 7 — interactions.py: LOCATOR GENERIC de confluență (MK, Mandat 5.8).

Funcție PURĂ de intersecție matricială — calculator boolean de suprapunere între vectori de condiții
primitive și zone de preț. NU citește prețuri, NU apelează `load()`, NU rulează backtest. mypy --strict.

RULING (Statistician v2.6.1 `2fb948f`, `3c64848`, Problema 5):
  Modulul 7 e un locator GENERIC parametrizabil, NU o ipoteză hardcodată. Primește un SET de condiții
  primitive ca PARAMETRI, verifică co-ocurența la aceeași bară (sau, prin dilatare, într-o fereastră de
  toleranță), și returnează evenimentele calificate — analog `count_bpr`, parametrizat pe toleranță, nu
  hardcodat pe o valoare.

  FĂRĂ logică de trade, FĂRĂ ordine de execuție, FĂRĂ orizonturi, FĂRĂ management de poziție. Acestea ar
  transforma locatorul într-o ipoteză, care ar cere pre-înregistrare completă (populație / orizont / criteriu
  de succes / familie de corecție), neautorizată aici.

  EXEMPLUL din ordinul inițial — „TRUE dacă next-open atinge un OB validat într-un bazin extern activ în
  London sau NY" — a fost RESPINS de Statistician ca fiind o IPOTEZĂ completă (intrare + condiție + fereastră),
  nu o primitivă. NU e codificat aici. Dacă se dorește vreodată testat, trece prin pre-înregistrare separată
  (ca oricare din cele 20 SMC_S*), reutilizând ACEST locator generic ca mecanism de detecție — de exemplu
  `confluence([ob_active, basin_active, session_is_london_or_ny])` — dar combinația rămâne alegerea IPOTEZEI,
  nu comportamentul implicit al modulului.
"""

from __future__ import annotations

from typing import Sequence


def to_mask(indices: Sequence[int], n: int) -> list[bool]:
    """Convertește un set de indici de eveniment într-o mască booleană de lungime `n`. Indici în afara
    [0, n) sunt ignorați (locatorul e agnostic la sursă)."""
    mask = [False] * n
    for i in indices:
        if 0 <= i < n:
            mask[i] = True
    return mask


def dilate(mask: Sequence[bool], before: int, after: int = 0) -> list[bool]:
    """Dilatare morfologică pură: fiecare True se extinde cu `before` bare înapoi și `after` înainte.
    Toleranță parametrizabilă (analog `count_bpr`). Implicit `after=0` = STRICT CAUZAL (fereastră trailing);
    consumatorul alege explicit dacă vrea o fereastră simetrică — locatorul nu impune o convenție."""
    if before < 0 or after < 0:
        raise ValueError("before/after trebuie ≥ 0")
    n = len(mask)
    out = [False] * n
    for i in range(n):
        if mask[i]:
            lo = max(0, i - before)
            hi = min(n - 1, i + after)
            for j in range(lo, hi + 1):
                out[j] = True
    return out


def confluence(masks: Sequence[Sequence[bool]]) -> list[int]:
    """Co-ocurență la ACEEAȘI bară: indicii unde TOATE măștile sunt True (ȘI element-cu-element).
    Confluența într-o fereastră = `confluence([dilate(m, tol) for m in masks])` (compunere, nu convenție
    băgată în locator). Set gol de măști → listă goală (fără co-ocurență de definit)."""
    if not masks:
        return []
    n = len(masks[0])
    for m in masks:
        if len(m) != n:
            raise ValueError("toate măștile trebuie să aibă aceeași lungime")
    return [i for i in range(n) if all(m[i] for m in masks)]


def price_in_zone(price: Sequence[float], lower: float, upper: float) -> list[bool]:
    """Apartenența per-bară a unui vector de preț la o bandă `[lower, upper]` (inclusiv). Intersecție
    booleană preț↔zonă. Ordinea `lower/upper` e normalizată."""
    lo, hi = (lower, upper) if lower <= upper else (upper, lower)
    return [lo <= float(p) <= hi for p in price]


def price_in_any_zone(price: Sequence[float], zones: Sequence[tuple[float, float]]) -> list[bool]:
    """Intersecție matricială preț↔MULTIPLE zone: True la bara i dacă `price[i]` cade în ORICARE zonă.
    Vector de preț × set de zone → mască booleană. Zone goale → tot False."""
    n = len(price)
    out = [False] * n
    for lower, upper in zones:
        member = price_in_zone(price, lower, upper)
        for i in range(n):
            if member[i]:
                out[i] = True
    return out
