# VOLPATH_PHASE1_REPORT — path geometry findings + HARD GATE

Frontier: can the PATH of a predictable volatility expansion be harvested WITHOUT predicting direction? Phase-1 info-only, 4,304
deduped mature-compression events, causal. Evidence in `VOLPATH_INFORMATION_LEDGER.md`.

## Hypothesis verdicts (§5)
- **H1** compression → large two-sided opportunity, SYMMETRIC path ordering — **SUPPORTED** (P(both±1ATR)=0.685; ordering UP≈DN≈0.50 at every k).
- **H2** first-break DIRECTION weak but first-break QUALITY predicts persist-vs-recross — **SUPPORTED** (raw first-break follow-through
  negative/weak; but an OBSERVED 2-bar follow-through ft2≥0.3ATR lifts P(CONTINUES) 0.154→0.395 cross-era-stable, cuts double-break).
- **H3** some compression classes → frequent double-sided excursions SUITABLE for non-directional harvesting — **NOT_SUPPORTED as
  "suitable"**: double-sided IS frequent (47% double-break, P(both±1)=0.685) but that is exactly the whipsaw hazard — it makes a straddle
  pay twice, not harvest. Frequent two-sided = whipsaw, not opportunity.
- **H4** other classes → one-sided escape where straddle false-activates — **SUPPORTED** (tight ±1ATR 68.5% both = false-activation; only
  a WIDE ±2ATR gets 62% one-sided escape).
- **H5** recross count/speed encodes whipsaw-vs-expansion — **SUPPORTED** (recross mean 3.1, P(≥2)=0.61 = a real whipsaw classifier; clean
  25% vs whipsaw-dominant 61%).
- **H6** session changes geometry without predicting direction — **AMBIGUOUS** (London mildly cleaner CONTINUES 0.21 vs NY 0.13; effect small).
- **H7** first impulse consumes most expansion (waiting destroys opportunity) — **NOT_SUPPORTED** (first 8b = only 24% of dominant excursion).
- **H8** significant residual expansion remains AFTER early classification — **SUPPORTED** (~76% of the dominant excursion remains after 8b).

## Central Phase-1 picture
Compression expansions are **WHIPSAW-DOMINANT and DIRECTIONALLY SYMMETRIC**: both sides reached, path ordering coinflip, 61% recross the
midpoint ≥2×, 47% double-break, raw first break has negative follow-through. → **naive straddle (pays whipsaw twice) and naive breakout
(confirmed VOLTIME-2 null) are both dead.** BUT two properties are genuinely NEW, stable, causal, non-trivial:
1. **POST-CLASSIFICATION continuation (H2):** an observed 2-bar follow-through raises continuation 2.5× (0.395), cross-era-stable —
   direction supplied by the observed move, not predicted from the endpoint.
2. **Slow consumption / residual expansion (H8):** ~76% of the move remains after the early classification window (8 bars) — so a
   post-classification entry does not sacrifice the opportunity.

## §7 HARD GATE — is there a stable causal path property that could plausibly monetize?
Answer: **MARGINAL / CONDITIONAL — proceed to a BOUNDED Phase-2 with the §14 redundancy test FIRST.**
- (1) non-trivial ✔ (0.154→0.395), (2) persistent ✔ (cross-era D/C/O stable), (3) not pure endpoint-direction-prediction ✔-ish (the
  direction is supplied by observed price, like S5's breakout — a path property, not a compression-endpoint forecast), (4) large enough
  vs cost **UNRESOLVED** — P(CONTINUES)=0.395 vs P(DOUBLE_BREAK)=0.336 is a THIN margin, and this closely resembles the already-FAILED
  momentum/breakout family. **Primary Phase-2 risk = REDUNDANCY (§14):** post-classification entry may reduce to "delayed VOLTIME-2
  breakout" and fail costs identically.
- **Decision:** the property is real and stable enough to warrant ONE bounded Phase-2 falsification (D-family: post-classification entry;
  and a WIDE ±2ATR conditional straddle as the two-sided candidate). If Phase-2 shows it is REDUNDANT_WITH_PREVIOUSLY_CLOSED_FRONTIER or
  fails cost/robustness → close VOLPATH honestly as an information-only result. No strategy claimed. S5 frozen. Broker disabled.

## PHASE-2 (bounded) — both candidates FALSIFIED; VOLPATH closes INFORMATION-ONLY
`volpath_phase2.py` (STRESS 0.24, blocks D/C/O):
- **RAW breakout baseline: net −0.439** all eras (confirms VOLTIME-2 null-negative).
- **POST-CLASSIFICATION (D) entry: net −0.519 — WORSE than the raw breakout** → **REDUNDANT_WITH_PREVIOUSLY_CLOSED_FRONTIER** (§14). The
  Phase-1 continuation lift (0.154→0.395) was mechanical/definitional; entering after the 2-bar follow-through arrives later (0.3ATR gone)
  and still hits 34% double-break — a delayed breakout that fails identically. NOT a distinct edge.
- **STRADDLE (B) range-boundary: net −0.375/event, both-side-activation 0.478** — pays whipsaw on BOTH sides ~48% of the time (the 47%
  double-break confirmed), net-negative every era. Straddle harvests whipsaw, not volatility.

## §7 HARD GATE — RESOLVED: **NO monetizable path asymmetry.** VOLPATH CLOSED as information-only.
The compression-expansion path is whipsaw-dominant and directionally symmetric; the one non-trivial property (post-classification
continuation) is redundant with the already-failed breakout, and two-sided harvesting pays whipsaw twice. **No strategy invented**
(mandate §7/§17 stop A+B). The genuine deliverable is the PATH-GEOMETRY INFORMATION itself (VOLPATH_INFORMATION_LEDGER.md) — it precisely
characterizes WHY the predictable expansion is not harvestable (symmetric double-break oscillation), a fifth non-directional information
asset alongside VOLTIME-1 / DXY-NDX1 / SF-3. S5 frozen/untouched; broker disabled; no protected data; no mining.
