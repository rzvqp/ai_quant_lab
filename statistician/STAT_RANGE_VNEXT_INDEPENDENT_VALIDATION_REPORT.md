# STAT — RANGE LIFECYCLE vNEXT INDEPENDENT VALIDATION

**Mandate ID:** `STAT-RANGE-LIFECYCLE-VNEXT-INDEPENDENT-VALIDATION-001`
**Division:** Statistician (independent statistical validation)
**Date:** 2026-08-22
**Subject:** VE `bba6310bd30caf5ca26c46a90a0f714461a8ddbc` — `RANGE_LIFECYCLE_VNEXT_CANDIDATE_READY_FOR_INDEPENDENT_VALIDATION`

**Scope directives honoured:** `INDEPENDENT_VALIDATION_ONLY` · `NO_IMPLEMENTATION_CHANGES` ·
`NO_THRESHOLD_RETUNING` · `NO_PNL` · `TRUE_CANONICAL_WARMUP` · `REPRODUCE_V4_4_PATHOLOGY` ·
`VALIDATE_MULTI_CANDIDATE_ARCHITECTURE` · `AUDIT_MERGE_IDENTITY` · `AUDIT_SUPERSESSION` ·
`AUDIT_PREMATURE_KILLS` · `DISTINGUISH_CONFIRMED_STRUCTURE_FROM_CANONICAL_SELECTION_CHURN` ·
`VERIFY_FORMATION_AGE_GATE` · `VERIFY_ACTIVE_REGISTRY_BOUND` · `VERIFY_RESTART_DETERMINISM` ·
`CLASSIFY_SNAPSHOT_GROWTH_LIMITATION` · `547_TESTS_REPRODUCE`

**Nothing was modified.** No implementation, config, threshold, test, cap, merge rule, supersession rule or
RANGE semantic was changed. Defects are reported, not fixed.

---

## 0 — TERMINAL VERDICT

```
RANGE_LIFECYCLE_VNEXT_INDEPENDENT_VALIDATION_FAIL
RANGE_LIFECYCLE_VNEXT_UNBOUNDED_STATE_BLOCKER
```

**Ten of the eleven §22 gates PASS, most of them exactly.** The candidate is a genuine, well-built
architectural repair and is dramatically safer than the rejected v4.5. It fails on one specific, structural,
mechanically-demonstrated point:

> **Gate C — "candidate population remains bounded" — is not delivered.** The cap is tested only on the
> REPLACEMENT admission branch. **CONTINUATION admits a candidate and removes none, and is ungated.** Driving
> only the engine's own code path with `cap = 3`, I reached **34 active candidates** — 11× the cap — with
> `REGISTRY_CAPACITY_REFUSED` never emitted. The bound the verdict rests on held **empirically** (max 4 over
> 15 years), never **structurally**.

§12 required me to "establish that the hard cap is actually enforced deterministically" and stated
"**No candidate explosion is allowed**". I tested it adversarially, as instructed, and it is not enforced.

**This is one ungated branch, not a design failure.** I expect it to be a small, well-scoped fix — but §2
and §25 forbid me from making it, and §22 requires *all* material claims to be supported.

---

## 1 — IDENTITY AND SCOPE RECONSTRUCTION (§3)

| item | value | |
|---|---|---|
| commit | `bba6310bd30caf5ca26c46a90a0f714461a8ddbc` | ✓ |
| parent | `3b18028` (v4.5 `RECOVERY_BLOCKED`) | ✓ |
| branch | `discovery-mk-matrix-v1` | ✓ |
| changed-file scope | **7 files, 2,509 insertions, 0 deletions — purely additive** | ✓ |
| v4.3 / v4.4 source | `git diff --stat` **empty** on every v4.3/v4.4 file | ✓ **untouched** |
| mirrors | alpha1 / discovery / lab / trader — **all four MATCH** | ✓ |
| data | `OANDA_XAUUSD_M15.csv`, sha256 `57f4ed9544993c8f…`, **355,696 bars**, 2011-07-26 → 2026-07-27 | ✓ |
| v4.4 config_id | `23d98c07488913c1…` | ✓ |
| vNext config_id | `3f2f7ba6bef59d68…` | ✓ |
| contract | `range-hierarchical-vnext-multicandidate-v1` | ✓ |

