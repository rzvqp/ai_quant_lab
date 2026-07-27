# V1 Operationalized Contracts — Flow A (pre-registered BEFORE incoming data, 2026-07-26)

**Purpose.** Turn narrative V0s into testable V1 operationalizations satisfying the Statistician's five
criteria — **frozen and committed before the incoming 2011-2022 M15 / M5 data exists**, so a later test
is a genuine confirmation, not an after-the-fact operationalization (the E015-V1 failure mode).

**Number-sourcing rule (obeyed throughout).** Every numeric choice is derived from the narrative V0 text
or from a convention **already committed in an existing Flow A script** — never from data. Sources reused:
- ATR-14 (`_common.load`); displacement `range > 1.5×ATR14[prior]` + body `≥ 0.5×range`
  (E010/E015 `PRIMARY_DISP=1.5`, `BODY_FRAC=0.5`); OB lookback 10 (E010 `LOOKBACK_OB`).
- 3-bar FVG (E012 `detect_fvgs`). Fractal swing k=5 (E009/E017/E028).
- `REVISIT_HORIZON = 480` M15 bars = 5 trading days (E010/E012/E029).
- `movement_profile` horizons `(1,3,5,10,20,50)` and `REACTION_THRESHOLD = 1.0×ATR` → continuation/
  reversal/stall (`_profile.py` l.11/l.13). Max response ceiling = 50 bars.
- Penetration/departure `0.25×ATR` (E027 `DEPARTURE_THRESHOLD_ATR`); "equal" tolerance `0.15×ATR`
  (E017 `PRIMARY_TOL`); 50% equilibrium (E032); session completeness `0.875` (E006).
- Session windows (`_common`): asia `hr<8`, london `8–13`, ny `13–21`, late `≥21` (UTC).
- Trend context = 20-bar EMA-slope, `norm_slope>0.5` → bull / `<-0.5` → bear (`_profile.context_features`).

**Primary timeframe = M15** (matches the incoming 11-yr M15). Bar-count horizons are given in M15 bars,
with the M5 equivalent ×3. **Where a number cannot be derived without looking at data, it is NOT invented
— the edge is marked.** No testing is started here.

---

## GROUP 1 — 5 clear, data-eligible on XAUUSD M15+M5

### E001-V1 — Asia-Range Sweep-and-Reverse (London)
- **(3) Population/denominator:** every calendar day with a complete Asia session (`session=='asia'`,
  UTC 00:00–08:00) at ≥ **0.875** bar-completeness (E006). Asia range = `[min(low), max(high)]` over Asia
  bars. Denominator = Asia days that then produce a London sweep (below).
- **(1) Detection threshold:** a **sweep** = the first London bar (`session=='london'`, 08:00–13:00) whose
  extreme trades **≥ 0.25×ATR14 beyond** an Asia extreme (E027 departure). The swept extreme (high or low)
  and its direction are fixed at that bar.
- **(2) Horizon:** **52 M15 bars** (= 13h, London-open→NY-close 08:00→21:00; ×3 = 156 M5 bars) from the
  sweep bar.
- **(4) Reaction classification:** binary **reached-opposite** = within the horizon, any bar touches the
  opposite Asia extreme (`low ≤ level ≤ high`). Magnitude in R = (opposite extreme − sweep price) /
  (sweep price − swept extreme). No subjectivity.
- **(5) Free params:** none — completeness 0.875, sweep 0.25×ATR, horizon 52 bars, target = exact
  opposite level, all fixed.

### E002-V1 — Frankfurt Aggressive Move Reverses in London
- **(3) Population:** every day with a complete **Frankfurt window** (UTC 06:00–08:00, the final 8 M15
  bars of the Asia tag) at ≥0.875 completeness, that shows an aggressive move (below). Frankfurt net move
  `Δ = close(08:00) − open(06:00)`; direction = sign(Δ).
- **(1) Detection threshold:** **aggressive** = `|Δ| ≥ 1.5×ATR14[at 06:00]` (reuses the program's
  displacement multiple 1.5, its standing "strong move" convention).
