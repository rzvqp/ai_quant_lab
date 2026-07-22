"""OBS-0010 (new perspective): do daily extremes cluster at round-number price levels?
Pre-reg: for daily highs and lows, compute distance to nearest multiple of $50 and $100, as a
fraction of $50/$100. If round numbers attract/reject, the distribution of (price mod 50) for
daily extremes is NON-uniform, concentrated near 0. Compare share within +/-$5 of a $50 multiple
vs the uniform expectation (10/50 = 20%). Bootstrap CI on the share.
"""
from _lab import *
import numpy as np

df, meta = load("H1"); df["day"] = df["dt"].dt.date
daily = df.groupby("day").agg(h=("high", "max"), l=("low", "min")).reset_index()
ext = np.concatenate([daily["h"].values, daily["l"].values])
print("OBS-0010 |", len(ext), "daily extremes 2023-2025")

for base in (50, 100):
    mod = np.mod(ext, base)
    dist = np.minimum(mod, base - mod)          # distance to nearest multiple
    band = base * 0.1                            # +/-10% of the grid = +/-$5 ($50) or +/-$10 ($100)
    share = float((dist <= band).mean())
    expected = 2 * band / base                   # uniform expectation
    rng = np.random.default_rng(7)
    boot = [ (dist[rng.integers(0, len(dist), len(dist))] <= band).mean() for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print(f"  ${base} grid: share within +/-{band:.0f} = {share:.3f} "
          f"(CI[{lo:.3f},{hi:.3f}]) vs uniform {expected:.3f}  "
          f"{'-> clustering' if lo > expected else '-> no clustering'}")
