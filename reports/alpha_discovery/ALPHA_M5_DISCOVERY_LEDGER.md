# M5 Discovery Ledger (native M5, causal, 2021-2026 single macro-era — disclosed; no era-independence claim)

Program: higher-TF (M15/H1/H4) structural edge + M5 trigger/path-info (§6). Info-first (§7); M5 must add INCREMENTAL causal
information, not tighter-fitted stops or optimized timing. Partitions within window: DISC<=2023 / CONF 2024 / OOS 2025-26.

## Frontier M5-1 — H1-down + M15-bounce SHORT, M5 down-break trigger (m5_f1.py, m5_f1_trade.py) : M5 info REAL but NOT tradeable
INFO: M5 down-break entry raises P(down-first) in ALL partitions (BASE->M5-COND delta DISC +0.010 / CONF +0.041 / OOS +0.023) —
first causal cross-partition ordering improvement in the campaign. BUT absolute ordering stays ~0.51 (near-coinflip). TRADEABLE:
BASE short avgR -0.056, M5-COND -0.068 (delta -0.012, M5 WORSE) — the M5 trigger delays entry to a lower price, worsening RR and
offsetting the ordering gain; setup era-dependent (CONF 2024 -0.22, bull bought the bounces). M5 adds info but not tradeable value.
Lesson: M5 ordering gain is real but small; delayed-entry RR penalty cancels it; M5 cannot fix era-dependent DIRECTION.

## Frontier M5-2 — M15 breakout + M5 acceptance/hold (m5_f2.py) : CAUSALLY NULL (circularity caught & removed)
FIRST pass gave P(up1st)=0.93 for M5-accepted — a CIRCULARITY artifact: the acceptance window (i+1..i+24) OVERLAPPED the outcome
window (from bar i), so 'held above level' was mechanically entangled with 'didn't hit down-stop first'. FIXED: enter at the
acceptance-confirmation bar (i+24), measure outcome strictly forward. Result: M5-ACCEPTED P(up1st)=0.507 vs BASE 0.505 (delta
+0.002, NOT robust: DISC +0.011 / CONF -0.014 / OOS -0.002). M5 acceptance/hold carries NO causal forward information; apparent
value was 100% lookahead. (Rigor note: same overlap-lookahead class the Statistician caught in CRS-1 — self-caught here.)

## M5 first-batch pattern (M5-1, M5-2)
M5 path info, measured causally, is marginal-to-null: M5-1 momentum-onset timing gives a small real adverse-first gain (+0.02)
but the delayed-entry RR penalty cancels it (tradeable delta -0.012); M5-2 acceptance/hold is causally null. Finer resolution
relocates the same ~coinflip ordering; it does not create era-independent DIRECTION (R20). M5 cannot fix what M15 could not.
