# Inventory: Non-Promoted Observations, 2026-01-29 -> 2026-05-15

**Type**: Administrative inventory -- compiles existing `OBSERVATION_REGISTRY.md` entries already
on record; introduces no new observation, analysis, candidate, or addendum. Filed 2026-07-25 per
explicit CEO request, alongside Alpha 1's closure follow-up work.

**Scope**: every Observation Registry entry (phenomenon noted, deliberately not promoted to a
Discovery Candidate or addendum) whose market date falls within 2026-01-29 through 2026-05-15
inclusive -- the tail end of Alpha 1's replay coverage before its 2026-05-15 20:59:59 UTC stop
position. Two entries fall in this window; there is no Registry entry between 2026-04-23 and the
2026-05-15 stop, and none between the window's start and 2026-01-29 other than the 2026-01-19 entry
(out of range, not included).

## Entry 17 -- 2026-01-29 14:15-15:35 UTC (XAUUSD, M15/M5/M1)

**Headline**: a large, genuinely heavy-volume decline whose exact extreme low is compromised by a
likely data artifact at the tick level.

- Sustained decline from a local high of 5549.565, building through several M15 candles with
  escalating volume (up to 53,832 on one M15 candle -- would be an all-time volume record if taken
  at face value, exceeding the then-standing record of 42,808 by 25.8%).
- Dropping to M1 isolated the issue: two consecutive one-minute candles (15:27:00, 15:28:00 UTC)
  carrying a 120-136pt range on only 748-3,980 volume (as low as ~6.2 vol/pt against this window's
  ~90-110 baseline) -- the same "large range, unexpectedly thin volume" artifact signature as the
  Black Friday case (Registry entry 11), though structurally distinct (continuous timestamps here,
  vs. sparse/gapped timestamps there).
- The broader decline (14:15 UTC through ~15:26 UTC) is judged genuine and well-supported by
  volume, matching the DC-0013/DC-0024-family shape of a real heavy-volume sell-off. A conservative,
  credible floor (~5242-5258) puts the genuine decline at **~291-307 points** from the 5549.565
  high -- itself large, but well short of the ~452-point figure the uncorroborated 5097.215 tick
  print would otherwise imply, and well short of any record claim.
- **Disposition**: per the CEO's v2 pre-investigation-filter instruction, no DC/addendum filed when
  a range/volume combination matches the thin-volume artifact signature. Logged as Registry entry
  only. No record claim (volume or magnitude) was made on the basis of the uncorroborated figures.

## Entry 18 -- 2026-04-23 ~17:40-18:05 UTC (XAUUSD, M15/M5)

**Headline**: a fast, organic-volume sweep down followed by an over-recovery to a net new local
high, at the second-highest single-candle volume in this replay.

- Sharp break down from ~4698.91-4711.99 to an intrabar low of 4664.38 (~34.53pt), then an
  immediate, sharp reversal recovering ~57.86pt to a new intrabar high of 4722.24 -- a net **+23.33pt
  above** the pre-decline level (a full round-trip plus continuation, not a partial retrace).
- The low-print M15 candle carries the **second-highest single-M15-candle volume observed in this
  replay to date** (40,069, exceeded only by the 53,154 all-time record, DC-0023 Addendum C).
  Verified organic on M5 (largest sub-candle share 34.4%, below the 42.7% organic reference).
- Neither axis is a new all-time record: volume 40,069 < 53,154; magnitude 57.86pt << 514.165pt
  (the family's current all-time magnitude record, DC-0024 Addendum D -- already on record at the
  time this entry was filed).
- Does not cleanly match DC-0026 (thin-liquidity daily-rollover spike -- wrong time-of-day and
  duration profile) or DC-0025 (escalating-volume waterfall -- this event's volume is roughly flat
  across the four candles, and the outcome is a full round-trip to a new high, not a partial
  retrace).
- **Disposition**: given the CEO's high bar for new DCs and the strong bias toward
  Addendum-or-nothing, and given no single existing DC's mechanism is decisively matched, logged as
  a Registry entry rather than promoted -- filed for completeness (two-outcome rule) and as a
  comparison point for any future "organic sweep-then-over-recovery" recurrence.

## Summary

| Entry | Market date/time | Why not promoted |
|---|---|---|
| 17 | 2026-01-29 14:15-15:35 UTC | Genuine decline confirmed, but the extreme-low print and any record claim are compromised by a tick-level thin-volume data artifact; filed per the v2 artifact-handling protocol, not a DC/addendum |
| 18 | 2026-04-23 ~17:40-18:05 UTC | Genuine, organic, second-highest-volume event, but matches no existing DC's mechanism decisively and sets no all-time record on either axis; filed under the high-bar-for-new-DCs / Addendum-or-nothing standard |

Both entries reflect Alpha's two-outcome rule (DC/Addendum or Registry entry, never silent
discard) operating as designed -- neither is an omission, and neither is revisited or promoted by
this inventory.

## Cross-References

- `research_log/OBSERVATION_REGISTRY.md` (entries 17 and 18, full text)
- `discovery_candidates/DC-0022_ny_afternoon_record_duration_magnitude_sustained_expansion/CORRECTION_NOTE_2026-07-25.md`
  (514.165pt current record, cited above for entry 18's context)
- `research_log/SESSION_STATE.md` (top banner, Alpha 1 closure)
