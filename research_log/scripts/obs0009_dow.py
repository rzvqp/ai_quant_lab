"""OBS-0009 (E008 / new perspective): day-of-week structure in volatility and returns.
Pre-reg: mean Parkinson r (H1) by weekday; mean daily close-to-close return by weekday; with
bootstrap CI. Descriptive -- looking for a repeatable weekday volatility/return signature.
"""
from _lab import *
import numpy as np

df, meta = load("H1")
df["r"] = np.log(df["high"] / df["low"])
df["dow"] = df["dt"].dt.day_name()
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sunday"]
print("OBS-0009 | mean Parkinson r (x1e4) by weekday (H1):")
for d in order:
    a = df[df["dow"] == d]["r"].values * 1e4
    if len(a) > 30:
        lo, hi = boot_ci((a).tolist()); print(f"  {d:9s} n={len(a):5d} mean={a.mean():.1f} CI95=[{lo:.1f},{hi:.1f}]")

# daily returns by weekday
dfd = df.copy(); dfd["day"] = dfd["dt"].dt.date
daily = dfd.groupby("day").agg(close=("close", "last"), dow=("dow", "last")).reset_index()
daily["ret"] = daily["close"].diff()
print("\ndaily close-to-close change by weekday:")
for d in order:
    a = daily[daily["dow"] == d]["ret"].dropna().values
    if len(a) > 10:
        lo, hi = boot_ci(a.tolist()); print(f"  {d:9s} n={len(a):4d} mean={a.mean():+.2f} CI95=[{lo:+.2f},{hi:+.2f}]")
