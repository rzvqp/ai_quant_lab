# POLICY — OB Sweep-Rejection × Liquidity-Void Confluence — **v3.0 (live-valid exit horizon)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0018.** Correction only: the v2.0 exit's fallback was a **discovery-only "block boundary"** (never
fires live → open forever). Replaced with a **real-time horizon**. Single variant, family-native; no
optimization. **Part A and the rest of Part B unchanged from v2.0.** Supersedes v2.0 (kept, marked
superseded). **No new primitive.**

## Primitive source references — W10
- **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6` · branch `discovery-mk-matrix-v1`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_order_blocks`, `detect_rejections`, `track_breaker`, `ReactionEvent`, `GROUP_A_HORIZON=20` | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `code/order_block_void.py` | `detect_liquidity_voids` (entry qualifier) | `6ec7adbfd3bbaab2d4c1e35f1ad6de2631875319bb5312e90fba572ded32b921` |

## PART B — exit (corrected); all other fields unchanged from v2.0
| Field | Method · reason |
|---|---|
| **stop_loss** | *(unchanged)* OB whole-bar floor `Low_OB`/`High_OB`. |
| **exit** | **OB body far edge in the reaction direction** **OR** a **`GROUP_A_HORIZON = 20`-bar time-stop** counted forward from entry. **Reason:** 20 is the ratified reaction horizon of the OB-rejection component (the void is only the entry qualifier). Real-time. Replaces the discovery-only block boundary. |
| **management** | *(unchanged)* DECLARED ABSENT. |
| **sizing** | *(unchanged)* fixed 1R. |
| **min_trades** | *(unchanged)* deferred to the Statistician. |

**FAIL-CLOSED check:** composable live from `GROUP_A_HORIZON`; method stands. No lookahead.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
