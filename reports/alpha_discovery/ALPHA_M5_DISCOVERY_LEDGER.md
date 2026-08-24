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

## Frontier M5-3 — pullback-completion entry + M5-structural stop (m5_f3.py) : REJECT (tighter stop worse, §7 guard)
M5-structural (micro-high) stop avgR -0.109 vs same-entry ATR-stop control -0.061 (medStop 2.78 vs 3.83 USD) — the tighter M5
stop is hit MORE (micro-high doesn't hold), worse not better. §7 guard rejects (tighter-fitting, not informational). Both fail
(setup era-dependent CONF -0.18/-0.21). M5-structural stops carry no incremental path-survival information here.

## Frontier M5-4 — M15 coil-breakout + M5 displacement-confirmation (m5_f4.py) : no robust M5 info
Causal (entry at M5-displacement bar, outcome forward). P(target-first) BASE 0.484 -> M5-DISP 0.500 (coinflip), delta not robust
(DISC -0.004 / CONF +0.039 / OOS +0.040). M5 displacement does not reliably separate real breakout from fakeout across partitions.

## M5 FIRST-BATCH CONCLUSION (M5-1..M5-4; substrate ready + causal-audited)
Native M5 substrate is verified + causally aligned (H4->H1->M15->M5, strict nominal-close, 0 leak). Four info-first frontiers
covering the main M5-value hypotheses — momentum-onset entry-timing (M5-1: +0.02 adverse-first but tradeable worse via RR penalty),
acceptance/hold (M5-2: causally null, circularity caught), structural-stop/path-survival (M5-3: tighter stop worse, §7-rejected),
displacement-confirmation (M5-4: coinflip, not robust) — ALL show M5 path information is MARGINAL-to-NULL causally and does NOT
convert a higher-TF setup into a tradeable edge. ROOT: the binding constraint is HIGHER-TF DIRECTION (era-dependent, R20), which
lives above the entry layer; M5 (a finer entry/path layer) relocates the ~coinflip ordering but cannot create era-independent
direction. BOUNDED conclusion (not universal): no M5-incremental edge found in the hypotheses tested; substrate remains available
for any future setup that first demonstrates an era-robust higher-TF direction (which price+volume has not, except S5).
