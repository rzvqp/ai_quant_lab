# RED TEAM — S5 EV AGGREGATE ARTIFACT RE-STAMP
### RT-S5-EV-AGGREGATE-RESTAMP-001 · Auditor: Red Team · 2026-08-22

Status reconciliation of the existing `S5_VALIDATED_EV_AGGREGATES_V1` artifact after the Statistician's
independent reconciliation PASS. **No evidence value changed. No ledger re-extraction. No new statistics.**

---

## 0 — FINAL STATUS

```
S5_ESCROW_EV_AGGREGATES_VERIFIED
S5_VALIDATED_EV_AGGREGATES_READY_FOR_RUNTIME_PACKAGING
```

The previously-withheld READY status is now issued: the sole basis for the earlier `BRACKET_FAIL` — the
`n_stop ≥ 99` floor — has been formally **withdrawn** by the Statistician (`9cfcc5f`), who confirmed the bound
constrained *total losing trades*, not *stop exits*, exactly as Red Team diagnosed. The exact aggregate values
are unchanged.

No runtime wiring changed. Escrow boundary intact.

## 1 — ARTIFACT LINEAGE

| element | value |
|---|---|
| artifact | `S5_VALIDATED_EV_AGGREGATES_V1` |
| produced by | RT-S5-EV-ESCROW-AGGREGATE-EXTRACTION-001, commit `8228ded` (LEDGER E98) |
| source ledger | `cd4e8d4aae0104cd…7831e1d7` (frozen S5 validation ledger) |
| validation lineage | RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001 `633bd5da` (PASS) |
| strategy | `C_2d587447` / S5 / rep `7472f3d412f2` / LONG |
| population | 52,572 bars · `pop_ohlc bac65b1a` · `timeline 4c9ce7b7` |
| cost / R semantics | TICK 0.01 · BASE 0.05 / STRESS 0.24 · GROSS R (cost applied separately by REAL EV) |

## 2 — STATISTICIAN RECONCILIATION REFERENCE

`STAT-S5-EV-AGGREGATE-RECONCILIATION-001`, commit `9cfcc5fbf099dc48d7758634541ca726e6415318` (verified present,
branch statistician-foundation). Verdicts issued:
```
S5_EV_AGGREGATE_RECONCILIATION_PASS
S5_CANONICAL_EV_EVIDENCE_SUPPORTED
S5_EV_EVIDENCE_READY_FOR_RUNTIME_PACKAGING
```
The Statistician states verbatim: *"The bracket failure was mine, not Red Team's"*, and confirms Red Team's
aggregates are "arithmetically, contractually and semantically valid."

## 3 — AGGREGATE IDENTITY (unchanged — §2 of mandate)

```
n              = 295
n_target       = 15
n_horizon      = 196
n_stop         = 84        (derived: n − n_target − n_horizon)
sum_horizon_r  = +102.2125344478   (GROSS R)
```
Verified byte-for-byte against the E98 artifact: **no rounding change, no re-estimation, no reclassification,
no ledger access.**

## 4 — COUNT INTEGRITY (§4)

| check | result |
|---|---|
| 15 + 196 + 84 = 295 | ✓ |
| n_target + n_horizon ≤ n (211 ≤ 295) | ✓ |
| all counts integer, non-negative, finite | ✓ |
| sum_horizon_r finite | ✓ (+102.2125344478) |

## 5 — R SEMANTICS (§5) — unchanged, GROSS

`sum_horizon_r` remains the **GROSS** (pre-cost) signed R sum over horizon exits. Per the sealed
`ve_brain._ev_core` contract `ev = p_t·rr − p_s·1.0 + p_h·e_x_h − cost_over_r`: target term gross `+3R`, stop
term gross `−1R`, horizon term gross `E[R|h]`, and the round-trip cost deducted **once, separately** by the
REAL EV engine. **No conversion to net R.** The Statistician's reconciliation accepted exactly this semantics.

