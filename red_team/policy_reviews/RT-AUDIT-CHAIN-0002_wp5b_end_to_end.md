# RED TEAM — END-TO-END CHAIN AUDIT · wp5b level tower + bus
### RT-AUDIT-CHAIN-0002 · N1→N2→N3→opportunity_id→N4→PolicyMatcher→N6 + bus (MarketState, PolicyMatcher, Provenance)
**Date:** 2026-08-09 · **Auditor:** Red Team · **Repo:** `ai_quant_lab-wp5b`, branch `discovery-mk-matrix-v1`, DoD @ `d782401`. Components: `c40d3386` (level_output+opportunity_id), `5888978` (N3 re-anchored), `7f2694f` (N4 W=3), `850815f` (N2 directional), `62c447e` (N1 contract), `d782401` (bus+integration). Seven targets: lookahead, leakage, opportunity identity, cross-timeframe alignment, decision clock, TRADE/NO-TRADE integrity, audit trail. **No real-data run; verified on synthetic + source; nothing modified; no remedy.**

## VERDICT — **PASS_WITH_LIMITATIONS.**
The integration **genuinely closes my three prior silent-consumption findings** (L-U2/Z4-L1/ZM-U1) via the `LevelOutput` type; the fail-closed cascade, audit trail, and opportunity identity are sound. One limitation is **material before Shadow**: the bus's `decide()`/recognizers **key on N4's confirmation**, so the bus decision depends on evidence available only at `hit+W+1` — contradicting the CEO-fixed `decision_clock=zone_hit` and the opportunity_id module's own discipline. It is **dormant** now (no policy has validated edge → always NO_TRADE) but **activates at Shadow.**

---

## TARGET — TRADE/NO-TRADE INTEGRITY + the silent-consumption closure: **VERIFIED CLOSED.**
The `LevelOutput = Ok[T] | Unavailable` contract closes L-U2/Z4-L1/ZM-U1:
- **`Unavailable` has NO `.value`** (verified) — a consumer physically cannot read the payload without narrowing `Ok` vs `Unavailable` first; `mypy --strict` enforces it; a third constructor triggers `assert_never`. The "0/UNDETERMINED silently consumed as neutral" failure mode is **structurally impossible** for the availability axis.
- **Cascade fail-closed with reason:** `decide()` checks `isinstance(state.regime, Unavailable)` → **NO_TRADE, reason = `regime_unavailable:<reason>` propagated** (verified). N1 Unavailable cascades to N2 (`regime_axes_status`), N3 (`regime_available=False`), N4 (skipped) — all by `isinstance` narrowing.
- **The classified-UNDETERMINED** (Ok payload, ordinal 0) is handled **by enum-member check** in the recognizers (`conf is ZoneConfirmation.UNDETERMINED → WAITING`), not consumed as neutral arithmetic. ✅
This is a real achievement — the contract is the correct structural fix for the recurring silent-consumption pattern.

## TARGET — DECISION CLOCK: **the sharpest finding. The bus decision depends on N4 (`hit+W+1`), violating `decision_clock=zone_hit`.**
The `opportunity_id.py` module **correctly** implements the CEO's discipline: two immutable records — `DecisionRecord(decided_at=i0=zone_hit, inputs over N1/N2/N3)` and `EvidenceRecord(attached_at=i0+W+1, N4)` — **linked only by `opportunity_id`, so N4 cannot modify the decision (point 6, enforced by TYPE).** The decision clock (zone_hit) is thus independent of the observed evidence (N4). **But the bus `decide()` does NOT use this machinery:** it builds its own `market_bus.DecisionRecord` from `PolicyMatcher` matches, and the recognizers **read N4** (`_first_confirmation → state.confirmations`, verified). So the bus decision **depends on N4**, which is only observable at `hit+W+1` → the effective decision clock is `hit+W+1`, **the entry moved**, exactly the Statistician's forbidden "clock depends on observed evidence."
- **Dormant vs active:** in the DoD the MATCH came from N4 but the outcome (NO_TRADE) came from `edge=False`, so N4 did not move a real entry. **The violation is latent — it activates the moment any policy has `has_validated_edge=True`** (MATCH-via-N4 → TRADE at `hit+W+1`). **Before Shadow, the recognizers must key on N1/N2/N3 at zone_hit, with N4 as evidence-only, per the opportunity_id contract.** (E2E-L1.)

## TARGET — CROSS-TIMEFRAME ALIGNMENT: **as-of correct + auditable; `valid_until` carried but UNENFORCED.**
Each level runs on its own timeframe's array and its provenance records that timeframe's **last-closed-bar timestamp** (`t4[-1]/t1[-1]/t15[-1]/t5[-1]`); the decision `as_of` is the last M5 bar. So a regime from the 12:00 H4 bar used at a 15:55 M5 decision is **correct** (that is the last *closed* H4) and **auditable** (the 4h age is visible in provenance). **But:** `Ok` carries `valid_until` ("carry-forward = type error"), and the bus **does not enforce it** — no check that each level's `valid_until ≥ decision as_of`; it **trusts the caller** to cut each timeframe's bars to `≤ as_of`. A genuinely-stale level (caller error) would be silently used. The contract expresses the guard; the bus doesn't execute it. (E2E-L2.)

