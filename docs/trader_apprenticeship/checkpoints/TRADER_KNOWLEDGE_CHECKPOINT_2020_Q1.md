# TRADER_KNOWLEDGE_CHECKPOINT_2020_Q1

- **KNOWLEDGE_VERSION**: KNOWLEDGE_V1 (first checkpoint; no prior version to supersede)
- **LANE**: Lane A — HISTORICAL_MARKET_APPRENTICESHIP
- **INSTRUMENT**: XAUUSD
- **COVERAGE**: 2020-01-01 through 2020-03-31 (2020-Q1), genuine chronological M15 TradingView Bar Replay,
  H4/H1 as causal context. Frozen 2026-08-25 (real session date).
- **STATUS**: FROZEN — this document is not retroactively edited. A changed interpretation in a later
  quarter creates KNOWLEDGE_V2, referencing this version, never rewriting it (mandate §18).

---

## 1. What actually happened this quarter (chronological summary)

**January – mid-February: range-bound regime.** Following a 2019 uptrend and a Jan 1-2 breakout, XAUUSD
traded in a roughly 1517-1593 range through most of January and into mid-February. This is the regime
in which TOC-001 was first observed.

**Late February – March: the COVID-19 / oil-price-war volatility regime begins and never resolves
within Q1.** A fresh multi-week high (~1598, 2020-02-19) held for an unusually long stretch (44+ M15
bars) before the broader market moved into acute, sustained volatility. By 2020-03-10 through 03-12,
the market was in a genuine liquidation-cascade phase: a record-volume crash bar (volume 10,962) on
03-12, a second severe crash leg 03-13, and a further leg down to fresh lows (~1451-1465) around
03-16. 1451.4 became the quarter's structural low.

**Late March: a large, volatile recovery leg, still inside the same unresolved volatility regime.**
From roughly 03-20 (price ~1494.5) through 03-27, price mounted a single sustained bullish leg to a
high near 1644 — the largest, most sustained directional move observed all quarter (~150 points over
several days). This leg was punctuated repeatedly by fast, high-volume whipsaws at specific levels
(1504.8, 1568, 1608, 1620, 1638.9), each initially looking like genuine multi-bar or volume-confirmed
resolution and then failing within a handful of bars.

**Final week (03-28 to 03-31): extended chop, then a late, decisive break.** Price spent the last few
days of the quarter chopping in a broad 1596-1638.9 band. The 1596 level specifically was tested via
wick four-plus separate times across this stretch and never once closed below — until the final hours
of the quarter (03-31, roughly 17:00-19:05 UTC in-replay), when it broke decisively on two of the
heaviest-volume M15 bars of the entire quarter (8,690 and 8,116). Q1 closed at **~1578.7**, well below
both the pre-crash January range and the late-March recovery high, still inside the broader volatility
regime that began with the crash and did not normalize by quarter-end.

---

## 2. Frozen TRADER_OBSERVATION_CANDIDATEs this quarter

Two candidates were frozen this quarter, both still `UNVALIDATED_TRADER_OBSERVATION` — this
apprenticeship generates candidates for a separate, CEO-authorized Alpha audit; it does not
self-validate them.

### TOC-001 — fresh range extremes tend to fade, but not always
Discovered 2020-02-19 in the January-February range-bound regime: a fresh multi-week extreme that
meaningfully exceeds the prior tested high/low of an established range is usually not held — price
gives back most of the extension within 1-2 bars. 4 confirming instances. **One confirmed
counterexample** was logged in the same freeze: the 02-19 breakout itself held for 44+ consecutive M15
bars without reverting, categorically different from the 1-2 bar rejections in the other 4 instances.
The frozen definition's "1-2 bar rejection window" is too narrow/absolute as originally written and
needs revision — a real, mixed record (not proof either way), disclosed honestly rather than hidden.

