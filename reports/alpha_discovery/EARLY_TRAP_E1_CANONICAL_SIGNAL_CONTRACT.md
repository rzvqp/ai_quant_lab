# EARLY_TRAP_E1 — CANONICAL SIGNAL CONTRACT

**Signal ID:** `EARLY-TRAP-E1` · **Version:** `1.0.0` · **Status:** `EARLY_TRAP_E1_CANONICAL_SIGNAL_FROZEN`
**Artifact:** [`early_trap_e1_signal.py`](early_trap_e1_signal.py) · **Tests:** [`test_early_trap_e1.py`](test_early_trap_e1.py) (12/12 pass)
**Lineage (authoritative):** Alpha discovery `6a5d535` (rule R2) + Statistician audit `de35453` (`EARLY_TRAP_E1_SIGNAL_SUPPORTED`, 8/8 figures reproduced).
**Scope:** price-only XAUUSD, DEV-only. No CALIB / V1 / 2025+ / N4 / exogenous. **This contract is the signal only — no execution geometry.**

---

## 1. Exact formula (no reinterpretation, no additions)
```
frozen Asia-High sweep parent
  -> E1 = first completed M15 bar after the sweep bar   (e1_index = sweep_index + 1)
  -> FIRE  iff   E1.close < Asia_High   AND   E1.close < E1.open
```
- Both comparisons are **strict** (`<`).
- **Doji** (close == open) → not a bearish body → **no fire**.
- **Exact equality** (close == Asia_High) → not strictly below → **no fire**.
- **NaN / missing E1 bar** → **fail-closed** (no fire).
Pure rule function: `early_trap_e1_fires(e1_open, e1_close, asia_high) -> bool`.

## 2. Session identity (frozen, DST-correct)
`session_definition_identity = 4e62cd996ce16b9f8129a5f30a54b031a6ccf542b4918694e5a8eb8b1f434e3c`
| session | window | DST handling |
|---|---|---|
| ASIA | 00:00–07:00 **UTC** | fixed UTC (Tokyo 09:00–16:00 JST; Japan has **no DST**) |
| LONDON | 08:00–16:00 Europe/London local | DST-correct via `tz_convert` (+1:00 summer / 0:00 winter) |
| NEW YORK | 08:00–17:00 America/New_York local | DST-correct via `tz_convert` (−4:00 / −5:00) |
Asia range requires ≥12 completed M15 Asia bars.

## 3. Parent identity (frozen, unchanged)
`parent_population_identity = 583aca7bc7b62601d8bcb8d4a539a81f2e02c51888dfd8858ad08a42be20d085`
- Level = **Asia High** (max high over the 00:00–07:00 UTC Asia window; low/mid derived).
- Sweep = **first** completed M15 bar with `utc_hour ≥ 7` in **London or New York** session with `high > Asia_High`.
- **One sweep per day**; DEV only. **329 parent sweep-days.** (LONDON 232 / NY 14 / OVERLAP 83.)

## 4. Causal timing
- Asia range is **complete at 07:00 UTC**, strictly before any sweep can be detected (sweep requires `utc_hour ≥ 7`).
- Sweep bar is a **completed** bar; **E1 is exactly the first completed M15 bar after it** (`sweep_index + 1`).
- **`signal_time` = E1 `close_time`** (epoch seconds) — the signal is knowable only at E1 close.
- **`earliest_execution_time` = strictly after E1 close** (`signal_time + 1`, i.e. ≥ next M15 open). No partially-formed E1 bar is ever used.

## 5. Output schema (per fired episode)
`signal_id, signal_version, day, session, split{DISC|CONF}, sweep_index, e1_index, signal_time, earliest_execution_time, asia_high, asia_low, asia_mid, e1_open, e1_close, reach_mid_diag`
`reach_mid_diag` is the **diagnostic outcome label only** (reach Asia mid within 24 same-day M15 bars from E1+1); it is **not part of the signal** and drives no trade.

## 6. Fingerprints (deterministic)
| fingerprint | value |
|---|---|
| implementation_fingerprint | `33bec4498e72a05c486ec1763854edac17cc9da82556932d0f3257d62f6c2a16` |
| configuration_fingerprint | `a172771591289fccade25c89121fe30e46115d76cd78e0ef01ebe2eb0503ef90` |
| session_definition_identity | `4e62cd996ce16b9f8129a5f30a54b031a6ccf542b4918694e5a8eb8b1f434e3c` |
| parent_population_identity | `583aca7bc7b62601d8bcb8d4a539a81f2e02c51888dfd8858ad08a42be20d085` |
| episode_set_identity | `920dee40b64156118e50985399bb0a1e53307ffb37fb381a37ab66025c17631e` |
Recompute: `python early_trap_e1_signal.py`.

## 7. Reproduction (audit-exact)
| quantity | expected (audit) | canonical | ✓ |
|---|---|---|---|
| parent sweeps | 329 | 329 | ✓ |
| fires (episodes) | 118 | 118 | ✓ |
| unique days | 118 | 118 | ✓ |
| DISC fires | 68 | 68 | ✓ |
| DISC P(reach mid) | 0.794 | 0.794 | ✓ |
| CONF fires | 50 | 50 | ✓ |
| CONF P(reach mid) | 0.840 | 0.840 | ✓ |
→ `EARLY_TRAP_E1_CANONICAL_REPRODUCTION_PASS`.

## 8. Known limitations
- **Diagnostic endpoint only.** `reach_mid_diag` is a directional/mean-reversion diagnostic (P(reach Asia mid)), **not** a P&L edge. No entry/SL/TP/RR/break-even/partials/runner/M5 is defined here — execution is a **separate future mandate**.
- **Single-year OOS window.** CONF is essentially 2023 (chronological split cut 2023-04-27). Mitigated by positive in-sample lift in 2021/2022 (discovery lineage), but not independently multi-year-validated.
- **Path survivability risk (descriptive):** for fired episodes P(new high above sweep) ≈ 0.50 — a real execution risk for the future execution mandate, not resolved here.
- **`prior_attacks()` defect (excluded):** the Statistician found `prior_attacks()` counts Asia bars that themselves define `asia_high`, so it is ≥1 by construction. **EARLY-TRAP-E1 does not use `prior_attacks`** — the feature is explicitly excluded (mandate §8 option A); zero impact on this signal. Repaired nothing (isolation preserved).
- **No promotion / broker / live.** Research artifact; frozen for execution research, not for trading.
