"""BLINDED FEATURE VALUE BUILDER -- REDACTED COPY.

The executable original (values.py) implements all 46 features BY NAME and is deliberately NOT committed:
these repositories are mirrored and readable by every division, so committing it would defeat the blinding.
Held by the Statistician with feat.py, reblind.py and the BLIND_KEY; released at unblinding.

Published so the build is verifiable after the fact:
  BLINDED_FEATURE_VALUES_HASH = 2ea066c6a6a75705d7429ed9ad982430f1bfd02c5242760d43cf8f363cc7e871
  FEATURE_MAP_HASH            = 6cddeef6371fb42da7e4db5f5f936b7451727fae8673cc4414d5ab282ab5e943
  BLIND_KEY_HASH              = 268a4f1878ff15df81adba165f1786d320c15b62a148327f440eb3cf293f146f

METHOD:
 1. Panel = htf_context_historical.load_mstrat_historical() -- the Statistician-ratified gap-safe HTF
    context. Byte-identical columns and identical non-HTF values to mstrat.load(); HTF/PDH coverage
    23.7% -> 55.4%. Same feature definitions, better-covered source; NOT a redefinition.
 2. Compute the 46 frozen pre-entry features, all from bars <= the current bar.
 3. Apply the FROZEN binning: numeric -> quintile index 0..4 from a trailing-2000-bar causal percentile
    rank (rolling(2000, min_periods=500).rank(pct=True).shift(1)); bool -> 0/1; categorical -> declared
    level index. Bin edges come from the freeze and are never recomputed.
 4. Emit BIN INDICES ONLY (Int8). Raw values are deliberately withheld so threshold scanning is
    structurally impossible rather than merely prohibited.
 5. Rename to f001..f046 via the held-back keyed map; write parquet + metadata; hash.

CAUSALITY DEFECT FOUND AND FIXED DURING THE BUILD: the "bars remaining in the session block" feature
would have used the block's own total length, which is only known once the block ENDS. It is implemented
from the PREVIOUS completed block's length instead. The truncation test passes on it; the obvious
implementation would not have.

AUDIT: truncation test at bars 120,000 / 240,000 / 330,000 -- rebuild the whole pipeline on the truncated
panel and compare bar K-1 against the full-panel value. 43 panel features x 3 = 129 comparisons,
0 mismatches. No outcome field is read or produced anywhere in the original.
