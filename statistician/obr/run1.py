"""STAT-OBR-BULL-1 run 1 -- spec freeze, population census, baseline reproduction, fill-ordering audit.
Read-only. OBR-BULL-1 is not modified.
"""
from __future__ import annotations
import sys, os, json, hashlib
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\obr"
sys.path.insert(0, AD); os.chdir(AD)
import ob_core as OB, htf_core as HC
from ob_contrast import limit_fill
from tsm_core import independent_episodes

# ---------------- spec freeze ----------------
files = ["ob_core.py", "ob_candidate.py", "ob_contrast.py", "ob_falsify.py", "ob_m5.py", "htf_core.py"]
hs = {}
for f in files:
    hs[f] = hashlib.sha256(open(os.path.join(AD, f), "rb").read()).hexdigest()
spec = dict(K=OB.K, DL=OB.DL, RETEST_WIN=OB.RETEST_WIN, FLOOR_ATR=OB.FLOOR_ATR,
            disp_min=1.5, tgtR=2.0, sessions=["LN", "NY"], side="LONG",
            COST_PRICE=HC.COST_PRICE, PIP=HC.PIP,
            entry="limit BUY at frozen block_high", stop="block_low - 0.1*ATR, floored to risk>=0.5*ATR")
SPEC_HASH = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
print("=" * 96)
print("  SECTION 1 -- CANDIDATE SPEC FREEZE")
print("=" * 96)
for f, v in hs.items(): print(f"    {f:18} sha256 {v[:16]}")
print(f"    frozen params: {spec}")
print(f"    SPEC_HASH = {SPEC_HASH}")

m, H1, H4, P = OB.build()
print(f"\n    M15 bars={len(m)}  span {m['dt'].min()} .. {m['dt'].max()}")

# ---------------- population census ----------------
print("\n" + "=" * 96)
print("  SECTION 3 -- EVENT POPULATION CENSUS")
print("=" * 96)
ev_all = OB.detect_obs(P, 0.75, "bull")
ev_15 = [e for e in ev_all if e["disp"] >= 1.5]
print(f"    causal OB events (disp>=0.75, bull) : {len(ev_all)}")
print(f"    causal OB events (disp>=1.5,  bull) : {len(ev_15)}")
fr = [e for e in ev_all if OB.first_retest(P, e) is not None]
print(f"    with a fresh first retest (disp>=0.75): {len(fr)}   (Alpha census: 17,432 OBs / 13,137 retests -- both directions)")

atr = P["atr"]; hi100 = P["hi100"]; hr = m["dt"].dt.hour.values; yr = m["dt"].dt.year.values


def collect(disp_min=1.5, tgtR=2.0, fill="frozen"):
    """fill='frozen'  -> Alpha's limit_fill (close-invalidation checked BEFORE the touch on the same bar)
       fill='causal'  -> a resting limit fills the moment low[k]<=level; invalidation only on bars BEFORE the fill"""
    h = P["h"]; l = P["l"]; c = P["c"]; n = P["n"]
    ev = OB.detect_obs(P, disp_min, "bull"); rows = []
    for e in ev:
        i = e["i"]; a = atr[i]; d = 1
        lvl = e["bhi"]; stop = e["blo"] - OB.FLOOR_ATR * a
        if abs(lvl - stop) < 0.5 * a: stop = lvl - 0.5 * a
        if fill == "frozen":
            k = limit_fill(P, e, lvl, d, i)
        else:
            k = None
            end = min(i + OB.RETEST_WIN, n - 1)
            for kk in range(i + 1, end + 1):
                if l[kk] <= lvl:            # resting limit triggers intrabar -- FILL
                    k = kk; break
                if c[kk] < e["blo"]:        # only an un-filled bar can invalidate
                    break
        if k is None: continue
        risk = abs(lvl - stop); room = (hi100[k] - lvl) / risk
        o = OB.retest_outcome(P, lvl, stop, d, k, tgtR, resolve_from=k)
        if o is None: continue
        H_ = hr[k]; sess = "AS" if H_ < 8 else ("LN" if H_ < 13 else ("NY" if H_ < 20 else "LT"))
        y = yr[k]; era = "D" if y <= 2018 else ("C" if y <= 2022 else "O")
        rows.append(dict(net=o["net_R"], g=o["gross_R"], risk=risk, room=max(room, 0), disp=e["disp"],
                         sess=sess, era=era, k=k, year=int(y), mfe=o["mfe_R"], mae=o["mae_R"],
                         cost_R=HC.COST_PRICE / risk, i=i))
    return rows


