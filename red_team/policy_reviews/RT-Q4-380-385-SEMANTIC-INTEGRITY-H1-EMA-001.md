# RED TEAM — Q4 BARS 380–385 SEMANTIC INTEGRITY AUDIT · H1 EMA50 / P007 CONTINUITY
### RT-Q4-380-385-SEMANTIC-INTEGRITY-H1-EMA-001 · Auditor: Red Team · 2026-08-30

Audit of whether already-committed Q4 bars 380–385 remain scientifically valid, adjudicating AI
Trader's two disputed semantic claims (bar-379 provenance; the M15-vs-causal-H1 EMA50 reference).
Read-only forensics + independent causal-H1-EMA50 reconstruction. Bar 386 not accessed / not
materialized; Q4 not resumed; engine and strategy definitions not modified.

---

## 0 — VERDICT

The error is **documentation-only**. Under the correct causal H1 EMA50 semantic, **every** committed
decision for bars 380–385 is unchanged, and Q4-P007-003 remains OPEN throughout.

```
Q4_380_385_INTEGRITY_AUDIT_COMPLETE = YES
BAR_379_PROVENANCE_CORRECTED        = YES
CAUSAL_H1_EMA50_RECONSTRUCTED       = YES

BAR_379_PROVENANCE = apprenticeship replay (CEO-authorized single-bar validation pass, 2026-08-30);
                     NOT Red Team
BAR_379_APPRENTICESHIP_DECISION_EXISTS = YES  (ROUTINE_NO_EVENT / NO_TRADE)
RED_TEAM_CONSUMED_REAL_BAR_379         = NO

BARS_380_385_DECISIONS_IDENTICAL_UNDER_CORRECT_H1_EMA = YES
P007_STATUS_IDENTICAL = YES
ANY_TRADE_DECISION_AFFECTED     = NO
ANY_MGMT004_DECISION_AFFECTED   = NO
ANY_NO_TRADE_DECISION_AFFECTED  = NO

SOURCE_USED_380_385 = OANDA_XAUUSD_M15.csv (vendor/alpha_automation_demo_gate/data/market/ copy)
SOURCE_SHA256       = 57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37
MATCHES_ACCEPTED_CANONICAL_SOURCE = YES        SOURCE_LINEAGE_VALID = YES

REAL STATE FREEZE: LAST_COMMITTED_BAR = 385  NEXT_UNSEEN_BAR = 386  BAR_386_ACCESSED = NO

ERROR CLASSIFICATION = SEMANTIC_DOCUMENTATION_ERROR_ONLY  (append-only correction prescribed)
BLOCKING_FINDINGS    = NONE
NONBLOCKING_FINDINGS = 3 (log internal contradiction; out-of-order log blocks; sub-bar miscount)

BARS_380_385_SCIENTIFICALLY_VALID = YES
SAFE_TO_CONTINUE_FROM_BAR_386     = YES (subject to the standing E106 wiring note + CEO authorization)
RED_TEAM_VERDICT                  = PASS_WITH_NONBLOCKING_NOTES
NEXT_AUTHORIZED_ACTION            = NONE — CEO DECISION REQUIRED
```

## 1 — BAR-379 PROVENANCE (§2)

Reconstructed from durable Git/log/review evidence:

- **Who first semantically exposed bar 379:** the **apprenticeship replay**. Bar 379 (Q4_SEALED_1_379.csv,
  `651b944f…`, close 1880.496) was materialized in VE's incremental-unlock checkpoint `a87f42d` (Red Team
  E104) from the canonical source, and its market decision was frozen by AI Trader in a *CEO-authorized
  single-bar validation pass* via the real `engine.step()`/`commit_decision()` handshake (log's own
  validation-pass + reconciliation blocks). The durable state's `last_committed=379` reflects that commit.
