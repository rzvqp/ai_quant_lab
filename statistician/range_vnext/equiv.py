"""Section 7/8 -- full-history equivalence pre-fix (bba6310) vs post-fix (fa36324), plus the age gate."""
from __future__ import annotations
import json, os, sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
PRE = r"C:\Users\MEDION~1\AppData\Local\Temp\vnext"
POST = r"C:\Users\MEDION~1\AppData\Local\Temp\vnext2"

a = json.load(open(os.path.join(PRE, "metrics_vnext.json")))
b = json.load(open(os.path.join(POST, "metrics_vnext.json")))

print("=" * 90)
print("SECTION 7 -- FULL-HISTORY EQUIVALENCE  (355,696 M15 bars, canonical warmup from the first bar)")
print("=" * 90)
print(f"  {'metric':44} {'PRE-FIX bba6310':>17} {'POST-FIX fa36324':>18}  ")
rows = [
    ("bars", a["bars"], b["bars"]),
    ("confirmed bars total", a["confirmed_bars_total"], b["confirmed_bars_total"]),
    ("genuine confirmations (OK_RANGE_MACRO)", a["ok_range_macro_events"], b["ok_range_macro_events"]),
    ("canonical confirmed id transitions", a["canonical_confirmed_id_transitions"],
     b["canonical_confirmed_id_transitions"]),
]
ea, eb = a["event_totals_by_depth"], b["event_totals_by_depth"]
for k in ("EPISODE_REPLACEMENT|MACRO", "EPISODE_CONTINUATION|MACRO", "EPISODE_MERGED|MACRO",
          "CANDIDATE_SUPERSEDED_BY_MERGE|MACRO", "CANDIDATE_ABANDONED_PRICE_MOVED_ON|MACRO",
          "REGISTRY_CAPACITY_REFUSED|MACRO", "OK_RANGE_MACRO|MACRO", "ZONES_DEGENERATE|MACRO",
          "BREAKOUT_ACCEPTED|MACRO", "RANGE_CANDIDATE_PRESENT|MACRO", "RANGE_WEAKENING|MACRO",
          "IS_TREND_MACRO|MACRO", "ZONES_INVERTED|MACRO", "WEAKENING_RECOVERED|MACRO"):
    rows.append((k, ea.get(k, 0), eb.get(k, 0)))
births_a = ea.get("EPISODE_REPLACEMENT|MACRO", 0) + ea.get("EPISODE_MERGED|MACRO", 0) + ea.get("EPISODE_CONTINUATION|MACRO", 0)
births_b = eb.get("EPISODE_REPLACEMENT|MACRO", 0) + eb.get("EPISODE_MERGED|MACRO", 0) + eb.get("EPISODE_CONTINUATION|MACRO", 0)
rows.append(("--> macro candidate BIRTHS", births_a, births_b))
drift = 0
for nm, x, y in rows:
    ok = "IDENTICAL" if x == y else "*** DRIFT ***"
    if x != y:
        drift += 1
    print(f"  {nm:44} {x:>17} {y:>18}  {ok}")

print("\n  per-year confirmed bars:")
ya, yb = a["confirmed_bars_by_year"], b["confirmed_bars_by_year"]
yrs = sorted(set(list(ya) + list(yb)), key=int)
for y in yrs:
    x, z = ya.get(y, 0), yb.get(y, 0)
    if x != z:
        drift += 1
    print(f"    {y}: pre={x:6d}  post={z:6d}  {'IDENTICAL' if x == z else '*** DRIFT ***'}")

print("\n  registry occupancy distribution:")
oa, ob = a["registry_occupancy"], b["registry_occupancy"]
for k in sorted(set(list(oa) + list(ob))):
    x, z = oa.get(k), ob.get(k)
    if x != z:
        drift += 1
    print(f"    {k:22} pre={str(x):>8}  post={str(z):>8}  {'IDENTICAL' if x == z else '*** DRIFT ***'}")

print("\n  ALL event kinds compared (both depths, full set):")
allk = sorted(set(list(ea) + list(eb)))
ediff = [(k, ea.get(k, 0), eb.get(k, 0)) for k in allk if ea.get(k, 0) != eb.get(k, 0)]
print(f"    distinct event kinds: pre={len(ea)} post={len(eb)}  differing: {len(ediff)}")
for k, x, z in ediff:
    print(f"      *** {k}: pre={x} post={z}")
drift += len(ediff)

print(f"\n  TOTAL DRIFTING FIELDS: {drift}")
print(f"  VERDICT: {'ZERO HISTORICAL SEMANTIC DRIFT' if drift == 0 else 'DRIFT DETECTED -- REVALIDATION FAIL'}")

print()
print("=" * 90)
print("SECTION 8 -- AGE GATE (frozen d_macro = 29), post-fix, per structure")
print("=" * 90)
Sp = json.load(open(os.path.join(PRE, "S_vnext.json")))
Sq = json.load(open(os.path.join(POST, "S_vnext.json")))


def f(x):
    try:
        return None if x in (None, "None", "") else float(x)
    except Exception:
        return None


def ages(S):
    out = []
    for r in S:
        c, s = f(r.get("conf")), f(r.get("start"))
        if r.get("confirmed") and c is not None and s is not None:
            out.append(c - s)
    return np.array(out)


for nm, S in (("PRE-FIX  bba6310", Sp), ("POST-FIX fa36324", Sq)):
    ag = ages(S)
    print(f"  {nm}: structures={len(S):6d}  confirmed={len(ag):5d}  min={ag.min():.0f}  median={np.median(ag):.0f}"
          f"  max={ag.max():.0f}  BELOW GATE (<29): {int((ag < 29).sum())}")
mc = [r for r in Sq if r.get("confirmed") and r.get("cont") not in (None, "None")]
agm = np.array([f(r["conf"]) - f(r["start"]) for r in mc if f(r.get("conf")) is not None and f(r.get("start")) is not None])
print(f"  POST-FIX merge/continuation-born confirmations: n={len(agm)}  min_age={agm.min():.0f}  below_gate={int((agm < 29).sum())}")
idp = sorted((r["sid"], f(r.get("conf")), f(r.get("start"))) for r in Sp if r.get("confirmed"))
idq = sorted((r["sid"], f(r.get("conf")), f(r.get("start"))) for r in Sq if r.get("confirmed"))
print(f"\n  confirmed-structure sets identical pre vs post (id, confirm_ts, start_ts): {idp == idq}")
print(f"  capacity-refusal events post-fix: {eb.get('REGISTRY_CAPACITY_REFUSED|MACRO', 0)}"
      f"  (cap=16 vs historical max active {ob.get('max')} -> newly-covered path never fires on this dataset)")

json.dump(dict(mandate="STAT-RANGE-VNEXT-HARD-CAP-REVALIDATION-001",
               drifting_fields=drift,
               pre_fix_commit="bba6310", post_fix_commit="fa36324",
               metrics_pre=a, metrics_post=b,
               confirmed_structure_sets_identical=(idp == idq),
               age_gate_below_post=int((ages(Sq) < 29).sum())),
          open(os.path.join(POST, "STAT_RANGE_VNEXT_HARDCAP_EQUIVALENCE.json"), "w"), indent=1, default=str)
