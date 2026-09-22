"""m5_panel.py — native M5 panel (2021-07-27..2026, single macro-era) + CAUSAL HTF context for '4H/Daily view -> M5 entry'. All lookahead-free:
H4/H1/D1 trend = resample M5->period (calendar), EMA trend, asof last COMPLETED bar (avail=start+period). PDH/PDL = prev UTC-day. pw = prev ISO-week.
session/OR/bar_in_sess/sess_high-low from M5. rmax/rmin20/50 shifted. ema20 (M5), session vwap. Returns a dict of numpy arrays."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-data-acq\reports\alpha_discovery")
import m5_core
def _asof_trend(T,H,L,C,period):
    b=(T//period)*period
    g=pd.DataFrame({"b":b,"h":H,"l":L,"c":C}).groupby("b").agg(h=("h","max"),l=("l","min"),c=("c","last")).reset_index()
    span=50 if period>=14400 else 50
    g["ema"]=g["c"].ewm(span=span,adjust=False).mean(); g["trend"]=(g["c"]>g["ema"]).astype(float); g["avail"]=g["b"]+period
    m=pd.merge_asof(pd.DataFrame({"t":T}),g[["avail","trend"]].sort_values("avail"),left_on="t",right_on="avail",direction="backward")
    return m["trend"].to_numpy()
def build():
    d=m5_core.load(); T=d["t"].astype(np.int64); O=d["o"].astype(float); H=d["h"].astype(float); L=d["l"].astype(float); C=d["c"].astype(float); ATR=d["atr"].astype(float); hr=d["hr"]; yr=d["yr"]; n=d["n"]
    # session by UTC hour
    sess=np.where(hr<7,"asia",np.where(hr<12,"london",np.where(hr<20,"ny","late")))
    # session block = day + session
    day=(T//86400); blk=day.astype(np.int64)*10+ (np.where(sess=="asia",0,np.where(sess=="london",1,np.where(sess=="ny",2,3))))
    df=pd.DataFrame({"blk":blk,"h":H,"l":L,"c":C})
    g=df.groupby("blk")
    orh=g["h"].transform(lambda x:x.iloc[:12].max()); orl=g["l"].transform(lambda x:x.iloc[:12].min())  # first 12 M5 = 1h OR
    bis=g.cumcount().to_numpy()
    bh=g["h"].max(); bl=g["l"].min(); psh=df["blk"].map(bh.shift(1)).to_numpy(); psl=df["blk"].map(bl.shift(1)).to_numpy()
    # daily
    dd=pd.DataFrame({"day":(T//86400)*86400,"h":H,"l":L,"c":C}).groupby("day").agg(h=("h","max"),l=("l","min"),c=("c","last")).reset_index()
    dd["avail"]=dd["day"]+86400; dd["pdh"]=dd["h"]; dd["pdl"]=dd["l"]; dd["ema10"]=dd["c"].ewm(span=10,adjust=False).mean(); dd["d1t"]=(dd["c"]>dd["ema10"]).astype(float)
    md=pd.merge_asof(pd.DataFrame({"t":T}),dd[["avail","pdh","pdl","d1t"]].sort_values("avail"),left_on="t",right_on="avail",direction="backward")
    pdh=md["pdh"].to_numpy(); pdl=md["pdl"].to_numpy(); d1t=md["d1t"].to_numpy()
    # weekly
    wk=((T-345600)//604800); ww=pd.DataFrame({"wk":wk,"h":H,"l":L}).groupby("wk").agg(h=("h","max"),l=("l","min")).reset_index(); ww["avail"]=(ww["wk"]+1)*604800+345600
    mw=pd.merge_asof(pd.DataFrame({"t":T}),ww[["avail","h","l"]].rename(columns={"h":"pwh","l":"pwl"}).sort_values("avail"),left_on="t",right_on="avail",direction="backward")
    pwh=mw["pwh"].to_numpy(); pwl=mw["pwl"].to_numpy()
    h4t=_asof_trend(T,H,L,C,14400); h1t=_asof_trend(T,H,L,C,3600)
    rmax20=pd.Series(H).rolling(20).max().shift(1).to_numpy(); rmin20=pd.Series(L).rolling(20).min().shift(1).to_numpy()
    rmax50=pd.Series(H).rolling(50).max().shift(1).to_numpy(); rmin50=pd.Series(L).rolling(50).min().shift(1).to_numpy()
    ema20=pd.Series(C).ewm(span=20,adjust=False).mean().to_numpy()
    atr_ma=pd.Series(ATR).rolling(50).mean().to_numpy(); comp=(ATR<0.8*atr_ma).astype(float)
    return dict(t=T,o=O,h=H,l=L,c=C,atr=ATR,n=n,yr=yr,hr=hr,sess=sess,blk=blk,orh=orh.to_numpy(),orl=orl.to_numpy(),bis=bis,
                psh=psh,psl=psl,pdh=pdh,pdl=pdl,pwh=pwh,pwl=pwl,h4t=h4t,h1t=h1t,d1t=d1t,rmax20=rmax20,rmin20=rmin20,rmax50=rmax50,rmin50=rmin50,ema20=ema20,comp=comp)
if __name__=="__main__":
    p=build(); T=p["t"]
    for k in ["h4t","h1t","d1t","pdh","pwh","orh"]:
        s=pd.Series(p[k]); print(f"{k:6s} cov={100*s.notna().mean():5.1f}% first={pd.to_datetime(T[s.notna().to_numpy().argmax()],unit='s',utc=True)}")
    print("sessions:", dict(pd.Series(p['sess']).value_counts()))
    print("span:", pd.to_datetime(T[0],unit='s',utc=True),'->',pd.to_datetime(T[-1],unit='s',utc=True),' bars',p['n'])
