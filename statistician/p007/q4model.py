"""Q4-ONLY formalization of the apprenticeship lesson. Mechanical round-trip / volume / fresh-extreme
computed from bars using the ledger's own TRIGGER_BAR / RESOLUTION_BAR. Q1 2021 is NOT opened."""
import sys, os, io, re, json, math, csv
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
RM = r"C:\Users\MEDION GAMING\ai_quant_lab-research-main"
T = r"C:\Users\MEDION~1\AppData\Local\Temp\p7"
FIX = os.path.join(RM, "ai_trader", "csv_causal_replay", "fixtures", "data", "Q4_SEALED_1_5932.csv")

raw = list(csv.reader(open(FIX)))[1:]
ts = np.array([int(float(r[0])) for r in raw]); o = np.array([float(r[1]) for r in raw])
hi = np.array([float(r[2]) for r in raw]); lo = np.array([float(r[3]) for r in raw])
cl = np.array([float(r[4]) for r in raw]); vol = np.array([float(r[5]) for r in raw])
Q4_START_TS = 1601510400
q4i = np.where(ts >= Q4_START_TS)[0]
base = q4i[0]                       # Q4 bar index 1 == array position `base`
def A(q4bar): return base + int(q4bar) - 1
print(f"  bars {len(raw)}   Q4 bar 1 at array pos {base}   Q4 bars {len(q4i)}")

L = pd.read_csv(os.path.join(T, "ledger.csv"))
L = L.dropna(subset=["trigger_bar", "label"]).copy()
L["trigger_bar"] = L.trigger_bar.astype(int)
print(f"  ledger episodes usable: {len(L)}  ({L.label.value_counts().to_dict()})")

rows = []
for _, r in L.iterrows():
    tb = A(r.trigger_bar)
    rb = A(int(r.resolution_bar)) if pd.notna(r.resolution_bar) else None
    if tb <= base or tb >= len(raw): continue
    if rb is None or rb <= tb or rb >= len(raw):
        rows.append(dict(id=r.id, label=r.label, ok=False)); continue
    pre = cl[tb - 1]                       # level the decline started from (bar before trigger)
    seg_lo = lo[tb:rb + 1]
    deep = float(seg_lo.min())
    decline = pre - deep
    reclaim = cl[rb]
    rt = (reclaim - deep) / decline if decline > 1e-9 else np.nan      # round-trip completeness
    dur = rb - tb + 1
    v_ep = vol[tb:rb + 1]
    v_base = vol[max(0, tb - 96):tb].mean()
    v_peak = float(v_ep.max())
    v_sust = float((v_ep > 1.25 * v_base).mean()) if v_base > 0 else np.nan   # share of episode bars elevated
    v_iso = (v_peak / max(v_ep.mean(), 1e-9))
    fresh = float(deep < lo[max(0, tb - 96):tb].min())                 # fresh 24h extreme
    rows.append(dict(id=r.id, label=r.label, ok=True, trigger=tb, res=rb, dur=dur,
                     pre=pre, deep=deep, decline=decline, reclaim=reclaim,
                     round_trip=rt, vol_sustain=v_sust, vol_isolation=v_iso, fresh_extreme=fresh))
D = pd.DataFrame(rows)
G = D[D.ok].copy()
print(f"  episodes with a computable round-trip: {len(G)} of {len(D)}   "
      f"({G.label.value_counts().to_dict()})")
print(f"  dropped (no RESOLUTION_BAR or bad index): {list(D[~D.ok].id)}")

print("\n" + "=" * 100); print("  §6-§8  DOES THE LESSON SEPARATE, MECHANICALLY, IN-SAMPLE ON Q4?"); print("=" * 100)
sup = G[G.label == "SUPPORT"]; rej = G[G.label == "REJECTED"]
for nm in ("round_trip", "vol_sustain", "vol_isolation", "fresh_extreme", "dur", "decline"):
    a, b = sup[nm].dropna(), rej[nm].dropna()
    if len(a) < 5 or len(b) < 5: continue
    # Mann-Whitney U -> AUC, the natural separation measure for a 24/65 split
    comb = np.concatenate([a, b]); rk = pd.Series(comb).rank().to_numpy()
    ra = rk[:len(a)].sum(); U = ra - len(a) * (len(a) + 1) / 2
    auc = U / (len(a) * len(b))
    print(f"    {nm:15} SUPPORT median {np.median(a):8.3f}  REJECTED median {np.median(b):8.3f}   AUC {auc:.3f}")

print("\n  AUC 0.50 = no separation. AUC < 0.50 means the SUPPORT group sits LOWER on that quantity.")
print("  The apprenticeship lesson predicts round_trip AUC well BELOW 0.50 (SUPPORT = partial round-trip).")
G.to_csv(os.path.join(T, "q4_episodes.csv"), index=False)
json.dump(dict(n=len(G), sup=int((G.label == "SUPPORT").sum())), open(os.path.join(T, "q4model.json"), "w"))
