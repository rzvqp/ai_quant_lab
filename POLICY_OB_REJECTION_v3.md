# POLICY — Order-Block Sweep-Rejection — **v3.0 (live-valid exit horizon)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0011.** Correction only: the v2.0 exit's fallback was a **discovery-only "block boundary"** (does
not exist on a forward-going account → the leg would never fire → a trade could stay open forever).
Replaced with a **real-time horizon**. Single variant, family-native; no optimization. **Part A and the
rest of Part B (stop, sizing, mgmt) unchanged from v2.0.** Supersedes v2.0 (kept, marked superseded).
**No new primitive** — the horizon constant is already-ratified.

## Primitive source references — W10
- **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6` · branch `discovery-mk-matrix-v1`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_order_blocks`, `detect_rejections`, `track_breaker`, `ReactionEvent`, `GROUP_A_HORIZON=20` (the ratified reaction-measurement horizon of these primitives) | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |

## PART B — exit (corrected); all other fields unchanged from v2.0
| Field | Method · reason |
|---|---|
| **stop_loss** | *(unchanged)* OB whole-bar floor `Low_OB`/`High_OB` (the ratified breaker boundary). |
| **exit** | **OB body far edge in the reaction direction** (`zone_upper`/`zone_lower`) **OR** a **`GROUP_A_HORIZON = 20`-bar time-stop** counted forward from entry. **Reason:** `GROUP_A_HORIZON=20` is exactly the ratified reaction-measurement window of `detect_rejections` — the primitive's *own* horizon, real-time (a forward bar count, no block, no future). Replaces the discovery-only block boundary. |
| **management** | *(unchanged)* DECLARED ABSENT. |
| **sizing** | *(unchanged)* fixed 1R, no equity-%. |
| **min_trades** | *(unchanged)* deferred to the Statistician. |

**FAIL-CLOSED check:** the horizon is composable live from the ratified `GROUP_A_HORIZON`; method stands. No lookahead.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
