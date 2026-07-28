"""Mandate 4.2 -- E004 fill control run. Executes STATISTICIAN_E004_FILL_CONTROL_SPEC_v1.0.md
(ai_quant_lab statistician-foundation @ b02c5a1), read integrally. NUMBERS + mechanical label only.

Control population (spec §1): same 3-bar imbalance as E004 (E012 def, PRIMARY_MIN_GAP=0.0), WITHOUT the
13:30-15:30 window and WITHOUT the first-of-session clause; ONE instance per trading day, chosen uniformly
at random, seed=7 (K6/DC-0004 convention). Days with no instance contribute nothing. Outcome: binary
`fill` = price re-enters [zone_low, zone_high] within 50 M15 bars of formation -- identical to E004.

Window (spec §2): same 3 M15_v2 discovery regimes (bear/bull/correction, 2011-2021). NOT 2022-2026
(SAME-WINDOW-RESAMPLED). E004 fill is RECALCULATED here on this exact window (not reused from Mandate 4.1),
with the fill horizon confined WITHIN each regime's contiguous bars (no cross-regime-boundary leakage).

Test (spec §3): Fisher exact, one-sided, 2x2 (filled/unfilled x E004/control), H1 p(E004) > p(control),
counts pooled over the 3 regimes. NOT part of the BH-6 family. Label (spec §4): read mechanically from the
pre-registered thresholds -- not chosen. Official loader v6 only; sealed untouched.
"""
import json

import numpy as np
from scipy.stats import fisher_exact

from ._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC

FILL_HORIZON = 50
SEED = 7
REGIMES = [
    ("bear_2011_2015", 1311697800, 1451602800, "-42.0%"),
    ("bull_2015_2020", 1451602800, 1596228300, "+86.3%"),
    ("corr_2020_2022", 1596228300, 1667259900, "-17.4%"),
]
# Pre-registered thresholds (spec §4), fixed before the result:
BAND_LOW = 0.512     # 0.662 - 0.15
BAND_HIGH = 0.886    # 0.736 + 0.15


def detect_fvgs(sub):
    """3-bar imbalance on a contiguous sub-frame. Returns list of (i, mid_i, zlow, zhigh) local indices."""
    hi = sub["high"].values
    lo = sub["low"].values
    out = []
    for i in range(2, len(sub)):
        if lo[i] > hi[i - 2]:
            out.append((i, i - 1, float(hi[i - 2]), float(lo[i])))          # bull
        elif hi[i] < lo[i - 2]:
            out.append((i, i - 1, float(lo[i - 2]), float(hi[i])))          # bear
    return out


def fill_flag(sub, i, zlow, zhigh):
    """price re-enters [zlow, zhigh] within FILL_HORIZON bars AFTER formation bar i, WITHIN this sub-frame."""
    hi = sub["high"].values
    lo = sub["low"].values
    end = min(i + 1 + FILL_HORIZON, len(sub))
    if end <= i + 1:
        return None                                                          # no forward window -> excluded
    return bool(((lo[i + 1:end] <= zhigh) & (hi[i + 1:end] >= zlow)).any())


