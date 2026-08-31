"""session_remaining.py — SESSION_TIMING_LIQUIDITY_DISCOVERY_V1 remaining families (info-first, DST-correct, per era, no strategy).
(6) LBMA PM 15:00 Europe/London: after a LARGE pre-fix move (|London-session move into the fix| >= 1.5ATR), does the benchmark window
    change continuation vs reversal? (do NOT assume reversal.)
(3p) London H/L LEVEL interaction at the US 08:30 window: freeze London range [London-open, 08:30 ET); at [08:30, +2h] classify first
    interaction (break=close beyond / sweepback=wick beyond+close back); continuation vs reversal.
(1D) Asia→London D refinement: of the C-sweepback Asia events, those with a reclaim+retest — do they reverse more?
Continuation = move continues in the break/pre-fix direction (up 1.5ATR before dn). Per era D/C/O. cur_data M15 UTC."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cur_data as CD
import session_tz as STZ
KF=24
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); ts=m["time"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy(); dd=m["dt"].dt.date.to_numpy()
    A=STZ.build_anchor_maps(dd); lo_m=A["london_open"]; us_m=A["us_macro"]; pm_m=A["lbma_pm"]
    from collections import defaultdict
    byday=defaultdict(list)
    for i in range(n): byday[dd[i]].append(i)
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    def cont_from(i, contdir):
        if i>=n-KF or not np.isfinite(atr[i]) or atr[i]<=0: return None
        a=atr[i]; sh=h[i+1:i+1+KF]-c[i]; sl=c[i]-l[i+1:i+1+KF]
        up=np.where(sh>=1.5*a)[0]; dn=np.where(sl>=1.5*a)[0]; fu=up[0] if len(up) else 10**9; fd=dn[0] if len(dn) else 10**9
        if fu==fd==10**9: return None
        upf=fu<fd; return (upf if contdir>0 else (not upf))
    def report(name, evs):
        # evs = list of (era, cont_bool)
        allc=[x[1] for x in evs]
        if len(allc)<40: print(f"  {name}: n={len(allc)} thin"); return
        pc=np.mean(allc); es=" ".join(f"{e}={np.mean([x[1] for x in evs if x[0]==e]):.2f}(n{sum(1 for x in evs if x[0]==e)})" for e in ["D","C","O"])
        print(f"  {name}: n={len(allc):4d} P(cont)={pc:.3f} P(rev)={1-pc:.3f} | era {es}")
    # ---- (6) LBMA PM ----
    pm_evs=[]
    for day,idxs in byday.items():
        lo=lo_m.get(day); pm=pm_m.get(day)
        if lo is None or pm is None: continue
        lob=[i for i in idxs if i and ts[i]>=lo]; fixb=[i for i in idxs if ts[i]>=pm]
        if not lob or not fixb: continue
        i_lo=lob[0]; i_fix=fixb[0]
        if i_fix>=n-KF or not np.isfinite(atr[i_fix]) or atr[i_fix]<=0: continue
        premove=c[i_fix]-o[i_lo]; a=atr[i_fix]
        if abs(premove)<1.5*a: continue   # large pre-fix move only
        contdir=1 if premove>0 else -1
        r=cont_from(i_fix, contdir)
        if r is not None: pm_evs.append((era(i_fix), r))
    print("(6) LBMA PM 15:00: after a LARGE pre-fix move, does it CONTINUE (vs reverse) post-fix?")
    report("LBMA post-fix continuation", pm_evs)
    # ---- (3p) London H/L level interaction at 08:30 ----
    lvl_break=[]; lvl_sweep=[]
    for day,idxs in byday.items():
        lo=lo_m.get(day); us=us_m.get(day)
        if lo is None or us is None: continue
        lonr=[i for i in idxs if lo<=ts[i]<us]; win=[i for i in idxs if us<=ts[i]<us+2*3600]
        if len(lonr)<4 or len(win)<2: continue
        LH=max(h[i] for i in lonr); LL=min(l[i] for i in lonr)
        for i in win:
            up=h[i]>=LH; dn=l[i]<=LL
            if up or dn:
                side=1 if (up and not dn) else (-1 if (dn and not up) else (1 if (h[i]-LH)>=(LL-l[i]) else -1))
                if side>0: brk=c[i]>LH
                else: brk=c[i]<LL
                r=cont_from(i, side)
                if r is not None: (lvl_break if brk else lvl_sweep).append((era(i), r))
                break
    print("\n(3p) London H/L interaction at US 08:30 window: continuation by type")
    report("break(close beyond)->cont", lvl_break)
    report("sweepback(wick+close back)->cont", lvl_sweep)
    print("=> if sweepback P(rev) >> break P(rev) cross-era -> London-level sweep carries reversal info; else no info.")
    # ---- (1D) Asia sweep+reclaim ----
    asia_reclaim=[]
    LONWIN=5*3600
    for day,idxs in byday.items():
        lo=lo_m.get(day)
        if lo is None: continue
        asia=[i for i in idxs if ts[i]<lo]; lon=[i for i in idxs if lo<=ts[i]<lo+LONWIN]
        if len(asia)<4 or len(lon)<6: continue
        AH=max(h[i] for i in asia); AL=min(l[i] for i in asia)
        # find first sweepback of an Asia extreme, then a reclaim+retest -> measure reversal (contdir = fade)
        for k,i in enumerate(lon[:-4]):
            up=h[i]>=AH and c[i]<AH; dn=l[i]<=AL and c[i]>AL
            if up or dn:
                side=1 if up else -1; lvl=AH if up else AL
                # reclaim+retest within next 4 bars: price returns to lvl and holds (rejection)
                rec=False
                for j in lon[k+1:k+5]:
                    if up and h[j]>=lvl and c[j]<lvl: rec=True; ri=j; break
                    if dn and l[j]<=lvl and c[j]>lvl: rec=True; ri=j; break
                if rec:
                    r=cont_from(ri, -side)  # fade: after upside sweep+reclaim, continuation of FADE = down
                    if r is not None: asia_reclaim.append((era(ri), r))
                break
    print("\n(1D) Asia sweep+RECLAIM+retest -> FADE continuation (reversal setup):")
    report("Asia sweep+reclaim->fade", asia_reclaim)
    print("=> P(fade-cont)>>0.5 cross-era = reclaim adds reversal edge; ~0.5 = no info (consistent with SF-1).")
if __name__=="__main__": main()
