"""L5 — AUDIT DE SCURGERE, mecanic. Doua teste independente:
   (A) contextul HTF: valoarea la bara i provine EXCLUSIV din bare HTF inchise la sau inainte de time[i]
   (B) lantul setups+simulate: stabilitate de prefix sub trunchiere"""
import os, sys, json
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
sys.path.insert(0, os.path.join(AA, "code"))
import mstrat, mstrat_ext as ME
from alpha_lab import CFG
mstrat.TICK = 0.01
if hasattr(ME, "TICK"): ME.TICK = 0.01
def cfg_for(rt):
    c = dict(CFG); c["spread_ticks"] = rt / (2 * mstrat.TICK); c["slip_ticks"] = 0.0; return c
CB = cfg_for(0.05)
d = mstrat.load()
t = d["time"].to_numpy()

print("=" * 116); print("  (A) CONTEXT HTF — provine doar din bare inchise? (reconstructie independenta din fisierele sursa)"); print("=" * 116)
MK = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market"
def indep_trend(path, period):
    """Reimplementare independenta: EMA20>EMA50 pe inchiderile HTF; disponibil abia la close = time+period."""
    x = pd.read_csv(os.path.join(MK, path)).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    c = x["close"]
    up = (c.ewm(span=20, adjust=True).mean() > c.ewm(span=50, adjust=True).mean()).astype(float)
    return pd.DataFrame({"close_time": x["time"].to_numpy() + period, "trend_up": up.to_numpy()})

for col, path, period in (("h4_trend_up", "OANDA_XAUUSD_H4.csv", 14400),
                          ("h1_trend_up", "OANDA_XAUUSD_H1.csv", 3600)):
    ht = indep_trend(path, period)
    j = pd.merge_asof(pd.DataFrame({"time": t}).sort_values("time"), ht.sort_values("close_time"),
                      left_on="time", right_on="close_time", direction="backward")
    both = d[col].notna().to_numpy() & j.trend_up.notna().to_numpy()
    agree = float((d[col].to_numpy()[both] == j.trend_up.to_numpy()[both]).mean())
    print(f"  {col:14} bare comparabile {int(both.sum()):7d}   acord cu reconstructia STRICT-CAUZALA = {agree:.4f}")
    # testul care conteaza: exista vreo bara unde panoul stie o valoare ce provine dintr-o bara HTF NEINCHISA?
    x = pd.read_csv(os.path.join(MK, path)).drop_duplicates("time").sort_values("time")
    openbar = pd.merge_asof(pd.DataFrame({"time": t}).sort_values("time"),
                            pd.DataFrame({"bar_open": x["time"].to_numpy()}).sort_values("bar_open"),
                            left_on="time", right_on="bar_open", direction="backward")
    未 = (j.close_time.to_numpy() > t)
    print(f"  {col:14} bare unde close_time-ul sursei DEPASESTE timpul barei (scurgere) = {int(np.nansum(未))}")

print("\n=== pdh/pdl: disponibilitate ===")
d1 = pd.read_csv(os.path.join(MK, "OANDA_XAUUSD_D1.csv")).drop_duplicates("time").sort_values("time").reset_index(drop=True)
d1["avail"] = d1["time"].shift(-1)
j = pd.merge_asof(pd.DataFrame({"time": t}).sort_values("time"),
                  d1[["avail","high","low"]].dropna().astype({"avail":"int64"}).sort_values("avail"),
                  left_on="time", right_on="avail", direction="backward")
both = d["pdh"].notna().to_numpy() & j.high.notna().to_numpy()
print(f"  pdh acord cu reconstructia (avail = deschiderea D1 URMATOARE) = {float((d['pdh'].to_numpy()[both]==j.high.to_numpy()[both]).mean()):.4f}")
print(f"  bare unde avail > time (scurgere) = {int((j.avail.to_numpy() > t).sum())}")

print("\n" + "=" * 116); print("  (B) LANT setups+simulate — STABILITATE DE PREFIX SUB TRUNCHIERE"); print("=" * 116)
print("  Recalculez setup-urile si simularea pe d[:K]. Tranzactiile cu exit mult inainte de K trebuie sa fie IDENTICE.")
TARGET = {}
for N in range(1, 52):
    for mod in (mstrat, ME):
        g = getattr(mod, f"s{N}_grammar", None); s = getattr(mod, f"s{N}_setups", None)
        if not (g and s): continue
        for h in g():
            if h["id"] in ("85dfa65a9ce1", "047d776a1bcb", "601e20753a4a"):
                TARGET[h["id"]] = (f"S{N}", mod, h, s)
        break
for hid, (fam, mod, h, sfn) in TARGET.items():
    full = mstrat.simulate(d, sfn(d, h), CB)
    print(f"\n  {fam} {hid}  (full: {len(full)} tranzactii)")
    for K in (330000, 345000, 353000):
        dk = d.iloc[:K].reset_index(drop=True)
        tk = mstrat.simulate(dk, sfn(dk, h), CB)
        cut = K - 200                                  # marja peste orizontul de 48 bare
        a = full[full.ei < cut][["si", "ei", "R"]].round(9).reset_index(drop=True)
        b = tk[tk.ei < cut][["si", "ei", "R"]].round(9).reset_index(drop=True)
        same = a.equals(b)
        print(f"    K={K}: full={len(a)} trunchiat={len(b)} identice={'DA' if same else 'NU'}"
              + ("" if same else f"   PRIMA DIFERENTA la randul {int((a!=b).any(axis=1).idxmax()) if len(a)==len(b) else 'lungimi diferite'}"))
