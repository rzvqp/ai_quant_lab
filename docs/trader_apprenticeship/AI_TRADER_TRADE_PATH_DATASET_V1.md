# AI_TRADER_TRADE_PATH_DATASET_V1

**Mandate:** `AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1`, §2-4. Q4 sealed throughout — every trade below
is dated 2020-06 through 2020-07-22, entirely inside the already-fully-replayed Q1-Q3 window.
Original entries, directions, initial stops, and structural targets are preserved exactly as frozen
at the time; the only thing this mandate studies is what happens to management *after* entry.

**Source discipline:** all `MFE_R`/`MAE_R`/`RESULT_R` figures are the already-frozen values from
`TRADE_EVIDENCE_LOG.md` (verified this pass against the raw per-trade EVIDENCE TAGS/EVIDENCE CLOSE
entries, lines 98-596) and `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md` §7. **No path field below was
synthesized** — where full bar-by-bar path reconstruction (continuous `MFE_PATH`/`MAE_PATH` time
series, exact `TIME_FROM_ENTRY` for every intermediate R-level) is not present in the committed
record, it is marked `NOT_RECONSTRUCTED_THIS_PASS`, not estimated. What IS reported for every trade
either comes directly from the frozen record or is a direct arithmetic derivation from frozen
numbers (e.g. `MAX_GIVEBACK_FROM_MFE = MFE_R - RESULT_R`), each labeled as such.

---

## 1. Population determination (§2 of the mandate)

| Trade | Has frozen MFE_R AND MAE_R? | Population |
|---|---|---|
| Q2 #57, #58, #59, #60, #61, #62, #63, #64, #65, #66 | YES — all 10 have both fields explicitly frozen in `TRADE_EVIDENCE_LOG.md` | **PRIMARY** |
| Q3-001, Q3-002 | YES — both have explicitly frozen `MFE_PIPS/MFE_R` and `MAE_PIPS/MAE_R` fields | **PRIMARY** |
| Q3-003 | Partial — no frozen `MFE_R` field, but a stated wick-high value ("approached TP1 via wick to 1815.236... never closed through") lets MFE be derived arithmetically from entry price + risk points, both frozen; no MAE evidence at all | **SECONDARY** |
| Q3-004 | Partial — a narrative-only MFE figure ("~3.16R") is stated in the trade's own OUTCOME_NOTES but not independently frozen as a formal `MFE_R` field with the same rigor as the primary set; no MAE evidence | **SECONDARY** |
| Q3-005 | NO — no MFE or MAE evidence of any kind in the retained record (stopped out within 2h15m, no favorable-excursion note) | **EXCLUDED** |
| Q1 (all) | N/A | **N/A** — zero trades in Q1 (pure observation quarter) |

```
PRIMARY_N   = 12  (10 Q2 fully-evidenced + Q3-001 + Q3-002)
SECONDARY_N = 2   (Q3-003, Q3-004)
EXCLUDED_N  = 1   (Q3-005)
EXCLUSION_REASONS = Q3-005: no MFE/MAE evidence of any kind logged in the retained record —
                     including it in a giveback-quantification study would require fabricating a
                     favorable-excursion figure that does not exist in the source, which §7/§16 of
                     the mandate explicitly forbids.
```

**No trade from the primary or secondary population had its entry, direction, initial stop, or
structural target altered for this study** — every field below is copied from the frozen entry-time
record.

---

## 2. Primary population — original trade contract + path evidence

