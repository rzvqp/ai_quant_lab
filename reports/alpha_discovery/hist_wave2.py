"""HISTORICAL RE-REVIEW WAVE 2 + DEVELOPMENT POPULATION INTEGRITY RECOVERY.
Uses ONLY the manifest-gated discovery-block population (VE migration ed57853, load_mstrat_historical).
DEVELOPMENT = blocks 0+1 (105,254 bars), evaluated PER-BLOCK (no 2013->2016 gap bridging). CALIBRATION = block 2.
VALIDATION (block 3) / SEALED never touched. Cost RATIFIED BASE 0.05 / STRESS 0.24. Exact frozen specs, no retune."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"; ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
os.environ.setdefault("RATIFIED_CODE_DIR", WP5B)
for p in (os.path.join(ALPHA, "code"), WP5B, ALPHA):
    if p not in sys.path: sys.path.insert(0, p)
import mstrat, htf_context_historical as H
SP = os.path.dirname(os.path.abspath(__file__)); TICK = mstrat.TICK
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP, "wave2.log"), "a").write(f"{int(time.time())} {m}\n")

log("load_mstrat_historical (gated) ...")
d = H.load_mstrat_historical(); d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True); d = d.reset_index(drop=True)
blocks = H.discovery_blocks()  # [(b0s,b0e),(b1s,b1e),(b2s,b2e),(b3s,b3e)]
ts_all = d["time"].astype("int64").to_numpy()
def in_block(bi): s, e = blocks[bi]; return (ts_all >= s) & (ts_all <= e)
DEV = in_block(0) | in_block(1); CALIB = in_block(2); VAL = in_block(3)
import hashlib
dev_rows = d[DEV]
DEV_ID = dict(loader="htf_context_historical.load_mstrat_historical (VE ed57853)", manifest="config/split_manifest.json",
              blocks={"block0": [str(dev_rows["dt"].iloc[0]), "2013-09-27"], "block1": ["2016-01-11", str(dev_rows[in_block(1)[DEV]]["dt"].iloc[-1]) if False else "2018-04-06"]},
              dev_bars=int(DEV.sum()), block0_bars=int(in_block(0).sum()), block1_bars=int(in_block(1).sum()),
              calib_bars=int(CALIB.sum()), sha256_ohlc=hashlib.sha256(d.loc[DEV, ["time","open","high","low","close"]].to_numpy().tobytes()).hexdigest()[:16])
log(f"GATED DEVELOPMENT bars={DEV_ID['dev_bars']} (block0={DEV_ID['block0_bars']} block1={DEV_ID['block1_bars']}) CALIB={DEV_ID['calib_bars']} sha={DEV_ID['sha256_ohlc']}")
assert d.loc[DEV, "dt"].max() < pd.Timestamp("2018-05-01", tz="UTC"), "DEV leak past 2018-05"
assert not d.loc[DEV].equals(d.loc[VAL]) and int(DEV.sum()) < 120000, "DEV population sanity"

# N1 regime aligned to full d by ts
Z = np.load(os.path.join(SP, "n1_ledger.npz"), allow_pickle=True)
pos = np.searchsorted(Z["ts_open"].astype(np.int64), ts_all); ok = Z["ts_open"].astype(np.int64)[pos] == ts_all
bit = {x: 1 << i for i, x in enumerate(list(Z["vocab"]))}
mask_all = np.where(ok, Z["mask"][pos], 0); disp_all = np.where(ok, Z["is_disp"][pos], False).astype(bool)
CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
RT = {"GROSS": 0.0, "BASE": CM["base_ratified"]["round_trip_total"], "STRESS": CM["stress_ratified"]["round_trip_total"]}

# ── per-block gated evaluation: run setups on each DEV block slice separately (no cross-gap) ──────────
BLOCK_SLICES = {}
for name, bi in (("b0", 0), ("b1", 1), ("calib", 2)):
    m = in_block(bi); sl = d[m].reset_index(drop=True)
    tsl = sl["time"].astype("int64").to_numpy(); p2 = np.searchsorted(Z["ts_open"].astype(np.int64), tsl); o2 = Z["ts_open"].astype(np.int64)[p2] == tsl
    reg = dict(up=np.where(o2, (Z["mask"][p2] & bit["TREND_UP"]) != 0, False), down=np.where(o2, (Z["mask"][p2] & bit["TREND_DOWN"]) != 0, False),
               disp=np.where(o2, Z["is_disp"][p2], False).astype(bool))
    BLOCK_SLICES[name] = (sl, reg)

def eval_family(fam, h, scen, blocks_use=("b0", "b1"), keep_side=None):
    """Run mstrat family setups on each block slice, cost-apply, combine R with (block, si, dir)."""
    cfg = dict(mstrat.CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = RT[scen] / (2 * TICK)
    out = []
    for bn in blocks_use:
        sl, reg = BLOCK_SLICES[bn]; setups = mstrat.REGISTRY[fam][1](sl, h)
        if keep_side is not None:
            setups = [s for s in setups if (reg["up"][s["si"]] if s["dir"] > 0 else reg["down"][s["si"]])] if keep_side == "protrend" else setups
        dmap = {s["si"]: s["dir"] for s in setups}
        led = mstrat.simulate(sl, setups, cfg)
        for r, si in zip(led["R"], led["si"]): out.append(dict(r=float(r), block=bn, si=int(si), dir=int(dmap.get(int(si), 1))))
    return out

def eval_da(w, nacc, hold, scen, blocks_use=("b0", "b1")):  # Candidate-001 style (integrity replay of frozen V1: w0.8,a2,hold48)
    cfg = dict(mstrat.CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = RT[scen] / (2 * TICK); out = []
    for bn in blocks_use:
        sl, reg = BLOCK_SLICES[bn]; o = sl["open"].to_numpy(); cl = sl["close"].to_numpy(); atr = sl["m_atr"].to_numpy(); nb = len(sl)
        disp = reg["disp"]; setups = []
        for j in range(2, nb - nacc - 2):
            if not disp[j] or atr[j] != atr[j] or abs(cl[j] - o[j]) < w * atr[j]: continue
            dr = 1 if cl[j] > o[j] else -1
            if all((cl[j + 1 + k] > cl[j]) == (dr > 0) for k in range(nacc)):
                i = j + nacc; raw = o[j] - dr * 0.1 * atr[j]; ref = o[min(i + 1, nb - 1)]
                fl = max(2 * (0.08 if scen == "STRESS" else 0.05 if scen == "BASE" else 0.0), 0.05, 0.10 * atr[i]) if atr[i] == atr[i] else 0.05
                st = ref - dr * max(abs(ref - raw), fl)
                if (dr > 0 and st < ref) or (dr < 0 and st > ref): setups.append(dict(si=i, ei=i + 1, dir=dr, stop=float(st), exit_kind="time", exit_param=float(hold)))
        dmap = {s["si"]: s["dir"] for s in setups}
        led = mstrat.simulate(sl, setups, cfg)
        for r, si in zip(led["R"], led["si"]): out.append(dict(r=float(r), block=bn, si=int(si), dir=int(dmap.get(int(si), 1))))
    return out

def Mt(res):
    if not res: return dict(n=0)
    r = np.sort(np.array([x["r"] for x in res]))[::-1]; nn = len(r); w = r[r > 0]; l = r[r <= 0]; tot = float(r.sum())
    byb = defaultdict(float)
    for x in res: byb[x["block"]] += x["r"]
    rem = lambda p: round(float(r[max(1, int(nn * p)):].mean()), 4)
    return dict(n=nn, avg_R=round(float(r.mean()), 4), win=round(len(w) / nn, 3),
                pf=round(float(w.sum() / -l.sum()), 3) if l.sum() < 0 else None, median=round(float(np.median(r)), 3),
                top1_share=round(float(r[:max(1, int(nn * 0.01))].sum() / tot), 3) if tot > 0 else None,
                best1_removed=rem(0.01), best2_removed=rem(0.02),
                per_block={k: round(v, 2) for k, v in byb.items()},
                long_frac=round(float(np.mean([x["dir"] > 0 for x in res])), 2))
def classify(g, b, s, mins=150):
    nn = g.get("n", 0)
    if nn < 30: return "HISTORICAL_CANDIDATE_INSUFFICIENT_EVIDENCE"
    if nn < mins: return "HISTORICAL_CANDIDATE_INSUFFICIENT_EVIDENCE"
    if (g.get("avg_R") or -9) <= 0 or (b.get("avg_R") or -9) <= 0: return "HISTORICAL_CANDIDATE_FAIL"
    if (s.get("avg_R") or -9) <= 0: return "HISTORICAL_CANDIDATE_COST_FRAGILE"
    return "HISTORICAL_CANDIDATE_CONFIRMED_FOR_DEEPER_RESEARCH"

# ── replays ──────────────────────────────────────────────────────────────────────────────────────
CANDS = {
 "S5_C_2d587447": ("S5", dict(session="ny", mode="breakout", side="up", stop="or_opp", exit="rr3")),
 "S9_C_0bb5095b": ("S9", dict(c4h="up", conf1h="any", lb=20, stop="structural", exit="rr2")),
 "S9_C_d008e0a4": ("S9", dict(c4h="up", conf1h="align", lb=10, stop="structural", exit="rr3")),
 "S20_C_09d2245b": ("S20", dict(ctx="h4up", trig="breakout", lb=50, stop="atr", exit="rr3")),
 "S1swing_C_954698b1": ("S1", dict(confirm="close_beyond", exit="time", imb="fvg", liq_lb=20, liq_ref="swing", side="low", stop="beyond_sweep", window=8)),
 "S1PDH_C_dca5629f": ("S1", dict(confirm="consecutive2", exit="rr2", imb="none", liq_lb=20, liq_ref="pdh_pdl", side="low", stop="beyond_sweep", window=8)),
 "S1PDH_C_9214b37b": ("S1", dict(confirm="displacement", exit="rr3", imb="none", liq_lb=20, liq_ref="pdh_pdl", side="high", stop="beyond_sweep", window=8)),
}
records = {}
for cid, (fam, h) in CANDS.items():
    g = Mt(eval_family(fam, h, "GROSS")); b = Mt(eval_family(fam, h, "BASE")); s = Mt(eval_family(fam, h, "STRESS"))
    st = classify(g, b, s); records[cid] = dict(family=fam, spec=h, GROSS=g, BASE=b, STRESS=s, status=st)
    log(f"{cid} [{fam}]: n={b.get('n')} G={g.get('avg_R')} B={b.get('avg_R')} S={s.get('avg_R')} best1_rem={b.get('best1_removed')} per_block={b.get('per_block')} -> {st}")
# Candidate-001 V1 integrity replay (frozen w0.8 a2 hold48)
g = Mt(eval_da(0.8, 2, 48, "GROSS")); b = Mt(eval_da(0.8, 2, 48, "BASE")); s = Mt(eval_da(0.8, 2, 48, "STRESS"))
records["Candidate001_V1"] = dict(family="displacement_acceptance", spec="w0.8,a2,hold48 (frozen)", GROSS=g, BASE=b, STRESS=s, status=classify(g, b, s),
                                  note="integrity replay only; not resurrected/modified")
log(f"Candidate001_V1 integrity: n={b.get('n')} G={g.get('avg_R')} B={b.get('avg_R')} S={s.get('avg_R')} best1_rem={b.get('best1_removed')} per_block={b.get('per_block')} -> {records['Candidate001_V1']['status']}")

json.dump(dict(development_population=DEV_ID, records=records, migration="ed57853 (25/25 tests PASS)",
               validation_access=0, final_holdout_access=0), open(os.path.join(SP, "wave2_records.json"), "w"), indent=1, default=float)
log("WAVE2_COMPLETE")
