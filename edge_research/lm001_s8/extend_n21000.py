"""LM-001 S8 extension — FPR@0.05 al `block_bootstrap@v1` pe null AR(1) până la n≈21.000.

Mandat 5.4. Extinde bateria S8 EXISTENTĂ (validation_engine/ve/{methods/block_bootstrap.py,
calibration/synthetic_block_bootstrap.py}, copiate AICI NEMODIFICATE ca provenance) cu punctul
n≈21.000 + puncte intermediare pentru curbă. NU o baterie nouă, NU atinge prețuri reale
(distribuții sintetice în memorie), NU .load(), NU backtest.

Spec: manifest v2.5.5 (1d03e4f) `lm_001_preregistration.bootstrap_method`:
  - populație n = 21.048 (combined_population), familie 1, alfa 0,05.
  - B = 10.000 (Mandat 5.4).
  - Bandă de acceptare PRE-ÎNREGISTRATĂ: FPR@0,05 ≤ ~0,055-0,06 (nominal, comparabil cu φ=0,4
    la n=1.000-2.000) → block_bootstrap@v1 utilizabil pentru LM-001. Altfel → WP-5' structural
    (NICIODATĂ matched_null@v1, scop greșit).

Lungimea blocului L = round(n^(1/3)) — rata principială Politis-White pentru medie; reproduce
punctele deja calibrate (n=1.000 → L=10, exact ca în recordul care a picat). NEALES-ca-să-treacă.
"""

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import block_bootstrap as BB               # noqa: E402  (metoda VE, nemodificată)
import synthetic_block_bootstrap as S      # noqa: E402  (harness-ul S8 existent)

ALPHA = 0.05
B = 10000
N_SERIES = 300
NS = [1000, 2000, 5000, 10000, 21048]
PHIS = (0.4, 0.6)


def fpr_ar1(n: int, L: int, phi: float, seed0: int) -> tuple[float, tuple[float, float]]:
    ps = []
    for s in range(N_SERIES):
        rng = np.random.default_rng(seed0 + s)
        r = S.generate_r_series(rng, n, edge=0.0, ar1=phi)     # null autocorelat, edge=0
        ps.append(BB.run(r, block_length=L, B=B, tail="right",
                         centering="zero", seed=seed0 + s + 1_000_000)["p_hat"])
    return S.fpr(ps, ALPHA)


def main() -> int:
    t0 = time.time()
    rows = []
    for phi in PHIS:
        for n in NS:
            L = round(n ** (1.0 / 3.0))
            seed0 = int(phi * 10) * 1_000_000 + n
            f, ci = fpr_ar1(n, L, phi, seed0)
            nominal = ci[0] <= ALPHA <= ci[1] or f <= 0.06
            rows.append({"phi": phi, "n": n, "L": L, "fpr05": f,
                         "ci": [round(ci[0], 4), round(ci[1], 4)],
                         "nominal_<=0.06": f <= 0.06})
            print(f"phi={phi} n={n:6d} L={L:3d}: FPR@0.05={f:.4f} "
                  f"CI=[{ci[0]:.4f},{ci[1]:.4f}]  {'NOMINAL' if f<=0.06 else 'ANTI-CONSERVATOR'}"
                  f"   [{time.time()-t0:.0f}s]", flush=True)

    rec = {"config": {"B": B, "n_series": N_SERIES, "L_rule": "round(n**(1/3))",
                      "alpha": ALPHA, "acceptance_band": "FPR@0.05 <= ~0.055-0.06"},
           "curve": rows}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lm001_s8_extension_results.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2)
    print("\nrecord ->", os.path.relpath(out))
    # verdict pe punctul decisiv n=21048
    dec = {(r["phi"]): r for r in rows if r["n"] == 21048}
    print("\n=== DECISIVE n=21048 ===")
    for phi, r in dec.items():
        print(f"  phi={phi}: FPR@0.05={r['fpr05']:.4f} CI={r['ci']} -> "
              f"{'PASS (nominal)' if r['fpr05'] <= 0.06 else 'FAIL (anti-conservator) -> WP-5'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
