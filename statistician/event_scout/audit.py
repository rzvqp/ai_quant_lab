import json, glob, os, sys, hashlib
import pandas as pd, numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
CAL = r"C:\Users\MEDION GAMING\ai_quant_lab-data-acq\acquisition_staging\calendar"
NEWS = r"C:\Users\MEDION GAMING\ai_quant_lab-data-acq\acquisition_staging\news\NEWS_LEDGER.csv"
M5   = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M5.csv"

print("="*100); print("  SCHEDULED_EVENT_RESPONSE_SCOUT_V1 -- SECTION 1 DATA AUDIT"); print("="*100)

# ---------- 1. fields, every format ----------
print("\n-- FIELDS PRESENT (verified per format, not per prose) --")
j = json.load(open(os.path.join(CAL,"ff_calendar_2026-W32_raw.json"), encoding="utf-8"))
jk = sorted({k for r in j for k in r})
print("  JSON raw      :", jk, f"({len(j)} records)")
craw = pd.read_csv(os.path.join(CAL,"ff_calendar_2026-W32_raw.csv"))
print("  CSV raw       :", list(craw.columns))
norm = pd.read_csv(os.path.join(CAL,"ff_calendar_2026-W32_UTC.csv"))
print("  CSV normalized:", list(norm.columns))
cap = pd.read_csv(sorted(glob.glob(os.path.join(CAL,"captures","*","ff_calendar_thisweek.csv")))[0])
print("  capture CSV   :", list(cap.columns))
for f in ("actual","Actual","revision","Revision","revised","surprise"):
    hit = (f in jk) or (f in craw.columns) or (f in norm.columns) or (f in cap.columns)
    print(f"    field '{f}': {'PRESENT' if hit else 'ABSENT'}")

# ---------- 2. timezone: verify the JSON<->CSV reconciliation myself ----------
print("\n-- TIMEZONE (independently reconciled, not taken from the acquisition report) --")
jt = pd.to_datetime(pd.Series([r["date"] for r in j]), utc=True, format="ISO8601")
offs = sorted({r["date"][-6:] for r in j})
ct = pd.to_datetime(craw["Date"]+" "+craw["Time"], format="%m-%d-%Y %I:%M%p", errors="coerce", utc=True)
pair = pd.DataFrame({"j":jt.values, "c":ct.values, "tj":[r["title"] for r in j], "tc":craw["Title"].values})
mis = int((pair.j != pair.c).sum())
print(f"  JSON offsets present         : {offs}  (offset-aware, per record)")
print(f"  JSON->UTC vs CSV timestamps  : {len(pair)-mis}/{len(pair)} identical, {mis} mismatch")
print(f"  timestamp precision          : minute (seconds always 00: {bool((jt.dt.second==0).all())})")
print(f"  DST                          : offset is explicit per record; only EDT (-04:00) observed -- no winter week exists to test")

# ---------- 3. coverage ----------
print("\n-- COVERAGE --")
rows=[]
n = norm.copy(); n["dt"]=pd.to_datetime(n.datetime_utc, utc=True)
n = n.rename(columns={"event":"Title","currency":"Country","impact":"Impact","forecast":"Forecast","previous":"Previous"})
n["src"]="ff_calendar_2026-W32_UTC.csv"; rows.append(n[["dt","Title","Country","Impact","Forecast","Previous","src"]])
for f in sorted(glob.glob(os.path.join(CAL,"captures","*","ff_calendar_thisweek.csv"))):
    d=pd.read_csv(f); d["dt"]=pd.to_datetime(d.Date+" "+d.Time, format="%m-%d-%Y %I:%M%p", errors="coerce", utc=True)
    d["src"]=os.path.basename(os.path.dirname(f)); rows.append(d[["dt","Title","Country","Impact","Forecast","Previous","src"]])
E = pd.concat(rows, ignore_index=True).sort_values("dt").reset_index(drop=True)
print(f"  calendar snapshots           : {len(rows)} weekly 'thisweek' pulls")
print(f"  total event rows             : {len(E)}")
print(f"  calendar date range          : {E.dt.min()}  ->  {E.dt.max()}   ({(E.dt.max()-E.dt.min()).days} days)")
print(f"  unresolved timestamps        : {int(E.dt.isna().sum())}")
dup = E.duplicated(["dt","Title","Country"]).sum()
print(f"  duplicate (dt,title,country) : {int(dup)}")
print(f"  impact distribution          : {E.Impact.value_counts().to_dict()}")
print(f"  currency top                 : {E.Country.value_counts().head(6).to_dict()}")
print(f"  missing forecast             : {int(E.Forecast.isna().sum())}/{len(E)}  ({E.Forecast.isna().mean():.0%})")
print(f"  missing previous             : {int(E.Previous.isna().sum())}/{len(E)}  ({E.Previous.isna().mean():.0%})")
hi = E[(E.Country=="USD") & (E.Impact.isin(["High","Medium"]))]
print(f"  USD High+Medium events       : {len(hi)}  over {(E.dt.max()-E.dt.min()).days} days")

# ---------- 4. simultaneity (S11) ----------
g = E.groupby("dt").size()
print(f"\n-- SIMULTANEITY (mandate S11) --")
print(f"  distinct timestamps          : {len(g)}")
print(f"  timestamps with >1 release   : {int((g>1).sum())}  ({(g>1).mean():.0%})")
print(f"  max releases at one timestamp: {int(g.max())}")

# ---------- 5. THE OVERLAP TEST ----------
print("\n"+"="*100); print("  THE DECIDING TEST -- OVERLAP WITH GOVERNED XAU PRICE DATA"); print("="*100)
import subprocess
prices = {}
for f in sorted(glob.glob(r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\*.csv")):
    d = pd.read_csv(f, usecols=[0]); c=d.columns[0]
    t = pd.to_datetime(d[c], unit="s", utc=True) if pd.api.types.is_numeric_dtype(d[c]) else pd.to_datetime(d[c], utc=True, errors="coerce")
    prices[os.path.basename(f)] = (t.min(), t.max(), len(d))
ev_min, ev_max = E.dt.min(), E.dt.max()
print(f"  event population span : {ev_min} -> {ev_max}\n")
print(f"  {'governed price file':<62} {'last bar':<26} events inside")
for k,(a,b,nn) in prices.items():
    inside = int(((E.dt>=a) & (E.dt<=b)).sum())
    print(f"  {k:<62} {str(b):<26} {inside}")
tot_overlap = 0
for k,(a,b,nn) in prices.items():
    tot_overlap = max(tot_overlap, int(((E.dt>=a)&(E.dt<=b)).sum()))
gap = (ev_min - max(b for _,b,_ in prices.values()))
print(f"\n  MAXIMUM events falling inside ANY governed XAU price series : {tot_overlap}")
print(f"  gap between last governed bar and first captured event      : {gap}")

nl = pd.read_csv(NEWS); nt = pd.to_datetime(nl.deduced_ts_utc, utc=True, errors="coerce")
print(f"\n  (unscheduled NEWS_LEDGER, for completeness: {len(nl)} items, {nt.min()} -> {nt.max()}, "
      f"events inside M5: {int(((nt>=prices['OANDA_XAUUSD_M5.csv'][0])&(nt<=prices['OANDA_XAUUSD_M5.csv'][1])).sum())})")

E.to_csv("event_population.csv", index=False)
print("\n  wrote event_population.csv")
