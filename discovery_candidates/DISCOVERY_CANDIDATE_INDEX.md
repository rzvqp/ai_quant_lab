# Discovery Candidate Index

Master, authoritative registry of every Discovery Candidate ID ever assigned. An ID is reserved
the moment its folder is created and is never reused, even if the candidate is later withdrawn or
rejected -- its row stays, marked with its final status, rather than being deleted.

This is the **only** place where a candidate's *current* lifecycle status is recorded. Frozen
candidate documents never contain a live status field themselves -- see
`DISCOVERY_CANDIDATE_TEMPLATE.md`'s Metadata section.

**Lifecycle status values** (fixed set):
`OBSERVED` -> `FROZEN` -> `UNDER_REVIEW` -> `REJECTED` | `SURVIVED_RED_TEAM` -> `SENT_TO_FLOW_C`

Alpha sets `OBSERVED` at creation and `FROZEN` at handoff -- the only two transitions Alpha itself
performs. `UNDER_REVIEW`, `REJECTED`, `SURVIVED_RED_TEAM`, and `SENT_TO_FLOW_C` are set later by
whichever division currently owns the candidate.

**Known correction notes (bookkeeping only, frozen text unmodified in all cases)**: DC-0001 has an
open hash-reproducibility item (investigation closed 2026-07-25, disposition still pending
CEO/Red Team -- see `DC-0001_HASH_REPRODUCIBILITY_INVESTIGATION.md`). DC-0022's family-magnitude-
record claim is factually superseded, currently by DC-0024 Addendum D's 514.165pt (Red Team F2 --
see `DC-0022_.../CORRECTION_NOTE_2026-07-25.md`). DC-0013's "One instance" Confidence line describes
only its 2026-07-23 base freeze and no longer describes its current ~12-instance family scope
(Red Team F4 -- see `DC-0013_.../CORRECTION_NOTE_2026-07-25.md`). None of these change any Title,
Date Frozen, or Lifecycle Status cell below.

