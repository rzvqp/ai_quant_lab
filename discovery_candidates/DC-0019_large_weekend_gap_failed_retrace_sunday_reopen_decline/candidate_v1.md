# Discovery Candidate DC-0019: A Weekend Gap Nearly Double the Prior Record Fails to Retrace, Extending Into a Sustained Sunday-Reopen Decline Before a Partial Recovery

## Metadata

- **candidate_id**: DC-0019
- **title**: A Weekend Gap Nearly Double the Prior Record Fails to Retrace, Extending Into a Sustained Sunday-Reopen Decline Before a Partial Recovery
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-24
- **date_frozen**: 2026-07-24
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5
- **data_split_id**: post_holdout_reopened_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00 (original cutoff; this candidate's data postdates it under the CEO's explicit window-reopening authorization — see note below)
- **source_artifacts**: 2025-10-24 21:45 UTC -> 2025-10-26/27 (Sun/Mon) ~02:15 UTC, OANDA:XAUUSD M15/M5 replay window
- **related_ids**: DC-0013 (NY-session sustained multi-candle decline family, established 9-12k+ volume band), DC-0016 (also immediately followed a weekend gap, but a small one that retraced quickly — direct contrast), OBS-0015 (statistical weekend-gap-fill-rate finding, H1, n=148 — this instance runs counter to that base rate at the single-instance level)
- **content_hash**: sha256:4130deed316f517237f3473b5bbb1730df0c2c5e560e0ec25083a705814391d8

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

The last M15 candle before the weekend close (Friday 2025-10-24, 21:45-22:00 UTC) closed at
4114.125. After the usual weekend market closure (replay advanced ~49.25h in a single step,
consistent with the 9 prior weekend-gap instances already logged in this replay), the Sunday
reopen candle (2025-10-26, 22:00-22:15 UTC) opened at 4085.70 — a **28.425-point gap down**, by a
wide margin the largest weekend-gap magnitude observed in this replay (previous record ~15.7pt,
2025-10-10 -> 10-12; the other 8 instances ranged from near-zero to a few points).

The reopen candle's intrabar high (4107.575) came within 6.55pt of a full gap-fill and it closed at
4104.84 — at that point indistinguishable from the pattern shared by all 9 prior instances (a quick
partial-or-full retrace). The next two M15 candles broke that pattern: close 4091.765, then close
4080.405 — the latter trading **below the original gap-open print itself**, meaning the move did
not merely fail to fill, it extended past the opening discontinuity. The decline continued for
roughly 9 M15 candles total (22:15 UTC Sunday to about 00:15 UTC Monday, ~2 hours), reaching an
intrabar low of 4058.205 and a closing low of 4064.665 — approximately 55.9pt below Friday's
pre-gap close (49.5pt close-to-close), and roughly 21-27pt beyond the gap-open print itself.
Volume through the decline ran roughly 4.7k-8.5k per M15 candle — moderate, but notably below the
9-12k+ band established for the NY-session sustained-decline family (DC-0013).

Three candles of stabilization followed (roughly 00:15-01:00 UTC), essentially flat with fading
volume (~3.3k-4.7k). A recovery then began: the first recovery candle closed 4090.195 on 13,384
volume (the single largest M15 volume print in the entire sequence), extending to an intrabar high
of 4097.87 before settling into an oscillation between roughly 4088 and 4098 through the end of the
observed window (current_date 1761529499, ~02:15 UTC Monday). This recovers only about 30-33 of the
~50-56 points lost — a **partial**, not full, recovery; price remains well short of the original
4114.125 pre-gap level.

