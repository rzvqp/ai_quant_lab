# AI_TRADER_FAILURE_CORPUS_V1

**Mandate:** `AI_TRADER_FAILURE_ENGINEERING_V1`. Q4 unseen throughout. S5/Market Intelligence/
ve_brain untouched. This is Phase 1 (§4-5 of the mandate): a versioned evidence corpus, bucketed,
normalized to only pre-decision-observable fields, nothing synthesized. No filtering, thresholding,
or optimization occurs in this document — that is deliberately deferred to
`AI_TRADER_FAILURE_ENGINEERING_REPORT_V1.md`.

**Source discipline:** buckets A-E are drawn from this repository's own frozen trade/pattern
evidence (`TRADE_EVIDENCE_LOG.md`, `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md`, `2020_Q3_H4_LOG.md`,
`GOLD_BEHAVIOR_MODEL_V1.md`, `AI_TRADER_Q3_INTEGRITY_AUDIT.md`). Bucket F is drawn from the
committed, versioned Alpha-division artifacts identified during the company-wide reconstruction
(`COMPANY_STATE.md`, commit `20a6d10`) — read-only, no new Alpha investigation performed.

---

## Bucket A — AI Trader actual losses (Q1/Q2/Q3)

**Q1: N/A.** Q1 was pure market observation — zero trades taken (`TOC-001`/`TOC-002` observation
candidates only). No loss evidence exists for Q1.

