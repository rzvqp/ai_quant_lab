# PORTFOLIO_ARCHITECT_DESIGN.md — Portfolio Architect Design Report (Flow B roadmap step 2/6)

**Status: DESIGN ONLY. No code written, no code modified, nothing committed to `ai_trader/`.** Produced
per explicit CEO authorization following the ACCEPTED verdict on Strategy Health Integration
(`dc79cb5`/`eb6f9eb`, `PROJECT_STATE_v2.md` §8.24). This document answers the CEO's 10-step
investigation, the 12 mandatory design questions, and the 14-item deliverable, in that order. It
recommends an approach; it does not adopt one — every allocation/arbitration policy choice in §7 and
every item in §14 is an open decision awaiting CEO approval before any implementation begins.

Research for this document was gathered via five parallel, read-only codebase investigations (Signal/
Scoring Engine, Risk Manager, Harness/Portfolio/Execution Simulator, existing portfolio-research tooling
+ Strategy Manager + Decision Intelligence, and the shared-slot root-cause corpus). All file:line
citations below were verified directly against the live source, not assumed from prior documentation.

---

## 1. Current architecture reconstruction

### 1.1 The six frozen, live pipeline modules (per bar, per symbol, in this exact order)

`ai_trader/simulation/harness.py::_run_one_bar` (`harness.py:339-528`) composes six frozen modules
(`market_scanner/`, `strategy_manager/`, `signal_engine/`, `scoring_engine/`, `risk_manager/`,
`execution_engine/` — all `FROZEN (READY)` per `PROJECT_STATE_v2.md` §9) plus the extensible
orchestration layer (`harness.py`, `portfolio_simulator.py`, `execution_simulator.py` — explicitly
`NOT frozen, extensible`, same §9). The current per-symbol sequence, condensed:

1. Market Scanner produces `context_batch` for `as_of` (`harness.py:350`).
2. Strategy handles resolved — either `build_runtime_handles(..., only_ids=self._strategy_id_filter)`
   or `strategy_manager.active_strategies()` (`harness.py:354-369`). This is Strategy Manager's own,
   separate, one-time, contract-declared-maturity admission gate (`ManagerConfig.auto_admit_min_maturity`
   → `_maybe_auto_admit` → `Lifecycle.EXPERIMENTAL → activatable`, `strategy_manager/manager.py:217-230`)
   — unrelated to trading performance, fires once at library load, never re-evaluated live.
3. **Signal Engine** `evaluate()` — pure, no scoring, no risk (`signal_engine/engine.py:6-7`). Hard
   invariant: **exactly one `StrategySignal` per `(strategy_id, symbol, as_of)`**
   (`signal_engine/SIGNAL_ENGINE_API.md:100`, enforced by `_dedupe()`,
   `signal_engine/engine.py:145-165`) — but a strategy CAN produce one signal per symbol per bar across
   *multiple* symbols in the same bar, since the harness loops symbols independently
   (`harness.py:370`) feeding the *same* strategy handles into each per-symbol call.
4. **Scoring Engine** `score_batch()` — pure opportunity-quality evaluator, consumes `StrategySignal`,
   produces `OpportunityScore` 1:1 per signal (`scoring_engine/engine.py:59-90,165-201`). Computes a
   cross-signal `conflict_penalty` component *within this same bar's group* (same `(symbol, as_of)`) —
   this is the Root-Cause Report's "Mechanism B" (§1.4 below). The Ranker
   (`scoring_engine/ranker.py:13-26`) then assigns a total, deterministic `rank` field:
   `sorted by (-total_score, -historical_confidence, -signal_strength, strategy_id)`.
5. `health_eligible_ids` filter (Strategy Health Integration, this session's own prior deliverable,
   `harness.py:379-387`) — subsets `score_batch.scores` to `risk_opportunities`, strictly after Signal/
   Scoring have run unfiltered.
6. **Risk Manager** `evaluate(risk_opportunities, risk_context, portfolio_state)` — processes
   opportunities `sorted(opportunities, key=lambda o: o.rank)` (`risk_manager/engine.py:264`, note: **re-
   sorts by the `rank` field itself, ignoring input list order**), applies a fixed, per-opportunity,
   greedy gate chain (state gate → sanity → recommendation floor/min-score → pre-trade filters →
   portfolio limits → loss/drawdown guards → cooldowns → sizing → constraints;
   `risk_manager/pipeline.py:49-158`), against a **running** `PortfolioState` view that accumulates each
   ALLOW within the same batch (`risk_manager/engine.py:136-153`). Returns `RiskDecisionBatch`.
