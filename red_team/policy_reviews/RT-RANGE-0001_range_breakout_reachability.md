# RED TEAM — RANGE / BREAKOUT_TRANSITION GIT-ONLY REACHABILITY INVESTIGATION
### RT-RANGE-0001 · **RT_RANGE_BREAKOUT_REACHABILITY_REPORT_READY**
**Date:** 2026-08-18 · **Auditor:** Red Team · **Method:** static, Git-only + ratified documents. No implementation, no backtest, no engine change, no Alpha run, no LIVE_SHADOW access, no PnL, no 2025‑11+ data, no enum reinterpreted to force a route. For the Statistician, then the Architect/VE.

# BOTTOM LINE
**BREAKOUT_TRANSITION is statically unreachable, and RANGE is never produced — both by construction, provable from Git.** `applicable_regimes` emits BREAKOUT_TRANSITION only when `is_displacement AND structure == "range"`, but the current N1 producer (`RawAxesBuilder`@`21ae632`) maps structure **only** through `_BREAK_KIND_TO_STRUCTURE_DIRECTION = {bos_bull/bos_bear→"strong", choch_bull/choch_bear→"weak"}` — so `structure ∈ {None,"weak","strong"}` and **`structure == "range"` can never be true**. RANGE was deliberately **retracted** by CEO decision (`bd60c7a`) and survives only as a declaration-only enum value routed fail-closed to `TRUE_RANGE_NOT_IDENTIFIABLE`. This exactly matches Alpha's ledger finding (BREAKOUT_TRANSITION on zero bars); the 44 breakout hypotheses are correctly `NOT_EVALUATED — REGIME_UNREACHABLE`, not falsified.

---

## §1 — Authoritative sources (file · commit · line)
- **RawAxes / RawAxesBuilder** — `ai_trader/new_brain_bridge/raw_axes_builder.py`@`21ae632` (blob `d071c8cb`, the same N1 producer the live runtime and both replay wheels use). `observe()` L95‑119: `structure, direction = _structure_and_direction(breaks)`; `is_displacement = bool(exp[last])`; `is_compressed = bool(comp[last]) if valid[last] else None`.
- **structure/direction enums & values** — `ve_brain.RawAxes`@`fbc0f20` (`regime_routing.py` L46‑52): `direction ∈ {down,weak_down,neutral,weak_up,up}`, `structure ∈ {none,range,weak,strong}` *as vocabulary*. The **producible** set is narrower (see §3). Break kinds: `market_structure.BreakKind`@`61cbd58c` (L55‑59) = `BOS_BULL, BOS_BEAR, CHOCH_BULL, CHOCH_BEAR` only.
- **StrategyRouter / applicable_regimes** — `ve_brain/regime_routing.py`@`fbc0f20`: `applicable_regimes` L58‑72; `StrategyRouter._decide` L239+ (`router-v1`).
- **RANGE predicate** — none in `applicable_regimes` (no branch emits `SemanticRegime.RANGE`); L33 `RANGE = "RANGE"  # NEIDENTIFICABIL … NICIODATĂ produsă`. Router L245: RANGE-dependent strategies → `TRUE_RANGE_NOT_IDENTIFIABLE`.
- **BREAKOUT_TRANSITION predicate** — `regime_routing.py`@`fbc0f20` L65‑66: `if axes.is_displacement and axes.structure == _STRUCT_RANGE ("range"): out.add(BREAKOUT_TRANSITION)`.
- **Detectors** — via `structural_observer/vendor_bridge.py`@`21ae632` (L40‑42): `market_structure` (`detect_swings, label_structure, detect_breaks`), `imbalance_mechanics` (`detect_fvgs, detect_fvg_reactions`), `market_state` (`expansion, compression, sessions, atr14`), all @`61cbd58c`. **No trendline, retest, or liquidity‑sweep detector is imported.**
- **N1/Router contracts** — `n1-replay-request-v1`, `router-v1`, `raw_axis_schema_version`, `n1_contract_version` (ve_brain `version.py`@`fbc0f20`).
- **RANGE block / retraction** — `bd60c7a` "Retract RANGE mapping + single-state partition (DECIZIE CEO pe defectul de range)"; `7e4f155` "CEO decision on range defect: mean-reversion pairs BLOCKED (TRUE_RANGE_NOT_IDENTIFIABLE)"; `c962f75` (RT-AUDIT-MEAS-0007, +5 handoff conditions + multi-axial router); `c111d82` (FAIL-2 additive independent axes). Ratified docs: `ve_brain/CONTRACTS.md` L48‑54, `HANDOFF_GATES.md` L36‑39, L122.
- **Prior BREAKOUT_TRANSITION proxy** — `bd60c7a` diff (removed CEO note) + `HANDOFF_GATES.md` L122: it was always a **per-bar proxy**, never a longitudinal detector.

