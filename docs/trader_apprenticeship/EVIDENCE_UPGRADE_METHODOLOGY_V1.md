# CEO APPRENTICESHIP EVIDENCE UPGRADE V1 — Frozen Methodology

STATUS: INSTALLED 2020-05-27 (replay clock), during Q2 Lane A.
NATURE: Measurement and learning instrumentation ONLY. Does not alter entry logic,
confirmation rules, the close-based stop-trigger/fill convention, trade-management
rules, regime definitions, or existing Q2 methodology. Any new behavioral rule this
instrumentation surfaces must be explicitly frozen (see [[AI_TRADER_REGIME_STRATEGY_MATRIX]])
before it may affect a future decision — findings here are evidence, not standing orders,
until promoted.

Companion files:
- `TRADE_EVIDENCE_LOG.md` — per-trade tags, R-metrics, static-baseline tracking.
- `STRATEGY_EVIDENCE_DENOMINATOR.md` — qualifying-occurrence counts per developing playbook.
- `REGIME_TRANSITION_WATCH.md` — observation-only log of possible H4 regime weakening.

---

## 1. Actual Management vs Static Baseline

Every trade carries two result paths:

- **ACTUAL_MANAGEMENT** — the real forward decisions made (as already logged in
  `2020_Q2_H4_LOG.md` / `AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md`). Unchanged.
- **STATIC_BASELINE** — a shadow, observation-only result using ONLY the contract frozen
  at entry (ENTRY, INITIAL_STOP, PRIMARY_TARGET/horizon if any). Never influences the
  live trade.

**Definitional gap found on installation, resolved here:** every trade in this
apprenticeship to date has used `TARGET_OBJECTIVE: none fixed -- trailing management`.
With no frozen target, a pure "hold with original stop only" shadow has no natural
terminal condition when price never returns to the original stop — it would stay open
indefinitely. To make STATIC_BASELINE well-defined without inventing a new *trading*
rule, the following MEASUREMENT-ONLY convention is adopted:

> STATIC_BASELINE resolves at the EARLIER of: (a) a bar's CLOSE crossing the trade's
> ORIGINAL (never-trailed) initial stop [same close-based trigger convention as live
> trading], or (b) 192 M15 bars (~48 hours) after entry, marked-to-market at that
> horizon bar's close. If (b) fires, STATUS = HORIZON_MARK, not a true terminal close.

This horizon (48h / 192 bars) is my own mechanical choice within the mandate's
discretion — long enough to let genuine continuation show, short enough to keep
bookkeeping bounded. It is a measurement convention only and carries no trading
authority.

Tracking a still-open STATIC_BASELINE costs nothing extra in tool calls: on each
regular bar read already being done for the live trade or (post-close) for ordinary
replay, silently check the bar's close against the frozen ORIGINAL_STOP and against
the horizon timestamp. Resolve and freeze the moment either fires.

After enough trades resolve, compare ACTUAL_RESULT_POINTS/R vs STATIC_RESULT_POINTS/R
in aggregate to judge whether discretionary trailing is VALUE_ADDING, NEUTRAL, or
VALUE_DESTROYING. No such verdict is rendered until real sample size exists.

## 2. Normalized R Metrics

- `INITIAL_RISK_POINTS = |ENTRY - INITIAL_STOP|`, frozen at entry.
- `RESULT_R = RESULT_POINTS / INITIAL_RISK_POINTS`, computed at close.
- `MFE_POINTS` / `MAE_POINTS` (and their R equivalents) — the trade's best/worst
  unrealized excursion during its life.

**Backfill scope for trades before this install:** RESULT_R is backfilled only for
trades where ENTRY and INITIAL_STOP were unquestionably logged, in real time, before
the outcome was known — true for every trade this apprenticeship has taken (the
standing convention has always been to write ENTRY + STRUCTURAL_INVALIDATION/
INITIAL_STOP at the moment of entry). MFE_POINTS/MAE_POINTS for PRIOR trades are
marked `NOT_RECOVERABLE_WITHOUT_HINDSIGHT` in this first pass — precise bar-by-bar
excursion reconstruction for closed trades would require re-reading extensive log
history, which conflicts with the mandate's "must not materially slow replay"
instruction. This is a deferred, separately-schedulable task, not a refusal — the raw
bars already exist in `2020_Q2_H4_LOG.md` if it is later prioritized. Nothing is
fabricated or estimated in its place.

