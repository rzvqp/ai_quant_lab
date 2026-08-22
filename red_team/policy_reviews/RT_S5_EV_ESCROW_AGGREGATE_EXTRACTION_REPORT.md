# RED TEAM — S5 EV ESCROW AGGREGATE EXTRACTION
### RT-S5-EV-ESCROW-AGGREGATE-EXTRACTION-001 · Auditor: Red Team · 2026-08-22

Privacy-preserving aggregate extraction of the REAL EV empirical-Bayes contract inputs from the exact frozen
S5 validation ledger `cd4e8d4a…`. No new validation, no strategy change, no individual trade exposed.

---

## 0 — VERDICT

```
S5_ESCROW_EV_AGGREGATES_EXTRACTED          (mechanically exact, internally consistent)
S5_ESCROW_AGGREGATE_BRACKET_FAIL           (n_stop = 84 falls below the Statistician bracket floor of 99)
```

The extraction itself is **exact and internally proven** (reconstruction closes to 9×10⁻¹⁴; exit semantics
cross-check exactly). But the exact `n_stop = 84` falls **outside** the Statistician's independent integrity
bracket `n_stop ∈ [99,147]` (§7). Per the fail-closed rule I **do not alter the value** and I **do not** issue
`S5_VALIDATED_EV_AGGREGATES_READY_FOR_STATISTICAL_VERIFICATION`. Root cause is a mis-derivation in the bracket,
not the ledger (§ below) — surfaced for Statistician reconciliation, not resolved unilaterally.

No runtime wiring changed. Escrow boundary intact.

---

## 1 — LEDGER IDENTITY (§2)

| identity | value | check |
|---|---|---|
| ledger fingerprint | `cd4e8d4aae0104cd…7831e1d7` | **MATCH** (sha256 of the frozen S5 ledger) |
| strategy | `C_2d587447` / family S5 / rep `7472f3d412f2` / LONG | ✓ |
| spec (frozen) | `S5{session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3}` | ✓ exact |
| config fingerprint | `S5-frozen-spec:…;tick=0.01;or_bars=4;entry_window_bis=4-20;hold_bars=48;rr=3.0` | ✓ |
| validation lineage | RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001 `633bd5da` (PASS) | ✓ |
| population | 52,572 bars, `pop_ohlc bac65b1a`, `timeline 4c9ce7b7` | ✓ |
| cost model | TICK 0.01, BASE RT 0.05, STRESS RT 0.24 | ✓ |

No identity mismatch → not `S5_ESCROW_LEDGER_IDENTITY_FAIL`.

## 2 — EXIT SEMANTICS (§3/§4) — recovered from `ve_brain` code, not natural language

The REAL EV contract (`RealEVDecisionEngine.decide → ve_brain.run_ev → _ev_core.decide`, audited at `e54a2a5`)
consumes four outcome counters from one empirical-Bayes cell:
```
edge_schema = "real-ev-expected-edge-v1"
n           = total trades in cell
n_target    = TARGET exits (hit the rr3 target)
n_horizon   = HORIZON exits (48-bar time-stop; holding = 49)
sum_horizon_r = signed sum of R over horizon exits;  E[X|h] = sum / n_horizon
n_stop      = n - n_target - n_horizon   (IMPLICIT, not transmitted)
credibility = 0.80 (ratified policy default; NOT evidence)
```

**★ Critical R-semantics finding (§4).** The sealed core formula is
`ev = p_t·rr − p_s·1.0 + p_h·e_x_h − cost_over_r`: the target term uses `rr = 3.0` (gross +3R), the stop term
is exactly `−1.0` (gross), and the round-trip cost is subtracted **once, separately** as `cost_over_r`.
Therefore `sum_horizon_r` (→ `e_x_h`) must be the **GROSS (pre-cost)** signed R sum. Supplying BASE- or
STRESS-net R would double-count cost. This is the exact semantic the mandate's §4 required me to pin down; I
extract **gross** R. **No mismatch** between the validation exit classification and the EV classification →
not `S5_EV_EXIT_SEMANTICS_MISMATCH`. The exit-type classification is drawn directly from the ledger's exit
prices (exit == target ⇒ TARGET; exit == stop ⇒ STOP; else ⇒ HORIZON), cross-checked against holding.

## 3 — AGGREGATE EXTRACTION (§3)

```
n              = 295
n_target       = 15
n_horizon      = 196
n_stop         = 84        (implicit: 295 − 15 − 196)
sum_horizon_r  = +102.2125344478   (GROSS)      E[X|h] = +0.521493
```
(BASE-net horizon sum would be +101.4089 — recorded only to show the ~0.8R cost gap; the contract uses gross.)

## 4 — COUNT INTEGRITY (§6)

| check | result |
|---|---|
| n_target ≥ 0, n_horizon ≥ 0, n_stop ≥ 0 | ✓ (15, 196, 84) |
| n_target + n_horizon + n_stop = n | ✓ 15+196+84 = 295 |
| direct stop-class count = implicit n_stop | ✓ (84 = 84) |
| sum_horizon_r finite, no NaN/inf | ✓ |
| all counts integer | ✓ |
| population N = validated S5 population | ✓ (295) |

## 5 — EXIT-SEMANTICS CROSS-CHECK (§4)

HORIZON classified by exit price (neither stop nor target) = **196**; HORIZON classified by holding = 49
(the 48-bar time-stop) = **196**. **Exact agreement** — the two independent definitions coincide, confirming
the classification is faithful. Targets fill at exactly +3.0 gross R (all 15); stops at exactly −1.0 gross R
(all 84).

## 6 — R RECONSTRUCTION (§9) — contract-exact

