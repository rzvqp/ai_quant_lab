# ATTRIBUTION V2 — FINAL HANDOFF INTEGRITY FIX

**Request:** `V2 FINAL HANDOFF INTEGRITY FIX` — one handoff correction. No research, no scoring, no redesign.
**Division:** Statistician. **Date:** 2026-09-02.

```
V2_FINAL_HANDOFF_INTEGRITY = PASS
PROTOCOL_CHANGE_REQUIRED   = NO
READY_FOR_ALPHA_V2_RESUME  = YES
```

---

## 1 — THE HASH: MY BOOKKEEPING ERROR, NOT A PROTOCOL CHANGE

**Cause, exactly.** `PROTOCOL_PACKAGE_HASH` is computed over every file in `statistician/attribution_v2/`.
I wrote the three handoff artifacts **into that directory**, so the directory hash moved from `4488f0e8…`
to `36e07fb7…` — while the protocol's scientific contents never changed. Reporting a new package hash
beside `PROTOCOL_CHANGE_REQUIRED = NO` was contradictory on its face, and you were right to stop on it.

**Fix.** The handoff artifacts are moved out of the identity-bearing directory:

```
statistician/attribution_v2/           12 files -- the frozen protocol CORE, identity-bearing
statistician/attribution_v2_handoff/    4 files -- values parquet, metadata, trade-level spec, manifest
```

```
PROTOCOL_CORE_HASH = 4488f0e89ae8bb079bf51eb74e4a2767f072d4e368ee383bae1d875ac4359b8f
                     -> RESTORED, identical to the frozen identity
```

The hash `36e07fb7…` is **withdrawn**. It was never a protocol identity; it was a directory checksum that
happened to include delivery files. The frozen identity stands and was not replaced.

---

## 2 — BYTE-IDENTITY VERIFIED (§2)

```
ORIGINAL_PROTOCOL_FILES_BYTE_IDENTICAL = YES   (12 / 12)
```

`git diff 6a9e0b5 → working tree` over `attribution_v2/` is **empty**, and each of the 12 files hashes
identically to its state in the commit that produced `4488f0e8…`.

**A false alarm I hit and had to correct.** My first per-file check compared `git show <blob>` (stored LF)
against the on-disk file (CRLF, from `core.autocrlf`) and reported all 12 as DIFFERING — while the directory
hash simultaneously matched. Two contradictory results mean one method is wrong; the line-ending-normalised
comparison is the correct one. Recording it because a CRLF artefact that looks like corruption is worth
knowing about the next time a hash is audited on this machine.

---

## 3 — TRADE-LEVEL BLIND FEATURE SPEC (§3)

```
attribution_v2_handoff/ATTRIBUTION_V2_TRADE_LEVEL_BLIND_FEATURE_SPEC.csv
TRADE_LEVEL_BLIND_FEATURE_SPEC_HASH = 03e636639012cd3e4edc6925c2b0f6c568941c7cb8060cf23ed896c7c711b4e2
```

Three rows — `f025`, `f029`, `f045` — each with `F_ID`, `KIND`, `N_BINS`, `SOURCE_FIELD`, `COMPUTATION`,
`DECISION_TIME_AVAILABILITY`, `BINNING_RULE`, `MISSINGNESS_RULE`. Nothing has to be inferred or
reverse-engineered.

> **CORRECTED 2026-09-02:** this table originally transposed `f025` and `f045`. The shipped
> `ATTRIBUTION_V2_TRADE_LEVEL_BLIND_FEATURE_SPEC.csv` was always correct, so no execution was affected.

| f-ID | what Alpha does | availability |
|---|---|---|
| `f025` | constant per object: the `DIRECTION` column of the execution universe; NULL for the 89 `BOTH` objects | **AT_DECISION** |
| `f029` | `abs(fill − stop) / ATR[decision_bar]`; 5 causal quintiles on a trailing-2000-**trade** rank within the object, shifted by one trade | **AT_FILL** |
| `f045` | read the trade's committed direction from its own ledger; bin 1 = LONG, 0 = SHORT | **AT_DECISION** |

**Semantic disclosure, stated as required.** Specifying these three necessarily reveals what they are. That
is unavoidable — Alpha cannot construct a value it cannot name — and it is added to the **already-declared
partial blinding**. It does not touch the other 43.

**A gap the dry run exposed and the spec now closes.** For the 14 objects supplied as pre-existing trade
logs, `STRATEGY_ATTRIBUTION_MASTER_TABLE.csv` carries **neither a stop nor a fill price**, so `f029` is not
derivable from it. The missingness rule now states the two permitted actions explicitly: **regenerate** the
object from its own generator (which yields both), or record `NOT_AVAILABLE_FOR_FAMILY`. **Do not impute and
do not substitute a proxy.** Without this the run would have stalled again, on the same class of gap.

---

## 4 — TRADE-LEVEL CAUSALITY (§4)

```
TRADE_LEVEL_FEATURE_CAUSALITY = PASS
```

Each of the seven forbidden dependencies checked per feature: future fill information, future stop/target
outcome, MFE, MAE, eventual exit, future costs → **NO** for all three. `f025` and `f045` are fixed at the
decision bar and depend on nothing after it.

