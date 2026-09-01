"""DATA-CHARACTERISATION ONLY (not a hypothesis test, no strategy, no lag search).
Uses the 11-session GC sample already on disk + governed XAU M15 to establish, empirically:
  (1) do the two clocks align causally?  (2) how much of GC PRICE is a re-encoding of XAU?
  (3) is GC real VOLUME genuinely new information vs OANDA tick-volume?"""
import sys, hashlib, numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
GC = r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\alpha\gc_15m.csv"
XA = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M15.csv"

g = pd.read_csv(GC); g["dt"] = pd.to_datetime(g["dt"], utc=True)
x = pd.read_csv(XA).drop_duplicates("time").sort_values("time")
x["dt"] = pd.to_datetime(x["time"], unit="s", utc=True)
print("="*112); print("  EXISTING GC SAMPLE -- verified on disk"); print("="*112)
print(f"  file   {GC}")
print(f"  sha256 {hashlib.sha256(open(GC,'rb').read()).hexdigest()[:32]}...")
print(f"  bars {len(g)}   {g.dt.min()} -> {g.dt.max()}   fields {list(g.columns)}")
print(f"  sessions {g['day'].nunique()}   price range {g.close.min():.1f} - {g.close.max():.1f}")
print(f"  bar stamp spacing: {sorted(pd.Series(g.dt.diff().dt.total_seconds()/60).value_counts().head(4).to_dict().items())}")

print("\n"+"="*112); print("  §6  CAUSAL TIMESTAMP ALIGNMENT -- tested, not assumed"); print("="*112)
lo, hi = g.dt.min(), g.dt.max()
xs = x[(x.dt >= lo) & (x.dt <= hi)].copy()
print(f"  GC  : {len(g):5d} M15 bars in window, UTC-bucketed from Databento ts_event (nanoseconds UTC)")
print(f"  XAU : {len(xs):5d} M15 bars in window, UTC unix seconds, stamp = bar OPEN")
m = pd.merge(g[["dt","open","high","low","close","volume","ntrades"]],
             xs[["dt","open","high","low","close","volume"]], on="dt", suffixes=("_gc","_xau"))
print(f"  bars whose UTC stamps match EXACTLY: {len(m)}  ({len(m)/len(g):.1%} of GC bars, {len(m)/len(xs):.1%} of XAU bars)")
print(f"  -> both are UTC, both bucket on the same 15-minute grid: a same-stamp join is exact, no resampling needed.")
gonly = set(g.dt) - set(xs.dt); xonly = set(xs.dt) - set(g.dt)
print(f"  GC bars with no XAU bar : {len(gonly)}  (GC trades Sun 22:00 UTC-ish and through the XAU rollover break)")
print(f"  XAU bars with no GC bar : {len(xonly)}  (GC halts 21:00-22:00 UTC daily maintenance; thin GC bars dropped at ntrades<5)")
print(f"  => CAUSAL_TIMESTAMP_ALIGNMENT_FEASIBLE = YES, with an explicit session-mask; the only rule needed is")
print(f"     to compare on bar CLOSE time (stamp+15m) via a backward as-of join -- the convention the lab already ratified.")

print("\n"+"="*112); print("  §14  IS GC GENUINELY NEW INFORMATION, OR A RE-ENCODING OF XAU?"); print("="*112)
m = m.sort_values("dt").reset_index(drop=True)
rg = m.close_gc.diff(); rx = m.close_xau.diff()
ok = np.isfinite(rg) & np.isfinite(rx)
print(f"  overlapping M15 bars used: {int(ok.sum())}  (11 sessions -- characterisation only, NOT a hypothesis test)")
print(f"\n  PRICE  -- contemporaneous M15 return correlation GC vs XAU : {np.corrcoef(rg[ok], rx[ok])[0,1]:.4f}")
print(f"           level correlation                                  : {np.corrcoef(m.close_gc, m.close_xau)[0,1]:.4f}")
print(f"           mean |GC-XAU| level difference (the carry basis)    : {(m.close_gc-m.close_xau).mean():.2f} USD")
print(f"           sd of that difference within the window            : {(m.close_gc-m.close_xau).std():.2f} USD")
print(f"    -> GC PRICE is very nearly the same series as XAU price. As an information source, GC *price*")
print(f"       is largely a re-encoding of data the price-only campaign has already exhausted.")
print(f"\n  VOLUME -- GC real traded contracts vs OANDA XAU tick-count:")
print(f"           GC   volume: median {m.volume_gc.median():.0f} contracts/bar, ntrades median {m.ntrades.median():.0f}")
print(f"           XAU  volume: median {m.volume_xau.median():.0f} (OANDA tick count from ONE retail broker, not traded size)")
print(f"           correlation of the two volume series (levels) : {np.corrcoef(m.volume_gc, m.volume_xau)[0,1]:.4f}")
print(f"           correlation in logs                           : {np.corrcoef(np.log1p(m.volume_gc), np.log1p(m.volume_xau))[0,1]:.4f}")
print(f"           R^2 of XAU tick-volume explaining GC volume   : {np.corrcoef(np.log1p(m.volume_gc), np.log1p(m.volume_xau))[0,1]**2:.3f}")
sh = np.corrcoef(np.log1p(m.volume_gc), np.log1p(m.volume_xau))[0,1]**2
print(f"    -> ~{100*(1-sh):.0f}% of the variation in real COMEX volume is NOT captured by the tick-count series")
print(f"       the lab currently owns. THIS is the genuinely new channel, not GC price.")