| ID | Title | Origin | Date Frozen | Current Version | Lifecycle Status | Folder |
|---|---|---|---|---|---|---|
| DC-0001 | Isolated Single-Bar Velocity Outlier Followed by Gradual Multi-Bar Continuation | discretionary-observation, Discovery Cycle #3 | 2026-07-21 | v1 | FROZEN | `DC-0001_isolated_velocity_outlier_then_gradual_continuation/` |
| DC-0002 | Higher-Timeframe Compression Resolves Into Expansion In The Direction Of The Prevailing H4 Bias | discretionary-observation, Alpha autonomous replay sprint | 2026-07-22 | v1 | FROZEN | `DC-0002_htf_compression_resolves_with_h4_bias/` |
| DC-0003 | Scale Inversion — Micro-Scale Coils And Higher-Timeframe Compressions Resolve In Opposite Ways | discretionary-observation, manual candle-by-candle replay | 2026-07-22 | v1 | FROZEN | `DC-0003_scale_inversion_of_break_behaviour/` |
| DC-0004 | New-York-Session Prior-Day-High Sweep-Reject Is Followed By Reversion | systematic observation + descriptive analysis (OBS-0001→0013) | 2026-07-22 | v1 | FROZEN | `DC-0004_ny_session_conditioned_sweep_reject/` |
| DC-0005 | The Third Test Of A Level Behaves Differently From The First Two | discretionary-observation, replay manual stepping | 2026-07-22 | v1 | FROZEN | `DC-0005_third_test_of_a_level/` |
| DC-0006 | Candles With Extreme Relative Volume Frequently Fail To Extend | discretionary-observation, replay manual stepping | 2026-07-22 | v1 | FROZEN | `DC-0006_extreme_volume_candle_fails_to_extend/` |
| DC-0007 | A Cluster Of Near-Equal Lows Is Taken And Reclaimed Within A Single Candle | discretionary-observation, replay manual stepping | 2026-07-22 | v1 | FROZEN | `DC-0007_equal_lows_swept_and_reclaimed_same_candle/` |
| DC-0008 | A Large M15 Candle Built From Sustained Multi-Minute Volume, Not Single-Minute Concentration | discretionary-observation, Alpha autonomous replay sprint | 2026-07-22 | v1 | FROZEN | `DC-0008_sustained_multiminute_volume_vs_single_minute_concentration/` |
| DC-0009 | A Narrow Resistance Band Survives Seven Touches Across Three Calendar Days, Including A Weekend Gap | discretionary-observation, Alpha autonomous replay sprint | 2026-07-22 | v1 | FROZEN | `DC-0009_multiday_resistance_band_survives_seven_touches/` |
| DC-0010 | A Consistently Quiet Hour Breaks With A Sustained Volume Expansion On One Session | discretionary-observation, Alpha autonomous replay sprint | 2026-07-22 | v1 | FROZEN | `DC-0010_quiet_hour_volume_break_early_asia/` |
| DC-0011 | A Single-Minute Sweep Is Reclaimed And The Move Extends To New Highs, Not Just Back To Pre-Sweep Levels | discretionary-observation, Alpha autonomous replay sprint | 2026-07-22 | v1 | FROZEN | `DC-0011_single_minute_sweep_reclaim_to_new_highs/` |
| DC-0012 | Sustained High Volume With No Net Displacement (Two-Sided Absorption) | discretionary-observation, Alpha autonomous replay sprint | 2026-07-22 | v1 | FROZEN | `DC-0012_absorption_high_volume_no_displacement/` |
| DC-0013 | A Large NY-Session Directional Expansion Built From Sustained Multi-Minute Volume, Extending Across Four Consecutive M15 Candles With No Reversal | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-23 | v1 | FROZEN | `DC-0013_ny_session_large_sustained_expansion_no_reversal/` |
| DC-0014 | A V-Shaped Reversal at the 00:00-01:00 UTC Hour Builds Into a Sustained Four-Candle Rally, Then Reverses | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-23 | v1 | FROZEN | `DC-0014_asia_hour_v_reversal_sustained_multicandle_rally_then_reversal/` |
| DC-0015 | A Sustained NY-Session Directional Expansion Persists Across Eleven Consecutive M15 Candles (~2h45m), the Longest Single-Direction Run Observed in This Replay | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-23 | v1 | FROZEN | `DC-0015_ny_session_prolonged_multicandle_expansion_2h45m/` |
| DC-0016 | A Sustained Early-Asia/Pre-London Directional Expansion Reaches the Largest Point Move of This Family, Then Reverses at a Marginal New High | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-23 | v1 | FROZEN | `DC-0016_early_asia_pre_london_prolonged_expansion_reversal/` |
| DC-0017 | An NFP-Scale 12:30 UTC Impulse, Built From Sustained Multi-Minute Volume, Holds Its Gains Across Four Subsequent High-Volume Candles Without Reversing or Extending Dramatically Further | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-23 | v1 | FROZEN | `DC-0017_1230_utc_nfp_scale_impulse_sustained_multicandle_hold/` |
| DC-0018 | An Extreme-Volume Spike to a Fresh Multi-Session High Fails Completely Within the Same Candle, Then Extends Into a Sustained Multi-Candle Decline | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-23 | v1 | FROZEN | `DC-0018_extreme_volume_fresh_high_failure_then_sustained_decline/` |
| DC-0019 | A Weekend Gap Nearly Double the Prior Record Fails to Retrace, Extending Into a Sustained Sunday-Reopen Decline Before a Partial Recovery | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-24 | v1 | FROZEN | `DC-0019_large_weekend_gap_failed_retrace_sunday_reopen_decline/` |
| DC-0020 | An 18:00 UTC Low Sweep Followed By a Failed Fresh-High Reclaim Sets a New All-Time Volume Record and Extends Into a Multi-Leg, Bidirectional Decline | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-24 | v1 | FROZEN | `DC-0020_1800utc_sweep_failed_high_reclaim_extreme_volume_record_multileg_decline/` |
| DC-0021 | A Sustained NY-Morning Decline Transitions Directly Into a Multi-Candle Absorption Phase at Persistently Elevated Volume, With No Volume Decay Between Phases | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-24 | v1 | FROZEN | `DC-0021_decline_into_sustained_absorption_no_volume_decay/` |
| DC-0022 | An NY-Afternoon Sustained Directional Expansion Sets New Duration and Magnitude Records for the Family, Nearly Doubling the Prior Longest Run Before Reversing | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-24 | v1 | FROZEN | `DC-0022_ny_afternoon_record_duration_magnitude_sustained_expansion/` |
| DC-0023 | An 8-Hour Multi-Leg, Choppy Episode at Persistently Extreme Volume, Containing a Single Candle Among the Largest-Volume Candles in the Replay | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-24 | v1 | FROZEN | `DC-0023_8hour_choppy_extreme_volume_episode_with_embedded_massive_candle/` |
| DC-0024 | A London-Morning Sustained Decline Sets a New All-Time Magnitude Record (125.7 Points), Then Partially Recovers | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-24 | v1 | FROZEN | `DC-0024_london_morning_record_magnitude_decline_partial_recovery/` |
| DC-0025 | A Two-Candle Escalating-Volume Waterfall Decline Sets a New All-Time Volume Record, Then Retraces ~75% Before Consolidating | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-25 | v1 | FROZEN | `DC-0025_two_candle_escalating_volume_waterfall_decline_record_volume/` |
| DC-0026 | A Thin-Liquidity Daily-Rollover Reopen Produces a ~100-Point Parabolic Spike That Fully Reverses Within Minutes | discretionary-observation, Alpha autonomous replay sprint (v2 filter) | 2026-07-25 | v1 | FROZEN | `DC-0026_daily_rollover_thin_liquidity_parabolic_spike_reversal/` |
