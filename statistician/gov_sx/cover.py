import os,sys,numpy as np,pandas as pd
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; sys.path.insert(0,os.path.join(AA,"code"))
import mstrat
d=mstrat.load(); t=pd.to_datetime(d["time"],unit="s",utc=True)
print("="*114); print("  L2 — ACOPERIREA CONTEXTULUI in mstrat.load() (panoul folosit de screen)"); print("="*114)
for c in ("pdh","pdl","h4_trend_up","h1_trend_up","d1_trend_up"):
    nn=d[c].notna()
    print(f"  {c:14} non-null {nn.mean():.3f}   prima data non-null = {t[nn].min()}")
print(f"\n  => toate contextele HTF/PDH incep la aceeasi data; inainte de ea sunt NaN,")
print(f"     iar conditiile de setup care le folosesc sunt False -> zero semnale.")
print("\n"+"="*114); print("  FRECVENTA REALA DE TRANZACTIONARE (tpy raportat vs tpy efectiv)"); print("="*114)
YRS=(d['time'].iloc[-1]-d['time'].iloc[0])/(365.25*86400)
for hid,fam in (("85dfa65a9ce1","S1"),("047d776a1bcb","S9"),("601e20753a4a","S20")):
    tr=pd.read_csv(f"trades_{hid}.csv")
    ts=pd.to_datetime(d["time"].to_numpy()[tr.ei.to_numpy()],unit="s",utc=True)
    span=(ts.max()-ts.min()).total_seconds()/(365.25*86400)
    print(f"  {fam:4} {hid}  N={len(tr):4d}  tpy raportat (N/15.00) = {len(tr)/YRS:5.1f}"
          f"   tpy EFECTIV (N/{span:.2f} ani activi) = {len(tr)/span:5.1f}   factor {(len(tr)/span)/(len(tr)/YRS):.1f}x")
