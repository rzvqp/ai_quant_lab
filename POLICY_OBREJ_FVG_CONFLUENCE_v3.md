# POLICY — OB Sweep-Rejection × FVG-CE50 Confluence — **v3.0 (live-valid exit horizon)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0015.** Correction only: the v2.0 exit's fallback was a **discovery-only "block boundary"** (never
fires live → open forever). Replaced with a **real-time horizon**. Single variant, family-native; no
optimization. **Part A and the rest of Part B unchanged from v2.0.** Supersedes v2.0 (kept, marked
superseded). **No new primitive.**

## Primitive source references — W10
- **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6` · branch `discovery-mk-matrix-v1`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_order_blocks`, `detect_rejections`, `ReactionEvent`, `GROUP_A_HORIZON=20` | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `code/imbalance_mechanics.py` | `detect_fvgs`, `detect_fvg_reactions`, `FairValueGap` edges | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |

## PART B — exit (corrected); all other fields unchanged from v2.0
| Field | Method · reason |
|---|---|
| **stop_loss** | *(unchanged)* below both structures: `min(Low_OB, FVG.lower)` / `max(High_OB, FVG.upper)`. |
| **exit** | **Far side of the combined imbalance zone** (`max(OB.zone_upper, FVG.upper)` / `min(OB.zone_lower, FVG.lower)`) **OR** a **`GROUP_A_HORIZON = 20`-bar time-stop** counted forward from entry. **Reason:** 20 is the ratified reaction horizon of the OB-rejection component; both structures are imbalances (no daily level). Real-time. Replaces the discovery-only block boundary. |
| **management** | *(unchanged)* DECLARED ABSENT. |
| **sizing** | *(unchanged)* fixed 1R. |
| **min_trades** | *(unchanged)* deferred to the Statistician. |

**FAIL-CLOSED check:** composable live from `GROUP_A_HORIZON`; method stands. No lookahead.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
