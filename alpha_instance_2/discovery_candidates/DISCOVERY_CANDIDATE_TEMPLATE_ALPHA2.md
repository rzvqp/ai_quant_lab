<!-- ============================================================
     OFFICIAL DISCOVERY CANDIDATE TEMPLATE (CEO-approved 2026-07-21, primary Alpha instance)
     Reused verbatim for Parallel Instance #2, with candidate_id namespace AP2-DC-XXXX instead of
     DC-XXXX (local instance ID, NOT an official lab ID -- official DC-XXXX assigned later at
     reconciliation). Alpha -> Red Team handoff interface.

     AMENDMENT (CEO ruling, 2026-07-25): Section 5 ("Testability & Falsifiability") below is
     mandatory as of this date, adopted from Statistician Phase 1 Summary §5-§6
     (`statistician/STATISTICIAN_PHASE1_SUMMARY.md`) after review of Red Team's finding that
     "largest so far" / record-type framings are unfalsifiable by construction and generate
     unbounded candidates without new information (Red Team finding F1, `red_team/RED_TEAM_STATE.md`
     -- documented against Alpha #1's portfolio, adopted here pre-emptively). This is the one
     exception to "do not add sections beyond what is defined here": Section 5 is now part of the
     defined structure, not an addition to it. No candidate may be frozen without it starting
     AP2-DC-0003.

     Do not add sections beyond what is defined here (Section 5 is part of "here" as of the
     amendment above).
     Do not include Competing Hypotheses, Internal Red-Team Findings,
     Information Gap Analysis, or Required Observables as structured
     sections -- Alpha is a pure Discovery division; those
     responsibilities belong to later, independent divisions. Informal
     notes of that kind may appear under "Additional Notes" only if they
     arose naturally, never as a required checklist.

     Do not include entries, stops, targets, position sizing, RR framing,
     tuned parameters, backtest results, or expectancy claims.
     Do not reference or include content from Flow B (ai_trader/).

     NOTE on Section 5's "numeric threshold": this is a DEFINITIONAL threshold -- the number that
     lets a second researcher decide, without asking Alpha, whether a new instance counts as an
     example of this candidate (e.g. "breakout counts as 'sharp' if range >= Npt and volume >=
     Mx the preceding 2hr average"). It is not a trading threshold, stop, target, or tuned
     parameter, and the prohibition on those is unchanged.

     PROHIBITED: record-type framing as attention-justification or supporting evidence.
     "Largest/longest/most [X] observed so far", "new record", "near-record", "among the highest
     ever seen this replay" -- these claims are true by construction (nothing has yet exceeded
     them) and therefore cannot fail. A candidate justified this way is unfalsifiable at the
     moment of freezing and will keep re-justifying itself as "even bigger" indefinitely, never
     producing new information about the mechanism. Magnitude/duration/volume MAY be reported as
     plain descriptive facts (e.g. "31.5pt single-candle range, volume 12627"), but may not be the
     stated reason a candidate deserves promotion or further investigation. If magnitude is the
     only thing distinguishing this candidate from an already-logged Observation Registry family,
     that is a signal to keep it in the registry, not to freeze it as a new candidate.
     ============================================================ -->

# Discovery Candidate <AP2-DC-XXXX>: <Title>

## Metadata

- **candidate_id**: AP2-DC-XXXX (local instance ID, not an official lab ID)
- **title**:
- **origin_mode**: (e.g. "discretionary-observation, Parallel Instance #2 replay sprint")
- **date_first_observed**:
- **date_frozen**:
- **version**: v1
- **instrument**:
- **timeframes_examined**:
- **data_split_id**:
- **holdout_cutoff**:
- **source_artifacts**: (chart windows / date ranges reviewed, within 2024-08-01 -> 2025-08-01)
- **related_ids**: (other Candidate IDs or Edge Discovery Registry entries this may relate to --
  disclosure only, never a merge or promotion)
- **content_hash**: (hash of this file's body, computed at freeze time)

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_INDEX_ALPHA2.md`.

## 1. Observation

What was directly observed.

## 2. Why It Attracted Attention

Why it appears unusual or noteworthy.

## 3. Why It May Repeat

Basis for believing this is not a one-off.

## 4. Why It Deserves Further Investigation

Why the observed behaviour appears important enough to justify additional research. Do not
describe exploitability, entries, stops, targets, or edge potential -- whether it is exploitable
is a later decision made by other divisions.

## 5. Testability & Falsifiability (mandatory as of 2026-07-25 — Statistician Phase 1 §5-§6)

All five items below must be filled in. "None" / "not applicable" / "not counted" are acceptable
answers where genuinely true — an explicit absence is the requirement, not a number.

- **Proposed numeric threshold(s)**: for every categorical or binary distinction this candidate's
  observation depends on (e.g. "sharp" breakout, "sustained" decline, "elevated" volume), state a
  candidate numeric value or range, even approximate and untested. Someone else must be able to
  apply the same rule to a new instance without asking Alpha what "sharp" means.
- **Outcome horizon**: the fixed number of bars (or fixed time window) after the defining event
  over which the outcome is measured, stated as a number at formulation time -- not a narrative
  description of "what happened afterward." (e.g. "outcome measured over the next 12 M15 bars
  from the origin candle's close.")
- **Denominator**: either the count of comparable non-events reviewed and passed over during this
  observation, or an explicit one-sentence statement that this was not counted (e.g. "denominator
  not tracked -- this instance did not count how many large-volume candles of comparable scale
  were seen and did not lead to this pattern").
- **Known confounds**: name the specific already-established or plausible alternative explanations
  that could produce the same observation without the mechanism this candidate proposes (e.g. the
  lab's ratified Volatility primitive, session/liquidity regime, day-of-week, a scheduled-release
  calendar slot already documented elsewhere). Do not leave this section empty because none come
  to mind -- if genuinely none are known, say so explicitly rather than omitting the field.
- **Reducible to**: `[primitive name]` if this candidate might just be a restatement of an
  already-ratified lab primitive (e.g. Volatility clustering) or an already-documented Observation
  Registry family, or `None identified` if a deliberate check found none. This is a disclosure, not
  a self-assessment of validity -- Statistician/Red Team make the actual determination.

## 6. Confidence

Low / Medium / High

## Additional Notes (optional)

Freeform. Comparative observations, tentative ideas, open questions, or cross-candidate
references may appear here if they arose naturally during observation. Not a required structure,
not a checklist -- omit entirely if there is nothing to add.

## Handoff Statement

Frozen as of version **v1**, dated **<date_frozen>**. Content hash: **<content_hash>**. This
document is immutable from this point forward. Any correction or new evidence must be filed as a
separate, dated addendum in this candidate's folder, or as a new version file -- never as an edit
to this file.
