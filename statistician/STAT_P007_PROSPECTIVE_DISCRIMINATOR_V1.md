# STAT_P007_PROSPECTIVE_DISCRIMINATOR_FALSIFICATION_V1

**Mandate:** `P007 PROSPECTIVE DISCRIMINATOR FALSIFICATION V1` — formalize on Q4 only, freeze, test on
unseen Q1 2021. Behavioural-discriminator experiment only.
**Division:** Statistician. **Date:** 2026-09-02.
**Code:** `statistician/p007/` — `build.py`, `q4model.py`, `trigtime.py`, `freeze.py`.

## VERDICT

```
P007_PROSPECTIVE_DISCRIMINATOR_V1_COMPLETE = NO — the Q1 arm cannot be executed
Q4_POPULATION_REPRODUCED = YES  (89 / 24 SUPPORT / 65 REJECTED, exact)

VERDICT = P007_DISCRIMINATOR_WEAK / INCONCLUSIVE
          (INCONCLUSIVE on the prospective axis — the test is not runnable;
           WEAK on the Q4 in-sample axis, and weaker than the apprenticeship believed)

P007_TRADEABLE = NO
READY_FOR_TRADING_RESEARCH = NO
```

**The Q1 2021 prospective test is blocked, on three independent grounds, and I will not manufacture a
result.** Everything the mandate asks for on the Q4 side was executed, and it produced two findings that
change the picture regardless of Q1.

---

## 1 — Q4 POPULATION REPRODUCED (§3)

Parsed independently from `AI_TRADER_Q4_PATTERN_LEDGER.md`:

```
entries          : 89   (ids Q4-P007-001 .. Q4-P007-089, contiguous, none missing)
SUPPORT          : 24
REJECTED         : 65
unlabelled       : 0
TRIGGER_BAR field: 89/89 present     RESOLUTION_BAR field: 87/89
```

Matches the CEO's frozen figures exactly. `Q4_POPULATION_REPRODUCED = YES`.

**But the population is a curated registry, not a mechanical set — and that matters for Q1.** Running the
frozen `p007_detector` over the sealed Q4 fixture (7,932 rows, 5,932 Q4 bars) produces **121 TRIGGERs**, not
89. Only **25 of the 89 ledger trigger bars coincide exactly** with a detector trigger; 63 fall within ±2
bars. The detector is deliberately over-inclusive by design, and the 89 entries are AI Trader's own
judgement about which breaks were P007-shaped enough to register. **There is no mechanical rule that
regenerates the 89.**

---

## 2 — TIMING SEMANTICS (§5) — the finding the mandate was right to call critical

```
EARLIEST_CAUSAL_CLASSIFICATION_TIME = AT_RECLAIM (episode resolution)
```

The round-trip quantity, in the ledger's own terms, is *"a ~79% retracement of the full decline"* — i.e.

```
round_trip = (reclaim_close − deepest_low_of_episode) / (close_before_trigger − deepest_low_of_episode)
```

It needs the **deepest low of the whole episode** and the **reclaim close**. Neither exists until the
episode ends — which is the same moment the SUPPORT/REJECTED label is assigned. **The primary lesson is
therefore a resolution-time description, not a forward-looking signal**, and no classifier built on it can
be prospective in the sense the mandate's core question asks for.

| component | earliest available |
|---|---|
| trigger-bar depth, range, body, volume | **AT_TRIGGER** |
| volume persistence across the episode | DURING_EPISODE (complete only at resolution) |
| fresh extreme of the episode | DURING_EPISODE (complete only at resolution) |
| **round-trip completeness** | **AT_RECLAIM** |
| episode duration, total decline | **AT_RECLAIM** |

---

## 3 — DOES THE LESSON SURVIVE MECHANICAL FORMALISATION? (§4)

Computed from bars for the 83 of 89 episodes with a resolution bar (22 SUPPORT / 61 REJECTED). Separation
measured by AUC, the right statistic for a 24/65 split:

| quantity | SUPPORT median | REJECTED median | AUC | available |
|---|---|---|---|---|
| **episode duration (bars)** | 83.5 | 4.0 | **0.931** | AT_RECLAIM |
| volume isolation (peak/mean) | 4.31 | 1.38 | **0.917** | AT_RECLAIM |
| total decline (pt) | 18.69 | 2.43 | **0.908** | AT_RECLAIM |
| fresh extreme | 1.00 | 0.00 | 0.862 | DURING_EPISODE |
| **trigger-bar volume, 3-bar (AT_TRIGGER)** | 2.13 | 0.86 | **0.819** | **AT_TRIGGER** |
| trigger-bar range / ATR (AT_TRIGGER) | 2.68 | 1.10 | 0.795 | **AT_TRIGGER** |
| volume persistence | 0.221 | 0.067 | 0.672 | DURING_EPISODE |
| **round-trip completeness** | **0.881** | **1.291** | **0.309 (= 0.691 inverted)** | AT_RECLAIM |

