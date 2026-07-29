"""SARCINA 1 (Mandat cost-correction) — verificarea populației eligibile a IPOTEZEI NOI (OB/DemandZone/ATR).

Ipoteza nouă (v2.7.8, doc d9b4d12 Partea 4) folosește o PODEA DE ATR, nu filtrul vechi de spike:
  R = 0,7 × ATR;  saturație la 3×cost = R  →  ATR_min = 3×cost/0,7 = 3×0,20/0,7 ≈ 0,857$.
Statisticianul a semnalat că pragul (≈86 „pips" la TICK=0,01) ar putea depăși ATR-ul curent și mai ales
mediana istorică — populația eligibilă ar putea fi ~goală. VERIFIC DIRECT în DOLARI (unitate neambiguă,
evită confuzia de pips 0,01 vs 0,10). NU ajustez filtrul, NU propun altul. Dacă e ~goală → spun și mă opresc.

READ-ONLY, in-sample, M15_v2 130.491 bare, loader v6. atr14 = coloana loader-ului (tr.rolling(14) $, verific.).
GARD 2 neatins, sigilat neatins.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load
import split_manifest as SM

COST = 0.20
R_ATR_MULT = 0.7
ATR_FLOOR = 3.0 * COST / R_ATR_MULT      # ≈ 0,857$
EXPECTED = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


def _stats(a: np.ndarray) -> dict[str, Any]:
    a = a[np.isfinite(a)]
    if not len(a):
        return {}
    return dict(
        n=int(len(a)), min=round(float(a.min()), 3),
        p10=round(float(np.percentile(a, 10)), 3), p25=round(float(np.percentile(a, 25)), 3),
        median=round(float(np.percentile(a, 50)), 3), p75=round(float(np.percentile(a, 75)), 3),
        p90=round(float(np.percentile(a, 90)), 3), max=round(float(a.max()), 3),
        pct_ge_floor=round(100.0 * float((a >= ATR_FLOOR).mean()), 2),
        n_ge_floor=int((a >= ATR_FLOOR).sum()))


def _regime_label(seg: dict[str, Any], i: int) -> str:
    for k in ("regime", "label", "name"):
        v = seg.get(k)
        if isinstance(v, str):
            return v.lower()
    return ["bear", "bull", "correction"][i]


def main() -> int:
    df, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | discovery bars = {len(df)} | ATR_FLOOR = {ATR_FLOOR:.4f}$ "
          f"(= 3×{COST}/{R_ATR_MULT}) = {ATR_FLOOR/0.01:.0f} pips@TICK0.01 = {ATR_FLOOR/0.10:.1f} pips@TICK0.10")
    if len(df) != 130_491:
        print(f"STOP: {len(df)} bare, aștept 130.491."); return 2
    if "atr14" not in df.columns:
        print("STOP: coloana atr14 lipsește din loader."); return 4

    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    t = df["time"].to_numpy()
    print("\n=== atr14 (DOLARI) per regim; fracția ≥ podeaua de 0,857$ ===")
    global_ge = 0; global_n = 0
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = df[(t >= s_ep) & (t < e_ep)].reset_index(drop=True)
        if EXPECTED.get(label) not in (None, len(sub)):
            print(f"STOP: regim {label} {len(sub)} bare."); return 3
        atr = sub["atr14"].to_numpy()
        st = _stats(atr)
        global_ge += st["n_ge_floor"]; global_n += st["n"]
        print(f"\n[{label.upper()}] {st}")
        if "session" in sub.columns:
            for sess in ("asia", "london", "ny", "late"):
                m = sub["session"].to_numpy() == sess
                ss = _stats(atr[m])
                if ss:
                    print(f"   {sess:7s} median={ss['median']}$ p25={ss['p25']} p75={ss['p75']} "
                          f"≥floor={ss['pct_ge_floor']}% (n={ss['n']})")
    frac = 100.0 * global_ge / global_n if global_n else 0.0
    print(f"\n=== GLOBAL: {global_ge}/{global_n} bare cu atr14 ≥ 0,857$ = {frac:.2f}% ===")
    if frac < 1.0:
        print("CONSTATARE: populația eligibilă e ~ZERO la podeaua ATR derivată — ipoteza nouă e "
              "inexecutabilă cu acest filtru pe descoperire. MĂ OPRESC (Statisticianul rezolvă).")
    else:
        print(f"CONSTATARE: populația eligibilă NU e goală ({frac:.1f}% din bare ≥ podea). "
              "Podeaua de 0,857$ e sub mediana ATR — semnalez faptul, NU concluzionez viabilitatea.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
