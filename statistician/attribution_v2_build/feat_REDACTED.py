"""FEATURE INVENTORY BUILDER -- REDACTED COPY.

The executable original enumerates the 46 pre-entry features by name and is deliberately NOT committed:
these repositories are mirrored and readable by every division, so committing the name list would defeat
the blinding this protocol exists to provide.

Held by the Statistician, released at unblinding:
    feat.py      -- the feature derivation + name list
    reblind.py   -- the keyed permutation that assigns f001..f046
    BLIND_KEY    -- the permutation key

Published here instead, so the freeze is verifiable after the fact:
    FEATURE_MAP_HASH = 6cddeef6371fb42da7e4db5f5f936b7451727fae8673cc4414d5ab282ab5e943
    BLIND_KEY_HASH   = 268a4f1878ff15df81adba165f1786d320c15b62a148327f440eb3cf293f146f

METHOD (fully described so it is reproducible at unblinding):
 1. Enumerate the governed feature module mstrat.load() -- 54 columns, 355,696 rows, lookahead-safe by
    construction -- and classify every column.
 2. Declare 46 deterministic causal pre-entry derivations of it (level distances in ATR units, range
    locations, volatility state, returns/efficiency, run lengths, volume ratios, session position,
    H1/H4/D1 states and alignment, imbalance/displacement flags, clock and calendar variables).
    NO feature was taken from the wording of any prompt.
 3. Assign blind ids by sorting on sha256(KEY + true_name) -- a keyed permutation, not alphabetical order.
    (An earlier draft sorted alphabetically; that is reconstructable from a guessed name list and was
    replaced before anything was committed.)
 4. Publish only BLIND_ID / KIND / CLASS / N_BINS.

DECLARED RESIDUAL LEAK: 4 of the 46 carry a unique bin count (4, 12, 24, 48) and are therefore
identifiable from FEATURE_BINNING.csv alone. Blinding is PARTIAL, not perfect. The compensating control
is in the protocol: for those four, the shuffle placebo must accompany the primary result, and the rank
of every prompt-mentioned condition among all 46 must be reported.
