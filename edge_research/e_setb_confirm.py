"""Set B out-of-sample CONFIRMATION run for the three Set-B-eligible derived hypotheses (STEP 3).

Frozen operationalization: DERIVED_HYPOTHESIS_REGISTER.md ("Confirmation harness" section, 2026-07-25).
Reuses the EXACT Discovery detectors (imported from the e010/e012/e015 scripts -- not reimplemented) so
methodology is identical to the Set-A Discovery pass; the only differences are (a) data is Set B via
`_setb.load_setb` with a 250-bar Set-A warmup for indicator continuity, and (b) events are filtered by
`_setb.countable_events` to genuine Set B bars (condition 1) with a full forward window (condition 3).

Every result is REGIME-LIMITED (Set B is the same 2022-2026 bull regime). M15 is primary; H1 is
secondary/supporting. BH family = the three M15 primary p-values (rank-1 crit 0.01667).

E028-INV is BURNED (RULE 2B-1) and is NOT run here.
"""
import json
import numpy as np

import _profile as P
from _common import vol_regime
from _setb import load_setb, countable_events
import e010_breaker_block_snatch as M10
import e012_inverted_fvg as M12
import e015_order_block_remitigation as M15

WARMUP = 250
FN_480 = M10.REVISIT_HORIZON + max(P.HORIZONS)   # 530
FN_960 = M15.TRACK_HORIZON + max(P.HORIZONS)     # 1010


def _frame(tf, hyp, prov):
    m, meta = load_setb(tf, hypothesis_id=hyp, provenance_edges=prov, warmup_bars=WARMUP)
    m["vol_regime"] = vol_regime(m)
    m["date"] = m["dt"].dt.date
    return m, meta


def control_with_outcome(m, dists, n_events, horizon, forward_needed, half_width_mult, seed=42):
    """Random-matched-distance control on Set B only, WITH a directional outcome (mirrors the Discovery
    random_matched geometry; adds movement_profile in the zone's random direction). Sampling universe is
    restricted to in_setb bars with a full forward window, so the control is a Set B quantity."""
    rng = np.random.default_rng(seed)
    close = m["close"].values; high = m["high"].values; low = m["low"].values; atr = m["atr14"].values
    in_setb = m["in_setb"].values; n = len(m)
    dists = np.asarray([d for d in dists if np.isfinite(d)])
    if len(dists) == 0:
        return dict(n=0)
    elig = np.where(in_setb & np.isfinite(atr) & (atr > 0))[0]
    elig = elig[(elig > 20) & (elig + 1 + forward_needed <= n)]
    if len(elig) == 0:
        return dict(n=0)
    chosen = rng.choice(elig, size=min(n_events, len(elig)), replace=False)
    sampled = rng.choice(dists, size=len(chosen), replace=True)
    outcomes = []
    for idx, d in zip(chosen, sampled):
        a = atr[idx]; direction = rng.choice([-1, 1])
        zc = close[idx] - direction * d * a
        zl, zh = zc - half_width_mult * a, zc + half_width_mult * a
        end = min(idx + 1 + horizon, n)
        rmask = (low[idx + 1:end] <= zh) & (high[idx + 1:end] >= zl)
        if not rmask.any():
            continue
        rv = idx + 1 + int(np.argmax(rmask))
        mp = P.movement_profile(m, rv, direction, a)
        if mp is not None:
            outcomes.append(mp["outcome"])
    if not outcomes:
        return dict(n=0)
    return dict(n=len(outcomes),
                continuation_rate=float(np.mean([o == "continuation" for o in outcomes])))