| Trade | Dir | Entry | Initial Stop | Structural Target | Orig. mgmt plan | Result R | MFE R | MAE R | Giveback (MFE−Result) |
|---|---|---|---|---|---|---|---|---|---|
| #57 | SHORT | 1706.11 | 1710.66 | none fixed (standing practice at the time) | hold to original stop, no trail | −1.361 | 0.138 | 1.586 | 1.499 |
| #58 | SHORT | 1740.327 | 1745.304 | none fixed | discretionary trail (3 trails) | +2.463 | 3.743 | 0.109 | 1.280 |
| #59 | SHORT | 1712.008 | 1726.146 | none fixed | discretionary trail (trail-flip) | −0.046 | 1.586 | 0.267 | 1.632 |
| #60 | SHORT | 1707.01 | 1713.5 | none fixed | hold to original stop, no trail | −1.379 | 0.223 | 1.497 | 1.602 |
| #61 | SHORT | 1707.856 | 1718.5 | none fixed | hold to original stop, no trail | −1.150 | 0.695 | 1.280 | 1.845 |
| #62 | SHORT | 1680.167 | 1688.5 | none fixed | hold to original stop, no trail | −1.001 | 1.168 | 1.058 | 2.169 |
| #63 | LONG | 1695.555 | 1685.5 | none fixed | discretionary trail (4 trails) | +2.306 | 3.163 | 0.506 | 0.857 |
| #64 | SHORT | 1740.496 | 1744.918 | none fixed | discretionary trail (3 trails) | +1.443 | 2.467 | 0.209 | 1.024 |
| #65 | SHORT | 1724.903 | 1732.242 | **1704.484** (single frozen TP, fixed-SL/TP methodology — first such trade) | fixed-SL/TP, no trailing | −1.119 | 1.652 | 1.119 | 2.771 |
| #66 | SHORT | 1766.952 | 1778.874 | **1747.566** (single frozen TP) | fixed-SL/TP, no trailing | −1.398 | 1.626 | 1.467 | 3.024 |
| Q3-001 | SHORT | ~1767 area (level break) | per entry tag | none independently confirmed in retained record | close-based, standard | −1.084 | 0.686 | 1.086 | 1.770 |
| Q3-002 | SHORT | 1776.216 | 1779.446 | **TP1 1758.665 (50%) / TP2 1748.566 (50%)** — a genuine 2-way split, NOT the 40/30/30 framework | TP1/TP2, no trail before TP1 | −1.120 | 0.752 | 1.271 | 1.872 |