**Config identity — no retuning (§2).** All **21 inherited v4.4 fields are byte-identical**. Exactly two
differences: `contract_version`, and one new field `max_active_macro_candidates = 16`. The thresholds the new
mechanisms consume are unchanged: `tol_cluster = 1.6`, `d_macro = 29`, `IOU_CONTINUE = 0.5`.

**One identity weakness, reported not fixed.** `RANGE_HIERARCHICAL_VNEXT_IMPLEMENTATION_FINGERPRINT` is the
hand-written string `"vnext-implementation-freeze-2026-08-22"`, not a content hash — and `restore_state`
guards snapshot compatibility on it. An edited implementation would still accept an old snapshot. The guard
names an integrity property it does not enforce. **Severity: INFORMATIONAL.**

---

## 2 — BASELINE PATHOLOGY REPRODUCTION (§5) — **PASS, EXACT**

Independent dual-engine replay, true canonical warmup (**the first bar of the file — no arbitrary replay
start date**), 355,696 M15 bars.

v4.4 canonical CONFIRMED bars per year:

| 2011 | 2012 | 2013 | 2014 | 2015 | **2016–2024** | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| 946 | 1226 | 2394 | 1933 | 1357 | **0, all nine years** | 686 | 24 |

**Byte-identical to VE's published table.** Total confirmed bars 8,566; **`OK_RANGE_MACRO` events = 187** —
the canonical 187 confirmations the entire RANGE lineage cites, independently reproduced from scratch.

```
  v4.4 confirmed bars, 2016-2024 : 0
  v4.4 EPISODE_MERGED, full 15y  : 0     <- v4.4's MERGE branch is genuinely unreachable, as VE stated
```

The pathology is real, is not a data-gap artifact, and is exactly as severe as reported.

---

## 3 — FULL-HISTORY vNEXT REPLAY (§6) — **PASS, EXACT**

| metric | mine | VE | |
|---|---|---|---|
| total bars | 355,696 | 355,696 | ✓ |
| candidate births (macro) | **12,813** | 12,813 | **MATCH** |
| ↳ replacements / merges / continuations | 11,607 / 361 / 845 | — | decomposed here |
| `EPISODE_MERGED` | **361** | 361 | **MATCH** |
| `CANDIDATE_SUPERSEDED_BY_MERGE` (macro) | **361** | 361 | **MATCH** |
| `CANDIDATE_ABANDONED_PRICE_MOVED_ON` (macro) | **4,108** | 4,108 | **MATCH** |
| `REGISTRY_CAPACITY_REFUSED` | **0** | 0 | **MATCH** |
| genuine confirmations `OK_RANGE_MACRO` | **4,092** | 4,092 | **MATCH** |
| occupancy min / median / p95 / p99 / **max** | 0 / 1 / 2 / 2 / **4** | identical | **MATCH** |
| bars with zero active | 28,075 | 28,075 | **MATCH** |
| bars with >1 active | 73,229 | 73,229 | **MATCH** |
| longest zero-active run | 45 bars | 45 | **MATCH** |

Confirmed bars per year 2011→2026: 2745, 7077, 6802, 7704, 7603, 6717, 7068, 7660, 6595, 7537, 6743, 6429,
7237, 6727, 5952, 3597 — **every value identical to VE's table**.

### 3.1 Two VE reporting slips (summary fields only; the underlying data is right)

1. VE's aggregate states **55,713** confirmed bars in the 2016–2024 window. Summing VE's own per-year table
   gives **62,713** — the figure I measure. Difference exactly 7,000; a digit slip in the summary field.
2. VE states the in-window range is "6,429–7,704 bars/year". **7,704 is 2014, outside the window.** The true
   in-window maximum is **7,660** (2018).

Neither affects the conclusion; both should be corrected in the record.

---

## 4 — 2016–2024 PATHOLOGY TEST (§7) — **PASS**

```
  v4.4  confirmed bars 2016-2024 : 0
  vNext confirmed bars 2016-2024 : 62,713   (per-year 6,429 - 7,660)
```

Confirmation activity is restored throughout the exact nine-year blocked window, and — per §7's instruction
not to compare totals alone — these are **genuine lifecycle structures**: all 4,092 vNext confirmations
satisfy the frozen formation gate (§7 below), and the historically stuck candidate still never confirms on
its own merits. The blocking is removed; the semantics are not loosened.

---

## 5 — CANONICAL-SELECTION CHURN (§14) — **PASS, and the effect is larger than reported**

