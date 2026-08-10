"""Baterie sintetică de calibrare pentru `block_bootstrap@v1` (suitele S1/S3/S4/S8).

Generează serii-R sintetice cu medie (edge) și autocorelație (AR1) controlabile, le
trece prin ACEEAȘI implementare `ve.methods.block_bootstrap.run`, și măsoară:

  S1  contract de ieșire + reproducibilitate pe seed (p_hat=(k+1)/(B+1), p≠0)
  S3  calibrare sub null: p uniform (KS) + FPR ≈ nominal la edge=0
  S4  putere: curbă monotonă în magnitudinea edge-ului injectat
  S8  autocorelație: pe null AUTOCORELAT, block-boot păstrează acoperirea (FPR≈nominal)
      acolo unde iid (bloc=1) devine anti-conservator — proprietatea specifică metodei
"""

from __future__ import annotations

import numpy as np

from ..methods import block_bootstrap


def generate_r_series(rng, n, edge=0.0, ar1=0.0, tail_df=None, sigma=1.0):
    """Serie-R sintetică: edge + zgomot (opțional Student-t, opțional AR(1)), varianță unitară."""
    if tail_df:
        z = rng.standard_t(tail_df, n) / np.sqrt(tail_df / (tail_df - 2.0))  # varianță 1
    else:
        z = rng.standard_normal(n)
    if ar1:
        out = np.empty(n)
        out[0] = z[0]
        s = np.sqrt(1.0 - ar1 * ar1)
        for t in range(1, n):
            out[t] = ar1 * out[t - 1] + s * z[t]
        z = out
    return edge + sigma * z


def one_p(seed, n=250, edge=0.0, ar1=0.0, L=15, B=2000, tail="right", tail_df=None):
    rng = np.random.default_rng(seed)
    r = generate_r_series(rng, n, edge=edge, ar1=ar1, tail_df=tail_df)
    return block_bootstrap.run(r, block_length=L, B=B, tail=tail,
                               centering="zero", seed=seed + 100000)["p_hat"]


def ks_uniform(ps):
    """Statistica KS a lui `ps` față de U(0,1) + p-value aproximativ (Kolmogorov asimptotic)."""
    x = np.sort(np.asarray(ps, dtype=float))
    n = len(x)
    i = np.arange(1, n + 1)
    d = max(np.max(i / n - x), np.max(x - (i - 1) / n))
    t = (np.sqrt(n) + 0.12 + 0.11 / np.sqrt(n)) * d
    pv = 2 * sum((-1) ** (j - 1) * np.exp(-2 * j * j * t * t) for j in range(1, 101))
    return float(d), float(min(max(pv, 0.0), 1.0))


def wilson(k, n):
    if n == 0:
        return (0.0, 1.0)
    z, phat = 1.959963984540054, k / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = z * ((phat * (1 - phat) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def fpr(ps, alpha=0.05):
    k = int((np.asarray(ps) < alpha).sum())
    n = len(ps)
    return k / n, wilson(k, n)


def run_battery(n_series=300, B=2000, n=250, seed0=0):
    """Rulează S3 (uniformitate/FPR), S4 (putere), S8 (autocorelație). Returnează dict."""
    # S3 — null iid, uniformitate + FPR
    ps_null = [one_p(seed0 + s, n=n, edge=0.0, ar1=0.0, B=B) for s in range(n_series)]
    ks_d, ks_p = ks_uniform(ps_null)
    fpr05, ci05 = fpr(ps_null, 0.05)
    fpr01, ci01 = fpr(ps_null, 0.01)
    fpr10, ci10 = fpr(ps_null, 0.10)

    # S4 — curbă de putere (edge crescător)
    power = {}
    for e in (0.0, 0.1, 0.2, 0.3):
        ps = [one_p(seed0 + 10000 + s, n=n, edge=e, ar1=0.0, B=B) for s in range(n_series)]
        power[e] = fpr(ps, 0.05)[0]  # rata de respingere la 0.05

    # S8 — null AUTOCORELAT (φ=0.4): block-boot (L=15) vs iid (L=1)
    def fpr_ar1(L):
        ps = []
        for s in range(n_series):
            rng = np.random.default_rng(seed0 + 20000 + s)
            r = generate_r_series(rng, n, edge=0.0, ar1=0.4)
            ps.append(block_bootstrap.run(r, block_length=L, B=B, tail="right",
                                          centering="zero", seed=seed0 + 20000 + s + 100000)["p_hat"])
        return fpr(ps, 0.05)
    fpr_block, ci_block = fpr_ar1(15)   # preserves autocorrelation
    fpr_iid, ci_iid = fpr_ar1(1)        # destroys autocorrelation

    return {
        "config": {"n_series": n_series, "B": B, "n": n, "L": 15, "ar1_S8": 0.4},
        "S3": {"ks_d": ks_d, "ks_p": ks_p,
               "fpr01": fpr01, "ci01": list(ci01),
               "fpr05": fpr05, "ci05": list(ci05),
               "fpr10": fpr10, "ci10": list(ci10),
               "mean_p": float(np.mean(ps_null))},
        "S4": {str(k): v for k, v in power.items()},
        "S8": {"fpr_block_L15": fpr_block, "ci_block": list(ci_block),
               "fpr_iid_L1": fpr_iid, "ci_iid": list(ci_iid)},
    }
