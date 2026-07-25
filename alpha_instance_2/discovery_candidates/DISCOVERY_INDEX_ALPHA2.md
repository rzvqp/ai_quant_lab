# Discovery Candidate Index — Alpha Parallel Instance #2

Master, authoritative registry of every Discovery Candidate ID ever assigned by this instance. An
ID is reserved the moment its folder is created and is never reused, even if the candidate is
later withdrawn or rejected -- its row stays, marked with its final status, rather than being
deleted. Uses the `AP2-DC-XXXX` local namespace -- these are NOT official lab IDs. Official
`DC-XXXX` IDs are assigned later during the reconciliation stage.

This is the **only** place where a candidate's *current* lifecycle status is recorded. Frozen
candidate documents never contain a live status field themselves -- see
`DISCOVERY_CANDIDATE_TEMPLATE_ALPHA2.md`'s Metadata section.

**Lifecycle status values** (fixed set):
`OBSERVED` -> `FROZEN` -> `UNDER_REVIEW` -> `REJECTED` | `SURVIVED_RED_TEAM` -> `SENT_TO_FLOW_C`

This instance sets `OBSERVED` at creation and `FROZEN` at handoff -- the only two transitions it
performs itself. `UNDER_REVIEW`, `REJECTED`, `SURVIVED_RED_TEAM`, and `SENT_TO_FLOW_C` are set
later by whichever division currently owns the candidate.

| ID | Title | Origin | Date Frozen | Current Version | Lifecycle Status | Folder |
|---|---|---|---|---|---|---|
| AP2-DC-0001 | A Sharp Breakout On A First-Friday-Of-Month Session Fully Reverses Into A Larger, Extended Decline That Overshoots The Pre-Breakout Level | discretionary-observation, Alpha Parallel Instance #2 manual replay_step walkthrough | 2026-07-24 | v1 | FROZEN | `AP2-DC-0001_nfp_breakout_fails_into_extended_decline/` |
| AP2-DC-0002 | A Major Scheduled Political Catalyst Produces a Multi-Hour, Near-Record-Volume, Complex Two-Way Volatility Episode Far Exceeding Any Routine Data-Release Reaction | discretionary-observation, Alpha Parallel Instance #2 manual replay_step walkthrough | 2026-07-25 | v1 | FROZEN | `AP2-DC-0002_election_night_extended_high_volatility_episode/` |