**The one thing I will not smooth over.** `f029` needs the **fill price**, which is the next bar's open —
so it exists at *trade inception*, not at the *signal*. It is outcome-free: the fill is fixed before any bar
of the trade's life elapses and cannot be touched by MFE, MAE, exit or cost. It is also the quantity that
*defines* R, so a trade without it is not a trade.

**My frozen §9 wording — "available at entry … no future bars" — is ambiguous exactly here**, and that
ambiguity is mine. I am applying the **at-fill** reading for trade-level features and **not redefining the
feature**, because redefinition would be a protocol change and §13 says to stop rather than silently repair.
Under a strict at-*decision*-only reading, `f029` would be ineligible and would drop to 45 features. **That
is your call, and I am flagging it rather than deciding it quietly.** Nothing else in the handoff depends on
which way it goes.

---

## 5 — ALPHA JOIN CONTRACT (§5)

```
ALPHA_FEATURE_INPUT_COMPLETE = YES
```

> **Bar features (43).** Join on the **decision bar**: the signal bar index `si` for M15-native objects, or a
> **backward as-of join on `BAR_CLOSE_TIME ≤ decision_time`** otherwise. **Never the entry bar.** Values
> arrive as frozen bin indices; do not re-bin.
>
> **Trade-level features (3).** Populate from
> `ATTRIBUTION_V2_TRADE_LEVEL_BLIND_FEATURE_SPEC.csv`, using the frozen binning in that file.
>
> **Result.** Exactly one deterministic value — or an explicitly permitted NULL — for every
> `(ANALYSIS_OBJECT, TRADE, F_ID)` triple. A NULL is a **recorded absence** (`NOT_AVAILABLE_FOR_FAMILY`) and
> stays in the denominator; it is never imputed and never dropped.

---

## 6 — END-TO-END DRY RUN (§6)

```
END_TO_END_HANDOFF_DRY_RUN = PASS
```

Six objects across two tiers, **74,956 trades**, identities only — `sid`, `ent`, `side`, `si`, `ei`, `dir`,
`stop`. **No PnL, R, win/loss, MFE, MAE or exit column was loaded.**

| object | tier | trades | joined | bar-feature availability | `f025` | `f029` | `f045` |
|---|---|---|---|---|---|---|---|
| `S1::4b7c6d5c6035` | regenerate | 11,881 | 11,881 | 0.883 | 1.00 | 1.00 | SET |
| `S5::15be26301532` | regenerate | 22,089 | 22,089 | 0.885 | 1.00 | 1.00 | SET |
| `S21::6ddb75c3f9b1` | regenerate | 15,504 | 15,504 | 0.885 | 1.00 | 1.00 | SET |
| `S48::6d74b2000433` | regenerate | 15,355 | 15,355 | 0.881 | 1.00 | 1.00 | NULL (BOTH) |
| `HTF_RECLAIM` | log exists | 6,834 | 6,834 | 0.885 | 1.00 | — see §3 | NULL (BOTH) |
| `SESS_A` | log exists | 3,293 | 3,293 | 0.881 | 1.00 | — see §3 | NULL (BOTH) |

Every check passes: trade identity exists · decision index exists for every trade · bar-feature rows join
1:1 with `many_to_one` validated · trade-level values populate · all 46 f-IDs available or explicitly NULL ·
**no feature semantics need to be reconstructed by Alpha**.

The ~88% bar-feature availability is the block-limited HTF/level context already declared in the handoff —
a recorded absence, never imputed.

---

## 7 — FINAL

```
V2_FINAL_HANDOFF_INTEGRITY = PASS
PROTOCOL_CHANGE_REQUIRED   = NO

PROTOCOL_CORE_HASH                     = 4488f0e89ae8bb079bf51eb74e4a2767f072d4e368ee383bae1d875ac4359b8f
ORIGINAL_PROTOCOL_FILES_BYTE_IDENTICAL = YES (12/12)
  (36e07fb7... WITHDRAWN -- it was a directory checksum that included delivery files, never an identity)

BLINDED_FEATURE_VALUES_HASH           = 2ea066c6a6a75705d7429ed9ad982430f1bfd02c5242760d43cf8f363cc7e871
BLINDED_FEATURE_HANDOFF_MANIFEST_HASH = edf196e56df1d51b9f6a638b79691dd3866604dc1f95b8a86d979361bf3dd3b2
TRADE_LEVEL_BLIND_FEATURE_SPEC_HASH   = 03e636639012cd3e4edc6925c2b0f6c568941c7cb8060cf23ed896c7c711b4e2

TRADE_LEVEL_FEATURE_CAUSALITY = PASS   (at-entry standard; SUPERSEDED -- CEO ruled f029 INELIGIBLE
                                        under the strict decision-time standard. See
                                        ATTRIBUTION_V2_STRICT_CAUSALITY_CORRECTION.md: 45 features, 5,240 tests.)
ALPHA_FEATURE_INPUT_COMPLETE  = YES
END_TO_END_HANDOFF_DRY_RUN    = PASS

READY_FOR_ALPHA_V2_RESUME = YES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

No research, no scoring, no outcome inspected, no protocol content altered. The blind key, the name→id map
and the semantic builders remain outside every repository. Not touched: **S5, Q4, AI Trader, P007,
MGMT-004, MT5, StrategyCatalog.**