| engine | genuine confirmations (`OK_RANGE_MACRO`) | canonical id transitions |
|---|---|---|
| vNext | **4,092** | 5,812 |
| v4.4 | **187** | 293 |

Transitions exceed genuine confirmations in **both** engines, so churn is not a vNext artifact — but no
transition-based count may be reported as a confirmation count. **VE identified this correctly and
self-corrected before delivery.** My measurement gives a larger inflation than VE's (5,812 vs their 4,240)
under a slightly different transition definition, which strengthens rather than weakens their caution. All
metrics in this report use `OK_RANGE_MACRO` events.

---

## 6 — FORMATION-AGE GATE (§13) — **PASS, perfectly**

Measured per structure (`confirm_ts − start_ts`), never per transition. Frozen `d_macro = 29`.

| engine | n | min | p1 | median | max | **below gate** |
|---|---|---|---|---|---|---|
| vNext | 4,092 | **29** | 29 | 29 | 649 | **0 (0.0000%)** |
| v4.4 | 187 | **29** | 29 | 36 | 16,658 | **0** |
| vNext, merge/continuation-born | 346 | **29** | — | — | — | **0** |

**Not one confirmation in 4,092 occurs below the frozen gate**, including the 346 born through a merge or
continuation identity. The reason is structural: MERGE and CONTINUATION both allocate a **fresh**
`StructureV44` with `start_ts = cand_start` and only the two pending swings. Identity inheritance **resets**
the formation clock rather than inheriting it — conservative, not permissive. Bypass is impossible by
construction.

★ **Correction of VE, in VE's favour.** VE reported "99.95% at/above the frozen age gate", implying ~2
violations. **I measure zero.** VE's own figure was pessimistic; the gate is perfectly held.

---

## 7 — MERGE IDENTITY (§10) — **PASS**

- **Id collision: structurally impossible.** `Registry.new_id()` is strictly monotonic; `_dead` refuses
  reuse (`DEAD_ID_REUSE_REFUSED`). 12,813 vNext and 426 v4.4 structures captured; **zero duplicate ids**.
- **No candidate overwrite** — every admission allocates a fresh id and inserts at that key.
- **No double counting** — confirmations counted from `OK_RANGE_MACRO` events, one per structure.
- **No future information** in the merge decision: `_episode_identity_for_new_macro_multi` reads only current
  active boundaries and the last-terminated zone.
- **Merge is not caused by canonical-selection churn** — canonical selection is a pure read; it mutates
  nothing.
- **v4.4's MERGE dead-code claim VERIFIED**: 0 firings in 15 years under v4.4, 361 under vNext.

**Semantic note, reported for the record:** MERGE discards the merged-into candidate's accumulated touches
and elapsed age. This is faithful to v4.4's own MERGE branch (which likewise builds a fresh structure and
overwrites the slot) and is conservative — but "merge" here means *replace-with-identity-link*, not
*combine-evidence*. The causal chain remains interpretable through `continued_from_id` / `predecessor_id`.

---

## 8 — SUPERSESSION / ABANDONMENT (§11) — **PASS**

| property | finding |
|---|---|
| uses only information available at that bar | **YES** — current `close`, current boundaries, current `atr_ref` |
| uses frozen pre-existing tolerance | **YES** — `tol_cluster · atr_ref`, `tol_cluster = 1.6` unchanged from v4.4 |
| encodes future confirmation outcome | **NO** |
| behaves as an arbitrary age timeout | **NO** — see below |
| never fires on an isolated candidate | **YES** — guarded by `len(active) < 2` |
| touches confirmed structures | **NO** — skips `reached_confirmed`; **0 of 4,092 confirmed structures ended by abandonment** |

**The age-timeout test.** If abandonment were an elapsed-time rule in disguise, terminated lifetimes would
cluster at a fixed age. They do not:

```
  abandoned lifetimes: n=4,108   median 27   p95 94   max 2,120 bars
  fired BEFORE the age gate (<29 bars): 54.50%
```

Dispersed across two orders of magnitude, with more than half firing before the age gate is even reachable.
**It is genuinely structural — "superseded by current structure", not "expired by elapsed time".** This is
the substantive difference from the T-STALE and v4.5 attempts, and it is real.

