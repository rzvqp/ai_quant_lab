"""THREE-REGIME PERSISTENCE RUN (Mandate 1.1, M15_v2 discovery). Runs the 428 ATR hypotheses on each
of the 3 regime discovery blocks IN ISOLATION (per-block data dir -> no cross-block/sealed lookback),
canonical D2-closed engine (mark_invalid/target_first at default). Descriptive only: per-regime
exp/win/pf/dd/n + NET concentration (best/sumR, top3, top5, wo1). NO t1/t3/t5, NO FDR, NO selection.
Central output: persistence leaderboard (profitable in 3/2/1/0 regimes).

Orchestrator: slices each block's M15_v2 + derived HTF into a temp dir (mstrat's expected filenames),
runs a worker subprocess per block with AI_QUANT_DATA_DIR=block, aggregates. Worker mode: --worker.
"""
import os, sys, json, subprocess
import numpy as np, pandas as pd

CLONE = r"C:\Users\MEDION GAMING\aql_stat_clone"
AA    = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
DM    = os.path.join(AA, "data", "market")
MAN   = os.path.join(AA, "config", "split_manifest.json")
OUT   = os.path.join(CLONE, "results", "reproduction_d2")
BLOCKROOT = os.path.join(OUT, "_regime_blocks")
ENUM  = json.load(open(os.path.join(OUT, "..", "matched_null_validation", "subset_prereg_enumeration.json")))
ATR_IDS = sorted(set(ENUM["atr_subset_ids"]))          # 428
ATR_VALID = set(ENUM["atr_subset_valid_ids"])          # 412 eligible (n>=25 full-sample); the other 16 flagged
CTX = {"H4": "OANDA_XAUUSD_H4_from_M15_v2.csv", "H1": "OANDA_XAUUSD_H1_from_M15_v2.csv",
       "D1": "OANDA_XAUUSD_D1_from_M15_v2.csv"}

def metrics(R):
    n = len(R)
    if n == 0: return dict(n=0)
    R = np.asarray(R, float); srt = np.sort(R)[::-1]; sumR = float(R.sum())
    eq = np.cumsum(R); dd = float(np.max(np.maximum.accumulate(eq) - eq))
    gp = R[R > 0].sum(); gl = -R[R < 0].sum()
    return dict(n=n, exp=float(R.mean()), win=float((R > 0).mean()),
                pf=float(gp/gl) if gl > 0 else float("inf"), dd=dd, sumR=sumR,
                net1=(srt[:1].sum()/sumR) if sumR > 0 else float("nan"),
                net3=(srt[:3].sum()/sumR) if sumR > 0 else float("nan"),
                net5=(srt[:5].sum()/sumR) if sumR > 0 else float("nan"),
                wo1=(sumR - srt[:1].sum())/max(n-1, 1))

def profitable(m):
    return bool(m.get("n", 0) >= 25 and m.get("sumR", 0) > 0 and m.get("exp", -1) > 0 and m.get("pf", 0) > 1.00)

# ---------------- WORKER ----------------
def worker(label, out_path):
    sys.path.insert(0, os.path.join(CLONE, "code"))
    import mstrat as MS
    d = MS.load()
    idmap = {}
    for fam in MS.REGISTRY:
        for h in MS.REGISTRY[fam][0](): idmap[h["id"]] = h
    rows = []
    for hid in ATR_IDS:
        h = idmap[hid]
        tr = MS.simulate(d, MS.setups(d, h))       # canonical D2-closed engine, defaults
        m = metrics(tr["R"].values)
        rows.append(dict(id=hid, fam=h["family"], regime=label, eligible=bool(hid in ATR_VALID),
                         profitable=profitable(m), **{k: m.get(k) for k in ("n","exp","win","pf","dd","sumR","net1","net3","net5","wo1")}))
    pd.DataFrame(rows).to_parquet(out_path)
    print(f"[worker {label}] {len(rows)} hyps, bars={len(d)}, wrote {out_path}")

