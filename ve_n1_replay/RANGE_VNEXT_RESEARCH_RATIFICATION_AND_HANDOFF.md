# RANGE vNext — research ratification record and technical handoff

**Producer**: Validation Engine (VE). **Consumers**: Market Intelligence research, Alpha Discovery research
context, controlled offline evaluation, future research-side integration preparation — per the CEO's own
explicit scope grant (§7 below). **Date**: 2026-08-23. **Status**: `RANGE_LIFECYCLE_VNEXT_RESEARCH_RATIFIED`
/ `RANGE_LIFECYCLE_VNEXT_APPROVED_FOR_RESEARCH_USE` / `RANGE_LIFECYCLE_VNEXT_MARKET_INTELLIGENCE_RESEARCH_
BASELINE`. **Authorizing decision**: `CEO-RANGE-VNEXT-RESEARCH-RATIFICATION-001`.

This document has two purposes: (1) preserve the full independent-validation chain that earned this
ratification, in one place, and (2) let you consume RANGE vNext for research purposes **without reopening
its design** — mirroring exactly how `RANGE_V4_4_ALPHA_DISCOVERY_HANDOFF.md` served V4.4 at its own
ratification. If a question you have isn't answered here, that's a signal to ask VE/CEO before inventing an
interpretation — don't guess at semantics this document doesn't cover.

---

## 1 — The full independent-validation chain (preserved, not summarized away)

| Step | Commit | Branch | Verdict |
|---|---|---|---|
| VE: bounded multi-candidate architecture delivered | `bba6310` | `discovery-mk-matrix-v1` | `RANGE_LIFECYCLE_VNEXT_CANDIDATE_READY_FOR_INDEPENDENT_VALIDATION` |
| Statistician: original independent validation | `54fa51f` | `statistician-foundation` | `RANGE_LIFECYCLE_VNEXT_INDEPENDENT_VALIDATION_FAIL` / `UNBOUNDED_STATE_BLOCKER` (found the real CONTINUATION-past-cap defect: cap=3, active reached 34, zero refusals) |
| VE: hard-cap remediation | `fa36324` | `discovery-mk-matrix-v1` | `RANGE_LIFECYCLE_VNEXT_HARD_CAP_REMEDIATED` / `READY_FOR_INDEPENDENT_REVALIDATION` |
| Statistician: independent hard-cap revalidation | `90b572e` | `statistician-foundation` | `PASS` / `READY_FOR_RED_TEAM` (own independently-materialized pre-fix control reproduced the original defect first, confirming the harness itself is sound) |
| Red Team: final adversarial validation | `986cba8` | `statistician-foundation` | `RANGE_LIFECYCLE_VNEXT_RED_TEAM_PASS` / `RESEARCH_RATIFICATION_READY` (13/13 material gates pass, own independently-constructed gates, own independent full-history dual-engine replay) |
| CEO: ratification | `CEO-RANGE-VNEXT-RESEARCH-RATIFICATION-001` | — | `RANGE_LIFECYCLE_VNEXT_RESEARCH_RATIFIED` |

