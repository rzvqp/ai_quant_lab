# RED TEAM — HANDOFF REVALIDATION · `ve_brain` 0.1.3 @ `fbc0f20` · **VE_HANDOFF_PASS**
### RT-HANDOFF-0005 · sealed catalog · poisoning fixture · ten checks · seal · testing isolation · eight points · complete path · 12 deliverables
**Date:** 2026-08-13 · **Auditor:** Red Team · **Target:** `ve_brain/` 0.1.3 @ `fbc0f20` (internal sealed canonical catalog; 26 tests, mypy clean). **Verdict rule (unchanged, pre-registered):** reproducible decision-path bypass → FAIL; documentary limitation without path impact → CONDITIONAL; all pass, no reproducible bypass → PASS; no invented defects; if no reproducible violation → PASS. **No engine modified; no repair; no real data.** Verified on imported source @`fbc0f20` + the CEO's exact fixture + VE's 26 tests re-run (26 passed).

# VERDICT — **VE_HANDOFF_PASS**
The registry-poisoning attack the CEO named is **impossible via the production surface**, and all pre-registered criteria pass with the complete path demonstrated. I hunted the sixth instance of the bypassable-guard pattern and found **no reproducible decision-path bypass** reachable through the artifact's contract. Per the fixed rule, this is PASS. **Mandate 2 distributes automatically to AI Trader — no further CEO approval.**

## 1 · THE EXACT POISONING FIXTURE — now IMPOSSIBLE
- **`register_canonical_strategy` / `reset_canonical_registry` / `set_registry_available` are removed from the production surface** (absent on `ve_brain`, not in `__all__`; present only in docs/CHANGELOG and a test-only module). The fixture cannot even be constructed on the public API.
- **`range_fade` is baked in the catalog with its TRUE definition** (`allowed=(RANGE,)`, `RANGE_MEAN_REVERSION`, RATIFIED) precisely so N6 blocks it. Every consumer attempt verified → NO_TRADE:
  - forged as TREND (family/status/fp mismatched) → **STRATEGY_POLICY_MISMATCH**;
  - matching the true canon → **TRUE_RANGE_NOT_IDENTIFIABLE**;
  - fabricated id not in catalog → **UNKNOWN_STRATEGY**;
  - legitimate `trend_pullback` → **TRADE** (control).
- **No production path defines the policy.** The catalog is embedded Python literals (no file/env/network — grep-verified), sealed at import, version + integrity-hash checked. The consumer can reference an approved strategy; it cannot author `strategy_family`/`allowed_regimes`/`requires_true_range`/`validation_status`/`strategy_policy_fingerprint`.

## 2 · THE TEN CHECKS — re-run
| # | check | finding |
|---|---|---|
| 1 | `register_canonical_strategy` public? | **NO** (removed from `ve_brain`) |
| 2 | who can call it at runtime? | no one — it does not exist on the artifact |
| 3 | registry starts empty / consumer-populable? | **NO** — catalog embedded + sealed at import; not populable |
| 4 | "first to register wins" → poisoning? | **NO** — no register API; catalog pre-sealed |
| 5 | reset/clear/replace accessible in production? | **NO** — `reset`/`set_registry_available` removed from production; isolated in `ve_brain.testing`, gated |
| 6 | consumer self-grants PROMOTED/RATIFIED? | **NO** — status resolved from the baked catalog canon, not the candidate; `trend_shadow` (SHADOW_ELIGIBLE) → SHADOW_TRADE_CANDIDATE, `trend_experimental` (EXPERIMENTAL) → NO_ELIGIBLE_STRATEGY (verified) |
| 7 | same strategy → different policy after restart? | **NO** — catalog is immutable literals; identical every process; no runtime mutation on the production surface |
| 8 | catalog loading deterministic + integrity-verified? | **YES** — embedded literals; `content_hash`/version checked against embedded approved constants |
| 9 | registry SEALED before event processing? | **YES** — `SealedRegistry.build()` seals at import; `_SEALED_CATALOG.sealed` |
| 10 | N6 refuses unsealed / version-mismatched? | **YES** — `CATALOG_NOT_SEALED` / `CATALOG_VERSION_MISMATCH` (verified they FIRE, below) |