# ---------------- ORCHESTRATOR ----------------
def slice_block(seg, blockdir):
    os.makedirs(blockdir, exist_ok=True)
    a, b = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
    m = pd.read_csv(os.path.join(DM, "OANDA_XAUUSD_M15.csv"))
    m = m[(m["time"] >= a) & (m["time"] < b)].reset_index(drop=True)
    m.to_csv(os.path.join(blockdir, "OANDA_XAUUSD_M15.csv"), index=False, lineterminator="\n")
    for tf, fn in CTX.items():
        h = pd.read_csv(os.path.join(DM, fn))
        h = h[(h["time"] >= a) & (h["time"] < b)].reset_index(drop=True)
        h.to_csv(os.path.join(blockdir, f"OANDA_XAUUSD_{tf}.csv"), index=False, lineterminator="\n")
    return len(m)

def orchestrate():
    M = json.load(open(MAN, encoding="utf-8"))
    segs = [s for s in M["timeframes"]["M15_v2"]["regime_segments"] if s.get("split") != "TOO_SHORT_FULLY_SEALED"]
    expected = {"bear": 52403, "bull": 52851, "correction": 25237}
    perblock = {}
    for s in segs:
        lab = s["type"]; bd = os.path.join(BLOCKROOT, lab)
        n = slice_block(s, bd)
        assert n == expected[lab], f"BAR-ACCOUNTING FAIL {lab}: {n} != {expected[lab]}"
        outp = os.path.join(OUT, f"four_regime_{lab}.parquet")
        env = dict(os.environ); env["AI_QUANT_DATA_DIR"] = bd; env["PYTHONIOENCODING"] = "utf-8"
        print(f"[orch] {lab}: {n} bars OK -> worker")
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--worker", lab, outp], env=env)
        if r.returncode != 0: raise SystemExit(f"worker {lab} failed")
        perblock[lab] = pd.read_parquet(outp)
    # ---- aggregate + persistence leaderboard ----
    allm = pd.concat(perblock.values(), ignore_index=True)
    allm.to_parquet(os.path.join(OUT, "four_regime_all.parquet"))
    piv = allm.pivot_table(index="id", columns="regime", values="profitable", aggfunc="first").fillna(False)
    for lab in expected:
        if lab not in piv.columns: piv[lab] = False
    piv["n_regimes"] = piv[list(expected)].sum(axis=1).astype(int)
    lb = {k: int((piv["n_regimes"] == k).sum()) for k in (3, 2, 1, 0)}
    print("\n=== PERSISTENCE LEADERBOARD (428 ATR; profitable = n>=25 & sumR>0 & exp>0 & pf>1.00 per regime) ===")
    print("profitable in N of 3 regimes:", lb)
    # eligible-only view (the 412; 16 atr-n<25 flagged ineligible)
    elig = allm[allm["eligible"]]["id"].unique()
    pe = piv.loc[[i for i in piv.index if i in set(elig)]]
    lbe = {k: int((pe["n_regimes"] == k).sum()) for k in (3, 2, 1, 0)}
    print("  (eligible 412 only):", lbe, f"  [n_eligible={len(pe)}]")
    survivors = sorted(piv[piv["n_regimes"] == 3].index)
    print(f"\npersist in ALL 3: {len(survivors)}")
    # for all-3 persisters: wo1 + net1 per regime (not aggregated)
    if survivors:
        det = allm[allm["id"].isin(survivors)][["id","fam","regime","n","exp","pf","net1","wo1"]].sort_values(["id","regime"])
        det.to_parquet(os.path.join(OUT, "four_regime_persisters.parquet"))
        print(det.to_string(index=False))
    json.dump({"leaderboard_428": lb, "leaderboard_412_eligible": lbe, "n_persist_all3": len(survivors),
               "persisters": survivors, "expected_bars": expected},
              open(os.path.join(OUT, "four_regime_summary.json"), "w"), indent=1)
    print("\nwrote four_regime_{all,persisters}.parquet + four_regime_summary.json")

if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--worker":
        worker(sys.argv[2], sys.argv[3])
    else:
        orchestrate()
