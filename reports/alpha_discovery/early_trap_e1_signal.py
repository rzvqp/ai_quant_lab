"""EARLY-TRAP-E1 — CANONICAL SIGNAL ARTIFACT (deterministic, fingerprintable).

Mandate: ALPHA-EARLY-TRAP-E1-CANONICAL-FREEZE-001.
Materializes EXACTLY the independently-audited prose rule from:
  - Alpha discovery lineage : commit 6a5d535 (ALPHA_XAUUSD_EARLY_SESSION_LIQUIDITY_TRAP_REPORT.md, rule R2)
  - Statistician audit      : commit de35453 (EARLY_TRAP_E1_SIGNAL_SUPPORTED, 8/8 figures reproduced)

RULE (no reinterpretation, no additions):
  frozen Asia-High sweep parent  ->  E1 = first completed M15 bar after the sweep bar (sweep_index+1)
  FIRE  iff  E1.close < Asia_High  AND  E1.close < E1.open (bearish body).

This module performs NO execution geometry (no entry/SL/TP/RR/M5/partials/BE). The 'reach Asia mid'
computation is the DIAGNOSTIC outcome label used ONLY to reproduce the audited P(mid) statistics; it is
not part of the signal and drives no trade. Price-only, DEV-only. No CALIB / V1 / 2025+ / N4 / exogenous.
"""
import os, sys, json, hashlib, inspect
import numpy as np, pandas as pd
SP = os.path.dirname(os.path.abspath(__file__))
if SP not in sys.path: sys.path.insert(0, SP)
import m5_data as D   # sanctioned firewall loader (gated M5 -> causal M15/H1/H4)

SIGNAL_ID = "EARLY-TRAP-E1"
SIGNAL_VERSION = "1.0.0"
PIP = 0.10

# ============================ FROZEN CONFIGURATION ============================
CONFIG = {
    "signal_id": SIGNAL_ID,
    "signal_version": SIGNAL_VERSION,
    "timeframe": "M15",
    "evidence_scope": "DEV",
    "lineage": {"alpha_discovery_commit": "6a5d535", "statistician_audit_commit": "de35453"},
    "session_definition": {
        "asia_window_utc_hours": [0, 7],                 # 00:00-07:00 UTC (Tokyo 09:00-16:00 JST; Japan NO DST -> fixed UTC)
        "london_local": {"tz": "Europe/London", "hours": [8, 16]},   # DST-correct via tz_convert
        "newyork_local": {"tz": "America/New_York", "hours": [8, 17]},# DST-correct via tz_convert
        "asia_min_bars": 12,
    },
    "parent_definition": {
        "level": "ASIA_HIGH",
        "sweep": "first completed M15 bar with utc_hour>=7 in LONDON or NEW_YORK session and high > asia_high",
        "one_sweep_per_day": True,
        "asia_range": "high/low/mid over 00:00-07:00 UTC M15 bars (>=12), complete at 07:00 UTC before any sweep",
    },
    "rule": {
        "landmark": "E1 = sweep_index + 1 (first completed M15 bar after the sweep bar)",
        "condition_close_below": "E1.close < asia_high      (strict)",
        "condition_bearish_body": "E1.close < E1.open        (strict)",
        "fire": "condition_close_below AND condition_bearish_body",
        "comparisons": "strict less-than; equality (doji / close==asia_high) => NO fire; NaN => fail-closed (NO fire)",
    },
    "causal_timing": {
        "asia_range_complete_before_sweep": True,
        "e1_must_be_completed_bar": True,
        "signal_time": "E1 close_time (epoch seconds)",
        "earliest_execution_time": "strictly AFTER E1 close_time (i.e. >= next M15 open)",
    },
    "diagnostic_outcome": {
        "definition": "reach Asia mid = low <= (asia_high+asia_low)/2 within 24 M15 same-day bars, measured from E1+1",
        "role": "AUDIT REPRODUCTION ONLY — not part of the signal, drives no execution",
    },
    "excluded_known_defect": {
        "prior_attacks": "NOT used by EARLY-TRAP-E1. Statistician found prior_attacks() counts Asia bars that "
                         "define asia_high so it is >=1 by construction; zero impact here. Left explicitly excluded (option A).",
    },
    "expected_reproduction": {"parents": 329, "fires": 118, "unique_days": 118,
                              "disc_fires": 68, "disc_P_mid": 0.794, "conf_fires": 50, "conf_P_mid": 0.840},
}

