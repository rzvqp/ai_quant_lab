# RED TEAM — POLICY ATTACK, PHASE A
### RT-POLICY-A-0001 · Target: PDH/PDL policy v1.1, PART A (entry mechanism)
**Date:** 2026-07-25 · **Auditor:** Red Team · **Mandate:** CEO — Phase A attack on Part A only
**Target object:** `POLICY_PDH_PDL_v1.md` at commit **`78634d5`** on **`alpha-automation-v1`** (read via `git show`, bound to that exact object).
**Scope:** PART A (context/regime/trigger/entry/invalidation/no-trade/expiry) **only**. Part B is unspecified *by decision*, not omission — **not attacked, no risk method proposed.**
**Constraints honoured:** policy not modified · no remedy designed · **nothing run on data** · Part B untouched. Verification used **branch/commit state + primitive definitions** (documentation/code definitions), never execution.

> Risk/vulnerability finding, not a laboratory decision ([RISK_VERDICTS](../methodology/RISK_VERDICTS.md)). Contrary evidence → "compatible with limitation", never "refuted", per E10.

---

## 0. HEADLINE

**The entry mechanism itself survives the attack** — it is fully specified, mechanical, and **lookahead-safe**, and I confirmed each field against the *actual* ratified primitives, not against the policy's description of them. Targets 4 (lookahead) and 6 (falsifiability) are genuine PASSES; the mechanism is *more* falsifiable than most Alpha Discovery Candidates.

**But the handoff is blocked by one fatal-for-handoff defect, stated directly:**

> **F-A1 — The ratified primitives Part A is "grounded in" do not exist on the policy's own branch.**
> `code/institutional_levels.py` (with `compute_prior_day_levels`, `detect_level_touches`, `LevelKind`, …) is **not in commit `78634d5`'s tree** and **not on `alpha-automation-v1`**. It exists **only on `discovery-mk-matrix-v1`** (verified: `git branch --contains` of the implementing commit `1930467` yields `discovery-mk-matrix-v1` and its remote, and **not** `alpha-automation-v1`; `git ls-tree -r 78634d5` finds no such file; no `def compute_prior_day_levels` exists in `78634d5`'s tree).
>
> This is **the same failure mode Part B openly declares** ("the cited v8.5 M_031–M_034 was confirmed nonexistent") and a **sibling of W9** (D3 fix on `flow-c-foundation`, never merged to `statistician-foundation`). The policy's central claim — *"built on ratified primitives **in the repo**"* — is **branch-conditional and false on its own branch.** A Statistician who picks up the policy on `alpha-automation-v1` finds its grounding absent, exactly as Part B's grounding is absent.
>
> **This does not falsify the mechanism** (the code exists and is correct *where* it exists — see Target 4). It falsifies the *handoff as-is*: Part A is not actionable on the branch it was submitted on. **Resolution is an architecture matter, not Red Team's to design** (cf. W9); recorded as integrity item **W10**.

---

## 1. TARGET-BY-TARGET

### Target 1 — Candidate selection: **post-hoc selection concern is VALID, but already neutralised by the policy itself.**
PDH/PDL was chosen after examining 9 mechanisms; "6/7 years positive" with P(≥6/7 | p=0.5)=0.0625, so across 9 mechanisms the chance expectation is 9×0.0625 ≈ **0.56 occurrences**. Observing one 6/7 mechanism among nine is **exactly what chance produces** — the 6/7 carries **no evidential weight** after the 9-way search.
**Attack outcome:** the concern lands on the *exploratory figures*, which the policy **explicitly de-privileges** ("carry no privileged status and are not relied on here"). The policy makes **no statistical claim**; it hands the edge question to the Statistician. So this does **not** wound Part A as a *specification* — but it hard-constrains the downstream test: **PDH/PDL must be evaluated selection-corrected (as 1 of 9), and the in-sample 6/7 is not evidence.** Same posture as DC-0004 (enters as a hypothesis, not a result). **Survives as a spec; carried as warning W-sel.**

