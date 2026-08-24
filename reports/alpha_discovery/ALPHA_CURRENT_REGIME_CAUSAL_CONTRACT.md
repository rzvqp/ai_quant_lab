# ALPHA_CURRENT_REGIME_CAUSAL_CONTRACT (FROZEN)

**Mandate:** `VE-CURRENT-REGIME-TEMPORAL-CAUSALITY-REPAIR-001`. Infrastructure repair only — no strategy
rule, RR, stop, target, threshold, dedup, session, regime economics, or candidate identity is touched by
this contract or its implementation. Source audit: Statistician independent review
`STAT-CRS1-INDEPENDENT-REVIEW-FDR-001` (commit `4163382`, branch `statistician-foundation`,
`ai_quant_lab-alpha-automation`).

## The defect (confirmed by direct code inspection, not assumed from the audit alone)

`cur_screen.like_at` (and, structurally, anything joining an M15 timestamp to an `agg()`-produced H4/H1
bucket by that bucket's own `time` column) floored the M15 timestamp to its own H4 bucket's START and
looked up a label keyed by that same start. `sig_build.py`'s `like` flag at bucket-start `T` is computed
from descriptors (`vol_norm`/`vol_rel`/`effic`/`ddfh`/`ret60`) that all depend on that bucket's own `close`
— only knowable once the bucket actually closes, at `T+14400`. Any M15 timestamp in `[T, T+14400)` — i.e.
virtually every M15 bar inside the bucket — therefore saw a label computed from a bar that, from that M15
bar's own point of view, had not closed yet. Measured (Statistician, reproduced independently below):
100% of tested entries affected, median lookahead ≈135min, max 240min.

**This was not the only causal-alignment convention already in this codebase.** The SAME file's own
`cur_cr13_trade.py` (`h4_up_map`) already used a correct, independent convention for its H4-trend gate:
`pd.merge_asof(m15, h4[["close_time","ema_state"]], left_on="time", right_on="close_time",
direction="backward")` — the most recent H4 bucket whose own close is already known at the M15 decision.
The two gates disagreed. This contract makes the correct convention canonical and singular, not a second
one alongside it.

## The canonical contract (ENFORCED)

- `agg()` (`cur_data.py`) keys each aggregated H1/H4 bucket by its own **START** timestamp (`time`); a
  bucket's own `close_time` is `time + TF_SECONDS[tf]` (900s later than its last M15 sub-bar's own open,
  by construction — no partial bars).
- **Any label/descriptor/regime-state computed FROM a bucket's own data is only causally available starting
  at that bucket's `close_time`.** A finer-grained decision at timestamp `t` may consult only the bucket
  whose `close_time <= t` — never the bucket containing `t`.
- **The single canonical function**: `cur_data.causal_bucket_asof(times, bucket_starts, tf)` — a proper
  backward-asof search (`np.searchsorted` on `bucket_starts + TF_SECONDS[tf]`) over whichever buckets
  *actually exist* in `bucket_starts`, not fixed-offset arithmetic. Returns `-1` (sentinel) where no bucket
  has closed yet.
- **Why asof, not `T - TF_SECONDS[tf]`:** a fixed one-bucket-back shift assumes buckets exist at every
  regular calendar slot. They do not — the market closes over weekends/holidays, so the immediately-prior
  arithmetic slot is frequently absent from any real aggregated data. A fixed shift then silently defaults
  to "no data" (`False`/unmatched) for roughly one bucket-width after every reopen, discarding otherwise
  valid, already-closed information. Measured on the full canonical history: 5,352 of 355,696 M15 bars
  (1.5%) disagreed between the two methods — 5,208 of those (97%) at the Sunday reopen, the rest scattered
  holiday/gap closures. The asof form is causally IDENTICAL in safety (it can never reach a bucket that
  has not closed) and strictly more informative (it correctly carries the last-known state across a gap,
  exactly matching `cur_cr13_trade.py`'s own already-established `merge_asof`-backward convention — cross-
  validated exactly equal to it across the full 355,696-bar history, zero divergence).
- **Every join from an M15 (or any finer-grained) entry timestamp to a per-bucket label keyed by `agg()`'s
  own `time` column — including every `__cur_cache__/*.parquet` cache built from one — must go through
  `causal_bucket_asof`.** No file re-derives the floor/shift arithmetic locally.

## Concrete instantiation: `cur_screen.like_at`

```python
def like_at(times):
    _load(); h4 = CD.causal_bucket_asof(times, _LK_STARTS, "H4")
    return np.array([bool(_LK.get(int(t), False)) for t in h4])
```

`_LK_STARTS` = the sorted array of every H4 bucket-start timestamp actually present in
`current_like_h4.parquet` (cached once at `_load()`, not re-sorted per call).

## Verification performed (mechanical, not asserted)

- `causal_bucket_asof` exactly reproduces `cur_cr13_trade.py`'s own independent `merge_asof`-backward-on-
  `close_time` construction across the full canonical history (355,696 M15 bars, zero mismatches after the
  asof redesign; 5,352 mismatches under the naive fixed-offset predecessor, fully explained by gaps, see
  above).
- `like_at`'s own returned boolean values (not merely the underlying arithmetic helper in isolation) were
  checked against an independently-computed expectation and against the exact Statistician counterexample
  shape (an M15 entry inside a bucket must never see that bucket's own flag) — see
  `test_cur_causal_alignment.py`.
- Tests were verified to actually catch the original defect, not merely assert against it: the fix was
  temporarily reverted (in-memory monkey-patch, no file touched) to the original `(t//14400)*14400`
  formula and the relevant tests were confirmed to fail before the real fix was restored.

## Scope boundary (explicit, per mandate)

This contract governs **timestamp alignment only**. It does not evaluate, retune, or pass judgment on any
strategy rule, threshold, RR, stop, target, dedup spacing, session window, or regime-economics claim.
Whether a given CR-1..CR-15 result survives causal execution is a **separate, subsequent** question,
answered by replaying each candidate's own exact frozen definition against this now-corrected
infrastructure — never by modifying the candidate's own definition to fit.

**Frozen.**