Every commit above was independently confirmed to exist and to contain the claimed content before this
document was written — not accepted from a summary alone (`git show`/`git log`/`git merge-base
--is-ancestor` against all 4 mirror remotes; full Red Team report read in full, not secondhand).
`54fa51f`/`90b572e`/`986cba8` live on `statistician-foundation`, not `discovery-mk-matrix-v1` — Statistician
and Red Team validate by materializing the exact candidate code from its own git blob into a separate
environment (`90b572e`'s own words: "materialised the PRE-FIX module from its bba6310 git blob into a
throwaway package copy"), not by merging branches, so their commits are correctly **not** git ancestors of
`fa36324` — this is the established, sound methodology for this project's independent-validation model, not
a provenance gap.

## 2 — Audit nuance, preserved per explicit CEO instruction (do not erase or normalize away)

Red Team's own independent full-history replay (own ATR pipeline, own harness) reproduced every structural
total from VE's own reference **exactly** — births 12,813, merges 361, genuine confirmations 4,092, max
active 4, capacity refusals 0, early confirmations 0 — and confirmed **PRE-FIX == POST-FIX byte-identical
across all 355,696 bars in their own harness too** (zero divergence bars). Two *secondary* aggregates
differed from VE's own numbers, both explained and neither remediation-induced:

- **Price abandonments: 4,152 (Red Team) vs 4,108 (VE reference)**, a +1.0% difference — attributed to
  marginal `atr_ref` sensitivity of the distance-based abandonment trigger between VE's and Red Team's own
  independently-built ATR feeds. Zero effect on any confirmation, birth, merge, or the cap invariant itself.
- **Per-year confirmed-bar tally**: a counting-convention difference (Red Team's harness counts every bar
  the canonical macro carries a `confirm_ts`, including WEAKENING state; VE's counts by `OK_RANGE_MACRO`
  reason) — genuine confirmation *events* match exactly (4,092) in both, so this is definitional, not a
  behavioral difference.

Both differences are **PRE==POST identical within each harness respectively** — i.e., neither harness's own
pre-fix and post-fix runs diverged from each other, which is what actually matters for "did the remediation
change anything." The remediation itself is proven semantically inert by two independent measurements, not
one.

## 3 — Canonical identity

| Field | Value |
|---|---|
| Commit (ratified, do not use any other) | `fa36324` |
| Repo / branch | `ai_quant_lab-wp5b` / `discovery-mk-matrix-v1` |
| `contract_version` | `range-hierarchical-vnext-multicandidate-v1` |
| `config_id` | `3f2f7ba6bef59d689f96424424e3f0378ffe10ff6f64ecd6bd3ec40e53322c22` |
| Implementation fingerprint | `vnext-implementation-hardcap-remediation-2026-08-22` |

Before consuming any output, verify `ConfigVNext().config_id()` equals the value above. If it doesn't
match, stop — you are not looking at the ratified baseline. This fingerprint is intentionally distinct
from the pre-remediation `vnext-implementation-freeze-2026-08-22` (delivered `bba6310`) — a snapshot taken
under the pre-remediation implementation is fail-closed refused by the ratified one; do not attempt to
restore or trust one against the other.

**v4.4 (`3bb61cf`) remains the canonical DEPLOYED baseline.** This ratification does not change that — see
§7.

---

## 4 — Import / API path

**vNext is source-only. It is not in any built `ve_n1_replay` wheel** (the highest wheel actually present in
`release/` is `0.3.1`, from well before any RANGE V4.x/vNext work — confirmed by inspecting the `release/`
directory directly, not assumed). Import directly from the source tree of this exact repo/commit:

```python
from ve_n1_replay.range_semantic_vnext import ConfigVNext, RangeSemanticProducerVNext, RangeSemanticResultVNext
from ve_n1_replay.range_engine_vnext import RangeSemanticEngineVNext
```

**Preferred entry point**: `RangeSemanticEngineVNext` (composes canonical N1 + the vNext producer):

```python
engine = RangeSemanticEngineVNext(
    symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
    implementation_commit=<N1 implementation commit>,
    range_config=ConfigVNext(),
    acknowledge_construction_only=True,   # REQUIRED, not optional friction -- forces a conscious
                                           # acknowledgment this is research-only code, every construction
)
n1_result, range_result, events = engine.observe_closed_bar(bar)
```

Fail-closed on `config_id` mismatch (`ContractErrorV43`) — do not catch and bypass this. Batch replay:
`engine.replay_batch(bars) -> RangeLedgerVNext`. Snapshot/restore: `producer.snapshot_state()` /
`producer.restore_state(snapshot)` — fail-closed on any `contract_version`/`config_id`/
`implementation_fingerprint` mismatch.

---

## 5 — Config identity (full registry, `ConfigVNext`, 22 fields — frozen, do not modify)

```
d_macro=29, d_internal=12, n_touch=2, K_reentry=22, N_accept=3, K_struct=2, n_external_swings=2,
atr_window=14, w_atr=0.8, atr_source=ai_trader.structural_observer.vendor_bridge.atr14,
atr_provenance_wheel_sha256=39673910666e13708b1d4cb7266d1730bb1c9ceea4e0b021a1bf3cfa1f8281f4,
contract_version=range-hierarchical-vnext-multicandidate-v1, ER_max=0.5, RND_max=1.0, ALT_MIN=0.5,
MIN_TRAVERSALS=1, W=29, ER_weakening=0.75, RND_weakening=2.0, WEAKENING_MAX_BARS=22, IOU_CONTINUE=0.5,
GAP_MAX=12, max_active_macro_candidates=16
```

The first 21 fields are byte-identical to V4.4's own frozen registry (nothing about the underlying
formation/confirmation geometry was retuned to build vNext). The one new field,
`max_active_macro_candidates=16`, is a resource cap only — never consulted by merge/continuation/
replacement/abandonment geometry — evidence-derived (4x the measured historical max of 4 concurrent
candidates over the full 15-year canonical history). Use `ConfigVNext()` (all defaults) — do not override
any field; the `config_id` guard exists precisely so a locally-modified config cannot be silently consumed.

