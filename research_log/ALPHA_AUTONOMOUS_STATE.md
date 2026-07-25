<!--
ALPHA_AUTONOMOUS_STATE — operational checkpoint contract.

This file is machine-appended-to and human-readable. It is REWRITTEN COMPLETELY by Alpha at the
end of every automation cycle (see prompts/ALPHA_AUTOMATION_CONTINUE.md, section 6). The
orchestrator (scripts/run_alpha_automation.ps1) treats a cycle as "no progress" if this file's
content hash is unchanged after a cycle that reported ALPHA_CONTINUE_REQUIRED or
ALPHA_MISSION_COMPLETE, and will fail closed (stop the loop) rather than assume progress happened.

Do not delete fields. If a field is genuinely not applicable, write "N/A" and say why.
-->

# Alpha Autonomous State

## *** ALPHA 1 OFFICIALLY CLOSED (2026-07-25) — DO NOT AUTO-RESUME ***
Alpha 1 (the manual, `/loop`-driven TradingView replay observation track described below under
"Discovery Candidates") was **officially closed by explicit CEO directive on 2026-07-25**. This is
an administrative closure, not a scientific conclusion: no candidate was validated, invalidated,
or promoted as part of it. If this orchestrator (`scripts/run_alpha_automation.ps1`) or any future
automated cycle reads this file: **do not reopen the TradingView replay window and do not produce
any new Discovery Candidate or addendum** until an explicit new CEO directive authorizes it. This
rewrite (2026-07-25) is an administrative correction pass, not a completed automation cycle — see
`cycle_id` below, which is unchanged from its prior value for that reason.

## Contract
- **schema_version:** 1.0
- **last_updated:** 2026-07-25T00:00:00Z (administrative correction pass — Alpha 1 closure +
  factual-accuracy fixes to this file; not an executed automation cycle)
