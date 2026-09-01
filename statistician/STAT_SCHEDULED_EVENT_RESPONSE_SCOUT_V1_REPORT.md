# STAT_SCHEDULED_EVENT_RESPONSE_SCOUT_V1 — REPORT

**Mandate:** `SCHEDULED_EVENT_RESPONSE_SCOUT_V1` — independent statistical discovery, economic-event response.
**Division:** Statistician. **Date:** 2026-09-01.
**Code:** `statistician/event_scout/audit.py` (§1 audit), `statistician/event_scout/feas.py` (feasibility
arithmetic), `statistician/event_scout/event_population.csv` (the complete governed event population, 446 rows).

## VERDICT

```
SCHEDULED_EVENT_RESPONSE_SCOUT_V1_COMPLETE = NO  — STOPPED AT SECTION 1 AS INSTRUCTED
ECONOMIC_EVENT_DATA_AUDIT_PASS             = NO
STATUS                                     = DATA_BLOCKED
```

The mandate instructs: *"If the available data is too incomplete for meaningful causal research: STOP with
DATA_BLOCKED."* That condition is met, and not marginally. **The governed economic-event population and the
governed XAU price series do not overlap by a single event.** Every captured event lies in the future
relative to the last bar of every governed price file.

I did not run the scan. I did not manufacture surprise values. I did not reconstruct an event schedule from
institutional release rules — that would be creating ungoverned data, which the mandate forbids twice.

---

## 1 — DATA AUDIT

Everything below was verified mechanically from the files. The acquisition division's own inventory report
makes several of these claims; I re-derived each rather than quoting it, and where I could check its
arithmetic (the JSON↔CSV timezone reconciliation) **it is correct**.

### 1.1 What was captured

| | |
|---|---|
| source | ForexFactory structured export, `nfs.faireconomy.media` — `ff_calendar_thisweek` only |
| location | `acquisition_staging/calendar/` (**quarantined**, never integrated into a data manifest) |
| snapshots | **5 weekly pulls**: W32 normalized + captures `2026-08-10`, `-08-17`, `-08-24`, `-08-31` |
| total event rows | **446** |
| calendar date range | **2026-08-02T09:15Z → 2026-09-04T14:00Z** (33 days ≈ 4.7 weeks) |
| unresolved timestamps | 0 |
| duplicate (timestamp, title, country) | **0** |

Also present, and audited for completeness: `acquisition_staging/news/NEWS_LEDGER.csv` — **884 unscheduled
news headlines**, 2026-08-09 → 2026-09-01. That is a *news* feed, not a scheduled-event calendar, and it
shares the same coverage problem.

### 1.2 Fields that exist — verified per format, not per prose

| format | fields |
|---|---|
| JSON (raw) | `country, date, forecast, impact, previous, title` |
| CSV / XML (raw) | `Title, Country, Date, Time, Impact, Forecast, Previous, URL` |
| CSV (normalized) | `datetime_utc, date_ny, time_ny, src_offset, currency, impact, event, forecast, previous, url` |

| field the mandate asks about | present? |
|---|---|
| event timestamp | **YES** |
| timezone | **YES** — see §1.3 |
| event name / category | **YES** (`title`, free text; no category taxonomy) |
| importance | **YES** — `High / Medium / Low / Holiday` |
| country / currency | **YES** |
| **actual** | **ABSENT — in every format, in every snapshot** |
| forecast | present, **30% missing** (136/446) |
| previous | present, **14% missing** (61/446) |
| **surprise** | **ABSENT** (and underivable — requires `actual`) |
| **revision flag** | **ABSENT** |

**This alone kills mandate §9.** `surprise = actual − forecast` cannot be computed, because `actual` is never
in the structured export. And `previous` is a bare scalar with no revision flag, so it is *undecidable from
the file* whether it holds the originally-published or the later-revised value — i.e. **potential backward
leakage that cannot be detected, let alone excluded**. Under mandate §3, `previous` is therefore unusable and
only timestamp/category would have been admissible.

### 1.3 Timezone and precision — independently reconciled

- JSON `date` is **offset-aware per record** (`2026-08-07T08:30:00-04:00`).
- CSV/XML carry `Date`+`Time` that are **UTC but unmarked** — a live trap for anyone who reads the
  displayed New-York wall clock.
- **I converted all 98 JSON records to UTC and matched them against the CSV: 98/98 identical, 0 mismatch.**
  The acquisition report's reconciliation reproduces exactly.
- **Timestamp precision: minute** (seconds are 00 in every record).
- **DST: only `-04:00` (EDT) is observed.** Because the offset is explicit per record the UTC instant is
  unambiguous, but **no winter week exists in the capture**, so the EST transition is untested. Not a defect
  today; a thing to re-verify once a November capture exists.

### 1.4 Composition

