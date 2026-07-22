# Discovery Candidate DC-0004: New-York-Session Prior-Day-High Sweep-Reject Is Followed By Reversion

## Metadata

- **candidate_id**: DC-0004
- **title**: New-York-Session Prior-Day-High Sweep-Reject Is Followed By Reversion
- **origin_mode**: systematic observation + descriptive analysis, Alpha autonomous research (OBS-0001 → 0003 → 0008 → 0012 → 0013)
- **date_first_observed**: 2026-07-22
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: H1 (event and outcome), daily (prior-day levels)
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: `research_log/OBS-0001`, `OBS-0003`, `OBS-0008`, `OBS-0012`, `OBS-0013` + scripts `obs0003_session_reject.py`, `obs0008_ny_reject_null.py`, `obs0012_reject_allcells_null.py`, `obs0013_ny_stability.py`. Data 2023-01-02 → 2025-10-23, 16,623 H1 bars.
- **related_ids**: K01 (raw sweeps without confirmation are non-positive; conditioned sweeps are where content may live); E017; OBS-0004 (sweep depth uninformative)
- **content_hash**: sha256:c42c8d7c646a86c2f242e25267df02a86fb2c01f88236e1a1fbacc4dd86141bb
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `PENDING`

## 1. Observation

On XAUUSD H1, the first bar of a day whose **high exceeds the prior-day high but which closes back below
it** (a "sweep-reject" of the prior-day high) is followed by **reversion** — but **only when that event
occurs during the New York session**. In other sessions the same event shows no reversion, and on the
Asia/London side the sign is reversed.

Measured against the NY session's *own* forward baseline (not global drift):
- K6 continuation-excess **−3.64**, CI95 **[−6.90, −0.12]** (excludes zero), matched-null left-tail **p = 0.021**
- K12 continuation-excess **−4.80**, CI95 [−8.88, +0.05], matched-null p = 0.029
- P(continuation) = 0.36 at K6, 0.26 at K12; n = 42

Across all six session × direction reject cells, NY-up-reject is the **only** cell reaching nominal
significance (next best p = 0.36). It is **sign-stable** across both temporal halves (2023–24: −3.25,
n=29; 2025: −4.65, n=13).

## 2. Why It Attracted Attention

It emerged from the wreckage of a negative result. OBS-0001 established that the generic sweep-reject vs
break-hold distinction is not supported at the 1–6h horizon. Splitting by session revealed that the
generic null concealed strongly *heterogeneous* behaviour — the NY cell pointed one way while Asia and
London pointed the other, cancelling in aggregate.

## 3. Why It May Repeat

Descriptively: prior-day highs are widely-watched reference levels, and the NY session is when the
largest scheduled participation and liquidity arrives. A level being taken and rejected during the
session with the most participation plausibly reflects a different population of activity than the same
geometry occurring in thin Asian hours. No causal claim is made.

## 4. Why It Deserves Further Investigation

It is precisely specified (level, event definition, session window, horizon), it survived a
pre-registered same-data matched null, it is uniquely distinguished among all tested cells rather than
being one of many, and it is temporally sign-stable. It also sits exactly where lab claim **K01** says
content might live: raw sweeps are dead, *conditioned* sweeps are the open question.

## 5. Confidence

**Medium-low.**

Opposing evidence recorded deliberately:
- **Fails Bonferroni.** p = 0.021 against a corrected threshold of 0.0083 across the 6 cells tested.
- **Selection**: the cell was chosen after inspecting ~12 session × direction cells in OBS-0003, so the
  matched-null p is not selection-corrected.
- **n = 42**, and only 13 events in the second temporal half; per-half CIs both include zero.
- Entirely in-sample; the reserved holdout has never been touched for this.
- **OBS-0004** showed sweep *depth* carries no information, so no depth-based refinement is available.

## Additional Notes (optional)

The decisive test is out-of-sample confirmation on the reserved holdout (post 2025-10-23), which is a
CEO-gated resource and has deliberately not been spent.

## Handoff Statement

Submitted to Red Team as a descriptive observation only. **Not** validated, **not** an edge, **not** a
strategy, no profitability claim. Content hash: sha256:c42c8d7c646a86c2f242e25267df02a86fb2c01f88236e1a1fbacc4dd86141bb.
