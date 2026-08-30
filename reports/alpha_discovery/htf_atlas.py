"""htf_atlas.py — H1/H4 setup atlas + contrast census: for each family, HTF_ON baseline net-R + direction x era breakdown +
independent episodes. Produces the numbers for H1_H4_SETUP_ATLAS_V1 / CONTRAST_REPORT_V1. Cross-era sign-stability is the gate.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
from htf_setups import prep, detect, evaluate
from tsm_core import independent_episodes

def main():
    m,H1,H4=prep()
    yrs=m["dt"].dt.year.values
    for fam in ["PBK_TREND","RECLAIM","RANGE_FADE","TGT_BREAK"]:
        on=evaluate(m,detect(m,H1,H4,fam,htf_on=True))
        off=evaluate(m,detect(m,H1,H4,fam,htf_on=False))
        if len(on)<20: print(f"\n{fam}: HTF_ON N={len(on)} too small"); continue
        ent=np.array([r["ent"] for r in on]); side=np.array([r["side"] for r in on])
        net=np.array([r["net_R"] for r in on]); g=np.array([r["gross_R"] for r in on])
        era=np.where(yrs[ent]<=2018,"D",np.where(yrs[ent]<=2022,"C","O"))
        ieH4=len(independent_episodes(ent,H=16*4))   # ~ H4-episode spacing (16 M15 bars/H4 *4 = 64)
        offnet=np.array([r["net_R"] for r in off]).mean() if len(off)>=20 else float('nan')
        print(f"\n=== {fam} === HTF_ON N={len(on)} ie~{ieH4} netR={net.mean():+.3f} (HTF_OFF netR={offnet:+.3f}) WR={(g>0).mean():.3f}")
        for d,dn in [(+1,"LONG"),(-1,"SHORT")]:
            cells=[]
            for e in ["D","C","O"]:
                mk=(side==d)&(era==e)
                cells.append(f"{e}:{net[mk].mean():+.3f}(N{mk.sum()})" if mk.sum()>=15 else f"{e}:--")
            allmk=(side==d)
            print(f"   {dn:5s} all={net[allmk].mean():+.3f}(N{allmk.sum():4d})  "+"  ".join(cells))
    print("\nGATE: a candidate needs a cross-era SIGN-STABLE positive cell. Sign-reversal across D/C/O => R20 era-trend artifact => FALSIFIED.")

if __name__=="__main__":
    main()