```
impact    : Low 343 · High 51 · Medium 48 · Holiday 4
currency  : USD 129 · EUR 92 · GBP 43 · AUD 41 · JPY 38 · CAD 33 · ...
USD High+Medium: 42 rows over 33 days
```

### 1.5 Simultaneity (mandate §11)

The mandate is right to insist on this, and the data confirms the concern is real:

```
distinct timestamps            : 298
timestamps carrying >1 release : 73  (24%)
maximum releases at one instant: 8
```

Nearly a quarter of timestamps are multi-release. Counting rows as episodes would have inflated N by ~50%.
Under a 30-minute clustering rule the 42 USD High+Medium rows collapse to **22 independent episodes**.

### 1.6 THE DECIDING TEST — overlap with governed XAU price data

| governed price file | last bar | events inside |
|---|---|---|
| `OANDA_XAUUSD_M5.csv` | 2026-07-27 17:55Z | **0** |
| `OANDA_XAUUSD_M15.csv` | 2026-07-27 16:15Z | **0** |
| `OANDA_XAUUSD_H1.csv` | 2026-07-13 05:00Z | **0** |
| `OANDA_XAUUSD_H4.csv` | 2026-07-13 01:00Z | **0** |
| `OANDA_XAUUSD_D1.csv` | 2026-07-09 21:00Z | **0** |
| `*_from_M15_v2` (H1/H4/D1, the 2011-history builds) | ≤ 2025-10-12 | **0** |
| `OANDA_XAUUSD_M15__SUPERSEDED_v1` | 2026-07-13 06:00Z | **0** |

```
XAU_M5_OVERLAP  = 0 events, 0 bars
first captured event  2026-08-02 09:15Z
last governed bar     2026-07-27 17:55Z
gap                   5 days 15:20
```

**MISSINGNESS, stated in the terms that matter: the treatment variable is 100% missing over the entire
period for which the outcome variable exists.** This is not sparse data or a low-power sample. There is no
sample. Not one event episode can be paired with a single XAU bar.

This is a *structural* consequence of the acquisition mechanism, not an accident of timing: the CDN serves
`thisweek` only — `lastweek`, `nextweek`, `thismonth` and dated endpoints all return 404 — so the calendar is
**forward-only by construction**, and capture began 2026-08-04, after the price archive's cutoff. The price
archive ends where it ends; the event archive begins where capture began; they do not meet.

`ECONOMIC_EVENT_DATA_AUDIT_PASS = NO`. `STOP — DATA_BLOCKED.`

---

## 2 — WHY I DID NOT PROCEED ANYWAY

Three routes exist to produce event-looking results from this state. I rejected all three, and name them so
the rejection is auditable rather than implicit.

1. **Reconstruct the event schedule from institutional release rules** (NFP = first Friday 08:30 ET, CPI
   ≈ mid-month 08:30 ET, FOMC from the published year-ahead schedule). This would produce a large historical
   event set overlapping the M5 archive. **Rejected:** the mandate says *"Do NOT acquire new data"* and *"do
   not manufacture missing values"*. A schedule I write from memory is ungoverned, unversioned, unhashable
   data with no provenance and no error bars on its own correctness. It is exactly the kind of input that
   later becomes indistinguishable from evidence.
2. **Test the release clock instead of the release** — compare XAU path structure at 12:30/13:30 and
   14:00/15:00 UTC against other times. **Rejected on identification grounds, which matters more than the
   governance point:** without a calendar I cannot separate event days from non-event days at the same clock
   time, so this measures **time-of-day**, not events. Worse, mandate §10 designates time-of-day as the
   *matched control*. Running it as the treatment would be presenting the control as the finding — the exact
   confusion the mandate was written to prevent.
3. **Use the 446 forward events with live price pulled from elsewhere.** **Rejected:** that is new data
   acquisition, it is outside the governed manifest, and even at full success the sample is ~22 USD
   High+Medium episodes — see §3.

Route 1 is the only one that could ever be legitimate, and only if the CEO authorizes it as a *governed
acquisition* with its own provenance, hash and error audit. It is a data-division decision, not something a
discovery scan should quietly assume.

---

## 3 — WHAT WOULD UNBLOCK THIS, QUANTIFIED

Arithmetic only. **Zero hypothesis tests were run; no DEV/OOS data was consumed; nothing enters any
multiplicity ledger.** The variance scale is a descriptive marginal moment of an already-consumed price series.

**Observed episode-accrual rate at the current capture cadence** (30-min clustering):

| family | rows | independent episodes | per week |
|---|---|---|---|
| USD High | 19 | 9 | **1.9** |
| USD High + Medium | 42 | 22 | **4.7** |
| any-currency High | 51 | 25 | 5.3 |
| USD employment family | 18 | 13 | 2.8 |
| USD inflation family | 10 | 6 | 1.3 |
| central-bank / rate family | 41 | 30 | 6.4 |

