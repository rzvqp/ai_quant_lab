"""voltime_session.py — VOLTIME-4: S5-generalization. S5 (frozen) = NY-open opening-range breakout. Test whether a SECOND
session-timing edge exists: opening-range breakout at the LONDON open and ASIA open (NY shown read-only as an S5 reference/positive
control — S5's frozen definition is NOT touched or promoted). OR = first 4 M15 bars (1h) after the session open; entry on first close
beyond OR hi/lo within the session window; stop=opposite OR extreme -/+0.1ATR; target=+RR*risk; one trade per session/day. Direction
supplied by the break (non-directional frontier). STRESS 0.24. Cross-era gate. A London/Asia edge surviving costs cross-era + S5-
independent = genuine second edge for the router."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
COST=0.24; HMAX=48
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy(); hr=m["dt"].dt.hour.to_numpy(); mn=m["dt"].dt.minute.to_numpy()
    day=m["dt"].dt.date.to_numpy()
    # index bars by day
    from collections import defaultdict
    dayrows=defaultdict(list)
    for i in range(n): dayrows[day[i]].append(i)
    def run(open_hr, RR=2.0, orbars=4, winbars=24, buf=0.1):
        sig=[]
        for d,idxs in dayrows.items():
            # OR window = first `orbars` M15 bars at/after open_hr:00
            orr=[i for i in idxs if hr[i]==open_hr]
            if len(orr)<orbars: continue
            orr=orr[:orbars]; s0=orr[0]
            if s0<250 or s0>=n-HMAX-winbars-2: continue
            ohi=max(h[i] for i in orr); olo=min(l[i] for i in orr); a=atr[orr[-1]]
            if not np.isfinite(a) or a<=0: continue
            entry_i=orr[-1]+1; brk=None
            for j in range(entry_i, min(entry_i+winbars, n-2)):
                if c[j]>ohi: brk=(j,1); break
                if c[j]<olo: brk=(j,-1); break
            if brk is None: continue
            j,dirn=brk; ei=j+1
            if ei>=n-HMAX: continue
            entry=o[ei]; stop=(olo-buf*a) if dirn>0 else (ohi+buf*a); risk=abs(entry-stop)
            if risk<=0.05*a: continue
            tgt=entry+RR*risk*dirn; seg_l=l[ei:ei+HMAX]; seg_h=h[ei:ei+HMAX]
            if dirn>0: fs=np.where(seg_l<=stop)[0]; ft=np.where(seg_h>=tgt)[0]
            else: fs=np.where(seg_h>=stop)[0]; ft=np.where(seg_l<=tgt)[0]
            fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
            if fstop==ftgt==10**9: continue
            sig.append((yr[s0],(RR if ftgt<fstop else -1.0),dirn))
        return sig
    st=lambda a:(len(a),(np.mean([x>0 for x in a]) if len(a) else float('nan')),(np.mean(a) if len(a) else float('nan')),(np.mean([x-COST for x in a]) if len(a) else float('nan')))
    print("VOLTIME-4 opening-range breakout by session (STRESS 0.24, RR=2). NY = S5 reference (frozen, read-only).")
    for name,ohr in [("ASIA(00h)",0),("LONDON(07h)",7),("LONDON(08h)",8),("NY-ref(13h)",13),("NY-ref(14h)",14)]:
        for RR in [2.0,3.0]:
            s=run(ohr,RR=RR)
            if not s: print(f"  {name} RR{RR}: 0 sig"); continue
            arr=np.array([x[1] for x in s]); yrs=np.array([x[0] for x in s])
            N,wr,g,net=st(arr)
            e=lambda mk: st(arr[mk])[3]
            dD=e(yrs<=2018); dC=e((yrs>=2019)&(yrs<=2022)); dO=e(yrs>=2023)
            flag=" <== cross-era NET+" if (net>0 and dD>0 and dC>0 and dO>0) else ""
            print(f"  {name:12s} RR{RR}: n={N:4d} WR={wr:.3f} grossR={g:+.3f} netR={net:+.3f} | D={dD:+.2f} C={dC:+.2f} O={dO:+.2f}{flag}")
    print("\n=> a LONDON/ASIA cell with netR>0 AND D/C/O all>0 = candidate SECOND session-timing edge -> preregister + full gate + S5-independence.")
if __name__=="__main__": main()
