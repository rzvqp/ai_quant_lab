# POLICY — FVG Consequent-Encroachment Reaction — canonical schema — **v2.0 (Part B completed)**

# 🟠 DEMO_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**One authorized pilot Part B — single variant, chosen with a logical reason BEFORE any result; no
multiple variants, no optimization.** Structural, composed from ratified primitives, no new calculation,
no lookahead. Supersedes v1.0 (Part B UNSPECIFIED). Part A unchanged.

| Field | Value |
|---|---|
| **policy_id** | `FVG-CE50-REACTION` |
| **version** | `2.0` (DEMO_BASELINE — Part B completed; Part A unchanged from v1.0) |
| **family** | `imbalance_reaction` (MK-03) |

## Primitive source references — W10
**No new primitive introduced by Part B** — stop and target both use `FairValueGap.lower`/`.upper` (the
gap's own ratified edges), already cited. v1.0 W10 block stands:
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/imbalance_mechanics.py` | `detect_fvgs`, `FairValueGap` (`upper`, `lower`, `ce_50`, `confirmed_idx=i+1`), `detect_fvg_reactions` (CE-50 Q6, consume-once Q5), `detect_inverse_fvgs` (Q4 = decisive close beyond the far edge) — MK-03, CLOSED | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/imbalance_mechanics.py | sha256sum`.

---

## PART A — ENTRY MECHANISM — **UNCHANGED from v1.0** (see `POLICY_FVG_REACTION_v1.md`)
Activation = a 3-bar FVG known from `confirmed_idx=i+1`, block-confined. Trigger = first CE-50 touch
(`detect_fvg_reactions`, consume-once Q5). Entry = FVG polarity (bullish → long, bearish → short),
`entry@next-open`. `regimes_permitted` / `min_trades` = Statistician.

---

## PART B — RISK MANAGEMENT — **COMPLETED (DEMO_BASELINE — single variant, structural)**

**Choice rationale, fixed BEFORE any result:** fixed-ATR is non-informative (structure dominated). This is
an **imbalance-reaction** family — its natural structural anchors are the **FVG's own two edges** (NOT a
daily level, NOT a displacement bar). The far edge is already the ratified invalidation boundary (Q4: a
decisive close beyond it *inverts* the gap). One variant only.

| Field | Method (single chosen variant) · reason |
|---|---|
| **stop_loss** | **The FVG's FAR edge** (fill-through): bullish FVG (long) → stop = `lower` (`= high[i-1]`, the gap bottom); bearish (short) → stop = `upper`. **Reason:** the entry thesis is "the gap holds as demand/supply"; its ratified structural falsification is a decisive move through the far edge — the very boundary whose close-beyond defines FVG **inversion** (Q4). Event-anchored to the gap's own geometry, not a distance. |
| **exit** | **The FVG's NEAR edge in the reaction direction** (gap respected): bullish (long) → target = `upper` (top of gap); bearish (short) → target = `lower`. **Reason:** a respected imbalance reacts back out of its own zone; the gap's opposite edge is the structural completion of that reaction. Resolves at the **first of**: stop breached · target reached · block boundary (time-stop). *Note:* entering at `ce_50` (the midpoint), `upper − ce_50 = ce_50 − lower`, so the R:R is ≈1 **as a geometric consequence of a midpoint entry**, not a chosen fixed RR. |
| **management** | **DECLARED ABSENT** (no partials/breakeven/trailing) — DEMO_BASELINE minimalism. |
| **sizing** | **Fixed 1R, risk-normalized** to `entry − stop`. No equity-%. R-metrics are sizing-invariant. |
| **min_trades** | **Deferred to the Statistician's DEMO criteria.** |

**Validity guards (structural, lookahead-safe):** no trade if the entry (`next-open`) is already beyond the
far edge (stop) or beyond the near edge (target). All Part-B coordinates (`lower`, `upper`) known at entry
→ no lookahead.

**FAIL-CLOSED check:** buildable from ratified primitives without inventing any calculation (stop and
target are the gap's own ratified edges). Method stands.

---

## Verdict — **DEFINED (DEMO_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
## Handoff (DEMO pipeline): Red Team → Statistician (DEMO criteria) → VE → CEO → AI Trader (DEMO only).
**Other candidate production continues in parallel. No production use.**
