# RED TEAM — PHASE 1 REPORT
### Adversarial analysis of the complete Discovery Candidate portfolio (DC-0001 … DC-0018)
**Date:** 2026-07-23 · **Reviewer:** Red Team · **Mandate:** CEO — Red Team Phase 1
**Sources (read-only):** `ai_quant_lab-alpha-automation`, on-disk state read 2026-07-23 (last commit `005f837`; index/handoff/session-state working tree is ahead of that commit) — 18 × `candidate_v1.md`, 16 × addenda, `DISCOVERY_CANDIDATE_INDEX.md`, `HANDOFF_LOG.md`, `OBSERVATION_REGISTRY.md`, `SESSION_STATE.md`, `metadata_v1.json`.

**Snapshot integrity check (performed at report close):** Alpha is actively working — `SESSION_STATE.md` (+972 lines), `DISCOVERY_CANDIDATE_INDEX.md`, `HANDOFF_LOG.md` and `config/alpha_automation.json` carry uncommitted changes, and a second working area (`alpha_instance_2/`) has appeared. **Critically, no `candidate_v1.md` and no addendum was modified**, and no candidate beyond DC-0018 exists. The frozen documents this report analyses are therefore intact and the analysis is bound to them. Flagged because Red Team reviews frozen targets: if Alpha's live session produces DC-0019+ or new addenda, this report covers the 18/16 set only.
**Nothing was modified.** No Discovery Candidate, addendum, SESSION_STATE, or Knowledge Base entry was touched. No confidence changed. No new hypothesis created. No statistics computed. No implementation. No promotion.

> **Posture for Phase 1 (per CEO):** attempt to *destroy*. Each hypothesis was approached as something to be falsified, not confirmed. Where a candidate survived, it survived an attempt to break it — that is not endorsement.

---

## 0. HEADLINE

The portfolio is honestly produced. Alpha's self-falsification is genuinely unusual — several addenda exist **only** to record evidence against their own parent candidate (DC-0008-D, DC-0009-D, DC-0010-A, DC-0017-A/B). That is a real methodological strength and it is what made this analysis possible.

But the portfolio does not contain 18 phenomena. Adversarially, it contains **roughly four or five questions**, one of which (a single unmeasured ratio) silently gates seven candidates, and one already-promoted lab primitive (volatility clustering + hour-of-day profile) plausibly generates the appearance of about half the portfolio without any candidate testing against it.

**Classification: A = 3 · B = 11 · C = 4.**

---

## 1. PORTFOLIO MAP

| Group | Candidates | Underlying question |
|---|---|---|
| **I — Candle construction / microstructure** | DC-0008 *(root)*, 0013, 0014, 0015, 0016, 0017, 0018, 0011, 0012, 0006, 0010 | How is a large move built at M1, and does construction predict aftermath? |
| **II — Level / structure memory** | DC-0004, 0005, 0007, 0009 | Does prior interaction with a level carry information? |
| **III — Compression & scale** | DC-0002, 0003 | Does compression resolution depend on scale relative to noise? |
| **IV — Bar velocity** | DC-0001 | Does a single bar's pace carry direction-independent information? |

Eleven of eighteen candidates sit in Group I. That concentration is the portfolio's central structural problem.

---

## 2. PORTFOLIO-LEVEL FINDINGS

### F1 — Six candidates reduce to one construction plus a post-hoc descriptor
DC-0013, 0014, 0015, 0016, 0017, 0018 each state explicitly that their construction is *the same as DC-0008* ("sustained, distributed multi-minute volume"). What distinguishes them is entirely descriptive and entirely read off *after* the event: clock time (NY midday / 00:00 UTC / NY afternoon / early Asia / 12:30 / 14:00), duration (4 / 5 / 11 / 6–7 / 1+4 / 1+6 candles), magnitude (43 / 35 / 31 / 47 / 33 / 47.8 pt), and ending shape.