## 6 — WITHDRAWN BRACKET ACKNOWLEDGEMENT (§6)

The previous `BRACKET_FAIL` was caused **solely** by an invalid derived lower bound `n_stop ≥ 99`. That bound
was derived from the aggregate loss mass (`≈ −101.5 R`) divided by the per-losing-trade cost-inflated unit loss
(`≈ 1.03 R`), giving `count ≥ 99` — a bound on the count of **losing trades** (`n_losers`), then mislabelled as
`n_stop`. Since `n_stop ≤ n_losers`, a lower bound on `n_losers` places **no** lower bound on `n_stop`. Actual
decomposition (accepted): `TARGET 15`, `HORIZON 196` (`positive 147` / `negative 49`), `STOP 84`; `winners 162`,
`losers 133`, `WR 0.549`. `n_losers = 133 ≥ 99` is satisfied (and vacuous for `n_stop`). **The withdrawn floor
is not an active validation condition and must not be reinstated.** The failure was in the bracket, never in the
Red Team extraction.

## 7 — FINGERPRINT HANDLING (§7)

The V1 artifact design places `status` and reconciliation metadata **inside** the fingerprinted payload, so
re-stamping the status necessarily changes the canonical artifact bytes. Per §7 second branch, the new
fingerprint is produced and documented:

```
OLD artifact_fingerprint = fe6eaf9fedbbe0be0a64ef0890d1a10388f80bee6e5b2e25c2770dbeb847e866
NEW artifact_fingerprint = ff1384a2fba6d37c859613887d89837bdd11a94614ade0a1ed034176653dddd4
reason = status re-stamped BRACKET_FAIL_PENDING… → READY_FOR_RUNTIME_PACKAGING; reconciliation reference
         (9cfcc5f) and bracket-withdrawal note added. ALL economic evidence values byte-identical.
```

To make future status changes non-disruptive and to satisfy §7's intent, a **stable `evidence_fingerprint`**
is added, computed over the economic evidence **only** (edge_schema, strategy/validation/ledger/population/cost
identity, `n`, `n_target`, `n_horizon`, `n_stop`, `sum_horizon_r`, credibility default, artifact_version) —
excluding status/reconciliation metadata:
```
evidence_fingerprint = 9ca6e2bd9884389b822518bed2341f7273288018187974c468016b20070593b4
```
This value changes **iff** an economic evidence value changes (§12), and is invariant to status re-stamping. No
economic evidence was changed to preserve any fingerprint.

## 8 — PRIVACY CONFIRMATION (§8)

Aggregates only. **No** individual trades, timestamps, entries, exits, individual R, trade order, or ledger rows
are present in the artifact or this report. The raw ledger remains sealed in `escrow_red_team/`.

## 9 — RUNTIME HANDOFF (§9)

```
S5_VALIDATED_EV_AGGREGATES_READY_FOR_RUNTIME_PACKAGING
```
The verified aggregates are ready for a **separate** runtime-packaging/engineering mandate. **No** runtime
wiring is performed here: `RealEVDecisionEngine`, AI Trader, S5 plugin, StrategyCatalog, Risk, Execution, MT5,
and broker settings are untouched (§10).

## 10 — FINAL VERDICT

```
S5_ESCROW_EV_AGGREGATES_VERIFIED
S5_VALIDATED_EV_AGGREGATES_READY_FOR_RUNTIME_PACKAGING
```
Exact aggregates (`n=295, n_target=15, n_horizon=196, n_stop=84, sum_horizon_r=+102.2125` gross) verified
unchanged and now cleared of the withdrawn bracket. Evidence fingerprint `9ca6e2bd`; artifact fingerprint
re-stamped `fe6eaf9f → ff1384a2`. Next owner: a separate runtime-packaging mandate (CEO-authorized).

---

*Red Team · re-stamp only · no value change · no ledger re-extraction · aggregates-only · escrow boundary
intact · no AI Trader / runtime change · LEDGER E99 (prev E98).*