def run_e010(tf):
    m, meta = _frame(tf, "E010-D1", ["E010"])
    _, unflipped = M10.detect_obs_and_breakers(m, M10.PRIMARY_DISP)
    kept_idx, report = countable_events(m, [e["confirm_idx"] for e in unflipped], FN_480)
    kept = set(kept_idx)
    unflipped_kept = [e for e in unflipped if e["confirm_idx"] in kept]
    rows = M10.build_rows(m, unflipped_kept)
    real = M10.outcome_summary(rows)
    dists = [r["dist"] for r in rows if r.get("revisited") and r.get("dist") is not None]
    ctrl = control_with_outcome(m, dists, real.get("n_revisited_with_outcome", 0),
                                M10.REVISIT_HORIZON, FN_480, 0.25)
    p = M10.chi2_p(real.get("continuation_rate", 0), real.get("n_revisited_with_outcome", 0),
                   ctrl.get("continuation_rate", 0), ctrl.get("n", 0)) if ctrl.get("n", 0) else None
    return dict(tf=tf, filter_report=report, n_setb_bars=meta["n_setb"], n_warmup=meta["n_warmup"],
                real=real, control=ctrl, real_cont=real.get("continuation_rate"),
                control_cont=ctrl.get("continuation_rate"), p=p)


def run_e012(tf):
    m, meta = _frame(tf, "E012-D1", ["E012"])
    all_fvgs = M12.detect_fvgs(m)
    _, uninverted = M12.find_inversions(m, all_fvgs, M12.PRIMARY_MIN_GAP)
    kept_idx, report = countable_events(m, [e["confirm_idx"] for e in uninverted], FN_480)
    kept = set(kept_idx)
    uninv_kept = [e for e in uninverted if e["confirm_idx"] in kept]
    rows = M12.build_rows(m, uninv_kept)
    real = M12.outcome_summary(rows)
    close = m["close"].values; atr = m["atr14"].values
    dists = [abs((r["zone_low"] + r["zone_high"]) / 2 - close[r["confirm_idx"]]) / atr[r["confirm_idx"]]
             for r in rows if r.get("revisited") and np.isfinite(atr[r["confirm_idx"]]) and atr[r["confirm_idx"]] > 0]
    ctrl = control_with_outcome(m, dists, real.get("n_revisited_with_outcome", 0),
                                M12.REVISIT_HORIZON, FN_480, 0.15)
    p = M12.chi2_p(real.get("continuation_rate", 0), real.get("n_revisited_with_outcome", 0),
                   ctrl.get("continuation_rate", 0), ctrl.get("n", 0)) if ctrl.get("n", 0) else None
    return dict(tf=tf, filter_report=report, n_setb_bars=meta["n_setb"], n_warmup=meta["n_warmup"],
                real=real, control=ctrl, real_cont=real.get("continuation_rate"),
                control_cont=ctrl.get("continuation_rate"), p=p)


def run_e015(tf):
    m, meta = _frame(tf, "E015-V1", ["E015"])
    obs = M15.detect_obs(m, M15.PRIMARY_DISP)
    kept_idx, report = countable_events(m, [o["ob_idx"] for o in obs], FN_960)
    kept = set(kept_idx)
    obs_kept = [o for o in obs if o["ob_idx"] in kept]
    rows = M15.build_visit_rows(m, obs_kept)
    by_visit = M15.summarize_by_visit(rows)
    # secondary/supporting control (unrestricted, as in Discovery) -- NOT part of the primary p
    rng = np.random.default_rng(M15.RNG_SEED)
    rand_rows = M15.random_matched_visits(m, len(obs_kept), M15.TRACK_HORIZON, rng)
    rand_by_visit = M15.summarize_by_visit(rand_rows)
    p = M15.chi2_p(by_visit["1"].get("continuation_rate", 0), by_visit["1"].get("n", 0),
                   by_visit["2"].get("continuation_rate", 0), by_visit["2"].get("n", 0))
    return dict(tf=tf, filter_report=report, n_setb_bars=meta["n_setb"], n_warmup=meta["n_warmup"],
                by_visit=by_visit, random_matched_by_visit=rand_by_visit,
                v1_cont=by_visit["1"].get("continuation_rate"), v2_cont=by_visit["2"].get("continuation_rate"),
                v1_n=by_visit["1"].get("n"), v2_n=by_visit["2"].get("n"), p_v1_vs_v2=p)