**Structural-target finding (mechanical, not opinion):** of the 12 primary trades, **8 had NO fixed
target of any kind** (#57-64, pure discretionary-trail-or-hold-to-original-stop methodology), **2
had a single frozen TP** (#65, #66 — not split into TP1/TP2), and **1 had a genuine two-way TP1/TP2
split** (Q3-002, 50/50, not 40/30/30). **None of the 12 primary trades used the 40/30/30 framework**
— see `AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md` §5 for why this matters.

---

## 3. Derived (not fabricated) touch/giveback fields

For every trade, the following are **arithmetically or logically derived from the frozen MFE_R/MAE_R/
RESULT_R values above** — not new observations, not estimates:

| Trade | 0.5R touched | 1.0R touched | 1.5R touched | 2.0R touched | 2.5R touched | 3.0R touched | TP1 touched | TP2 touched |
|---|---|---|---|---|---|---|---|---|
| #57 | NO (MFE 0.138) | NO | NO | NO | NO | NO | N/A (no target) | N/A |
| #58 | YES | YES | YES | YES | YES | YES | N/A | N/A |
| #59 | YES | YES | YES | NO | NO | NO | N/A | N/A |
| #60 | NO | NO | NO | NO | NO | NO | N/A | N/A |
| #61 | YES | NO | NO | NO | NO | NO | N/A | N/A |
| #62 | YES | YES | NO | NO | NO | NO | N/A | N/A |
| #63 | YES | YES | YES | YES | YES | YES | N/A | N/A |
| #64 | YES | YES | YES | YES | NO | NO | N/A | N/A |
| #65 | YES | YES | YES | NO | NO | NO | **NO** (closest approach 8.296pts short) | N/A |
| #66 | YES | YES | YES | NO | NO | NO | **NO** (closest approach 0.006pt short — see integrity note below) | N/A |
| Q3-001 | YES | NO | NO | NO | NO | NO | N/A | N/A |
| Q3-002 | YES | NO | NO | NO | NO | NO | **NO** (TP1 at 5.434R, MFE only 0.752R) | **NO** |

**A touch at threshold X is inferred `YES` only when `MFE_R >= X` (a valid, non-fabricated logical
consequence of the frozen peak value) and `NO` when `MFE_R < X`. The exact TIME each threshold was
first touched is `NOT_RECONSTRUCTED_THIS_PASS` for any threshold below the trade's own peak — only
the peak's own timestamp is recorded in the source for most trades.**

**Integrity note on #66 (disclosed, not silently resolved):** `TRADE_EVIDENCE_LOG.md`'s own close
narrative for #66 states *"price moved the wrong way throughout the trade's entire life — closest
approach to TP was near entry itself, never meaningfully favorable"* — this **directly contradicts**
`TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md` §2's own account, *"closest approach 0.006pts [from full
TP], 2020-06-26 14:15 UTC, near-full-TP approach,"* which is also the source of the MFE_R=1.626
figure used throughout this document. The checkpoint's account is used as the authoritative MFE_R
figure here because it is internally arithmetic-consistent (1.626R × 11.922pts risk = 19.38pts ≈ the
full 19.386pt entry-to-TP distance, matching the "0.006pt short" claim exactly), while the log
narrative's "near entry itself" claim does not reconcile with any other number in the record. **This
is reported as a genuine, unresolved provenance conflict between two committed files, not silently
picked** — see `AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md`'s integrity section.

**`RETURN_TO_ENTRY_AFTER_MFE`** — derived: `YES` (definitionally) for every trade where `RESULT_R <=
0` and `MFE_R > 0` (price must have retraced through breakeven to reach a net-negative or breakeven
close) — this is 9 of 12 primary trades. For the 3 winners (#58, #63, #64), price never closed below
entry, so `RETURN_TO_ENTRY_AFTER_MFE = NO` for the realized close (though a mid-trade dip to entry
without a full round-trip cannot be ruled out from peak-only data — marked `UNKNOWN (peak-only
data)`, not asserted `NO` with false confidence).

---

## 4. Sequencing convention (disclosed modeling assumption)

Where the source explicitly states a timestamp for MFE and/or notes MAE as *"the closing/triggering
bar's own high"* (true for #59, #60, #61, #62, #66 — verified directly in the source text), the
documented sequence is **MFE peak occurs first, then price slides adversely all the way to the
final close** — i.e. giveback is one continuous move, not a re-test of favorable territory after an
initial reversal. This is the basis for every loss-side policy simulation in
`AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md`. For trades without an explicit stated order (#57, Q3-001,
Q3-002), the same convention is applied by analogy (all three are SHORT entries with a close-based
stop-out, structurally identical in kind to the trades where the order IS explicitly stated) — **this
is a disclosed assumption, not a directly observed fact, for these three trades specifically.** For
the 2 winners with an explicit early-MAE/late-MFE order (#64: MAE at 14:30 UTC near the 14:15 UTC
entry, MFE at 17:15 UTC later), the reverse ordering (risk tested first, favorable move later) is
used, consistent with a typical breakout-entry mechanism.

---

## 5. Context fields (where available, never synthesized)

| Trade | Session | H4/H1/M15 relation (frozen at entry) | Direction | Holding duration |
|---|---|---|---|---|
| #57 | NY_US_CASH | H4 BEARISH / WITH_TREND | SHORT | not separately logged |
| #58 | NY_US_CASH | H4 BEARISH / WITH_TREND | SHORT | resolved via 192-bar horizon |
| #59 | PRE_US | H4 BEARISH / WITH_TREND | SHORT | ~34.5h to horizon |
| #60 | PRE_US | H4 BEARISH / WITH_TREND | SHORT | 2 bars to stop (very fast) |
| #61 | NY_US_CASH | H4 BEARISH / WITH_TREND | SHORT | not separately logged |
| #62 | LONDON | H4 BEARISH / WITH_TREND | SHORT | 5 bars to stop |
| #63 | LONDON | H4 BEARISH (stale) / H1 bullish reclaim / TRANSITIONAL | LONG | ~48.5h |
| #64 | not separately logged | H4 BEARISH / PARTIALLY_ALIGNED | SHORT | ~58h wall-clock / ~35 bars trading |
| #65 | LONDON | H4 BEARISH / FULLY_ALIGNED | SHORT | ~44.25h |
| #66 | LONDON | H4 BEARISH / PARTIALLY_ALIGNED | SHORT | 146.25h |
| Q3-001 | not separately logged this pass | PARTIALLY_ALIGNED | SHORT | 30min |
| Q3-002 | LONDON | FULLY_ALIGNED | SHORT | 3h15m |

---

*See `AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md` for the pathology quantification, pre-registered
policy tests, and robustness analysis built from this dataset.*
