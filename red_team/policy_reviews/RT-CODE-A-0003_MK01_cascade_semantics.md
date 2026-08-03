# RED TEAM — CODE RE-ATTACK · MK-01 cascade break semantics
### RT-CODE-A-0003 · Target: the new cascade semantics, commit `0000225` (vs `f4f8fab`)
**Date:** 2026-07-25 · **Auditor:** Red Team · **Mandate:** CEO — attack the cascade semantics (targets: BOS∧CHoCH co-occurrence, order, F4). Do not reopen D2/D7-pools/F3; liquidity_mechanics untouched.
**Method:** read the diff `f4f8fab → 0000225`, the rewritten `detect_breaks`, and the new tests (`tests/test_cascade_breaks.py`). **No data run.**

## 0. WHAT CHANGED (verified from the diff)
Per bar `c`, the old code kept **single-slot** `live_*` pointers (only the most-recent swing per label) and used **intra-direction `if/elif`** (a BOS suppressed a same-bar CHoCH). The new code collects **ALL** active (`confirmed_idx<c`, unconsumed) swings exceeded by `close[c]` into `hits`, sorts them **descending by `idx`**, and emits one break per hit at `c`, consuming each immediately. This fixes both delay vectors and, critically, the **lost-break** (a suppressed CHoCH that never re-fires when the close falls back). This is the delivery of what D7 already specified (each distinct swing → exactly one break); D2/D7-pools/F3 unchanged — **only the bar on which a break is recorded changes.** My RT-CODE-A-0002 mis-timing finding is thereby resolved (breaks are no longer staggered), and the Statistician's measurement (**40.9 % of break-bars carry ≥2 breaks; 542 references were lost outright**) shows it was frequent and, worse, **count-non-conserving** under the old code.

---

## 1. TARGET 1 — BOS ∧ CHoCH on the same bar: **NOT double-counting** (survives), with one dependence flagged
Two breaks on one bar reference **distinct swings** (distinct `idx`, distinct labels); each swing yields exactly one break; the shared `consumed` set is keyed by unique `idx`. So the Statistician is right: **not double-counting** — it conserves the count D7 requires. `test_bos_and_choch_same_bar_distinct_refs` confirms {ref 8, ref 13}.

**Deliberate attack — the events are distinct but often NOT independent.** When a BOS breaks an HH that sits **above** a co-broken LH (the common nested case: highs `…, HH=120, LH=115, …`, a close of 125 exceeds both), the CHoCH-vs-LH is **structurally implied** by the stronger BOS-vs-HH (`close>120 ⟹ close>115`). The two are distinct references but a **dependent pair** — the higher break entails the lower. A downstream that counts CHoCH events as *reversal* signals would **over-count reversals inside strong continuations**. This is not a double-count and does not break the count-conservation; it is a **dependence the "two independent events" framing understates.** Flagged for the ratification, not a defect of the emission.

## 2. TARGET 2 — the ordering claim is **INACCURATE for the lost-break population** (finding)
The docstring's rationale: descending-by-`reference_swing.idx` *"keeps the reference the old code already chose first (`_first_break_after` with `b.idx < best.idx` cannot separate equal idx) → the change stays strictly TIMING, not reference."*

- **For same-label cascades it holds.** Old staggered HH@18→c, HH@13→c+1, HH@8→c+2; `_first_break_after` (earliest bar) got HH@18. New emits all at `c`, descending → HH@18 first. Same first-reference. `test_sustained_cascade` (refs [18,13,8]) matches.
- **For the cross-kind / lost-break population it does NOT hold** — and that is exactly the population the fix targets. Old **suppressed and lost** the LH CHoCH (if/elif), so old's only bar-`c` break was the surviving **BOS vs HH@8**; `_first_break_after` returned **ref 8**. New **delivers** the LH@13 break AND, being the higher idx, emits it **first** → `_first_break_after` (same-bar tie broken by list order, per the stated consumer model) now returns **ref 13**, a **different reference and a different kind (BOS→CHoCH).** This is **demonstrable from the code's own `test_bos_and_choch_same_bar_distinct_refs`**, which asserts `br[0].reference_swing.idx == 13` — whereas the old semantics would have surfaced ref 8.

**So the change is *not* "strictly timing, not reference"** for the ≥2-break bars (40.9 %): the newly-delivered breaks can become the first reference and **displace** the one the old consumer saw. Whether it *matters* depends on `_first_break_after`'s real comparison — **and that consumer is NOT in this commit** (only a stray string in `config/generate_split_manifest.py`; the actual consumers are downstream, e.g. `trading_strategies.py`, another branch). **Recommend the CEO/Statistician verify the first-reference stability against the real `_first_break_after` consumers before ratifying the "timing-only" claim.** If those consumers key off the first break's reference/kind (a 20-bar eligibility window would), their selection changes on 40.9 % of break-bars.