- **Was an apprenticeship decision frozen for bar 379:** **YES** — `ROUTINE_NO_EVENT` / NO_TRADE (price
  below causal H1 EMA50, no H1 candle closed on 379, outside NY session, Q4-P007-003 open). Independently
  consistent with my H1 reconstruction (§3): bar 379 close 1880.496 is ~21pt below H1 EMA50 1901.160.
- **Did Red Team E105/E106 consume real bar 379 as new market evidence:** **NO.** E105 audited the one-bar
  remediation on synthetic data; E106 (`6a8861d`) audited the extend→bind→step identity handoff using
  **synthetic bars 1–12 only**, and left the real durable state **byte-unchanged** (E106 recorded it
  `40397a74…`, symbol still `UNKNOWN`, next=380). Red Team tested the *mechanism*, never read bar 379's
  price action.

**Correction to claim A:** AI Trader's earlier log framing — "BAR 379 … consumed via Red Team E2E
validation, not genuine prospective reasoning" — is **inaccurate**. It conflates Red Team's synthetic E2E
mechanism test with the apprenticeship's own commit of bar 379. The log already contains an append-only
reconciliation that re-reasons bar 379 as an apprenticeship `ROUTINE_NO_EVENT`; the erroneous earlier
header remains physically in the file (see NONBLOCKING-1). `BAR_379_PROVENANCE_CORRECTED = YES`. History
not rewritten.

## 2 — CAUSAL H1 EMA50 RECONSTRUCTION (§3)

Independently reconstructed from the sealed 385 fixture ONLY (never bar 386): M15→H1 aggregation
(H1 close = last M15 close in the hour), standard EMA (SMA-50 seed, α=2/51), **only fully-closed H1
candles update the EMA**, gap-aware bar-index→timestamp mapping (Q4 gaps at bars 85/177/269/361 make the
mapping non-linear — corrected).

**Calibration (method validation):** my reconstruction reproduces the established Red Team checkpoint
**exactly** — causal H1 EMA50 @ bar 378 = **1901.160**, below-EMA streak @ 378 = **39** (and 40 @ 379,
matching the log). Only then are the 380–385 outputs trusted.

| BAR | TIMESTAMP (UTC) | CLOSE | CAUSAL_H1_EMA50 | PRICE vs H1_EMA50 | H1_CANDLE_CLOSED_THIS_BAR |
|----:|---------------:|------:|----------------:|:-----------------:|:-------------------------:|
| 380 | 1602038700 (02:45) | 1881.263 | 1900.380 | **BELOW** (−19.1) | YES (02:00–03:00 closes) |
| 381 | 1602039600 (03:00) | 1882.261 | 1900.380 | **BELOW** (−18.1) | NO |
| 382 | 1602040500 (03:15) | 1881.900 | 1900.380 | **BELOW** (−18.5) | NO |
| 383 | 1602041400 (03:30) | 1882.538 | 1900.380 | **BELOW** (−17.8) | NO |
| 384 | 1602042300 (03:45) | 1883.020 | 1899.699 | **BELOW** (−16.7) | YES (03:00–04:00 closes) |
| 385 | 1602043200 (04:00) | 1882.958 | 1899.699 | **BELOW** (−16.7) | NO |

The causal H1 EMA50 steps only on bars 380 and 384 (the two bars on which an H1 candle fully closes):
1901.160 → 1900.380 → 1899.699, drifting *down* as price sits below it — never toward a reclaim. Max close
in the window (1883.020) is **~17pt under** the min H1 EMA50 (1899.699).

## 3 — P007 DECISION REPLAY, CORRECT H1 SEMANTIC (§4, §5)

Q4-P007-003 resolves only on a close back **above** the causal H1 EMA50 (a binary reclaim test; no gate
reads a streak count). No bar 380–385 closes above it — **no reclaim** — so P007-003 **remains OPEN** at
every bar, exactly as committed.

