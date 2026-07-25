"""`matched_null@v1` — nul cu potrivire structurală, exact conform protocolului Alpha.

Statistica = media excess-ului pe evenimentele celulei. Nulul: B trageri, fiecare
reeșantionând `len(ex)` valori CU ÎNLOCUIRE din `pool` (excess-ul tuturor barelor
sesiunii), media lor. p (coada stângă) = fracția de medii-nul ≤ media observată.

Un SINGUR generator, seed dat, este consumat între celule ÎN ORDINEA primită.
Ordinea celulelor și consumul generatorului sunt detalii de reproducere ale
implementării istorice (obs0012), nu proprietăți științifice ale metodei — vezi
`F5_REPORT` / decizia CEO.
"""

from __future__ import annotations

import numpy as np


def _cell_p(ex: np.ndarray, pool: np.ndarray, B: int, tail: str, rng) -> tuple[float, float]:
    k = len(ex)
    m = float(ex.mean())
    null = np.array([pool[rng.integers(0, len(pool), k)].mean() for _ in range(B)])
    if tail == "left":
        p = float((null <= m).mean())
    elif tail == "right":
        p = float((null >= m).mean())
    else:
        p = float((np.abs(null - null.mean()) >= abs(m - null.mean())).mean())
    return m, p


def run(cells: list[dict], B: int, tail: str = "left", statistic: str = "mean",
        *, shared_seed: int | None = None, per_cell_seeds: dict | None = None) -> list[dict]:
    """cells: listă de {cell_id, ex, pool}. Două moduri de seeding, exclusive:

    - `shared_seed` (REPRODUCERE istorică, obs0012): UN singur `default_rng(shared_seed)`
      consumat între celule în ordinea `cells`. Rezultatul depinde de ordine — artefact
      de implementare, NU proprietate științifică.
    - `per_cell_seeds` (OFICIAL, principial): fiecare celulă are propriul `default_rng`
      cu sămânța ei; rezultatul este INDEPENDENT DE ORDINE.
    """
    if statistic != "mean":
        raise ValueError(f"statistică neimplementată la F5: {statistic}")
    if tail not in ("left", "right", "two_sided"):
        raise ValueError(f"tail invalid: {tail}")
    if (shared_seed is None) == (per_cell_seeds is None):
        raise ValueError("exact unul dintre shared_seed / per_cell_seeds trebuie dat")

    shared_rng = np.random.default_rng(shared_seed) if shared_seed is not None else None
    out = []
    for c in cells:
        ex = np.asarray(c["ex"], dtype=float)
        pool = np.asarray(c["pool"], dtype=float)
        rng = shared_rng if shared_rng is not None else np.random.default_rng(per_cell_seeds[c["cell_id"]])
        m, p = _cell_p(ex, pool, B, tail, rng)
        se = (p * (1 - p) / B) ** 0.5
        ci = (max(0.0, p - 1.96 * se), min(1.0, p + 1.96 * se))
        seed_used = shared_seed if shared_seed is not None else per_cell_seeds[c["cell_id"]]
        out.append({
            "cell_id": c["cell_id"], "n": len(ex), "observed": round(m, 6),
            "p": p, "B": B, "seed": seed_used, "mc_ci95": [round(ci[0], 6), round(ci[1], 6)],
        })
    return out