Gross target = +3.0, gross stop = −1.0 (verified exact from geometry):
```
3.0 · n_target  −  1.0 · n_stop  +  sum_horizon_r
= 3.0·15 − 84 + 102.2125344478
= 63.2125344478
sum(R_gross over all 295 trades) = 63.2125344478
residual = 9.2 × 10⁻¹⁴   (float noise)
```
The aggregate partition **reproduces the total validated gross R exactly**. Published-metric cross-check
(§8): BASE avg = 0.2098 (matches the published +0.210, rounding only); WR = 162/295 = 0.549. Winners = 15
targets + 147 positive-horizon; losers = 84 stops + 49 negative-horizon = 133. All consistent.

## 7 — BRACKET VERIFICATION (§7) — the one failure, root-caused

| counter | exact | Statistician bracket | result |
|---|---:|---|---|
| n_target | 15 | [0, 54] | **PASS** |
| n_horizon | 196 | [148, 196] | **PASS** (at ceiling) |
| **n_stop** | **84** | **[99, 147]** | **FAIL** (84 < 99) |

**Root cause — the bracket is mis-derived, the ledger is right.** The Statistician's `n_stop ≥ 99` floor
was obtained from `avg_loser = −0.763` over 133 losers (total loser R ≈ −101.5) divided by the per-stop loss
(≈ −1.03R). That quotient bounds the number of **losing trades** (≥ 99), **not** the number of **stops**. The
true data has **133 losers = 84 stops + 49 negative-horizon exits**; the 49 negative horizons carry loss the
bound implicitly attributed to stops, so `n_stop = 84 < 99`. Equivalently: at `n_horizon = 196` (the
Statistician's own ceiling, which the exact data hits), `n_stop ≥ 99` would force `n_target ≤ 0`, contradicting
`n_target = 15`. The `n_stop` floor and `n_horizon` ceiling are jointly infeasible for any `n_target > 0`.

Per §7 I **did not alter any value** and I halt on `S5_ESCROW_AGGREGATE_BRACKET_FAIL`. The extraction is
nonetheless proven correct (exact reconstruction, exact semantics cross-check), so the reconciliation action
lies with the Statistician's bracket, not with re-extraction.

## 8 — COST IDENTITY (§10)

```
validation economics : TICK=0.01 (RT-CODE-A-0007 defect 0.1 NOT used) · next-bar open entry
                       stop floor max(2·spread, 0.05, 0.10·ATR) → max(0.05, 0.10·ATR), bound in 0% of trades
                       spread folded into slippage (spread_ticks=0, slip_ticks=RT/(2·TICK))
                       R = (dir·(exit − entry) − round_trip) / risk,  risk in price units
BASE round-trip  = $0.05     STRESS round-trip = $0.24   (AI_TRADER_SHADOW_COST_MODEL_v1.json)
runtime (ve_brain._rr_r_cost): r=|entry−stop|; cost = full_spread + entry_slip + exit_slip  (== 0.05 / 0.24)
```
The internal decomposition of the round-trip (spread vs slippage split) is **not uniquely identified** by the
frozen validation artifacts (spread was folded into slippage); only the totals (0.05 / 0.24) are authoritative.
Not invented.

## 9 — PRIVACY CONFIRMATION (§5/§12)

The deliverable and this report contain **aggregate evidence only** — counts and one signed R-sum. **No**
individual trades, timestamps, entries, exits, individual R/PnL, trade ordering, or raw rows are exposed. The
escrow boundary remains intact; the raw ledger stays sealed in `escrow_red_team/`.

## 10 — AGGREGATE ARTIFACT IDENTITY (§11/§12)

`S5_VALIDATED_EV_AGGREGATES_V1` (aggregates only), with `status = BRACKET_FAIL_PENDING_STATISTICIAN_RECONCILIATION`
(NOT "ready"). Deterministic fingerprint over strategy/validation/ledger/population/cost identity + the counts +
`sum_horizon_r`:
```
artifact_fingerprint = fe6eaf9fedbbe0be0a64ef0890d1a10388f80bee6e5b2e25c2770dbeb847e866
```
Any change to identity, counts, or `sum_horizon_r` changes the fingerprint (§12).

## 11 — WHAT DID NOT HAPPEN (§13/§14/§15)

No modification to AI Trader / `RealEVDecisionEngine` / StrategyCatalog / S5 plugin / risk / execution / broker.
No retuning, no RR/OR/session/SL/TP change, no filters, no re-running Alpha discovery. No CALIB, no 2025+
supplementation, no new holdout/validation population, no future trades — only the frozen `cd4e8d4a` ledger.

---

## 12 — FINAL VERDICT & RECOMMENDATION

```
S5_ESCROW_EV_AGGREGATES_EXTRACTED           (exact; reconstruction + semantics proven)
S5_ESCROW_AGGREGATE_BRACKET_FAIL            (n_stop=84 outside [99,147])
```
The exact EV aggregates are `n=295, n_target=15, n_horizon=196, n_stop=84, sum_horizon_r=+102.2125` (gross).
They are correct and privacy-preserving, but I withhold the READY-for-verification status because they fail an
independent pre-registered bracket. **Recommendation to CEO/Statistician:** reconcile the `n_stop` bracket — its
floor conflated total-losers (≥99, satisfied at 133) with stops; the corrected `n_stop` bracket that admits
negative-horizon losers contains 84. Once the Statistician re-derives the bracket (or confirms the correction),
the identical aggregate artifact can be promoted to `S5_VALIDATED_EV_AGGREGATES_READY_FOR_STATISTICAL_VERIFICATION`
without any change to the extracted values. No AI Trader wiring is authorized here regardless.

---

*Red Team · aggregates-only · escrow boundary intact · no runtime/strategy change · frozen ledger cd4e8d4a ·
LEDGER E98 (prev E97).*