def M(rows):
    if len(rows) < 2: return dict(N=len(rows))
    net = np.array([r["net"] for r in rows]); g = np.array([r["g"] for r in rows])
    k = np.array([r["k"] for r in rows]); risk = np.array([r["risk"] for r in rows])
    eq = np.cumsum(net)
    ie = len(independent_episodes(k, H=OB.RETEST_WIN))
    return dict(N=len(net), ie=ie, net=float(net.mean()), gross=float(g.mean()),
                WR=float((g > 0).mean()), PF=float(g[g > 0].sum() / (abs(g[g < 0].sum()) + 1e-9)),
                medR=float(np.median(net)), maxDD=float((eq - np.maximum.accumulate(eq)).min()),
                bestrm=float((net.sum() - net.max()) / (len(net) - 1)),
                med_risk_pip=float(np.median(risk) / HC.PIP),
                med_cost_R=float(np.median([r["cost_R"] for r in rows])))


print("\n" + "=" * 96)
print("  SECTION 4 -- BASELINE REPRODUCTION  (frozen fill semantics, disp>=1.5, LN+NY, 2R)")
print("=" * 96)
rows_f = collect(fill="frozen")
lnny_f = [r for r in rows_f if r["sess"] in ("LN", "NY")]
mf = M(lnny_f)
claims = dict(N=2122, ie=954, net=0.154, WR=0.482, PF=1.86, bestrm=0.153)
for kk, vv in claims.items():
    got = mf[kk]
    ok = "MATCH" if abs(got - vv) <= max(0.004, abs(vv) * 0.02) else "DIFFER"
    print(f"    {kk:10} reproduced {got:>10.4f}   claimed {vv:>8}   {ok}")
print(f"    gross={mf['gross']:+.4f} medianR={mf['medR']:+.4f} maxDD={mf['maxDD']:.2f}R "
      f"median risk={mf['med_risk_pip']:.1f} pips  median cost_R={mf['med_cost_R']:.4f}")

print("\n" + "=" * 96)
print("  SECTION 2 -- ANTI-LOOKAHEAD: FILL-ORDERING AUDIT (the analogue of the depth artifact)")
print("=" * 96)
print("  ob_contrast.limit_fill, for a LONG, evaluates on the SAME bar k:")
print("      if c[k] < block_low: return None      <-- checked FIRST")
print("      if l[k] <= level:    return k")
print("  A resting limit BUY at block_high fills the instant low[k] <= block_high, regardless of where")
print("  bar k later CLOSES. Conditioning the fill on the bar's close is end-of-bar information.")
rows_c = collect(fill="causal")
lnny_c = [r for r in rows_c if r["sess"] in ("LN", "NY")]
mc = M(lnny_c)
print(f"\n    frozen fill semantics : N={mf['N']:4d} ie={mf['ie']:4d} net={mf['net']:+.4f} WR={mf['WR']:.3f} PF={mf['PF']:.2f}")
print(f"    causal fill semantics : N={mc['N']:4d} ie={mc['ie']:4d} net={mc['net']:+.4f} WR={mc['WR']:.3f} PF={mc['PF']:.2f}")
print(f"    delta N = {mc['N']-mf['N']:+d} trades     delta net-R = {mc['net']-mf['net']:+.4f}")
kf = set((r["i"], r["k"]) for r in lnny_f); kc = set((r["i"], r["k"]) for r in lnny_c)
addf = [r for r in lnny_c if (r["i"], r["k"]) not in kf]
if addf:
    an = np.array([r["net"] for r in addf])
    print(f"    trades the frozen semantics DROPS: n={len(addf)}  their net-R = {an.mean():+.4f}  "
          f"(win rate {(np.array([r['g'] for r in addf])>0).mean():.3f})")
json.dump(dict(spec_hash=SPEC_HASH, hashes=hs, frozen=mf, causal=mc,
               dropped_n=len(addf), dropped_net=float(np.mean([r["net"] for r in addf])) if addf else None),
          open(os.path.join(OUT, "run1.json"), "w"), indent=1)
pd.DataFrame(lnny_f).to_json(os.path.join(OUT, "rows_frozen.json"), orient="records")
pd.DataFrame(lnny_c).to_json(os.path.join(OUT, "rows_causal.json"), orient="records")
print("\n  persisted")
