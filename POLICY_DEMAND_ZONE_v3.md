# POLICY — Demand/Supply-Zone Re-entry Reaction — **v3.0 (live-valid exit horizon)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0013.** Correction only: the v2.0 exit's fallback was a **discovery-only "block boundary"** (never
fires live → open forever). Replaced with a **real-time horizon**. Single variant, family-native; no
optimization. **Part A and the rest of Part B unchanged from v2.0.** Supersedes v2.0 (kept, marked
superseded). **No new primitive.**

## Primitive source references — W10
- **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6` · branch `discovery-mk-matrix-v1`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_demand_zones`, `DemandZone` edges, `GROUP_A_HORIZON=20` (Module-5 reaction horizon) | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `code/interactions.py` | `price_in_zone` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

## PART B — exit (corrected); all other fields unchanged from v2.0
| Field | Method · reason |
|---|---|
| **stop_loss** | *(unchanged)* the zone's far edge (`zone_lower`/`zone_upper`). |
| **exit** | **Zone near edge in the reaction direction** **OR** a **`GROUP_A_HORIZON = 20`-bar time-stop** counted forward from entry. **Reason:** 20 is the lab's ratified Module-5 reaction-measurement horizon; a zone reaction resolves within it. Real-time (forward bar count, no block). Replaces the discovery-only block boundary. |
| **management** | *(unchanged)* DECLARED ABSENT. |
| **sizing** | *(unchanged)* fixed 1R. |
| **min_trades** | *(unchanged)* deferred to the Statistician. |

**FAIL-CLOSED check:** composable live from `GROUP_A_HORIZON`; method stands. No lookahead.

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