**Contribution:** 32.06% of all terminations (4,108 of 12,813) — the dominant new mechanism, as VE disclosed.
Termination profile: `ZONES_DEGENERATE` 39.30% (legacy) · abandonment 32.06% · `BREAKOUT_ACCEPTED` 25.64% ·
merge-supersession 2.82% · `ZONES_INVERTED` 0.18%.

---

## 9 — NEGATIVE CONTROL / PREMATURE KILLS (§8, §9) — **PASS on substance, FAIL on measurement rigour**

I built an independent matcher and **did not reuse VE's implementation**: all 187 real v4.4 confirmations
matched against vNext's complete 12,813-structure history by time-window overlap **and** zone overlap, with
forward merge/continuation chain following.

### 9.1 Primary result

| classification | n | share |
|---|---|---|
| CONFIRMED under a different identity | 173 | 92.51% |
| CONFIRMED via merge/continuation chain | 2 | 1.07% |
| **GENUINELY LOST (overlapped, never confirmed)** | **12** | **6.42%** |

**VE publishes 5/187 = 2.7% (or 4/187 = 2.14%). I measure 12/187 = 6.42%.**

### 9.2 The reason for the gap — the rate is not an identified quantity

| time tolerance | IoU > 0.0 | IoU > 0.1 | IoU > 0.3 |
|---|---|---|---|
| 0 bars | **12 (6.42%)** | 15 (8.02%) | 34 (18.18%) |
| 29 bars | 8 (4.28%) | 11 (5.88%) | 29 (15.51%) |
| **100 bars** | **4 (2.14%)** ← VE | 6 (3.21%) | 20 (10.70%) |
| 500 bars | 0 (0.00%) | 2 (1.07%) | 12 (6.42%) |
| 2000 bars | 0 (0.00%) | 0 (0.00%) | 4 (2.14%) |

**The premature-kill rate spans 0.00% – 18.18% purely as a function of two arbitrary matcher settings.**
VE's published figure is reproduced *exactly* at `tolerance = 100 bars, any zone overlap`. VE correctly
identified that the raw "24.6% lost" was a matching artifact — but the refined 2.7% is a point in the same
monotone family, and **the sensitivity was not disclosed**. This is the metric the whole verdict gates on
(§9: "This number is a CRITICAL validation gate").

### 9.3 A hypothesis I formed, tested, and had refuted

I suspected the matcher itself was reading a base rate: vNext emits **21.9× more confirmations** than v4.4
(4,092 vs 187), so a loose matcher should find "a confirmed structure nearby" for almost any window by
chance. I tested it with two placebos — same zone shifted 80,000 bars into the wrong era, and right era with
a shuffled zone:

| setting | real match | time-shifted placebo | zone-shuffled placebo | discrimination |
|---|---|---|---|---|
| tol 0, IoU>0 | 92.5% | 4.3% | 2.7% | **+88.2%** |
| tol 100, IoU>0 | 97.3% | 6.4% | 7.0% | **+90.4%** |
| tol 2000, IoU>0.3 | 96.8% | 13.9% | 15.0% | **+81.8%** |

**My hypothesis is refuted.** Discrimination is +76% to +90% at every setting. The matcher genuinely measures
correspondence, not chance. **VE's matching approach is sound** — only the undisclosed tolerance sensitivity
is at issue. I report this because a suspicion I raised and could not sustain belongs in the record as
prominently as one I could.

### 9.4 The honest interval, and mechanism attribution

The defensible core is **2.14% – 6.42%** (the IoU>0 family). I judge the 18.18% endpoint over-strict: it
requires IoU>0.3, which penalises legitimate re-forming — a merged candidate restarts with only two swings,
so its zone is necessarily narrower than its predecessor's.

Attribution among the 12 lost at my primary setting:

```
  price-abandonment present  : 11
  merge-supersession present :  0     <- INDEPENDENTLY CONFIRMS VE exactly
  capacity-refusal present   :  0     <- INDEPENDENTLY CONFIRMS VE exactly
  legacy ZONES_DEGENERATE    :  6     <- pre-existing v4.3/v4.4 semantics, not vNext
```

**Merge and capacity are clean at 0/187 — exactly as VE reported.** Abandonment is the contributor, as VE
disclosed.

---

## 10 — CANDIDATE EXPLOSION / BOUNDED STATE (§12) — **FAIL. THE BLOCKER.**

### 10.1 Empirical bound — clean

```
  occupancy: min 0 · median 1 · p95 2 · p99 2 · max 4 · mean 1.134
  registry-capacity refusals over 355,696 bars: 0
```

