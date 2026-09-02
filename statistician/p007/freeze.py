"""Q4-only model selection (bounded, all alternatives reported), freeze + hash, and Q1-2021 population
scoping. Q1 OUTCOMES ARE NOT OPENED -- none exist."""
import sys, os, io, json, csv, hashlib, math
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = r"C:\Users\MEDION~1\AppData\Local\Temp\p7"
G = pd.read_csv(os.path.join(T, "q4_episodes.csv"))
X = pd.read_csv(os.path.join(T, "q4_trigger_features.csv"))
M = G.merge(X[["id", "t_vol_rel_3", "t_bar_range_atr"]], on="id")
y = (M.label == "SUPPORT").to_numpy()

def metrics(pred, y):
    tp = int((pred & y).sum()); fp = int((pred & ~y).sum())
    fn = int((~pred & y).sum()); tn = int((~pred & ~y).sum())
    rec = tp / max(tp + fn, 1); spec = tn / max(tn + fp, 1)
    prec = tp / max(tp + fp, 1)
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, precision=prec, recall=rec,
                specificity=spec, balacc=(rec + spec) / 2)

print("=" * 104); print("  §6/§9  BOUNDED SPECIFICATION SEARCH ON Q4 -- every alternative reported"); print("=" * 104)
print(f"  Q4 episodes with computable features: {len(M)}  ({int(y.sum())} SUPPORT / {int((~y).sum())} REJECTED)")
print(f"\n  A. ROUND_TRIP_ONLY  (primary concept named by the mandate)   rule: round_trip < th -> SUPPORT")
best_a = None
for th in (0.80, 0.85, 0.90, 0.95, 1.00):
    m = metrics(M.round_trip.to_numpy() < th, y)
    print(f"     th={th:.2f}  prec {m['precision']:.3f}  rec {m['recall']:.3f}  spec {m['specificity']:.3f}  balacc {m['balacc']:.3f}")
    if best_a is None or m["balacc"] > best_a[1]["balacc"]: best_a = (th, m)
print(f"     -> best {best_a[0]:.2f}, balanced accuracy {best_a[1]['balacc']:.3f}")

print(f"\n  B. ROUND_TRIP + VOLUME_PERSISTENCE (does volume add? -- mandate §7)")
best_b = None
for th in (0.85, 0.90, 0.95):
    for vt in (0.10, 0.20):
        m = metrics((M.round_trip.to_numpy() < th) & (M.vol_sustain.to_numpy() > vt), y)
        print(f"     rt<{th:.2f} & vol_sustain>{vt:.2f}   prec {m['precision']:.3f}  rec {m['recall']:.3f}  "
              f"spec {m['specificity']:.3f}  balacc {m['balacc']:.3f}")
        if best_b is None or m["balacc"] > best_b[2]["balacc"]: best_b = (th, vt, m)
print(f"     -> best balanced accuracy {best_b[2]['balacc']:.3f}   INCREMENTAL vs A: {best_b[2]['balacc']-best_a[1]['balacc']:+.3f}")

print(f"\n  C. + FRESH_EXTREME (does it add after round-trip and volume? -- mandate §8)")
m_c = metrics((M.round_trip.to_numpy() < best_b[0]) & (M.vol_sustain.to_numpy() > best_b[1]) &
              (M.fresh_extreme.to_numpy() > 0.5), y)
print(f"     prec {m_c['precision']:.3f}  rec {m_c['recall']:.3f}  spec {m_c['specificity']:.3f}  balacc {m_c['balacc']:.3f}")
print(f"     -> INCREMENTAL vs B: {m_c['balacc']-best_b[2]['balacc']:+.3f}")

print(f"\n  D. AT_TRIGGER-ONLY volume rule (the only genuinely PROSPECTIVE option)   t_vol_rel_3 > th -> SUPPORT")
best_d = None
for th in (1.2, 1.5, 1.8, 2.0):
    m = metrics(M.t_vol_rel_3.to_numpy() > th, y)
    print(f"     th={th:.1f}   prec {m['precision']:.3f}  rec {m['recall']:.3f}  spec {m['specificity']:.3f}  balacc {m['balacc']:.3f}")
    if best_d is None or m["balacc"] > best_d[1]["balacc"]: best_d = (th, m)
