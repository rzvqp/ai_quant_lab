# AI_TRADER_Q4_MANAGEMENT_PROSPECTIVE_PROTOCOL_V1

**Mandate:** `AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1`, §18. **This document freezes a proposed
protocol. It does NOT authorize Q4. No Q4 bar has been revealed to produce this document.** The
protocol becomes actionable only if/when the CEO separately authorizes Q4 apprenticeship resumption.

---

## Frozen protocol for MGMT-004 (POLICY-4)

```
POLICY_ID           = MGMT-004
TRIGGER              = First M15 close at or beyond +1.0R favorable excursion from entry, on any
                        trade opened during Q4 under the existing apprenticeship entry rules
                        (unchanged from Q1-Q3 — this protocol does not touch entry logic in any way).
PARTIAL_SIZE         = None — this is a full-position stop adjustment, not a partial exit. No change
                        to position sizing.
STOP_CHANGE           = Move the stop-loss level to exactly the entry price (0R) the instant the
                        trigger condition is met. No earlier or later adjustment.
TRAIL_RULE            = None beyond the single breakeven move — this protocol tests ONLY the
                        breakeven-at-1R mechanism observed in Q1-Q3, not a broader trailing scheme
                        (POLICY-2's structural trail was `MANAGEMENT_NOT_SUPPORTED` for lack of any
                        trigger evidence and is NOT part of this frozen protocol).
TARGET_RULE           = Unchanged. Any structural target already frozen in the original trade plan
                        remains exactly as specified. This protocol does not move, add, or remove any
                        target.
COST_MODEL            = None incremental — a single stop-level change carries no additional
                        transaction cost beyond the trade's own original entry/exit fill convention
                        (close-based, per standing methodology).
NO_RETROACTIVE_CHANGES = This protocol applies ONLY to trades opened AFTER Q4 authorization and after
                        this protocol is frozen. It does not, and cannot, retroactively alter any
                        Q1-Q3 trade's recorded result — those remain exactly as evidenced. If a Q4
                        trade's initial stop, entry, or setup logic needs any change to accommodate
                        this protocol, that would itself violate this protocol's own preconditions
                        and must be flagged, not silently absorbed.
```

## What Q4 evidence would be needed to move this candidate's status

Per the mandate's own explicit rule (§12: "no same-sample validation claim... Q4 must remain unseen
and may later serve as forward evidence only after CEO authorization"), moving MGMT-004 beyond
`MANAGEMENT_CANDIDATE_UNVALIDATED` would require, at minimum:

1. **At least one Q4 trade that reaches +1.0R and would otherwise have closed negative** — to test
   whether the mechanism reproduces in genuinely new (not re-analyzed) data.
2. **At least one LONG-direction instance** — the entire Q1-Q3 supporting evidence is SHORT-only
   (§`AI_TRADER_MANAGEMENT_POLICY_LIBRARY_V1.md`'s own disclosed limitation); Q4 is the first
   opportunity to test whether the mechanism is direction-symmetric.
3. **Ideally, evidence from more than one quarter/regime context** — the entire Q1-Q3 supporting
   sample is a single continuous episode; a genuine regime shift during Q4 (should one occur) would
   be a materially stronger test than more of the same regime.
4. **No sign-flip under the same leave-one-out discipline applied in the discovery pass.**

**Even full confirmation on Q4 evidence would not make this "VALIDATED" under this apprenticeship's
own standing terminology** — the appropriate next status, per the established evidence-grade
conventions used throughout this project (e.g. `GOLD_BEHAVIOR_MODEL_V1.md`'s own status ladder),
would be a graduated research status (e.g. `DEVELOPING_MANAGEMENT_POLICY` or similar), still short of
formal validation, which per this project's standing practice requires independent
Statistician/Red-Team-tier review outside the AI Trader apprenticeship itself — not something this
document claims authority to grant.

---

**This document does not start Q4. It exists so that, if and when Q4 is separately authorized, this
specific management-layer question can be tested cleanly, prospectively, and without retrofitting a
rule to outcomes already known — exactly the discipline this whole mandate was built to protect.**