No descriptor was specified in advance. None was shown to be the *operative* variable. Six single instances of one construction were promoted to six candidates because each differed from the last in some noticed dimension. **The reduction is: one phenomenon (DC-0008's sustained construction), observed six more times.**

*(Recording a reduction is not consolidation. Per CEO ruling, structure is untouched and consolidation is reserved for Statistician + Reasoning Engine.)*

### F2 — The family is unfalsifiable as a set: it exhausts the outcome space
After a large sustained expansion, the portfolio documents:

| Aftermath | Candidate |
|---|---|
| Consolidation near highs | DC-0013 |
| Sharp reversal | DC-0014, DC-0016 |
| Modest pullback | DC-0015 |
| Hold / drift up | DC-0017 (then contradicted by its own Addendum B) |
| Sustained decline the other way | DC-0018 |
| Sideways at the new level | DC-0008 Addendum B |
| Extended two-sided chop, full giveback | DC-0017 Addendum B |

Every possible outcome is catalogued, each as a separate candidate. **There is no observation of a large sustained expansion that could contradict this family.** Individually each document is careful and descriptive; collectively they make no prediction and cannot be wrong. That is a falsifiability failure at the portfolio level, invisible from inside any single document.

### F3 — One unmeasured ratio gates seven candidates *(highest-value gap in the portfolio)*
DC-0008 defines the distinction operationally — *(largest M1 or M5 volume share) ÷ (M15 total)*, plus whether volume returns to baseline before close — but **specifies no threshold**. "Sustained" vs "concentrated" is therefore still an eyeball judgement, not a decidable classification.

Consequence: every family claim of the form *"same construction as DC-0008"* (DC-0013, 0014, 0015, 0016, 0017, 0018, and DC-0010, DC-0011-B) is currently **unverifiable**, because the class it appeals to has no boundary.

The decisive question is cheap and purely a counting exercise: **compute the distribution of that ratio across all large M15 candles. If it is unimodal/continuous, the two "construction types" are an artifact of visual classification and a large part of Group I collapses.** Nothing else in the portfolio offers this much falsifying leverage for this little work.

### F4 — The strongest alternative explanation is the lab's own promoted primitive
The Volatility primitive is already **PROMOTED** in this laboratory (clustering acf1 ≈ +0.53; daily-range persistence ≈ +0.26; hour-of-day profile ≈ 4.3× peak/trough — cited by DC-0002/0003/0004's own Library Concept Scans). If volatility clusters and has a strong hour-of-day shape, it predicts, with no new mechanism:

- large moves arriving in temporally clustered bursts → "sustained multi-minute participation" is simply what a high-volatility regime looks like at M1 resolution (**DC-0008 and family**);
- elevated volume decaying over hours rather than snapping back → **DC-0017 Addendum A** (4h15m decay) and **DC-0010 Addendum A** (whole session elevated) are textbook clustering;
- expansions persisting 4 / 7 / 11 candles → persistence of the volatility state, not six distinct phenomena (**DC-0013/0015/0016**);
- activity concentrated at particular clock hours → **DC-0010, DC-0012, DC-0017's 12:30 series**.

**Not one candidate in Group I is tested against a volatility-clustering / hour-profile null.** This is the single most damaging unexcluded alternative in the portfolio, and it is not speculative — it is the lab's own ratified primitive.

### F5 — There is no denominator anywhere
Every discretionary candidate was found by stepping through replay and stopping when something looked notable. The stopping rule is not recorded, and **no candidate reports how many comparable non-events were passed over.** DC-0005 and DC-0006 admit this explicitly ("no count of levels tested three times that produced nothing — almost certainly the majority"; "no counting of the (probably many) high-volume candles that did extend").

Therefore every frequency-flavoured phrase in the portfolio — *"frequently fail to extend"*, *"consistently quiet hour"*, *"repeatedly"*, *"never gave way"* — is currently uncheckable. This affects Group I and Group II across the board.

### F6 — All volume claims rest on a broker proxy
The feed is OANDA tick/broker volume, not exchange volume. Only DC-0006 notes this, in one line. The majority of the portfolio is volume-based, and several claims are *hour-conditioned*. If the proxy's relationship to true participation varies by session — which is the normal case — then hour-conditioned volume claims are partly measuring the broker feed rather than the market. Unexcluded portfolio-wide.

### F7 — The level-memory thread is internally inconsistent
Group II asserts, across four documents: a level matters more on the third touch (DC-0005); a level that held three times stopped mattering immediately (DC-0007); a band held nine touches then broke (DC-0009); a broken level held as support on its first retest and **failed on its second, ~21h later** (DC-0009 Addendum D). Taken together the thread supports no consistent statement about level memory. DC-0009-D is a direct, Alpha-filed refutation of the simplest reading.

### F8 — DC-0002 is a special case of DC-0003
DC-0003 states it itself: the HTF half of its claim *is* DC-0002's subject, and the two are "complementary halves of one scale question." DC-0003 is the general statement (resolution depends on whether the boundary sits inside or outside prevailing noise); DC-0002 is its higher-timeframe instance. Recorded as a reduction, not actioned.

### F9 — The "unusual hour" thread is refuted by Alpha's own registry
DC-0010 and DC-0012 both rest on 00:00–01:00 UTC being anomalous. `OBSERVATION_REGISTRY.md` subsequently records ~12 instances of that hour — extreme-directional, extreme-absorption, several fully ordinary, one moderate-directional — and concludes in Alpha's own words that **"no consistent single characterization of this hour holds across instances."** DC-0010's own Addendum A further shows the entire 2025-08-07 session ran hot, not the hour. The hour-specificity of both candidates is refuted by material already inside the laboratory.

---

## 3. CONTRADICTIONS

### 3.1 Cross-candidate

| # | Contradiction | Evidence |
|---|---|---|
| X1 | **Extreme volume fails to extend** (DC-0006) vs **extreme volume extended** | DC-0008's 12:30 candle (24,005) extended to new highs — DC-0008 notes the contrast itself; DC-0013 (29,674) extended 4 candles; DC-0017 (30,975) held/drifted up. DC-0018 (36,798) failed. Extreme-volume candles both extend and fail across the portfolio. |
| X2 | **Sweep aftermath is not one thing** | DC-0011: sweep → extends past pre-sweep range. DC-0007: cluster swept, reclaimed, level then irrelevant. DC-0018: spike to fresh high → complete failure → sustained decline. DC-0008-B: concentration → sideways consolidation ("a third aftermath type"). Four incompatible aftermaths, all documented. |
| X3 | **Level memory** | DC-0005 (third touch matters) vs DC-0007 (level stopped mattering after three) vs DC-0009-C/D (support held on retest 1, failed on retest 2). |
| X4 | **12:30 UTC has a characteristic behaviour** | DC-0017 (impulse → hold) vs DC-0008 Addenda B/C/D: five 12:30 instances, five different outcomes (sustained/extend, concentrated/consolidate, ordinary/nothing, concentrated-down/choppy, sustained again) — "the only common thread being the clock time itself." |
| X5 | **NFP is the driver** (DC-0008 §3, DC-0017) vs **DC-0008 Addendum D** | Both Fridays showed sustained construction, including a non-NFP Friday → the association, if any, runs with day-of-week or something else, not NFP. |
| X6 | **00:00–01:00 UTC is anomalous** (DC-0010, DC-0012) vs `OBSERVATION_REGISTRY` | ~12 instances, no consistent characterization; several fully ordinary. |

### 3.2 Internal (within a single submission)

| # | Candidate | Self-contradiction |
|---|---|---|
| I1 | **DC-0017** | Headline is "holds gains across four candles without reversing or extending." Addendum A: it actually drifted higher for ~4h15m (not a hold). Addendum B: a comparable-magnitude 12:30 print gave back the entire move in two-sided chop. **The stated hypothesis is contradicted twice by its own package.** |
| I2 | **DC-0010** | Headline is that *this hour* broke from baseline. Addendum A shows the whole session ran 2–3× baseline with a second spike at 05:00–06:00 — an all-day phenomenon, not an hour. |
| I3 | **DC-0009** | Addendum C reads as "old resistance now acts as support"; Addendum D records the same band failing on the next retest and explicitly says this "directly contradicts a naive reading of Addendum C." |
| I4 | **DC-0006** | Confidence "Very low" because the relation **inverted within 24 hours** — the counterexample is inside the submission. |
| I5 | **DC-0005** | One of only two supporting sequences is impure: the third-test displacement "died inside the range" — the difference was "in character, not in follow-through." |
| I6 | **DC-0008** | §3 offers the NFP timing association; Addendum A then documents the identical construction at 19:30 UTC with no release slot. (Filed deliberately by Alpha — a strength, but it removes the stated context.) |

---

## 4. OVERLAPS — candidates describing the same phenomenon

| Overlap | Candidates | Nature |
|---|---|---|
| **O1** | DC-0013, 0014, 0015, 0016, 0017, 0018 → **DC-0008** | Same construction; differ only by post-hoc descriptors (F1). |
| **O2** | DC-0002 → **DC-0003** | DC-0002 is the HTF special case of DC-0003's scale statement; DC-0003 says so (F8). |
| **O3** | DC-0005 ↔ DC-0009 (↔ DC-0007) | All are "does interaction count with a level carry information" at different counts (2→3, 7→9, 3-then-swept). DC-0009 leaves this identity explicitly open. |
| **O4** | DC-0010 ↔ DC-0012 | Same hour, opposite sign, both n=1; DC-0012 explicitly frames itself as the second break of that hour's baseline. |
| **O5** | DC-0011 ↔ DC-0007 | Both are sweep-and-reclaim of a level; differ only in whether price then exceeded the pre-sweep range. |
| **O6** | DC-0006 ↔ DC-0018 | Both are "extreme volume candle fails"; DC-0018 is the same claim plus a multi-candle continuation, and cites DC-0006 as its closest precedent. |
| **O7** | DC-0017 → DC-0008's 12:30 series | DC-0008 Addenda B/C/D already own the 12:30 UTC question with five instances; DC-0017 is a sixth. |

**Effective distinct questions in the portfolio: about five** — (1) does construction predict aftermath, (2) does interaction count with a level carry information, (3) does compression resolution depend on scale, (4) does bar velocity carry direction-independent information, (5) is the NY sweep-reject reversion real out-of-sample.

---

## 5. IMPLICIT ASSUMPTIONS (portfolio-wide, unstated and load-bearing)

1. **That "sustained" and "concentrated" are two categories rather than a continuum** — no threshold, no distribution (F3).
2. **That the events noticed are representative of the events that occurred** — no denominator, unrecorded stopping rule (F5).
3. **That broker tick volume tracks participation uniformly across sessions** (F6).
4. **That a clock hour is a mechanism** rather than a label for whatever is scheduled or liquid at that time (DC-0010, 0012, 0017).
5. **That volatility clustering is not already producing what is being observed** (F4) — nowhere considered in Group I.
6. **That one replay pass over one instrument (XAUUSD/OANDA), in-sample, generalises** — stated per-candidate as "one instrument," never treated as a portfolio-wide limit.
7. **That descriptors noticed after the fact (duration, ending shape) are the operative variables** (F1/F2).

---

## 6. PER-CANDIDATE ANALYSIS

> Format: **Hypothesis (reconstructed) · Addenda · Internal contradiction · Cross-DC · Alternative · Reducible to · Missing evidence · Falsifier · Class**

### DC-0001 — Single-bar velocity outlier → gradual continuation
**Hypothesis:** a bar moving many times its neighbours' pace is followed by a distinctly slower multi-bar sequence, independent of direction. **Addenda:** none. **Internal:** none; explicitly a question. **Cross-DC:** isolated — the only Group IV member; no other candidate addresses pace. **Alternative (unexcluded):** an outsized bar followed by smaller bars is the generic signature of range mean-reversion and of volatility decay after a shock — picking the fastest bar guarantees slower neighbours (regression to the mean). **Reducible to:** the Volatility primitive's clustering/decay behaviour. **Missing:** any measurement at all (pace judged by eye), and the count of bars showing a velocity gap that were *not* followed by deceleration. **Falsifier:** measure the velocity-gap population; if post-gap deceleration matches what shuffled/matched bars produce, the candidate dies. **Class: B** — clear, cheap to test, but two eye-selected instances and no denominator.

### DC-0002 — HTF compression resolves with the H4 bias
**Hypothesis:** an H4 compression phase terminates in expansion in the direction of the prevailing H4 bias. **Addenda:** none (Library Concept Scan folded inline). **Internal:** none — confound disclosed. **Cross-DC:** subsumed by DC-0003 (O2). **Alternative (Alpha-named, serious):** K05 long-beta — 3 of 4 resolved up inside the 2023–25 gold bull; "resolves with the H4 bias" is operationally "goes up." Also K03 overlap (trend-efficiency gating, already weak OOS). **Reducible to:** DC-0003's scale statement. **Missing:** a formal definition of "compression" (Alpha states trend-efficiency is only *proposed*); bearish and lateral-H4 cases; a direction/beta-matched null. **Falsifier:** Alpha's own — if lateral-H4 compressions still resolve upward systematically, it is long beta and the candidate dies. **Class: B** — a statistician cannot yet select the events, because the event is undefined. One pre-registered instance (C4) is a genuine strength; it is not enough at n=4 with the confound.

### DC-0003 — Scale inversion (micro coils vs HTF compressions resolve oppositely)
**Hypothesis:** a boundary inside prevailing noise amplitude carries no information (marginal break fails); a boundary outside it requires genuine displacement (break holds). **Addenda:** none. **Internal:** none; self-labels its own key claim as untested. **Cross-DC:** subsumes DC-0002; explains part of DC-0006 (three of DC-0006's instances are micro coils where failure is already predicted). **Alternative (Alpha-named):** both micro cases sat in thin Asian tape — the effect may be *liquidity*, not *scale*; the two are entangled and unseparated. **Reducible to:** nothing more general in the portfolio; it is itself the generalisation. **Missing:** where the class boundary lies (Alpha proposes a multiple of prevailing ATR, untested); micro-C instances outside thin tape. **Falsifier:** re-run OBS-0017's 384 swing-high exceedances with scale separation — **if the pooled null does not decompose, the candidate dies.** **Class: A** — this is a specific, pre-stated, falsifiable prediction about an existing dataset, implementable without new judgement calls, whose negative result is unambiguous. The scale/liquidity entanglement is a covariate for that test, not a blocker.

### DC-0004 — NY-session prior-day-high sweep-reject → reversion
**Hypothesis:** a first-bar sweep-reject of the prior-day high is followed by reversion, conditional on the NY session; other sessions show no effect or the opposite sign. **Addenda:** none. **Internal:** none — every weakness is foregrounded. **Cross-DC:** the only Group II member with a defined population; related to DC-0005/0007/0009 by subject but methodologically separate. **Alternative (Alpha-named, decisive):** multiple testing / selection — the cell was chosen after inspecting ~12 cells; p = 0.021 fails the Bonferroni threshold of 0.0083; both per-half CIs include zero. K04 records that calendar-like conditioning previously failed to replicate OOS. **Reducible to:** the Volatility hour-of-day profile supplies the conditioning variable (NY = peak participation) — the session effect may be a volatility-regime effect rather than a level effect. **Missing:** out-of-sample confirmation; nothing else. **Falsifier:** the reserved post-2025-10-23 holdout. **Class: A** — precisely specified (level, event, session, horizon, baseline), already matched-null tested, sign-stable across halves, uniquely distinguished among six cells, with one clean pre-identified decisive test. It must enter validation **as a hypothesis, not as a result** — the selection effect means the in-sample p carries no evidential weight.

### DC-0005 — The third test of a level differs from the first two
**Hypothesis:** the third interaction with a level resolves differently from the first two. **Addenda:** none. **Internal:** I5 — one of two supporting cases produced displacement that "died inside the range." **Cross-DC:** X3; overlaps DC-0009 and DC-0007 (O3). **Alternative (Alpha-named):** it is folk knowledge ("third time breaks"), which raises the prior on confirmation bias; and there is no count of third tests that produced nothing — "almost certainly the majority." **Reducible to:** one general question with DC-0009/DC-0007 — does interaction count carry information. **Missing:** the base rate; an outcome distribution by interaction index. **Falsifier:** tabulate outcomes by touch index over all ≥3-touch levels; if index 3 is indistinguishable from 1 and 2, it dies. **Class: B.**

### DC-0006 — Extreme relative volume candles frequently fail to extend
**Hypothesis:** the highest-relative-volume candle of a local sequence tends not to continue; continuation arrives on ordinary volume. **Addenda:** none. **Internal:** I4 — the relation **inverted within 24 hours** of being noticed, inside the submission. **Cross-DC:** **X1 — directly contradicted by the portfolio's own evidence:** DC-0008 (24,005 → extended, contrast noted by Alpha), DC-0013 (29,674 → extended 4 candles), DC-0017 (30,975 → held/drifted up). Supported only by DC-0018. **Alternative (Alpha-named):** three of ~five instances are micro-scale coils where **DC-0003 already predicts failure** — the volume variable may be entirely redundant with scale; plus tick/broker volume (F6). **Reducible to:** DC-0003 (scale) for the coil instances; DC-0008's ratio work for the rest. **Missing:** the count of high-volume candles that *did* extend (absent by Alpha's own admission); scale-controlled comparison. **Falsifier:** already effectively met — the portfolio contains at least three extreme-volume candles that extended, plus a next-day inversion. **Class: C — REJECT.** The claim as stated is falsified by evidence already inside the laboratory, is confounded with an existing candidate, and has no denominator. *Rejecting this claim does not close the underlying question (does volume predict continuation) — that question is properly carried by DC-0008's ratio measurement, where it can be answered with a defined population.*

### DC-0007 — Equal lows swept and reclaimed within one candle
**Hypothesis:** a cluster of ≥3 near-equal lows is taken and reclaimed inside a single candle, after which the level ceases to matter. **Addenda:** none. **Internal:** none. **Cross-DC:** X2, X3; overlaps DC-0011 (O5) and the DC-0005/0009 level thread (O3). **Alternative:** at n=1, with no volume signature, indistinguishable from ordinary intrabar noise; a ~2.4pt excursion against 3–7pt local ranges is within noise (DC-0003's own criterion). **Reducible to:** DC-0003 (excursion inside noise amplitude) and the level-count question. **Missing:** a count of ≥3-equal-low clusters and their sweep/reclaim outcomes vs a base rate. **Falsifier:** enumerate such clusters; if same-candle sweep-reclaim is common and the level's subsequent irrelevance is the norm, there is no phenomenon. **Class: B.**

### DC-0008 — Sustained multi-minute vs single-minute construction *(portfolio root)*
**Hypothesis:** a large M15 candle is built either from sustained multi-minute participation or from a single dominant minute; the M15 bar alone cannot distinguish them; the two may have different aftermaths. **Addenda:** A (sustained construction with no news slot), B (12:30 Tuesday, concentrated → consolidation), C (12:30 Thursday, concentrated-down → choppy incomplete reclaim), D (12:30 non-NFP Friday, sustained again). **Internal:** I6 — the NFP framing in §3 is removed by Addendum A and reframed to day-of-week by Addendum D (deliberate, honest). **Cross-DC:** X1, X4, X5; **root of O1 and O7** — seven other candidates depend on this class existing. **Alternative (unexcluded, serious):** F4 — a high-volatility regime produces broadly elevated participation across minutes by construction, so "sustained" may be a restatement of "the volatility state was high," not a separate mechanism. **Reducible to:** possibly the Volatility primitive; that is precisely what the measurement would reveal. **Missing:** **the threshold and the distribution of the ratio (F3)** — without it the class is undecidable and seven candidates rest on an eyeball; plus aftermath outcomes tabulated by construction type. **Falsifier:** compute the ratio across all large M15 candles — **if the distribution is unimodal/continuous, the two "types" are an artifact of visual classification and Group I largely collapses; if bimodal but aftermaths do not differ by type, the aftermath claim dies.** **Class: A** — not because the claim is supported (it is n≈6 and confounded with volatility), but because it is the one candidate that is precisely operationalised, cheap to measure, and whose result would falsify or rescue seven others at once. **This is the recommended first target for the Statistician.**

### DC-0009 — Narrow band survives seven (then nine) touches
**Hypothesis:** a level's touch count relates to how it eventually resolves; a much-tested band's final rejection is sharper/higher-volume than earlier ones. **Addenda:** A (touch count → 9), B (break on the highest volume of the sequence), C (first retest holds as support), D (**second retest fails**). **Internal:** I3 — C and D contradict; Alpha says so explicitly. **Cross-DC:** X3; O3 with DC-0005/DC-0007. **Alternative:** with one band, "survived nine touches then broke" is the description of any range boundary that eventually breaks; nothing distinguishes it from an arbitrary consolidation edge. Weekend-gap and session-context variation are uncontrolled. **Reducible to:** the single level-interaction question shared with DC-0005/0007. **Missing:** many bands, not one; outcome distribution by touch count; base rate of retests that hold vs fail. **Falsifier:** if touch count does not shift the outcome distribution across many levels, the candidate dies. **Class: B** — the richest single case in the portfolio, but n=1 level whose own lifecycle refutes the simplest reading.

### DC-0010 — A consistently quiet hour breaks with a sustained expansion
**Hypothesis:** the 00:00–01:00 UTC hour, established as the quietest over three prior days, broke on 2025-08-07 with 5–7× volume and a sustained directional move — i.e. *this hour* is prone to occasional outsized activity. **Addenda:** A — **the entire session ran 2–3× baseline with a second spike at 05:00–06:00.** **Internal:** I2 — the hour-specific framing is destroyed by its own addendum; the phenomenon is all-day. **Cross-DC:** X6, O4 — and `OBSERVATION_REGISTRY` records the same hour running fully ordinary on 2025-08-11/12, 08-13, 08-21, 08-25, with Alpha concluding no consistent characterization holds. **Alternative:** a day-specific volatility regime (F4), which Addendum A directly supports; plus a three-day baseline is far too short to establish "consistently quiet." **Reducible to:** the Volatility hour-of-day profile and clustering — both already promoted. **Missing:** a per-hour distribution across many sessions separating "this hour breaks often" from "some days are hot at every hour." **Falsifier:** already effectively met — by its own addendum and by the registry. **Class: C — REJECT.** As an *hour-specific* claim it is refuted by material inside the laboratory; what remains ("2025-08-07 was a busy day") is not a Discovery Candidate. The residual legitimate question — is any hour special once volatility profile is accounted for — belongs to the promoted Volatility primitive, not here.

### DC-0011 — Single-minute sweep reclaimed, extends to new highs
**Hypothesis:** a single-minute sweep that is reclaimed and then *exceeds the pre-sweep range* is a distinct shape from sweep-and-stall. **Addenda:** A (second instance, larger, same anomalous session), B (third instance — but the reclaim was built over five minutes, not one). **Internal:** the "single-minute" qualifier in the title is not satisfied by Addendum B's own instance. **Cross-DC:** X2 — DC-0018 shows a spike that failed completely and ran the other way; DC-0008-B shows consolidation instead of extension; DC-0007 shows the level simply ceasing to matter. **Alternative (Alpha-named):** all three instances sit on sessions Alpha itself pre-flagged as anomalously active — "whether it is simply what any sharp move looks like on an unusually high-volume day is not established." A genuine, unbroken selection confound. **Reducible to:** DC-0008's construction question (the reclaim construction is exactly the sustained/concentrated distinction) + the sweep-aftermath taxonomy. **Missing:** sweep instances on ordinary-volume days; outcomes (extend / stall / reverse) against a base rate. **Falsifier:** if sweeps on ordinary days extend no more often than chance, or if the extend/stall split matches the unconditional continuation rate, it dies. **Class: B** — the outcome recurs three times, which is real, but every instance shares one confound and the title's construction claim is already violated by its own addendum.

### DC-0012 — Absorption: sustained high volume, no net displacement
**Hypothesis:** a window can carry volume far above baseline with range at or below baseline (two-sided absorption) — a distinct, nameable shape from "volume with displacement." **Addenda:** A — it resolved into a downside break on the very next candle. **Internal:** none. **Cross-DC:** O4 with DC-0010 (same hour, opposite sign); it is the explicit inverse of DC-0008/0010/0011. **Alternative:** the hour-anomaly framing is refuted (F9/X6). More seriously, high-volume/low-range bars are a *guaranteed* part of any volume-range joint distribution — their existence is not a finding; only their frequency and aftermath could be. **Reducible to:** the volume-range joint distribution; conceptually the null-displacement corner of DC-0008's construction space. **Missing:** the scan the candidate itself specifies — instance count and aftermath distribution vs base rate. **Falsifier:** if such windows are common and their aftermath matches the unconditional distribution, "absorption" is a label, not a phenomenon. **Class: B** — the cleanest operational definition in the portfolio (a statistician could run it unchanged), held back only by n=1 and by the fact that its stated instance is entangled with a refuted hour claim. **Highest-priority B.**

### DC-0013 — Large NY sustained expansion across four candles, no reversal
**Hypothesis:** a large NY-session expansion of sustained construction persists across multiple candles without a pullback and ends in consolidation rather than reversal. **Addenda:** A (second instance, seven candles, consolidation ending). **Internal:** none. **Cross-DC:** O1 (root DC-0008); F2 — its "consolidation ending" is one of six mutually exhaustive endings catalogued across the family; X1 against DC-0006. **Alternative:** F4 volatility persistence; plus NY-open scheduled participation, which Alpha notes (13:30 UTC proximity) but does not control. **Reducible to:** DC-0008 + "it lasted four candles and then consolidated." **Missing:** the DC-0008 threshold (F3) — without it "sustained construction" is unverified; and a duration/ending distribution across all expansions. **Falsifier:** if ending shape is independent of construction and duration across a proper sample, the candidate has no content. **Class: B** — two instances sharing an ending is the best-supported family sub-claim, but it cannot be validated before DC-0008's measurement defines the class.

### DC-0014 — 00:00 UTC V-reversal → four-candle rally → reversal
**Hypothesis:** a within-candle V (light-volume decline to a fresh low, sustained-volume recovery past the open) builds into a multi-candle rally and then reverses. **Addenda:** none. **Internal:** none; Alpha explicitly warns it should not be read as repeatable. **Cross-DC:** O1; X6 — the hour it occurs in has no consistent behaviour per the registry; F2 — its "reversal ending" duplicates DC-0016's. **Alternative:** a three-part compound narrative fitted to a single occurrence is the canonical overfitting risk; each component (V-shape, multi-candle continuation, reversal) is individually common. **Reducible to:** DC-0008 + a post-hoc three-part description. **Missing:** any recurrence of the compound sequence; base rates for each component separately. **Falsifier:** decompose — if each component's base rate is ordinary and their conjunction is no rarer than independence implies, there is nothing here. **Class: B** — the most narrative-dependent candidate in the portfolio; survives only because it is honestly labelled and cheap to decompose.

### DC-0015 — Eleven-candle NY expansion (~2h45m), longest run observed
**Hypothesis:** a sustained NY expansion can persist across eleven consecutive candles — the longest single-direction run in this replay — possibly with a volume-decay-then-pullback "exhaustion" ending. **Addenda:** none. **Internal:** none. **Cross-DC:** O1; F2 (its "modest pullback" ending is a fifth catalogued ending). **Alternative:** **the longest run in any finite sample exists by definition.** Selecting the sample maximum and describing it is not an observation about the market; it is an order statistic. The "exhaustion" ending is a post-hoc read of one tail. **Reducible to:** DC-0008 + "this one lasted longest." **Missing:** the duration distribution of all sustained expansions — against which 11 candles may be entirely ordinary. **Falsifier:** compute the duration distribution; if 11 sits within its bulk, the candidate has no content. But note this falsifier tests a claim the candidate never actually makes. **Class: C — REJECT.** The distinguishing feature is a sample extremum, not a hypothesis: it makes no statement that could be false, and it will be superseded automatically the moment a longer run is observed. Its underlying content (do expansions have a characteristic duration) is already covered by DC-0008/DC-0013 and belongs to the family measurement, where it has a denominator.

### DC-0016 — Early-Asia/pre-London expansion, largest of the family, then reversal
**Hypothesis:** the same sustained construction appears at a fourth clock time, reaching the family's largest point move, ending in a sharp reversal at a marginal new high. **Addenda:** A (second same-hour instance, ~60% magnitude, ~half duration, **same ending shape**). **Internal:** none; Alpha explicitly disclaims a Monday/week-open mechanism. **Cross-DC:** O1; F2 — shares DC-0014's reversal ending. **Alternative:** F4; and "reversal at a marginal new high" is a generic exhaustion description applicable to most failed extensions. **Reducible to:** DC-0008 + clock time + ending shape. **Missing:** the DC-0008 threshold; a base rate for "marginal new high then sharp giveback" across all expansions. **Falsifier:** if that ending is the modal outcome of large expansions generally, the same-hour recurrence carries no information. **Class: B** — the addendum contributes the family's only *pre-flagged-then-recurring* feature (ending shape, with magnitude explicitly shown to vary), which is genuinely more than the other family members offer.

### DC-0017 — NFP-scale 12:30 impulse holds its gains
**Hypothesis:** an NFP-scale 12:30 UTC impulse of sustained construction holds its gains across four subsequent high-volume candles without reversing or extending further. **Addenda:** A (the regime actually lasted ~4h15m and price **drifted higher** — not a hold), B (2025-09-11, second-largest 12:30 volume, non-NFP, resolved as **extended two-sided chop giving back the entire move**). **Internal:** **I1 — the stated hypothesis is contradicted twice by its own package.** **Cross-DC:** X4 — DC-0008 Addenda B/C/D already document five 12:30 instances with five different outcomes; X5 — the NFP attribution is undermined by DC-0008-D. **Alternative:** F4 (volume decay over hours is clustering); and magnitude alone demonstrably does not determine resolution — Addendum B says so in as many words. **Reducible to:** DC-0008's 12:30 series (O7), which has more instances and no directional claim. **Missing:** nothing collectible would rescue *this* hypothesis; the resolution-diversity question needs the 12:30 population, which DC-0008's addenda already begin. **Falsifier:** already met, internally, by Addendum B. **Class: C — REJECT.** The hypothesis as stated is falsified by its own submitted evidence. *This is a credit to Alpha's filing discipline, not a criticism of it — the addendum that kills it exists only because Alpha filed contrary evidence against its own candidate. The residual question (how do large 12:30 prints resolve) survives inside DC-0008's series with a better instance count.*

### DC-0018 — Extreme-volume spike to a fresh high fails, then sustained decline
**Hypothesis:** an extreme-volume push to a fresh multi-session high that fails within the same candle is followed by a sustained multi-candle decline of comparable scale to the expansion family. **Addenda:** none. **Internal:** none; Alpha flags the sweep-vs-rejection ambiguity itself. **Cross-DC:** O6 with DC-0006 (which this supports while DC-0008/0013/0017 contradict — X1); O1 (same construction, inverted direction); X2 (a fourth sweep aftermath). **Alternative (Alpha-named):** whether the initial spike was a stop-run (DC-0011, which resolved *oppositely*) or a genuine rejected breakout is unresolved — and the two predict opposite continuations, so the candidate cannot currently say which regime it is in. The subsequent decline may be unrelated aftermath. **Reducible to:** DC-0008 (construction, direction-inverted) + DC-0006's volume-failure claim, which is itself rejected here. **Missing:** other fresh-high extreme-volume failures with forward outcomes; an operational rule separating sweep-reclaim from genuine rejection. **Falsifier:** if fresh-high failures on extreme volume are followed by declines no more often than the unconditional rate, it dies. **Class: B** — a four-part compound at n=1, but it is the sample's largest-volume event and the sweep-vs-rejection distinction it exposes is a real, answerable question.

---

## 7. MISSING EVIDENCE — consolidated and prioritised

| Priority | Missing item | Unblocks |
|---|---|---|
| **1** | **The DC-0008 ratio distribution + threshold** (largest M1/M5 share ÷ M15 total, across all large M15 candles) | DC-0008, 0010, 0011, 0013, 0014, 0015, 0016, 0017, 0018 — decides whether "construction type" is real |
| **2** | **A volatility-clustering / hour-of-day null** for Group I | All 11 Group I candidates; tests F4, the portfolio's strongest alternative |
| **3** | **Denominators** — for every "frequently / consistently / repeatedly" claim, the count of comparable non-events | DC-0001, 0005, 0006, 0007, 0009, 0010, 0012 |
| **4** | **An operational definition of "compression"** (Alpha proposes trend efficiency) | DC-0002, DC-0003's HTF half |
| **5** | **Outcome distribution by level-interaction index** across many levels | DC-0005, 0007, 0009 |
| **6** | **The reserved OOS holdout** (post 2025-10-23), CEO-gated | DC-0004 only — spend deliberately |
| **7** | **Exchange-volume cross-check** or an explicit statement of tick-volume limitations | every volume-based candidate |
| **8** | **Bearish / lateral-H4 compression cases** | DC-0002 (its own stated falsifier) |

---

## 8. FINAL RECOMMENDATIONS

| DC | Class | One-line justification |
|---|---|---|
| DC-0003 | **A — READY FOR STATISTICAL VALIDATION** | Specific falsifiable prediction about an existing dataset (scale-separated re-run of OBS-0017); unambiguous negative result available. |
| DC-0004 | **A — READY FOR STATISTICAL VALIDATION** | Fully specified event/population/horizon, matched-null already run, sign-stable, one clean decisive OOS test — enters as a *hypothesis*, not a result, because of the disclosed selection effect. |
| DC-0008 | **A — READY FOR STATISTICAL VALIDATION** | The one precisely operationalised measurement in the portfolio, cheap to run, and its result falsifies or rescues seven other candidates at once. **Recommended first target.** |
| DC-0001 | **B — NEEDS MORE EVIDENCE** | Two eye-selected instances, pace never measured, no denominator. |
| DC-0002 | **B — NEEDS MORE EVIDENCE** | "Compression" not yet definable → events cannot be selected; K05 long-beta confound unbroken at n=4. |
| DC-0005 | **B — NEEDS MORE EVIDENCE** | n=2 with one impure case, folk-knowledge prior, no base rate. |
| DC-0007 | **B — NEEDS MORE EVIDENCE** | n=1; excursion size sits inside noise amplitude by DC-0003's own criterion. |
| DC-0009 | **B — NEEDS MORE EVIDENCE** | One band; Addendum D refutes the simplest reading of its own Addendum C. |
| DC-0011 | **B — NEEDS MORE EVIDENCE** | Outcome recurs 3× but every instance shares an anomalous-day confound; own addendum violates the title's construction claim. |
| DC-0012 | **B — NEEDS MORE EVIDENCE** | Cleanest operational definition in the portfolio; needs the scan it specifies. **Highest-priority B.** |
| DC-0013 | **B — NEEDS MORE EVIDENCE** | Best-supported family sub-claim (2 instances, shared ending) but gated on the DC-0008 threshold. |
| DC-0014 | **B — NEEDS MORE EVIDENCE** | Compound three-part narrative at n=1 at an hour with no consistent behaviour; decompose before resourcing. |
| DC-0016 | **B — NEEDS MORE EVIDENCE** | Only family member with a pre-flagged feature that then recurred (ending shape), magnitude shown variable. |
| DC-0018 | **B — NEEDS MORE EVIDENCE** | Compound at n=1, but exposes a real answerable question (sweep-reclaim vs genuine rejection). |
| DC-0006 | **C — REJECT** | Contradicted by the portfolio's own evidence (three extreme-volume candles that extended) plus a self-reported 24h inversion; confounded with DC-0003; no denominator. |
| DC-0010 | **C — REJECT** | Hour-specificity refuted by its own Addendum A (whole session elevated) and by ~12 registry instances showing no consistent characterization. |
| DC-0015 | **C — REJECT** | Its distinguishing feature is a sample extremum, not a hypothesis; makes no statement that could be false. |
| DC-0017 | **C — REJECT** | The stated hypothesis is contradicted twice by its own addenda (A: drifted, not held; B: comparable print gave everything back). |

**Tally: A = 3 · B = 11 · C = 4.**

### Note on the four rejections
None is a criticism of Alpha's conduct. Three of the four are killed by evidence **Alpha itself filed against its own candidate**, and the fourth (DC-0015) is a classification error rather than a bad observation. Rejecting a *claim* does not discard the *observation*: in every case the residual legitimate question survives elsewhere in the portfolio with a better instance count (DC-0006 → DC-0008's ratio; DC-0010 → the Volatility primitive; DC-0015 → the family duration distribution; DC-0017 → DC-0008's 12:30 series).

### What Red Team did **not** do
No Discovery Candidate, addendum, `SESSION_STATE.md`, or Knowledge Base entry was modified. No confidence rating changed. No family consolidated and no portfolio structure altered (per CEO ruling, consolidation is reserved for Statistician + Reasoning Engine — reductions above are recorded as findings only). No new hypothesis proposed. No statistics computed. No implementation. Nothing promoted. The Critique Battery v1.0 verdict ledger was deliberately **not** updated with these A/B/C classifications, which await CEO approval.

**Report ends. Red Team halts and awaits CEO approval.**