**The lesson's direction is right — SUPPORT episodes do retrace less (0.881 vs 1.291). But round-trip is the
WEAKEST of the components AI Trader identified, not the strongest.** The apprenticeship ranked it primary
and called volume and fresh-extreme "materially weaker"; measured mechanically, that ranking inverts.

**And the two strongest separators are label-definitional.** A REJECTED episode is one AI Trader judged a
*marginal EMA touch*; a SUPPORT episode is a *genuine sharp break*. Duration (0.931) and decline magnitude
(0.908) are close to restatements of that judgement rather than predictions of it. This is the tautology
risk in the lesson, and it is why in-sample separation here cannot be taken at face value.

---

## 4 — Q4 MODEL SELECTION (§6, §7, §8, §9)

Bounded, interpretable search; **every alternative considered is reported**, per §6.

**A. `ROUND_TRIP_ONLY`** — `round_trip < th → SUPPORT`

| th | precision | recall | specificity | balanced accuracy |
|---|---|---|---|---|
| 0.80 | 0.500 | 0.409 | 0.852 | 0.631 |
| 0.85 | 0.526 | 0.455 | 0.852 | 0.654 |
| 0.90 | 0.522 | 0.545 | 0.820 | 0.683 |
| 0.95 | 0.480 | 0.545 | 0.787 | 0.666 |
| **1.00** | 0.455 | 0.682 | 0.705 | **0.693** |

**B. `+ VOLUME_PERSISTENCE`** (§7): best `rt<0.90 & vol_sustain>0.10` → **0.717**, incremental **+0.024**.

**C. `+ FRESH_EXTREME`** (§8): **0.719**, incremental **+0.002** — negligible. **Dropped for parsimony**, as
§8 instructs.

**D. `AT_TRIGGER_VOLUME_ONLY`** — `t_vol_rel_3 > th → SUPPORT`, the only genuinely prospective option:

| th | precision | recall | specificity | balanced accuracy |
|---|---|---|---|---|
| 1.2 | 0.474 | 0.818 | 0.672 | 0.745 |
| 1.5 | 0.533 | 0.727 | 0.770 | 0.749 |
| **1.8** | 0.714 | 0.682 | 0.902 | **0.792** |
| 2.0 | 0.765 | 0.591 | 0.934 | 0.763 |

```
BASELINE_BALANCED_ACCURACY = 0.500   (ALWAYS_REJECTED; its raw accuracy is 0.735 — which is exactly
                                      why raw accuracy is not used, per §9)

ROUND_TRIP_INCREMENTAL_VALUE    = +0.193 balanced accuracy over baseline
VOLUME_INCREMENTAL_VALUE        = +0.024 over round-trip alone
FRESH_EXTREME_INCREMENTAL_VALUE = +0.002 over round-trip + volume  (NEGLIGIBLE — dropped)
```

**The mandate's own §7/§8 instruction — "do not assume the more complicated version is better" — is
vindicated: adding two components to round-trip buys +0.026 balanced accuracy in total, while a single
trigger-time volume rule reaches 0.792 on its own.**

---

## 5 — FROZEN SPEC (§10)

```
SPEC_HASH_PRE_Q1 = 0a25ae24edfe5a27cc5d58a5841fbfd4ac1fe6abf3ce5aa78dd580de87946590

PRIMARY_DISCRIMINATOR = ROUND_TRIP_ONLY: round_trip < 1.00 -> SUPPORT, else REJECTED
  round_trip = (reclaim_close − deepest_low) / (close_before_trigger − deepest_low)
  EARLIEST_CAUSAL_CLASSIFICATION_TIME = AT_RECLAIM
  Q4 balanced accuracy 0.693

SECONDARY_1 = ROUND_TRIP + VOLUME (rt<0.90 & vol_sustain>0.10), AT_RECLAIM, Q4 balacc 0.717
SECONDARY_2 = AT_TRIGGER_VOLUME_ONLY (t_vol_rel_3 > 1.8), AT_TRIGGER,  Q4 balacc 0.792
```

The spec was frozen and hashed **before** any attempt to look at Q1, exactly as §10 requires. Both
secondaries were frozen at the same moment and are marked SECONDARY, so §13's prohibition on Q1-driven
model selection is satisfied in advance — whichever way a future Q1 test goes.

---

## 6 — WHY THE Q1 2021 TEST CANNOT BE RUN (§11)

Three independent blockers, any one of which is sufficient:

1. **No Q1 ground truth exists, and it cannot legitimately be created.** SUPPORT/REJECTED is a
   *reasoning-layer judgement* recorded episode-by-episode during apprenticeship — e.g.
   *"STATUS REJECTED — not a genuine PATTERN-007 instance"*. A lab-wide search returns **zero** Q1-2021
   P007 labels. I cannot define the labels myself (I would then be scoring a discriminator against my own
   invented target — circular), and §1 forbids AI Trader from touching Q1. Labels generated after this
   experiment would not be independent of it in any case.