# ============================ PURE SIGNAL RULE (unit-testable) ============================
def early_trap_e1_fires(e1_open, e1_close, asia_high):
    """Canonical EARLY-TRAP-E1 firing rule. Deterministic, fail-closed on NaN. NO side effects."""
    if not (np.isfinite(e1_open) and np.isfinite(e1_close) and np.isfinite(asia_high)):
        return False                                   # fail-closed
    return bool((e1_close < asia_high) and (e1_close < e1_open))   # strict close-below AND strict bearish body

# ============================ FROZEN PARENT + EVALUATION ============================
def _sessions(dt):
    uh = dt.hour.to_numpy()
    lon = dt.tz_convert("Europe/London").hour.to_numpy()
    ny = dt.tz_convert("America/New_York").hour.to_numpy()
    a = CONFIG["session_definition"]
    asia = (uh >= a["asia_window_utc_hours"][0]) & (uh < a["asia_window_utc_hours"][1])
    london = (lon >= a["london_local"]["hours"][0]) & (lon < a["london_local"]["hours"][1])
    newyork = (ny >= a["newyork_local"]["hours"][0]) & (ny < a["newyork_local"]["hours"][1])
    return uh, asia, london, newyork

def build_parent(tfs):
    """Frozen Asia-High sweep parent population (deterministic). Returns list of parent dicts."""
    M = tfs["M15"]
    h = M["high"].to_numpy(); l = M["low"].to_numpy(); c = M["close"].to_numpy(); o = M["open"].to_numpy()
    atr = M["atr"].to_numpy(); dev = M["is_dev"].to_numpy()
    ct = M["close_time"].to_numpy().astype("int64")
    dt = pd.to_datetime(M["time"].to_numpy(), unit="s", utc=True)
    uday = dt.floor("D").astype("int64").to_numpy()
    uh, asia, london, newyork = _sessions(dt)
    post_asia = uh >= CONFIG["session_definition"]["asia_window_utc_hours"][1]
    minbars = CONFIG["session_definition"]["asia_min_bars"]
    n = len(o); parents = []
    for d in np.unique(uday):
        m = (uday == d) & asia & np.isfinite(atr)
        if m.sum() < minbars: continue
        hi = h[m].max(); lo = l[m].min(); mid = (hi + lo) / 2
        day_idx = np.where((uday == d) & post_asia & np.isfinite(atr))[0]
        sw = None
        for i in day_idx:
            if h[i] > hi and (london[i] or newyork[i]):
                sw = i; break
        if sw is None or not dev[sw]:
            continue
        sess = "OVERLAP" if (london[sw] and newyork[sw]) else ("LONDON" if london[sw] else "NY")
        parents.append(dict(day=int(d), sweep_index=int(sw), sweep_close_time=int(ct[sw]),
                            asia_high=float(hi), asia_low=float(lo), asia_mid=float(mid), session=sess))
    return parents, dict(h=h, l=l, c=c, o=o, atr=atr, ct=ct, uday=uday, n=n, dt=dt)

def _reach_mid_after_E1(P, r, e1):
    """DIAGNOSTIC ONLY: does low reach Asia mid within 24 same-day M15 bars measured from E1+1?"""
    h=P["h"]; l=P["l"]; uday=P["uday"]; n=P["n"]
    for j in range(e1+1, min(e1+1+24, n)):
        if uday[j] != r["day"]: break
        if l[j] <= r["asia_mid"]: return True
    return False

