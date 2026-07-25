# Correction Note to DC-0013 (dated 2026-07-25)

**Type**: Administrative bookkeeping correction -- NOT a scientific addendum, NOT new market
evidence, NOT a new observation. Filed per Red Team finding **F4** (`red_team/RED_TEAM_STATE.md`
§5: "DC-0013 = family container") and explicit CEO directive at Alpha 1's official closure
(2026-07-25). `candidate_v1.md` is frozen and is **not edited** by this note, per its own Handoff
Statement -- this correction is filed as a separate, dated file in this candidate's folder instead.

## The Error

`candidate_v1.md` §5 (Confidence) reads: **"Low. One instance, one instrument, one session
type."** This was accurate at freeze time (2026-07-23, base candidate only). It is no longer an
accurate description of what this candidate's folder now contains: 13 addenda (`addendum_2026-07-
23_a.md` through `addendum_2026-07-25_m.md`) have since been filed against it, each documenting a
further instance of the same sustained-multi-minute-volume-expansion construction. Red Team's
finding F4 (echoed in `RED_TEAM_FINAL_EVALUATION.md` and `_v2.md`) identifies that DC-0013 has, in
practice, become the **root of a family of roughly a dozen instances** (the base candidate plus
its 13 addenda, plus related sibling candidates DC-0014 through DC-0024 that Red Team treats as
the same underlying construction) -- while its own frozen text still reads as if it describes a
single, one-off occurrence.

## Correction

DC-0013's `candidate_v1.md` §5 Confidence statement ("One instance, one instrument, one session
type") describes only the **base candidate as originally frozen** and must not be read as
describing the candidate's current evidentiary scope. As of Alpha 1's closure (2026-07-25),
DC-0013 is the root document of a **family of approximately twelve documented instances** (the
base observation plus Addenda A-M), and Red Team's characterization of it as "a family container
... not a single falsifiable claim" (`RED_TEAM_FINAL_EVALUATION.md`) should be read as the current,
correct description of its evidentiary status, superseding the base document's original "one
instance" framing for that purpose.

## Why This Happened (context, not excuse)

The addendum mechanism (append dated new evidence, never edit the frozen base) is working exactly
as designed -- each addendum was correctly filed as new evidence rather than as a silent edit. The
gap Red Team identifies is structural, not a filing error: nothing in this candidate's own text
signals, to a reader of `candidate_v1.md` alone, that thirteen addenda now exist and have shifted
its status from "single observation" to "family container." This correction note exists to close
that gap for future readers without touching the immutable base text.

## Disposition

- `candidate_v1.md` is unmodified (frozen, per its Handoff Statement); its §5 Confidence line
  remains historically accurate for what it originally described (n=1, at 2026-07-23).
- This correction note is the authoritative pointer that the candidate's *current* status, given
  its 13 addenda, is "family container, ~12 instances" rather than "one instance" -- consistent
  with Red Team's F4.
- Alpha does not restate a confidence rating, define a falsifiable sub-claim for the family, or
  otherwise evaluate the candidate -- that remains Red Team's / the Statistician's role (per
  `RED_TEAM_PHASE1_REPORT.md`'s recommendation that the DC-0008 concentration-ratio measurement is
  the gating test for this whole family).

## Cross-References

- `red_team/RED_TEAM_STATE.md` §5 (F4), `red_team/RED_TEAM_FINAL_EVALUATION.md` (DC-0013 row),
  `red_team/RED_TEAM_FINAL_EVALUATION_v2.md` (DC-0013 note).
- `discovery_candidates/DC-0013_ny_session_large_sustained_expansion_no_reversal/addendum_2026-07-23_a.md`
  through `addendum_2026-07-25_m.md` (13 addenda).
- `discovery_candidates/HANDOFF_LOG.md`
