# Cross-Edge Research Candidates — Flow A

**Purpose**: a registration-only log for phenomena observed as SIDE EFFECTS of a properly-scoped edge's
own control group — not themselves a numbered entry in `EDGE_DISCOVERY_REGISTRY_v1.md` (the 40-edge
backlog's own frozen structure is not modified by this document, per explicit CEO instruction), and not
themselves subject to `EDGE_RESEARCH_PROTOCOL.md`'s stage pipeline until/unless a future, separate CEO
decision opens one as a formally registered edge. **No study is conducted from this document.** This is
observation + risk registration only.

---

## Candidate CEC-001 — "Unviolated structural zones may retain directional continuation information;
the same zones lose that information after structural violation or inversion"

**Status: CANDIDATE OBSERVATION ONLY — NOT AN EDGE. Not V0. Not Discovery. Not Frozen Candidate. Not
Validation. Not Final Verdict.** Registered 2026-07-22 per explicit CEO decision, following acceptance
of E010 and E012's own (negative) V0 conclusions, which are unchanged by this entry.

### 1. Exact observation from E010 (Breaker Block Snatch, `edge_research/E010_breaker_block_snatch.md`)

Order blocks (a displacement bar's originating opposite-colored bar, per E010's own disclosed
1.5×ATR/50%-body/10-bar-lookback construction) that were **never later closed through** within the
480-bar (5-trading-day) test horizon ("unflipped") showed a large continuation-in-ORIGINAL-polarity
rate, sharply unlike the "breaker" (flipped) group's own ~50% coin-flip result.

### 2. Exact observation from E012 (Inverted Fair Value Gap, `edge_research/E012_inverted_fvg.md`)

Fair Value Gaps (standard 3-bar imbalance, per E012's own disclosed construction) that were **never
later fully closed through** within the same 480-bar horizon ("un-inverted") showed the same
qualitative pattern: a large continuation-in-ORIGINAL-role rate, sharply unlike the "inverted" group's
own ~50-53% coin-flip result.

### 3. Sample sizes

| Edge | Group | Timeframe | n (total) | n (revisited, outcome measured) |
|---|---|---|---|---|
| E010 | Unflipped OB | M15 | 1,096 | 1,093 |
| E010 | Unflipped OB | H1 | 325 | 325 |
| E010 | Breaker (contrast) | M15 | 5,833 | 5,604 |
| E010 | Breaker (contrast) | H1 | 1,550 | 1,478 |
| E012 | Un-inverted FVG | M15 | 1,196 | 704 |
| E012 | Un-inverted FVG | H1 | 316 | 189 |
| E012 | Inverted (contrast) | M15 | 12,804 | 12,433 |
| E012 | Inverted (contrast) | H1 | 2,994 | 2,898 |

### 4. Continuation rates

| Edge | Group | Timeframe | Continuation rate | Mean net return @ 1 bar (ATR) |
|---|---|---|---|---|
| E010 | Unflipped OB | M15 | 88.0% | +1.03 |
| E010 | Unflipped OB | H1 | 86.2% | +1.12 |
| E010 | Breaker (contrast) | M15 | 49.9% | +0.005 |
| E010 | Breaker (contrast) | H1 | 51.4% | +0.012 |
| E012 | Un-inverted FVG | M15 | 86.8% | +0.48 |
| E012 | Un-inverted FVG | H1 | 86.2% | +0.48 |
| E012 | Inverted (contrast) | M15 | 50.0% | −0.013 |
| E012 | Inverted (contrast) | H1 | 52.9% | +0.004 |

### 5. Control definitions (verbatim from each edge's own script)

- **E010 "unflipped" control**: an order block (as constructed above) for which no later bar's CLOSE,
  within 480 bars of formation, decisively violates the OB zone (below its low for a bullish OB, above
  its high for a bearish one). Reaction measured in the OB's own ORIGINAL polarity direction, from the
  first revisit of the zone.
- **E012 "un-inverted" control**: an FVG (as constructed above) for which no later bar's CLOSE, within
  480 bars of formation, decisively violates the gap zone. Reaction measured in the FVG's own ORIGINAL
  role direction, from the first revisit of the zone.
- Both are defined **relative to the same 480-bar horizon used to detect the "breaker"/"inverted" event
  in each edge's own primary test** — this shared construction is itself the source of risk items 7.1-7.3
  below.

### 6. p-values (χ² test, continuation rate: unbroken-control vs. broken/flipped-contrast group)

| Edge | Timeframe | p-value |
|---|---|---|
| E010 | M15 | 5.9 × 10⁻¹¹⁹ |
| E010 | H1 | 3.6 × 10⁻³⁰ |
| E012 | M15 | 4.4 × 10⁻⁸⁰ |
| E012 | H1 | 8.6 × 10⁻¹⁹ |

**These p-values must NOT be read as evidence this candidate is real** — see section 7. They quantify
how different the two GROUPS look under the classification already used to build them, which is exactly
what section 7 argues may be a large part of the problem, not a solution to it.

### 7. Known risks (the reason this is registered as a candidate, not an edge)

1. **Look-ahead bias in the classification itself**: "unflipped"/"un-inverted" status is DEFINED by
   whether a violation occurs anywhere in the NEXT 480 bars after formation. At formation time, this
   status is unknowable — the classification is built using the very future the continuation outcome
   also measures. This is not merely a statistical nuance; it is a structural look-ahead issue in how
   the two comparison groups were built.
2. **Event-definition leakage**: because of (1), group membership (unflipped vs. flipped) and the
   outcome (continues vs. reverses) are computed from **overlapping, non-independent slices of the same
   forward price path** — they are not two separate measurements of two separate things.
3. **Tautological continuation labels**: for a bullish OB/FVG, "never closed below the zone" and "price
   continued upward without falling back through support" are, in many geometries, close to the SAME
   statement restated twice. A large measured "effect" may partly or wholly be an artifact of comparing
   a fact to a near-restatement of itself, not independent confirmation of a predictive mechanism.
4. **Overlap between event window and outcome window**: the classification horizon (480 bars from
   formation) and the outcome-measurement window (from the revisit point forward) are not cleanly
   separated in time — revisits and their subsequent reactions can fall inside the same window used to
   decide "unflipped" in the first place.
5. **Survivorship of unbroken zones**: the "unflipped"/"un-inverted" population is, by construction, a
   survivor set — cases where the zone happened not to be tested hard or happened to hold. This is
   classic survivorship bias: the zone may be incidental to a trend that was already going to continue,
   not causal to the continuation.
6. **Unequal distance-to-target between the two groups**: the broken/flipped group and the unbroken
   group were never distance-matched against EACH OTHER (unlike each edge's own primary V0 test, which
   did distance-match against a random control). If unbroken zones are systematically further from
   price at formation (e.g., because price moved away quickly and never returned to test them hard),
   that alone could produce this pattern without any real predictive content.
7. **Unequal event age**: an "unflipped" classification requires surviving the FULL 480-bar window,
   while a "breaker"/"inverted" classification can trigger at any point within it (often very early,
   per each edge's own median time-to-flip figures). The two groups are not matched on how much of the
   forward path remains to be measured at the point of classification.
8. **Repeated observations from the same zone / same structural episode**: order blocks and FVGs that
   form during one strong, sustained trending move can be numerous, overlapping, and highly correlated
   with each other (many events from the same underlying price swing). Nominal sample sizes (n=1,096,
   n=1,196, etc.) likely overstate the number of genuinely independent observations.
9. **Dependence between samples (statistical)**: point 8's consequence — the χ² tests in section 6
   assume independent trials; if effective independent sample size is much smaller than nominal n, the
   extreme p-values in section 6 are likely a substantial overstatement of true statistical confidence,
   independent of points 1-7's own more fundamental concerns.
10. **No random-matched-distance control was run for the unbroken groups themselves** — each edge's own
    primary V0 test had a random-matched-distance control; this candidate's own "unbroken" groups were
    only ever compared to the broken/flipped contrast group, never to a pure-noise, no-structure
    baseline built with the same survivorship/classification logic applied to it.

### 8. Why this is not yet an accepted edge

- It emerged as an **incidental side-effect** of E010's and E012's own control-group construction, not
  from an independently pre-registered V0 hypothesis stated before any data was examined — this itself
  is contrary to `EDGE_RESEARCH_PROTOCOL.md`'s own founding principle (§0.1, "discovery, not
  confirmation") if promoted without a fresh, dedicated design.
- Section 7's risks (especially items 1-3, the look-ahead/tautology cluster) are severe enough that a
  large fraction, or all, of the observed effect could be a labeling artifact rather than a genuine
  predictive signal — this has not been ruled out.
- No distance-matched or random-matched control has been run for this candidate specifically (item 10).
- No cross-instrument or cross-structural-type generalization has been checked beyond the two
  coincidentally-similar constructions (order blocks, FVGs) that happened to surface it.
- Registering it as a numbered edge (e.g. assigning it an E0XX identifier in
  `EDGE_DISCOVERY_REGISTRY_v1.md`) would modify that document's own frozen 40-edge structure — explicitly
  not done in this entry, per the CEO's own instruction; it requires a separate, future, explicit CEO
  decision if pursued at all.

### 9. What independent falsification would require

1. A **freshly pre-registered V0**, stated before examining any further data, distinct from E010's and
   E012's own (already-closed) V0s.
2. A classification method that **breaks the look-ahead/tautology overlap** (risk items 1-4) — e.g.
   classifying "unbroken" status using a short, FIXED, EARLY confirmation window (such as the first 5-10
   bars only) and measuring the continuation outcome over a SEPARATE, LATER, non-overlapping window, so
   the classifying fact and the measured outcome no longer share the same forward price data.
3. **Distance-matching AND a random-matched-distance control applied to the "unbroken" group itself**
   (not only a broken-vs-unbroken contrast), built with the same survivorship structure so the control
   is genuinely comparable.
4. An **age-matched design** so unbroken and broken groups are compared at equivalent stages of their
   own forward window, not systematically different ones (risk item 7).
5. A **dependence-aware statistical test** (e.g. block-bootstrap by time period, or clustering by
   underlying trend episode) instead of a plain χ² test, to address risk items 8-9.
6. **Generalization beyond order blocks and FVGs** to at least one more structural-zone construction, to
   check this is not an artifact specific to how these two particular concepts were operationalized.
7. **Out-of-time replication** once the Tier-0 history extension closes the gap to the protocol's own
   ~5-6 year requirement.

Only after all of the above would this candidate be eligible for a genuine V0 registration and Stage 2
Discovery pass under `EDGE_RESEARCH_PROTOCOL.md` — and even then, per that protocol, reaching a Final
Verdict would still not itself authorize implementation.

---

*This document does not change E010's or E012's own accepted conclusions (both V0 NOT SUPPORTED, no V1,
Stage 2 — Discovery, full profile complete, no Final Verdict). It exists solely to preserve, with the
same rigor the project applies to positive findings, an honest record of an unresolved side-observation
and the specific reasons it must not be mistaken for a validated edge.*
