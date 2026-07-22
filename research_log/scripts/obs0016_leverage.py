"""OBS-0016 (new perspective): asymmetric volatility / leverage effect on gold. Pre-reg: at daily
scale, does the SIGN of today's return predict tomorrow's range (leverage effect: down days ->
higher next-day vol, as in equities)? Measure mean next-day Parkinson range after down vs up days,
and corr(return_t, range_{t+1}). Also daily range persistence corr(range_t, range_{t-1}).
"""
from _lab import *
import numpy as np

df, meta = load("H1"); df["day"] = df["dt"].dt.date
daily = df.groupby("day").agg(h=("high", "max"), l=("low", "min"),
                              o=("open", "first"), c=("close", "last")).reset_index()
daily["ret"] = daily["c"].diff()
daily["rng"] = np.log(daily["h"] / daily["l"])
daily = daily.dropna().reset_index(drop=True)
print("OBS-0016 |", len(daily), "trading days")
# range persistence
print(f"  daily range persistence corr(rng_t, rng_t-1) = "
      f"{np.corrcoef(daily['rng'].values[1:], daily['rng'].values[:-1])[0,1]:+.3f}")
# leverage: next-day range after down vs up days
nxt = daily["rng"].values[1:]; cur_ret = daily["ret"].values[:-1]
up = nxt[cur_ret > 0]; dn = nxt[cur_ret < 0]
lo_u, hi_u = boot_ci((up * 1e4).tolist()); lo_d, hi_d = boot_ci((dn * 1e4).tolist())
print(f"  next-day range after UP days   = {up.mean()*1e4:.1f} CI[{lo_u:.1f},{hi_u:.1f}] (n={len(up)})")
print(f"  next-day range after DOWN days = {dn.mean()*1e4:.1f} CI[{lo_d:.1f},{hi_d:.1f}] (n={len(dn)})")
c = np.corrcoef(cur_ret, nxt)[0, 1]
print(f"  corr(return_t, range_t+1) = {c:+.3f}  (equity-style leverage => NEGATIVE)")
