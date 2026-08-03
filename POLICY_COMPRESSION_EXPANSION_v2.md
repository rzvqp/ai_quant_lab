> **SUPERSEDED by POLICY_COMPRESSION_EXPANSION_v3.md** — the v2 exit's third term was a discovery-only 'block boundary' that never fires on a live forward account. Kept for the record; do not use.

# POLICY — Compression-to-Expansion Breakout — canonical schema — **v2.0 (Part B completed)**

# 🟠 DEMO_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**One authorized pilot Part B — single variant, chosen with a logical reason BEFORE any result; no
multiple variants, no optimization.** Structural, composed from ratified primitives + raw OHLC, no new
calculation, no lookahead. Supersedes v1.1 (Part B UNSPECIFIED). Part A unchanged.

| Field | Value |
|---|---|
| **policy_id** | `COMPRESSION-EXPANSION-BREAKOUT` |
| **version** | `2.0` (DEMO_BASELINE — Part B completed; Part A unchanged from v1.1) |
| **family** | `volatility_state_transition` (market_state) |

## Primitive source references — W10
**No new primitive introduced by Part B** — stop and exit both use `market_state.expansion` (bar mask +
raw OHLC of the expansion bar), already cited. v1.1 W10 block stands:
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/market_state.py` | `compression`, `expansion` (+ its per-bar direction `sign(close-open)` and raw `low/high`), `atr14`; `DISP_MULT=1.5`, `BODY_FRAC=0.5`, `COMPRESSION_WINDOW=460`, `COMPRESSION_PCTL=10` — ratified (Statistician v2.6.1) | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/market_state.py | sha256sum`.

---

## PART A — ENTRY MECHANISM — **UNCHANGED from v1.1** (see `POLICY_COMPRESSION_EXPANSION_v1.md`)
Activation = a valid compressed bar (`is_valid ∧ is_compressed`, trailing-460 P10 Parkinson log-range,
strictly causal). Trigger = the first **expansion** bar `i` immediately after a compressed bar
(`expansion[i] ∧ is_compressed[i-1]`). Entry = expansion-direction breakout, `entry@next-open` (bar `i+1`).
Disclosed compression-anchoring risk carried forward. `regimes_permitted` / `min_trades` = Statistician.

---

## PART B — RISK MANAGEMENT — **COMPLETED (DEMO_BASELINE — single variant, structural)**

**Choice rationale, fixed BEFORE any result:** fixed-ATR is non-informative here (identical 0.378–0.385
winrate across six mechanisms; structure dominated). This is a **volatility-breakout** family — its
natural structural anchors are the **displacement bar** and the **displacement primitive itself**, NOT a
daily level (deliberately different from PDH/PDL). One variant only.

| Field | Method (single chosen variant) · reason |
|---|---|
| **stop_loss** | **The opposite extreme of the expansion (displacement) bar `i`**: bullish breakout (long) → stop = `low[i]`; bearish (short) → stop = `high[i]`. **Reason:** the breakout thesis is "the coil resolves and the displacement drives"; the structural falsification is price returning **through** the displacement bar (below its low for a long). Event-anchored to the bar that generated the signal — not a distance. (Raw OHLC at the ratified expansion index; no new calc.) |
| **exit** | **The first OPPOSING-direction expansion bar** after entry (`expansion[k]==True` with `sign(close[k]-open[k])` opposite to the entry direction), i.e. a hard displacement against the position = momentum reversal → exit at `open[k+1]`. **Reason:** a displacement-driven breakout runs until an opposing displacement reverses it; the exit uses the *same* ratified primitive as the entry, so it is family-native, not a level borrowed from another family. Resolves at the **first of**: stop breached · opposing expansion · block boundary (time-stop). |
| **management** | **DECLARED ABSENT** (no partials/breakeven/trailing) — DEMO_BASELINE minimalism. |
| **sizing** | **Fixed 1R, risk-normalized** to `entry − stop`. No equity-%. **Reason:** R-metrics are sizing-invariant; avoids the deauthorized equity-% parameter. |
| **min_trades** | **Deferred to the Statistician's DEMO criteria.** |

**Validity guards (structural, lookahead-safe):** no trade if the entry (`open[i+1]`) is already beyond the
stop (`open[i+1] <= low[i]` for a long; symmetric for a short). All Part-B coordinates known at entry → no
lookahead.

**FAIL-CLOSED check:** buildable from ratified primitives + raw OHLC without inventing any calculation
(stop = a bar extreme; exit = an opposing displacement from the same primitive). Method stands.

---

## Verdict — **DEFINED (DEMO_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
## Handoff (DEMO pipeline): Red Team → Statistician (DEMO criteria) → VE → CEO → AI Trader (DEMO only).
**Other candidate production continues in parallel. No production use.**
