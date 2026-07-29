"""OBDZ-001 — RULAREA pe descoperire (PASUL 2). Prima ipoteză compusă. Read-only, in-sample, M15_v2.

Loader oficial v6 (discovery-safe). Bias context-derivat (H1_from_M15_v2/H4_from_M15_v2, ema20>ema50,
forward-safe). Mașina de stare ÎNGHEȚATĂ `obdz001` + `partial_exit`. Test WP-5' block_bootstrap@v1 (L>=28,
H0: mean(net_R)<=0) — oracolul e VALIDAT pentru H=20, exact orizontul aici. GARD 2 neatins, sigilat intact.
Descoperirea e in-sample: un rezultat pozitiv e CANDIDAT, nu confirmare (regula SMC_S1). NU interpretez.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research"), os.path.join(_ROOT, "edge_research", "lm001_s8")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load
import split_manifest as SM  # type: ignore[import-not-found]
import block_bootstrap as BB  # type: ignore[import-not-found]
from obdz001 import HORIZON, SL_MULT, detect_obdz001_signals, evaluate_obdz001

L, BOOT, SEED = 28, 2000, 20260729
EXPECTED = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


def _htf_trend(dfh: Any, period: int) -> Any:
    ema20 = dfh["close"].ewm(span=20).mean(); ema50 = dfh["close"].ewm(span=50).mean()
    tu = (ema20 > ema50).astype(float)
    avail = dfh["time"].shift(-1)
    avail.iloc[-1] = int(dfh["time"].iloc[-1]) + period
    return pd.DataFrame({"avail": avail.astype("int64"), "trend_up": tu.to_numpy()})


def _day_index(time: Any) -> np.ndarray:
    dt = pd.to_datetime(time, unit="s", utc=True)
    ny = dt.dt.tz_convert("America/New_York").dt.tz_localize(None)
    days = (ny - pd.Timedelta(hours=17)).dt.floor("D").values.astype("datetime64[D]").astype("int64")
    return np.asarray(days, dtype=np.int64)


def _dist(a: np.ndarray) -> dict[str, Any]:
    a = a[np.isfinite(a)]
    if not len(a):
        return {}
    return dict(n=int(len(a)), min=round(float(a.min()), 2), p25=round(float(np.percentile(a, 25)), 2),
                median=round(float(np.percentile(a, 50)), 2), p75=round(float(np.percentile(a, 75)), 2),
                max=round(float(a.max()), 2), mean=round(float(a.mean()), 2))


def _regime_label(seg: dict[str, Any], i: int) -> str:
    for k in ("regime", "label", "name"):
        v = seg.get(k)
        if isinstance(v, str):
            return v.lower()
    return ["bear", "bull", "correction"][i]


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh1, _ = load("H1_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh4, _ = load("H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)} H1={len(dfh1)} H4={len(dfh4)} | L={L} B={BOOT}")
    if len(dfm) != 130_491:
        print(f"STOP: M15 {len(dfm)} bare."); return 2
    dfm = dfm.sort_values("time").reset_index(drop=True)
    for name, dfh, per in (("h1", dfh1, 3600), ("h4", dfh4, 4 * 3600)):
        htf = _htf_trend(dfh, per).sort_values("avail")
        dfm = pd.merge_asof(dfm, htf.rename(columns={"trend_up": name}), left_on="time", right_on="avail",
                            direction="backward").drop(columns="avail")
    dfm["day"] = _day_index(dfm["time"])
    t_all = dfm["time"].to_numpy()

    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    out: dict[str, Any] = {"L": L, "B": BOOT, "regimes": {}}
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()
        sess = sub["session"].tolist() if "session" in sub.columns else [""] * n

        signals = detect_obdz001_signals(o, h, l, c, atr.tolist(), h1.tolist(), h4.tolist(), day.tolist(), n)
        signals = sorted(signals, key=lambda s: s.entry_idx)     # ordine de timp pentru structura de suprapunere

        net_r: list[float] = []; net_d: list[float] = []; rds: list[float] = []
        reasons: dict[str, int] = {}
        plasa = eod_ct = 0
        realized: list[int] = []; sessions: list[str] = []
        for s in signals:
            res = evaluate_obdz001(s, h, l, c)
            r_dollars = SL_MULT * s.atr                          # R în dolari = 0,7×ATR
            net_r.append(res.net_R); net_d.append(res.net_R * r_dollars); rds.append(r_dollars)
            reasons[res.exit_reason] = reasons.get(res.exit_reason, 0) + 1
            if res.exit_reason in ("timeout_no_tp1", "tp1_then_timeout"):
                if s.entry_idx + HORIZON <= s.eod_idx:
                    plasa += 1
                else:
                    eod_ct += 1
            realized.append(res.leg2_exit_idx - s.entry_idx)
            sessions.append(str(sess[s.entry_idx]))

        nt = len(net_r)
        rec: dict[str, Any] = {"n_trades": nt}
        if nt:
            nr = np.asarray(net_r); nd = np.asarray(net_d)
            sumR = float(nr.sum()); srt = np.sort(nr)[::-1]
            reach_tp1 = reasons.get("tp1_then_tp2", 0) + reasons.get("tp1_then_breakeven", 0) + reasons.get("tp1_then_timeout", 0)
            bb = BB.run(nr, block_length=L, B=BOOT, tail="right", centering="zero", seed=SEED) if nt > L else {}
            rec.update(
                reach_TP1=reach_tp1, reach_TP2=reasons.get("tp1_then_tp2", 0),
                breakeven_after_TP1=reasons.get("tp1_then_breakeven", 0),
                stopped_full=reasons.get("stopped_full", 0), timeout_plasa=plasa, timeout_EOD=eod_ct,
                winrate=round(float((nr > 0).mean()), 4), R_mediu_dollars=round(float(np.mean(rds)), 4),
                expectancy_R=round(float(nr.mean()), 5), expectancy_dollars=round(float(nd.mean()), 5),
                net_sumR=round(sumR, 3), net_sum_dollars=round(float(nd.sum()), 3),
                best_over_sumR=round(float(srt[0]) / sumR, 4) if sumR else None,
                top3_over_sumR=round(float(srt[:3].sum()) / sumR, 4) if sumR else None,
                top5_over_sumR=round(float(srt[:5].sum()) / sumR, 4) if sumR else None,
                wo1_netR=round(sumR - float(srt[0]), 3),
                p_wp5=bb.get("p_hat"), p_ci95=bb.get("p_mc_ci95"),
                realized_horizon=_dist(np.asarray(realized, dtype=float)),
                horizon_buckets={"lt10": int(sum(1 for x in realized if x < 10)),
                                 "ge10": int(sum(1 for x in realized if x >= 10))},
                by_session={s: int(sessions.count(s)) for s in ("asia", "london", "ny", "late")})
        out["regimes"][label] = rec
        print(f"\n=== {label.upper()} ({n} bare) ===")
        if not nt:
            print("  (fără tranzacții)"); continue
        print(f"  n={nt} | TP1={rec['reach_TP1']} TP2={rec['reach_TP2']} BE={rec['breakeven_after_TP1']} "
              f"SL={rec['stopped_full']} plasa={rec['timeout_plasa']} EOD={rec['timeout_EOD']}")
        print(f"  WR={rec['winrate']} Rmed=${rec['R_mediu_dollars']:.2f} E_R={rec['expectancy_R']:+.4f} "
              f"E_$={rec['expectancy_dollars']:+.4f} netR={rec['net_sumR']:+.2f} net$={rec['net_sum_dollars']:+.2f}")
        print(f"  best/sumR={rec['best_over_sumR']} top3={rec['top3_over_sumR']} top5={rec['top5_over_sumR']} "
              f"wo1R={rec['wo1_netR']:+.2f}")
        print(f"  p_WP5={rec['p_wp5']} CI95={rec['p_ci95']} | orizont realizat {rec['realized_horizon']} "
              f"buckets {rec['horizon_buckets']} | sesiuni {rec['by_session']}")

    path = os.path.join(_ROOT, "reports", "obdz001_run_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/obdz001_run_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
