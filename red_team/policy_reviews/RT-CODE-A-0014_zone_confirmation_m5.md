# RED TEAM — CODE ATTACK · Level-4 M5 zone confirmation
### RT-CODE-A-0014 · Target: `code/zone_confirmation.py` @ `ca683ff`
**Date:** 2026-08-07 · **Auditor:** Red Team · **Spec:** STAT-LEVEL4-M5-CONFIRMATION-SPEC-v1.0 (`d977446`, manifest v2.7.54). Level 4, step 3. Common validation with Level 3 **deferred by CEO** (M5/M15_v2 discovery windows overlap ~40 days, one regime — seal not broken). Checklist only. **No real-data run** — algorithm verified on synthetic M5 (module + `market_state` read-only from branch); nothing modified; no remedy.

## VERDICT — **PASS_WITH_LIMITATIONS.**
Lookahead-free (proven), leakage/circularity/overfitting/hidden-params/reproducibility clean; W=60 derivation correct; persistence/return is an exact identity; effort-saturation is a rate property; the contradiction (absorption∧acceptance) is genuinely **inexpressible by type**. Two real limitations, both at the **integration boundary**: (a) the fail-closed **UNDETERMINED sentinel is encoded as the ordinal value 0 at the arithmetic midpoint** — a value-consuming downstream reads it as *neutral/proceed*, not block; (b) the time boundary **forces the confirmation to REPLACE the Level-3 trade, changing the tested hypothesis.**

---

## CHECKLIST
- **Lookahead — PASS, PROVEN.** The descriptor reads bars only in `[hit+1, hit+W]` (`win_end = hit+W`); entry is permitted at `hit+W+1`. ATR is taken at `hit` (`atr14[hit]`, causal). **Numeric proof:** scrambling every bar `> win_end` to a sentinel leaves `confirmation/persistence/progress/encounters` **identical** → the descriptor is a function of bars `≤ hit+W` alone. ✅
- **Leakage — PASS.** Pure per-interaction function; no cross-state.
- **Circularity — PASS/N-A.** Pure classifier; no probability, no feedback (Level 4 emits the ordinal; Level 6 does probability).
- **Ambiguity — see Z4-L1 (the ordinal-0 sentinel) and Z4-U1 (identity framing).**
- **Overfitting — PASS.** Tertiles are declared equal-occupancy **choices**; the binomial derivation was honestly **discarded** (it would pass 5% under independence but 44.7% actually — bars not independent), not kept as a false anchor.
- **Hidden params — PASS.** `W=60` derived + declared; tertiles declared; `tick_volume` excluded (unconfirmed provenance, never in primary classification — the function takes only OHLC); a `schema_hash` pre-registers the ordered descriptors + W + tertiles + exclusions.
- **Reproducible — PASS.** Deterministic; schema-hashed.

## SPEC TARGET 1 — tertiles: **legitimate equal-occupancy convenience (consistent with Level 1).**
The binomial derivation failed (no natural threshold under a false independence assumption), so the tertiles are declared **ALEGERI** anchored on equal occupancy. As at Level 1 (RT-CODE-A-0009): when no mechanistic threshold exists, equal-occupancy is a sound **declared default** (balanced cells), **not** a discovered boundary — correctly labelled, must not be read as market-meaningful. The classification requires **both** axes in the same tertile (acceptance = both ≥P67; absorption = both ≤P33), so UNDETERMINED is the majority — a conservative design. PASS.

## SPEC TARGET 2 — the time boundary: **eliminates outcome-conditioning, but it does NOT "just move" it — it REPLACES the trade (hypothesis changes).**
Closing the window at `hit+W` and entering at `hit+W+1` correctly removes lookahead (verified). **But the declared consequence is real and load-bearing:** the Level-4 entry is **W=60 M5 bars (5 hours) after the penetration**, at a **different price and risk** — so the confirmation **does not filter** the Level-3 zone trade, it **replaces** it with a **post-resolution momentum entry.** The economic hypothesis therefore **changes**: from *"does the zone hold, so take the zone trade?"* (a filter) to *"after 5h of zone resolution, does entering in the resolved direction pay?"* (a new trade). This is an **honest, acceptable design forced by the no-lookahead constraint** — but the Statistician/CEO must **not** interpret a Level-4 result as validating a *zone filter on the Level-3 entry*; it validates a distinct, later trade. **FLAG (Z4-L2).**

## SPEC TARGET 3 — "saturated effort" an artifact of W=60? **NO — it is a RATE property, ~W-invariant.**
`encounters` (bars penetrating) is a **rate**: measured across W=20/40/60/80 it stays roughly constant (~0.6–0.87 in my synthetic; the real median is 38/60 ≈ 0.63). Price hovers near a just-penetrated level, so a high **fraction** of window bars penetrate at **any** W — the count scales with W but the rate does not. So the saturation is a property of the phenomenon, **not** of W=60, and **excluding `encounters` as a threshold is correct at any W.** PASS.