## 3. TARGET 3 — F4 (simultaneous OPPOSITE breaks): **surface genuinely grew; still unresolved; now in scope**
My RT-CODE-A-0001 F4 (CHOCH_BULL vs LH **and** CHOCH_BEAR vs HL on one bar when `lh.price < close < hl.price`) is now **more reachable**: the all-hits loop evaluates **every** active swing, so multiple LHs below the close and HLs above it all fire → **more simultaneous opposite breaks**, exactly as the Statistician warned. A `BOS_BULL` (HH) can also co-fire with a `CHOCH_BEAR` (HL) when `HH.price < close < HL.price` (an old low-high below a recent higher-low — reachable in a strong uptrend or a triangle apex).

**Assessment:** like Target 1, this is **not** a count/consumption defect — each is a distinct valid break under D7. But it emits **structurally contradictory signals on one close** (bullish *and* bearish change-of-character), and the new semantics **amplifies the frequency**. detect_breaks is arguably *correct* to emit every distinct break; the incoherence lives in **downstream interpretation**, which needs an explicit rule for contradictory same-bar signals. **This does not block the cascade fix** (which conserves count correctly); it is an **inherited open item made more visible** — resolution is a downstream/ratification decision, not a change to `detect_breaks`.

## 4. TEST COVERAGE — "sufficient? what is not exercised?"
`tests/test_cascade_breaks.py` (4) covers, with an in-test replica of the OLD semantics for contrast: (a) sustained same-label cascade (3 BOS at one bar, descending, old=1), (b) suppressed-and-lost CHoCH now delivered (old=0, new=1), (c) BOS∧CHoCH same bar / distinct refs / descending, (d) descending order across kinds. **Solid on the core.**

**Not exercised:**
- **F4 — simultaneous OPPOSITE breaks** (CHOCH_BULL ∧ CHOCH_BEAR, or BOS ∧ opposite CHoCH). No test builds `lh.price < close < hl.price`. The behavior the Statistician says *grows* is **unasserted** (do both fire? in what order? is the count conserved?).
- **The `_first_break_after` preservation claim** (§2) — tests assert the descending **order**, but **no test** verifies the consumer's *first-reference selection* is preserved old-vs-new. The load-bearing "timing-only" claim is asserted only by the docstring.
- **Aggregate count conservation** — one lost break is shown delivered, but no test asserts, over a complex multi-swing series, that **every** old-or-should-have-been break appears exactly once and none vanishes (the 542-figure is a measurement, not a regression guard).
- **Cross-direction order edge** — where a **bearish** highest-idx hit would emit before a co-occurring bullish break (the case that changes `_first_break_after`); all order tests are bullish/CHoCH-bull.
- **High multiplicity** — max-24-per-bar is measured but tests use ≤3.

---

## 5. VERDICT

**The cascade semantics SURVIVES.** It correctly conserves the break count — fixing both delay vectors and the count-losing suppression — and BOS∧CHoCH co-occurrence on distinct references is genuinely **not double-counting**. The emission logic is sound; my prior mis-timing finding is resolved.

**Two findings for the ratification decision (neither blocks the count-conservation fix):**
1. **Target 2 — the "strictly timing, not reference" rationale is inaccurate** for the ≥2-break bars (40.9 %): newly-delivered breaks can become the first reference and displace the one the old consumer saw (shown by the code's own test). The real `_first_break_after` consumer is **not in this commit** — **verify first-reference stability against `trading_strategies.py` (s2/s3/s10/s11) before relying on "timing-only."**
2. **Target 3 / F4 — simultaneous opposite breaks are now more frequent and remain unresolved**; not a count defect, but a contradictory-signal surface that needs a downstream interpretation rule; **untested**.

Plus coverage gaps: F4, the `_first_break_after` preservation claim, aggregate count conservation, and the cross-direction order edge are not exercised.

## 6. HANDOFF → CEO, for the final MK-01 / MK-02 ratification.
The cascade fix is sound and conserves the count. Before ratifying: (a) verify the **first-reference stability** claim against the real downstream consumers (not in this commit); (b) decide the **contradictory-signal (F4)** interpretation rule; (c) consider adding the four missing tests. Red Team designs no fix; reopens neither D2 nor D7-pools nor F3; `liquidity_mechanics.py` untouched. Nothing modified, nothing run on data.
