"""S21.7: does M5-timed entry improve the H4 transition candidate? Coarse H4 entry vs M5 momentum entry,
SAME H4 SL + SAME H4 TP. Only entry timing differs."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import transition_campaign as TC
tfs=TC.tfs; PIP=TC.PIP; RT=TC.RT
H4=tfs["H4"]; M5=tfs["M5"]
h4o=H4["open"].to_numpy();h4h=H4["high"].to_numpy();h4l=H4["low"].to_numpy();h4atr=H4["atr"].to_numpy();h4ct=H4["close_time"].to_numpy();h4dev=H4["is_dev"].to_numpy()
m5t=M5["time"].to_numpy();m5o=M5["open"].to_numpy();m5h=M5["high"].to_numpy();m5l=M5["low"].to_numpy();m5c=M5["close"].to_numpy();n5=len(M5)
RR=1.5;MAXH=48*48  # 48 H4 bars in M5
def walk(ej,side,stop,tgt):
    if ej<=0 or ej>=n5-1: return None
    e=m5o[ej];end=min(ej+MAXH,n5);ex=None
    for j in range(ej,end):
        if side>0:
            if m5l[j]<=stop: ex=stop;break
            if m5h[j]>=tgt: ex=tgt;break
        else:
            if m5h[j]>=stop: ex=stop;break
            if m5l[j]<=tgt: ex=tgt;break
    if ex is None: ex=m5c[end-1]
    return e,ex
A=[];B=[]
for (i,side) in TC.gen("rng2trend_disponly",True,"H4"):
    if not h4dev[i]: continue
    a=h4atr[i];stop=min(h4l[i-3:i+1])-0.15*a
    jr=int(np.searchsorted(m5t,h4ct[i],side="right"))
    if jr<=0 or jr>=n5-1: continue
    er=m5o[jr];risk=abs(er-stop)
    if not (risk>0) or stop>=er: continue
    tgt=er+RR*risk
    wa=walk(jr,1,stop,tgt)
    if wa: A.append((1*(wa[1]-wa[0])-RT["STRESS"])/risk)
    # M5 momentum entry: first M5 up-momentum bar within next 48 M5 bars (into the trend)
    ej=None
    for j in range(jr,min(jr+48,n5-2)):
        if m5c[j]>m5o[j] and m5c[j]>m5c[j-1]: ej=j+1;break
    if ej:
        wb=walk(ej,1,stop,tgt)
        if wb: B.append((1*(wb[1]-wb[0])-RT["STRESS"])/risk)
A=np.array(A);B=np.array(B)
print(f"COARSE H4 entry: n={len(A)} avgR={A.mean():.4f} WR={np.mean(A>=RR-0.05):.3f}")
print(f"M5 momentum entry (same H4 SL/TP): n={len(B)} avgR={B.mean():.4f} WR={np.mean(B>=RR-0.05):.3f}")
print(f"=> M5 entry value dAvgR={B.mean()-A.mean():.4f} -> {'M5 ADDS value' if B.mean()>A.mean() else 'M5 does NOT add value (coarse >= M5)'}")
