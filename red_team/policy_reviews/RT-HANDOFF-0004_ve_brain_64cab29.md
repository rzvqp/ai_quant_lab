# RED TEAM — FINAL HANDOFF REVALIDATION · `ve_brain` 0.1.2 @ `64cab29`
### RT-HANDOFF-0004 · the delivered repair + the one decisive attack (registry poisoning), pre-registered verdict rule
**Date:** 2026-08-13 · **Auditor:** Red Team · **Target:** `ve_brain/` 0.1.2 @ `64cab29` (registry-injection self-attack closed; 21 tests, mypy clean). Verdict rule pre-registered (RT-HANDOFF-0003) and, for this specific attack, fixed by the CEO: reproducible false-registration → CONDITIONAL with one remedy; impossible + eight points pass → PASS. **No engine modified; no repair; no real data; no invented defects.** Verified on imported source @`64cab29` + the CEO's exact fixture + VE's 21 tests re-run (21 passed).

# VERDICT — **VE_HANDOFF_CONDITIONAL**
The delivered repair is real: the prior forged-eligibility hole is **closed** — N6 reads `requires_true_range` from the internal registry, independent of the eligibility object (verified: forged `eligible=True` against a correctly-registered RANGE strategy → `NO_TRADE / TRUE_RANGE_NOT_IDENTIFIABLE`). **But the one decisive attack the CEO named is REPRODUCIBLE:** the canonical registry starts empty and is populated through the **public** `register_canonical_strategy`, with no approved catalog and no seal — so a consumer can register `range_fade` **as TREND** before any true policy exists, and N6 then trades it. Per the CEO's pre-registered mapping for this test, reproducible ⇒ **CONDITIONAL** with a **single** remedy: an internal versioned + sealed catalog and no public arbitrary-definition API in production.

## THE DECISIVE ATTACK — reproducible (CEO's exact fixture)
```
register_canonical_strategy(StrategyContract(strategy_id="range_fade", strategy_family="TREND",
    allowed_regimes=(TREND_UP,), validation_status=RATIFIED, strategy_version="v1", ...))
# then: matching candidate (strategy_policy_fingerprint = fp of the poisoned contract), matching eligibility, EV+
decide_n6(candidate, eligibility)
```
- **observed:** `decision = TRADE`, `reason = TRADE_VALIDATED_EDGE`.
- **required:** `NO_TRADE` — this definition is not in an approved catalog.
- **why it works:** N6 resolves `requires_true_range` from the registry (correct design), but the **registry itself is defined by the consumer**. Registering `range_fade` with `allowed_regimes=(TREND_UP,)` makes `requires_true_range(canon) = False`; the candidate mirrors the poisoned policy, so `strategy_policy_fingerprint`, `strategy_family`, and `validation_status` all match (no `STRATEGY_POLICY_MISMATCH`); the range block never fires → TRADE. `test_c16` catches a candidate that lies **against a correct registry**; it does **not** catch poisoning the registry itself (candidate + registry consistent, both forged).
- **file · path:** `ve_brain/n6.py::register_canonical_strategy` (public, populates the module singleton with no approved-catalog / seal check); `ve_brain/regime_routing.py::StrategyRegistry.register` ("first to register wins": blocks only same `(id,version)` with a *different* policy).
- **owner:** VE.

## THE TEN CHECKS (evidence for CONDITIONAL)
| # | check | finding |
|---|---|---|
| 1 | `register_canonical_strategy` exported PUBLIC? | **YES** (`__all__`) |
| 2 | who can call it at runtime? | any consumer (AI Trader) — no guard |
| 3 | registry starts empty? | **YES** (`StrategyRegistry()` empty) |
| 4 | "first to register wins" → catalog poisoning? | **YES** — `register` blocks only same `(id,version)` + *different* policy; first registration accepted unconditionally |
| 5 | reset/clear/replace accessible in production? | **YES** — `reset_canonical_registry` **and** `set_registry_available` are public (`__all__`), documented "tests only" but not isolated |
| 6 | consumer can self-grant PROMOTED/RATIFIED? | **YES** — `validation_status` is caller-set on the registered contract; no legitimacy check |
| 7 | same strategy → different policy after restart? | **YES** — in-memory, empty each process; `reset` wipes it mid-process; the duplicate-guard holds only within one populated session |
| 8 | catalog loading deterministic + fingerprint-verified vs an approved catalog? | **NO** — no approved catalog; the policy fingerprint is recomputed from whatever the consumer registered (internal consistency only) |
| 9 | registry SEALED before event processing? | **NO** — no seal mechanism exists (`seal`/`is_sealed` absent) |
| 10 | N6 refuses when unsealed / catalog version mismatched? | **NO** — N6 checks only `_REGISTRY_AVAILABLE` (a manual fault flag), not a seal or an approved version |

## WHAT IS GENUINELY FIXED (credited)
- **Prior CONDITIONAL (forged eligibility) — CLOSED.** N6 reads `requires_true_range` from the registry and applies the range block **independent of** `reason_codes`/`is_eligible`/EV. Verified: forged `eligible=True` + a correctly-registered RANGE strategy → `NO_TRADE / TRUE_RANGE_NOT_IDENTIFIABLE`. VE also self-found and closed the registry-as-parameter forgery (registry is now an internal singleton, not a `decide_n6` parameter). This is real, disciplined progress.
- The eight prior points remain intact (FAIL-2 independent axes, simultaneity, A5 complete identity, comparability-by-absence, mandatory eligibility with identity checks, `STRATEGY_POLICY_MISMATCH` for a candidate lying against a correct registry).

## THE PRINCIPLE (why this is the one remedy, not a new defect)
A canonical strategy must not be **defined** by the AI-Trader runtime. The authoritative `strategy_family` / `allowed_regimes` / `requires_true_range` / `validation_status` / `strategy_policy_fingerprint` must come from a **controlled, versioned catalog inside the VE artifact** (or a controlled loader that verifies an approved definition against it). The consumer may **request** loading an approved strategy; it may not author the policy. Test-only injection/reset is fine **if** clearly isolated from the production API and impossible to reach accidentally from AI Trader — today `register_canonical_strategy`/`reset_canonical_registry`/`set_registry_available` are all in the production `__all__`.

## VERDICT — **VE_HANDOFF_CONDITIONAL** · one remedy
The false-registration attack is **reproducible and material** (a range strategy trades by self-registering as trend). Per the CEO's pre-registered rule for this test, that is **CONDITIONAL**, not PASS. **Single required remedy:** ship an **internal, versioned, sealed** canonical catalog (approved definitions baked into / loaded-and-verified by the artifact), **seal it before event processing**, have N6 refuse on an unsealed or version-mismatched catalog, and remove the arbitrary-definition/reset/availability APIs from the production surface (move them to a clearly-isolated test-only entrypoint). **I am not adding any further defect** — this closes the test. **Mandate 2 remains NOT authorized** until the remedy lands; on the next PASS it distributes automatically.

## HANDOFF → CEO / VE
1. **The one remedy:** internal versioned+sealed catalog; `register_canonical_strategy` either removed from production or restricted to loading an **approved** definition (verified against the baked catalog fingerprint); `reset`/`set_registry_available` moved to an isolated test-only module; N6 emits a fail-closed reason on unsealed/unapproved registry.
2. Re-submit; I re-run the exact poisoning fixture + the eight points + the complete path. If the attack is impossible and all pass → **PASS** (Mandate 2 auto-distributes).

Red Team designed no remedy beyond naming the single pre-registered fix, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