### TOC-002 — multi-bar holds are not reliable confirmation in this extended-volatility regime
Discovered 2020-03-10 to 03-12 during the crash cascade: a multi-bar hold (5-6 consecutive M15 closes)
on one side of a contested level is not by itself reliable confirmation that the level is resolved —
even holds that clear a "wait for multi-bar confirmation" bar can still fail. This was **reinforced
repeatedly through the rest of the quarter**, across three separate multi-day stretches spanning very
different market conditions within the same broader regime:
- 03-10 to 03-12 (original 3 instances, crash-cascade volatility)
- 03-24 (1568 break-and-reclaim within ~4 bars, during the bullish leg's pullback)
- 03-25 (1608 break-and-reclaim within ~2 bars, volume-confirmed, still failed)
- 03-27 (a genuine 5-bar hold below 1620 — matching TOC-002's original bar-count threshold exactly —
  still reversed and reclaimed within 2 bars)

Six total instances across three distinct sub-stretches, no confirmed counterexample yet (a hold that
genuinely stuck was never observed this quarter — every multi-bar hold attempted eventually gave way,
some after 16+ bars). Updated read: the mechanism looks less like "crash-specific liquidity chaos" and
more like a durable property of the whole extended-volatility regime that has persisted since late
February — this remains untested against a genuinely calm regime, which never arrived within Q1.

---

## 3. The quarter's central, honestly-disclosed learning event

The most repeated, costly-if-acted-on pattern this quarter was **whipsaws at specific levels during
sustained high volatility** — 1504.8, 1568, 1596, 1608, 1620, and 1638.9 were each tested and failed
(or held-then-failed) multiple times, often on volume that looked decisive. Several times a snapshot
called a break "confirmed" only to be explicitly reclassified INVALIDATED or PARTIALLY_CONFIRMED
within the next 1-2 bars — this is disclosed as-is in `AI_TRADER_EXPERIENCE_LEDGER.md`, including the
specific instance where a 16-bar hold above 1504.8 was prematurely treated as an emerging TOC-002
counterexample and then failed after all. The corrective lesson: in this regime, "hasn't failed yet" is
not the same as "won't fail" — wait for genuine resolution (continuation to a fresh reference, or a
closing failure) before classifying, no matter how long a hold has already lasted.

---

## 4. Data quality (REPLAY_DATA_GAP_LEDGER.md)

- **GAP-001 through GAP-026**: recurring class, almost all ~1h to ~90min, clustered around the
  ~21:00-23:00 UTC window on trading days. Attributed (not re-diagnosed each time, per standing
  instruction) to a broker daily-rollover/maintenance window. None had apprenticeship impact — no live
  setup was ever open across a gap.
- **WEEKEND-001 through WEEKEND-006**: expected Friday-close-to-Sunday/Monday-reopen closures
  (~49-50h each). WEEKEND-004 (Fri 03-13 → Sun 03-15) showed a large gap-up-then-fill tied to
  real-world crisis policy response; WEEKEND-005 and WEEKEND-006 reopened cleanly with no gap-jump.
- No genuinely unexplained, non-recurring gap was found this quarter beyond the single legacy GAP-001
  (~5.25h) from before this segment's convention was established.

---

## 5. Honest open questions carried into Q2

1. **Was the final 03-31 break of 1596 driven by genuine continuation of bearish structure, or by
   mechanical quarter-end positioning/rebalancing flow?** Price action alone cannot distinguish these,
   and this checkpoint does not guess. Worth watching whether the break holds or reverses early in Q2.
2. **Does TOC-002's mechanism generalize beyond this specific extended-volatility regime?** Every
   instance this quarter occurred while the market was still inside the same unresolved volatility
   regime that began with the COVID crash. A genuinely calm regime never arrived within Q1 to test
   whether multi-bar holds become reliable once volatility normalizes.
3. **Under what conditions does a fresh range extreme get accepted (TOC-001's counterexample) versus
   faded (TOC-001's 4 confirming instances)?** The frozen candidate's scope is presently too narrow;
   no distinguishing mechanism has been identified yet — this is a real gap in market-reading, not
   papered over.

---

## 6. Standing exclusions honored this quarter

S5, `StrategyCatalog`, live execution, and Market Intelligence tuning were never touched or referenced
as inputs. No Alpha division conclusion was imported or treated as this apprenticeship's own validated
knowledge — TOC-001 and TOC-002 remain `UNVALIDATED_TRADER_OBSERVATION`, pending a separate,
CEO-authorized Alpha audit per the mandate's own handoff mechanism (see `README.md`).

---

## 7. Sources

All content above is grounded in this quarter's actual logged observations:
`lane_a_historical/2020_Q1_H4_LOG.md` (full M15 batch summaries and visible MARKET_THESIS_SNAPSHOTs),
`AI_TRADER_EXPERIENCE_LEDGER.md` (dated entries, self-corrections), `REPLAY_DATA_GAP_LEDGER.md`
(GAP-001..026, WEEKEND-001..006), and `observation_candidates/TOC-001.md` /
`observation_candidates/TOC-002.md` (frozen candidate definitions). No content in this checkpoint was
fabricated or extrapolated beyond what those artifacts record.
