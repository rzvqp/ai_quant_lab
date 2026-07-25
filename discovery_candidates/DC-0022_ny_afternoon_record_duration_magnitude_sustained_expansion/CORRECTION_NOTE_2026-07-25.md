# Correction Note to DC-0022 (dated 2026-07-25)

**Type**: Administrative bookkeeping correction -- NOT a scientific addendum, NOT new market
evidence, NOT a new observation. Filed per Red Team finding **F2** (`red_team/RED_TEAM_STATE.md`
§5: "Record bookkeeping contradiction") and explicit CEO directive at Alpha 1's official closure
(2026-07-25). `candidate_v1.md` is frozen and is **not edited** by this note, per its own Handoff
Statement -- this correction is filed as a separate, dated file in this candidate's folder instead.

## The Error

`candidate_v1.md`'s title and body (§1, §2, §3, §5) claim that this instance's **86.75-point**
move is a new **magnitude record for the family** ("Sets New Duration and Magnitude Records for
the Family", "substantially exceeds prior family records"). This claim is **factually incorrect**
at the time it was written and remains incorrect now, by a much wider margin than first recorded
here. `DC-0013`'s own addenda already exceeded it before/around DC-0022's freeze --

- Addendum D: 89.4pt
- Addendum F: 100.97pt
- Addendum H: 180.53pt

-- but the true current family-wide record, per Red Team's own broader grouping of this family
(`RED_TEAM_FINAL_EVALUATION.md`: "one construction, twelve objects: DC-0008 (root) -> DC-0013,
0014, ..., 0022, 0023, 0024"), is **DC-0024 Addendum D's 514.165-point move** (2026-03-18 06:30 UTC
-> 2026-03-19 13:00 UTC), explicitly logged there as "this replay's largest single directional move
recorded to date" / "a new all-time magnitude record, either direction" -- nearly **6x** DC-0022's
claimed 86.75pt, and independently corroborated by `OBSERVATION_REGISTRY.md` entry 18
(2026-04-23), which cites the same 514.165pt figure as the standing record when comparing a later,
smaller event against it. An earlier version of this note cited only DC-0013 Addendum H (180.53pt)
as the correction value -- that was itself stale, having missed DC-0024's addenda; this revision
(2026-07-25) corrects that omission.

DC-0022's **duration** claim (16 candles / 4 hours, exceeding DC-0015's 11-candle run) is not
disputed by this correction and is not addressed by Red Team finding F2 -- only the magnitude
claim is wrong.

## Correction

DC-0022's 86.75-point move is **not** a family magnitude record, at freeze time or since. The
family's magnitude record, as of Alpha 1's closure (2026-07-25), is **DC-0024 Addendum D's
514.165-point move** (DC-0013 Addendum H's 180.53pt was itself only an intermediate record,
already superseded by the time DC-0022 was even a candidate for correction). DC-0022's own
observed value (86.75pt) is unchanged and stands as one instance within the DC-0008/DC-0013/
DC-0024 sustained-expansion family, without the "record" distinction its original text claims.

## Why This Happened (context, not excuse)

DC-0022 and the DC-0013 addenda were both being filed concurrently across 2026-07-24/25 by the
same observation process, each tracking "largest so far" independently within its own document
rather than against a single shared running-max register. Red Team's finding F2 (and the related
W3 in `RED_TEAM_FINAL_EVALUATION_v2.md`) identifies this as a structural bookkeeping gap: multiple
candidates in this family each declared their own "record" without cross-checking the others. This
correction addresses DC-0022's specific instance of that gap; it does not itself establish a
running-max register (that is a structural fix belonging to whoever owns the family's bookkeeping
going forward, not a task Alpha performs unilaterally at closure).

## Disposition

- `candidate_v1.md` is unmodified (frozen, per its Handoff Statement).
- This correction note is the authoritative record that the magnitude-record claim is superseded /
  incorrect, cross-referenced from `HANDOFF_LOG.md`.
- Alpha does not restate a confidence rating or otherwise evaluate the candidate -- that remains
  Red Team's / the Statistician's role.

## Cross-References

- `red_team/RED_TEAM_STATE.md` §5 (F2), `red_team/RED_TEAM_FINAL_EVALUATION_v2.md` (DC-0022 row,
  W3), `red_team/RED_TEAM_FINAL_EVALUATION.md` (family grouping, DC-0008 root).
- `discovery_candidates/DC-0013_ny_session_large_sustained_expansion_no_reversal/addendum_2026-07-24_h.md`
  (180.53pt, intermediate record).
- `discovery_candidates/DC-0024_london_morning_record_magnitude_decline_partial_recovery/addendum_2026-07-25_d.md`
  (514.165pt, current record).
- `research_log/OBSERVATION_REGISTRY.md` entry 18 (2026-04-23, independently cites 514.165pt).
- `discovery_candidates/HANDOFF_LOG.md`
