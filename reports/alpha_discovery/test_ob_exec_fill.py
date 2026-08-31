"""test_ob_exec_fill.py — PERMANENT regression test for the OBR-BULL-1 same-bar fill artifact (Statistician finding, §3).

The artifact: a resting BUY limit at block_high was cancelled ('no trade') when the SAME bar closed below block_low, instead of being
counted as a filled same-bar LOSS. Dropping those losers inflated net-R from the true ~-0.067R to +0.154R.

This test freezes the finding: the buggy fill must report materially higher net-R than the corrected true-resting-limit fill, and the
corrected fill must be non-positive (falsified). Run: python test_ob_exec_fill.py
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import ob_core as OB, ob_exec as EX

def _net(rows): return float(np.mean([r["net"] for r in rows]))

def main():
    m,H1,H4,P=OB.build()
    old=EX.collect(P,m,"OLD"); a=EX.collect(P,m,"A")
    old_net=_net(old); a_net=_net(a)
    print(f"OLD buggy fill net={old_net:+.4f} N={len(old)}")
    print(f"EXEC_A corrected net={a_net:+.4f} N={len(a)}")
    # 1. artifact reproduced: buggy is materially more optimistic
    assert old_net - a_net > 0.15, f"artifact not reproduced: old {old_net} vs corrected {a_net}"
    # 2. corrected true-limit is non-positive (OBR-BULL-1 falsified as tradeable)
    assert a_net <= 0.0, f"corrected fill should be non-positive, got {a_net}"
    # 3. the buggy fill drops trades that the corrected fill keeps (same-bar filled-then-closed-below losers)
    assert len(a) > len(old), f"corrected should keep >= buggy trade count (kept {len(a)} vs {len(old)})"
    # 4. corrected reproduces the Statistician figure ~ -0.067 within tolerance
    assert abs(a_net - (-0.067)) < 0.03, f"corrected net {a_net} should match Statistician -0.067"
    print("PASS: OLD_FILL_ARTIFACT_REPRODUCED=YES ; OLD_OBR_BULL_1_REMAINS_FALSIFIED=YES ; corrected matches Statistician -0.067")

if __name__=="__main__":
    main()