**Variance scale of the natural target.** Scout V2 established that XAU's structure lives in *timing*, so
time-to-first-±100p is the target an event scan would most plausibly move. On M5 (censored cases capped at
the 24h horizon): **mean 6.95 h, sd 6.96 h**, 5.4% censored at cap.

**Episodes needed** (two-sided α = .05, 80% power, treatment vs. a large matched control):

| effect on time-to-±100p | N episodes | weeks of USD High+Med capture |
|---|---|---|
| 2.0 h (29% of base) | 95 | **20** |
| 1.5 h (22%) | 169 | **36** |
| 1.0 h (14%) | 380 | **81** |
| 0.9 h (13% — the size Scout V2 actually found for V2-4) | 469 | **101** |

With Bonferroni at the mandate's own m = 60 budget (z: 1.96 → 3.02): a 1.5 h effect needs **321 episodes
≈ 1.3 years**; a 0.9 h effect needs **892 episodes ≈ 3.7 years**.

**Read that honestly.** Forward capture alone reaches an interesting-but-modest 2 h effect in ~5 months and
a Scout-V2-sized effect in ~2–4 years. If the CEO wants this branch answerable **this year**, forward capture
is not the route — a governed historical event archive is. If the answer can wait, the capture tasks are
already running and cost nothing; they just need to keep running, and the November capture should be checked
for the EST offset (§1.3).

*(Assumption stated plainly: this treats episodes as independent draws carrying the marginal variance. Real
event episodes cluster — NFP and CPI days co-occur with elevated volatility — so the true requirement is
likely **larger**, not smaller. The table is a floor.)*

---

## 4 — MANDATE ITEMS THAT CANNOT BE ANSWERED, STATED AS UNANSWERED

I am not converting an absent measurement into a null result. Each of these is **UNMEASURED**, which is a
different thing from NO.

```
POSITIVE_CONTROL                     = NOT_RUN  (no event population exists to inject a control into;
                                                 reporting PASS would be a false statement)
EVENT_INCREMENTAL_INFORMATION_FOUND  = UNMEASURED  (not NO)
STATISTICALLY_MEANINGFUL_EVENT_PHENOMENA = 0 tested, 0 testable
STRATEGY_HYPOTHESES_WORTH_TESTING    = 0
TOP_1..TOP_5                         = NONE — no event episode is pairable with any governed price bar
STRONGEST_EVENT_LEAD                 = NONE
READY_FOR_ALPHA_REPLICATION          = NO — there is nothing to replicate
```

Mandate §13 is explicit that a failed positive control forbids interpreting nulls. The situation here is one
step earlier: there is no scan to control. **Nothing in this report should be cited as evidence that
scheduled events lack information in XAU.** That question remains open and untouched.

---

## 5 — CEO QUESTION (§18)

> **Do scheduled events create more tradeable structure than ordinary price-only states?**

**UNKNOWN — and it is not answerable with any data this lab currently holds.** I will not rank an unmeasured
branch against measured ones as if the comparison had been made.

What I *can* state is the measured ranking, with events marked as the hole it is:

| rank | information source | evidence status |
|---|---|---|
| 1 | **timing / hazard** — time-to-expansion, time-to-±100p | **measured, strongest**: Scout V2, best \|z\| 8.89; 5 phenomena 6/6 years, OOS sign-consistent |
| 2 | **path / price sequence geometry** | measured, real: Scout V1's unconditional payoff geometry is the program's largest structural fact |
| 3 | **ordinary volatility / range state** | measured: transitions move time-to-±100p 0.9–1.9 h on a 9.2 h base — but session-sign-MIXED, so partly composition |
| 4 | **session / time-of-day** | measured: L1 is real and Bonferroni-surviving, but it is a *window* effect, honest-N 150–246 |
| — | **scheduled economic events** | **UNMEASURED — 0 usable observations. Cannot be placed.** |
| last | **direction prediction** | measured across 80 tests, best \|z\| 1.51 — repeatedly null |

One observation worth the CEO's attention, from the audit rather than from a test: **all USD High/Medium
releases fall in 08:15–10:00 ET**, by institutional schedule (BLS 08:30, ISM/Census 10:00). That window is the
NY morning. So event effects, whenever they can finally be measured, will be **structurally confounded with
the NY session and with L1's neighbouring hours**. Whoever designs the eventual scan must build the matched
control on time-of-day *first*, or the event variable will simply re-discover the clock. I raise it now
because it is a design constraint that is knowable today and cheap to forget later.

---

## 6 — PROTECTION

Not modified, not inspected: **S5, Q4, AI Trader, P007, MGMT-004, MT5, StrategyCatalog, L1, P2, V2-4.**
I did not read Alpha's active P2 work. No promotion. No new data acquired. The quarantined calendar staging
area was **read only**; nothing was integrated into a manifest.

```
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