---

## 6 — Output schema and what's new relative to V4.4

`RangeSemanticResultVNext` carries every V4.4 field (see `RANGE_V4_4_ALPHA_DISCOVERY_HANDOFF.md` §5 for the
shared fields, unchanged in meaning) **plus three new fields describing the multi-candidate registry**:

```python
active_macro_count: int          # how many MACRO candidates are concurrently tracked this bar (median
                                  # 1, p95 2, p99 2, max 4 over the full canonical history; hard cap 16)
active_macro_ids: tuple[int, ...]  # their structure_ids, ascending
active_internal_count: int       # at most one INTERNAL per active macro, structurally
```

`macro_id`/`macro_state`/`macro_reason`/etc. describe the **canonical** (arbitrated) macro only — the one
selected by deterministic structural rule (§11 of the architecture doc: prefer the CONFIRMED macro whose
zone contains the current close; else nearest by boundary distance; ties by lowest id) when more than one
candidate is CONFIRMED at once. A confirmed RANGE, for research purposes, is still `macro_state ==
"CONFIRMED"` exactly as under V4.4 — the difference is that vNext's own registry may be tracking several
other, non-canonical candidates simultaneously (visible via `active_macro_ids`), which V4.4 structurally
could never do.

---

## 7 — Scope of this ratification (verbatim from the CEO decision — do not expand it)

**Authorized**: research, Market Intelligence research, Alpha research context, controlled offline
evaluation, future research-side integration preparation.

**NOT authorized**: production, New Brain, AI Trader runtime, live shadow, MT5, broker, order submission,
live trading. Do not send RANGE vNext to AI Trader. Do not modify live Market Intelligence authority.
Production integration requires a **separate** CEO mandate after hardening (§9 below) — this document does
not grant it, and reaching this ratification does not silently authorize it.

**Canonical baseline distinction**: for NEW research work, RANGE vNext is now the approved RANGE research
baseline. For DEPLOYED/production runtime, **v4.4 remains the current baseline** until a separate
production-hardening and cutover mandate completes. Do not silently replace deployed v4.4 with vNext
anywhere.

---

## 8 — How research may consume vNext

Permitted, exactly as V4.4's own handoff authorized (§7 of that document, unchanged in spirit): use
`macro_state == "CONFIRMED"` spans (canonical, arbitrated) as a feature/context input into hypothesis
generation, backtesting, or signal construction. Treat vNext exactly as you would any other engineered
feature — an input to be tested, not ground truth.

**What's new to weigh relative to V4.4**: vNext trades V4.4's single-slot 9-year dead zone (2016-2024, zero
CONFIRMED bars, one candidate stuck 9.7 years) for materially higher CONFIRMED coverage throughout that
same window (6,429-7,660 bars/year, 62,713 total) — but carries its own disclosed risk profile (§9). If your
research question is specifically about periods where V4.4 produces zero signal, vNext is very likely the
better-behaved choice; if you need the absolute lowest false-positive rate at any cost, weigh §9's
price-abandonment risk explicitly rather than assuming vNext strictly dominates.

