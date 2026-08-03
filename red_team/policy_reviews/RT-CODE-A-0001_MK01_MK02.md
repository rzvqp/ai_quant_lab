# RED TEAM — CODE ATTACK (Ratification stage 3 of 4)
### RT-CODE-A-0001 · Targets: `code/market_structure.py` (MK-01) + `code/liquidity_mechanics.py` (MK-02)
**Date:** 2026-07-25 · **Auditor:** Red Team · **Mandate:** CEO — attack ambiguity, circularity, lookahead
**Frozen object:** commit **`8edbf9900b761b774b901a13a5b325be578468e6`** on `discovery-mk-matrix-v1` (read via `git show`; both files present, 292 + 229 lines).
**Prior stages:** Stage 1 Statistician 7/7 FIDEL vs D1–D7 (`e642c1c`); Stage 2 VE 12/12 tests, mypy clean, zero executability/leakage defects (`d586903`).
**Constraints honoured:** modules not modified · no remedy that changes a ratified decision · **no real data run** · verification = reading the frozen code only. Risk/vulnerability finding, not a ratification.

---

## 0. HEADLINE

**Lookahead: clean. Circularity: none in-module. But the attack found three real problems, one of them a logic defect that the prior two stages could not have caught by construction.**

- ✅ **Lookahead (D1)** — PASS everywhere. `confirmed_idx = idx+k` discipline is correct; breaks use only swings with `confirmed_idx < c`; sweeps require `available_idx < c`; `sweep_against_reference` delegates lag to the caller with an explicit warning. No field uses information unavailable at decision time.
- ✅ **D6 (sweep, intrabar)** — PASS. `low[c] < p AND close[c] > p` is a **completed-bar** signature; it is **path-agnostic** (never assumes low-then-close ordering within the bar) and forward-free.
- ✅ **D3** — PASS, clean. The ~2-per-block loss is **positional, not selective** (block-edge k-bars + first swing per type UNCLASSIFIED); correctly motivated by quarantine; no hidden bias. *(Detail in §2.)*
- ✅ **Circularity** — none in these modules (selection windows are backward fractals; no measurement window feeds selection — the measurement window is downstream/Statistician's, as in the PDH policy).

- 🔴 **F1 — D2 loss is SELECTIVE, not neutral** (answers the CEO's exact question). *Selection bias, not just volume reduction.*
- 🔴 **F2 — consumption cascade: spurious over-counted breaks against superseded levels** — a reachable logic consequence, invisible to fidelity/leakage tests. **Strongest finding.**
- 🟡 **F3 — undeclared, unenforced idx-ordering precondition** (VE-flagged; confirmed and extended to a second function; failure is silent).
- 🟡 **F4 — simultaneous opposite CHoCH on one bar** (minor ambiguity).

---

## 1. F1 — D2 rejects equalities SELECTIVELY *(answer: the loss is selective)*

`detect_swings`: `is_high = all(high[i] > high[j] for j in window if j != i)` — **strict `>` on both sides.**

**A plateau produces zero swings.** For a two-bar equal top `… , 3, 3, …` where 3 is the local max: bar *i* fails `high[i] > high[i±1]` (3 > 3 is false), and its equal neighbour fails identically. Double tops, triple tops, and every flat extreme are **entirely invisible** to `detect_swings`. Verified by construction, no data needed.

**Why this is selective, not neutral — and why it matters *here specifically*:** equal highs / equal lows are not a random subset of extrema. They are **the** canonical resting-liquidity structure — the exact object MK-02 exists to model (`build_pools`: HH/LH → ABOVE pool = "buy-stops above equal highs"). But an equal-high never becomes a `Swing` (D2 strict), so it never becomes a labelled swing, so **`build_pools` can never emit a pool at an equal-high cluster.** The upstream tie-break silently removes the very structures the downstream liquidity model is built to detect.

- The surviving swing population is **biased toward sharp single-bar reversals and against flat/plateau reversals.**
- The bias is **regime-dependent**: the quantified cost rises 24.8 → 42.9 → 59.7 % as the grid coarsens, and equalities proliferate at **low ATR / two-decimal gold**, i.e. in **consolidation regimes** — precisely where equal-high/low liquidity pools dominate. So the detected-structure set is conditioned on volatility state in a way **confounded with the phenomenon under study.**
- The mentioned-but-unimplemented alternative (**strict-left / non-strict-right**) would retain **one** bar per plateau — it is the tie-break that *keeps* equal-high structures. The ratified choice (strict both) is the one that **maximally excludes** them.

**Verdict on F1:** the code is correct and lookahead-safe; **the ratification's cost is understated.** "42.9 % of swings lost" reads as neutral decimation; it is in fact a **selection bias against equal-extreme liquidity structures**, strongest exactly where MK-02's subject lives. *I do not propose changing D2* (ratified); I report that the loss is **selective**, which is the question asked. This belongs in the CEO's ratification calculus.

---

## 2. F-D3 — the fixed 2-per-block loss is genuinely neutral *(attack found nothing)*

Two mechanisms: (a) block-edge — `for i in range(block.start+k, block.end-k)` plus `contains_window` drops the first/last *k* bars as swing *centres*; (b) `label_structure` marks the **first** high and **first** low per block `UNCLASSIFIED` (no in-block reference; borrowing across the quarantine boundary is forbidden — D3). `build_pools` then skips UNCLASSIFIED, so exactly **one high + one low per block** are lost to the pool/break layer.

**Attack result: nothing selective.** The loss is **positional** (block edges + first-of-type), not conditioned on price shape or regime — unlike F1. It is the minimum forced by the quarantine (no cross-block reference). The redundant `contains_window` check inside the already-bounded range is harmless. **D3 survives clean.**

---

## 3. F2 — consumption cascade: spurious breaks against superseded levels *(strongest finding)*

**`detect_breaks` activation loop** rebuilds the live reference each bar as the **last same-label swing in list order** that is confirmed and unconsumed:
```
for s in block_swings:
    if s.confirmed_idx >= c or s.idx in consumed: continue
    if s.label is HH: live_hh = s      # ends = most-recent unconsumed HH
...
if live_hh and px > live_hh.price: BOS_BULL; consumed.add(live_hh.idx)
```
Consuming the live reference **re-exposes an older, already-superseded same-label swing** on the next bar.

**Minimal reachable reproduction (described, not run):** two highs in one block, both confirmed, neither yet broken — `HH₁ = 100`, `HH₂ = 100.5` (HH₂ > HH₁ ⇒ both labelled HH). A breakout bar closes `101`:
- bar *c*: `live_hh = HH₂` → **BOS_BULL vs 100.5**, `consumed.add(HH₂.idx)`.
- bar *c+1* (close still ≥ 100): `HH₂` skipped ⇒ `live_hh = HH₁ = 100`; `101 > 100` → **a second BOS_BULL vs 100.**

The second break is **spurious**: 100 was already below the market the instant price cleared 100.5; re-breaking it is not a new structural event. In a trend with *N* ascending HHs, a single breakout emits **one real break + up to N−1 stale-reference breaks**, one per subsequent bar, until all older HHs are consumed. Symmetric for LL/BOS_BEAR. This **over-counts structural breaks** and would corrupt any downstream statistic (break frequency, BOS/CHoCH ratios, break spacing).

**Why the prior stages did not catch it:** it is **not lookahead** (all references confirmed `< c`), **not leakage**, **not an executability/crash defect**, and **not an infidelity to D1–D7** — the literal D7 text (*"a swing is consumed by the first break that exceeds it"*) is, read strictly, **satisfied** by breaking HH₁ at *c+1*. So Stage 1's 7/7-fidelity and Stage 2's 12/12-executability/leakage batteries would pass it by construction; it needs a **semantic** test with ≥2 ascending same-label swings.

**This is therefore an AMBIGUITY, not a bug against spec:** D7 is silent on *"is an older same-label swing still a live break reference after a newer one forms and is consumed?"* The code answers **yes** (fall back to it); the analytically-correct answer is **no** (a superseded internal level is not live resistance). The specification admits both readings; the implementation took the over-counting one. **I do not design the fix** (that would touch the D7 rule). I state the defect precisely and hand the resolution to the CEO. **This is the finding that should gate ratification.**

---

## 4. F3 — undeclared, unenforced idx-ordering precondition *(VE-flagged; confirmed + extended)*

VE noted `detect_breaks` picks the live reference as the **last in input-list order**, relying on idx-sorted swings — true of `detect_swings` output, but **undeclared**.

**Confirmed, and it is load-bearing in a second function too:** `label_structure` classifies each swing against `last_high.get(b)` / `last_low.get(b)` — the previous same-type swing **in iteration order**. If the list is not idx-sorted, the "previous" swing is the wrong one, so **HH/HL/LH/LL labels themselves are computed wrong**, which then propagates into `build_pools` (pool sides) and `detect_breaks` (references).

**What happens on violation:** **silent wrong output — no exception, no validation.** Neither function asserts sortedness. The canonical pipeline (`detect_swings → label_structure → …`) is safe because `detect_swings` emits ascending-idx swings **within each block**; but any caller that concatenates two `detect_swings` results, re-sorts by price/`confirmed_idx`, hand-builds a list, or passes blocks out of order **silently corrupts labels and breaks**. `build_pools` is order-independent (per-swing map) and unaffected.

**Verdict:** not a lookahead, not a current-pipeline bug — a **latent trap**. The precondition (*swings sorted by idx within block*) is real, undeclared, and unenforced, and its violation is silent. Declaring/asserting it does **not** change a ratified decision; recorded as a required precondition, resolution to CEO.

---

## 5. F4 — simultaneous opposite CHoCH on one bar *(minor ambiguity)*

`detect_breaks` runs the bullish `if/elif` and the bearish `if/elif` as **two independent blocks** on the same `close[c]`. When a compressed structure yields `live_lh.price < close[c] < live_hl.price` (a Lower-High priced **below** a Higher-Low — reachable near a contracting-triangle apex), **both** `CHOCH_BULL` (vs LH) and `CHOCH_BEAR` (vs HL) fire on one close → two contradictory change-of-character events at the same bar, bullish appended first (order artifact). Lower severity (needs crossed lh/hl), but it is a genuine ambiguity/over-count on a single bar. Noted for the ratification.

---

## 6. D6 and D7 — explicit target answers

**D6 — "does intrabar order matter?" NO.** `detect_sweeps` evaluates `penetrated` and `back_inside` from the completed bar's `low[c]`/`high[c]` and `close[c]`. It never assumes the low occurred before the close; it reads the bar's footprint, not its path. Forward-free (`available_idx < c` enforced). **Clean — the one genuinely lookahead-free primitive, as documented.**

**D7 — "does consumption block something legitimate?" YES, for pools.** `detect_sweeps` consumes a pool at first sweep (`consumed.add(k)`), so a **genuine second raid of the same resting level** — a core, recurring liquidity behaviour — is **never detected**. The re-arm alternative is documented-but-unimplemented (ratified one-shot). This is a **scope limitation**, not a bug, and it **compounds with F1**: F1 removes equal-high pools entirely; D7 caps each surviving pool at one sweep. For a *liquidity* module, first-touch-only materially narrows what can be observed. (For `detect_breaks`, one-shot consumption is more defensible in isolation — but see **F2**, where the consumption fallback is actively harmful.)

---

## 7. VERDICT

| Target | Result |
|---|---|
| **Lookahead (D1)** | ✅ PASS — no field uses unavailable-at-decision information; `confirmed_idx`/`available_idx` discipline correct throughout |
| **D6 sweep intrabar** | ✅ PASS — completed-bar, path-agnostic, forward-free |
| **D3 block loss** | ✅ PASS — positional, neutral, minimal-for-quarantine |
| **Circularity** | ✅ PASS — no measurement-window feedback in-module |
| **D2 equality rejection (F1)** | ⚠️ **Loss is SELECTIVE** — biased against equal-extreme liquidity structures (MK-02's own subject), regime-dependent; ratification cost understated |
| **Consumption cascade (F2)** | 🔴 **DEFECT** — spurious over-counted breaks against superseded same-label levels; reachable with 2 swings; invisible to fidelity/leakage tests; a D7 ambiguity resolved the over-counting way |
| **Ordering precondition (F3)** | 🟡 **Undeclared + unenforced** — load-bearing in `label_structure` *and* `detect_breaks`; silent wrong output on violation |
| **Opposite CHoCH same bar (F4)** | 🟡 minor ambiguity / over-count |
| **D7 pool consumption** | ⚠️ blocks legitimate re-sweeps; scope limitation; compounds F1 |

**What survives:** the modules are **lookahead-free and circularity-free**, and D3/D6 are clean. The primitives are, on those axes, sound.

**What does not survive unqualified:**
- **F2 is the one I flag directly as a fatal-for-correctness defect for the module's stated purpose** (it silently inflates the break count in exactly the trending/breakout conditions where breaks matter most). It is an *ambiguity in D7's scope*, not an infidelity — which is precisely why stages 1–2 passed it. **The ratification should not proceed on `detect_breaks` until F2's reading is decided.**
- **F1** changes the *interpretation* of every downstream result: MK-01/MK-02 output is computed on a swing set **selectively stripped of equal-extreme structures**, most severely in low-ATR regimes. Not a code fault; a standing condition on all results.
- **F3** must be declared/asserted before any non-canonical caller uses these functions.

## 8. HANDOFF

→ **CEO, for the final ratification decision.** Red Team does not ratify. Recommendation for the decision (not a remedy design):
- **F2** is a semantic defect that fidelity/executability testing cannot surface — it needs an explicit ruling on whether a superseded same-label swing remains a live break reference. Until then, `detect_breaks` break counts are inflated in trends.
- **F1** and **D7** should be recorded as **standing interpretive conditions** on all MK-01/MK-02 output (selective toward sharp reversals; blind to equal-extreme pools and to re-sweeps), so downstream (Statistician) never reads the structure set as complete.
- **F3** requires the idx-order precondition to be stated and enforced.
- Lookahead, circularity, D3, D6 — **no action needed.**

Nothing modified; nothing run on data; no ratified decision rewritten. Integrity/finding items logged (W11–W12).

**Attack ends. Red Team awaits the CEO's ratification decision.**
