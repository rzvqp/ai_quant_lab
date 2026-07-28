"""block_bootstrap@v1 — moving-block bootstrap al unei serii 1-D.

Statistica = media seriei. Nulul: reeșantionează blocuri CONTIGUE de lungime
`block_length` din seria centrată (media scoasă, când `centering='zero'`),
concatenează până la `n` observații, ia media. Blocurile contigue **păstrează
autocorelația** — exact diferența față de `iid_bootstrap@v1` (bloc de lungime 1).

p (coada dreaptă, testând media > 0) = fracția de medii-nul ≥ media observată.
`p_hat = (k+1)/(B+1)` — `p = 0` nu poate fi produs. Determinist pe `seed`.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _null_means(x_centered: np.ndarray, n: int, L: int, B: int,
                rng: np.random.Generator) -> np.ndarray:
    """B medii-nul, fiecare dintr-o serie reeșantionată din blocuri contigue (vectorizat)."""
    N = len(x_centered)
    n_blocks = int(np.ceil(n / L))
    starts_max = N - L + 1                       # startul unui bloc: [0, N-L]
    starts = rng.integers(0, starts_max, size=(B, n_blocks))
    offs = np.arange(L)
    idx = (starts[:, :, None] + offs[None, None, :]).reshape(B, n_blocks * L)[:, :n]
    return np.asarray(x_centered[idx].mean(axis=1))


def _wilson(k: int, B: int) -> tuple[float, float]:
    if B == 0:
        return (0.0, 1.0)
    z, phat, n = 1.959963984540054, k / B, B
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = (z * ((phat * (1 - phat) / n + z * z / (4 * n * n)) ** 0.5)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def run(series: np.ndarray, block_length: int, B: int, tail: str = "right",
        centering: str = "zero", *, seed: int) -> dict[str, Any]:
    """Rulează block-bootstrap pe `series`. Vezi contractul de ieșiri din registru."""
    if block_length < 1:
        raise ValueError(f"block_length invalid: {block_length}")
    if B < 1000:
        raise ValueError(f"B={B} sub minimul registrului (>=1000)")
    if tail not in ("left", "right", "two_sided"):
        raise ValueError(f"tail invalid: {tail}")
    if centering not in ("zero", "none"):
        raise ValueError(f"centering invalid: {centering}")

    x = np.asarray(series, dtype=float)
    n = len(x)
    if block_length > n:
        raise ValueError(f"block_length={block_length} > n={n}")
    observed = float(x.mean())
    x_c = x - x.mean() if centering == "zero" else x

    rng = np.random.default_rng(seed)
    null = _null_means(x_c, n, block_length, B, rng)

    if tail == "right":
        k = int((null >= observed).sum())
    elif tail == "left":
        k = int((null <= observed).sum())
    else:
        c = float(null.mean())
        k = int((np.abs(null - c) >= abs(observed - c)).sum())

    p_hat = (k + 1) / (B + 1)                     # niciodată 0
    lo, hi = _wilson(k, B)
    return {
        "n": n, "observed": round(observed, 8), "k": k, "B": B,
        "p_hat": p_hat, "p_mc_ci95": [round(lo, 6), round(hi, 6)],
        "mc_resolution": 1.0 / (B + 1), "null_draws_path": None,
        "block_length": block_length, "centering": centering, "tail": tail, "seed": seed,
    }