7. Shadow Evidence tap (`shadow_engine.observe`) — strictly after the real decision, always fed the
   *full, unfiltered* `score_batch`, never `risk_opportunities` (`harness.py:404-411`).
8. ALLOW decisions execute via `execution_engine.execute()`; DENYs recorded as `RiskEventRecord`s
   attributing the correct denied strategy (`harness.py:412-431`; proven by
   `test_shared_slot_denial_is_attributed_to_the_real_denied_strategy_not_the_slot_holder`).
9. Time-stop/trailing-stop overlays, fill matching, portfolio apply, mark-to-market, Shadow settlement
   (`harness.py:437-528`) — unrelated to Portfolio Architect's own scope.

### 1.2 What Risk Manager already does at the portfolio level — and what it does not

`RiskConfig.portfolio_limits` (`risk_manager/config.py:36-46`): `max_positions=5`, `max_per_symbol=1`
(**the "shared slot"**), `max_correlated=2`, `max_exposure_pct=0.30`, `max_leverage=3.0`,
`max_overnight_exposure_pct=0.15`. `correlation_groups: dict[str,str] = {}` is a **static, operator-
declared symbol→group string mapping** — empty by default, so `LIMIT_MAX_CORRELATED` and the
correlation-aware sizing budget split (`risk_manager/sizing.py:51-64`) are effectively inert until an
operator populates it. There is **no computed correlation** anywhere in Risk Manager (no covariance, no
statistical estimate), **no joint/batch-level optimization** across the opportunity set (it is a single
pass down a fixed rank order, greedy, first-come-first-served against a shrinking capacity), and **no
cross-strategy capital allocation strategy** beyond the aggregate exposure/leverage caps and the
even-split-by-correlation-group sizing formula. Sizing itself is fixed-fractional only
(`risk_manager/sizing.py:1-6`) — `VOL_SCALED`/`ATR_SCALED`/Kelly are defined in the type system but never
wired in.

The shared-slot mechanism itself is `check_max_per_symbol` (`risk_manager/limits.py:46-51`) plus the
structural fact that `PortfolioSimulator.account.positions: dict[str, Position]` is keyed by symbol
(`portfolio_simulator.py:89`) — **enforced redundantly at two layers**, Risk Manager's own gate and the
Portfolio Simulator's own dict-per-symbol accounting, so a design that wanted to relax "one position per
symbol" would need to touch both, and both are off-limits here (frozen / not this step's scope).

### 1.3 Strategy Health vs. Strategy Manager — confirmed no overlap

`ManagerConfig.auto_admit_min_maturity` (`strategy_manager/config.py:68-77`) is a **one-time, load-time**
admission keyed on a strategy's *self-declared* contract `Maturity` tier — never re-evaluated against
live results. `shadow_gate.py`'s `PolicyState`/`real_eligible_strategy_ids_at` is an **ongoing, evidence-
driven** real-eligibility filter, recomputed at any `as_of`, sourced from Shadow Evidence's own trade
ledger. No cross-import, no shared state, confirmed by direct code inspection — these are genuinely
orthogonal gates, and Portfolio Architect must respect both without conflating them.

### 1.4 The diagnosed problem (why this roadmap step exists)

`CEO_STRATEGY_CONSTRAINT_ROOT_CAUSE_REPORT.md` verdicts all six current A-Candidate strategies (S1, S13,
S39, S40, S46, S48) as **PORTFOLIO-LIMITED**, via two distinct mechanisms, both resource-contention, not
strategy-quality problems:

- **Mechanism A** (S1/S13/S39): `LIMIT_MAX_PER_SYMBOL` denials — *"a broad, symbol-wide contention
  effect (all six candidates and most other strategies in the library trade the single symbol
  XAUUSD)"* (line 240). S13 alone recorded 1,485 such denials.