Max 4 against a cap of 16 — the registry never came within 12 of the cap. **VE's empirical claim is exactly
correct.**

### 10.2 Deterministic cap enforcement — enforced on one branch of three

The check is:

```python
if action == "REPLACEMENT" and len(self._active_macros) >= self._cfg.max_active_macro_candidates:
```

- **MERGE** supersedes one candidate and admits one → net zero. Cannot grow the registry. ✓
- **REPLACEMENT** is gated. Verified deterministically at caps 1, 2, 3 and 16: refused every time,
  `REGISTRY_CAPACITY_REFUSED` emitted, registry never exceeded. ✓
- **CONTINUATION admits a candidate and removes none, and is not gated.** ✗

Adversarial test, driving only the engine's own `_offer_swing_everywhere` with no implementation change:

```
  cap = 3, seeded 3 active
  arrange a CONTINUATION (recently terminated macro, non-BREAKOUT end reason, zone IoU >= 0.5, within GAP_MAX)
  -> action = CONTINUATION -> admitted -> active = 4 > cap = 3, no REGISTRY_CAPACITY_REFUSED
  after 30 further engineered CONTINUATION offers -> active = 34   (11.3x the cap)
```

**The CONTINUATION branch is not hypothetical: it fires 845 times over the real 15-year history.** It simply
never coincided with a full registry, because occupancy never exceeded 4.

### 10.3 Why this is a blocker rather than a note

VE's architecture doc §7 does honestly document the REPLACEMENT-only check. But the same section calls it
"a hard cap on `len(self._active_macros)`" that "bounds worst-case memory" — and it does not. §4 of this
mandate lists "registry growth is bounded by a hard active-candidate cap" as an intended property I must
**verify mechanically rather than accept**. I verified it, and it does not hold.

§12 is unambiguous: establish enforcement **deterministically**; **no candidate explosion is allowed**. The
guarantee the verdict gates on is empirical, not structural — and this program has already rejected v4.5 for
failing a structural standard that an empirical reading would have passed.

**Why VE's own suite did not catch it:** `test_vnext4` and `test_vnext4b` both seed a *non-overlapping*
candidate, which forces the REPLACEMENT branch. **No test places a CONTINUATION at capacity.**

---

## 11 — RESTART / DETERMINISM (§16) — **PASS**

| test | result |
|---|---|
| 12,000 bars continuous vs snapshot@7,000 → restore → resume | **0 mismatching bars** |
| double restart: snapshot@3,000 → restore → snapshot@6,500 → restore → resume | **0 mismatching bars** |

Compared per bar: `macro_id`, `macro_state`, `macro_reason`, `active_macro_count`, `active_macro_ids`, both
boundaries, `regime`, and the full event tuple `(kind, depth, structure_id)`. **Identical registry, lifecycle
state, canonical output, future confirmations and reason codes. No hidden in-memory-only behaviour.**

---

## 12 — CAUSALITY (§15) — **PASS**

`observe()` ordering: ATR applied → confirmed swings offered → closes pushed → per-candidate step → reversal
watches → price-abandonment retirement → internal step → canonical selection. Every operation reads only bar
*i*'s OHLC/ATR plus prior state. **No future-bar leakage found.** All iteration is via `sorted()`, with ties
broken by lowest `structure_id`; the per-candidate loop is explicitly guarded against concurrent removal.
Warmup is controlled — the replay starts at the file's first bar, with no arbitrary start date. The
zero-mismatch restart result is independent empirical confirmation.

---

## 13 — SNAPSHOT GROWTH (§17) — **`REMEDIATION_REQUIRED_BEFORE_PRODUCTION`**

Measured independently on both engines over an identical 60,000-bar window:

| bars | vNext bytes | `_dead` | `_awaiting_role` | active | v4.4 bytes | `_dead` | `_awaiting_role` |
|---|---|---|---|---|---|---|---|
| 10,000 | 234,044 | 401 | 92 | 1 | 128,431 | 60 | 14 |
| 30,000 | 426,032 | 1,210 | 237 | 1 | 220,052 | 143 | 45 |
| 60,000 | 758,494 | 2,301 | 475 | 1 | 337,497 | 318 | 90 |