## §2 — Hypotheses (CONFIRMED / INFIRMAT / NECONFIRMAT)
| # | Hypothesis | Verdict | Evidence |
|---|---|---|---|
| 1 | `StructBand.RANGE` means a freshly-flipped/unstable direction, not a lateral range | **CONFIRMAT** | `regime_routing.py`@`fbc0f20` L11‑12; `CONTRACTS.md` L54 ("struct=range … dovadă de INSTABILITATE (flip proaspăt), NU de range"); `bd60c7a` quotes Red Team+Statistician: "axa de structură NU are stare de 'piață laterală'" |
| 2 | The structure axis cannot emit a true range | **CONFIRMAT** | `_BREAK_KIND_TO_STRUCTURE_DIRECTION`@`21ae632` produces only `strong`/`weak`; intended "range" was POST-FLIP instability, not consolidation |
| 3 | `Direction.NEUTRAL` conflates real range / warmup / missing structure / fail-closed | **CONFIRMAT** | `bd60c7a` message; `CONTRACTS.md` L50 ("conflatează PATRU situații") |
| 4 | Using NEUTRAL as RANGE would misroute warmup/unavailable | **CONFIRMAT** | `bd60c7a`: "Maparea ar fi rutat barele de WARMUP în range" — the stated reason for retraction |
| 5 | BREAKOUT_TRANSITION was only a per-bar proxy, not a longitudinal detector | **CONFIRMAT** | `HANDOFF_GATES.md` L122 ("proxy per-bară; versiunea strictă cere un detector de tranziție 2-stări peste N1"); `applicable_regimes` L59 ("Pură, per-bară") |
| 6 | RANGE was blocked via `TRUE_RANGE_NOT_IDENTIFIABLE` | **CONFIRMAT** | `bd60c7a`, `7e4f155`; Router L245; `CONTRACTS.md` L50‑52; `HANDOFF_GATES.md` L36‑39 |
| 7 | Work items `TRUE_RANGE_DISAMBIGUATION` / `data_readiness` / `consolidation_state` existed | **CONFIRMAT** | `CONTRACTS.md` L52‑53: "Dezambiguizarea = work item SEPARAT (câmpuri aditive `data_readiness` / `consolidation_state`, cu spec cauzală + preînregistrare + Red Team + CEO)" |

## §3 — Truth table & reachability
`RawAxesBuilder`@`21ae632` sets `(structure, direction)` **together** from the latest break only (`_structure_and_direction` L123‑130); no break → `(None, None)`. Producible pairs are exactly:

| latest break kind | structure | direction |
|---|---|---|
| — (none) | None | None |
| bos_bull | strong | up |
| bos_bear | strong | down |
| choch_bull | weak | weak_up |
| choch_bear | weak | weak_down |

with `is_compressed ∈ {None, True, False}` (None during warmup / invalid ATR window) and `is_displacement ∈ {True, False}`. Feeding every producible combination through `applicable_regimes`@`fbc0f20` (`_DIR_UP={up,weak_up}`, `_DIR_DOWN={down,weak_down}`, `_STRUCT_TREND={weak,strong}`, `_STRUCT_RANGE="range"`):

| structure | direction | is_compressed | is_displacement | applicable_regimes |
|---|---|---|---|---|
| None (or any axis None) | — | — | — | {UNCERTAIN} |
| strong | up | False | F/T | {TREND_UP} |
| strong | up | True | F/T | {TREND_UP, COMPRESSION} |
| strong | down | False/True | F/T | {TREND_DOWN} (+COMPRESSION) |
| weak | weak_up | False/True | F/T | {TREND_UP} (+COMPRESSION) |
| weak | weak_down | False/True | F/T | {TREND_DOWN} (+COMPRESSION) |

- **Reachable regimes: `UNCERTAIN`, `TREND_UP`, `TREND_DOWN`, `COMPRESSION`.**
- **Impossible: `RANGE`** (no `applicable_regimes` branch produces it) **and `BREAKOUT_TRANSITION`** (its only trigger is `structure == "range"`).
- **The exact condition that can never become true: `axes.structure == "range"`.** `is_displacement` is irrelevant to BREAKOUT_TRANSITION reachability because it is AND‑gated behind that condition; wherever `is_displacement` is True the structure is already `strong`/`weak`, so only TREND_UP/TREND_DOWN can fire.
- **Ledger cross-check:** Alpha's canonical N1 ledger shows BREAKOUT_TRANSITION on **zero bars** — exactly what this static proof predicts. The proof is *definitive*, not merely empirical: no input the current `RawAxesBuilder` can emit satisfies the predicate. (No ledger re-run or benchmark performed.)