| BAR | ORIGINAL_DECISION | CORRECT_H1_SEMANTIC_DECISION | MATCH |
|----:|:------------------|:-----------------------------|:-----:|
| 380 | NO_TRADE (ROUTINE_NO_EVENT) | NO_TRADE — below H1 EMA50, no reclaim, P007 open | YES |
| 381 | NO_TRADE | NO_TRADE — below H1 EMA50, P007 open | YES |
| 382 | NO_TRADE | NO_TRADE — below H1 EMA50, P007 open | YES |
| 383 | NO_TRADE | NO_TRADE — below H1 EMA50, P007 open | YES |
| 384 | NO_TRADE | NO_TRADE — below H1 EMA50, P007 open | YES |
| 385 | NO_TRADE | NO_TRADE — below H1 EMA50, P007 open | YES |

**Why the EMA-reference confusion (claim B) was harmless to the decisions.** I also independently computed
the M15 EMA50 (reproducing the shipped `ema.py` figure: @378 = 1890.390, the "streak 44" reference). Price
is **BELOW the EMA under BOTH references at every bar 378–385** (M15 EMA ≈ 1888–1890; H1 EMA ≈ 1899–1901).
The two references disagree only on the *streak length* (M15 44→51 vs causal-H1 39→46), a descriptive
diagnostic no decision gate reads. Since both agree on sign, no reclaim occurs under either, and every
decision is NO_TRADE under either — so the choice of reference could not have flipped any decision.
`BARS_380_385_DECISIONS_IDENTICAL_UNDER_CORRECT_H1_EMA = YES · P007_STATUS_IDENTICAL = YES ·
ANY_TRADE/MGMT004/NO_TRADE_DECISION_AFFECTED = NO` (POSITION FLAT, 0 trades, 0 MGMT-004 triggers under
both semantics). **Classification: SEMANTIC_DOCUMENTATION_ERROR_ONLY.**

## 4 — SOURCE LINEAGE (§6)

