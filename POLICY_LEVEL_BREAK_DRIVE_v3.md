# POLICY — Level Break-and-Drive — **v3.0 (live-valid exit horizon)**

# 🟠 DEMO_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0009.** Correction only: the v2.0 exit's second term was a **discovery-only "block boundary"** —
which does not exist on a forward-going live account (a block is a construction of the discovery regime
segments), so that leg would never fire and a trade could stay open forever. This is the SAME defect
`21fb3f9` corrected for CAND-0002/0011/0013/0014/0015/0017/0018 — CAND-0009 was missed from that batch
(it belongs to neither list in that commit: not among the 7 fixed, not among the 6 confirmed already
live-valid). Replaced with a **real-time horizon**. Single variant, family-native, chosen with a logical
reason; no optimization. **Part A and the rest of Part B (stop, sizing, mgmt) unchanged from v2.0.**
Supersedes v2.0 (kept, marked superseded). **No new primitive** — the horizon constant is already-ratified
and already cited in this policy's own v1.0/v2.0 W10 block.

## Primitive source references — W10
**No new primitive introduced.** v1.0/v2.0 W10 block stands:
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/institutional_levels.py` | `compute_prior_day_levels` (PDH/PDL), `LevelKind` | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `code/market_state.py` | `expansion`, `atr14`, **`ATR_WINDOW=14`** (the ATR lookback `expansion` itself is computed from — the SAME constant, the SAME function, already driving both this policy's entry AND its primary exit condition; reused here as the live hold horizon) | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |
| `code/interactions.py` | `to_mask`, `confluence` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/market_state.py | sha256sum`.

**Why not `COMPRESSION_WINDOW=460` or `GROUP_A_HORIZON=20`, the two constants already used for this same
purpose elsewhere:** both were rejected on the same ground — reuse must come from the primitive the
POLICY ITSELF is built from, not from a same-repo constant borrowed off a sibling candidate's own
construction. `COMPRESSION_WINDOW` is a parameter of `market_state.compression()`, which CAND-0009 never
calls (its entry/exit trigger is `expansion()`, a function that only ever reads `ATR_WINDOW`/`ATR14` —
`compression()` and `expansion()` are independent functions in the same file, not the same computation).
`GROUP_A_HORIZON` lives in `code/order_block_void.py` (Module 5, order-block/zone reaction measurement) —
a different primitive module CAND-0009's family (`level_break_with_displacement`, MK-04 × `market_state`)
never touches. `ATR_WINDOW=14` is the ONLY already-ratified constant that is literally embedded inside the
one function (`expansion`) this policy's own entry AND exit both depend on.

## PART B — exit (corrected); all other fields unchanged from v2.0
| Field | Method · reason |
|---|---|
| **stop_loss** | *(unchanged)* the broken level (`PDH` for a long break-up; `PDL` for a short break-down). |
| **exit** | **First opposing-direction expansion bar** (`market_state.expansion`, opposite sign) → exit `open[k+1]` **OR** an **`ATR_WINDOW = 14`-bar time-stop** counted forward from entry. **Reason:** `expansion()` — the SAME function this policy uses to trigger entry AND to define its own primary exit — is itself computed relative to `ATR14[i-1]`, a 14-bar rolling window; a displacement drive that has produced no opposing expansion bar within that same 14-bar volatility-measurement window has run past the timescale its own trigger is defined over. Real-time (count 14 bars forward from entry, no block, no future knowledge). Replaces the discovery-only block boundary. Deliberately **not** the daily-level horizon PDH-PDL (CAND-0001) uses: CAND-0009 is a break-and-CONTINUATION trade, not a range-reversion trade — its target is not bounded by the day the levels were defined for, so a day-boundary cutoff would be an arbitrary constraint foreign to this policy's own family, not a family-native one. |
| **management** | *(unchanged)* DECLARED ABSENT. |
| **sizing** | *(unchanged)* fixed 1R, risk-normalized to `entry − stop`; no equity-%. |
| **min_trades** | *(unchanged)* deferred to the Statistician. |

**Validity guard:** *(unchanged)* no trade if the entry is already back through the level (stop). All
coords known at entry → no lookahead.

**FAIL-CLOSED check:** the horizon is composable live from the ratified `ATR_WINDOW` (a forward bar
count); method stands. No lookahead.

## Verdict — **DEFINED (DEMO_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
## Handoff (DEMO pipeline): Red Team → Statistician (DEMO criteria) → VE → CEO → AI Trader (DEMO only).
**Other candidate production continues in parallel. No production use.**
