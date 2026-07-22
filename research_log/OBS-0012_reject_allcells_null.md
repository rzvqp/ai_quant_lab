# OBS-0012 — Selection correction for the NY reject lead (all-cells matched null)
Type: Observation Record. **NOT a Discovery Candidate.** Date 2026-07-22 · XAUUSD H1 · loader · 6 reject cells · corrects OBS-0008.

**Q:** Is NY up-reject uniquely significant, or one of many cells that looks good by chance?
**Pre-reg:** matched-null left-tail p for every session×direction reject cell (n≥25); Bonferroni thr = 0.05/6 = 0.0083.

**Result:** `up-reject/NY p=0.0253` is the **only** cell below nominal 0.05; the other five are resoundingly null (next best p=0.36). But 0.0253 **> Bonferroni 0.0083** → does not survive correction.

**Verdict: the lead is UNIQUELY DISTINGUISHED but NOT statistically validated.** It is the sole standout (raising it above "one-of-many chance"), yet fails formal multiple-testing correction and n=42 is small, in-sample. Correct action: do **not** freeze a candidate; test temporal stability (OBS-0013) and reserve the holdout as the decisive gate.