print(f"     -> best {best_d[0]:.1f}, balanced accuracy {best_d[1]['balacc']:.3f}")

print(f"\n  TRIVIAL BASELINES")
b0 = metrics(np.zeros(len(y), bool), y)
print(f"     ALWAYS_REJECTED : balacc {b0['balacc']:.3f}   (accuracy {int((~y).sum())}/{len(y)} = {(~y).mean():.3f})")
print(f"     BASELINE_BALANCED_ACCURACY = 0.500 for any constant or random-with-matched-rate rule")

SPEC = dict(
  name="P007_DISCRIMINATOR_SPEC_V1",
  primary=dict(id="ROUND_TRIP_ONLY", rule=f"round_trip < {best_a[0]:.2f} -> SUPPORT else REJECTED",
    round_trip_definition="(reclaim_close - deepest_low_of_episode) / (close_of_bar_before_trigger - deepest_low_of_episode)",
    earliest_causal_classification_time="AT_RECLAIM (resolution). Requires the episode's deepest low AND "
      "the reclaim close; neither exists until the episode ends.",
    q4_balanced_accuracy=round(best_a[1]["balacc"], 4)),
  secondary_1=dict(id="ROUND_TRIP_PLUS_VOLUME",
    rule=f"round_trip < {best_b[0]:.2f} AND vol_sustain > {best_b[1]:.2f} -> SUPPORT",
    earliest_causal_classification_time="AT_RECLAIM",
    q4_balanced_accuracy=round(best_b[2]["balacc"], 4)),
  secondary_2=dict(id="AT_TRIGGER_VOLUME_ONLY", rule=f"t_vol_rel_3 > {best_d[0]:.1f} -> SUPPORT",
    definition="mean volume of the trigger bar and the two bars before it, divided by the mean volume of "
               "the 96 bars strictly before the trigger",
    earliest_causal_classification_time="AT_TRIGGER",
    q4_balanced_accuracy=round(best_d[1]["balacc"], 4)),
  population_rule="the P007 episode registry as curated in AI_TRADER_Q4_PATTERN_LEDGER.md; the frozen "
                  "mechanical detector is OVER-INCLUSIVE and does NOT reproduce it (121 vs 89 on Q4)",
  scoring="balanced accuracy = (recall_SUPPORT + specificity_REJECTED)/2; baseline 0.500",
  alternatives_considered=dict(round_trip_thresholds=[0.80, 0.85, 0.90, 0.95, 1.00],
                               volume_thresholds=[0.10, 0.20], trigger_vol_thresholds=[1.2, 1.5, 1.8, 2.0]),
  frozen_on="Q4 2020 only; Q1 2021 outcomes were never opened and none exist")
p = os.path.join(T, "P007_DISCRIMINATOR_SPEC_V1.json")
json.dump(SPEC, open(p, "w"), indent=1)
H = hashlib.sha256(open(p, "rb").read()).hexdigest()
print(f"\n  SPEC_HASH_PRE_Q1 = {H}")

print("\n" + "=" * 104); print("  Q1 2021 SCOPING -- population only. NO outcome, NO label, NO score."); print("=" * 104)
MK = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M15.csv"
d = pd.read_csv(MK).drop_duplicates("time").sort_values("time")
t = pd.to_datetime(d["time"], unit="s", utc=True)
q1 = d[(t >= "2021-01-01") & (t < "2021-04-01")]
print(f"  governed M15 bars in Q1 2021 : {len(q1)}   {pd.to_datetime(q1['time'].min(),unit='s',utc=True)} -> "
      f"{pd.to_datetime(q1['time'].max(),unit='s',utc=True)}")
print(f"  sealed Q4 replay fixtures end at bar 5932 = 2020-12-31 21:45 UTC -> NO Q1 2021 sealed fixture exists")
print(f"  Q1 2021 P007 LABELS (SUPPORT/REJECTED) existing anywhere in the lab : 0")
json.dump(dict(spec_hash=H, q1_bars=int(len(q1)),
               best_a=best_a[0], balacc_a=best_a[1]["balacc"],
               balacc_b=best_b[2]["balacc"], balacc_c=m_c["balacc"],
               best_d=best_d[0], balacc_d=best_d[1]["balacc"]),
          open(os.path.join(T, "freeze.json"), "w"), indent=1)
