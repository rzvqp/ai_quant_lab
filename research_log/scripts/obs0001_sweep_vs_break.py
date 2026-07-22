"""OBS-0001 -- Descriptive test: sweep-and-reject vs break-and-hold of the prior-day extreme.

PRE-REGISTERED (written before seeing results):
  Instrument/TF: XAUUSD H1, pre-holdout only (loader fail-closed, cutoff 2025-10-23).
  Prior-day high/low (PDH/PDL): from UTC-calendar daily OHLC, previous available trading day.
  Interaction (up):   the FIRST H1 bar of a day whose high > PDH.
      classify SWEEP_REJECT if that bar's close < PDH, else BREAK_HOLD.
  Interaction (down): the FIRST H1 bar of a day whose low < PDL.
      classify SWEEP_REJECT if that bar's close > PDL, else BREAK_HOLD.
  Aftermath: forward displacement of close over the next K bars, sign-normalized so that
      POSITIVE = "continuation in the breakout direction", NEGATIVE = "reversion back through level".
      up:   fwd = close[i+K] - close[i]        (up-break continuation is +)
      down: fwd = -(close[i+K] - close[i])     (down-break continuation is +)
  Falsification target: the SMC assumption predicts REJECT -> reversion (negative fwd) and
      HOLD -> continuation (positive fwd). If REJECT and HOLD forward displacements are NOT
      meaningfully different, the sweep/break distinction is descriptively weak.
  Controls: unconditional forward displacement over K bars (any bar), and base rate of the
      close ending on the far side of the level.
"""
import sys
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation")
import numpy as np
import pandas as pd
from edge_research import _common

CUTOFF = _common.RESEARCH_HOLDOUT_CUTOFF_UTC
SPLIT = _common.PRE_HOLDOUT_SPLIT_ID
KS = [3, 6, 12]
ATR_BUFFER_FRAC = 0.0  # v1: no buffer; a bar counts as interacting if it pierces the level at all

df, meta = _common.load("H1", data_split_id=SPLIT, cutoff=CUTOFF)
df = df.reset_index(drop=True)
assert df["dt"].max() < pd.Timestamp(CUTOFF), "holdout breach"
print("loaded H1:", meta["n_bars_used"], "bars", meta["min_date_used"], "->", meta["max_date_used"])

df["day"] = df["dt"].dt.date
daily = df.groupby("day").agg(d_high=("high", "max"), d_low=("low", "min")).reset_index()
daily["pdh"] = daily["d_high"].shift(1)
daily["pdl"] = daily["d_low"].shift(1)
pdh = dict(zip(daily["day"], daily["pdh"]))
pdl = dict(zip(daily["day"], daily["pdl"]))

records = []  # each: side, cls (reject/hold), i, day
for day, g in df.groupby("day"):
    ph, pl = pdh.get(day), pdl.get(day)
    if ph is None or pl is None or np.isnan(ph) or np.isnan(pl):
        continue
    idx = g.index.tolist()
    # first up-interaction
    up = next((i for i in idx if df.at[i, "high"] > ph), None)
    if up is not None:
        cls = "reject" if df.at[up, "close"] < ph else "hold"
        records.append(("up", cls, up))
    # first down-interaction
    dn = next((i for i in idx if df.at[i, "low"] < pl), None)
    if dn is not None:
        cls = "reject" if df.at[dn, "close"] > pl else "hold"
        records.append(("down", cls, dn))

n = len(df)
def fwd(i, K, side):
    j = i + K
    if j >= n:
        return None
    d = df.at[j, "close"] - df.at[i, "close"]
    return d if side == "up" else -d

print(f"\ninteractions: {len(records)}  "
      f"(up={sum(1 for r in records if r[0]=='up')}, down={sum(1 for r in records if r[0]=='down')})")
by = {("reject",): [], ("hold",): []}
for side, cls, i in records:
    by[(cls,)].append((side, i))
print(f"REJECT (sweep) n={len(by[('reject',)])}   HOLD (break) n={len(by[('hold',)])}")

# control: unconditional forward displacement magnitude (direction-agnostic baseline)
def summarize(vals):
    a = np.array([v for v in vals if v is not None], float)
    if len(a) == 0:
        return "n=0"
    return (f"n={len(a):4d}  mean={a.mean():+7.3f}  median={np.median(a):+7.3f}  "
            f"P(cont>0)={(a>0).mean():.2f}  std={a.std():.2f}")

print("\n=== forward displacement (sign-normalized; + = continuation, - = reversion) ===")
for K in KS:
    rej = [fwd(i, K, side) for side, i in by[("reject",)]]
    hol = [fwd(i, K, side) for side, i in by[("hold",)]]
    print(f"\nK={K} bars:")
    print(f"  SWEEP_REJECT : {summarize(rej)}")
    print(f"  BREAK_HOLD   : {summarize(hol)}")
    r = np.array([v for v in rej if v is not None]); h = np.array([v for v in hol if v is not None])
    if len(r) and len(h):
        diff = h.mean() - r.mean()
        # Welch-ish standardized gap (descriptive effect size, NOT a p-value claim)
        pooled = np.sqrt(r.var()/len(r) + h.var()/len(h))
        print(f"  gap(HOLD-REJECT) mean = {diff:+.3f}   standardized = {diff/pooled:+.2f}" if pooled else "")

# base-rate control: unconditional K-bar close change (up-direction convention), all bars
print("\n=== control: unconditional |K-bar close change| (all bars, up-convention) ===")
for K in KS:
    allv = [df.at[i+K, "close"] - df.at[i, "close"] for i in range(n-K)]
    a = np.array(allv, float)
    print(f"  K={K}: mean={a.mean():+.3f} mean|.|={np.abs(a).mean():.3f} std={a.std():.2f}")