- **run_id:** N/A (this automation script has still never executed a cycle)
- **cycle_id:** 0 (unchanged — accurate: `scripts/run_alpha_automation.ps1` itself has never run a
  cycle. This is a distinct fact from Alpha 1's manual-track portfolio below; see correction note)

## Correction note (2026-07-25)
This file previously stated, under "Discovery Candidates," **"None frozen by Alpha"** — that line
was misleading to the point of being wrong. It was written to mean "none frozen by *this
orchestrator's own automated cycles*" (true: `run_id` is still N/A), but read as a flat claim about
Alpha's entire body of work, which is false: **Alpha 1's manual replay-observation track has frozen
26 Discovery Candidates (DC-0001 through DC-0026)**, all FROZEN, submitted to Red Team, with 47
addenda and 18 Observation Registry entries, per `research_log/SESSION_STATE.md` and
`discovery_candidates/DISCOVERY_CANDIDATE_INDEX.md`. That track is now officially closed (see
banner above). The distinction that matters going forward: this specific automation script has
never executed a cycle (still true, still N/A) — it has never been the thing that froze anything.

## Instrument / data
- **symbol:** XAUUSD
- **replay_date:** 2024-03-20
- **replay_time:** 02:15–05:45 UTC (last recorded field-journal position, entry #013) — this
  reflects this file's own OBS-0001..0017 research line, not Alpha 1's manual track (which stopped
  its own, separate replay position at 2026-05-15 20:59:59 UTC and has since called `replay_stop`).
- **timezone:** UTC
- **active_timeframe:** M15 (primary observation), H1 used for traversal, H4 for bias
- **historical_start:** dataset begins per `data/market/OANDA_XAUUSD_*.csv` (see
  `alpha_automation/config.example.json` for the live-loader instrument mapping)
- **historical_endpoint (holdout cutoff):** 2025-10-23T09:15:00+00:00
  (`pre_holdout_2025-10-23T09-15-00Z_v1` — do not cross this without explicit CEO authorization)

## Chart state (NOT currently loaded — re-establish before trusting)
- **H4_bias:** UNKNOWN — not currently loaded. Last session was a localized M15 consolidation
  study; no H4 bias was recorded for the surrounding period. Re-anchor top-down before using.
- **H4_regime:** UNKNOWN — same caveat.
- **H1_direction:** UNKNOWN — same caveat.
- **active_range:** last known micro-range: ~2145–2195 (post-expansion consolidation, per
  journal entry #013), not confirmed current.
- **important_levels:** ceiling 2159.7–2159.8 (probed 4x, broke marginally to 2160.295 then
  reversed to 2156.95, entry #013); prior reference: Dec-2023 rejected excursion ~2145 acting as a
  consolidation boundary for ~3 months (entries #008/#008-RESOLUTION, LINE-B).

## Session / sprint
- **current_session:** Asia (per last journal entry; not necessarily the session the next cycle
  will open in — determined by whichever window is selected next).
- **current_research_sprint:** Observation-first batch toward 25 total Observation Records
  (`research_log/RESEARCH_MEMORY.md`). OBS-0001–0017 complete (17/25). OBS-0018 was next before
  Alpha 1's closure; **no further OBS records should be produced until a new CEO directive
  authorizes resuming this sprint** (see closure banner above).

## Coverage
- **completed_coverage:** OBS-0001 through OBS-0017 (see `RESEARCH_MEMORY.md` table for verdicts).
  Field journal entries #001–#013 plus method notes #007/#009.
- **unverified_coverage:** Everything not explicitly listed above. In particular: no H4/D1 bias
  survey has been logged for the 2024-03 period; the "batch 15/25" label in
  `RESEARCH_MEMORY.md`'s header text is stale relative to its own 17-row table — do not trust that
  header number, trust the table + this checkpoint.

## Research lines
- **LINE-A** (structural-break churn vs. isolation): now suspected ≡ lab's K03 (trend-efficiency).
  Needs a decisive test — does structural/churn context add anything beyond a plain trend-
  efficiency number? If not, LINE-A dies into K03. NOT resolved.
- **LINE-B** (failed-excursion defines a consolidation boundary, not a top): candidate, unopened,
  very low confidence, no directional claim.

## Discovery Candidates
- **None frozen by this automation script's own cycles** (`run_id` is still N/A — see Contract
  above). Leading candidate-grade lead from this research line: NY-session prior-day-high
  sweep-reject → ~6h reversion (chain OBS-0001→0003→0008→0012→0013). Full-sample matched-null
  CI<0, uniquely distinguished, sign-stable across both halves — **but fails Bonferroni correction,
  n=42, in-sample only.** CEO decision requested (per RESEARCH_MEMORY.md): authorize a
  reserved-holdout (post-2025-10-23) test as the decisive gate before any freeze. **Do NOT freeze
  on in-sample data.** This is a pending CEO decision, not a blocker for continued observation-first
  work — though see closure banner above: no new work proceeds without a fresh CEO go-ahead either
  way, since Alpha 1 is closed and this line has not been separately authorized to continue.
- **Separately, Alpha 1's manual replay-observation track** (a distinct, `/loop`-driven process —
  see Correction Note above) has frozen **26 Discovery Candidates (DC-0001–DC-0026)**, all
  submitted to Red Team, and is now **officially closed** (2026-07-25).
- Lab-side **DC-0001** (isolated single-bar velocity outlier → gradual continuation, frozen
  2026-07-21, submitted to Red Team) was flagged against OBS-0014 under an independent H1
  operationalization. **Reconciled at the definitional level 2026-07-25** — see
  `research_log/DC0001_OBS0014_RECONCILIATION_NOTE.md`: the two use different timeframes (M15 vs
  H1), different outlier definitions, and different forward horizons, so OBS-0014 is not a direct
  test of DC-0001 as specified. The underlying scientific question remains open, owned by Red Team
  / the Statistician, not resolved here.

## Falsifications (do not re-run as specified — extend only with a new control/condition/OOS)
OBS-0001 (prior-day sweep-reject vs break-hold, SMC), OBS-0002 (level vs trend), OBS-0004 (sweep
depth), OBS-0005 (prior-day-close magnet — opposite/confound), OBS-0009 (day-of-week returns —
negative; weak vol gradient survives), OBS-0010 (round-number clustering), OBS-0012 (all-cells
selection test, fails Bonferroni), OBS-0013 (spec as-is), OBS-0015 (weekend gap fill — true but
trivial), OBS-0017 (H4 swing-high marginal overshoot as reversal tell — uninformative).

## Unresolved questions
- K05 (lab): long-gold-beta vs. timing-alpha confound on ~11/13 OOS-positive candidates —
  unresolved, corroborated from three independent angles by Alpha's own observations
  (OBS-0001, OBS-0005, OBS-0017).
- DC-0001 vs OBS-0014 contradiction — **definitional reconciliation CLOSED 2026-07-25** (see
  `research_log/DC0001_OBS0014_RECONCILIATION_NOTE.md`); the decisive matched-definition test
  itself remains open and unowned by Alpha.
- Does LINE-A (churn/structural context) add anything beyond plain trend-efficiency (K03)? No
  decisive test designed yet.
- NY-lead: sign-stable across both halves but fails Bonferroni at n=42 — is this a power problem
  or a real absence of effect? Reserved-holdout test is the proposed resolution, pending CEO
  authorization.

## Exact next action
**Alpha 1 is closed and its replay window must not be reopened (see banner above).** This research
line's own next action (entering TradingView replay for OBS-0018) is **suspended, not cancelled**
pending an explicit new CEO directive that either (a) reauthorizes this observation-first sprint
specifically, or (b) reopens Alpha 1 more broadly. Until such a directive arrives, no automated or
manual cycle should act on the "Enter TradingView replay" instruction this section previously
carried. When work does resume, the original procedure remains valid: select the next unexamined
window per the lab's non-overlapping seeded-window policy, watch the M15 tape first
(observation-first methodology), consult `KNOWLEDGE_LIBRARY.md` only after an organic observation,
validate against the sanctioned pre-holdout Python loader, write the result as `OBS-0018` regardless
of verdict, and update `RESEARCH_MEMORY.md` / `KNOWLEDGE_LIBRARY.md` accordingly.

## Automation status (owned by the orchestrator, not by Alpha)
- **last_successful_cycle:** N/A — automation has not been run yet. This checkpoint was authored
  during infrastructure build-out (`scripts/run_alpha_automation.ps1` etc.), and this 2026-07-25
  revision is an administrative correction pass, not an automated Alpha cycle.
- **last_output_marker:** N/A
- **blocker_status:** ALPHA 1 CLOSED (2026-07-25) — the TradingView replay window must not be
  reopened and no new Discovery Candidate or addendum should be produced until an explicit new CEO
  directive authorizes it. Separately, the CEO holdout-gate decision on the NY-lead candidate
  remains a pending research-track decision, unaffected by the closure above.
