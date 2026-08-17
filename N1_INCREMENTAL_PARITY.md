# N1 incremental replay — parity report (0.1.1 vs vendored 0.1.0 oracle)

The incremental engine's per-bar output is **byte-identical** to 0.1.0's `RawAxesBuilder`/`N1ReplayEngine`, proven on
the **result** and on the **intermediate state**, plus adversarial and structural attacks. All evidence is executable in
`ve_n1_replay/tests/test_incremental.py` (25 tests) in a `ve_brain`-equipped venv with the `ai_trader` repo absent.

## What is compared

| level | fields | oracle |
|---|---|---|
| **result (RawAxes)** | `is_compressed`, `is_displacement`, `direction`, `structure` | `RawAxesBuilder.observe` (blob `d071c8cb`) per bar |
| **engine result** | `output_fingerprint` (= `_fp(n1_output_fp, router_output_fp)`), `availability_status`, `applicable_regimes`, `reason_codes` | vendored `N1ReplayEngine.observe_closed_bar` |
| **intermediate state** | confirmed swings + labels HH/HL/LH/LL, `live_hh/ll/hl/lh`, `consumed` set, `latest_break` kind | `label_structure(detect_swings(...))` + `detect_breaks(...)` recomputed at each history length over `Block(0, i+1)` — the exact detectors `RawAxesBuilder` calls |

The intermediate-state oracle reconstructs, at every bar `i`, the ratified detectors over the full prefix `[0, i]` and
extracts the unconsumed confirmed swings per label, the consumed idx set, and the latest break (`max(breaks, key=idx)`,
tie → bull, matching `_structure_and_direction`). The incremental builder's `confirmed_unconsumed()` /
`live_labels_next()` / `consumed_idx()` / `latest_break_kind` are asserted equal to it **at each of the ~478 bars** of
each fixture, not merely at the end.

## Timing note on the intermediate-state view (why it is faithful, not a fudge)

A swing whose extremum is at `idx` is **confirmed** at `confirmed_idx = idx + k` (k=2). `detect_breaks` may only use a
swing once `confirmed_idx < c` (STRICT). The incremental builder therefore holds a swing confirmed *at* bar `i` in a
one-bar `_pending` slot and pushes it to the label stack at bar `i+1` — precisely when it first becomes usable for a
break. `confirmed_unconsumed()` folds that just-confirmed pending swing back into the "as-of-i" view (computing its
label against the current `last_high`/`last_low`, identical to `label_structure`), so the comparison is against the
oracle's `confirmed_idx <= i` set with no off-by-one. This deferral is *why* the result parity is exact.

## Results (all green, 25/25)

### Result parity
- `trend_up` (478 bars → `{TREND_UP}`/FULL), `trend_down` (478), `uncertain` (200 → `{UNCERTAIN}`/PARTIAL),
  `bos_bull` (18): **0 mismatches** on the RawAxes 4-tuple, every bar.
- Engine `output_fingerprint`: incremental `replay_batch` == vendored `N1ReplayEngine` per bar (byte-identical).

### Intermediate-state parity
- `trend_up`, `trend_down`, `bos_bull`: `confirmed_unconsumed`, `consumed`, `latest_break`, `live_hh/ll/hl/lh` all equal
  to the recomputed-detector oracle at **every** bar.

### Adversarial — swing older than the horizon
- **gap 460 / gap 500** (a swing formed, then 460/500 flat bars with no break, then a spike breaking that old swing):
  **full byte-parity** vs the oracle on every bar, including the break firing on the old swing after the gap.
- **gap 5000** (swing older than 5000 bars): the O(n²) oracle is intractable at this length **because of the very defect
  0.1.1 remedies** (a full 5019-bar oracle pass exceeded 9 minutes). Proven in two rigorous parts instead:
  - **bounded axes** (`is_compressed`, `is_displacement`) equal a *fresh oracle over only the trailing 460-bar window*
    at deep checkpoints (600/1500/3000/4800/5019) — the bounded-horizon claim of `N1_INCREMENTAL_HORIZON.md`, verified
    live deep in history;
  - **unbounded axes** (`structure`/`direction`): the old swing persists across the 5000-bar gap and the break re-fires
    (`direction`/`structure` non-None at the spike) — and the *logic* is the same forward `detect_breaks` replay already
    byte-verified against the oracle at gaps up to n≈3020 (age is irrelevant to `detect_breaks`, which rescans all
    unconsumed swings regardless of how old).
- Direct full-oracle byte-parity was additionally confirmed at n = 1020 / 2020 / 3020 (old swing up to 3000 bars back),
  with measured oracle O(n²) vs incremental ~O(n): oracle 12.4s / 77.9s / 205.0s vs incremental 2.2s / 4.8s / 7.7s
  (speedup 6× → 16× → 27×, growing).

### Structural attacks
- **chunk-size irrelevant**: feeding the same bars split into `[478]`, `[1,477]`, `[230,248]`, `[100,100,100,178]`,
  `[469,1,8]` with a snapshot/restore at each boundary yields the identical per-bar `output_fingerprint` sequence.
- **restart between swing and break**: snapshot taken with an unconsumed old swing on the stack but the break not yet
  fired, restored into a fresh engine, then the breaking bars fed → the break still fires identically
  (`latest_break_kind == "bos_bull"`), tail matches no-restart.
- **zero lookahead**: outputs for bars `≤ i` are independent of bars `> i` (identical prefixes across runs); mutating a
  bar changes that bar's output and leaves all earlier outputs unchanged, deterministically (repeatable).
- **two instances share no state**: one engine advanced 100 bars does not perturb a second engine's full-sequence
  output; `bars_observed` independent.
- **ledger key invalidation (fail-closed)**: changing any bar's content, or the horizon, changes `ledger_key`.
- **refusals**: out-of-order and conflicting-duplicate bars raise; a foreign-identity snapshot is rejected by `restore`.

## Conclusion

On every axis the mandate enumerates — swings, labels, `live_*`, consumed, breaks, latest break, structure, direction,
displacement, compression, RawAxes, fingerprints — the incremental engine reproduces 0.1.0 exactly. `N1_INCREMENTAL_PASS`
is **not** self-declared; this report is submitted for Red Team revalidation.