def main():
    g, meta = load("M15_v2", data_split_id="CONTROL_RUN_E004_FILL", cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    g = g.reset_index(drop=True)

    rng = np.random.default_rng(SEED)          # single seeded RNG, drawn over days in chronological order

    e004 = {}     # regime -> (n, fills)
    ctrl = {}
    per_regime = {}
    for name, s, e, lbl in REGIMES:
        sub = g[(g["time"] >= s) & (g["time"] < e)].reset_index(drop=True)
        hh = sub["dt"].dt.hour.values
        mm = sub["dt"].dt.minute.values
        dates = sub["dt"].dt.date.values
        fvgs = detect_fvgs(sub)                                   # (i, mid, zlow, zhigh)
        by_day = {}
        for (i, mid, zl, zh) in fvgs:
            by_day.setdefault(dates[i], []).append((i, mid, zl, zh))

        # E004 population: first FVG per day whose MIDDLE bar is in 13:30-15:30 UTC
        e_n = e_fill = 0
        for day in sorted(by_day):
            chosen = None
            for (i, mid, zl, zh) in by_day[day]:      # by_day preserves detection (chronological) order
                t = hh[mid] * 60 + mm[mid]
                if 13 * 60 + 30 <= t < 15 * 60 + 30:
                    chosen = (i, zl, zh)
                    break
            if chosen is None:
                continue
            f = fill_flag(sub, chosen[0], chosen[1], chosen[2])
            if f is None:
                continue
            e_n += 1
            e_fill += int(f)
        e004[name] = (e_n, e_fill)

        # Control population: ONE random FVG per day (any hour), seed=7, chronological day order
        c_n = c_fill = 0
        for day in sorted(by_day):
            insts = by_day[day]
            pick = insts[int(rng.integers(0, len(insts)))]        # uniform over the day's instances
            f = fill_flag(sub, pick[0], pick[2], pick[3])
            if f is None:
                continue
            c_n += 1
            c_fill += int(f)
        ctrl[name] = (c_n, c_fill)

        per_regime[name] = dict(label=lbl,
                                e004_n=e_n, e004_fill=e_fill,
                                e004_rate=round(e_fill / e_n, 4) if e_n else None,
                                control_n=c_n, control_fill=c_fill,
                                control_rate=round(c_fill / c_n, 4) if c_n else None)

    # pooled over regimes (spec §3)
    E_n = sum(e004[r][0] for r, *_ in [(k,) for k in e004]); E_fill = sum(e004[r][1] for r in e004)
    C_n = sum(ctrl[r][0] for r in ctrl); C_fill = sum(ctrl[r][1] for r in ctrl)
    E_rate = E_fill / E_n
    C_rate = C_fill / C_n

    # Fisher exact one-sided: H1 p(E004) > p(control)
    table = [[E_fill, E_n - E_fill], [C_fill, C_n - C_fill]]
    odds, p = fisher_exact(table, alternative="greater")

    # Mechanical label (spec §4) -- read from the table, not chosen
    rejects = p < 0.05
    if C_rate <= BAND_LOW and rejects:
        label = "CONFIRMED_STRUCTURAL_ANOMALY"
    elif C_rate >= BAND_HIGH:
        label = "OBSERVED_BELOW_BASELINE"
    else:
        label = "OBSERVED_NOT_DISTINCTIVE"

    out = dict(
        mandate="4.2", run_label="CONTROL_RUN_E004_FILL",
        loader=meta["loader_version"], manifest=meta["manifest_version"],
        window=dict(tf="M15_v2", split="discovery", n_bars=meta["n_bars_delivered"],
                    range=[meta["min_date_used"][:10], meta["max_date_used"][:10]], regimes=3),
        seed=SEED, fill_horizon=FILL_HORIZON,
        per_regime=per_regime,
        pooled=dict(e004_n=E_n, e004_fill=E_fill, e004_rate=round(E_rate, 4),
                    control_n=C_n, control_fill=C_fill, control_rate=round(C_rate, 4)),
        fisher=dict(alternative="greater(H1: p_E004 > p_control)", odds_ratio=round(float(odds), 4),
                    p_one_sided=float(p), rejects_at_0_05=bool(rejects)),
        prereg_thresholds=dict(band_low=BAND_LOW, band_high=BAND_HIGH,
                               rule="control<=0.512 AND Fisher rejects -> ANOMALY; control>=0.886 -> BELOW_BASELINE; else NOT_DISTINCTIVE"),
        label=label,
    )
    with open("mandate42_e004_control_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)

    print("MANDATE 4.2 -- E004 fill control | loader", meta["loader_version"], "| manifest", meta["manifest_version"])
    print(f"window: M15_v2 discovery {out['window']['range']} n={meta['n_bars_delivered']}")
    for name, _s, _e, lbl in REGIMES:
        r = per_regime[name]
        print(f"  {name} ({lbl}): E004 fill {r['e004_rate']} (n={r['e004_n']}) | control {r['control_rate']} (n={r['control_n']})")
    print(f"POOLED: E004 fill = {out['pooled']['e004_rate']} (n={E_n}) | control = {out['pooled']['control_rate']} (n={C_n})")
    print(f"Fisher exact one-sided (H1 E004>control): p = {p:.4g}  rejects@0.05 = {rejects}")
    print(f"Pre-registered band: <=0.512 anomaly / 0.512-0.886 not-distinctive / >=0.886 below-baseline")
    print(f"LABEL (mechanical): {label}")


if __name__ == "__main__":
    main()