- **(2) Horizon:** the **London window, 20 M15 bars** (08:00→13:00; ×3 = 60 M5) after the Frankfurt window.
- **(4) Reaction classification:** binary **reversed** = by the 13:00 bar, price has retraced **≥ 50%** of
  Δ against the Frankfurt direction (50% = the equilibrium convention, E032). Else **extended**.
- **(5) Free params:** none.

### E004-V1 — First Post-US-Open FVG Follow-Through
- **(3) Population:** each US-session day; instance = the **first** 3-bar FVG (E012 `detect_fvgs`,
  `PRIMARY_MIN_GAP=0.0`) whose middle bar timestamp falls in the **8-bar window 13:30–15:30 UTC** (COMEX
  RTH open 08:30 CT; **disclosed DST caveat**: EST months shift +1h — fixed rule, flagged, not a free
  choice). Direction = FVG polarity.
- **(1) Detection threshold:** standard 3-bar imbalance (`low[i]>high[i-2]` bull / `high[i]<low[i-2]`
  bear), any gap size (E012 primary).
- **(2) Horizon:** **50 M15 bars** from FVG formation (max `_profile.HORIZONS`; ×3 = 150 M5) — for both
  directional follow-through and fill.
- **(4) Reaction classification:** `movement_profile` in the FVG direction → continuation/reversal/stall
  at `1.0×ATR` (`_profile`); **fill** = binary, price re-enters `[zone_low, zone_high]` within the horizon.
- **(5) Free params:** none.

### E013-V1 — Order-Block Mitigation Reaction ⚠ OVERLAP
- **(3) Population:** order blocks per the E010/E015 detector (displacement `range>1.5×ATR14[prior]` +
  `body≥0.5×range`; OB = last opposite-colored bar within 10 prior bars) that are **mitigated** (zone
  touched: `low≤zone_high ∧ high≥zone_low`) within `REVISIT_HORIZON=480` bars. Instance = the first
  mitigation. Direction = OB original polarity.
- **(1) Detection threshold:** displacement 1.5×ATR, body 0.5 (E010/E015).
- **(2) Horizon:** reaction measured over **50 M15 bars** from the mitigation bar (`movement_profile`).
- **(4) Reaction:** continuation/reversal/stall at 1.0×ATR (`_profile`).
- **(5) Free params:** none.
- **⚠ OVERLAP FLAG (do not drop):** this operationalization is **near-identical to E015's first-mitigation
  event set** (same detector, same first-touch). The roadmap already ranked E013 highest for
  definitional-overlap risk. The contract is complete, but whether testing E013 adds anything beyond E015
  is a research-design decision for the CEO/Statistician — flagged, not resolved here.

### E016-V1 — Propulsion-Block Continuation on Retrace ⚠ OVERLAP
- **(3) Population:** propulsion blocks = the last opposing candle before a displacement
  (`range>1.5×ATR14[prior]`, `body≥0.5×range`; last opposite-colored bar within 10 prior bars — identical
  to the OB detector) that price **retraces to** (zone touched) within `REVISIT_HORIZON=480` bars.
  Direction = impulse (OB) polarity.
- **(1) Detection threshold:** displacement 1.5×ATR, body 0.5.
- **(2) Horizon:** continuation measured over **50 M15 bars** from the retrace/touch bar.
- **(4) Reaction:** continuation/reversal/stall at 1.0×ATR (`_profile`).
- **(5) Free params:** none.
- **⚠ OVERLAP FLAG:** operationally this is the **same event population as E010/E013/E015** (order-block
  retrace + continuation), differing only in narrative framing. Testing all four may re-measure one
  population. Flagged for the overlap check the roadmap requires.

---

## GROUP 2 — 5 conditional. Exact blocking condition per edge (for the CEO to decide if liftable).

