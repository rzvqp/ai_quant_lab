"""htf_core.py — H1_H4_SETUP_M5_EXECUTION_V1 core engine.

Causal multi-timeframe: M15 (base, cur_data) -> H1 (UTC hour) -> H4 (UTC 4h blocks 00/04/08/12/16/20). At an M15 decision bar t, HTF
context uses ONLY completed H1/H4 bars (close_time <= t). H4 = context/location; H1 = structural setup; M15 = confirm; M5 = execution
(separate, 2021-07-27+ only). Outcome computed only after setup frozen. Cost: principled per-trade cost_R = COST_PRICE / stop_distance
(COST_PRICE=0.419 = 0.24R at the median M15 ATR $1.747); also a conservative flat 0.24R reported alongside.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cur_data as CD

COST_PRICE = 0.419      # round-trip spread+slippage in price (= 0.24R at median M15 ATR)
PIP = 0.10              # 1 project pip = $0.10 ; 100 pips = $10 move
M5_START = pd.Timestamp("2021-07-27", tz="UTC")

def _agg(dfM15, rule_hours):
    """Aggregate M15 -> higher TF on fixed UTC blocks of rule_hours. Returns OHLC + close_time (block end)."""
    sec = dfM15["time"].values.astype("int64")            # unix seconds (UTC)
    blk = (sec//(rule_hours*3600))*(rule_hours*3600)       # block start epoch
    key = pd.to_datetime(blk, unit="s", utc=True)
    g = dfM15.groupby(key)
    o=g["open"].first(); h=g["high"].max(); l=g["low"].min(); c=g["close"].last(); v=g["volume"].sum()
    out=pd.DataFrame({"open":o,"high":h,"low":l,"close":c,"vol":v})
    out["start"]=out.index
    out["close_time"]=out["start"] + pd.Timedelta(hours=rule_hours)   # block completes at start+rule_hours
    return out.reset_index(drop=True)

def build():
    m=CD.load_m15().reset_index(drop=True)
    m["ct"]=m["dt"]+pd.Timedelta(minutes=15)                          # M15 close time
    H1=_agg(m,1); H4=_agg(m,4)
    # HTF features (causal, computed on completed HTF bars)
    for D,span1,span2 in [(H1,20,50),(H4,20,50)]:
        c=D["close"]
        D["ema_f"]=c.ewm(span=span1,adjust=False).mean()
        D["ema_s"]=c.ewm(span=span2,adjust=False).mean()
        D["atr"]=(pd.concat([D["high"]-D["low"],(D["high"]-c.shift()).abs(),(D["low"]-c.shift()).abs()],axis=1).max(axis=1)).rolling(14).mean()
        D["swH"]=D["high"].rolling(20).max().shift(1)                 # prior swing extremes (knowable at bar)
        D["swL"]=D["low"].rolling(20).min().shift(1)
        D["hh"]=D["high"].rolling(50).max().shift(1); D["ll"]=D["low"].rolling(50).min().shift(1)
    # H4 context (frozen causal): TREND_UP / TREND_DOWN / BALANCE
    def ctx(D):
        up=(D["ema_f"]>D["ema_s"])&(D["close"]>D["ema_s"]); dn=(D["ema_f"]<D["ema_s"])&(D["close"]<D["ema_s"])
        return np.where(up,"TREND_UP",np.where(dn,"TREND_DOWN","BALANCE"))
    H4["ctx"]=ctx(H4)
    # map each M15 bar to the last COMPLETED H1 and H4 bar (close_time <= M15 close time)
    def map_last(D):
        cts=D["close_time"].values.astype("int64")
        idx=np.searchsorted(cts, m["ct"].values.astype("int64"), side="right")-1
        return idx
    m["h1i"]=map_last(H1); m["h4i"]=map_last(H4)
    return m,H1,H4

# ---------- outcome: directional structural barrier from an M15 anchor ----------
def outcome(m, t, side, stop_px, tgtR=2.0, H=64):
    """From M15 anchor close at t, long/short (side). stop at stop_px (price), target = entry + side*tgtR*risk.
    Return dict: gross_R, net_R(price-cost), net_R_flat(0.24), mfe_R, mae_R, t1R,t2R,t3R, mfe_pips, captured_pips, hold, risk_px."""
    h=m["high"].values; l=m["low"].values; c=m["close"].values; n=len(m)
    entry=c[t]; risk=abs(entry-stop_px)
    if risk<=0 or t+1>=n: return None
    tgt=entry+side*tgtR*risk
    end=min(t+H,n-1); mfe=-1e9; mae=1e9; t1=t2=t3=np.nan; res=None; hold=end-t
    for j in range(t+1,end+1):
        fav=(h[j]-entry)/risk if side>0 else (entry-l[j])/risk
        adv=(entry-l[j])/risk if side>0 else (h[j]-entry)/risk   # excursion toward stop (positive=toward stop)
        mfe=max(mfe,fav); mae=min(mae,-adv)
        if np.isnan(t1) and fav>=1: t1=j-t
        if np.isnan(t2) and fav>=2: t2=j-t
        if np.isnan(t3) and fav>=3: t3=j-t
        hit_t=(h[j]>=tgt) if side>0 else (l[j]<=tgt)
        hit_s=(l[j]<=stop_px) if side>0 else (h[j]>=stop_px)
        if hit_s and hit_t: res=-1.0; hold=j-t; break
        if hit_t: res=tgtR; hold=j-t; break
        if hit_s: res=-1.0; hold=j-t; break
    if res is None: res=side*(c[end]-entry)/risk               # mark to close
    cost_R=COST_PRICE/risk
    captured=res*risk/PIP                                       # realized move in pips (signed R*risk)
    return dict(gross_R=res, net_R=res-cost_R, net_R_flat=res-0.24, mfe_R=mfe, mae_R=mae,
                t1R=t1,t2R=t2,t3R=t3, mfe_pips=mfe*risk/PIP, captured_pips=captured, hold=hold,
                risk_px=risk, cost_pct_risk=cost_R)

if __name__=="__main__":
    m,H1,H4=build()
    print(f"M15 rows={len(m)}  H1 bars={len(H1)}  H4 bars={len(H4)}")
    # verify causality: H4 close_time mapped must be <= M15 close time
    ct=m["ct"].values.astype("int64"); h4ct=H4["close_time"].values.astype("int64")[m["h4i"].values]
    print("causal H4 map OK:", bool(np.all(h4ct<=ct)), "| any unmapped(-1):", int((m['h4i']<0).sum()))
    # H4 context census
    vc=H4["ctx"].value_counts(); print("H4 context bars:", dict(vc))
    # coverage of contexts over M15 bars
    ctxm=H4["ctx"].values[m["h4i"].values]
    import collections; print("M15 bars by H4 context:", dict(collections.Counter(ctxm[m['h4i'].values>=0])))
    print("median H1 ATR:", np.nanmedian(H1['atr']), " median H4 ATR:", np.nanmedian(H4['atr']))
