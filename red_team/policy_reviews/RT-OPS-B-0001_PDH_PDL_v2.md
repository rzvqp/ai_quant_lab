# RED TEAM — POLICY ATTACK, PART B (DEMO_BASELINE)
### RT-OPS-B-0001 · Target: CAND-0001 PDH-PDL **v2.0**, Part B (risk management)
**Date:** 2026-07-25 · **Auditor:** Red Team · **Mandate:** CEO — attack Part B only (Part A already SURVIVED, RT-OPS-A-0001; not re-run)
**Frozen object:** `POLICY_PDH_PDL_v2.md` @ commit **`1558397`** on `alpha-automation-v1` (read via `git show`).
**Constraints honoured:** Part A not attacked · no alternative risk method proposed · policy not modified · **no data run**. Verification = reading the frozen policy + the referenced convention `docs/MIN_STOP_FLOOR_PREREG.md`.

> Part B goes to a **DEMO account** (real fills). Per the mandate, any safety defect is stated **directly**.

---

## 0. HEADLINE

The risk mechanism is **lookahead-free, circularity-free, and carries no hidden optimization** — on those axes it is clean, and unusually so (zero tunable numeric parameters). **But two direct safety defects exist, both because Part B is silent on intrabar fill resolution and does not invoke the repo's own worst-case convention (`MIN_STOP_FLOOR_PREREG`) that governs exactly these cases.** They are not flaws of the *mechanism*; they are an unbound **DEMO-execution** gap that must be closed before the policy trades.

---

## 1. LOOKAHEAD — PASS (including the day-boundary question)

Every Part-B coordinate is known at entry (`touch_idx+1` open):
- **stop** = `low/high[touch_idx]` — the touch (trigger) bar's extreme; the touch bar precedes entry. ✅
- **target** = the opposite prior-day level (`PDH`/`PDL`) — from `compute_prior_day_levels`, known at the current day's first bar. ✅
- **day boundary (time-stop)** — *the CEO's pointed question: known at entry, or derived from future bars?* **Known at entry.** The boundary is the **17:00-NY DST-aware clock anchor** (`resample_ny.py`, feeding `day_index`) — a **scheduled wall-clock time**, deterministic in advance, **not derived from future OHLC**. The exact closing bar is *observed causally* when the clock reaches the anchor (equivalently, when the next bar's `day_index` differs); it is never *predicted* from future price. ✅ **No lookahead.**

The bar-count to the boundary varies (gaps), but Part B correctly expires on the **event** (day-index change), not a fixed bar number — consistent with Part A's counted-not-assumed treatment. **Lookahead: PASS.**

---

## 2. CIRCULARITY — PASS

The stop is *anchored* on the touch bar, which is also the trigger bar — the CEO's concern. But:
- **selection window** (trigger detection) ends at `touch_idx`;
- **measurement window** (stop/target/time-stop resolution) begins at `touch_idx+1` (entry) and runs forward to the day boundary.

The touch bar itself is **not** in the measurement window (entry is next-open). The stop is a **fixed price coordinate** read off the touch bar, but whether it is *hit* is measured strictly on bars `> touch_idx`. Selection and measurement **do not overlap**. This is the same clean separation as Part A's `entry@next-open` and directly satisfies the W-e010 interface guard carried from RT-OPS-A-0001. **Circularity: PASS.**

---

## 3. HIDDEN OPTIMIZATION — PASS (no sign of a data-informed choice)

- **Zero tunable numeric parameters.** stop = a bar extreme; target = an already-produced level; time-stop = an existing day boundary; sizing = 1R. **No ATR multiple, no RR ratio, no bar-count, no percentile.** A variant with **no free number has no optimization surface** — the strongest possible evidence against curve-fitting. The "single variant chosen before results" claim is credible *because there is nothing to tune*.
- **Justification is a general/negative result**, not a PDH/PDL-specific fit: fixed-ATR gave an *identical* 0.378–0.385 winrate across six mechanisms ⇒ structure dominates ⇒ go structural. That motivates the *direction*, not a tuned value. The exploratory PDH/PDL figures were de-privileged in Part A and are not invoked.
- **Sizing choice** explicitly *avoids* a parameter (rejects the "CEO-deauthorized 5% equity"), moving to parameter-free 1R.
- **No suspicious coincidence** with a prior winning configuration was found.

*One honest note (not a defect):* choosing *which* structural anchors (touch-bar extreme for the stop; opposite level for the target) is a **design-level** degree of freedom among structural alternatives (e.g. source-swing stop, measured-move target). Alpha took the minimal/most-obvious pair. That is defensible DEMO_BASELINE minimalism, with **no evidence** it was results-informed. **Hidden optimization: PASS.**

---

## 4. SAFETY — two direct defects

### 🔴 S1 — Same-bar stop **and** target: intrabar resolution order UNSPECIFIED; the repo's worst-case convention is NOT applied.
Part B says the trade "resolves at the **first of**: stop breached · opposite level reached · time-stop." On a **single wide bar** that spans *both* the stop and the opposite level, "first" is **undetermined** without the intrabar path — and Part B specifies **no** resolution order and makes **no** worst-case assumption. Verified: the policy contains **no** reference to intrabar ordering, tie-breaks, or the worst-case model (grep: only the "first of" line).