- **What grows:** `Registry._dead` and `_awaiting_role` — monotonically, with **lifetime** candidate count.
- **Why:** `_dead` implements the never-reuse-a-dead-id contract; `_awaiting_role` holds full structure
  snapshots cleared only under a narrow later-CONTINUATION condition most candidates never satisfy.
- **Not active-state explosion:** occupancy stayed at 0–1 throughout. `_macro_history` is genuinely bounded
  (`deque(maxlen=64)`) and contributes nothing. **VE's root-cause attribution is confirmed exactly.**
- **Genuinely inherited:** v4.4 grows at 4.18 B/bar by the same mechanisms. Not introduced by vNext.
- **Rate:** I measure 10.49 B/bar for vNext over 10k–60k. VE's own checkpoints give 3.96 B/bar over
  100k–355k. **Both are right — growth decelerates**, so my early-window extrapolation overstates the
  endpoint; VE's measured ~1.43 MB over 15 years stands.
- **Determinism impact: none.**

**Classification: `REMEDIATION_REQUIRED_BEFORE_PRODUCTION`.** 1.43 MB over 15 years is operationally trivial
for M15 and does not threaten this validation — but the state is monotonic with no eviction and
snapshot/restore sits on the restart critical path, so an indefinitely-running live engine has unbounded
serialization state. VE's "practically negligible" is fair on magnitude and slightly under-stated on class.
Remediation is lineage-wide (v4.3/v4.4/vNext), not vNext-specific. **Not fixed here.**

---

## 14 — RUNTIME (§18) — bounded for M15

| percentile | vNext | v4.4 |
|---|---|---|
| mean | 6,021 µs | 5,982 µs |
| median | 5,285 µs | 5,239 µs |
| p95 | 9,874 µs | 9,861 µs |
| p99 | 10,969 µs | 10,962 µs |
| max | 78,545 µs | 112,376 µs |

Measured **with** my per-bar structure-capture overhead, so VE's isolated 5,323 µs mean is the cleaner
figure. vNext is not materially slower than v4.4 at any percentile. Against an M15 budget of 900,000,000 µs
per bar there is ~5 orders of magnitude of headroom **including the max outlier**. Distribution reported, not
just the mean, per §18.

---

## 15 — EXISTING TESTS (§19) — 546/547; the one failure is environmental

```
  1 failed, 546 passed in 132.19s
  FAILED test_range_semantic_v4_3.py::test_mypy_strict_clean_on_all_touched_files
    incremental.py:22: error: Unused "type: ignore" comment  [unused-ignore]
```

**I do not score this against VE.** `incremental.py` was **not touched by this commit** (last modified at
`07da208`), and the assertion is a mypy-version-sensitive check on how `import ve_brain` resolves in the
local environment (mypy 2.3.0 here). VE's 547/547 claim is credible.

**Coverage audit — genuinely good, with one gap.** The 30 new tests exercise concurrent candidates (3),
merge (5), supersession/abandonment (5), canonical arbitration (3), capacity (2), causality (1),
determinism/restart (4), v4.4 isolation (2) and scope (5); two of them drive the real
`observe`/`_offer_swing_everywhere` path rather than synthetic seeded state. **The gap is exactly the defect
of §10:** both capacity tests force the REPLACEMENT branch, and nothing tests the cap under CONTINUATION.

---

## 16 — COMPARISON TO v4.5 (§21) — vNext is materially safer, and this holds under my stricter measurement

| | v4.5 (rejected) | vNext |
|---|---|---|
| premature-kill rate | **36.9% / 12.3% / 69.0%** | **2.14% – 6.42%** |
| mechanism | age/persistence release rules — kill slow candidates | multi-candidate registry — slow candidates simply stop blocking |
| isolated slow candidate | destroyed | **structurally protected** (`len(active) < 2` guard) |
| confirmed structures killed | — | **0 of 4,092** |

**This is not a different expression of the same stale-timeout failure.** v4.5 removed slow candidates;
vNext keeps them and removes their monopoly on the slot. The abandonment mechanism that could have
reintroduced the failure is demonstrably not an age rule (§8), never touches an isolated candidate, and
never touches a confirmed one.

**VE's §21 conclusion holds even at my stricter setting** — 6.42% is materially below all three v4.5 figures,
and at VE's setting it is an order of magnitude below. **This is the central architectural claim and it
survives independent scrutiny.**

---

## 17 — §22 GATE TABLE

