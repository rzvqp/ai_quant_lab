# AI Trader — Item #7 Verification: Is the Loop Complete?

**Nature of this document**: verification only, per explicit instruction. No code was written, modified,
or wired. No commit exists to any package under `ai_trader/`. Every claim below is traced to a specific
line in already-published code (commit `75585b6`), not inferred or assumed.

---

## Question 1 — Is the loop complete?

**What the system does now, verified in code**: a repository-wide search for any caller of
`CandidateSignalProducer.run_once()` or `LiveBarFeed.poll()` outside their own definitions and outside
test files returns **zero matches**. A repository-wide search for `while True`, `schedule`,
`APScheduler`, `asyncio.run`, or `threading.Timer` anywhere in `ai_trader/` (excluding tests) also
returns **zero matches**. `run_once()`'s own name is literal: it performs one poll → evaluate → journal
cycle and returns a tuple; nothing anywhere calls it more than once, nothing anywhere spaces its calls
in time.

**What it should do**: something external needs to invoke `run_once()` repeatedly, at an interval tied
to the bar timeframe, for the pipeline to run unattended. `LiveBarFeed`'s own dedup logic
(`_last_emitted_ts_open`) already makes it SAFE to poll faster than the bar interval — an over-frequent
caller would simply see empty results between closes — but nothing calls it at all today, at any
frequency.

**Verdict on subsumption**: **#7 is NOT subsumed by #6.** A scheduler/loop is a genuinely separate,
currently nonexistent piece — Piesa 1/2/3 give the system eyes; nothing yet moves those eyes repeatedly.

---

## Question 2 — What happens when a bar is missed?

**What it does now, verified in code** (`ai_trader/live_signal_source/bar_feed.py:45-83`): each `poll()`
call fetches `copy_rates_from(symbol, timeframe, now, lookback_count)` — by MT5's own semantics this
returns at most `lookback_count` bars ending at `now`, regardless of how long it has been since the
previous successful `poll()`. The only check against a bar being processed twice is
`ts_open <= self._last_emitted_ts_open` (line 71) — there is **no check anywhere that the next emitted
bar's `ts_open` is exactly one `bar_seconds` after the previous one**. That means:

- A gap **smaller than `lookback_count` bars** happens to be recovered on the next `poll()` — the missed
  bars are still inside the window `copy_rates_from` returns, and they pass the dedup check since their
  `ts_open` is newer than `_last_emitted_ts_open`. This recovery is an accidental side effect of the
  window size, not the result of any deliberate gap-detection logic — nothing marks these bars as
  "recovered after a gap" versus "normal sequential processing."
- A gap **larger than `lookback_count` bars** — exactly what a dropped connection, a terminal restart
  mid-session, or the ~21:00 UTC OANDA maintenance window you describe could produce — is **not
  recoverable and not detected**. `copy_rates_from` still succeeds and returns a full, valid set of the
  most recent rates, so `BarFeedError` is never raised (nothing is missing from the RESPONSE, only from
  history the response no longer reaches). The older, un-returned bars are gone; nothing in this code
  path knows they ever should have existed.

There is no reason code, no flag, no journal field for "a gap occurred here." A `LiveSignalJournalEntry`
only exists for bars the feed actually returned — the journal, as built, has no way to represent "we do
not know what happened between these two timestamps," so it reads identically to "nothing happened."

**What it should do**: the feed needs to be able to detect that the next bar it received is not the one
immediately following the last one it emitted, and record that fact somewhere durable and visible —
rather than silently proceeding as though nothing was missed, which today is exactly what happens in
every case above the recovery-by-accident window size.

---

## Question 3 — Does it survive a restart?

**What it does now, verified in code**: `LiveBarFeed._last_emitted_ts_open`
(`bar_feed.py:43`) is a plain instance attribute, set to `None` in `__init__` and never read from or
written to anything outside the object's own memory. A fresh `LiveBarFeed` constructed after a restart
starts with `_last_emitted_ts_open = None`. Separately, `LiveSignalJournal._entries`
(`journal.py:21`) is a plain Python list, also never persisted — a restarted process's journal begins
genuinely empty.

Two concrete, verified consequences follow:

- **Duplicate re-processing.** With `_last_emitted_ts_open is None`, the dedup check on line 71 is
  `False` for every bar (the `is not None` guard fails first), so the very first `poll()` after restart
  re-emits every closed bar still inside the lookback window — including ones already evaluated and
  journaled in the process that just ended. This is a failure mode Question 2's mid-run gap does NOT
  have (`_last_emitted_ts_open` never resets during one continuous run).
- **Total loss of prior history.** Bars closed further back than the lookback window before the restart
  are permanently lost, same mechanism as Question 2's large-gap case — but compounded by the journal
  itself also restarting empty, so there is no longer any record that a prior run even happened, let
  alone what it saw.

**Are Questions 2 and 3 the same problem or two distinct?**

**Two distinct triggers, converging on the same class of symptom.** Question 2's failure exists even
with **zero restarts** — a mid-run pause exceeding the lookback window loses bars purely because
`copy_rates_from` only ever returns a bounded recent window, independent of process continuity. Question
3's failure is caused specifically **by** the restart discarding in-memory state (the watermark, and
separately the entire journal) that would otherwise have remained perfectly correct — a persistence
problem, not a windowing problem.

Both are, however, the same STRUCTURAL pattern already disclosed on a different variable at Phase 2A
Step 3: the equity high-water mark and the consecutive-loss window are each "an in-memory-only value
whose only correctness guarantee depends on uninterrupted process continuity, silently degrading the
moment that continuity breaks." This is that same pattern's third and fourth occurrence, on two new
variables (`LiveBarFeed`'s watermark, and — a disclosure beyond what Step 3 named — `LiveSignalJournal`'s
entire observation history, not just one summary statistic).

---

## New item found, not yet in the dependency graph

`LiveSignalJournal`'s own restart-survival gap is broader than the bar-feed watermark alone: it means
**no observation history survives any restart at all**, not just a dedup reference. Fixing the bar
feed's watermark alone would not fix this — the journal itself would still start empty. Added to the
dependency graph as its own item (below), separate from the bar-feed watermark and from the gap/
continuity-detection item, since the three are distinct fixes even though they share one root
symptom class.

Three items added to `AI_TRADER_PHASE2A_DEPENDENCY_GRAPH.md`, all **NOT authorized to build**:

- **Bar/gap continuity detection** (Question 2) — applies with or without a restart.
- **`LiveBarFeed` watermark restart-survival** (Question 3, part 1) — prevents duplicate re-emission.
- **`LiveSignalJournal` history restart-survival** (Question 3, part 2, newly found) — prevents total
  loss of the observation record itself.

---

**Stopping here per instruction.** No code touched, no package wired, no loop started. Dependency graph
updated with the three findings above and this report's reference; #7's disposition (closed as subsumed
or held open) is left for you to decide from these answers, as instructed.
