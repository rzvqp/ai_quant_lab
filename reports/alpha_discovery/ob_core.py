"""ob_core.py — ORDER_BLOCK_RETEST_FACTORY_V1 core: causal order-block detection, freeze, first-retest, outcome, matched controls.

CAUSAL construction (anti-hindsight §4/§27):
  1. Bullish BOS at bar i = close[i] > prior causal swing high swH[i]=max(high[i-K:i]) AND close[i-1]<=swH[i-1] (fresh close-break).
  2. Origin OB = last bearish candle (close<open) in [i-DL, i-1] (the last down-candle before the up-impulse). Mirror for bearish.
  3. Displacement = (close[i] - block_high)/atr[i]  (impulse from block to BOS in ATR). Require >= disp_min.
  4. FREEZE block [low,high] of origin (FULL_RANGE) at ELIGIBILITY TIME = i (BOS bar close). Coordinates never change afterward.
  5. FIRST RETEST = first bar k>i with low[k]<=block_high (bull) before a causal close-invalidation (close<block_low). FRESH by
     construction. Entry = limit at block_high; stop = block_low - floor. Everything known at or before k.
Matched controls (§21): PULLBACK (retest 50% of impulse leg, non-OB), BOSONLY (first 1xATR pullback after BOS), BETA (random longs).
Reuses htf_core for the M15/H1/H4 causal panel and cost. cur_data M15 UTC.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import htf_core as HC

K=20; DL=10; RETEST_WIN=192; FLOOR_ATR=0.1

def build():
    m,H1,H4=HC.build()
    o=m["open"].values; h=m["high"].values; l=m["low"].values; c=m["close"].values; atr=m["atr"].values
    swH=pd.Series(h).rolling(K).max().shift(1).values      # prior causal swing high (excludes i)
    swL=pd.Series(l).rolling(K).min().shift(1).values
    hi100=pd.Series(h).rolling(100).max().shift(1).values; lo100=pd.Series(l).rolling(100).min().shift(1).values
    return m,H1,H4,dict(o=o,h=h,l=l,c=c,atr=atr,swH=swH,swL=swL,hi100=hi100,lo100=lo100,n=len(m))

def detect_obs(P, disp_min=0.75, direction="bull"):
    """Return list of frozen OB events (dict) at BOS bar i, with origin block coords + displacement + first-retest bar."""
    o=P["o"];h=P["h"];l=P["l"];c=P["c"];atr=P["atr"];swH=P["swH"];swL=P["swL"];n=P["n"]
    ev=[]
    for i in range(K+DL, n-1):
        a=atr[i]
        if not np.isfinite(a) or a<=0: continue
        if direction=="bull":
            bos = (c[i]>swH[i]) and (c[i-1]<=swH[i-1])
            if not bos: continue
            # origin = last bearish candle in [i-DL, i-1]
            oj=None
            for j in range(i-1, i-DL-1, -1):
                if c[j]<o[j]: oj=j; break
            if oj is None: continue
            blo,bhi=l[oj],h[oj]
            disp=(c[i]-bhi)/a
            if disp<disp_min or bhi<=blo: continue
            ev.append(dict(i=i,oj=oj,dir=1,blo=blo,bhi=bhi,bmid=(blo+bhi)/2,disp=disp,bos_close=c[i],swbroken=swH[i]))
        else:
            bos = (c[i]<swL[i]) and (c[i-1]>=swL[i-1])
            if not bos: continue
            oj=None
            for j in range(i-1, i-DL-1, -1):
                if c[j]>o[j]: oj=j; break
            if oj is None: continue
            blo,bhi=l[oj],h[oj]
            disp=(blo-c[i])/a
            if disp<disp_min or bhi<=blo: continue
            ev.append(dict(i=i,oj=oj,dir=-1,blo=blo,bhi=bhi,bmid=(blo+bhi)/2,disp=disp,bos_close=c[i],swbroken=swL[i]))
    return ev

def first_retest(P, e):
    """First causal retest of the frozen block after BOS bar i, before a close-invalidation. Return (k, depth) or None."""
    h=P["h"];l=P["l"];c=P["c"];n=P["n"]; i=e["i"]; blo=e["blo"]; bhi=e["bhi"]; d=e["dir"]
    end=min(i+RETEST_WIN, n-1)
    for k in range(i+1, end+1):
        if d>0:
            if c[k]<blo: return None                 # closing invalidation before retest
            if l[k]<=bhi:                            # price re-enters block from above
                depth=(bhi-l[k])/(bhi-blo); return k, min(depth,1.5)
        else:
            if c[k]>bhi: return None
            if h[k]>=blo:
                depth=(h[k]-blo)/(bhi-blo); return k, min(depth,1.5)
    return None

def retest_outcome(P, entry_px, stop_px, side, k, tgtR=2.0, H=RETEST_WIN, resolve_from=None):
    """From retest bar k, resolve 2R target / stop over H bars starting at resolve_from (default k). Causal."""
    h=P["h"];l=P["l"];c=P["c"];atr=P["atr"];n=P["n"]
    risk=abs(entry_px-stop_px)
    if risk<=0: return None
    start=k if resolve_from is None else resolve_from
    tgt=entry_px+side*tgtR*risk; end=min(start+H,n-1); mfe=-1e9; mae=1e9; res=None
    for j in range(start, end+1):
        fav=(h[j]-entry_px)/risk if side>0 else (entry_px-l[j])/risk
        adv=(entry_px-l[j])/risk if side>0 else (h[j]-entry_px)/risk
        mfe=max(mfe,fav); mae=min(mae,-adv)
        hit_t=(h[j]>=tgt) if side>0 else (l[j]<=tgt)
        hit_s=(l[j]<=stop_px) if side>0 else (h[j]>=stop_px)
        if hit_s and hit_t: res=-1.0; break
        if hit_t: res=tgtR; break
        if hit_s: res=-1.0; break
    if res is None: res=side*(c[end]-entry_px)/risk
    cost_R=HC.COST_PRICE/risk
    return dict(gross_R=res, net_R=res-cost_R, mfe_R=mfe, mae_R=mae, risk_px=risk, entry=entry_px, kbar=k)

if __name__=="__main__":
    m,H1,H4,P=build()
    for dd in ("bull","bear"):
        ev=detect_obs(P,0.75,dd); rt=[e for e in ev if first_retest(P,e)]
        print(f"{dd}: OB events(disp>=0.75)={len(ev)}  with first-retest(fresh, pre-invalidation)={len(rt)}")
    # anti-lookahead spot check: retest bar k must be > BOS bar i for all
    ev=detect_obs(P,0.75,"bull"); ok=all((lambda r: r is None or r[0]>e["i"])(first_retest(P,e)) for e in ev[:2000])
    print("all retests strictly after BOS:", ok)
