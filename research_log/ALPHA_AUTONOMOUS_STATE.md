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

## Contract
- **schema_version:** 1.0
- **last_updated:** 2026-07-22T12:00:00Z (infrastructure setup — not an Alpha research cycle)
- **run_id:** N/A (automation has not executed a cycle yet)
- **cycle_id:** 0

## Instrument / data
- **symbol:** XAUUSD
- **replay_date:** 2024-03-20
- **replay_time:** 02:15–05:45 UTC (last recorded field-journal position, entry #013)
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
  (`research_log/RESEARCH_MEMORY.md`). OBS-0001–0017 complete (17/25). OBS-0018 is next.

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
- **None frozen by Alpha.** Leading candidate-grade lead: NY-session prior-day-high sweep-reject →
  ~6h reversion (chain OBS-0001→0003→0008→0012→0013). Full-sample matched-null CI<0, uniquely
  distinguished, sign-stable across both halves — **but fails Bonferroni correction, n=42,
  in-sample only.** CEO decision requested (per RESEARCH_MEMORY.md): authorize a reserved-holdout
  (post-2025-10-23) test as the decisive gate before any freeze. **Do NOT freeze on in-sample
  data.** This is a pending CEO decision, not a blocker for continued observation-first work.
- Lab-side **DC-0001** (isolated single-bar velocity outlier → gradual continuation, frozen
  2026-07-21, awaiting Red Team) is **contradicted** by OBS-0014 under an independent H1
  operationalization. Reconciliation against DC-0001's exact spec is an open item, not yet done.

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
- DC-0001 vs OBS-0014 contradiction — needs reconciliation against DC-0001's exact
  `candidate_v1.md` definition before concluding either way.
- Does LINE-A (churn/structural context) add anything beyond plain trend-efficiency (K03)? No
  decisive test designed yet.
- NY-lead: sign-stable across both halves but fails Bonferroni at n=42 — is this a power problem
  or a real absence of effect? Reserved-holdout test is the proposed resolution, pending CEO
  authorization.

## Exact next action
Enter TradingView replay (via the TVRE tooling). Select the next unexamined window per the lab's
non-overlapping seeded-window policy (do not reuse OBS-0001–0017's windows as-is). Before forming
any question: watch the M15 tape first (observation-first methodology, CEO 2026-07-22 — see
`RESEARCH_MEMORY.md` header). Only after an organic observation, consult
`research_log/KNOWLEDGE_LIBRARY.md` to check for prior art. If a question survives that check,
validate it against the sanctioned pre-holdout Python loader
(`edge_research/_common.load(tf, *, data_split_id, cutoff)`). Write the result as `OBS-0018`
regardless of verdict (including a clean null). Update `RESEARCH_MEMORY.md`'s coverage table and
`KNOWLEDGE_LIBRARY.md` if anything changes. Then rewrite this checkpoint per
`prompts/ALPHA_AUTOMATION_CONTINUE.md` section 6.

## Automation status (owned by the orchestrator, not by Alpha)
- **last_successful_cycle:** N/A — automation has not been run yet. This checkpoint was authored
  during infrastructure build-out (`scripts/run_alpha_automation.ps1` etc.), not by an automated
  Alpha cycle.
- **last_output_marker:** N/A
- **blocker_status:** NONE. The CEO holdout-gate decision on the NY-lead candidate is a pending
  research-track decision, not an execution blocker — Alpha can continue observation-first work
  (OBS-0018+) regardless of when/whether that decision is made.
