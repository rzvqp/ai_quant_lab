# OB_CAUSAL_EXECUTION_HYPOTHESIS_REGISTER_V1 — 4 execution hypotheses (structure frozen)

§5 deliverable. Structure (OB/BOS/swing/freshness/first-retest/displacement≥1.5/session/stop/cost) FROZEN from OBR — not re-searched.
Only the causal EXECUTION protocol varies. All entries specify same-bar semantics before testing (§7) and pass the §19 anti-hindsight audit.

| ID | family | entry semantic | rejection/extra condition | result (net-R) | verdict |
|---|---|---|---|---|---|
| **EXEC-A** | true resting limit | fill at block_high on first bar `low≤block_high`; resolve from fill bar; conservative same-bar | none (same-bar close cannot cancel a touched fill) | **−0.067** (=Statistician) | FALSIFIED (sanity baseline) |
| **EXEC-B** | retest close → next open | enter next-bar OPEN | first retest bar still structurally valid at close (`close≥block_low`) | **−0.266** | FALSIFIED |
| **EXEC-C** | rejection close → next open | enter next-bar OPEN | retest bar closes back **above** block_high (bullish rejection) | **−0.206** | FALSIFIED |
| **EXEC-D** | penetration + reclaim → next open | enter next-bar OPEN | a bar penetrates (closes ≤block_high) then a later bar **reclaims** (closes >block_high) | **−0.185** | FALSIFIED |

## §19 anti-hindsight audit — ALL PASS (every family)
OB_KNOWN_BEFORE_RETEST=YES · BLOCK_FROZEN=YES · ENTRY_RULE_FROZEN=YES · ENTRY_INFORMATION_CAUSAL=YES ·
NO_ENTRY_BAR_CLOSE_USED_BEFORE_LIMIT_FILL=YES (EXEC-A fills on touch, close never cancels it) ·
NEXT_BAR_OPEN_USED_ONLY_AFTER_SIGNAL_BAR_CLOSE=YES (EXEC-B/C/D) · STOP_FROZEN_BEFORE_OUTCOME=YES · TARGET_FROZEN_BEFORE_OUTCOME=YES ·
NO_CENTERED_PIVOT_LOOKAHEAD=YES · NO_FUTURE_H1H4_DATA=YES (M15-only) · NO_INTRABAR_ORDER_INFERENCE=YES (conservative same-bar) ·
NO_SHALLOW_DEPTH_HINDSIGHT=YES (§6 — no execution conditions on eventual retest depth).

## §12 discipline
EXECUTION_HYPOTHESES_FROZEN_BEFORE_OOS = YES (4 families pre-specified per §5; DEV/OOS chronological; no OOS-driven redefinition).
OOS_INTEGRITY = PASS. §13 multiple-testing: 4 pre-specified executions on an already-discovered level; no cell mined — all 4 negative,
so no isolated-positive interpretation risk.

## Outcome
RAW=4 · TESTED=4 · FALSIFIED=4 · **SURVIVED=0.** No causal execution monetizes the confirmed OB level information.
