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

| ID | Title | Origin | Date Frozen | Current Version | Lifecycle Status | Folder |
|---|---|---|---|---|---|---|
| DC-0001 | Isolated Single-Bar Velocity Outlier Followed by Gradual Multi-Bar Continuation | discretionary-observation, Discovery Cycle #3 | 2026-07-21 | v1 | FROZEN | `DC-0001_isolated_velocity_outlier_then_gradual_continuation/` |
| DC-0002 | Higher-Timeframe Compression Resolves Into Expansion In The Direction Of The Prevailing H4 Bias | discretionary-observation, Alpha autonomous replay sprint | 2026-07-22 | v1 | FROZEN | `DC-0002_htf_compression_resolves_with_h4_bias/` |
| DC-0003 | Scale Inversion — Micro-Scale Coils And Higher-Timeframe Compressions Resolve In Opposite Ways | discretionary-observation, manual candle-by-candle replay | 2026-07-22 | v1 | FROZEN | `DC-0003_scale_inversion_of_break_behaviour/` |
| DC-0004 | New-York-Session Prior-Day-High Sweep-Reject Is Followed By Reversion | systematic observation + descriptive analysis (OBS-0001→0013) | 2026-07-22 | v1 | FROZEN | `DC-0004_ny_session_conditioned_sweep_reject/` |
| DC-0005 | The Third Test Of A Level Behaves Differently From The First Two | discretionary-observation, replay manual stepping | 2026-07-22 | v1 | FROZEN | `DC-0005_third_test_of_a_level/` |
| DC-0006 | Candles With Extreme Relative Volume Frequently Fail To Extend | discretionary-observation, replay manual stepping | 2026-07-22 | v1 | FROZEN | `DC-0006_extreme_volume_candle_fails_to_extend/` |
