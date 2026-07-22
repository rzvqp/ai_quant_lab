"""OBS-0007 (NRQ-5): Decompose the lag-24 volatility seasonality. Is it a fixed hour-of-day
profile (session opens/news), and does same-state clustering PERSIST after removing hour-of-day?
Pre-reg: mean r by UTC hour; residual rhat = r - hour_mean; compare acf1(r) vs acf1(rhat) and
acf24(r) vs acf24(rhat). If acf24 collapses on rhat but acf1 survives -> seasonality is hour-of-day,
clustering is separate same-state persistence.
"""
from _lab import *
import numpy as np

df, meta = load("H1")
df["r"] = np.log(df["high"] / df["low"])
df = df[df["r"] > 0].copy()
df["hour"] = df["dt"].dt.hour
prof = df.groupby("hour")["r"].mean()
print("OBS-0007 |", len(df), "bars. mean Parkinson r by UTC hour (x1e4):")
order = prof.sort_values(ascending=False)
print("  highest:", [f"{h:02d}h={v*1e4:.1f}" for h, v in order.head(4).items()])
print("  lowest :", [f"{h:02d}h={v*1e4:.1f}" for h, v in order.tail(4).items()])
print(f"  peak/trough ratio = {order.iloc[0]/order.iloc[-1]:.2f}x")

df["rhat"] = df["r"] - df["hour"].map(prof)
r = df["r"].values; rh = df["rhat"].values
def acf(x, lag):
    return float(np.corrcoef(x[:-lag], x[lag:])[0, 1])
print("\n            raw r     hour-resid rhat")
for lag in (1, 2, 24):
    print(f"  acf{lag:2d}   {acf(r,lag):+.3f}      {acf(rh,lag):+.3f}")
