"""sess_core.py — SESSION_SPECIALIST_FACTORY_V1 core. Causal session structure on governed XAUUSD M15 (UTC).

Sessions (DST-correct via session_tz anchors):
  ASIA   = UTC 00:00–07:00 (Tokyo/Sydney; negligible DST)
  LONDON = [london_open(08:00 Europe/London), nyse_open(09:30 America/New_York))  -> London-only pre-NY window
  NY     = [nyse_open, nyse_open + 6.5h)
Session ranges are FROZEN when the session completes; a decision at bar t uses ONLY completed sessions (no future session H/L). Prior-day
H/L/close are causal (yesterday). Entries = next-bar OPEN after the signal bar closes; stop structural; target 2R; conservative same-bar
ordering (ob_exec.resolve). S5 (NY opening-range breakout, long) is EXCLUDED from hypotheses — benchmark only.
"""
import sys, numpy as np, pandas as pd, datetime as dt
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import ob_core as OB, htf_core as HC, session_tz as STZ, ob_exec as EX

def build():
    m,H1,H4,P=OB.build()
    epoch=m["time"].values.astype("int64"); o=P["o"];h=P["h"];l=P["l"];c=P["c"];atr=P["atr"]
    dtu=m["dt"]; dates=dtu.dt.date.values; uhr=dtu.dt.hour.values; yr=dtu.dt.year.values
    amap=STZ.build_anchor_maps(dates)
    lon=amap["london_open"]; nys=amap["nyse_open"]
    lon_e=np.array([lon.get(d,0) for d in dates],dtype="int64")
    nys_e=np.array([nys.get(d,0) for d in dates],dtype="int64")
    asia=(uhr<7)
    london=(epoch>=lon_e)&(epoch<nys_e)
    ny=(epoch>=nys_e)&(epoch<nys_e+int(6.5*3600))
    # per-date session ranges (causal: value known only after the session's last bar)
    df=pd.DataFrame(dict(d=dates,o=o,h=h,l=l,c=c,ep=epoch,asia=asia,london=london,ny=ny,idx=np.arange(len(o))))
    S={}
    for d,g in df.groupby("d"):
        a=g[g.asia]; L=g[g.london]; N=g[g.ny]
        rec=dict()
        if len(a): rec["AH"]=a.h.max();rec["AL"]=a.l.min();rec["AO"]=a.o.iloc[0];rec["AC"]=a.c.iloc[-1];rec["Aend"]=int(a.idx.iloc[-1])
        if len(L): rec["LH"]=L.h.max();rec["LL"]=L.l.min();rec["LO"]=L.o.iloc[0];rec["LC"]=L.c.iloc[-1];rec["Lend"]=int(L.idx.iloc[-1]);rec["Lstart"]=int(L.idx.iloc[0])
        if len(N): rec["NH"]=N.h.max();rec["NL"]=N.l.min();rec["NO"]=N.o.iloc[0];rec["Nstart"]=int(N.idx.iloc[0]);rec["Nend"]=int(N.idx.iloc[-1])
        S[d]=rec
    return dict(m=m,P=P,epoch=epoch,dates=dates,uhr=uhr,yr=yr,o=o,h=h,l=l,c=c,atr=atr,
                asia=asia,london=london,ny=ny,lon_e=lon_e,nys_e=nys_e,S=S,n=len(o))

def resolve_entry(D, entry_bar, side, stop_px, tgtR=2.0):
    P=D["P"]; entry=D["o"][entry_bar]
    if (entry-stop_px)*side<=0: return None
    a=D["atr"][entry_bar]
    if abs(entry-stop_px)<0.5*a: stop_px=entry-side*0.5*a
    out=EX.resolve(P,entry,stop_px,side,entry_bar,tgtR)
    if out is None: return None
    net,g,mfe,amb=out
    return dict(net=net,g=g,mfe=mfe,amb=amb,risk=abs(entry-stop_px),k=entry_bar)

def era_of(y): return "D" if y<=2018 else ("C" if y<=2022 else "O")
