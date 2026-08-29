# AI QUANT RESEARCH LAB — COMPANY STATE

```
STATUS_DATE                    = 2026-08-29
SCOPE                          = COMPANY_WIDE
AUTHORITY                      = RECOVERY / CONTINUITY
LIVE_TRADING_AUTHORIZED        = NO
Q4_APPRENTICESHIP_STARTED      = NO
FAILURE_ENGINEERING_STARTED    = NO

LAST_COMPANY_RECONSTRUCTION_DATE = 2026-08-29
COMPANY_RECONSTRUCTION_STATUS    = COMPLETE (read-only, repository-evidence-only pass across
                                    every known repo/worktree; see §3 for per-repo detail)
KNOWN_REPOSITORY_COUNT           = 4 distinct git histories
KNOWN_WORKTREE_COUNT             = 11 checkouts (8 under `ai_quant_lab` + 3 standalone clones) +
                                    1 non-git directory (`escrow_red_team`, intentionally outside git)
```

**This file is a pointer/synthesis document.** It does not reproduce department reports — it cites
`SOURCE_REPO` / `SOURCE_PATH` / `SOURCE_COMMIT` for every material claim and sends the reader to the
authoritative artifact. Anything not mechanically re-derivable at the time of writing is marked
`UNRESOLVED` rather than guessed.

**This file does not supersede, rename, or overwrite** `PROJECT_STATE_v1.0.md`, `PROJECT_AUDIT.md`,
or `NEXT_SESSION.md` — those remain the Alpha-Discovery-Lab/Statistician-scoped historical artifacts
they always were (see §9). `COMPANY_STATE.md` is new, sits alongside them, and is the only file of
the four that is genuinely cross-department.

---

## 1. Cold-start recovery order

If all conversation memory disappeared, a new agent should:

1. Read this file (`COMPANY_STATE.md`) in full before touching anything.
2. Verify the repository HEADs listed in §3/§15 against the live repos (`git rev-parse HEAD`,
   `git ls-remote`) — do not trust this file's commit hashes as still-current without re-checking.
3. Read the department-specific authoritative artifact cited for whatever question is at hand —
   this file's summaries are not a substitute for the underlying report.
4. Check current worktree status (`git status`) in whichever repo is about to be touched.
5. Reconcile CURRENT FACT vs. historical/superseded facts — §16 lists known stale artifacts that
   must not be read as current truth.
6. Present the reconstructed state to the CEO.
7. **Wait for CEO authorization before starting any new work.** No item in §16 is auto-authorized
   by this file existing.

---

## 2. Company mission / governance model

Research flows through a fixed pipeline before anything can touch real risk:

```
Discovery  ->  independent validation (Statistician)  ->  adversarial validation (Red Team)
           ->  strategy/platform compatibility (VE / N6 catalog)  ->  risk  ->  execution
```

Distinguish these stages precisely — they are not interchangeable:

| Stage | Meaning |
|---|---|
| `DISCOVERY` | A research team (Alpha, family expansion, etc.) has found a candidate pattern/edge. Not evidence of anything beyond "worth testing." |
| `VALIDATION` | Statistician has independently re-derived the candidate from its own frozen identity (never trusting the discovering team's own report) and issued PASS/FAIL/BLOCKED. |
| `RESEARCH-RATIFIED` | A CEO-approved research baseline for further work — explicitly **not** a production or tradeable status (e.g. RANGE vNext, §8). |
| `DEPLOYED` | Currently the production/live baseline for its function (e.g. RANGE V4.4 as the deployed Market Intelligence detector — a detector, not a tradeable strategy in its own right). |
| `DEMO-ELIGIBLE` | Cleared to run against a real broker DEMO account (S5 only, §4/§12). |
| `LIVE-ELIGIBLE` | Cleared to submit real-money orders. **Currently zero strategies are LIVE-ELIGIBLE, and no LIVE execution adapter exists in the codebase at all** (§12). |

**Standing rules, stated explicitly because they have been violated by omission before:**
- Research evidence is **not automatically a strategy**. A discovery-stage finding, however
  statistically clean-looking, carries no trading authority until it clears Statistician and Red
  Team independently.
- **A Red Team PASS is not final** if later Statistician evidence finds an integrity defect —
  see CRS1 in §7, where a `RED_TEAM_PASS` was practically reversed by a subsequent independent
  Statistician FAIL on a lookahead defect. Verdicts are not permanently binding once a later,
  better-evidenced review contradicts them.
- **No strategy may go live merely because execution capability exists.** MT5 demo-order
  capability exists and is exercised by S5 (§12); this says nothing about any other candidate's
  readiness, and nothing in the codebase currently authorizes LIVE trading for anything.

---

## 3. Repository map

| REPO_ID | PURPOSE | AUTHORITATIVE_BRANCH | REMOTE_POLICY | CURRENT_IMPORTANT_COMMIT | UNCOMMITTED_STATE | DIVERGENCE |
|---|---|---|---|---|---|---|
| `ai_quant_lab` (main hub) | Statistician + cross-department continuity home (this file lives here) | `statistician-foundation` | 4 mirrors: `alpha1`/`discovery`/`lab`/`trader`, all remotes of the same underlying multi-worktree repo | `4163382` | 4 untracked scratch run-logs (`results/matched_null_validation/*.log`) — reproducible artifacts, not source | none — in sync with `lab` |
| `ai_quant_lab` worktree `-alpha-automation` | Alpha Discovery: VOLTIME/DXY/SESSION/VOLPATH frontier program | `alpha-automation-v1` | mirrors `alpha1` (also mirrored on `discovery`/`lab`/`trader` per the 2026-08-29 Alpha merge, §5/§15) | local `6092c8f`; **all four remotes now at `36ab8f7`** — local worktree has not pulled the merge yet | 2997 untracked (99.9% generated loop-state JSON/logs, verified) | **local behind all 4 remotes** — see §16 |
| `ai_quant_lab` worktree `-alpha-discovery` | Alpha "Flow A": E0xx edge-by-edge discovery program | `alpha-discovery` | mirrors `discovery` | `5185cbe` | none | none |
| `ai_quant_lab` worktree `-families` | S21-S51 strategy-family expansion | `family-implementation-s21-s40` | **no upstream configured** | `e3901da` | none | N/A (no remote) |
| `ai_quant_lab` worktree `-research-main` | AI Trader (apprenticeship + S5 execution + strategy-platform integration) | `ai-trader-implementation` | mirrors `trader` | `ace7320` | 12 modified + 6 untracked, all in `ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/` — a foreign, in-progress broker-clock-offset fix, not touched by this document | none on this branch vs. `trader`; separately, `alpha1`/`discovery`/`lab` mirrors of *this* branch lag behind `trader` (pre-existing, §16) |
| `ai_quant_lab` worktree `-research-main-strategies` | New-strategy integration work (G0037/G0184/G0059) | `ai-trader-three-strategies` | **no upstream configured** | `541fc04` | 4 untracked debug dumps tied to the `ve_brain` blocker investigation (§12) | N/A (no remote) |
| `ai_quant_lab` worktree `-stratdev` | Strategy dedup / mechanism library | `strategy-development` | **no upstream configured** | `0d776ec` | none | N/A (no remote) |
| `ai_quant_lab` worktree `-wp5b` | Validation Engineering / Market Intelligence (N1-N6, RANGE) | `discovery-mk-matrix-v1` | mirrors `alpha1` | `344df0f` | 41 untracked files, **not individually characterized** — flagged, not resolved (§16) | none vs. `alpha1` |
| `ai_quant_lab-data-acq` (separate clone) | Chronological Alpha campaign + data acquisition (calendar, M5, DXY) | `alpha-automation-v1` | `origin` | `ed91170` | none | none |
| `aql_stat_clone` (separate clone) | Statistician + Red Team joint validation work | `stat-work` | `origin/statistician-foundation` | `aee0fec` | 3 untracked scratch run-logs | none |
| `tradingview-mcp` (separate repo) | MCP tool server used to drive the AI Trader apprenticeship's TradingView replay | `main` | `origin` | `ab9c449` | 3 modified + 27 untracked, **not characterized this pass** | **2 ahead / 64 behind `origin/main` — real, unresolved history divergence, not investigated** (§16) |
| `escrow_red_team` | Red Team's blind-labeling/custodial-separation workspace | N/A | **intentionally not a git repository** — its own tooling docstring states this is deliberate, so no build/test process in `wp5b` or `alpha-automation` can accidentally consume the blind payload | N/A | N/A | N/A |

**Not every worktree is clean.** Three worktrees have zero uncommitted state (`-alpha-discovery`,
`-families`, `-stratdev`, `data-acq`); the rest have some combination of foreign in-progress work,
generated artifacts, or uncharacterized untracked files — see §16 for the disposition of each.

---

## 4. Current validated strategy state

```
TOTAL_VALIDATED_STRATEGIES = 1
LIVE_ELIGIBLE_STRATEGIES   = 0
```

### Sole validated strategy: S5

```
ID                 = C_2d587447
SIDE               = LONG
MECHANISM          = NY-session opening-range breakout
EXIT               = rr3
VALIDATION         = INDEPENDENT_VALIDATION_PASS
```

**Authoritative validation evidence:** `SOURCE_REPO=aql_stat_clone`,
`SOURCE_PATH=red_team/policy_reviews/RT_S5_S20_CLEAN_INDEPENDENT_VALIDATION_REPORT.md`,
`SOURCE_COMMIT=633bd5d` (mandate `RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001`, E97). All 8
gates (A-H) passed on a frozen clean 52,572-bar population (2023-07-24→2025-10-12): n=295,
BASE/STRESS expectancy both positive, all 3 chronological thirds positive, tail-robust (best-1%
removed still positive), delay-robust (+1 bar), maxDD −6.44R (≤15R ceiling), maxLoss −1.03R (≤2.0R
ceiling), engine-fidelity exact reproduction. Non-scalping (median TP 373 pips).

**Do not classify research detectors (RANGE, N1-N4 outputs) as tradeable strategies** — they are
Market Intelligence components, not strategies with their own validated entry/exit/risk contract
(§8).

---

## 5. Alpha Discovery state

`SOURCE_REPO` given per row. **`ALPHA_HISTORY_MERGE = 36ab8f7`** — verified this session via
`git ls-remote` against all four remotes (`alpha1`, `discovery`, `lab`, `trader`): all four are
synchronized at `36ab8f7` on `alpha-automation-v1`. **The local `-alpha-automation` worktree has not
yet pulled this merge** (still at `6092c8f`) — see §16.

| Frontier | Status | Verdict | Tradeable edge? | Authoritative report | Commit |
|---|---|---|---|---|---|
| Directional (chronological, 6-method campaign) | CLOSED | Cost-verified negative, exhausted | NO | `reports/alpha_discovery/CHRONOLOGICAL_CAMPAIGN_FINAL_REPORT.md` | `a31af7b` (`data-acq`) |
| Directional (Flow A, E0xx, 11 edges) | CLOSED | 11/11 NOT_SUPPORTED | NO | `discovery_candidates/DISCOVERY_CANDIDATE_INDEX.md` + per-edge reports | various (`-alpha-discovery`) |
| VOLTIME | CLOSED | Bounded-negative (predictable magnitude, unmonetizable) | NO (info-only) | `reports/alpha_discovery/VOLTIME_LEDGER.md` | `1a96ce3` (`-alpha-automation`) |
| DXY-NDX1 | CLOSED | Non-directional info only | NO (info-only) | `reports/alpha_discovery/ALPHA_DXY_NDX1_FINDING.md` | `fbbfb91` (`-alpha-automation`) |
| SESSION / SF-3 | CLOSED | All directional session events coinflip | NO (info-only, valid NO_TRADE map) | `reports/alpha_discovery/SESSION_LEDGER.md` | `adc81b0` (`-alpha-automation`) |
| VOLPATH | CLOSED | Both candidates falsified, no monetizable path asymmetry | NO (info-only) | `reports/alpha_discovery/VOLPATH_PHASE1_REPORT.md` | `6092c8f` (`-alpha-automation`) |
| S21-S51 family expansion | ONGOING (exploratory) | 143 research-worthy hypotheses total (S1-S51); only 3 new positives beyond the original 9 (S22, S39, S42); dedup 130 RW -> 17 distinct -> ~6-7 independent economic bets | NO (unvalidated, holdout sealed) | `docs/MECHANISM_DIVERSITY_LOG.md`, `STRATEGY_DEDUPLICATION_REPORT.md` | `646f587` (`-families`), `47d6e5f` (`-stratdev`) |
| `COMP-CONT-L-rr2` | FROZEN candidate, subsequently FAILED | Cross-era sign reversal | NO | `aql_stat_clone` `STAT_COMP_CONT_L_RR2_...` report | `1fb865d` (`ai_quant_lab`) |

**Historical/superseded — do not read as current:** `CANDIDATE_STATUS_REGISTER_v1.1.md`
(`SOURCE_REPO=-alpha-automation`, root, `SOURCE_COMMIT≈31c7406`, 2026-07-25) declares the Alpha
division "ÎNCHIS / CLOSED." This is directly contradicted by a full month of dated frontier work
through the VOLPATH close (`6092c8f`, 2026-08-29) and the subsequent Alpha history merge
(`36ab8f7`). Flagged as `HISTORICAL_CORRECTION`, not current truth.

---

## 6. Statistician state

Independent validation gate. Standing rule: never trusts a candidate's own report — re-derives
identity, causality, and cost model from the frozen specification before issuing a terminal verdict.
Explicit no-retune / no-repair mandate on every review.

| Candidate | Verdict | Note | Source |
|---|---|---|---|
| S5 | *(validated by Red Team on Statistician-frozen population, see §4)* | — | see §4 |
| S20 (`C_09d2245b`) | **FAIL** (Red Team, same mandate as S5) | Failed gate G only (drawdown −23.59R vs. 15R ceiling) — genuinely positive expectancy on every other gate | `aql_stat_clone`, `633bd5d`, RT-ALPHA-S5-S20 |
| CRS1 | **FAIL** | `STAT-CRS1-INDEPENDENT-REVIEW-FDR-001` — non-causal activation-label alignment (lookahead defect); this practically reverses an earlier `RED_TEAM_PASS` on the same candidate (§7) | `ai_quant_lab`, `4163382` |
| `COMP-CONT-L-rr2` | **FAIL** | Cross-era sign reversal | `ai_quant_lab`, `1fb865d` |
| RANGE-lifecycle-vNext | **FAIL** | Unbounded-state blocker | `ai_quant_lab`, `54fa51f` |
| RANGE-vNext-hard-cap | **PASS / READY_FOR_RED_TEAM** | Subsequently Red-Team-passed and CEO-ratified as a **research** baseline only (§8) | `ai_quant_lab`, `90b572e` |
| H4-bo-raw-S | **PACKAGE_AUDIT_PASS / VALIDATION BLOCKED** | No untouched authorized evidence remains to validate against — unresolved, not a clean pass or fail | `ai_quant_lab`, `3498069` |
| PLH-Asia spatial feature | **FAIL** | Not supported | `ai_quant_lab`, `6892bc6` |
| Legacy S1-S20 + 9 SMC state-machine + ~26 DC inventory | **RESEARCH_ONLY, STRICT_VALIDATION_PENDING lab-wide** | Zero families/candidates pass deep independent validation; terminal 20% holdout **never opened** | `aql_stat_clone`, `LEGACY_RESEARCH_LAB_STRATEGY_STATUS_REPORT.md`, `aee0fec` |

`PASS`, `FAIL`, `BLOCKED`, `PACKAGE_AUDIT_PASS`, and `RESEARCH_ONLY` are kept distinct above —
`PACKAGE_AUDIT_PASS` is not a validation pass, it means the audit of the submission package itself
passed while the underlying validation remains blocked.

---

## 7. Red Team state

Independent adversarial reviewer. Uses `escrow_red_team` (§3, deliberately non-git) as a blind
custodial-separation workspace: candidate predictions and ground-truth labels are sealed with
HMAC-authenticated encryption and only reconciled after independent, blind labeling — a design
explicitly intended to prevent VE/Alpha automation from ever reading the blind payload.

**Latest major verdicts:**
- **S5 PASS / S20 FAIL** — `RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001` (E97), §4/§6.
- **RANGE generalization** — the two most recent blind-generalization tests, on both V4.4 and
  V4.4.1, both returned **`GENERALIZATION_NOT_SUPPORTED`** (`aql_stat_clone`, `dfebe8f` and `8e550ae`
  respectively), despite earlier design/implementation audits on the same versions returning
  `PASS_WITH_NONBLOCKING_NOTES`.
- **RANGE-vNext-final** — `RED_TEAM_PASS / RESEARCH_RATIFICATION_READY` (`ai_quant_lab`, `986cba8`,
  E100) — research-only, see §8.
- **CRS1** — `RED_TEAM_PASS` (`ai_quant_lab`, `57b2883`, E101).

**Explicit standing caveat:** Red Team evidence is not immune to later reversal. CRS1's
`RED_TEAM_PASS` was practically superseded by Statistician's subsequent independent FAIL
(`4163382`, a lookahead/non-causal-alignment defect) — the later, better-evidenced review controls
in practical effect, even though neither document is edited to "undo" the other.

---

## 8. VE / Market Intelligence

**Canonical architecture, as actually implemented (not as originally conceived) — `SOURCE_REPO=-wp5b`:**

```
N1 = ve_n1_replay (H4 regime / structural-axes replay engine; also houses the RANGE detector line)
N2 = ve_tower.n2  -> code/bias_h1.py (compute_bias)          — H1 directional factor
N3 = ve_tower.n3  -> code/zone_map.py (build_zone_map)        — zone map, strict M15
N4 = ve_tower.n4  -> code/zone_confirmation.py                — zone confirmation, strict M5
N5 = DOES NOT EXIST — confirmed by exhaustive grep across the repo (only 2 incidental,
     unrelated doc hits for the literal token "N5")
N6 = ve_brain.n6  — final decision gate; sealed strategy catalog (§12)
```

**Canonical production/replay entrypoint: `ve_tower.run_tower_chain`.** Direct calls to
`run_n2`/`run_n3`/`run_n4` are explicitly disclaimed in `ve_tower`'s own review history
(`RT-TOWER-0007`) as `UNBOUND_DIRECT_API` — not proof of the production path.

**A parallel, unratified package exists: `ai_trader/market_intelligence/`.** `code/market_bus.py`'s
own docstring explicitly disclaims reusing it (*"NU reia MarketIntelligenceSnapshot (stratul
market_intelligence paralel, neratificat)"*). **Status: `UNRATIFIED / PARALLEL_OR_DEAD_PATH` — not
canonical, must not be represented as canonical in any downstream report.**

**RANGE deployment split:**
- **RANGE V4.4 (`3bb61cf`) = the current DEPLOYED baseline** for Market Intelligence RANGE
  detection.
- **RANGE vNext = RESEARCH-RATIFIED ONLY, not deployed.** `SOURCE_PATH` (`-wp5b`)
  `ve_n1_replay/RANGE_VNEXT_RESEARCH_RATIFICATION_AND_HANDOFF.md`, `SOURCE_COMMIT=344df0f`. Direct
  quote: *"NOT authorized: production, New Brain, AI Trader runtime, live shadow, MT5, broker, order
  submission, live trading... Do not silently replace deployed v4.4 with vNext anywhere."*

---

## 9. Historical department-scoped continuity artifacts (preserved, not company-wide)

`PROJECT_STATE_v1.0.md`, `PROJECT_AUDIT.md`, `NEXT_SESSION.md` (all `SOURCE_REPO=ai_quant_lab`,
repo root) are **Alpha-Discovery-Lab / Statistician S1-S20 campaign-scoped** documents — matched-null
validation, deduplication (D11), method-validity tracking. `PROJECT_STATE_v1.0.md` and
`NEXT_SESSION.md` last touched `1bc0ffb`/`d4ee4bb` (2026-07-13); `PROJECT_AUDIT.md` was updated more
recently (`50b5cb0`, 2026-07-28) but its scope remains the same narrow campaign — it is **not**
company-wide despite the later edit date. **Preserved as-is, not renamed or overwritten by this
document.**

---

## 10. Strategy Platform / N6 sealed-catalog blocker

**`SOURCE_REPO=-research-main-strategies`, `SOURCE_PATH=INTEGRATION_BLOCKED_VE_BRAIN_STRATEGY_CATALOG.md`,
`SOURCE_COMMIT=541fc04`.**

`ve_brain` (installed version 0.1.3) implements N6 with a **sealed, non-parameterized, 4-entry
internal catalog** (`trend_pullback`, `range_fade`, `trend_shadow`, `trend_experimental`, all
`strategy_version="v1"`). Three new AI Trader strategies — **G0037** (TREND_UP pullback long),
**G0184** (TREND_UP continuation long), **G0059** (TREND_UP momentum long) — use
`strategy_version` values derived from a canonical rerun hash that structurally cannot match `"v1"`.
`ve_brain.decide_n6()` therefore returns `NO_TRADE / UNKNOWN_STRATEGY` unconditionally for all three,
before eligibility, N3/N4 availability, or probability inputs are ever examined. Proven via 8
passing adversarial tests, including a control case confirming a genuinely catalog-registered
strategy proceeds further.

All three strategies are wired behind feature flags, **DEFAULT OFF (fail-closed)**.

**This is an ENGINEERING / COMPATIBILITY blocker — it is NOT evidence that G0037/G0184/G0059 are
profitable or unprofitable.** Resolution requires a new, versioned `ve_brain` release that registers
these strategies, followed by an appropriate Red Team pass. **No change is authorized by this
document.**

---

## 11. AI Trader apprenticeship

**Checkpoint: `SOURCE_REPO=-research-main` (branch `ai-trader-implementation`), `SOURCE_COMMIT=ace7320`**
(`docs/trader_apprenticeship/TRADER_KNOWLEDGE_CHECKPOINT_2020_Q3.md`,
`AI_TRADER_Q2_VS_Q3_FORENSIC_REVIEW.md`, `AI_TRADER_Q3_INTEGRITY_AUDIT.md`).

```
Q1 = COMPLETE
Q2 = COMPLETE
Q3 = COMPLETE
Q4 = NOT STARTED
```

**Q3 actual trade record:** 5 trades, 0 wins, 5 losses, **NET_R = -6.106R**. Execution has been
frozen since 2020-07-22 (in-quarter replay time) — no trade has been taken since.

**PATTERN-007** (the quarter's central behavioral finding — a severe H1-EMA50 break followed by an
eventual reclaim, observed inside one continuous advancing-trend episode):

```
RAW_TALLY               = n=31  (22 SUPPORT / 1 COUNTEREXAMPLE / 8 AMBIGUOUS)
STRICT_PROSPECTIVE_TALLY = n=23  (15 SUPPORT / 1 COUNTEREXAMPLE / 7 AMBIGUOUS)
BEHAVIORALLY_REAL                     = YES
TRADEABLE_WITH_CURRENT_DEFINITION     = NO
DISCRIMINATOR                         = INSUFFICIENT_EVIDENCE
PLAYBOOK_READY                        = NO
```

**Q2->Q3 learning comparison** (23-category audit, `AI_TRADER_Q2_VS_Q3_FORENSIC_REVIEW.md`):
`MARKET_READING = MIXED`, `NO_TRADE_QUALITY = IMPROVED`, `FAILURE_RECOGNITION = IMPROVED`.

**Q3 batching-integrity correction (do not restore the superseded count):** the original Q3
completion report claimed "5 PATTERN-007 instances affected by batching lapses, 3 excluded, 2
included." A dedicated forensic audit (`AI_TRADER_Q3_INTEGRITY_AUDIT.md`, same commit) found this
**materially wrong** — the true quarter-wide count of batching/same-batch-flagged instances is
**7**, and within the session's own window only **1** instance (not 2) survives a strict
chronological proof of blind classification. **The corrected figures (RAW n=31 / STRICT n=23, 7
batching incidents) are current truth; the original "5 incidents" claim is historical/superseded,
preserved in the audit document as a disclosed self-correction, not as current fact.**

**Separate from S5** (§4/§12) — S5 is an independently-validated strategy on its own MT5 execution
track; it is not part of the PATTERN-007 / apprenticeship trade record and is not frozen the way the
apprenticeship's own manual trades are.

---

## 12. Execution / MT5

`SOURCE_REPO=-research-main`, `SOURCE_PATH=ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/`.

**CAPABILITY** (what the code can do): `MT5DemoBrokerAdapter` submits real market orders via
`order_send`. No limit orders, no cancel. **No LIVE execution adapter exists anywhere in this
codebase** — `execution_mode.py` defines exactly two values, `DISABLED` and `MT5_DEMO_ONLY`; any
other value raises an error.

**AUTHORIZATION** (what conditions the code currently checks before allowing an order): a chain of
live, re-verified-every-call gates inside the adapter itself — connection established,
algo-trading enabled, `account_is_demo is True` (hard-refuses any non-demo account), expected-server
match, order volume ≤ configured max. A separate, unrelated `BrokerOrderSubmissionGate` kill-switch
exists elsewhere in the repo (`ai_trader/mandate2_readiness/broker_gate.py`, `enabled=False` by
default) but is **not wired into** this execution path — informational only, not currently gating
anything here.

**`RUNTIME_STATE_AT_AUDIT`** (time-sensitive — re-verify before relying on this, do not treat as
permanent): at the time of the 2026-08-29 company reconstruction pass, two Windows Scheduled Tasks
(`AITraderS5MT5DemoSoak`, `AITraderLiveShadow`) were confirmed **`Running`** with live OS process
IDs, connected to a DEMO account (`FPTradingLLC-Demo`), heartbeat current, `safety_blocked: false`.
**Zero orders had been submitted** (empty execution ledger; the audit fell on a weekend with markets
closed). This describes S5's demo-soak process specifically — **it does not constitute live trading,
and nothing here authorizes any strategy for LIVE execution.**

---

## 13. Data state

| Dataset | Source | Coverage | Governance | Holdout | Known limitations |
|---|---|---|---|---|---|
| XAUUSD M15/H1/H4/D1 | OANDA via TradingView Desktop CDP replay | 2023-01-02 -> present (statistical-campaign copy) | Governed | 20% terminal holdout, **SEALED, never opened** | UTC-hour-21 bar-count drop (~896 vs. ~2900/hr) — documented dataset artifact, not imputed or treated as a market finding |
| XAUUSD native M5 | OANDA via TradingView Desktop CDP replay | **2021-07-27 -> present** — no earlier native data exists; **synthetic/interpolated pre-2021 M5 reconstruction is explicitly forbidden by mandate** | Governed, **gated-loader only** — direct `read_csv` on `data/market/` disallowed by policy | DEV+CALIB populations frozen through 2024-06-20 (155,258 bars); gate not extended past that date | **N4 (zone-confirmation) currently excluded** from the M5 research surface — Statistician found a 2025+ region intended to be sealed as `OUTCOME_UNSEEN` had already been read by a script that bypassed the manifest gate; N4 and everything downstream of it is excluded from M5 Alpha-trigger research until re-sealed |
| DXY (US Dollar Index) | `ICEUS:DXY`, TradingView Desktop CDP replay | 2011-07-14 -> 2024-01-05 (raw) / -> 2023-12-29 (research-usable) | Contract-governed (`DXY_DATA_CONTRACT.md`) | 2024-01-01 onward **PROTECTED**, not usable for discovery | Cash/index series, not UUP/synthetic-basket/futures proxy — identity explicitly restricted to the ICE official series |
| Economic calendar | ForexFactory, weekly capture | Rolling, current | Active recurring automated OS Scheduled Task (verified weekly cadence over 3 consecutive weeks) | N/A | N/A |

**No evidence was found that US10Y, real yields, or GC (beyond the already-closed foundation-track
order-book engine) are currently integrated into any active research or execution path.** Do not
assume integration merely because these instruments have been discussed — only the four datasets
above are confirmed present and governed.

---

## 14. Current known integrity / provenance issues

| Issue | Classification | Detail |
|---|---|---|
| Q2 apprenticeship duplicate log unresolved | `UNKNOWN_PROVENANCE` | Two non-identical `2020_Q2_H4_LOG.md` files exist (`docs/trader_apprenticeship/` root, 8,313 lines, vs. `lane_a_historical/`, 22,570 lines) with no mechanical proof of which supersedes which; both retained, neither deleted. `SOURCE: -research-main, AI_TRADER_APPRENTICESHIP_MANIFEST.md, ace7320`. |
| Q3 batching-integrity correction | `HISTORICAL_CORRECTION` | See §11 — 7 incidents (not the originally-reported 5), 1 (not 2) validly strict-prospective. Disclosed, not silently fixed. |
| N4/M5 contaminated-region limitation | `BLOCKER` (for any M5+N4 strategy work) | See §13 — a 2025+ region intended as `OUTCOME_UNSEEN` was already read outside the gate; N4-dependent M5 research is blocked until re-sealed. |
| Stale Alpha "CLOSED" register | `HISTORICAL_CORRECTION` | `CANDIDATE_STATUS_REGISTER_v1.1.md` (2026-07-25) — superseded by a month of subsequent frontier work and the Alpha history merge (§5). |
| Sealed N6 catalog blocker | `BLOCKER` | See §10 — G0037/G0184/G0059 cannot reach a decision through `ve_brain` 0.1.3 at all. |
| `-wp5b` untracked files | `UNKNOWN_PROVENANCE` | 41 untracked files, not individually characterized by the company-wide reconstruction pass — requires department review before any staging decision. |
| Foreign `mt5_demo_bridge` active modifications | `NONBLOCKING_DEBT` (appears to be legitimate active work) | 12 modified + 6 untracked files in `-research-main`, implementing a broker-server-clock-offset fix (`broker_clock.py`); confirmed not to touch any execution-authorization logic (§12); not committed by this or the prior AI Trader session — belongs to whoever authored it. |
| `tradingview-mcp` history divergence | `UNKNOWN_PROVENANCE` | 2 ahead / 64 behind `origin/main`, unresolved, not investigated — needs its own dedicated review. |
| Local Alpha worktree behind the merge | `NONBLOCKING_DEBT` | `-alpha-automation` worktree local HEAD `6092c8f`; all four remotes now at `36ab8f7` (verified this session via `git ls-remote`). The worktree simply hasn't pulled yet — not a conflict, just unsynced. |
| No-upstream strategy worktrees | `UNKNOWN_PROVENANCE` | `-families`, `-stratdev`, `-research-main-strategies` have no configured remote at all — unclear whether this is intentional (local-only research) or an oversight. |

---

## 15. Remote / checkpoint status

```
AI_TRADER_CHECKPOINT    = ace7320   (repo: ai_quant_lab-research-main, branch: ai-trader-implementation)
ALPHA_HISTORY_CHECKPOINT = 36ab8f7  (repo: ai_quant_lab, branch: alpha-automation-v1)

Alpha remote state (verified via git ls-remote, this session):
  alpha1     -> 36ab8f7
  discovery  -> 36ab8f7
  lab        -> 36ab8f7
  trader     -> 36ab8f7
```

**This does NOT mean the entire company is fully synchronized.** See §14 — the local
`-alpha-automation` worktree itself has not pulled `36ab8f7` yet, `-wp5b` has 41 uncharacterized
untracked files, `tradingview-mcp` has an unresolved 64-commit divergence, and several worktrees have
no remote at all. Mirror synchronization at the Alpha-history level is one specific, verified fact —
not a claim about every repository.

---

## 16. Open CEO decisions

No item below is authorized by this document's existence. Each requires an explicit, separate CEO
decision:

1. Failure Engineering / Negation Rules authorization.
2. Q4 apprenticeship authorization.
3. Next Alpha research frontier / new substrate (directional space is exhausted per §5 — what next
   is undecided).
4. N6 sealed-catalog resolution (new `ve_brain` release + Red Team pass for G0037/G0184/G0059).
5. `mt5_demo_bridge` active-work disposition (whose work is it, should it be committed).
6. `-wp5b` untracked-file provenance review.
7. Whether the no-upstream strategy worktrees (`-families`, `-stratdev`, `-research-main-strategies`)
   should get a remote, or are intentionally local-only.
8. `tradingview-mcp` divergence resolution.
9. AI Trader Q2 duplicate-log resolution (§14).
10. Company-wide remote/mirror policy — should every branch mirror all four remotes, or is
    per-branch/per-team mirroring (as currently observed) the intended design?

---

*Produced under CEO DIRECTIVE — CREATE COMPANY-WIDE CONTINUITY HUB V1. Source discipline: every
material claim above cites a `SOURCE_REPO`/`SOURCE_PATH`/`SOURCE_COMMIT` traceable to the read-only
company-wide reconstruction pass completed the same day. No repository was mutated in the production
of this document beyond its own commit (see the accompanying final report for commit/push details).*