def bh(pvals):
    """Benjamini-Hochberg at FDR 0.05 over the provided {name: p} (primary family). Returns per-name
    critical value + pass flag, and the number passing."""
    items = [(k, v) for k, v in pvals.items() if v is not None]
    ranked = sorted(items, key=lambda kv: kv[1])
    mfam = len(pvals)
    out = {}
    passing = set()
    # standard BH: find largest rank i with p_(i) <= (i/m)*0.05; all ranks <= i pass
    max_pass_rank = 0
    for i, (k, v) in enumerate(ranked, start=1):
        crit = 0.05 * i / mfam
        if v <= crit:
            max_pass_rank = i
    for i, (k, v) in enumerate(ranked, start=1):
        crit = 0.05 * i / mfam
        passed = i <= max_pass_rank
        out[k] = dict(rank=i, p=v, bh_crit=crit, passes=passed)
        if passed:
            passing.add(k)
    for k, v in pvals.items():
        if v is None:
            out[k] = dict(rank=None, p=None, bh_crit=None, passes=False)
    return out, sorted(passing)


def main():
    results = {"run": "setB_confirmation_STEP3", "verdict_label": "REGIME-LIMITED",
               "bh_family_size": 3, "bh_rank1_crit": round(0.05 / 3, 5),
               "warmup_bars": WARMUP, "by_hypothesis": {}}

    e010 = {tf: run_e010(tf) for tf in ["M15", "H1"]}
    e012 = {tf: run_e012(tf) for tf in ["M15", "H1"]}
    e015 = {tf: run_e015(tf) for tf in ["M15", "H1"]}
    results["by_hypothesis"] = {"E010-D1": e010, "E012-D1": e012, "E015-V1": e015}

    primary = {"E010-D1": e010["M15"]["p"], "E012-D1": e012["M15"]["p"], "E015-V1": e015["M15"]["p_v1_vs_v2"]}
    bh_out, passing = bh(primary)
    results["primary_pvalues_M15"] = primary
    results["bh"] = bh_out
    results["passing"] = passing

    print("=" * 78)
    print("SET B CONFIRMATION (STEP 3) -- REGIME-LIMITED. BH family=3, rank-1 crit=0.01667")
    print("=" * 78)
    for tf in ["M15", "H1"]:
        r = e010[tf]
        print(f"[E010-D1 {tf}] unflipped cont={r['real_cont']} (n_react={r['real'].get('n_revisited_with_outcome')})"
              f" vs control cont={r['control_cont']} (n={r['control'].get('n')}) p={r['p']} | "
              f"kept={r['filter_report']['kept']} exW={r['filter_report']['excluded_warmup']} "
              f"exE={r['filter_report']['excluded_right_edge']}")
    for tf in ["M15", "H1"]:
        r = e012[tf]
        print(f"[E012-D1 {tf}] uninv cont={r['real_cont']} (n_react={r['real'].get('n_revisited_with_outcome')})"
              f" vs control cont={r['control_cont']} (n={r['control'].get('n')}) p={r['p']} | "
              f"kept={r['filter_report']['kept']} exW={r['filter_report']['excluded_warmup']} "
              f"exE={r['filter_report']['excluded_right_edge']}")
    for tf in ["M15", "H1"]:
        r = e015[tf]
        print(f"[E015-V1 {tf}] v1 cont={r['v1_cont']} (n={r['v1_n']}) v2 cont={r['v2_cont']} (n={r['v2_n']})"
              f" p_v1_v2={r['p_v1_vs_v2']} rand_by_visit_v1={r['random_matched_by_visit'].get('1',{}).get('continuation_rate')}"
              f" rand_v2={r['random_matched_by_visit'].get('2',{}).get('continuation_rate')} | "
              f"kept={r['filter_report']['kept']} exW={r['filter_report']['excluded_warmup']} "
              f"exE={r['filter_report']['excluded_right_edge']}")
    print("-" * 78)
    print("PRIMARY M15 p-values:", primary)
    for k, v in bh_out.items():
        print(f"  {k}: rank={v['rank']} p={v['p']} bh_crit={v['bh_crit']} PASSES={v['passes']}")
    print("PASSING (BH):", passing if passing else "NONE")

    with open("e_setb_confirm_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