2. **No Q1 episode population exists.** The 89 are curated, and the frozen detector does not reproduce them
   (121 vs 89; 25 exact matches). Running the detector on Q1 yields a *different kind of object* — an
   over-inclusive trigger set — so its classifications would not be comparable to the Q4 population the
   discriminator was fitted on.
3. **No Q1 sealed replay fixture exists.** The fixtures end at `Q4_SEALED_1_5932.csv` = 2020-12-31 21:45
   UTC. Governed M15 bars for Q1 2021 do exist (5,772 bars, 2021-01-03 → 2021-03-31), so blocker 3 alone
   would be surmountable — but 1 and 2 are not.

```
Q1_TOTAL = NOT_EXECUTABLE     Q1_SUPPORT = NOT_EXECUTABLE     Q1_REJECTED = NOT_EXECUTABLE
CONFUSION_MATRIX / SUPPORT_PRECISION / SUPPORT_RECALL / SPECIFICITY / BALANCED_ACCURACY = NOT_EXECUTABLE
```

Reporting these as anything other than not-executable would require inventing the target variable. §14's
failure analysis is likewise not applicable — there are no Q1 errors to inspect, because there is no Q1
scoring.

---

## 7 — WHAT THIS DOES SETTLE

The mandate's core question is *"can P007 be discriminated prospectively?"* The Q1 arm is blocked, but the
Q4 work answers a sharper version of it:

- **A prospective discriminator does exist in principle**: trigger-bar volume intensity reaches balanced
  accuracy **0.792** on Q4 using only information available *at the trigger*, against a 0.500 baseline —
  materially better than the round-trip rule the apprenticeship nominated as primary (0.693), which is not
  prospective at all.
- **But that number cannot be trusted in-sample**, because SUPPORT is partly *defined* as a
  "volume-confirmed" break. A volume rule scoring well against a volume-inflected label is close to
  circular. **This is precisely the confound an out-of-sample test would resolve — and it is the reason the
  Q1 blocker matters rather than being a formality.**
- **The apprenticeship's component ranking is inverted by measurement.** Round-trip is the weakest of the
  identified components and the least available; volume is the strongest and the most available. That is a
  concrete, evidence-based correction to `APPRENTICESHIP_FINAL_LEVEL = PROSPECTIVE_DISCRIMINATION_LEARNED`,
  and it does not require Q1 to establish.

**What would unblock a real test.** Q1 2021 P007 episodes would have to be registered and labelled by the
same process that produced the Q4 registry, **blind to this frozen spec and to its predictions**, before any
scoring. That is an apprenticeship-side task under CEO control, not something this division can produce.
The spec hash above exists so that, if the CEO authorises it, the test can be run without any suspicion of
retrofitting.

---

## 8 — FINAL

```
P007_PROSPECTIVE_DISCRIMINATOR_V1_COMPLETE = NO (Q1 arm not executable)
Q4_POPULATION_REPRODUCED = YES
Q4_TOTAL = 89   Q4_SUPPORT = 24   Q4_REJECTED = 65

PRIMARY_DISCRIMINATOR = ROUND_TRIP_ONLY (round_trip < 1.00 -> SUPPORT), Q4 balanced accuracy 0.693
EARLIEST_CAUSAL_CLASSIFICATION_TIME = AT_RECLAIM
SPEC_HASH_PRE_Q1 = 0a25ae24edfe5a27cc5d58a5841fbfd4ac1fe6abf3ce5aa78dd580de87946590

Q1_TOTAL / Q1_SUPPORT / Q1_REJECTED = NOT_EXECUTABLE (no ground truth, no curated population, no fixture)
SUPPORT_PRECISION / SUPPORT_RECALL / SPECIFICITY / BALANCED_ACCURACY = NOT_EXECUTABLE
BASELINE_BALANCED_ACCURACY = 0.500

ROUND_TRIP_INCREMENTAL_VALUE    = +0.193 over baseline (Q4 in-sample)
VOLUME_INCREMENTAL_VALUE        = +0.024 over round-trip
FRESH_EXTREME_INCREMENTAL_VALUE = +0.002 over round-trip + volume — dropped for parsimony

VERDICT = P007_DISCRIMINATOR_WEAK / INCONCLUSIVE
P007_TRADEABLE = NO
READY_FOR_TRADING_RESEARCH = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

No entry expectancy, PnL, target, stop or sizing was computed. PATTERN-007 was not modified and is not
promoted. AI Trader was not consulted and Q1 2021 outcomes were never opened. Not touched: **S5, AI Trader,
the P007 standing definition, MGMT-004, MT5, StrategyCatalog.** Alpha's active Attribution V2 work was not
interfered with.