### Target 2 — Level effect vs session effect: **unresolved confound; a required downstream control, not a mechanism defect.**
London is positive across **all 8** typed mechanisms → London is a **common session factor** that lifts everything; it is not evidence for any specific level. PDH/PDL being positive in **4/4 sessions** is the stronger fact — it is *not* confined to London — but "positive in every session" is equally consistent with a **general session-liquidity / long-beta** effect as with a **level-reaction** effect. Nothing in Part A isolates a *level-specific* reaction from "price reacts at salient intraday times generally."
**Attack outcome:** not fatal (the mechanism is defined regardless), but the level-vs-session confound is **unbroken**. The Statistician must test PDH/PDL against **both** a session-matched null **and** a level-matched null (e.g. a random/placebo intraday reference level) — if a placebo level reacts the same in 4/4 sessions, the effect is session/structure, not the prior-day level. Echoes DC-0002 (K05) and DC-0004 (session-vs-level). **Survives; carried as warning W-conf.**

### Target 3 — Overlap: **plausibly distinct at the event-set level; one check outstanding.**
356 triggers, **<40% overlap with most** other types → **>60% of PDH/PDL triggers are unique**, which is real distinctness as an event set. The gap: "<40% with *most*" leaves open whether **one** type overlaps heavily. If a single mechanism shares >60% of PDH/PDL's triggers, PDH/PDL may be redundant with that one specifically.
**Attack outcome:** distinctness is **plausibly established** but not complete — the Statistician should confirm the **single highest-overlap** type is still below a redundancy threshold. **Survives; minor check W-ovl.**

### Target 4 — Lookahead: **PASS. No lookahead in the mechanism, verified against the actual primitives.**
Each field checked against `code/institutional_levels.py` @ `discovery-mk-matrix-v1` (the only place it exists) and `resample_ny.py`:
- **`available_idx` = first bar of the current day (Q4)** — confirmed: the primitive sets `available_idx = cur_first` and documents *"bara de la care nivelul e cunoscut fără lookahead = prima bară a perioadei curente."* The level (prior-day max-high / min-low) is fully knowable at the current day's first bar. ✓
- **17:00-NY DST-aware anchor** — `day_index` derives from the 17:00-NY anchor (`resample_ny.py`), applied **caller-side**; the module is agnostic to bars-per-day and groups by `day_index`. Bars-per-day **counted** (`sub`), never assumed 92/96. ✓
- **D3_bis reset at block boundary** — the primitive iterates days *within each block* and marks the first day of each block UNCLASSIFIED (no level, no cross-block borrow). ✓
- **D7 consumption at first touch** — `detect_level_touches` breaks at the first touch, "consumat la prima atingere (D7), fără re-armare." ✓
- **`entry@next-open`** — entry at the open of the bar *after* the trigger bar; no sub-bar path assumption, strictly forward of the touch. ✓
**Attack outcome:** I actively looked for a lookahead and found none. The level is backward-looking (prior day), availability is the current day's first bar, the trigger uses bars up to the touch, and entry is strictly the next bar's open. **PASS.**

### Target 5 — Circularity (the "E010" overlap risk): **no realised circularity inside Part A; one unstated interface constraint.**
Trigger window = `[available_idx, current day's last bar]`; the touch is detected at bar *j*; entry is at *j+1* open; the measurement window is the **Statistician's** and is not defined here (correctly).
- **Within Part A there is no self-overlap:** detection ends at *j*, entry/measurement begin at *j+1* — the measurement cannot reuse the touch bar.
- **The residual risk is at the interface, not realised in Part A:** because Part A's trigger window *extends to the current day's last bar* and an intraday policy's natural measurement horizon is *also* day-bounded, a naïve Statistician window that **starts before entry** (anywhere in `[available_idx, j]`) would overlap the trigger-detection region.
**Attack outcome:** Part A does **not** contain the circularity, but it also does **not hand over the guard against it.** The interface needs an explicit constraint — *measurement begins at entry (j+1) and includes no bar in `[available_idx, j]`* — so the Statistician cannot construct the overlap. Stating that this constraint is *needed* is a finding, not a remedy (I do not design the measurement window). **Survives; interface-hardening item W-e010.**

