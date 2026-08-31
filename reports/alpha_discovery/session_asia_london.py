"""session_asia_london.py — SESSION_TIMING_LIQUIDITY_DISCOVERY_V1, FIRST PRIORITY (info-first, no strategy).
Asia range forms -> Asia High/Low frozen at London open (causal, DST-correct anchor) -> during the London window, classify the FIRST
interaction with an Asia extreme: A clean break/acceptance (close beyond), C sweep+close-back-inside (wick beyond, close back), E no
interaction. (B sweep = A∪C.) For each, measure continuation vs reversal, MFE/MAE, P(target-before-invalidation), time-to-resolution,
adverse-first — LONG (Asia-High interaction) and SHORT (Asia-Low) separate, per era D<=2018/C19-22/O23+. INFORMATION-FIRST: does
'sweep+close-back' (C) predict REVERSAL more than 'clean break' (A)? Complexity must add info. Causal: Asia levels frozen at London
open; outcomes measured forward from the interaction bar. cur_data M15 UTC."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cur_data as CD
import session_tz as STZ
KF=24  # forward horizon (6h) for outcome
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); ts=m["time"].to_numpy(); n=len(m); dt=m["dt"]; yr=dt.dt.year.to_numpy(); dd=dt.dt.date.to_numpy()
    anchors=STZ.build_anchor_maps(dd)["london_open"]
    # group bar indices by date
    from collections import defaultdict
    byday=defaultdict(list)
    for i in range(n): byday[dd[i]].append(i)
    LONDON_WIN=5*3600
    events=[]  # (type, side, i, era)
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    for day,idxs in byday.items():
        lo=anchors.get(day)
        if lo is None: continue
        day0=int(ts[idxs[0]])//86400*86400   # 00:00 UTC of the day (approx via first bar)
        asia=[i for i in idxs if ts[i]<lo]        # pre-London bars this date = Asia range
        lon=[i for i in idxs if lo<=ts[i]<lo+LONDON_WIN]
        if len(asia)<4 or len(lon)<4: continue
        AH=max(h[i] for i in asia); AL=min(l[i] for i in asia)
        # first interaction with an Asia extreme in London window
        inter=None
        for i in lon:
            up=h[i]>=AH; dn=l[i]<=AL
            if up or dn:
                side=1 if (up and not dn) else (-1 if (dn and not up) else (1 if (h[i]-AH)>=(AL-l[i]) else -1))
                lvl=AH if side>0 else AL
                if side>0: typ="A_break" if c[i]>AH else "C_sweepback"
                else: typ="A_break" if c[i]<AL else "C_sweepback"
                inter=(typ,side,i); break
        if inter is None: events.append(("E_none",0,lon[0])); continue
        events.append((inter[0],inter[1],inter[2]))
    # outcomes
    def outcome(i, contdir):
        """contdir=+1 continuation is UP (upside interaction), -1 continuation is DOWN. Returns dict."""
        if i>=n-KF or not np.isfinite(atr[i]) or atr[i]<=0: return None
        a=atr[i]; segh=h[i+1:i+1+KF]-c[i]; segl=c[i]-l[i+1:i+1+KF]
        up=np.where(segh>=1.5*a)[0]; dnn=np.where(segl>=1.5*a)[0]
        fu=up[0] if len(up) else 10**9; fd=dnn[0] if len(dnn) else 10**9
        if fu==fd==10**9: return None
        up_first = fu<fd
        cont = up_first if contdir>0 else (not up_first)
        mfe = (np.max(segh) if contdir>0 else np.max(segl))/a
        mae = (np.max(segl) if contdir>0 else np.max(segh))/a
        ttr = min(fu,fd); ttr=int(ttr) if ttr<10**9 else -1
        return dict(cont=cont, mfe=mfe, mae=mae, ttr=ttr, advfirst=(mae>0 and (fd<fu if contdir>0 else fu<fd)))
    # aggregate by (type, side)
    rows=defaultdict(list)
    for typ,side,i in events:
        if typ=="E_none": continue
        oc=outcome(i, side)  # continuation dir = side (upside interaction -> continuation is up)
        if oc: rows[(typ,side,era(i))].append(oc)
    ne=sum(1 for e in events if e[0]=="E_none"); tot=len(events)
    print(f"ASIA->LONDON interaction (n_days={tot}): no-interaction(E)={ne} ({100*ne/tot:.0f}%), interacted={tot-ne}")
    print("Continuation vs Reversal by interaction type/side (info-first). P(cont)=continue in break direction; reversal=1-P(cont).\n")
    def agg(key):
        v=rows.get(key,[])
        if len(v)<40: return None
        return (len(v), np.mean([x['cont'] for x in v]), np.median([x['mfe'] for x in v]), np.median([x['mae'] for x in v]),
                np.median([x['ttr'] for x in v]), np.mean([x['advfirst'] for x in v]))
    for side,sname in [(1,"UPSIDE(AsiaHigh->LONG-cont)"),(-1,"DOWNSIDE(AsiaLow->SHORT-cont)")]:
        print(f"  {sname}:")
        for typ in ["A_break","C_sweepback"]:
            allv=[x for e in ["D","C","O"] for x in rows.get((typ,side,e),[])]
            if len(allv)<40: print(f"    {typ:12s}: n={len(allv)} thin"); continue
            pc=np.mean([x['cont'] for x in allv]); mfe=np.median([x['mfe'] for x in allv]); mae=np.median([x['mae'] for x in allv])
            adv=np.mean([x['advfirst'] for x in allv])
            eras=" ".join(f"{e}={np.mean([x['cont'] for x in rows.get((typ,side,e),[])]):.2f}(n{len(rows.get((typ,side,e),[]))})" if len(rows.get((typ,side,e),[]))>=20 else f"{e}=--" for e in ["D","C","O"])
            print(f"    {typ:12s}: n={len(allv):4d} P(cont)={pc:.3f} P(rev)={1-pc:.3f} MFE={mfe:.2f} MAE={mae:.2f} advFirst={adv:.2f} | era {eras}")
    print("\n=> INFO CHECK: if C_sweepback P(rev) >> A_break P(rev) (cross-era), the sweep+close-back adds REVERSAL information over a")
    print("   raw break. If ~equal or era-unstable, the refinement adds nothing. (No strategy yet; information-first.)")
if __name__=="__main__": main()
