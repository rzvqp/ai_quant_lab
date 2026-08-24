"""state_session.py — session-conditioned state family. Does entering the H1 path in a given UTC session
(Asia/London/NY), optionally x HTF-trend, change P(+100/-70) L/S stably (DEV per-year+DISC/CONF) AND cross-pop
(b0/b1)? Price-only, causal. Completes the state-information map before the bounded conclusion."""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd
from state_validate import passage, P
SESS={"Asia(0-7)":(0,7),"London(7-13)":(7,13),"NY(13-21)":(13,21)}
def lift(up,dn,side,bm,cm):
    b,_=P(up,dn,100,70,side,48,bm); c,nc=P(up,dn,100,70,side,48,cm); return c-b,nc
def main():
    tfs=sb.build_frames(); h1=tfs["H1"]; dev=h1["is_dev"].to_numpy(); yr=h1["dt"].dt.year.to_numpy(); hr=h1["dt"].dt.hour.to_numpy()
    up,dn=passage(h1); idx=np.where(dev)[0]; cut=idx[int(len(idx)*0.6)]
    disc=dev&(np.arange(len(h1))<cut); conf=dev&(np.arange(len(h1))>=cut)
    hh1=hd.load()["H1"]; up2,dn2=passage(hh1); hr2=hh1["dt"].dt.hour.to_numpy(); b0=hh1["is_b0"].to_numpy(); b1=hh1["is_b1"].to_numpy()
    print("session-conditioned screen: enter-in-session -> H1 P(+100/-70) H48 lift. DEV(yr,DISC,CONF)+cross-pop b0/b1.")
    for name,(a,b) in SESS.items():
        cond=(hr>=a)&(hr<b); cond2=(hr2>=a)&(hr2<b)
        print(f"  {name}: N_dev={int((dev&cond).sum())}")
        for side in ("L","S"):
            ld,nc=lift(up,dn,side,dev,dev&cond); dl,_=lift(up,dn,side,disc,disc&cond); cl,_=lift(up,dn,side,conf,conf&cond)
            py=[(lift(up,dn,side,dev&(yr==y),dev&(yr==y)&cond)[0] if (dev&(yr==y)&cond).sum()>=40 else None) for y in (2021,2022,2023)]
            lb0,_=lift(up2,dn2,side,b0,b0&cond2); lb1,_=lift(up2,dn2,side,b1,b1&cond2)
            devstable=(abs(ld)>=0.03 and np.sign(dl)==np.sign(ld) and np.sign(cl)==np.sign(ld) and all(np.sign(v)==np.sign(ld) for v in py if v is not None))
            cross=devstable and np.sign(lb0)==np.sign(ld) and np.sign(lb1)==np.sign(ld) and abs(lb0)>=0.02 and abs(lb1)>=0.02
            pys=" ".join(f"{y}:{('%.2f'%v) if v is not None else 'na'}" for y,v in zip((2021,2022,2023),py))
            print(f"     {side}: DEVlift={ld:+.3f}(n{nc}) DISC={dl:+.2f} CONF={cl:+.2f} yr[{pys}] | b0={lb0:+.3f} b1={lb1:+.3f}"+(" <== CROSS_STABLE" if cross else (" (dev-stable)" if devstable else "")))
if __name__=="__main__":
    main()