| gate | claim | verdict |
|---|---|---|
| **A** | v4.4 pathology independently reproduced | **PASS** — exact, byte-identical per-year |
| **B** | vNext removes the single-slot blocking pathology | **PASS** — 62,713 bars restored in 2016–2024 |
| **C** | candidate population remains bounded | **FAIL** — cap ungated on CONTINUATION; 34 reached at cap 3 |
| **D** | confirmation semantics remain causal | **PASS** |
| **E** | merge identity is valid | **PASS** — monotonic ids, 0 collisions, 0/187 loss involvement |
| **F** | formation-age gate preserved | **PASS** — 0 of 4,092 below gate |
| **G** | restart / determinism holds | **PASS** — 0 mismatches, single and double restart |
| **H** | premature-kill rate acceptably low **and correctly measured** | **PARTIAL** — low (2.14–6.42%) but the point estimate is not robust; sensitivity undisclosed |
| **I** | no major false-confirmation mechanism introduced | **PASS** |
| **J** | snapshot-growth limitation correctly classified | **PARTIAL** — root cause and magnitude accurate; class under-stated (see §13) |
| **K** | measurement does not inflate confirmation counts | **PASS** — VE separated churn correctly; I confirm |

---

## 18 — LIMITATIONS

1. My replays include a per-bar structure-capture overhead; latency figures are upper bounds.
2. `maxDD`-style equity concepts do not apply here — **no P&L was computed** (§20).
3. The premature-kill interval (2.14–6.42%) is a *range*, deliberately. I do not claim a point estimate,
   because §9.2 shows the metric is not identified without a pre-registered matcher.
4. My cap-bypass construction drives `_offer_swing_everywhere` directly with a synthetic terminated-macro
   state. The CONTINUATION branch fires 845 times on real data, so the branch is genuinely reachable; I did
   **not** demonstrate the *conjunction* (full registry **and** continuation) arising organically, and it
   never did in 15 years.
5. Restart determinism was tested over 12,000 bars, not the full 355,696.
6. **Nothing was modified.** No fix was applied to any defect reported here.

---

## 19 — HANDOFF

| action | owner | blocking? |
|---|---|---|
| Extend the capacity check to the CONTINUATION admission branch (or state, and test, an explicit bound covering all three branches) | **VE**, on CEO mandate | **YES** |
| Add a test placing a CONTINUATION at capacity | VE | yes |
| Pre-register the negative-control matcher (tolerance + overlap threshold) before re-measuring the premature-kill rate | Statistician spec → VE | yes, for gate H |
| Correct the two summary-field slips (55,713 → 62,713; in-window max 7,660) | VE | no |
| Make `implementation_fingerprint` a content hash | VE | no |
| Snapshot-growth remediation across the v4.3/v4.4/vNext lineage | separate mandate | no, for this verdict |

**After remediation this candidate is, in my assessment, close to ready.** Ten of eleven gates pass, most of
them exactly reproduced, and the architectural thesis — solve blocking by removing the monopoly rather than
by killing slow candidates — is independently validated and materially safer than the rejected v4.5.

**Not ratified. Not production-ready. Not New-Brain-ready. Not authorized for Market Intelligence
integration. v4.4 remains the canonical deployed research baseline.**

---

## 20 — ARTIFACTS

`statistician/range_vnext/` — `STAT_RANGE_VNEXT_BASELINE_REPRODUCTION.json` ·
`STAT_RANGE_VNEXT_LIFECYCLE_METRICS.json` · `STAT_RANGE_VNEXT_NEGATIVE_CONTROL.json` ·
`STAT_RANGE_VNEXT_IDENTITY_MERGE_AUDIT.json` · `STAT_RANGE_VNEXT_RESTART_CAUSALITY_AUDIT.json` ·
`STAT_RANGE_VNEXT_PERFORMANCE_LIMITATIONS.json` · reproduction code (`full2.py`, `restart_cap.py`,
`cap_bypass.py`, `neg2.py`, `sens.py`, `placebo.py`, `age.py`, `snapgrow.py`).

**Environment:** Python 3.14, mypy 2.3.0, data sha256 `57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37`
(355,696 bars), commit `bba6310`, v4.4 config `23d98c07…`, vNext config `3f2f7ba6…`.
**Test command:** `python -m pytest ve_n1_replay/tests -q`.

---

*Statistician division — independent statistical validation. Verdicts are scoped strictly to the evidence
examined and are not transferable to adjacent claims.*
