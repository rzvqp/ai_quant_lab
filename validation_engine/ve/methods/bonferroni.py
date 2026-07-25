"""bonferroni@v1 — corecția family-wise (aritmetică deterministă; suita S7).

Funcție PURĂ. Dat `(alpha, familia realizată, p-values per membru eligibil)`, produce
exact ieșirile declarate în registru: `p_adjusted`, `threshold_per_test`,
`family_size`, `realized_family`, `dropped_members`, `m_realized`.

Fără RNG, fără serii sintetice, fără seed, fără `B`. Garanția Bonferroni (FWER ≤ α)
este inegalitatea Boole — o **teoremă**, nu o proprietate empirică; verificarea ei
este aritmetică (`α/m`, `p×m`), nu o baterie de calibrare stocastică. De aceea
`bonferroni@v1` poartă în registru exclusiv suita S7, disjunctă de S1/S3/S4.

Familia realizată provine din `ve.population.eligibility.realized_family`
(contabilitate de populație pe câmpuri pre-rezultat). Acest modul NU o recalculează —
aplică doar pragul `α/m` și `p×m` pe familia deja determinată. Fail-closed peste tot.
"""

from __future__ import annotations

from ..errors import SpecHalt, VEError


def correct(alpha: float, realized: dict, member_pvalues: dict[str, float]) -> dict:
    """Aplică corecția Bonferroni pe o familie realizată.

    - `m = realized["m_realized"]`; membrii eligibili = `realized["eligible_cells"]`.
    - Familie eligibilă vidă (`m == 0`) → oprire **E6 PRECONDITION**
      (`empty_eligible_family_halts`), niciodată corecție tăcută pe familie goală.
    - `threshold_per_test = alpha / m` (uniform — pragul Bonferroni).
    - `p_adjusted[k] = min(1.0, p_k × m)` pentru fiecare membru eligibil (plafonat la 1).
    - Fail-closed: `alpha` în afara (0,1) sau un p-value lipsă pentru un membru eligibil
      → E6 (VE nu inventează o valoare).
    """
    if not (0.0 < float(alpha) < 1.0):
        raise SpecHalt([VEError(
            "E6", "multiple_testing/params/alpha",
            f"alpha={alpha} în afara intervalului (0,1).",
            "alpha: number in (0,1)")])

    m = int(realized["m_realized"])
    eligible = list(realized["eligible_cells"])

    if m == 0:
        raise SpecHalt([VEError(
            "E6", "multiple_testing/member_eligibility",
            "Familie eligibilă vidă (m_realized=0): nicio corecție pe o familie goală.",
            "empty_eligible_family_halts")])

    if len(eligible) != m:
        raise SpecHalt([VEError(
            "E6", "multiple_testing/realized_family",
            f"m_realized={m} dar {len(eligible)} membri eligibili enumerați — incoerent.",
            "m_realized = |eligible_cells|")])

    missing = [k for k in eligible if k not in member_pvalues]
    if missing:
        raise SpecHalt([VEError(
            "E6", "multiple_testing/family_members",
            f"p-value lipsă pentru membri eligibili: {missing}.",
            "fiecare membru al familiei realizate cere un p-value observat")])

    threshold = alpha / m
    p_adjusted = {k: min(1.0, member_pvalues[k] * m) for k in eligible}

    return {
        "m_realized": m,
        "family_size": m,
        "threshold_per_test": threshold,
        "p_adjusted": p_adjusted,
        "realized_family": list(eligible),
        "dropped_members": realized.get("dropped_cells", []),
        "eligibility_rule": realized.get("eligibility_rule"),
    }