## 3 · THE SEAL — real guards, on the one decision path
`decide_n6` is the single decision path; step 2 checks `sealed` + `catalog_version` + `content_hash` against the embedded approved constants **before** any resolve/EV/TRADE. Verified the guards are not decorative (via the gated test hooks): an **unsealed** catalog → `CATALOG_NOT_SEALED`; a **version mismatch** → `CATALOG_VERSION_MISMATCH`; restore → legitimate trend trades. There is **no public setter** to unseal or swap the catalog (public names are read-only constants/classes; `SealedRegistry.unsealed` is called only from `ve_brain.testing`). Breaking the seal at runtime requires monkeypatching two private module globals — outside the contract (any library is monkeypatchable; a consumer with that access self-sabotages, it is not an API bypass — a stance previously credited by the CEO).

## 4 · `ve_brain.testing` ISOLATION + the token (documentary, non-material)
- **Not imported by any production module** (grep-verified: the only mentions are a comment in `n6.py` and the module's own error strings). Not in top-level `__all__`. Reachable only by an explicit `import ve_brain.testing`.
- **Gated:** every hook raises until `unlock_for_tests(TOKEN)`; an accidental import moves nothing (verified: `install_unsealed_catalog` without unlock → RuntimeError).
- **The token IS a plaintext source constant** (`"VE-BRAIN-TEST-ONLY"`) — guessable/extractable, as the CEO asked. **This is a documentary hardening note, not a decision-path bypass:** the module is off the production surface, and a consumer who deliberately imports it and unlocks could equally monkeypatch `n6._SEALED_CATALOG` directly — the token is not a security boundary against in-process code and adds no barrier a deliberate attacker lacks. It has **no impact on the production decision path**, so under the verdict rule it does not lower the verdict. **Optional hardening (not required for PASS):** a per-install random token or making the hooks importable only under a test conftest would add defense-in-depth. I am not inflating this into a defect.

## 5 · THE EIGHT POINTS + COMPLETE PATH (break attempts explicit)
- (1) router not bypassable / (2) a RANGE strategy cannot TRADE / (3) N6 requires a valid EligibilityDecision — all hold, now backed by the sealed catalog (range blocked on every surface path; `None` eligibility → MISSING_OR_INVALID_ELIGIBILITY). (4) axes independent + (5) simultaneity — `{COMPRESSION, BREAKOUT_TRANSITION}` both present. (6) A5 complete data identity (block_end included). (7) comparability by absence (no internal comparison; `compare_decisions` raises). (8) 12 deliverables present. The complete path N1 `RawAxes` → `StrategyRouter` → `EligibilityDecision` → EV → N6-revalidates-against-sealed-catalog runs and blocks/permits correctly; each break attempt (forged eligibility, forged policy, fabricated id, unsealed/mismatched catalog, status escalation) returns a specific fail-closed reason.

## 6 · THE 12 DELIVERABLES — present + consistent
Versioned installable (`pyproject.toml` 0.1.3) · exact source commit (`version.py SOURCE_COMMIT`) · public contracts (`CONTRACTS.md`) · input/output schemas (`contracts.py` validate_request/response) · EV adapter (`ev_engine.py`/`_ev_core.py`) · unit+contract tests (26) · canonical fixtures with known results (`test_fixtures_canonical.py`) · dependency list (`DEPENDENCIES.md`) · install/upgrade/rollback (`INSTALL.md`) · proof EV drops old levels + deterministic NO_TRADE without a validated strategy (`RANGE_STRATEGY_ROUTING=DISABLED`, `BROKER_ORDER_SUBMISSION=DISABLED`, UNKNOWN_STRATEGY/NO_ELIGIBLE_STRATEGY) · changelog + compatibility (`CHANGELOG.md` + `assert_compatible`).

## VERDICT — **VE_HANDOFF_PASS**
No reproducible decision-path bypass exists via the artifact's contract; the false-registration attack is impossible; all eight points, the complete path, the seal, the testing isolation, and the 12 deliverables pass. I did not invent defects and did not inflate the one documentary observation (the plaintext test token, off the production surface) into a blocker. **Mandate 2 distributes automatically to AI Trader.** A2 and the canonical measurement contract remain an **independent** track (my extended suite + zero unexplained divergences + CEO approval) — this PASS is the handoff gate, not that ratification.

## HANDOFF → CEO / VE / AI Trader
1. **VE_HANDOFF_PASS** — Mandate 2 auto-distributes.
2. Optional (non-blocking) hardening: replace the plaintext test-unlock token with a per-install random value or a conftest-only gate.
3. The canonical-measurement-contract ratification (A2 / the 18-test suite) is separate and continues on its own track.

Red Team designed no remedy beyond one optional non-blocking note, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