## OWN TARGET — W=60 derivation: **correct, same discipline as L=28 / 460.**
5 hours = 5×60 min / 5 min = **60 M5 bars.** The 5h dependence horizon (which justified H=20 on M15: 20×15 min = 5h) is a **calendar-time** horizon, which transfers across timeframes; a *bar* count does not. So `W=60` is **derived** (5h in M5 units), not transplanted — the exact reasoning that corrected the L=28 (bars→trades) and 460 (week→quarter) unit-transplants. ✅

## OWN TARGET — persistence vs return: **sum = 1 BY CONSTRUCTION, not empirical.**
`persistence = beyond/wlen`; `return` would be `(wlen−beyond)/wlen = 1 − persistence` — an **identity** (closes partition into beyond/not-beyond). And `median(1−X) = 1 − median(X)` for any X, so **`0.517 + 0.483 = 1.000` is guaranteed, not measured.** Therefore using persistence alone is **correct** and return carries **zero** independent information — it **cannot diverge** in other conditions (it is an identity, not an empirical near-equality). The code computes only `persistence` (never `return`), consistent. **Minor (Z4-U1):** the spec presents this identity as if it were an empirical finding ("median 0.517 vs 0.483"); cosmetic — the conclusion is right.

## OWN TARGET — the UNDETERMINED → NO-TRADE chain: **NOT verifiable here, and the ordinal-0 encoding invites silent consumption. (Z4-L1, sharpest.)**
All fail-closed paths → `UNDETERMINED` with `status=UNAVAILABLE` (verified: zone_unavailable / invalid_side / incomplete_window / atr_unavailable / no_penetration). **But two problems:**
1. **The chain "UNDETERMINED ⇒ sentinel at Level 6 ⇒ NO-TRADE by type" is not in this file** — the Level-4→Level-6 wiring is absent (the decision engine, RT-CODE-A-0008, consumes OutcomeCell *counts*, not a `ZoneConfirmation`). Same unbuilt-wiring gap as Level 1 (RT-CODE-A-0009 L-U2).
2. **UNDETERMINED is encoded as ordinal value `0`, at the arithmetic MIDPOINT of −2..+2.** A downstream that consumes the **value** (as a weight/factor/score) reads `0` as **neutral → proceed**, exactly *not* block. "Sentinel by type" holds **only if Level 6 checks the enum member (`is UNDETERMINED`) or `status`, never the numeric value.** **Most fragile for the MAJORITY case:** a *classified*-UNDETERMINED (mixed persistence/progress — the spec's majority) has `status=AVAILABLE` and its **only** signal is the ordinal `0` — no `status` sentinel to fall back on. So for the majority of interactions, a value-consuming Level 6 would **silently proceed unconfirmed.** **This must be verified at the Level-4→6 integration; as encoded, silent consumption is the default behavior of a value-consuming downstream.**

## SEVERITY
- 🟠 **Z4-L1 · UNDETERMINED silent-consumption risk** — the fail-closed/classified sentinel is ordinal `0` at the neutral midpoint; "block by type" requires Level 6 to check the enum member/`status`, unverified (wiring absent), and the majority classified-UNDETERMINED case has only the ordinal signal. Analog of RT-CODE-A-0009 L-U2.
- 🟠 **Z4-L2 · Replace-not-filter changes the hypothesis** — the time boundary forces a 5h-later momentum entry, not a zone filter; a Level-4 result must not be read as validating a Level-3 zone filter.
- 🟡 **Z4-U1 · Identity framed as empirical** — persistence+return=1 is a construction identity, presented as "0.517 vs 0.483"; cosmetic.

## WHAT SURVIVES (verified)
Lookahead-free by construction (proven); leakage/circularity/overfitting/hidden-params/reproducibility clean; W=60 correctly derived (5h in M5); persistence/return an exact identity (one suffices); effort-saturation a rate (excluding it is W-robust); tertiles a legitimate declared convenience; the absorption∧acceptance contradiction genuinely **inexpressible by type** (the ordinal is the right structural choice for *that*); all fail-closed paths reach UNDETERMINED+UNAVAILABLE.

## VERDICT — **PASS_WITH_LIMITATIONS.** The classifier is causally and structurally sound; the two limitations live at the **integration boundary**, not in the classification: (Z4-L1) the UNDETERMINED sentinel's ordinal-0 encoding must be enforced by a **type/status check at Level 6**, or the majority-undetermined interactions are silently traded; (Z4-L2) the confirmation **replaces** the Level-3 trade and thus tests a different hypothesis. Neither is a defect in this file; both must be honored downstream.

## HANDOFF → CEO / Statistician
1. **Z4-L1 (before wiring):** Level 6 must treat UNDETERMINED via the enum member / `status=UNAVAILABLE`, **never** the ordinal value 0 (which reads as neutral); verify the classified-UNDETERMINED (status=AVAILABLE, value 0) also blocks.
2. **Z4-L2:** record that Level 4 validates a **post-window momentum entry**, not a Level-3 zone filter — the deferred common validation must test that object, not "zone-hold improves the Level-3 trade."
3. The classification itself (lookahead, W derivation, tertiles, persistence identity, effort exclusion, type-safe contradiction) is **verified clean.**

Red Team designed no remedy, ran no data on the market, modified nothing outside `red_team/`.