## §4 — Where real breakouts go today
- **BOS bullish** → `strong`/`up` → **TREND_UP**. **BOS bearish** → `strong`/`down` → **TREND_DOWN**.
- **CHoCH bullish** → `weak`/`weak_up` → **TREND_UP**. **CHoCH bearish** → `weak`/`weak_down` → **TREND_DOWN**.
- **Compression exit / displacement** — `is_compressed`/`is_displacement` are independent axes; a displacement bar with a break resolves to **TREND_UP/TREND_DOWN** (+`COMPRESSION` if still compressed). It **never** yields BREAKOUT_TRANSITION.
- **Close outside a structure** — only observable when `detect_breaks` fires a BOS/CHoCH (body close vs prior HH/LL/HL/LH) → **TREND**.
- **Retest** — **no detector exists** → **lost** (not classified).
- **Sweep over high / under low + return** — **no N1 detector** → **lost**, unless it incidentally produces a BOS/CHoCH.
- **Trendline breakout** — **no trendline detector exists** anywhere in the N1 surface (verified against `vendor_bridge` imports) → **lost**.

**Separation:** *breakout from range* — impossible (range never exists to break out of); *structural breakout (BOS/CHoCH)* — absorbed into TREND_UP/TREND_DOWN; *trendline breakout* — no detector, entirely absent.

## §5 — Architectural verdict (evidence-only, no implementation)
The demonstrated answer is **B for RANGE + C for BREAKOUT**, with **A as the sanctioned future work item**:
- **RANGE — B (intentionally blocked, dead route):** retracted by `bd60c7a`; a declaration-only enum; RANGE-dependent strategies are fail-closed at `TRUE_RANGE_NOT_IDENTIFIABLE` (Router L245). It is **not** an accidental omission. To become a *real* regime it needs a **new versioned producer** (the CEO-declared work item: additive `data_readiness` / `consolidation_state` with a causal spec + pre-registration) — that is **A**, deliberately deferred.
- **BREAKOUT_TRANSITION — C (event, not per-bar regime):** the current per-bar-proxy regime is a **dead predicate** (`structure=="range"` never emitted). The ratified path (`HANDOFF_GATES.md` L122) is a **longitudinal 2‑state transition detector over N1** — i.e., breakout modeled as an **event within a regime**, not a standalone per-bar regime.

**On the CEO's proposed model** — regimes `{TREND_UP, TREND_DOWN, RANGE, UNCERTAIN}` + events `{RANGE_LOW/HIGH_REJECTION, BREAKOUT_CANDIDATE, BREAKOUT_ACCEPTED, BREAKOUT_RETEST, FAILED_BREAKOUT, LIQUIDITY_SWEEP_REVERSAL}`: it is **compatible** with `N1→Router→N3→N4→EV→N6` in shape, but requires new production, not a re-labeling. Needed: (1) a **new versioned N1 producer** emitting a genuine longitudinal RANGE/consolidation state (new axis or a real `structure="range"` backed by `consolidation_state`), so `applicable_regimes` can actually produce RANGE; (2) a **stateful 2‑state breakout detector** to emit the breakout events (the events naturally bind to N3 levels / N4 confirmation, which already exist); (3) Router changes to route RANGE (removing the fail-closed) and to arm/confirm the events. **Contract/version bumps required:** `n1_contract_version` (new N1 request/axes schema), `raw_axis_schema_version`, `router_version`, and a new event contract (extension to `EligibilityDecision`/`RoutingMode`/reason codes). N3/N4/EV/N6 keep their contracts (they consume the decision), though the events would *reference* N3 levels.

## §6 — Impact
- **Correct:** the N1 producer (`RawAxesBuilder` + `market_structure` axis mapping) and `ve_brain.regime_routing` (`applicable_regimes` + Router). These are the only modules that decide reachability.
- **Unmodified:** N3 (zone map), N4 (confirmation), EV, N6, cost model — they consume the decision; breakout events would *bind to* existing N3 levels, not require rewriting them.
- **Longitudinal stateful detector: REQUIRED** — both a real RANGE (needs `consolidation_state` over time) and a strict breakout transition (needs the prior-regime→break 2‑state test) are inherently multi-bar; a per-bar proxy cannot express them (`HANDOFF_GATES.md` L122).
- **Migration of the 44 breakout hypotheses:** they remain **`NOT_EVALUATED` (REGIME_UNREACHABLE)**, never negative/falsified. On a re-run with the new producer they become evaluable; **`hypothesis_semantic_fingerprint` and the family size `m` must stay unchanged** (the hypotheses are not redefined — only the regime producer changes), so prior results stay `NOT_EVALUATED`, not counted as rejections.
- **Mandatory tests for any future producer:** reachability (RANGE/breakout events actually producible + an updated truth table + the dead-route removed), zero-lookahead, restart determinism, and snapshot fidelity — the same gates already applied to the N1 replay artefacts.

## §7 — Interdictions honored
No engine modified; no new detector written; no PnL evaluated; no `2025‑11+` data accessed; Alpha not run; LIVE_SHADOW not touched; **no enumeration reinterpreted to make a route reachable** — the finding is that `structure=="range"` is *statically* unproducible and must not be faked. Read-only Git + ratified documents only.

**Status: `RT_RANGE_BREAKOUT_REACHABILITY_REPORT_READY`.** For the Statistician, then the Architect/VE, to design and implement the correct versioned contract. Red Team changed nothing outside `red_team/`.
