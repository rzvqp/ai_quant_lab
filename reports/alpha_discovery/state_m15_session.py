"""state_m15_session.py — SESSION-conditioned M15 (§13, last untested family). Does session CONTEXT add a
tradeable, cross-era-stable path asymmetry on M15? Three tests, each measured vs the SESSION's own base
(not the global base), event-deduped, cross-era b0/b1:
  (1) session structural bias: is any session (Asia/London/NY) L- or S-skewed in P(+70/-50) 8h, cross-era?
  (2) session-open burst: do the first bars after each session open lift path odds vs the session base?
  (3) concentration of the ONE stable signal (high/rising-vol -> short) by session vs that session's base.
Price-only, causal, UTC hours. Sessions: Asia 0-7, London 7-13, NY 13-21, Off 21-24.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from state_m15_discover import feats, dedup

SESS=[("Asia",0,7),("London",7,13),("NY",13,21),("Off",21,24)]

def sess_mask(df,lo,hi):
    h=df["dt"].dt.hour.to_numpy(); return (h>=lo)&(h<hi)

def sess_base(ou,od,mask,H=32):
    return Pm(ou,od,70,50,'L',H,mask)[0], Pm(ou,od,70,50,'S',H,mask)[0]

def main():
    print("SESSION-conditioned M15: P(+70/-50) 8h vs SESSION base, event-deduped, cross-era.")
    m=sb.build_frames()["M15"]; dev=m["is_dev"].to_numpy()
    ou,od,_,_=passage_m15(m); F=feats(m)
    h=m15d.build(verbose=False)["M15"]; b0=h["is_b0"].to_numpy(); b1=h["is_b1"].to_numpy()
    ou2,od2,_,_=passage_m15(h); F2=feats(h)
    hv =((F["vr"]>1.3)|(F["vc"]>1.2)); hv =np.nan_to_num(hv.astype(float),nan=0).astype(bool)
    hv2=((F2["vr"]>1.3)|(F2["vc"]>1.2));hv2=np.nan_to_num(hv2.astype(float),nan=0).astype(bool)

    # (1) session structural bias vs GLOBAL deduped base (is a session itself L/S skewed?), cross-era
    gL=Pm(ou,od,70,50,'L',32,dev&dedup(np.ones(len(m),bool)))[0]; gS=Pm(ou,od,70,50,'S',32,dev&dedup(np.ones(len(m),bool)))[0]
    g0L=Pm(ou2,od2,70,50,'L',32,b0&dedup(np.ones(len(h),bool)))[0]; g0S=Pm(ou2,od2,70,50,'S',32,b0&dedup(np.ones(len(h),bool)))[0]
    g1L=Pm(ou2,od2,70,50,'L',32,b1&dedup(np.ones(len(h),bool)))[0]; g1S=Pm(ou2,od2,70,50,'S',32,b1&dedup(np.ones(len(h),bool)))[0]
    print(f"\n(1) SESSION structural bias vs global base (DEV L={gL:.3f}/S={gS:.3f})")
    for nm,lo,hi in SESS:
        d=dev&sess_mask(m,lo,hi)&dedup(np.ones(len(m),bool))
        z0=b0&sess_mask(h,lo,hi)&dedup(np.ones(len(h),bool)); z1=b1&sess_mask(h,lo,hi)&dedup(np.ones(len(h),bool))
        if d.sum()<60: continue
        sL=Pm(ou,od,70,50,'L',32,d)[0]-gL; sS=Pm(ou,od,70,50,'S',32,d)[0]-gS
        s0L=Pm(ou2,od2,70,50,'L',32,z0)[0]-g0L; s0S=Pm(ou2,od2,70,50,'S',32,z0)[0]-g0S
        s1L=Pm(ou2,od2,70,50,'L',32,z1)[0]-g1L; s1S=Pm(ou2,od2,70,50,'S',32,z1)[0]-g1S
        fl="";
        if abs(sL)>=0.03 and np.sign(sL)==np.sign(s0L)==np.sign(s1L) and abs(s0L)>=0.02 and abs(s1L)>=0.02: fl+=" L_CROSS_STABLE"
        if abs(sS)>=0.03 and np.sign(sS)==np.sign(s0S)==np.sign(s1S) and abs(s0S)>=0.02 and abs(s1S)>=0.02: fl+=" S_CROSS_STABLE"
        print(f"   {nm:7s} N={int(d.sum()):5d} L={sL:+.3f}(b0{s0L:+.2f}/b1{s1L:+.2f}) S={sS:+.3f}(b0{s0S:+.2f}/b1{s1S:+.2f}){fl}")

    # (2) session-open burst: first 4 M15 bars after session start (open volatility), vs that session base
    print(f"\n(2) SESSION-open first 4 bars vs that session's base")
    for nm,lo,hi in SESS:
        smk=sess_mask(m,lo,hi); openb=smk&(m["dt"].dt.hour.to_numpy()==lo)&(m["dt"].dt.minute.to_numpy()<60)
        d=dev&smk; base=sess_base(ou,od,d&dedup(np.ones(len(m),bool)))
        z0m=b0&sess_mask(h,lo,hi); z1m=b1&sess_mask(h,lo,hi)
        b0base=sess_base(ou2,od2,z0m&dedup(np.ones(len(h),bool))); b1base=sess_base(ou2,od2,z1m&dedup(np.ones(len(h),bool)))
        ob=dev&openb&dedup(np.ones(len(m),bool)); n=int(ob.sum())
        if n<40: print(f"   {nm:7s} open N={n}(thin)"); continue
        oL=Pm(ou,od,70,50,'L',32,ob)[0]-base[0]; oS=Pm(ou,od,70,50,'S',32,ob)[0]-base[1]
        ob0=b0&(h["dt"].dt.hour.to_numpy()==lo)&dedup(np.ones(len(h),bool)); ob1=b1&(h["dt"].dt.hour.to_numpy()==lo)&dedup(np.ones(len(h),bool))
        o0L=Pm(ou2,od2,70,50,'L',32,ob0)[0]-b0base[0]; o0S=Pm(ou2,od2,70,50,'S',32,ob0)[0]-b0base[1]
        o1L=Pm(ou2,od2,70,50,'L',32,ob1)[0]-b1base[0]; o1S=Pm(ou2,od2,70,50,'S',32,ob1)[0]-b1base[1]
        print(f"   {nm:7s} open N={n:4d} L={oL:+.3f}(b0{o0L:+.2f}/b1{o1L:+.2f}) S={oS:+.3f}(b0{o0S:+.2f}/b1{o1S:+.2f})")

    # (3) high/rising-vol -> SHORT concentration by session vs that session's SHORT base
    print(f"\n(3) high-vol -> SHORT lift by session vs that session's SHORT base (does the one stable signal concentrate?)")
    for nm,lo,hi in SESS:
        smk=sess_mask(m,lo,hi); d=dev&smk; sb_=sess_base(ou,od,d&dedup(np.ones(len(m),bool)))[1]
        cond=dev&smk&hv&dedup(dev&smk&hv); n=int(cond.sum())
        z0m=b0&sess_mask(h,lo,hi); z1m=b1&sess_mask(h,lo,hi)
        s0b=sess_base(ou2,od2,z0m&dedup(np.ones(len(h),bool)))[1]; s1b=sess_base(ou2,od2,z1m&dedup(np.ones(len(h),bool)))[1]
        if n<40: print(f"   {nm:7s} hv-short N={n}(thin)"); continue
        v =Pm(ou,od,70,50,'S',32,cond)[0]-sb_
        c0=b0&sess_mask(h,lo,hi)&hv2&dedup(b0&sess_mask(h,lo,hi)&hv2); c1=b1&sess_mask(h,lo,hi)&hv2&dedup(b1&sess_mask(h,lo,hi)&hv2)
        v0=Pm(ou2,od2,70,50,'S',32,c0)[0]-s0b; v1=Pm(ou2,od2,70,50,'S',32,c1)[0]-s1b
        fl=" S_CROSS_STABLE" if (abs(v)>=0.03 and np.sign(v)==np.sign(v0)==np.sign(v1) and abs(v0)>=0.02 and abs(v1)>=0.02) else ""
        print(f"   {nm:7s} hv-short N={n:4d} lift={v:+.3f} (b0{v0:+.2f}/b1{v1:+.2f}){fl}")

if __name__=="__main__":
    main()
