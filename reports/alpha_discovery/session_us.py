"""session_us.py — SESSION_TIMING_LIQUIDITY_DISCOVERY_V1 families 3+4: US 08:30 ET (macro window) and NYSE 09:30 ET (equity open),
as TWO DISTINCT events (DST-correct anchors). Info-first + tradeable-relevant. For each anchor: opening-range (first 30min = 2 M15
bars) breakout, direction supplied by the break, continuation measured (P(cont), MFE/MAE, net 2R:1R after STRESS 0.24), per era. Plus
family-4: does the 08:30->09:30 move CONTINUE past 09:30? These DST-correct macro/equity anchors are NOT the fixed-UTC ORBs VOLTIME-4
tested. S5 frozen (a 09:30 edge, if any, is a NEW identity, not S5). cur_data M15 UTC."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cur_data as CD
import session_tz as STZ
COST=0.24; HMAX=32
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); ts=m["time"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy(); dd=m["dt"].dt.date.to_numpy()
    amaps=STZ.build_anchor_maps(dd)
    from collections import defaultdict
    byday=defaultdict(list)
    for i in range(n): byday[dd[i]].append(i)
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    def orb_at(anchor_name, ORBARS=2, WIN=12, RR=2.0):
        """OR = first ORBARS M15 bars at/after the anchor; break within WIN bars -> 2R:1R bracket. Returns list of (era,R,dir)."""
        anc=amaps[anchor_name]; sig=[]
        for day,idxs in byday.items():
            a0=anc.get(day)
            if a0 is None: continue
            orr=[i for i in idxs if a0<=ts[i]<a0+ORBARS*900]
            if len(orr)<ORBARS: continue
            s0=orr[0]
            if s0<250 or s0>=n-HMAX-WIN-2: continue
            ohi=max(h[i] for i in orr); olo=min(l[i] for i in orr); aa=atr[orr[-1]]
            if not np.isfinite(aa) or aa<=0: continue
            ei0=orr[-1]+1; brk=None
            for j in range(ei0, min(ei0+WIN, n-2)):
                if c[j]>ohi: brk=(j,1); break
                if c[j]<olo: brk=(j,-1); break
            if brk is None: continue
            j,dirn=brk; ei=j+1
            if ei>=n-HMAX: continue
            entry=o[ei]; stop=(olo-0.1*aa) if dirn>0 else (ohi+0.1*aa); risk=abs(entry-stop)
            if risk<=0.05*aa: continue
            tgt=entry+RR*risk*dirn; segl=l[ei:ei+HMAX]; segh=h[ei:ei+HMAX]
            if dirn>0: fs=np.where(segl<=stop)[0]; ft=np.where(segh>=tgt)[0]
            else: fs=np.where(segh>=stop)[0]; ft=np.where(segl<=tgt)[0]
            fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
            if fstop==ftgt==10**9: continue
            sig.append((era(s0),(RR if ftgt<fstop else -1.0),dirn))
        return sig
    st=lambda a:(len(a),(np.mean([x>0 for x in a]) if len(a) else float('nan')),(np.mean([x-COST for x in a]) if len(a) else float('nan')))
    print("SESSION US-participation ORB (DST-correct anchors, 2R:1R, STRESS 0.24). P(cont)=winrate; net after cost.")
    for anc,name in [("us_macro","US 08:30 ET (macro)"),("nyse_open","NYSE 09:30 ET (equity open)")]:
        for RR in [2.0,3.0]:
            s=orb_at(anc,RR=RR); arr=np.array([x[1] for x in s]); yrs=[x[0] for x in s]
            if len(arr)<50: print(f"  {name} RR{RR}: n={len(arr)} thin"); continue
            N,wr,net=st(arr)
            byera={e:st(np.array([x[1] for x in s if x[0]==e])) for e in ["D","C","O"]}
            es=" ".join(f"{e}net={byera[e][2]:+.2f}(n{byera[e][0]})" for e in ["D","C","O"])
            flag=" <== net>0 ALL" if all(byera[e][2]>0 for e in ["D","C","O"]) else ""
            print(f"  {name:28s} RR{RR}: n={N:4d} WR={wr:.3f} netR={net:+.3f} | {es}{flag}")
    # family-4: does the 08:30->09:30 move continue past 09:30?
    cont=[]
    for day,idxs in byday.items():
        a830=amaps["us_macro"].get(day); a930=amaps["nyse_open"].get(day)
        if a830 is None or a930 is None: continue
        b830=[i for i in idxs if abs(ts[i]-a830)<450]; b930=[i for i in idxs if abs(ts[i]-a930)<450]
        if not b830 or not b930: continue
        i830=b830[0]; i930=b930[0]
        if i930>=n-HMAX or not np.isfinite(atr[i930]) or atr[i930]<=0: continue
        mv=np.sign(c[i930]-o[i830])  # 08:30->09:30 move direction
        if mv==0: continue
        # continuation after 09:30: does price extend in mv direction 1.5ATR before reversing?
        seg=slice(i930+1,i930+1+HMAX); a=atr[i930]
        if mv>0: fu=np.where(h[seg]-c[i930]>=1.5*a)[0]; fd=np.where(c[i930]-l[seg]>=1.5*a)[0]
        else: fu=np.where(c[i930]-l[seg]>=1.5*a)[0]; fd=np.where(h[seg]-c[i930]>=1.5*a)[0]
        f1=fu[0] if len(fu) else 10**9; f2=fd[0] if len(fd) else 10**9
        if f1==f2==10**9: continue
        cont.append((era(i930), f1<f2))
    allc=[x[1] for x in cont]
    print(f"\nFamily-4: after 09:30, does the 08:30->09:30 move CONTINUE? n={len(allc)} P(continue)={np.mean(allc):.3f} " +
          " ".join(f"{e}={np.mean([x[1] for x in cont if x[0]==e]):.2f}" for e in ["D","C","O"]))
    print("=> any anchor ORB net>0 cross-era = NEW time-anchored edge -> new identity + full gate. P(continue)>>0.5 cross-era = 09:30 continuation info.")
if __name__=="__main__": main()