`SOURCE_USED_380_385 = OANDA_XAUUSD_M15.csv` (the `vendor/alpha_automation_demo_gate/data/market/` copy —
the log discloses this repo's `data/market/` copy did NOT match the origin hash and the vendor copy does).
`SOURCE_SHA256 (origin_source_content_hash) = 57f4ed95…`, identical in the 379 and 385 manifests and equal
to the origin the accepted 379 fixture cited (E104). Independently verified without touching bar 386:
every fixture 379→385's file SHA matches its own manifest; each fixture N−1 is an **exact byte-prefix +1
row** of fixture N; and fixture 379 is byte-identical to the E106-accepted `651b944f…` baseline. So 380–385
is a clean one-bar-at-a-time extension chain rooted in the canonical accepted source — no splice, no
divergence. The four Q4 gaps (bars 85/177/269/361) are identical across manifests and match
`REPLAY_DATA_GAP_LEDGER.md`. `MATCHES_ACCEPTED_CANONICAL_SOURCE = YES · SOURCE_LINEAGE_VALID = YES.`

## 5 — REAL STATE FREEZE (§7)

Durable state: `last_committed_bar = 1602043200` (bar 385), `next_bar = 386`, `sealed_through = 385`,
`pending_decision = null`, `open_event_state_reference = Q4-P007-003:OPEN`, `symbol = OANDA:XAUUSD` (healed
from the E106 `UNKNOWN` via the first legitimate bind — the E106 migration prediction, confirmed in
practice). No fixture ≥ 386 exists on disk; the 385 fixture contains no row with ts ≥ 1602044100. This
audit was strictly read-only (reconstruction read only the sealed 385 fixture). `BAR_386_ACCESSED = NO` ·
no further real bars consumed.

## 6 — FINDINGS

**BLOCKING: NONE.** Bars 380–385 are scientifically valid: correct source lineage, correct causal H1 EMA50
(reconstructed to the exact established checkpoint), and every committed decision matches the correct-H1
replay with P007-003 correctly held OPEN.

**NONBLOCKING (3) — all documentation, prescribing an append-only correction (never a silent rewrite):**
1. **Log internal contradiction on both disputed claims.** The file contains, append-only, BOTH the
   erroneous early statements — bar-379 header "consumed via Red Team E2E validation, not genuine
   prospective reasoning", and the migration note "the mandate's instruction to use CAUSAL H1 EMA50 …
   cannot currently be satisfied … only an M15-close-based causal EMA-50 exists" — AND their later
   corrections (the reconciliation block re-reasons bar 379 as an apprenticeship `ROUTINE_NO_EVENT`, and
   reconstructs the causal H1 EMA50 = 1901.160). The corrections are right; the stale statements remain
   physically present and contradict them. **Prescription (append-only):** stamp an explicit correction
   that (a) bar 379's provenance is the apprenticeship's own validation-pass decision, not Red Team
   consumption; (b) the causal H1 EMA50 IS reconstructable (method reproduces 1901.160 @ 378) and is the
   P007 reference, with the M15 `ema.py` streak explicitly demoted to a sign-only descriptive diagnostic.
2. **Out-of-order log blocks.** The bars-380–385 block physically precedes the bar-379 validation-pass /
   reconciliation block, i.e., chronologically inverted (the 379 SESSION STOP predates reasoning 380–385).
   Clarity only; no bearing on validity.
3. **Sub-bar miscount (log line 662).** Bar 379 is described as "2nd of 4 M15 sub-bars" of the 02:00–03:00
   H1 candle; it is the **3rd** (02:00, 02:15=b378, 02:30=b379, 02:45=b380). The conclusion is unaffected —
   the H1 candle closes on bar 380 and the H1 EMA50 is correctly unchanged at bar 379. Cosmetic.

(The streak-length disagreement M15 44–51 vs H1 39–46 is *not* a finding — it is descriptive-only, no gate
reads it, and the log discloses it correctly.)

## 7 — CONCLUSION

AI Trader's two disputed claims were both initially mis-stated and both already walked back append-only in
the same log; this audit confirms the corrected position independently. Bar 379 was reasoned and committed
by the apprenticeship (a `ROUTINE_NO_EVENT`), never consumed by Red Team. The causal H1 EMA50 is fully
reconstructable — my independent reconstruction reproduces the established checkpoint exactly (1901.160 @
378, streak 39) — and under it price sits ~17–19pt below the H1 EMA50 for all of bars 380–385, so
Q4-P007-003 correctly remains OPEN and every committed NO_TRADE decision is unchanged. Because price is
below the EMA under BOTH the correct H1 and the mistaken M15 reference, the reference confusion changed no
decision. The error is **documentation-only**; the remedy is an append-only correction, not a scientific
repair. Source lineage is clean and canonical. Bars 380–385 are scientifically valid, and it is safe to
continue from bar 386 — subject to the standing E106 wiring note (autonomous loop must call bind after
every extend) and explicit CEO authorization.

```
RED_TEAM_VERDICT                  = PASS_WITH_NONBLOCKING_NOTES
BARS_380_385_SCIENTIFICALLY_VALID = YES
SAFE_TO_CONTINUE_FROM_BAR_386     = YES (conditional)
BAR_386_ACCESSED                  = NO
NEXT_AUTHORIZED_ACTION            = NONE — CEO DECISION REQUIRED
```

Bar 386 not exposed, not materialized; Q4 not resumed; engine/strategy definitions not modified; no prior
log entry overwritten. Control returned to CEO.

---

*Red Team · Q4 380–385 semantic integrity · causal H1 EMA50 reconstructed to the exact established
checkpoint (1901.160 @ 378, streak 39) · all six decisions identical under correct-H1, P007-003 held OPEN ·
both EMA references agree on sign · source lineage canonical (57f4ed95, verified prefix chain) · bar-379
provenance = apprenticeship not Red Team · documentation-only error, append-only correction prescribed ·
bar 386 not accessed · LEDGER E107 (prev E106).*
