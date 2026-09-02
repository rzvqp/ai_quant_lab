"""cm_scan.py — CROSS_MARKET_RELATIVE_RESPONSE families A/B/C/E + controls (simple DXY impulse, beta). Next-H1-open entry, 2R, causal.
A CATCH-UP: DXY implied a move (|ez4|>1) but XAU under-reacted (|actual|<0.5|implied|) -> enter in implied dir.
B RELATIVE-STRENGTH: DXY implied down/up but XAU refused (residual z4 opposes implied, |z4|>1) -> enter with XAU's own strength.
C OVERSHOOT: XAU over-reacted (|az4|>2 and |actual|>1.8|implied|) -> fade.
E SESSION-RESOLUTION: dislocation (|z4|>1) at pre-London/NY bar -> enter at session in catch-up dir.
CONTROL_IMPULSE (§4): simple DXY impulse (|ez4|>1) -> implied dir, NO residual condition. CONTROL_BETA: random same-dir.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cm_core as CM
from tsm_core import independent_episodes

def run(E, fam):
    z4=E["z4"]; ez4=E["ez4"]; az4=E["az4"]; hr=E["hr"]; n=E["n"]; rows=[]
    for t in range(CM.W+5, n-1):
        if not (np.isfinite(z4[t]) and np.isfinite(ez4[t])): continue
        side=0
        if fam=="A":      # catch-up: implied real, XAU under-reacted (same sign but small)
            if abs(ez4[t])>1.0 and abs(az4[t])<0.5*abs(ez4[t]): side=int(np.sign(ez4[t]))
        elif fam=="B":    # relative strength: XAU opposes implied
            if abs(ez4[t])>1.0 and z4[t]>1.0 and ez4[t]<0: side=+1
            elif abs(ez4[t])>1.0 and z4[t]<-1.0 and ez4[t]>0: side=-1
        elif fam=="C":    # overshoot fade
            if abs(az4[t])>2.0 and abs(az4[t])>1.8*abs(ez4[t]): side=-int(np.sign(az4[t]))
        elif fam=="E":    # session resolution: dislocation before London(7-8 UTC) or NY(12-13 UTC)
            if hr[t] in (7,12) and abs(z4[t])>1.0 and abs(ez4[t])>0.5: side=int(np.sign(ez4[t]))
        elif fam=="CTRL_IMPULSE":
            if abs(ez4[t])>1.0: side=int(np.sign(ez4[t]))
        if side==0: continue
        r=CM.resolve(E,t+1,side,2.0,6)
        if r: r["side"]=side; rows.append(r)
    return rows

def summ(byera, label):
    allr=[r for E in byera.values() for r in E]
    if len(allr)<25: print(f"{label:22s} N={len(allr)} small"); return None
    net=np.array([r["net"] for r in allr]); g=np.array([r["g"] for r in allr])
    def eN(tag):
        rr=[r["net"] for era,rows in byera.items() for r in rows if CM.era_tag(era)==tag]
        return np.mean(rr) if rr else float('nan')
    print(f"{label:22s} N={len(net):5d} net={net.mean():+.3f} WR={(g>0).mean():.3f} "
          f"D(b0+b1)={eN('D'):+.3f} O(y2123)={eN('O'):+.3f} "
          f"[b0={np.mean([r['net'] for r in byera.get('b0',[])] or [np.nan]):+.3f} b1={np.mean([r['net'] for r in byera.get('b1',[])] or [np.nan]):+.3f} y2123={np.mean([r['net'] for r in byera.get('y2123',[])] or [np.nan]):+.3f}]")
    return net.mean()

def main():
    P=CM.prep()
    print(f"eras: {[ (e,P[e]['n']) for e in P]}")
    for fam,name in [("A","A.catch-up"),("B","B.relative-strength"),("C","C.overshoot-fade"),("E","E.session-resolution"),
                     ("CTRL_IMPULSE","CONTROL.simple-DXY-impulse")]:
        byera={era:run(E,fam) for era,E in P.items()}
        summ(byera,name)

if __name__=="__main__":
    main()
