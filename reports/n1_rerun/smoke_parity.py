"""N1 smoke parity — REAL ve_n1_replay API. The verified INPUT sequences are reconstructed byte-for-byte
from the AI Trader conftest arrays (BOS_BULL -> exactly one confirmed BOS_BULL at idx 14; TREND_UP = 460
calm bars + BOS_BULL -> last bar {TREND_UP}). We supply the authoritative INPUT; the OFFICIAL engine
produces the OUTPUT. No repo import, no invented outputs."""
import sys, json
import ve_n1_replay as R

SYM, TF, IVAL = "XAUUSD", "M15", 900

# ── verified INPUT arrays (identical to ai_trader/new_brain_bridge/tests/conftest.py) ────────────
BOS_BULL_HIGHS = [10, 11, 12, 13, 10, 9, 8, 12, 16, 12, 9, 8, 7, 11, 20, 14, 10, 9]
BOS_BULL_LOWS  = [9, 10, 11, 12, 9, 8, 7, 11, 15, 11, 8, 7, 6, 10, 19, 13, 9, 8]
BOS_BULL_CLOSES = [h - 1 for h in BOS_BULL_HIGHS]
BOS_BULL_OPENS  = [lo + 0.5 for lo in BOS_BULL_LOWS]
CALM = 460

def bar(sym, i, o, h, lo, c):
    return R.Bar(symbol=sym, ts_open=i * IVAL, ts_close=(i + 1) * IVAL,
                 open=float(o), high=float(h), low=float(lo), close=float(c), volume=100.0)

def bos_bull_bars(sym=SYM):
    return [bar(sym, i, BOS_BULL_OPENS[i], BOS_BULL_HIGHS[i], BOS_BULL_LOWS[i], BOS_BULL_CLOSES[i])
            for i in range(len(BOS_BULL_HIGHS))]

def trend_up_bars(sym=SYM):
    bars, price = [], 2400.0
    for i in range(CALM):
        o = price; h = o + 0.4; lo = o - 0.4; c = o + 0.02
        bars.append(bar(sym, i, o, h, lo, c)); price = c
    for i, b in enumerate(bos_bull_bars(sym)):
        off = CALM + i
        bars.append(R.Bar(symbol=sym, ts_open=off * IVAL, ts_close=(off + 1) * IVAL,
                          open=b.open, high=b.high, low=b.low, close=b.close, volume=b.volume))
    return bars

def modified_close(bars, index, delta):
    out = list(bars); o = out[index]
    out[index] = R.Bar(symbol=o.symbol, ts_open=o.ts_open, ts_close=o.ts_close, open=o.open,
                       high=o.high, low=o.low, close=o.close + delta, volume=o.volume)
    return out

def mirror(bars, C=5000.0):
    """Vertical price mirror x -> C-x: turns the up-trend/BOS_BULL into a genuine down-trend/BOS_BEAR
    through the SAME detectors. Input construction only; the engine produces the label."""
    out = []
    for b in bars:
        out.append(R.Bar(symbol=b.symbol, ts_open=b.ts_open, ts_close=b.ts_close,
                         open=C - b.open, high=C - b.low, low=C - b.high, close=C - b.close, volume=b.volume))
    return out

def eng():
    return R.initialize(symbol=SYM, timeframe=TF, bar_interval_seconds=IVAL)

TU = trend_up_bars(); BB = bos_bull_bars(); TD = mirror(TU)
res = {}

# live vs replay parity
e = eng(); live = [e.observe_closed_bar(b) for b in TU]; live_fps = [r.output_fingerprint for r in live]
replay = eng().replay(TU); replay_fps = [r.output_fingerprint for r in replay]
res["live_vs_replay_identical"] = (live_fps == replay_fps)

# TREND_UP resolved
last = live[-1]; ar = sorted(str(x) for x in last.applicable_regimes)
res["trend_up_last_regimes"] = ar
res["trend_up_is_TREND_UP"] = any("TREND_UP" in x for x in ar)
res["trend_up_raw_axes"] = str(last.raw_axes)

# UNCERTAIN (no confirmed break in a short calm prefix)
eu = eng(); early = [eu.observe_closed_bar(b) for b in TU[:50]]
res["uncertain_prefix_regimes"] = sorted(str(x) for x in early[-1].applicable_regimes)
res["uncertain_axes_status"] = str(early[-1].regime_axes_status)

# TREND_DOWN (mirror of the up-trend -> genuine bos_bear through the same detectors)
td = eng().replay(TD); ard = sorted(str(x) for x in td[-1].applicable_regimes)
res["trend_down_last_regimes"] = ard
res["trend_down_is_TREND_DOWN"] = any("TREND_DOWN" in x for x in ard)
res["trend_down_raw_axes"] = str(td[-1].raw_axes)

# BOS present
bos = eng().replay(BB)
res["bos_last_raw_axes"] = str(bos[-1].raw_axes)

# snapshot / restore
mid = len(TU) // 2
es = eng()
for b in TU[:mid]: es.observe_closed_bar(b)
er = eng(); er.restore(es.snapshot())
tail = [er.observe_closed_bar(b).output_fingerprint for b in TU[mid:]]
res["snapshot_restore_identical"] = (tail == replay_fps[mid:])

# dedup: re-observing the exact same bar (same ts) must be IDEMPOTENT — processed exactly once
# (bars_observed unchanged, identical fingerprint), per "bară duplicată procesată o singură dată".
ei = eng()
r_a = ei.observe_closed_bar(BB[0]); r_b = ei.observe_closed_bar(BB[1]); n_before = ei.bars_observed
r_b2 = ei.observe_closed_bar(BB[1])  # duplicate of the last
res["duplicate_bar"] = ("idempotent OK" if (ei.bars_observed == n_before and r_b2.output_fingerprint == r_b.output_fingerprint)
                        else "DOUBLE-PROCESSED (bad)")

# out-of-order fail-closed
seq = list(BB)
ooo = seq[:3] + [seq[1]] + seq[3:]
try:
    eng().replay(ooo); res["out_of_order"] = "ACCEPTED (unexpected)"
except (R.OutOfOrderBarError, R.DuplicateBarError) as ex: res["out_of_order"] = f"{type(ex).__name__} OK"

# content sensitivity: modifying the last close changes only the last fingerprint
mod = modified_close(TU, len(TU) - 1, 5.0)
mfps = [r.output_fingerprint for r in eng().replay(mod)]
res["modified_last_changes_only_last_fp"] = (mfps[-1] != replay_fps[-1] and mfps[:-1] == replay_fps[:-1])

res["n1_contract_version"] = last.n1_contract_version
res["router_version"] = last.router_version
res["detector_config_fp"] = last.detector_configuration_fingerprint

print(json.dumps(res, indent=2, default=str))
ok = (res["live_vs_replay_identical"] and res["trend_up_is_TREND_UP"] and res["trend_down_is_TREND_DOWN"]
      and res["uncertain_prefix_regimes"] == ["UNCERTAIN"] and res["snapshot_restore_identical"]
      and "OK" in res["duplicate_bar"] and "OK" in res["out_of_order"])
print("\nSMOKE_PARITY:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