### E022-V1 — VWAP Touch-and-Go — GATED ON CONFIRMED SESSION VOLUME
Fully operationalizable *except* the data gate. **(3)** population = session-VWAP touches while trending;
trend = `_profile.context_features` (20-bar EMA-slope, `norm_slope>0.5` bull / `<-0.5` bear). **(1)**
touch = a bar crossing the session VWAP (exact). **(2)** horizon = 50 M15 bars from the touch. **(4)**
`movement_profile` in the pre-touch trend direction, 1.0×ATR. **(5)** no free params **once VWAP is
computable.** **BLOCKING CONDITION: session VWAP needs a confirmed-provenance volume series** — the
existing `volume` column is an unconfirmed OTC/CFD proxy (registry l.64-65); confirm whether the incoming
M15/M5 carries verified volume. If yes, liftable immediately with the above.

### E031-V1 — 3-SD VWAP Reversion — GATED ON CONFIRMED SESSION VOLUME
**(1)** threshold already numeric in V0: **3rd** standard-deviation band of the session VWAP. **(3)**
population = bars touching the 3rd band; **(2)** reversion horizon = 50 M15 bars; **(4)** `movement_profile`
toward VWAP, 1.0×ATR; control = 1st/2nd-band touches (registry l.595). **(5)** no free params once
VWAP+bands are computable. **BLOCKING CONDITION: same as E022 — confirmed session volume** for
VWAP and its SD bands. Liftable if volume is verified.

### E018 — B-Book Stop Hunt — BLOCKED, NEEDS REFORMULATION (not a data gate, not invented)
The registry itself states the V0 as literally written references **broker-internal order routing, not
observable from price** and "needs reformulation into an observable price-based proxy before it can even
enter Discovery" (l.376-388). **I will not invent the proxy** — choosing the level type and excursion
threshold is a hypothesis-defining decision, not an operationalization. **BLOCKING CONDITION: a
CEO-authorized reformulation into an observable proxy** (the registry suggests "excursion beyond a
well-known level immediately followed by reversal"). Once the proxy hypothesis is authorized, it is
operationalizable from existing conventions (level types from E017/E025/prior-day; excursion 0.25×ATR;
reversal via `movement_profile`) — but that is a new hypothesis, not this V0.

### E019 — Volume Climax Exhaustion — BLOCKED, cannot pin without data
Two blockers. **(a)** needs a confirmed-provenance volume series (registry l.395-397). **(b)** the
detection threshold — what counts as a **"volume spike"** — has **no existing convention in any Flow A
script** to borrow (no script uses volume). Deriving it ("2×"? "3×"? top-decile? over what window?) would
require **looking at the data**, which is prohibited. **Per instruction I do not invent it.** BLOCKING
CONDITION: (a) confirmed volume, AND (b) a separately-decided, pre-registered spike definition — the
narrative "spike" alone does not determine a number.

### E023 — High Relative-Volume Breakout — BLOCKED, cannot pin without data
Same shape as E019. **(a)** needs confirmed volume. **(b)** "volume **significantly above** its recent
average" — the relative-volume multiple and averaging window have **no committed convention**; pinning
them needs data. **Not invented.** BLOCKING CONDITION: confirmed volume + a separately pre-registered
relative-volume threshold and window.

---

## Summary

| Bucket | Count | Edges |
|---|---|---|
| **Operationalized now (full V1, no gate)** | **5** | E001, E002, E004, E013⚠, E016⚠ |
| **Operationalized, gated on confirmed volume** | **2** | E022, E031 |
| **Blocked — cannot pin without data / reformulation (not invented)** | **3** | E018 (reformulation), E019 (volume + undefinable spike), E023 (volume + undefinable rel-vol) |
| **Impossible — missing instrument (marked in registry)** | **14** | E003, E007, E020, E021, E024, E030, E033-E040 |

**Count correction (owed):** the impossible bucket is **14, not 13** — the audit's "13" was an off-by-one
(it listed 14). 5 clear + 5 conditional + 14 impossible = 24 UNSTUDIED. The real testable pipeline on
incoming M15+M5 XAUUSD is **5 now + 2 if volume is confirmed = 5-7**, plus the 5 Set-B-burned edges
(E025/E026/E028/E029/E032) which are eligible for the never-seen 2011-2022 set.

**Nothing was operationalized by looking at data.** Every number above traces to the narrative V0 or a
pre-existing committed convention; where neither sufficed, the edge is marked, not filled in.