**Q2 losses (7 of the 10 fully-evidenced #57-66 trades):**

| ID | Dir | Entry | Result R | MFE_R | MAE_R | MTF_ALIGNMENT | Playbook | Notes |
|---|---|---|---|---|---|---|---|---|
| #57 | SHORT | 1706.11 | −1.361 | 0.138 | 1.586 | FULLY_ALIGNED | A (pre) | Countertrend-spike exhaustion thesis |
| #59 | SHORT | 1712.008 | −0.046 | 1.586 | 0.267 | FULLY_ALIGNED | A (pre) | Trail-flip; static-baseline comparison −2.225R vs. actual |
| #60 | SHORT | 1707.01 | −1.379 | 0.223 | 1.497 | FULLY_ALIGNED | A (pre) | Close-based fill overshot nominal stop by 2.458pts |
| #61 | SHORT | 1707.856 | −1.150 | 0.695 | 1.280 | FULLY_ALIGNED | A (pre) | Stop tested 4x over 4 bars (0.27-1.63pt margins) before triggering |
| #62 | SHORT | 1680.167 | −1.001 | 1.168 | 1.058 | FULLY_ALIGNED | A (pre) | Stop wick-pierced 3x (closest 0.147pt) before closing through |
| #65 | SHORT | 1724.903 | −1.119 | 1.652 | 1.119 | FULLY_ALIGNED | A-prime | First trade under fixed-SL/TP methodology |
| #66 | SHORT | 1766.952 | −1.398 | 1.626 | 1.467 | PARTIALLY_ALIGNED | A-prime | 0.006pt from full TP before reversing; near-miss narrative |

**Q2 wins, for contrast (not failures, included because §14/§7 require winner comparison):**

| ID | Dir | Entry | Result R | MFE_R | MAE_R | MTF_ALIGNMENT | Playbook |
|---|---|---|---|---|---|---|---|
| #58 | SHORT | 1740.327 | +2.463 | 3.743 | 0.109 | FULLY_ALIGNED | A (pre) |
| #63 | LONG | 1695.555 | +2.306 | 3.163 | 0.506 | TRANSITIONAL | B |
| #64 | SHORT | 1740.496 | +1.443 | 2.467 | 0.209 | PARTIALLY_ALIGNED | A-prime |

**Q3 losses (all 5 Q3 trades):**

| ID | Dir | Entry_time | Result R | MTF_ALIGNMENT | Notes |
|---|---|---|---|---|---|
| Q3-001 | SHORT | 2020-07-01 | −1.084 | PARTIALLY_ALIGNED (H1 EMA crossed, slope not yet FALLING) | Reclaimed within 2 bars (30min) — false continuation |
| Q3-002 | SHORT | 2020-07-07 09:00 | −1.120 | FULLY_ALIGNED (slope confirmed FALLING) | MFE 0.752R, fully reversed |
| Q3-003 | LONG | 2020-07-14 14:45 | −1.427 | PARTIALLY_ALIGNED | TP1 wicked to within 0.36pt, never closed through |
| Q3-004 | SHORT | 2020-07-16 16:30 | −1.352 | PARTIALLY_ALIGNED | Reached ~3.16R unrealized (TP1_ONLY), fully round-tripped |
| Q3-005 | SHORT | 2020-07-22 08:14:59 | −1.123 | **CONFLICTED** (M15 bearish vs. H1/macro bullish, disclosed at entry) | H1/macro reasserted within 2h15m |

**Total realized loss evidence: n=12 losses (7 Q2 + 5 Q3), n=3 wins (all Q2).** Q3 has zero wins.

---

## Bucket B — False positives (armed/triggered, market invalidated the interpretation)

For actual trades, Bucket B is the same population as Bucket A (every realized loss is, by
definition, an interpretation the market invalidated) — not artificially separated. **Additional
false-positive-shaped events that were NOT trades** (interpretation formed, invalidated, but no
capital was risked because execution was frozen or the setup was declined):

- **09-24-1759 / 09-25-0514 whipsaw reclaims** (PATTERN-007, `2020_Q3_H4_LOG.md`): a break-below-EMA
  read as a fresh PATTERN-007 instance reclaimed within a single bar (~15min) and then immediately
  re-broke — the "reclaim resolved" interpretation was invalidated almost immediately, twice in
  direct succession. Not a trade (execution frozen); reported here as a false-positive-shaped
  interpretation event with a real, dated, causally-grounded record.
- **09-30-1015 whipsaw reclaim**: same shape, third instance, same window.

These three are flagged `[LATE-DETECTED / PRE-CLASSIFICATION COMPROMISED]` in
`AI_TRADER_Q3_INTEGRITY_AUDIT.md` §3 — their *detection* was not strictly blind, but their
*market behavior* (reclaim then immediate re-break) is the real, observed event regardless of when
it was noticed. Used here as behavioral evidence, not as PATTERN-007 tally members.

---

## Bucket C — Correct NO_TRADE

Drawn from `AI_TRADER_Q2_VS_Q3_FORENSIC_REVIEW.md` §8 (unchanged, not re-derived):

| Event | Context | What tempted a trade | Why declined | Outcome | Verdict |
|---|---|---|---|---|---|
| 2020-08-10→08-13 | AMBIGUOUS #1, ~69h EMA50 breach through 1907.066 floor | Textbook-looking PATTERN-007 setup, 3 clean priors on record | Standing `NEW_TRADE_ENTRIES = FROZEN` | Eventually reclaimed only after breaching the deepest structural low of the advance by ~36pt | Correct NO_TRADE |
| 2020-08-27 | Jackson Hole news-catalyst SUPPORT instance | Fast (~10.5h), clean-looking reclaim on a major catalyst | Standing freeze; used as a deliberate discriminator test instead | Reclaimed cleanly | Correct NO_TRADE |
| 2020-09-21→09-24 | AMBIGUOUS #7, record 77.25h/1848.842 episode | Single most extreme-looking PATTERN-007 setup of the quarter, n≈24 priors by then | Standing freeze held despite severity | Eventually reclaimed, but set new all-time duration/depth/volume records first | Correct NO_TRADE |

`CORRECT_NO_TRADE_COUNT`: at minimum these 3 explicitly-notable instances, and by extension every
one of the 31 raw PATTERN-007 observations during the freeze window (none was traded). **No exact
per-instance "was this tempting enough to count" denominator exists in the record** — stated
honestly, not fabricated.

---

## Bucket D — False negative / missed opportunity

**None identified.** Per `AI_TRADER_Q2_VS_Q3_FORENSIC_REVIEW.md` §9, applying the causal-only
standard (enough information must have been available before a meaningful part of the move, not
merely visible in retrospect): every freeze-window non-trade is classified
`CORRECT_ABSTENTION_DESPITE_OUTCOME`. No instance of `EXCESSIVE_CAUTION`, `MISSING_CONCEPT`,
`BAD_REGIME_MODEL`, `STALE_CONTEXT`, `TARGET_RESTRICTION`, or `NO_VALID_PLAYBOOK` was found — the
sole reason any trade was declined was the standing mandate itself, applied uniformly, not a
market-reading failure. This bucket is empty by evidence, not by omission.

---

## Bucket E — Pattern counterexamples / ambiguous cases (PATTERN-007)

**Raw tally: n=31** (22 SUPPORT / 1 COUNTEREXAMPLE / 8 AMBIGUOUS). **Strict-prospective: n=23**
(15/1/7) — see `AI_TRADER_Q3_INTEGRITY_AUDIT.md` §3 for the full instance-by-instance derivation of
which 8 instances fail the strict test. Per the mandate, strict-prospective is primary evidence for
Phase 2 (§10); raw is secondary context only.

**The 1 COUNTEREXAMPLE (08-07, NFP-driven):** close decisively below both a structural level and
H1 EMA50 on record volume (8590 at the time), deepened continuously for >2.5 days without a single
reclaim attempt reaching EMA50 within the observed window. Genuine, non-cherry-picked disconfirming
evidence, preserved as-is.

**The 8 AMBIGUOUS instances (raw), ranked by active-market duration:**

| Instance | Active-market duration | Depth (low) | Strict-prospective? |
|---|---|---|---|
| 09-21→09-24 | 77.25h | 1848.842 (record) | YES |
| 08-10→08-13 | 69h | 1871.748 | YES |
| 08-19→08-24 | 60.75h | 1911.586 | YES |
| 09-02→09-07 | 58.75h | not separately logged | YES |
| 08-24→08-26 | 44.5h | 1902.726 | YES |
| 09-07→09-08 | 29.25h | 1906.628 | YES |
| 09-25→09-28 | 25.25h | 1848.801 (nominal 2nd record, noise-level) | YES (genuinely blind, strict 1-bar stepping) |
| 09-17→09-18 | 21.75h | 1932.886 | freeze-detection caveat only (§`AI_TRADER_Q3_INTEGRITY_AUDIT.md` §3.1) — retained in raw, excluded from strict n=23 |

**Full duration distribution (n=30 raw instances with a defined duration, excluding the undefined
COUNTEREXAMPLE):** MIN=0.25h, P25≈1.13h, MEDIAN≈3.63h, P75≈20.44h, P90≈58.95h, MAX=77.25h — see
`AI_TRADER_Q2_VS_Q3_FORENSIC_REVIEW.md` §11.G for the full derivation.

---

## Bucket F — Committed Alpha failure evidence (read-only, versioned)

Every entry cites `SOURCE_REPO`/`SOURCE_PATH`/`SOURCE_COMMIT` per `COMPANY_STATE.md`'s discipline.
**"23 negative quarters" (the chronological campaign) is NOT 23 independent losses of one
strategy** — it is 23 forward-tested quarterly checkpoints of a single walk-forward reader engine;
the experiment structure is preserved below rather than flattened into a trade count.

| Failure family | Mechanism (as stated in the source) | Source |
|---|---|---|
| Directional, chronological (6 methods) | Cost-verified negative, exhausted; **27 quarterly walk-forward checkpoints (2020Q1-2026Q3), reader net-negative in 85% of quarters (mean −0.246R)** — one structure (`BULLISH\|weak_up\|nearZone`) mildly survived ≥3 forward quarters, everything else did not | `data-acq`, `CHRONOLOGICAL_CAMPAIGN_FINAL_REPORT.md`, `a31af7b` |
| ASREJ-1 (mechanized, preregistered) | Quant-falsification FAIL, net −0.206R, cost-rejected on every dimension | `data-acq`, `9121eba`/`99ed83c` |
| WUZ-1 (mechanized, preregistered) | Quant-falsify FAIL, net −0.167R | `data-acq`, `9121eba` |
| CHoCH counter-bias | Exact driftless null (P2R=0.334, both directions) | `data-acq`, `c55992b` |
| Flow-A / E0xx (11 edges) | 11/11 `NOT_SUPPORTED` (false-break/reversal, session, structural hypotheses) | `-alpha-discovery`, `DISCOVERY_CANDIDATE_INDEX.md` |
| VOLTIME (5 families) | Bounded-negative — magnitude predictable, direction symmetric/unmonetizable | `-alpha-automation`, `VOLTIME_LEDGER.md`, `1a96ce3` |
| VOLPATH Phase-1/2 | Whipsaw-dominant, symmetric: **61% recross≥2, 47% double-break, straddle pays twice**; both mechanized candidates (post-classification, straddle) subsequently falsified in Phase-2 | `-alpha-automation`, `VOLPATH_PHASE1_REPORT.md`, `6092c8f` |
| DXY-NDX1 | Non-directional info only; direction regime-conditional, not tradeable | `-alpha-automation`, `ALPHA_DXY_NDX1_FINDING.md`, `fbbfb91` |
| SESSION / SF-3 (4 sub-tests) | All directional session events coinflip | `-alpha-automation`, `SESSION_LEDGER.md`, `adc81b0` |
| CRS1 (**corrected/invalidated state only**, per mandate §4) | `RED_TEAM_PASS` (`57b2883`) subsequently **FAILED** by Statistician (`STAT-CRS1-INDEPENDENT-REVIEW-FDR-001`, `4163382`) — non-causal activation-label alignment / lookahead defect; raw p 3.17e-8 → 0.243 after correction | `ai_quant_lab`, `4163382` |
| `COMP-CONT-L-rr2` | Statistician FAIL — cross-era sign reversal (DEV +0.443 avgR vs. pooled b0+b1 −0.183 avgR) | `ai_quant_lab`, `1fb865d` |
| RANGE V4.4 / V4.4.1 (most recent generalization tests) | Both `GENERALIZATION_NOT_SUPPORTED` on fresh blind-14 tests, despite passing design/implementation audits | `aql_stat_clone`, `dfebe8f`/`8e550ae` |
| RANGE V2 blind protocol (earliest) | `RANGE_V2_BLIND_PROTOCOL_COMPROMISED` | `aql_stat_clone`, `0e1a385` |
| RANGE MB3 blind batch | `MACRO_GENERALIZATION_NOT_SUPPORTED` | `aql_stat_clone`, `3496b73` |
| S20 (`C_09d2245b`) | Statistician/Red-Team FAIL on gate G only (drawdown −23.59R vs. 15R ceiling) — genuinely positive expectancy otherwise | `aql_stat_clone`, `633bd5d` |

---

*This corpus is preserved permanently and is not re-filtered by any downstream document. See
`AI_TRADER_FAILURE_ENGINEERING_REPORT_V1.md` for taxonomy and common-denominator analysis, and
`AI_TRADER_NEGATION_LIBRARY_V1.md` for candidate negation rules derived from it.*