Dropping to M5 across the decline leg confirmed distributed, organic construction: volume per
5-minute bar ran roughly 1,100-4,800 with no single candle dominating any M15 bar, matching the
"sustained, distributed" construction already catalogued in DC-0008/DC-0013/DC-0014/DC-0015/DC-0016,
not a single-minute concentrated spike. (The very first M5 print of the session carried only 57
volume — a thin/incomplete opening tick, consistent with a known artifact pattern at session
reopens, and immaterial next to the M15 aggregate's 8,561.)

## 2. Why It Attracted Attention

Nine prior weekend-gap instances in this replay (magnitudes 0 to ~-15.7pt) shared one uniform
resolution: a quick partial-or-full retrace within the first 1-2 M15 candles, then normal trading
resumed. This 10th instance diverges from that precedent on two dimensions at once — magnitude
(nearly double the prior record) and resolution style (an initial retrace attempt that failed and
reversed into a sustained ~2-hour continuation in the gap's direction, trading beyond the gap-open
print itself before eventually stabilizing and partially recovering). The v2 filter's escalation
criteria (novel dimension, or exceeds documented magnitude) were both met, and the event was watched
through to a clear resolution point (decline -> stabilization -> partial recovery) before writing
this candidate, rather than reacting to the gap candle alone.

## 3. Why It May Repeat

The underlying construction mechanism of the decline leg itself (sustained, distributed multi-minute
volume, no single-candle concentration) is the same family already catalogued in DC-0008/DC-0013/
DC-0014/DC-0015/DC-0016. What is new is the specific combination: a large weekend gap acting as an
apparent catalyst for a sustained continuation move, occurring in the low-liquidity Sunday-evening/
early-Monday-Asia reopen window rather than the NY session, and at a volume band (4.7k-8.5k) below
DC-0013's established 9-12k+ threshold. This raises a testable question -- does weekend-gap
magnitude predict resolution style (small gaps fill quickly, as in all 9 prior instances; large gaps
risk continuation instead)? -- but this rests on a single instance and should not be treated as
established.

## 4. Why It Deserves Further Investigation

This is the first instance in this replay where a weekend gap failed to retrace and instead
extended into a multi-candle directional move large enough to rival the DC-0013/DC-0014/DC-0015/
DC-0016 family in magnitude (~50-56pt) and duration (~2 hours), despite occurring in a session
(Sunday reopen/early Asia) and volume band (sub-9k) distinct from that family's NY-session,
9-12k+ characterization. Comparing this instance against any future large-magnitude weekend gaps —
does the failed-retrace-then-continuation shape recur, and does gap size predict it — is a natural
next step. It is also worth comparing this instance's session/volume profile against DC-0016
(early-Asia/pre-London, also post-weekend-gap, but that gap was small and retraced normally), to
see whether the weekend-gap-adjacent Sunday/Monday reopen window has any distinct behavior beyond
the immediate gap event itself.

## 5. Confidence

**Low.** A single instance of "large weekend gap -> failed retrace -> sustained continuation ->
partial recovery." The decline leg's construction mechanism has ample precedent, but the triggering
condition (gap magnitude), the session (Sunday reopen, not NY), and the volume band (sub-9k) are all
new relative to the established sustained-decline family, and this rests on n=1.

## Additional Notes (optional)

This candidate's observation window falls after the original holdout_cutoff (2025-10-23T09:15 UTC)
that governed the prior Alpha Discovery window. It was observed under the CEO's explicit decision to
resume Alpha Discovery past that cutoff in a reopened window; existing Discovery Candidates and
Addenda from the pre-cutoff window were not modified or recreated. No comparison against the
Knowledge Base or any validation step was performed, consistent with Alpha's observation-only
mandate — this candidate makes no claim about whether the pattern is exploitable, only that it was
observed and differs structurally from the prior 9 weekend-gap instances and from OBS-0015's
higher-timeframe statistical framing (93.2% fill rate, H1, n=148, which this single M15 instance
runs counter to without contradicting — different timeframe, different sample size, hedged
explicitly).

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-24**. Content hash: **sha256:4130deed316f517237f3473b5bbb1730df0c2c5e560e0ec25083a705814391d8**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file — never as an edit to this
file.
