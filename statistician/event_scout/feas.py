import sys, os, math
import pandas as pd, numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
sys.path.insert(0, AD); os.chdir(AD)
import m5_data

E = pd.read_csv(r"C:\Users\MEDION~1\AppData\Local\Temp\evt\event_population.csv", parse_dates=["dt"])
print("="*100); print("  FEASIBILITY ARITHMETIC (NOT a hypothesis test -- zero tests run, no DEV/OOS consumed)"); print("="*100)

# ---- independent EVENT_EPISODE rate (mandate S11 definition applied) ----
def episodes(sub, gap_min=30):
    t = np.sort(sub.dt.values.astype("datetime64[s]").astype(np.int64))
    if len(t)==0: return 0
    return 1 + int((np.diff(t) > gap_min*60).sum())
span_days = (E.dt.max()-E.dt.min()).days
print(f"\n-- independent EVENT_EPISODE rate (releases within 30 min collapsed to one episode) --")
print(f"   observation span: {span_days} days ({span_days/7:.1f} weeks)\n")
fams = {
  "USD High":                E[(E.Country=="USD")&(E.Impact=="High")],
  "USD High+Medium":         E[(E.Country=="USD")&(E.Impact.isin(["High","Medium"]))],
  "any-currency High":       E[E.Impact=="High"],
  "USD employment-family":   E[(E.Country=="USD")&E.Title.str.contains("Employment|Payroll|Unemploy|Hourly|Claims|ADP",case=False,na=False)],
  "USD inflation-family":    E[(E.Country=="USD")&E.Title.str.contains("CPI|PPI|PCE|Inflation",case=False,na=False)],
  "FOMC/central-bank":       E[E.Title.str.contains("FOMC|Rate|Powell|Fed |Minutes",case=False,na=False)],
}
rate={}
for k,v in fams.items():
    ep = episodes(v); rate[k]=ep/span_days*7
    print(f"   {k:<26} rows={len(v):4d}  episodes={ep:3d}  -> {rate[k]:5.2f} episodes/week")

# ---- variance scale of the Scout-V2 timing target, from already-consumed price data ----
m = m5_data.load_m5()
h=m["high"].to_numpy(float); l=m["low"].to_numpy(float); c=m["close"].to_numpy(float); n=len(m)
PIP=0.10; H=288
U=c+100*PIP; D=c-80*PIP
hu=np.full(n,np.inf); hd=np.full(n,np.inf)
for j in range(1,H+1):
    hj=np.concatenate([h[j:],np.full(j,np.nan)]); lj=np.concatenate([l[j:],np.full(j,np.nan)])
    hu=np.where((hj>=U)&np.isinf(hu),j,hu); hd=np.where((lj<=D)&np.isinf(hd),j,hd)
first=np.minimum(hu,hd); first=np.where(np.isinf(first),H,first)   # censored -> capped at horizon (documented)
tt=first*5/60.0
mu,sd=tt.mean(),tt.std(ddof=1)
print(f"\n-- variance scale of 'time to first +-100p' (M5, capped at 24h; DESCRIPTIVE, not a test) --")
print(f"   mean {mu:.2f} h   sd {sd:.2f} h   censored-at-cap share {np.mean(first>=H):.1%}")

print(f"\n-- episodes required to DETECT an event effect of a given size (two-sided, alpha .05 / 80% power) --")
print(f"   assumes episodes are independent draws with the marginal sd above; treatment vs a large matched control")
print(f"   {'effect (hours on time-to-+-100p)':<36} {'N episodes':>12} {'weeks of USD High+Med capture':>32}")
for eff in (2.0, 1.5, 1.0, 0.9, 0.5):
    N = math.ceil(2*(1.96+0.8416)**2 * (sd/eff)**2 / 2)   # one-sample-vs-large-control: (z*sd/eff)^2
    N = math.ceil(((1.96+0.8416)*sd/eff)**2)
    wk = N/rate["USD High+Medium"]
    print(f"   {eff:>5.1f} h  ({eff/mu*100:4.1f}% of the {mu:.1f}h base){'':<8} {N:>12d} {wk:>32.0f}")
print(f"\n   with Bonferroni at m=60 (the mandate's own budget) the z rises 1.96 -> 3.02:")
for eff in (1.5, 1.0, 0.9):
    N = math.ceil(((3.02+0.8416)*sd/eff)**2); wk=N/rate["USD High+Medium"]
    print(f"   {eff:>5.1f} h  -> N={N}, {wk:.0f} weeks ({wk/52:.1f} years) at the current capture cadence")