- **Mechanism B** (S40/S46/S48): every `BELOW_FLOOR` denial for these three carried an identical
  `conflict_penalty = 0.500` (the Scoring Engine's own `_OPPOSING_PENALTY` constant); a counterfactual
  with the penalty zeroed showed **100% of these events would have cleared the floor** (lines 175-176).

The Root-Cause Report's own recommendation (§9): *"a controlled portfolio-slot experiment... testing an
adjusted shared-slot/conflict-penalty policy in isolation from any sizing change"* is the highest-value
next step. `STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md` already scopes Portfolio Architect's contract
in anticipation: *"Portfolio Architect... would consume [Strategy Health's] already-filtered eligible set
as one of its own inputs when deciding capital allocation/sizing/diversification across the strategies
Health has already allowed to compete — Portfolio Architect does not reach past or override Strategy
Health's own exclusions."*

### 1.5 Existing portfolio-research tooling — confirmed NOT reusable live

`ai_trader/shadow_evidence/{research,comparison,portfolio_research}.py` (Checkpoint 4) provide
`correlation_matrix()`, `trade_overlap_stats()`, `simultaneous_exposure()`, `diversification_metrics()` —
all **pure, offline, full-history batch recomputations over CLOSED positions only**, never imported by
`harness.py`, with no incremental/streaming API and no notion of "as of the current bar." The
*mathematics* (Pearson correlation of monthly PnL, sweep-line concurrency) is a reasonable conceptual
starting point, but a live Portfolio Architect needs a genuinely different, incremental, point-in-time
shape — not a reuse of this module as-is (§8 below).

### 1.6 Decision Intelligence v1/v2 — confirmed disconnected from the harness

Both `decision_intelligence/engine.py::make_decision()` and `decision_intelligence_v2/engine.py
::make_decision_v2()` are pure, read-only, offline advisory systems — a single ranked ACCEPT/REJECT
recommendation, never sizing, never capital, never wired into `harness.py` (zero imports, confirmed by
direct grep). They are outside Portfolio Architect's boundary entirely, per this step's own restrictions.

### 1.7 Single-symbol vs. multi-symbol

The architecture is generically multi-symbol (`SimulationContext.symbols: tuple[str,...]`, threaded
through the per-bar loop, `PortfolioSimulator.account.positions` keyed by symbol) but **every fixture,
test, and dataset in the repo today uses `symbols=("XAUUSD",)` only** — multi-symbol code paths are
architecturally present but functionally unexercised. Any Portfolio Architect design that leans on cross-
symbol diversification would be exercising genuinely untested territory.

---

## 2. Mandatory design questions — explicit answers

**Q1. What exact problem does Portfolio Architect solve that Risk Manager and Strategy Health do not?**
Risk Manager is a per-opportunity, greedy, rank-ordered ALLOW/DENY gate chain with only static,
non-computed portfolio-level limits (§1.2) — it never asks "is this THE RIGHT combination of
opportunities for the portfolio," only "does this one opportunity, in isolation, clear a fixed set of
thresholds against the current running state." Strategy Health answers a strategy-level, bar-independent
question ("is this strategy allowed to compete for real capital at all right now"). Neither considers
computed correlation/redundancy across the SET of opportunities eligible on a given bar, neither
allocates scarce shared capacity (the one XAUUSD slot) by any portfolio-level objective (diversification,
concentration limits, avoiding one strategy/regime dominating), and neither reconsiders Scoring Engine's
own static `conflict_penalty`. Portfolio Architect's job is exactly this: given the eligible, scored
opportunity set for a bar, decide portfolio-level prioritization among them before Risk Manager's fixed
gate chain runs.

**Q2. What is the input contract?** Per bar, per symbol (matching current granularity): the Strategy-
Health-filtered `risk_opportunities: Sequence[OpportunityScore]`, the current `portfolio_state:
PortfolioState` (read-only), optionally `risk_context: RiskContext` (read-only, for regime/data-quality
awareness), and a point-in-time correlation/exposure estimate sourced from Shadow Evidence's own
accumulated ledger (never from future data — §8). A new `PortfolioArchitectConfig` supplies policy
parameters.

**Q3. What is the output contract?** A (possibly reordered-by-replacing-`rank`, possibly subsetted)
`Sequence[OpportunityScore]` — the exact shape Risk Manager already consumes — handed to
`risk_manager.evaluate()` in place of today's `risk_opportunities`. Optionally a parallel, disclosed,
diagnostics-only audit record (never fed back into ALLOW/DENY logic, mirroring Decision Intelligence's
own non-feedback convention). Portfolio Architect must NEVER emit an ALLOW/DENY verdict itself — that
authority stays exclusively with the frozen Risk Manager.

**Q4. At what lifecycle point does it execute?** Immediately after the existing `health_eligible_ids`
filter and immediately before `risk_manager.evaluate()`, inside `_run_one_bar`'s per-symbol loop
(`harness.py`, between the current step at line 387 and line 388) — the exact insertion point the
Strategy Health design doc's own forward-reference already anticipated.

**Q5. Does it rank strategies, individual opportunities, or both?** Individual `OpportunityScore` objects
— because that is Risk Manager's actual input type, and because eligibility (a strategy-level concept) is
already Strategy Health's job. Since Signal Engine guarantees at most one opportunity per
`(strategy_id, symbol)` per bar, per-opportunity and per-strategy ranking coincide in practice today, but
the mechanism operates on opportunities, not strategy identities, so it generalizes correctly if/when
multi-symbol use ever activates.

**Q6. How does it handle multiple opportunities from the same strategy?** Impossible within one
`(symbol, as_of)` pair by Signal Engine's own hard invariant. Possible across *different* symbols in the
same bar (architecturally, currently untested in practice — §1.7). No special dedup logic is needed;
Portfolio Architect must simply operate generically per-opportunity, and a design decision (§14) is
whether/how to treat one strategy holding simultaneous opportunities on multiple symbols as a
concentration concern.

**Q7. How does it prevent one strategy or one market regime from dominating the portfolio?** Candidate
policies, NOT decided (§7): (a) a rolling-window max-share-of-allocations cap per strategy or per
correlation-group; (b) diversification-aware re-ranking that deprioritizes an opportunity whose
strategy/group already holds a disproportionate share of currently open positions or recent trades; (c) a
regime-tag-aware concentration cap if Market Intelligence's regime classification is made available as a
read-only input. All are proposals; none is adopted by this document.

**Q8. How are correlation and redundant exposure estimated without introducing look-ahead?** Only from
data strictly before the current `as_of`, matching every other module's own point-in-time convention
(Scoring Engine's `conflict_penalty` is same-bar/no-future; Risk Manager's `PortfolioState` is
as-of-now). Two candidate sources (§8 below): the existing static `correlation_groups` declared mapping
(cheap, already partially wired into Risk Manager, non-statistical), or a new incremental, point-in-time
estimator built on Shadow Evidence's own `trade_legs` (Shadow already accumulates unconditional evidence
for every strategy — this would be a third reuse of that evidence source, after Strategy Health). The
existing `portfolio_research.correlation_matrix()` is confirmed NOT reusable as-is (§1.5) — a live
estimator would need to be purpose-built.

