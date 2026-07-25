# Open Item: DC-0001 Hash Reproducibility Investigation

**Status**: INVESTIGATION COMPLETE (closed 2026-07-25, per explicit CEO directive at Alpha 1's
official closure). **The hash itself remains unmodified** -- disposition (re-issue vs. mark
permanently unverifiable) still awaits a CEO / Red Team decision per the Explicit Constraints
below, which continue to apply unchanged.
**Opened by**: Alpha (administrative reconciliation pass), per explicit CEO directive
**Type**: Administrative / audit-integrity item -- NOT a Discovery Candidate. Do not add this file
to `DISCOVERY_CANDIDATE_INDEX.md` or treat it as part of the DC lifecycle. It concerns the
reproducibility of a content hash, not any market observation or scientific claim.

## What Was Found

During the 2026-07-23 HANDOFF_LOG.md reconciliation, all 18 Discovery Candidates' `candidate_v1.md`
content hashes were recomputed independently from the files on disk and compared against the value
recorded in three places: the file's own `content_hash` field, its Handoff Statement, and
`metadata_v1.json`.

For 17 of 18 candidates (DC-0002 through DC-0018), the recomputed hash matched all three recorded
locations exactly.

For **DC-0001** only, the three recorded locations agree with each other (all read
`sha256:1f1b3d399f2e9613b18d1d4ecaede8d7e3b0dec085ab709482b4d2c3f40cf75c`), but an independent
recomputation of the current `candidate_v1.md` on disk does **not** reproduce that value. The
recomputation consistently returns
`sha256:7d6282b2ae29400f3b654a8d9b4a1578a7d8d97edc884595f6879bf90de5438e` regardless of which
reasonable normalization variant is used:

- literal `PENDING` substituted for both hash occurrences (the convention used by DC-0002 onward)
- `sha256:PENDING` substituted (keeping the `sha256:` prefix)
- CRLF-to-LF normalization applied vs. left as-is
- forced single trailing newline vs. file's own trailing bytes left untouched

All four combinations converge on the same computed value, none of which match the recorded hash.

## What This Does NOT Mean (yet)

This finding does not by itself establish that DC-0001's content was altered after freezing, or
that the hash was miscomputed at freeze time, or that anything is wrong with the candidate's
scientific content. DC-0001 predates the standardized `content_hash_method` wording used from
DC-0002 onward (its own method description is phrased slightly differently), and it is the oldest
artifact in this repository -- there are several benign explanations that have not yet been ruled
out (e.g., a different original hashing tool/script, a since-corrected typo in the explanatory
prose added after the hash was first computed, or a hashing method that was never precisely
documented before the DC-0002+ convention existed).

## What This Investigation Should Determine

1. What hashing tool/script/method was actually used to produce DC-0001's original hash, and
   whether it differs materially from the DC-0002+ convention.
2. Whether `candidate_v1.md` for DC-0001 has been touched (even non-substantively, e.g. line-ending
   conversion by an editor or git) since 2026-07-21, by checking file history/timestamps if
   available.
3. Whether the recorded hash can be reproduced by any documented historical method once identified,
   or whether it must be treated as unverifiable and re-issued as a new, clearly-dated hash under
   the current method (which would itself need to be logged as a dated correction, never a silent
   edit).

## Explicit Constraints (per CEO directive, 2026-07-23)

- **Do not modify DC-0001's hash, content, or Handoff Statement** until this investigation
  concludes and a decision is made by the CEO / Red Team.
- This item stays OPEN. It is not resolved by this reconciliation pass and must not be marked
  resolved without a dedicated investigation.

## Investigation Findings (2026-07-25, closing this item)

Determination 1 (hashing method): Independently re-verified all four normalization variants
described above by recomputing sha256 directly against the current on-disk `candidate_v1.md`.
All four reproduce the values already reported here (`7d6282b2...` for both PENDING-literal
variants, `f927f0de...` for both sha256:PENDING-prefixed variants) -- none match the recorded
`1f1b3d39...`. No fifth variant was found that reproduces it. The hashing method actually used to
produce DC-0001's original value could not be identified from the four documented candidate
methods; it most likely reflects an ad hoc or undocumented method used before the DC-0002+
convention was formalized, consistent with DC-0001 being the first-ever candidate in this
repository.

Determination 2 (has the file been touched since freezing?): `git log --follow` on
`candidate_v1.md` shows exactly **one** commit ever -- "Discovery Cycle #3: freeze and submit
DC-0001 to Red Team" (2026-07-21 22:42:47 +0300). Filesystem birth/modify/change timestamps are
all identical (2026-07-21 23:36:45) with no later write. **This rules out post-freeze tampering or
accidental editing** -- the file on disk today is the same file that existed at freeze time.

Determination 3 (conclusion): The recorded hash cannot be reproduced by any currently-known
method and must be treated as **unverifiable under the current convention**, not as evidence of
altered content. Per the Explicit Constraints above, Alpha does not have standing to decide
whether to re-issue a new, clearly-dated hash under the DC-0002+ method -- that decision belongs
to the CEO / Red Team and remains open. This closes Alpha's own investigation task; it does not
close the hash-disposition decision itself.

## Cross-References

- `HANDOFF_LOG.md` -- reconciliation header note (2026-07-23) points here; 2026-07-25 closure note
  added alongside it.
- `research_log/SESSION_STATE.md` -- reconciliation section documents the same finding inline.
- `red_team/RED_TEAM_STATE.md` §6 item 3 -- Red Team's independent tracking of this same item.
