import pandas as pd, numpy as np, sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
a=pd.read_csv(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\GOV_SCREEN_ALL_RESULTS.csv")
print("="*112); print("  L1 — CATE IPOTEZE DISTINCTE EXISTA DE FAPT IN GRAMATICA?"); print("="*112)
print(f"  configuratii scorate (>=100 tranzactii) : {len(a)}")
sig=["family","N","WR","BASE","STRESS","PF","maxDD","db5","era1","era2","era3"]
a["sig"]=a[sig].astype(str).agg("|".join,axis=1)
g=a.groupby("sig").size()
print(f"  semnaturi de rezultat DISTINCTE          : {a.sig.nunique()}")
print(f"  configuratii care sunt duplicate exacte  : {len(a)-a.sig.nunique()}  ({(len(a)-a.sig.nunique())/len(a):.1%})")
print(f"  distributia marimii grupurilor de duplicate: {g.value_counts().sort_index().to_dict()}")
s=a[a.SURVIVE]
print(f"\n  supravietuitori raportati                : {len(s)}")
print(f"  supravietuitori DISTINCTI                : {s.sig.nunique()}")
for hid in ("85dfa65a9ce1","047d776a1bcb","601e20753a4a"):
    row=a[a.hid.str.contains(hid)]
    if len(row):
        twins=a[a.sig==row.sig.iloc[0]]
        print(f"    {hid}: {len(twins)} configuratii cu rezultat IDENTIC -> {[x.split('/id=')[0].split('::')[1] for x in twins.hid]}")
print("\n"+"="*112); print("  S49 — verific independent respingerea Alpha"); print("="*112)
s49=a[a.family=="S49"].sort_values("BASE",ascending=False)
print(s49[["hid","N","tpy","WR","BASE","STRESS","PF","db5","SURVIVE"]].head(8).to_string(index=False))
print(f"\n  N=68,736 tranzactii pe 355,696 bare = o tranzactie la fiecare {355696/68736:.1f} bare.")
print(f"  Suprapunerea e suprimata (last=xi), deci asta implica iesiri quasi-instantanee.")