**Q9. Behavior in named scenarios:**
- *No strategy eligible*: `risk_opportunities` is already empty (Strategy Health's own output) —
  Portfolio Architect must be a no-op returning empty; Risk Manager already handles empty batches
  gracefully (`risk_manager/engine.py:217-223`).
- *One strategy eligible*: pass through unmodified — no diversification policy may veto the sole
  available opportunity down to zero.
- *All strategies eligible*: normal case; apply whatever policy is configured (§7).
- *All opportunities highly correlated*: the dominance scenario Q7 addresses — a concentration cap may
  down-rank/exclude enough to enforce its limit, but must never blank the entire set unless the
  configured cap is stricter than 1 (an explicit, disclosed policy choice, never an implicit side
  effect).
- *Risk capacity exhausted*: this stays Risk Manager's own job (`LIMIT_MAX_EXPOSURE`/
  `LIMIT_MAX_LEVERAGE`/loss-drawdown guards) — Portfolio Architect must not duplicate this logic; it may
  read `portfolio_state` read-only for its OWN prioritization heuristics but must never assume it can
  predict Risk Manager's own gate outcomes.
- *Strategy Health classification changes during a run*: already handled structurally — Portfolio
  Architect only ever sees the CURRENT bar's already-filtered `risk_opportunities`, fresh every bar; no
  separate change-handling logic is needed.

**Q10. Which existing modules can be reused unchanged?** All six frozen pipeline modules (Signal, Scoring,
Risk Manager, Execution, Strategy Manager, Market Scanner), the five frozen Strategy Health modules,
`shadow_gate.py`, and `ShadowEvidenceEngine` (as a read-only evidence source, exactly as Strategy Health
already established) — every one of these, entirely unchanged.

**Q11. Which minimal new integration layer is required?** (a) a new `ai_trader/portfolio_architect/`
package, pure functions only, mirroring `shadow_gate.py`'s own established pattern — no new scoring
logic, one new file/module; (b) one more small, additive, disclosed touch to `harness.py` (the project's
5th such touch to `simulation/`, which is explicitly `NOT frozen, extensible`), inserting a call between
the existing `health_eligible_ids` filter and `risk_manager.evaluate()`, gated by a new optional
constructor parameter defaulting to a true no-op so byte-identical-when-disabled behavior is preserved by
construction — the same convention every prior touch (including `health_eligible_ids` itself) has
followed.

