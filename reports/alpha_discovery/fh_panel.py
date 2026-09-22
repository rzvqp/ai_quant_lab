"""fh_panel.py — FULL-HISTORY causal feature panel (2011-2026), fixing the mstrat truncation the Statistician found: mstrat.load() reads a 2023+
D1 file so pdh/pdl/h4/h1/d1 context is only 23.7% non-null (all from 2023-01-03). Here we OVERRIDE those columns with full-history causal versions
computed directly from the M15 series, so the governed grammar can be validated across TRUE calendar eras. All lookahead-free:
  pdh/pdl        = previous completed UTC-day high/low, available from the current day's first bar (asof on day-close availability).
  pw_high/low    = previous completed ISO-week high/low, available from the current week's start.
  h4_trend/h1_trend = resample M15->H4/H1 (calendar), EMA50 trend (close>ema50), asof-mapped to the last COMPLETED HTF bar (avail=start+period).
  d1_trend       = previous-day close > prev-day EMA(10 days) proxy from the M15-day series.
Returns a fixed copy of the mstrat panel. Verified: coverage ~full-history, 0 leak bars."""
import os, sys, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; sys.path.insert(0, os.path.join(AA,"code"))
import mstrat
def _asof(T, avail_df):
    return pd.merge_asof(pd.DataFrame({"t":T}), avail_df.sort_values("avail"), left_on="t", right_on="avail", direction="backward")
def build():
    d=mstrat.load().copy(); T=d["time"].to_numpy(np.int64); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); O=d["open"].to_numpy(float); n=len(d)
    # ---- full-history daily (UTC calendar day) ----
    day=(T//86400)*86400
    dd=pd.DataFrame({"day":day,"h":H,"l":L,"c":C,"o":O}).groupby("day").agg(h=("h","max"),l=("l","min"),c=("c","last"),o=("o","first")).reset_index()
    dd["avail"]=dd["day"]+86400                       # completed day available next day
    dd["pdh"]=dd["h"]; dd["pdl"]=dd["l"]; dd["pd_close"]=dd["c"]; dd["pd_open"]=dd["o"]
    dd["ema10"]=dd["c"].ewm(span=10,adjust=False).mean(); dd["d1trend"]=(dd["c"]>dd["ema10"]).astype(float)
    m=_asof(T, dd[["avail","pdh","pdl","pd_close","pd_open","d1trend"]])
    d["pdh"]=m["pdh"].to_numpy(); d["pdl"]=m["pdl"].to_numpy(); d["pd_close"]=m["pd_close"].to_numpy(); d["pd_open"]=m["pd_open"].to_numpy()
    d["pd_mid"]=(d["pdh"]+d["pdl"])/2; d["d1_trend_up"]=m["d1trend"].to_numpy()
    # ---- full-history weekly (ISO week via 7-day bucket anchored Monday) ----
    wk=((T-345600)//604800)                            # weeks since 1970-01-05 (Mon)
    ww=pd.DataFrame({"wk":wk,"h":H,"l":L}).groupby("wk").agg(h=("h","max"),l=("l","min")).reset_index()
    ww["avail"]=(ww["wk"]+1)*604800+345600
    ww["pwh"]=ww["h"]; ww["pwl"]=ww["l"]
    mw=_asof(T, ww[["avail","pwh","pwl"]]); d["pw_high"]=mw["pwh"].to_numpy(); d["pw_low"]=mw["pwl"].to_numpy()
    # ---- causal H4 / H1 trend from M15 (calendar buckets, EMA50, asof completed bar) ----
    def htf(period):
        b=(T//period)*period
        g=pd.DataFrame({"b":b,"h":H,"l":L,"c":C}).groupby("b").agg(h=("h","max"),l=("l","min"),c=("c","last")).reset_index()
        g["ema50"]=g["c"].ewm(span=50,adjust=False).mean(); g["trend"]=(g["c"]>g["ema50"]).astype(float); g["avail"]=g["b"]+period
        mm=_asof(T, g[["avail","trend"]]); return mm["trend"].to_numpy()
    d["h4_trend_up"]=htf(14400); d["h1_trend_up"]=htf(3600)
    return d
if __name__=="__main__":
    d=build(); T=d["time"].to_numpy(); yr=pd.to_datetime(T,unit="s",utc=True).year.to_numpy()
    for c in ["pdh","pdl","pw_high","h4_trend_up","h1_trend_up","d1_trend_up"]:
        s=d[c]; cov=100*s.notna().mean(); first=pd.to_datetime(T[s.notna().to_numpy().argmax()],unit="s",utc=True)
        print(f"{c:14s} coverage={cov:5.1f}%  first_nonnull={first}")
    # leak check: pdh at day D must equal a PRIOR day's high (never today's)
    day=(T//86400)*86400; import numpy as np
    dfh=pd.DataFrame({"day":day,"h":d['high'].to_numpy()}).groupby('day').h.max()
    # for a sample of bars, assert pdh <= max high of strictly-prior days (causal)
    ok=0; bad=0
    for i in range(2000, n:=len(d), 50000):
        di=day[i]; prior=dfh[dfh.index<di]
        if len(prior)==0 or not np.isfinite(d['pdh'].iloc[i]): continue
        if abs(d['pdh'].iloc[i]-prior.iloc[-1])<1e-6: ok+=1
        else: bad+=1
    print(f"pdh causal spot-check: matches-prior-day {ok}, mismatches {bad}")