## TARGET — OPPORTUNITY IDENTITY: **sound — survives band-exit, re-arm handled, D7, geometry-anchored.**
- Identity keyed on **frozen geometry** (`anchor=close[i0-1]`, `band=1×ATR[i0-1]`), never the bar index (`zone@{bar}` named ~5.23 ids per real zone).
- **Two clocks:** economic (`band_exit`) is only *marked* (`band_exit_at=j`), the opportunity is **not closed** — the **identity clock (`i0+W+1`) always closes it**, so the identity **survives band-exit** and N4 always has something to attach to (only ~4.77% survive to `i0+W+1`).
- **Re-arm:** an emission inside a live opportunity's band **refreshes** (same id, D7 — no re-decide); re-arms beyond W are **new opportunities, counted** (`re_arm_beyond_w`), not suppressed, no cooldown constant. ✅
- Band is **frozen** (a live band chases price → unbounded duration → fail-dead) — correct and conservative.

## TARGET — AUDIT TRAIL: **complete, traces to the detector.**
`Provenance(who, timeframe, as_of, detector, version)` per contribution; the full chain lands in `DecisionRecord.provenance = state.provenance + match provenances`. Each entry names **who** (N1_regime…), **timeframe** (H4…M5), **as_of** (the closed-bar timestamp it was available at), **detector** (`regime_classifier.classify_regime`…), **version** (schema_hash, or `"unavailable"` for an Unavailable level). One can trace any contribution back to its detector + schema + timeframe + timestamp. ✅

## TARGET — LOOKAHEAD / LEAKAGE: **causal (each level ≤ its last closed bar; opportunity_id reads j-1).**
All levels read `≤` their timeframe's last closed bar (verified per-level in RT-CODE-A-0008…0015); `OpportunityTracker.step` reads `close[j-1]/atr[j-1]`; N4's ATR reference is the **current M15 ATR** (`m15_atr[-1]`, ≤ as_of) broadcast to M5 — a causal cross-timeframe value, not lookahead. The chain is causal **provided the caller cuts each timeframe to ≤ as_of** (the bus trusts this, ties to E2E-L2).

## TARGET 6 — VE's two discrepancies: **faithful with named gaps.**
- **Generalized S1/S16 (pdh_pdl_demo/multi_policy_live don't exist):** the recognizers map the setup semantics onto the N4 ordinal (S1 sweep-absorbed → `ABSORPTION_PROXY_BEARISH`; S16 breakout → `ACCEPTANCE_BULLISH`) — **faithful as recognizers**, but they are **confirmation-ordinal proxies**, not the full S1/S16 entry/stop/target logic. **`S2` (reclaim) is named in the docstring but ABSENT** from `default_policies` (only 2 of 3 wired — verified). (E2E-U1.)
- **Minimal edge gate vs the full EV engine (bdd15e5):** `decide()` gates on the boolean `has_validated_edge` instead of per-decision `EV_LCB>0`. Since the whole library is `has_validated_edge=False` (exploratory), the chain **always** says NO_TRADE. This is **strictly conservative** — it cannot produce a TRADE the full EV would reject — so it does not change the decision semantics in an unsafe direction; but it is **not the real N6** (a boolean edge-existence proxy), and the full EV must replace it before real trading. Acceptable for a DoD whose goal is an **auditable NO_TRADE**, not a TRADE.

## SEVERITY
- 🟠 **E2E-L1 · Decision clock violated by the bus recognizers** — they key on N4 (`hit+W+1`), contradicting `decision_clock=zone_hit` and the opportunity_id discipline; dormant now (always NO_TRADE), activates at Shadow. **Fix before Shadow.**
- 🟠 **E2E-L2 · `valid_until` carried but unenforced** — the bus trusts the caller to cut bars; a stale level would be silently used; the "carry-forward = type error" guard is not executed at the bus.
- 🟡 **E2E-U1 · Generalization gaps** — S2 (reclaim) named but not wired; recognizers are ordinal proxies not full evaluators; the minimal edge gate is a conservative proxy for the full EV.

## WHAT SURVIVES (verified)
The `LevelOutput` contract **closes L-U2/Z4-L1/ZM-U1** (Unavailable has no value; consumers narrow; UNDETERMINED handled by enum member); fail-closed cascade → NO_TRADE with reason propagated; complete audit trail traceable to the detector; opportunity identity survives band-exit + handles re-arm + D7 + geometry anchor; as-of alignment correct and auditable; causal chain; the minimal edge gate is conservative (can't false-trade). **The DoD's auditable NO_TRADE is correct and honestly built.**

## VERDICT — **PASS_WITH_LIMITATIONS.** The tower-under-one-contract is a real structural achievement — the recurring silent-consumption pattern is closed by type, and the cascade/identity/audit are sound. The blocking item for **Shadow** is E2E-L1: the bus decision must be moved off N4 back to the zone_hit clock (the opportunity_id module already defines how), and E2E-L2 (enforce `valid_until`) should be closed with it. E2E-U1 is disclosure (wire S2, replace the minimal gate with the full EV before trading).

## HANDOFF → CEO / Statistician (before Shadow)
1. **E2E-L1 (blocking):** re-point the bus recognizers / `decide()` to the opportunity_id decision-clock records — decision on N1/N2/N3 at zone_hit, N4 as evidence-only; verify the entry does not move to `hit+W+1`.
2. **E2E-L2:** enforce `valid_until ≥ as_of` per level at the bus (don't rely on the caller's cut).
3. **E2E-U1:** wire S2 (reclaim); replace the boolean edge gate with the full EV engine (bdd15e5) before any TRADE.
4. The contract closure, cascade, identity, and audit trail are **verified clean** — the DoD holds.

Red Team designed no remedy, ran no data on the market, modified nothing outside `red_team/`.
