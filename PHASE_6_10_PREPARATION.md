# Phase 6.10 Preparation — Sparse-Evidence Strategy Governance Design

**Date:** 2026-07-17. **Status: preparation material only. No implementation. No selection made.**
This document contains exclusively: the problem Phase 6.9A found, its evidence, the conclusions that
evidence supports, the questions that remain open, every option worth considering, my own
recommendation, what must NOT be done, and what should be investigated before any implementation
begins. It does not begin Phase 6.10 and does not authorize beginning it.

---

## 1. The problem, stated plainly

Across three independent analyses (Phase 6.9's rolling gate, the Current XAUUSD 12-Month Relevance
Audit, and Phase 6.9A's own funnel audit), the same underlying problem keeps reappearing in
increasingly precise form: **the 43 strategies do not fail because they are bad — they fail to
accumulate enough trading evidence to be judged at all, and Phase 6.9A now shows WHY: the single-
position XAUUSD architecture denies the overwhelming majority of their own actionable signals before
either a Health System or a human ever gets to see whether those signals would have been good or bad.**

Any future governance design (Phase 6.10) is being asked to solve a problem whose root cause is now
measured, not guessed at. This document exists so that design work starts from the evidence, not from
the menu of ideas alone.

---

## 2. The evidence (from `PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_AUDIT_REPORT.md`, verified live)

Window: 2024-10-23 → 2025-10-23 (365 days, 23,639 M15 bars — the most recent complete 12 months lying
entirely outside the sealed holdout). Same $2,000 capital, 5% risk/trade, cost model, seed, execution
model, market data used throughout every phase to date.

- **Only 145 of 1,016,477** signals that reached Risk Manager were ever ALLOWED (0.48%).
- The shared-slot denial reason (`LIMIT_MAX_PER_SYMBOL`) totals **18,879** — roughly **4.8× every
  other genuine risk-policy denial reason combined** (3,919: spread/liquidity/volatility filters,
  cooldown-after-loss, sizing floors, other portfolio limits).
- **Isolated-slot trade counts, summed across all 43 strategies run completely alone (823), are 5.8×
  the actual competitive trade count (142)** over the identical market data and window — i.e., if
  slot contention were removed entirely, the SAME strategies over the SAME market would have produced
  roughly six times as many completed trades.
- Suppression-cause classification across all 43 strategies: **11 have the shared slot as their SOLE
  principal cause; it is a contributing factor in 20 of the 22 "mixed" strategies (31 of 43 total,
  72%)**. By contrast: scoring suppression is the sole principal cause for only 2/43; genuine risk-
  policy suppression and execution suppression are the sole principal cause for **zero** strategies
  each (and execution suppression showed literally zero rejected/expired orders — the only non-fills
  recorded were normal OCO-bracket sibling cancellations).
- Only 8/43 strategies are genuinely low-frequency at the raw-setup-detection level (the earliest,
  most upstream stage, before any pipeline gating). The other 35 generate substantial to massive raw
  signal volume (up to 2,751 actionable signals in the window for one strategy) that overwhelmingly
  never converts to a trade.

**Conclusion the evidence supports, stated as narrowly as the evidence itself supports it**: for the
large majority of these 43 strategies, the dominant reason recent trading evidence is sparse is that
they are competing for one shared XAUUSD position slot, not that their own underlying setups are rare
or that Scoring/Risk/Execution are filtering them out for cause.

**What the evidence does NOT show** (important, stated explicitly so it is not silently assumed by
whichever design follows this document): it does not show that these 43 strategies WOULD be profitable
if given independent slots — only that they would trade far more often. Wave D Audit's own finding
(the single-shared-slot architecture makes results non-additively composition-sensitive) means more
trades is not automatically more genuine edge; some of the additional isolated-slot trades could be
low-quality, and the isolated-slot counterfactual explicitly ALSO changes cooldown-after-loss dynamics
(a symbol-level, not strategy-level, mechanism), so the 823-vs-142 gap is not a pure, isolated measure
of slot contention alone — it is the combined effect of every shared-account dynamic (disclosed in
the Phase 6.9A report itself, §1.3).

---

## 3. Open questions (not answered by any analysis to date)

1. **Would the additional trades unlocked by independent slots actually be net profitable, or merely
   more numerous?** No phase to date has tested this — Wave D Audit's own path-dependence finding is a
   specific warning that composition changes can inflate apparent performance through path-dependent
   artifacts (a single outlier strategy capturing a disproportionate share of a freed slot), not
   genuine broad-based edge.
2. **Is the "genuine low frequency" 8-strategy group (category A) actually low-frequency in the
   underlying market, or could a longer window / different regime reveal more setups?** Only one
   12-month window has been examined this way; the strategies' own full 3.6-year lifetime trade counts
   (Wave D) suggest genuine rarity is plausible for some of these, but this has not been directly
   cross-checked strategy-by-strategy against the Phase 6.9A funnel.
3. **How much of the "shared-slot" effect is same-bar conflict (multiple strategies signaling
   simultaneously, only the top-ranked wins) versus persistent-position blocking (an old position from
   days ago blocking a brand-new, unrelated setup)?** Phase 6.9A's own report notes both flavors exist
   within the same `LIMIT_MAX_PER_SYMBOL` reason code but does not separate them — a future design
   would benefit from knowing which dominates, since the two point toward different remedies (same-bar
   conflict → better conflict-resolution/portfolio-level scoring; persistent blocking → more slots or
   shorter average holding periods).
4. **Would expanding to multiple symbols (not just XAUUSD) relieve the same pressure without adding
   position-count risk on a single instrument?** Not evaluated by any phase to date — this project has
   never traded anything other than XAUUSD.
5. **What holding-period distribution is driving average exposure ~84–88% of bars?** (Portfolio A's own
   average exposure in the relevance audit was 83.8%; Wave D's was 87.7%.) If a small number of very
   long-held positions dominate the occupied-slot time, a different remedy (e.g. tighter time-stops
   generally) might relieve contention without touching the slot architecture itself at all — not yet
   investigated.

---

## 4. Options (menu only — no selection made)

Every item below was already named in the Phase 6.9/relevance-audit handoffs; this section adds, for
each, a one-line note on how directly it addresses the NOW-CONFIRMED shared-slot bottleneck specifically
(as opposed to the Health System's general sparse-evidence problem, which motivated the original menu):

- **A. ACTIVE + WATCHLIST with differentiated risk** (a soft gate instead of a hard one) — lets more
  strategies keep trading at reduced size/frequency rather than being fully excluded; would increase
  slot contention rather than relieve it unless paired with a slot-level change too.
- **B. Hierarchical/Bayesian pooling of evidence across related strategies** — addresses the Health
  System's OWN evidence-sparsity problem (small per-strategy sample sizes), not the slot-contention
  problem directly; orthogonal to Phase 6.9A's own finding.
- **C. Longer evidence windows** — same as B: helps the Health System's own scoring, does not change
  how many trades get through the shared slot.
- **D. A minimum exploration allocation** — a small, guaranteed size/frequency reserved for non-ACTIVE
  strategies. Directly responsive: guarantees SOME slot time to strategies that would otherwise never
  get to prove themselves, at the cost of displacing some ACTIVE-strategy trades.
- **E. Portfolio-level rather than per-strategy Health scoring** — evaluates the PORTFOLIO's own
  realized trades (whoever happened to win the slot) rather than trying to score each strategy in
  isolation from a slot-constrained sample. Directly responsive: sidesteps the attribution problem
  entirely rather than trying to fix it, though it gives up per-strategy accountability.
- **F. Shadow-mode evidence accumulation** — paper-track a strategy's own hypothetical signals even
  when the real slot is occupied, so Health evidence keeps accumulating without needing real capital or
  a real slot. **Most directly responsive to the Phase 6.9A finding specifically**: it targets the
  exact mechanism (no trades → no evidence → no re-promotion) that produced Phase 6.9's own
  self-reinforcing lockout, without requiring more real capital at risk or changing the live slot
  architecture at all.
- **G. Regime-conditioned evidence** — weights evidence by market-regime similarity; orthogonal to the
  slot-contention finding, addresses a different (recency-vs-regime) concern.
- **H. Incumbency-until-negative-evidence** (keep a previously-ACTIVE strategy active until enough
  NEGATIVE evidence accumulates, rather than requiring fresh positive evidence) — reduces churn but
  does not address why FRESH strategies struggle to ever earn ACTIVE status in the first place.
- **I. (New, prompted directly by Phase 6.9A, not on the original menu) Multiple independent position
  slots or multi-symbol expansion** — the only option that changes the architecture Phase 6.9A actually
  measured as the bottleneck, rather than changing how evidence is scored around it. The CEO has
  explicitly instructed: **do not implement multi-position trading now** — listed here only because the
  evidence points at it directly and any complete options menu should say so plainly.

---

## 5. My recommendation

**Investigate, in this order, before designing anything**: (1) resolve open question 3 above (same-bar
conflict vs. persistent-position blocking) and (2) open question 5 (holding-period distribution),
since both are cheap to answer from data already collected (`phase69a_competitive_funnel.json` and the
existing trade ledgers) and would materially change which governance option is worth designing first.
If persistent blocking (not same-bar conflict) turns out to dominate, that argues for shadow-mode
evidence accumulation (F) as the highest-value next design target, since it directly breaks the
self-reinforcing lockout without touching real capital or the live architecture. If same-bar conflict
dominates instead, portfolio-level Health scoring (E) becomes more directly relevant, since the
problem would be more about how competing signals get resolved than about idle capacity.

Between the two, **I would lean toward scoping shadow-mode evidence accumulation (F) as the first
concrete Phase 6.10 design target**, because it is the option most directly aimed at the specific
mechanism Phase 6.9 and Phase 6.9A both measured (no trades → no evidence → no recovery), it requires
no new capital risk, and it does not require deciding up front whether more slots or better scoring is
the "right" long-run answer — it simply keeps the Health System supplied with evidence while that
larger question is worked out. This is a recommendation for what to scope and investigate next, not an
implementation, and open questions 1–2 above should inform the final design regardless of which option
is chosen.

---

## 6. What must NOT be done

- Do not redesign or implement any governance model yet.
- Do not activate any WATCHLIST or INSUFFICIENT_EVIDENCE strategy for live or shadow trading.
- Do not implement multi-position trading.
- Do not begin Shadow Mode, Telegram, Broker Adapter, or MT5 work.
- Do not modify any strategy, its parameters, or its contract.
- Do not modify the Strategy Health System's own scoring methodology, weights, or thresholds.
- Do not modify the Research Lab.
- Do not open the sealed terminal holdout.
- Do not select one of §4's options without a dedicated, separate CEO scoping decision — this document
  recommends an investigation order and a leaning, it does not choose.

---

## 7. What should be investigated before any implementation

- Open questions 1–5 in §3, in particular the same-bar-conflict-vs-persistent-blocking split (question
  3) and the holding-period distribution (question 5), both answerable from already-collected data
  without any new simulation runs.
- Whether a genuinely disentangled "shared-slot-only" counterfactual is possible (one that holds
  cooldown-after-loss dynamics constant across the isolated and competitive runs), to separate the
  823-vs-142 gap into its slot-contention component and its cooldown-dynamics component specifically.
- Whether the 8 genuinely-low-frequency strategies (category A) look different under a longer lookback
  or a different regime — before concluding they are simply rare in all conditions.
- Whatever the CEO's own scoping decision selects from §4 — this document deliberately stops short of
  designing any single option in detail, since that is Phase 6.10's own job once formally opened.
