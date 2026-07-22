# LINE-A — COMPRESSION CASE LEDGER
Purpose: accumulate **as many compression cases as possible**, across H4 regimes, to decide whether
"compression resolves in the direction of the H4 bias" survives outside a bull trend — or is long beta.
Forward observation only (manual stepping). Cases logged when *seen*, resolution appended after.

## Critical distinction discovered by observation (2024-03-27)
I had been pooling two different things under "compression". They behave **oppositely**:

| Class | Scale | Typical context | Observed behaviour |
|---|---|---|---|
| **HTF-C** | H4 / multi-day consolidation | after an expansion leg | resolves into a **genuine expansion** |
| **micro-C** | M15 coil, 5–10 candles | thin Asia tape, inside a range | **marginal break that fails** |

Pooling these would guarantee a null (they cancel). Any future test must separate them.
This also retro-explains OBS-0017's null: it tested *break geometry* across all scales at once.

---
## HTF-C cases (the ones that matter for the mechanism)
| # | Date | H4 regime | Compression evidence | Resolution | Matches H4 bias? |
|---|---|---|---|---|---|
| C1 | Oct 2023 (#003) | **BEARISH** | Jun–Aug stair-step chop, dense alternating structure | **DOWN**, clean 1925→1829 | ✅ |
| C2 | Jan–Feb 2024 (W1) | bullish | churn zone 2000–2060, many alternating labels | **UP**, +10% to 2195 | ✅ |
| C3 | Feb–Mar 2024 | bullish | slow grind, small overlapping candles | **UP**, vertical 2040→2195 | ✅ |
| C4 | Mar 12–20 2024 (#014, **pre-registered**) | bullish-corrective | range 2145–2195, vol contracting, effort-without-result | **UP**, to 2222.9 (+67) | ✅ |

**HTF-C: 4/4 matched the H4 bias.** But ⚠️ **3 of 4 are UP inside the 2023–25 gold bull trend** —
the K05 long-beta confound. **C1 is the only non-long case and currently carries the entire
falsification burden.** This is why I refuse to promote.

## micro-C cases
| # | Date | H4 regime | Compression evidence | Resolution |
|---|---|---|---|---|
| m1 | 2024-03-20 ~05:00 (#013) | lateral/corrective | ranges 1.51→0.62, vol 656→343, pinned 1.3pt | marginal break UP → **FAILED**, −3.3 |
| m2 | 2024-03-27 ~01:15 | **LATERAL** | ranges 1.55→0.62, vol ~210 flat, pinned 1.5pt | marginal break UP to 2180.25 → **FAILED**, back to 2177.4 |

**micro-C: 2/2 broke marginally UP and failed.** Both in thin Asian tape. Consistent with OBS-0017
(break geometry uninformative) and with #005/#006 (sub-H1 structure is noise-scale). Working read:
micro-C is **not** a mechanism, it is noise — but the *consistency of the failure* is worth more cases.

## LATERAL-H4 cases (the "no prediction" test)
| # | Date/time (UTC) | H4 regime | Compression / event | Resolution |
|---|---|---|---|---|
| L1 | 2024-03-27 01:15 → 08:45 | **LATERAL** (2150–2223) | micro-C coil (m2) under ~2180, then **three** marginal rejections at 2180.25 / 2180.43 | 3rd rejection produced real displacement DOWN (−7, to 2173.49) on the largest volume of the sequence (1810), at the **London open** — but the move **did not extend**; price rotated straight back to 2177.7 and settled 2175–2177 |

**Reading (recorded, not judged):** in a lateral H4 the sequence produced *rotation*, not expansion.
Under DC-0002 a lateral H4 supplies no directional bias, so no expansion is predicted — L1 is
consistent with that in the weakest possible sense (absence of a prediction being met by absence of a
move). It is **not** evidence for the candidate. What it does add is a distinct micro-observation
worth more cases: **repeated** rejections at one level (3×), timed to a session open, produced
displacement where single rejections (m1, m2) produced only failure — but the displacement died
inside the range.

---
## Falsification status
- The mechanism is **untested where it matters**: I have exactly **one** bearish-regime HTF-C case (C1).
- **What would kill it:** HTF-C compressions in bearish/lateral H4 that resolve *against* the H4 bias,
  or resolve randomly. In a lateral H4 there is no bias, so the mechanism makes **no prediction** —
  if lateral HTF-C resolutions are ~50/50, that is consistent-but-empty; if they systematically go
  up anyway, that is **long beta exposed** and LINE-A dies.
- **What would support it:** bearish-H4 HTF-C resolving DOWN, repeatedly.

## Hunting targets (forward only, no date-jumping)
Advance chronologically and log every HTF-C encountered, prioritising:
1. bearish H4 stretches (needed most — currently n=1);
2. lateral H4 stretches (the no-prediction test);
3. any HTF-C that resolves *against* the H4 bias (would be the most valuable single observation).

Current position: 2024-03-27 ~03:00 UTC. H4 regime: **LATERAL** (2150–2223 after the March expansion).

## CONTRA-EXEMPLU la DC-0002 (2024-07-19..24)
| C5 | 2024-07-22..24 | **BEARISH** (dupa -66pt / -2.7% pe 19 iul, de la 2470 la 2396) | compresie 3 zile, range 25-30pt, lateral 2384-2414, volum plat ~2450 | **UP** la 2418.5, peste plafonul de 3 zile | ❌ **NU** respecta biasul H4 |

Primul caz HTF-C care se rezolva IMPOTRIVA biasului H4. Bilant DC-0002: 4 respecta / 1 nu.
Exact cazul cerut (H4 bearish). Inregistrat, nu judecat - evaluarea e a Red Team.