Full-portfolio backfill (trades #1–#47, all prior to this session's active context) is
explicitly OUT OF SCOPE for this installation — those trades' exact entry/stop figures
are not currently loaded in working context, and reconstructing them would require a
dedicated read-through of the full historical log. Flagged as a standing to-do, not
fabricated.

## 3. Prospective Trade Context Tags

For every NEW trade (#57 onward), freeze at entry: H4_REGIME, H1_PHASE, M15_STATE,
REGIME_STACK, DIRECTION_RELATION (WITH_TREND/COUNTERTREND/TRANSITION/NEUTRAL_OR_UNCLEAR),
SESSION (ASIA/LONDON/PRE_US/NY_US_CASH/LATE_US/OTHER — mapped from the UTC hour already
being recorded), VOLATILITY_STATE (LOW/NORMAL/HIGH/EXPANSION/COMPRESSION/UNKNOWN, judged
qualitatively from the recent bar volumes/ranges already being narrated), SETUP_FAMILY,
LOCATION_TYPE, CONFIRMATION_TYPE. These are descriptive tags, not new filters. Old trades
are not retrofitted into categories they were not contemporaneously described in.

## 4. Strategy Evidence Denominator

See `STRATEGY_EVIDENCE_DENOMINATOR.md`. Tracks, per developing playbook:
QUALIFYING_OCCURRENCES, TRADES_TAKEN, TRADES_DECLINED, WINS, LOSSES,
CORRECT_NO_TRADES, INCORRECT_NO_TRADES/MISSED_OPPORTUNITIES, COUNTEREXAMPLES —
so a playbook is never judged only from the subset that became trades.

## 5. Adversarial Twin Review

Deferred to the Q2 checkpoint (`TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md`, not yet
reached). At that point, for each promising playbook, pair successful examples against
the most similar failed examples from already-observed forward evidence and ask what
was identical/different across regime, location, session, volatility, volume,
structure, confirmation, clear-path, distance-to-next-zone, and failure behavior — using
only what was visible prospectively. Any discriminator found this way is labeled
`RETROSPECTIVE_LESSON` and can only affect trading after being explicitly frozen in
`AI_TRADER_REGIME_STRATEGY_MATRIX.md`.

## 6. Regime Transition Watch

See `REGIME_TRANSITION_WATCH.md`. Observation-only; no fixed thresholds; a move against
H4 is not itself transition evidence. Logged only when something concrete is observed
(loss of continuation, failed extensions, role reversal, persistent acceptance beyond
important structure, a change in volatility or directional response character).

## 7. Quarterly Output (deferred to the Q2 checkpoint)

At `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md`: (A) Management Value Report (actual vs
static baseline), (B) R-Normalized Performance (overall and by context), (C) Regime
Performance Matrix (WITH_TREND vs COUNTERTREND, session, volatility state, regime,
setup family — wherever sample size supports it), (D) Adversarial Twin Report, (E)
Strategy Discovery Update (which observations are closest to becoming genuine
playbooks).

## 8. Speed / Implementation Discipline

No verbose narration added to ordinary M15 bars because of this mandate. Trade tags and
baseline fields are written only at trade-entry/trade-close events, and STATIC_BASELINE
resolution checks ride on bar reads already being performed for other reasons — never a
dedicated extra tool call per bar.

## Governance (unchanged, restated for the record)

Do NOT: change existing Q2 trade rules because of this mandate; retrofit outcomes;
invent historical tags; optimize thresholds; touch S5; touch StrategyCatalog; send
anything to Alpha; auto-promote a strategy. This is an evidence-quality upgrade only.