### Target 6 — Falsifiability: **PASS, and a genuine strength.**
Part A is a **precise, mechanical rule**: fade the first touch of the prior-day extreme (PDH→short, PDL→long), enter at next-open, one shot per level per day, no trade on block-first days. Every term is observable and pre-stated.
- **Disconfirming result is well-defined:** on out-of-sample, selection-corrected data with a fixed entry+horizon measurement, if the fade-the-touch signal's forward-return distribution is **indistinguishable from (or worse than) a session-and-level-matched null**, the policy does not work. That is a clean pass/fail.
- This is the **opposite** of the unfalsifiable Alpha candidates Red Team recommended for elimination (DC-0015/0022/0024 "largest so far"). PDH/PDL Part A **can be wrong**, and the experiment that would show it is nameable today.
- **Caveat (not a defect):** *entry-mechanism* falsifiability ≠ *full-strategy* falsifiability; a complete P&L test needs Part B (risk/exit), which is unspecified by decision. As an **entry signal**, it is falsifiable on a fixed measurement horizon. **PASS.**

---

## 2. VERDICT

**PART A — ENTRY MECHANISM: SURVIVES as a specification** (defined, lookahead-safe, falsifiable) — **but the handoff is BLOCKED by F-A1** until the grounding defect is resolved.

| Item | Result |
|---|---|
| Lookahead (T4) | **PASS** — verified field-by-field against the actual primitives |
| Falsifiability (T6) | **PASS** — precise, mechanical, disconfirmable; a strength |
| Circularity within Part A (T5) | **PASS** — entry is strictly post-trigger; no self-overlap |
| Post-hoc selection (T1) | **Survives as spec** — but 6/7 is not evidence; test selection-corrected (W-sel) |
| Level-vs-session confound (T2) | **Survives** — unbroken; needs session-**and**-level-matched null (W-conf) |
| Distinctness (T3) | **Survives** — plausible; check the single highest-overlap type (W-ovl) |
| E010 interface guard (T5) | **Survives** — needs an explicit "measurement starts at entry" constraint (W-e010) |
| **Grounding present on its own branch (F-A1)** | **FAIL — fatal for the handoff** — primitives live on `discovery-mk-matrix-v1`, absent on `alpha-automation-v1` and in `78634d5` (W10) |

**Direct statement, as requested:** there **is** a fatal defect — **not in the market mechanism** (that passed the lookahead attack cleanly) but **in the submission's grounding**: the ratified primitives it stands on are not on the branch it was submitted from. The mechanism is sound *where the code exists*; the policy, on its own branch, points at a file that isn't there — the very failure it correctly diagnosed for Part B. Until F-A1 is resolved (an architecture/merge matter, not Red Team's to design), Part A cannot be executed by the Statistician on `alpha-automation-v1`.

## 3. HANDOFF

**Conditional PASS to the Statistician.** The entry mechanism is worth statistical evaluation and is falsifiable — but the hand-off carries **one blocker (F-A1/W10)** that must be closed first, plus four controls the Statistician must apply, none of which Red Team designs:
- **W10 (blocker):** the grounding primitives are not co-located with the policy (branch split). Must be resolved before evaluation on `alpha-automation-v1`.
- **W-sel:** evaluate PDH/PDL selection-corrected (1 of 9); the in-sample 6/7 is not evidence.
- **W-conf:** test against a **session-matched and level-matched (placebo-level) null**; "positive 4/4 sessions" does not isolate a level effect.
- **W-ovl:** confirm the single highest-overlap mechanism is below redundancy.
- **W-e010:** fix the measurement window to begin at entry (j+1), reusing no bar in `[available_idx, j]`.

Part B remains unspecified by decision — not evaluated here.

---

**Attack ends. Nothing modified, nothing run on data, no remedy designed. Red Team awaits CEO/Statistician routing.**