The repo **already has the convention** for exactly this — `docs/MIN_STOP_FLOOR_PREREG.md`:
> *"A trade is marked **INVALID EXECUTION** (excluded, not counted) … [if] entry/exit inside the same bar with **ambiguous fill that the worst-case model cannot resolve**."* (and "intrabar ordering" is a per-trade audit field.)

**Part B does not invoke it.** Consequence for a DEMO account: if the execution engine defaults to *target-first* (optimistic), every stop-and-target-in-one-bar case is scored a win it may not have been — a **systematic upward bias** in reported DEMO results. This is a direct fill-integrity hole. **Stated directly, as instructed.**

### 🔴 S2 — No `min_executable_risk` floor: unbounded position size at a near-zero stop distance.
Part B guards the **≤ 0** case ("if next-open is already beyond the stop → no trade" — this correctly fail-closes the *zero-distance* and *stopped-at-entry* cases, so 1R never divides by zero). **But it does not floor a tiny-but-positive distance.** Sizing is "1R normalized to the stop distance", so as `entry − stop → 0⁺`, position size → ∞. A touch-bar extreme one tick below next-open ⇒ a 1-tick stop ⇒ an enormous 1R position. The repo convention floors exactly this (`strategy_stop_distance < min_executable_risk` ⇒ **floored to `min_executable_risk`**); **Part B does not apply the floor.**
Part B's defense ("all reported R-metrics are sizing-invariant") covers **R-reporting** but **not the DEMO account** — a real account has finite equity/margin, where an unbounded near-stop size is a live risk. **Stated directly.**

### 🟡 S3 — Target already visited earlier in the day (minor).
The at-entry guard rejects a next-open *already beyond* the target. It does **not** address a target that was **touched earlier in the day and left** before the entry trigger (e.g. PDH tagged at 10:00, then a PDL-long triggers at 14:00 targeting PDH again), nor whether a target level already **consumed** as a trigger (D7) is still a valid target. Not a lookahead/crash; an unhandled case that the Statistician's DEMO criteria should pin.

---

## 5. AMBIGUITY — the intrabar order (same as S1)

"First of stop / opposite level / time-stop" is **order-unspecified intrabar**. Three collisions are undefined: stop∧target (S1, worst), stop∧time-stop (a stop on the day's last bar), target∧time-stop. The repo's worst-case/INVALID-EXECUTION convention resolves all three; Part B invokes none. This is one defect surfaced twice (safety + ambiguity); the fix is a **binding**, not a new method.

---

## 6. VERDICT

| Axis | Result |
|---|---|
| Lookahead (incl. day boundary) | ✅ PASS — all coordinates known at entry; boundary is clock-anchored, not future-derived |
| Circularity | ✅ PASS — measurement strictly forward of the touch bar |
| Hidden optimization | ✅ PASS — zero free numeric parameters; general/negative justification; no results-informed sign |
| **Safety — same-bar stop∧target (S1)** | 🔴 **DEFECT** — intrabar order unspecified; worst-case convention not applied → optimistic-fill bias risk on a DEMO account |
| **Safety — no executable-risk floor (S2)** | 🔴 **DEFECT** — unbounded size at near-zero stop distance; repo floor not applied |
| Safety — target-visited-earlier (S3) | 🟡 minor, unhandled |
| Ambiguity (intrabar order) | 🔴 = S1 |

**→ SURVIVED_RED_TEAM_A — CONDITIONAL, with a hard pre-DEMO safety gate.**

**Reasoning, stated plainly:** the risk *mechanism* survives every adversarial axis — it is lookahead-free, circularity-free, and (uniquely) has no optimization surface. The two safety defects are **not** flaws of the mechanism and **not** unresolved: the repo already carries the exact convention that governs them (`MIN_STOP_FLOOR_PREREG` / "Engine v2": worst-case intrabar fills, INVALID-EXECUTION marking, `min_executable_risk` floor). Part B's fault is **silence** — it neither restates nor binds that convention. So the policy does **not** fail the attack, but it **must not reach the DEMO account** until execution is bound to that convention.

**Hard gate (Statistician DEMO criteria — not a remedy I design):** before any DEMO fill,
1. intrabar collisions (S1, and stop∧time-stop, target∧time-stop) must resolve under the **worst-case / INVALID-EXECUTION** convention of `MIN_STOP_FLOOR_PREREG`, **not** an optimistic default;
2. the **`min_executable_risk` floor** (S2) must apply to the 1R sizing;
3. the target-already-visited case (S3) must be given a defined rule.
If the DEMO engine cannot be shown to enforce Engine-v2, **the policy must not trade** — the safety defects are then live.

## 7. HANDOFF
→ **Statistician, for the DEMO criteria** — carrying the three-point hard gate above (plus the Part-A controls W-sel/W-conf/W-ovl/W-e010 from RT-OPS-A-0001). Part A unchanged and already SURVIVED. Nothing modified, nothing run on data, no risk method proposed.

**Attack ends. Red Team awaits the Statistician's DEMO-criteria binding / CEO routing.**