def evaluate(tfs=None):
    """Deterministic evaluation over the frozen DEV parent. Returns (episodes, meta)."""
    if tfs is None: tfs, _ = D.build()
    parents, P = build_parent(tfs)
    o=P["o"]; c=P["c"]; ct=P["ct"]; n=P["n"]
    # chronological DISC/CONF split by parent-day (60/40), fixed as in discovery lineage
    days = sorted(set(r["day"] for r in parents)); cutday = days[int(len(days)*0.6)]
    episodes = []
    for r in parents:
        e1 = r["sweep_index"] + 1
        if e1 >= n:                                    # E1 not a completed bar -> fail-closed
            continue
        fired = early_trap_e1_fires(o[e1], c[e1], r["asia_high"])
        if not fired:
            continue
        split = "DISC" if r["day"] < cutday else "CONF"
        episodes.append(dict(
            signal_id=SIGNAL_ID, signal_version=SIGNAL_VERSION,
            day=r["day"], session=r["session"], split=split,
            sweep_index=r["sweep_index"], e1_index=e1,
            signal_time=int(ct[e1]),                   # knowable at E1 close
            earliest_execution_time=int(ct[e1]) + 1,   # strictly after E1 close
            asia_high=r["asia_high"], asia_low=r["asia_low"], asia_mid=r["asia_mid"],
            e1_open=float(o[e1]), e1_close=float(c[e1]),
            reach_mid_diag=bool(_reach_mid_after_E1(P, r, e1)),
        ))
    meta = dict(n_parents=len(parents), n_fires=len(episodes),
                n_unique_days=len({e["day"] for e in episodes}), cutday=cutday)
    return episodes, meta

# ============================ FINGERPRINTS ============================
def _sha(obj): return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()
def configuration_fingerprint(): return _sha(CONFIG)
def session_definition_identity(): return _sha(CONFIG["session_definition"])
def implementation_fingerprint():
    src = "".join(inspect.getsource(fn) for fn in
                  (early_trap_e1_fires, _sessions, build_parent, _reach_mid_after_E1, evaluate))
    return hashlib.sha256(src.encode()).hexdigest()
def parent_population_identity(parents):
    return _sha(sorted((p["day"], p["sweep_close_time"]) for p in parents))
def episode_set_identity(episodes):
    return _sha(sorted((e["day"], e["signal_time"], e["e1_close"], e["asia_high"]) for e in episodes))

def fingerprints(tfs=None):
    if tfs is None: tfs, _ = D.build()
    parents, _ = build_parent(tfs); episodes, meta = evaluate(tfs)
    return dict(
        signal_id=SIGNAL_ID, signal_version=SIGNAL_VERSION,
        implementation_fingerprint=implementation_fingerprint(),
        configuration_fingerprint=configuration_fingerprint(),
        session_definition_identity=session_definition_identity(),
        parent_population_identity=parent_population_identity(parents),
        episode_set_identity=episode_set_identity(episodes),
    ), episodes, meta

# ============================ REPRODUCTION SELF-CHECK ============================
def reproduction_check(tfs=None):
    fp, episodes, meta = fingerprints(tfs)
    disc = [e for e in episodes if e["split"] == "DISC"]; conf = [e for e in episodes if e["split"] == "CONF"]
    pmid = lambda ee: round(float(np.mean([e["reach_mid_diag"] for e in ee])), 3) if ee else float("nan")
    got = dict(parents=meta["n_parents"], fires=meta["n_fires"], unique_days=meta["n_unique_days"],
               disc_fires=len(disc), disc_P_mid=pmid(disc), conf_fires=len(conf), conf_P_mid=pmid(conf))
    exp = CONFIG["expected_reproduction"]
    ok = (got["parents"]==exp["parents"] and got["fires"]==exp["fires"] and got["unique_days"]==exp["unique_days"]
          and got["disc_fires"]==exp["disc_fires"] and got["conf_fires"]==exp["conf_fires"]
          and got["disc_P_mid"]==exp["disc_P_mid"] and got["conf_P_mid"]==exp["conf_P_mid"])
    return ok, got, exp, fp

if __name__ == "__main__":
    ok, got, exp, fp = reproduction_check()
    print("=== EARLY-TRAP-E1 CANONICAL REPRODUCTION ===")
    print("expected:", exp)
    print("got     :", got)
    print("STATUS  :", "EARLY_TRAP_E1_CANONICAL_REPRODUCTION_PASS" if ok else "EARLY_TRAP_E1_CANONICAL_REPRODUCTION_FAIL")
    print("\n=== FINGERPRINTS ===")
    for k, v in fp.items(): print(f"  {k}: {v}")
    if not ok: sys.exit(1)