**Q12. What must remain out of scope for this step?** Any code implementation (this step is design-only);
modifying any frozen module (Risk Manager, Signal/Scoring Engine, Execution Engine, Strategy Manager,
Strategy Health's five frozen modules, or `shadow_gate.py`); Decision Intelligence integration; live
trading/MT5 integration; exercising multi-symbol correlation against real multi-symbol data (a separate,
future scoping decision); any change to position sizing (`sizing.py` stays frozen, Risk Manager's sole
authority); any change to the Scoring Engine's `conflict_penalty` mechanism — Portfolio Architect works
AROUND that frozen mechanism, never modifies it.

---

## 3. Portfolio Architect responsibility boundary

**Owns** (proposed, minimal v1 — see §15): relative PRIORITIZATION among an already-eligible,
already-scored opportunity set for one bar, expressed as a re-ranking and/or subsetting of
`OpportunityScore` objects, driven by a portfolio-level objective (diversification / concentration
control) that no existing module computes.

**Does NOT own**: eligibility (Strategy Health), ALLOW/DENY authority, sizing, exposure/leverage/drawdown
limits, cooldowns, pre-trade filters (all Risk Manager); signal generation or scoring (Signal/Scoring
Engine); order execution/fills (Execution Engine); strategy admission (Strategy Manager); any
recommendation/advisory output (Decision Intelligence).

Answering the CEO's explicit ownership-scope question directly: **v1 Portfolio Architect owns only
ranking/prioritization and (optionally) a concentration-driven subset exclusion — it does NOT own capital
allocation sizing, exposure budgeting as a hard limit, correlation control as a hard limit, slot
arbitration as a NEW mechanism (it operates upstream of and defers to Risk Manager's existing
`LIMIT_MAX_PER_SYMBOL` arbitration), turnover control, or concentration limits as hard-enforced caps.**
Every one of those remains Risk Manager's frozen authority; Portfolio Architect can only influence WHICH
opportunities Risk Manager sees and in what priority order, never override what Risk Manager decides once
it sees them. This is a deliberately narrow v1 boundary — see §14 for where the CEO may choose to expand
it in a later step.

---

## 4. Proposed data flow

```
score_batch (full, unfiltered)                                    [Scoring Engine — frozen]
   │
   ├──────────────────────────────────────────────────► shadow_engine.observe()   [unchanged tap]
   │
   ▼
health_eligible_ids filter → risk_opportunities                   [Strategy Health — existing]
   │
   ▼
Portfolio Architect: select_and_prioritize(                       [NEW — this design]
    risk_opportunities, portfolio_state, correlation_estimate, config
) → architected_opportunities
   │
   ▼
risk_manager.evaluate(architected_opportunities, risk_context, portfolio_state)   [Risk Manager — frozen]
   │
   ▼
decision_batch → execution / risk-event recording                 [unchanged]
```

Correlation/exposure estimate itself flows from Shadow Evidence's own accumulated `trade_legs`
(read-only, point-in-time, restricted to strictly-before-`as_of` data) into the new module — a read path
parallel to, and independent of, Strategy Health's own read of the same evidence source (§8, §9).

---

## 5. Proposed interfaces (contracts only — no implementation)

```python
# ai_trader/portfolio_architect/types.py  (proposed — NOT implemented)

class ArchitectPolicy(str, Enum):
    """Which arbitration strategy is active. PASSTHROUGH is the mandatory no-op default."""
    PASSTHROUGH = "PASSTHROUGH"        # returns input unchanged -- the only policy proven safe today
    # further members are open decisions, §14 -- not specified by this design

@dataclass(frozen=True, slots=True)
class PortfolioArchitectConfig:
    policy: ArchitectPolicy = ArchitectPolicy.PASSTHROUGH
    # remaining fields (diversification threshold, correlation window, max-share caps, ...)
    # are open decisions -- §7, §14 -- deliberately left unspecified here

# ai_trader/portfolio_architect/architect.py  (proposed — NOT implemented)

def select_and_prioritize(
    risk_opportunities: Sequence[OpportunityScore],
    portfolio_state: PortfolioState,
    trade_legs: Sequence[ShadowTradeLegRecord],   # point-in-time evidence source, §8
    as_of: int,
    config: PortfolioArchitectConfig,
) -> Sequence[OpportunityScore]:
    """Pure function. Returns risk_opportunities unchanged when config.policy is PASSTHROUGH.
    Never mutates its inputs; any re-ranking is expressed via dataclasses.replace(score, rank=...)
    on copies, matching the Ranker's own established pattern (scoring_engine/ranker.py:13-26)."""
```

`harness.py`'s proposed touch (illustrative only, not implemented):

```python
# between the existing health_eligible_ids filter (harness.py:379-387) and risk_manager.evaluate():
architected_opportunities = (
    risk_opportunities if self._portfolio_architect_config is None
    else select_and_prioritize(risk_opportunities, portfolio_state, self._shadow_trade_legs(), as_of, self._portfolio_architect_config)
)
decision_batch = self._risk_manager.evaluate(architected_opportunities, risk_context, portfolio_state)
```

`self._portfolio_architect_config: PortfolioArchitectConfig | None = None` (default `None` → identical to
today's behavior, no call made at all — stronger than a `PASSTHROUGH` policy, avoiding even the function
call overhead when disabled, matching `health_eligible_ids`'s own `is None` short-circuit).

---

## 6. Lifecycle placement

Confirmed and detailed in Q4/§4: strictly between the Strategy Health filter and Risk Manager's
`evaluate()` call, once per symbol per bar, inside `_run_one_bar`. No other lifecycle point was
considered viable: placing it before Scoring Engine would require re-scoring (touches frozen Scoring
Engine); placing it after Risk Manager would require either overriding ALLOW/DENY decisions (violates the
"Risk Manager stays sole authority" boundary, §3) or operating on already-executed fills (too late to
influence anything).

---

## 7. Allocation and arbitration policy options (NOT decided — proposals for CEO selection)

1. **PASSTHROUGH** (the only safe default) — returns input unchanged. Recommended as the initial,
   validated state before any real policy is authorized (§15).
2. **Static correlation-group concentration cap** — reuse Risk Manager's own existing
   `correlation_groups` declared mapping; re-rank so that once N opportunities from the same declared
   group are already prioritized this bar, further same-group opportunities are down-ranked (not denied
   — Risk Manager's own `LIMIT_MAX_CORRELATED` remains the hard enforcer). Cheapest to build; reuses an
   already-frozen-compatible config surface; inherits the static mapping's own limitation (empty by
   default, requires operator population, non-statistical).
3. **Rolling-window max-share-of-allocations per strategy** — cap how large a share of the last N
   ALLOWed opportunities (or last N days of Shadow-tracked activity) any one strategy may hold before
   being down-ranked relative to less-recently-favored eligible strategies. Directly targets "one
   strategy dominating."
2 vs. 3 vs. a combination, plus the exact threshold values, window lengths, and whether down-ranking vs.
outright exclusion is used, are **all open decisions — §14.**

---

## 8. Correlation and concentration treatment

Two viable point-in-time-safe sources, neither implemented, both compatible with the frozen boundary:

- **(a) Static declared correlation groups** — `RiskConfig.correlation_groups`, already present, already
  read by Risk Manager. Zero new computation, but non-statistical and requires an operator to have
  populated it (currently empty by default across the repo).
- **(b) A new incremental estimator over Shadow Evidence** — Shadow's `trade_legs` already accumulate
  unconditionally for every configured strategy (Strategy Health's own load-bearing invariant, reused
  here as a THIRD consumer of the same evidence source). A live correlation/co-occurrence estimate would
  need to be purpose-built as new, additive code — NOT a reuse of `shadow_evidence.portfolio_research
  .correlation_matrix()`, which is confirmed (§1.5) to be a full-history batch recomputation over closed
  positions only, with no incremental or point-in-time API. Building (b) is real implementation work
  deferred to the eventual implementation step, not decided here.

Concentration treatment (how a cap is enforced once a correlation/co-occurrence estimate exists) is
covered under §7's policy options — down-ranking (soft, Risk Manager still has final say) is recommended
over outright exclusion (hard, removes Risk Manager's own opportunity to evaluate) as the safer v1
mechanism, consistent with Portfolio Architect's narrow §3 boundary, but this is an open decision (§14).

---

## 9. Interactions with Strategy Health and Risk Manager

- **From Strategy Health**: Portfolio Architect receives `risk_opportunities` (already eligibility-
  filtered) as its sole opportunity-set input — it never reaches past or overrides Strategy Health's own
  exclusions, exactly as `STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md` already specifies. It may
  independently read the same Shadow Evidence `trade_legs` Strategy Health also reads (for correlation
  estimation, §8) — a parallel, read-only consumption of one shared evidence source, never a dependency
  between the two modules' own outputs.
- **To Risk Manager**: Portfolio Architect's sole output is a (possibly reordered/subsetted) opportunity
  sequence handed to `risk_manager.evaluate()` in place of today's `risk_opportunities`. Risk Manager's
  own `evaluate()` re-sorts by each opportunity's `rank` field regardless of input list order
  (`risk_manager/engine.py:264`) — so a re-ranking policy MUST express itself by replacing the `rank`
  field on cloned `OpportunityScore` objects (via `dataclasses.replace`, mirroring the Ranker's own
  established technique), not by reordering the list, or the change would silently have no effect. Risk
  Manager's ALLOW/DENY/sizing/limits logic is entirely unaware Portfolio Architect exists — it evaluates
  whatever sequence it is handed exactly as it does today.

---

## 10. Invariants (proposed, for whatever implementation eventually follows)

- Portfolio Architect must never emit an opportunity that was not already present in its own input
  `risk_opportunities` (no fabrication).
- Portfolio Architect must never emit an ALLOW/DENY verdict, a sizing value, or any `RiskDecision` field
  — output type is strictly `Sequence[OpportunityScore]`.
- With `policy=PASSTHROUGH` or the harness config left at its default `None`, competitive execution must
  be byte-identical to the pre-Portfolio-Architect baseline — proven the same way every prior harness
  touch has been proven (`test_shadow_disabled_parity.py`'s own established convention), before any other
  policy is authorized.
- Portfolio Architect must be a pure function of its declared inputs — no hidden global state, no
  implicit read of any evidence source not passed explicitly (mirroring `shadow_gate.py`'s own
  `TestProvenance` discipline).
- Shadow Evidence's own `observe()` tap must remain entirely unaffected by anything Portfolio Architect
  does — it already reads `score_batch` upstream of both the Strategy Health filter and Portfolio
  Architect (`harness.py:404-411`), and this must stay true regardless of what future policy Portfolio
  Architect implements.
- A single opportunity's own `strategy_id`/`symbol`/`signal_id`/`score_id` must never be altered — only
  `rank` (and, if a subsetting policy is chosen, presence/absence in the output sequence) may change.

---

## 11. Failure modes (to design against, not yet implemented)

- **Silent no-op re-ranking**: reordering the input list without replacing `rank` — Risk Manager ignores
  list order entirely, so this would be a no-op that appears to work in code review but does nothing at
  runtime. Must be caught by a dedicated test asserting Risk Manager's own processing order actually
  changed under a non-PASSTHROUGH policy.
- **Recreating a Phase-6.9-style lockout**: if a future policy accidentally couples the correlation/
  exposure ESTIMATE to the same resource it's gating (e.g., estimating correlation only from ALREADY-
  ALLOWED trades, which would shrink to nothing under a strict cap) — the estimate must be sourced from
  Shadow Evidence (unconditional, never gated by Portfolio Architect's own decisions), exactly the lesson
  already learned and encoded in `shadow_gate.py`'s own module docstring.
  Look-ahead leakage: any correlation/co-occurrence computation must be audited to confirm it only reads
  data strictly before the current `as_of` — the single most likely subtle bug in this kind of feature.
- **Duplicating Risk Manager's own limits**: a badly-scoped concentration cap could deny opportunities
  Risk Manager would have allowed anyway (redundant, wasted work) or, worse, conflict with Risk Manager's
  own `LIMIT_MAX_CORRELATED`/`LIMIT_MAX_PER_SYMBOL` in a way that produces confusing, doubly-attributed
  denials. Must stay a strict subset/priority layer, never a second independent enforcement mechanism.
- **Multi-symbol code exercising an untested path**: any policy leaning on cross-symbol diversification
  would be running through architecturally-present but never-yet-exercised multi-symbol code
  (§1.7) — needs its own dedicated multi-symbol test fixtures before being trusted, not a reuse of the
  existing single-symbol test conventions.

---

## 12. Test plan (proposed, for the eventual implementation step)

- **Byte-identical-when-disabled** (mandatory, first test written, matching every prior harness touch):
  `portfolio_architect_config=None` (or `policy=PASSTHROUGH`) produces a competitive fingerprint
  identical to the pre-existing baseline, across the same 4-strategy fixture scale
  `test_health_eligible_ids.py`/`test_shadow_disabled_parity.py` already established.
- **Empty input → empty output** (no-op on the `risk_opportunities` empty case, Q9).
- **Single opportunity is never excluded by a concentration policy** (Q9's "one strategy eligible" case).
- **Re-ranking actually changes Risk Manager's own processing order** — a dedicated test proving the
  `rank`-replacement mechanism (§9) is not a silent no-op; assert two opportunities for the same shared
  slot are ALLOWed/DENYed in the OPPOSITE order under a re-ranking policy vs. PASSTHROUGH.
- **No look-ahead**: a test constructing two runs that are identical up to `as_of` and diverge only
  strictly AFTER `as_of` — Portfolio Architect's output at `as_of` must be identical across both runs
  (the standard "point-in-time" proof pattern).
- **Strategy Health respected**: an opportunity for a PROBATION/DISABLED strategy never appears in
  `risk_opportunities` in the first place (already proven by Strategy Health's own tests) — confirm
  Portfolio Architect's output is always a subset of its own input, never a superset.
- **Concentration cap enforced under a maximally-correlated synthetic scenario** (Q9's "all opportunities
  highly correlated" case), once a concrete policy is chosen (§7/§14).
- **Full regression**: `ai_trader/strategy_health/` (72 tests) and the `simulation/` harness-touching
  suites (`test_health_eligible_ids.py`, `test_harness_integration.py`,
  `test_overlay_survives_demotion.py`, `test_conformance_vs_research_engine.py`,
  `test_risk_event_strategy_attribution.py`, `test_shadow_disabled_parity.py` — 137 tests total, per
  §8.24) must stay green, confirming zero regression on the accepted Strategy Health work.

---

## 13. Migration plan

Additive-only, no migration of existing state required: the new `harness.py` constructor parameter
defaults to `None` (identical to omitting it entirely, matching `strategy_id_filter`'s and
`health_eligible_ids`'s own precedent). No existing test, fixture, or committed result changes behavior
until a caller explicitly opts in by passing a non-`None`/non-`PASSTHROUGH` config. No data migration, no
schema version bump, no change to any frozen module's contract. Rollback, if ever needed, is simply
omitting the new parameter — no reversal procedure beyond that is required given the additive design.

---

## 14. Open decisions requiring CEO approval

1. **Which arbitration policy (§7) to authorize for implementation** — static correlation-group cap,
   rolling max-share-of-allocations, both, or a different mechanism entirely. This document recommends
   starting from PASSTHROUGH-only (prove the wiring byte-identical) before authorizing any real policy,
   but does not choose among the real-policy options.
2. **Correlation source (§8)** — reuse the existing static `correlation_groups` config (cheap, requires
   operator population) vs. build a new incremental Shadow-Evidence-sourced estimator (more work, more
   statistically grounded, a genuinely new module).
3. **Down-ranking vs. exclusion** as the concentration-enforcement mechanism (§8) — this document
   recommends down-ranking (Risk Manager retains final say) as the safer v1 choice but flags it as a
   decision, not a given.
4. **Whether multi-symbol diversification is in scope for v1 at all**, given it would exercise an
   architecturally-present but functionally untested code path (§1.7) — recommend deferring to a later
   step unless the CEO wants to prioritize multi-symbol data/fixtures first.
5. **Whether a diagnostics-only audit record (parallel to `RiskDecision`) is worth building in v1**, or
   deferred until real policies exist to audit.
6. **Exact numeric thresholds** for whichever policy is chosen (max-share percentage, rolling window
   length in days/trades, correlation cutoff) — none are proposed here; these are calibration decisions
   that likely warrant their own small research pass before being fixed, not values invented in this
   design document.
7. **Whether Strategy-Health's own `MIN_EVIDENCE_TRADES=25` convention should be reused as-is** for
   whatever minimum sample size a correlation estimator requires, or whether Portfolio Architect needs
   its own, separately justified threshold.

---

## 15. Recommended minimal design

Build nothing beyond a **structural no-op** first: a new `ai_trader/portfolio_architect/` package
containing exactly the `PASSTHROUGH`-only version of `select_and_prioritize()` (§5) — returns its input
unchanged, unconditionally — wired into `harness.py` via a new, additive, default-`None` constructor
parameter at the exact lifecycle point in §4/§6, proven byte-identical to today's behavior across the
same regression suites already used for Strategy Health (§12's first and last bullets). This establishes
the integration seam, the interface contract (§5), and the invariant tests (§10) with zero policy risk —
matching this project's own repeated convention of proving a new gate is a safe no-op before authorizing
any real behavior inside it (exactly how `health_eligible_ids` itself was built and accepted). Once that
seam is CEO-reviewed and accepted, the open decisions in §14 can be resolved one at a time, each behind
its own explicit authorization, without ever touching a frozen module.

**This document recommends, but does not request authorization for, that minimal PASSTHROUGH-only
scaffold as the next concrete step — implementation itself awaits its own separate CEO authorization, per
this step's own explicit restriction.**
