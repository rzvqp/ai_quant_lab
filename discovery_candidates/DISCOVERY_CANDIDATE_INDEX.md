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
