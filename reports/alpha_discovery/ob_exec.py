"""ob_exec.py — OB_CAUSAL_EXECUTION_FACTORY_V1: 4 causal execution protocols on the FROZEN OB level (structure unchanged).

Structure frozen from OBR (ob_core.detect_obs): last-bearish-candle OB before a bullish close-BOS of the causal 20-bar swing high,
displacement>=1.5 ATR, bull, LN+NY. Only the EXECUTION changes. Same-bar ordering is CONSERVATIVE everywhere: on any bar where both stop
and target are reachable, assume STOP first (worst case). No intrabar order inference, no same-bar close cancelling an already-touched fill.

Fill/entry semantics per family (all stop=block_low-0.1ATR floored to >=0.5ATR risk, target=2R, resolve to horizon):
  EXEC_A true resting limit : fill at block_high on FIRST bar low<=block_high (a same-bar close below block => filled LOSS, not dropped).
                              resolve from the fill bar.  (corrected canonical; sanity baseline)
  EXEC_B retest-close->next  : first bar low<=block_high AND close>=block_low (still structurally valid at close) -> enter next bar OPEN.
  EXEC_C rejection-close->next: first bar low<=block_high AND close>block_high (closed back above entry edge = rejection) -> next bar OPEN.
  EXEC_D penetration+reclaim : a bar closes <=block_high (penetration) then a later bar closes>block_high (reclaim) -> next bar OPEN.
OLD artifact reproduction: the buggy limit_fill (close<block_low returns None BEFORE the touch) -> drops same-bar losers -> inflates R.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import ob_core as OB, htf_core as HC

FLOOR=OB.FLOOR_ATR

def resolve(P, entry, stop, side, start, tgtR=2.0, H=OB.RETEST_WIN):
    """Conservative same-bar ordering: ambiguous bar (both reachable) => STOP (loss). Returns (net_R, gross_R, mfe_R, ambiguous)."""
    h=P["h"];l=P["l"];c=P["c"];n=P["n"]; risk=abs(entry-stop)
    if risk<=0 or start>=n: return None
    tgt=entry+side*tgtR*risk; end=min(start+H,n-1); mfe=-1e9; amb=0; res=None
    for j in range(start,end+1):
        fav=(h[j]-entry)/risk if side>0 else (entry-l[j])/risk; mfe=max(mfe,fav)
        t_reach=(h[j]>=tgt) if side>0 else (l[j]<=tgt)
        s_reach=(l[j]<=stop) if side>0 else (h[j]>=stop)
        if t_reach and s_reach: res=-1.0; amb=1; break     # conservative worst-case
        if s_reach: res=-1.0; break
        if t_reach: res=tgtR; break
    if res is None: res=side*(c[end]-entry)/risk
    return res-HC.COST_PRICE/risk, res, mfe, amb

def stop_of(e,a):
    stop=e["blo"]-FLOOR*a
    if e["bhi"]-stop<0.5*a: stop=e["bhi"]-0.5*a
    return stop

def exec_entry(P, e, mode):
    """Return (entry_px, resolve_start_bar) or None, using only causal info. i=BOS bar."""
    h=P["h"];l=P["l"];c=P["c"];o=P["o"];n=P["n"]; i=e["i"]; bhi=e["bhi"]; blo=e["blo"]; end=min(i+OB.RETEST_WIN,n-1)
    if mode=="A":
        for k in range(i+1,end+1):
            if l[k]<=bhi: return bhi, k          # fill at level on first touch (even if closes below => loss); resolve from k
        return None
    if mode=="B":
        for k in range(i+1,end+1):
            if c[k]<blo: return None             # invalidated before a valid retest
            if l[k]<=bhi and c[k]>=blo and k+1<=n-1: return o[k+1], k+1   # touched & still valid -> next open
        return None
    if mode=="C":
        for k in range(i+1,end+1):
            if c[k]<blo: return None
            if l[k]<=bhi and c[k]>bhi and k+1<=n-1: return o[k+1], k+1     # rejection close above edge -> next open
        return None
    if mode=="D":
        pen=False
        for k in range(i+1,end+1):
            if not pen:
                if c[k]<=bhi and l[k]<=bhi: pen=True           # penetration (closed into/through block edge)
                if c[k]<blo: return None
            else:
                if c[k]<blo: return None                        # invalidated during penetration
                if c[k]>bhi and k+1<=n-1: return o[k+1], k+1    # reclaim -> next open
        return None
    return None

def old_buggy_entry(P, e):
    """Reproduce the falsified fill: close<block_low returns None BEFORE the touch check (drops same-bar losers). resolve from k."""
    l=P["l"];c=P["c"];n=P["n"]; i=e["i"]; bhi=e["bhi"]; blo=e["blo"]; end=min(i+OB.RETEST_WIN,n-1)
    for k in range(i+1,end+1):
        if c[k]<blo: return None
        if l[k]<=bhi: return bhi, k
    return None

def collect(P, m, mode, disp_min=1.5, session=("LN","NY")):
    atr=P["atr"]; hr=m["dt"].dt.hour.values; yr=m["dt"].dt.year.values
    ev=OB.detect_obs(P,disp_min,"bull"); rows=[]
    for e in ev:
        a=atr[e["i"]]; stop=stop_of(e,a)
        r=(old_buggy_entry(P,e) if mode=="OLD" else exec_entry(P,e,mode))
        if r is None: continue
        entry,start=r
        # session of the entry bar
        eb=start; H_=hr[min(eb,len(hr)-1)]; ss="AS" if H_<8 else ("LN" if H_<13 else ("NY" if H_<20 else "LT"))
        if ss not in session: continue
        # for next-open modes the stop must still be below entry
        if entry-stop<=0: continue
        risk=entry-stop
        if risk<0.5*a: stop=entry-0.5*a; risk=entry-stop
        out=resolve(P,entry,stop,1,start,2.0)
        if out is None: continue
        net,g,mfe,amb=out
        y=yr[min(start,len(yr)-1)]; era="D" if y<=2018 else ("C" if y<=2022 else "O")
        rows.append(dict(net=net,g=g,mfe=mfe,amb=amb,risk=risk,era=era,y=y,k=start,entry=entry,stop=stop,ev=e))
    return rows
