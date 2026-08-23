"""m02_pullback3_net.py — MODULAR_DISCOVERY_PROGRAM_V1, M02 priority #1: resolve CAND-G0037 (TREND_UP x pullback3, stop=atr2,
exit=time40) NET verdict. EXACT historical definition (§7: no retuning) — same entry/stop/exit/regime/data; the ONLY change vs
the GROSS run is canonical_evaluate(gross=False) = NET of the canonical CFG cost. Reproduces GROSS +0.4206 as a control."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regime as _r  # triggers ratified-code sys.path fallback so market_structure imports
import numpy as np, pandas as pd
from edge_research._common import load, PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC
from edge_research.flowb_strategies import Ctx
from edge_research._screen import derive_blocks, canonical_evaluate, metrics
from edge_research.flowb_generator import gen_signals

SPEC = dict(entry="pullback3", regime="TREND_UP", stop="atr2", hold=40, exit_kind="time", exit_param=40.0)

def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    blocks = derive_blocks(d); ctx = Ctx(d, blocks)
    trades, elig = gen_signals(ctx, SPEC)
    print(f"CAND-G0037 EXACT replay. data M15_v2 pre-holdout: n={len(d)} {pd.to_datetime(d['time'].iloc[0],unit='s',utc=True)}..{pd.to_datetime(d['time'].iloc[-1],unit='s',utc=True)} | raw trades={len(trades)}")
    for label, gross in [("GROSS (control, gross=True)", True), ("NET (gross=False, CFG cost)", False)]:
        res = canonical_evaluate(ctx.d, trades, gross=gross)
        m = metrics(res)
        r = np.array([x["r"] for x in res]); si = np.array([x["signal_idx"] for x in res])
        yr = pd.to_datetime(d["time"].to_numpy()[si], unit="s", utc=True).year
        # recent-primary window 2022-12 -> 2025-10 (the estimand)
        t = d["time"].to_numpy()[si]
        rp = (t >= pd.Timestamp("2022-12-16", tz="UTC").timestamp()) & (t < pd.Timestamp("2025-10-23", tz="UTC").timestamp())
        disc = yr <= 2018; conf = (yr >= 2020) & (yr <= 2022); oos = yr >= 2023
        sr = np.sort(r); k1 = max(1, len(r)//100); k10 = max(1, len(r)//10)
        print(f"  {label}: N={m['n']} avgR={m['avg_R']:+.4f} PF={m.get('profit_factor')} trimmed1%={m['trimmed_top1pct']['avg_R']:+.4f}")
        print(f"    recent-primary(2022-12..2025-10) avgR={r[rp].mean():+.4f}(n{int(rp.sum())}) | best10%rm={sr[:-k10].mean():+.4f}")
        print(f"    DISC<=2018 {r[disc].mean():+.4f}(n{int(disc.sum())}) | CONF 20-22 {r[conf].mean():+.4f}(n{int(conf.sum())}) | OOS 23+ {r[oos].mean():+.4f}(n{int(oos.sum())})")
        by = {int(y): (round(float(r[yr==y].mean()),3), int((yr==y).sum())) for y in sorted(set(yr))}
        print(f"    by-year: {by}")
if __name__ == "__main__":
    main()