---

## 9 — Known limitations (do not omit when reporting results built on vNext)

Carried forward from the research report (§14, 9 items) and the remediation report, headlined by:

- **Price-abandonment premature-kill rate**: 2.14-6.42% (matcher-parameter-sensitive, disclosed, not
  uniquely identified — Red Team's own independent assessment: "placebo discrimination ~+76-90%,
  materially better than the rejected v4.5 timeout recovery's 36.9%/12.3%"). This is the architecture's
  largest disclosed false-positive risk and the single most valuable target if you observe a case where it
  appears to matter for your specific research question.
- **`Registry._dead` / `_awaiting_role` lifetime-state growth — `REMEDIATION_REQUIRED_BEFORE_PRODUCTION`**
  (Statistician's own classification, confirmed by Red Team as a production-hardening concern, not a
  research-correctness defect). Restart-serialization size grows with total lifetime candidate count
  (~4 bytes/bar, ~1.4MB after 15 years) — practically negligible for a single offline research replay, but
  **do not run vNext as a long-lived, continuously-live process expecting bounded memory/snapshot size** —
  that is exactly the condition this limitation would eventually matter for, and exactly why it blocks
  production, not research.
- The hard-cap remediation's own premature-kill rate is 0/187 (0.0%) — it never fired historically (max
  active 4 ≪ cap 16) — so the remediation itself adds zero additional slow-structure-kill risk beyond what
  was already disclosed for the original architecture.
- Promotion/regime detection remains GLOBAL/single-window, not per-candidate — inherited from V4.3,
  unchanged by any RANGE version to date.
- Evidence is XAUUSD M15 only, from canonical-warmup historical replay. No cross-instrument or
  cross-timeframe generalization claim is made.

---

## 10 — Forbidden interpretations

- Do not present vNext output as `PRODUCTION_READY`, `NEW_BRAIN_READY`, or `LIVE_READY` in any downstream
  report — none of these are true, and none of these strings appear in any verdict issued for vNext. The
  correct status is `RANGE_LIFECYCLE_VNEXT_RESEARCH_RATIFIED` / `MARKET_INTELLIGENCE_RESEARCH_BASELINE`.
- Do not use vNext (or any RANGE output) to submit orders, connect to a broker, or run in `LIVE_SHADOW`.
- Do not promote vNext (or anything derived from it) into the Strategy Catalog, AI Trader, or New Brain
  without a separate, explicit CEO authorization following a production-hardening mandate.
- Do not treat the `_dead`/`_awaiting_role` finding as resolved because research ratification happened —
  it is explicitly carried forward as a mandatory pre-production blocker, not waived by this document.
- Do not retune the price-abandonment mechanism or any matching-methodology parameter to chase a specific
  premature-kill percentage within the disclosed 2.14-6.42% range — that range is a measurement-sensitivity
  disclosure, not an invitation to select the flattering end of it.
- Do not construct `acknowledge_construction_only=True` as a stamp of production-readiness — same rule as
  V4.4, it exists to force conscious acknowledgment this is research-only code.

---

## 11 — Rollback reference

vNext at `fa36324` was independently rollback/regression-tested at every stage of the chain in §1 (VE's own
547→554 full-suite re-runs at each commit; Statistician's and Red Team's own independent 554/554
reproductions). v4.4 (`3bb61cf`) itself is completely untouched by any commit in this entire chain — `git
diff --stat` empty on `range_semantic_v4_3.py`/`range_semantic_v4_4.py`/`range_engine_v4_4.py` across the
full `3bb61cf..fa36324` range, independently verified by VE, Statistician, and Red Team separately. If
anything downstream of this handoff appears to depend on behavior not in this document, the fallback is:
re-clone `ai_quant_lab-wp5b` at `fa36324`, run `ve_n1_replay/tests/test_vnext_liveness.py`, and confirm you
get the same 37/37 baseline described in the delivery reports before concluding vNext itself has changed.
