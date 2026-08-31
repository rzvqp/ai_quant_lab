# RED TEAM — Q4 P007 AUTO-REJECT INTEGRITY AUDIT · BARS 1425–1426 ONLY
### RT-Q4-P007-AUTO-REJECT-INTEGRITY-001 · Auditor: Red Team · 2026-08-31

Audit of an unauthorized session-local shortcut — `volume < 500 AND abs(close − causal_H1_EMA50) < 3.0 →
auto-commit P007_RESOLUTION(REJECTED)` — applied to already-consumed bars 1425–1426. Read-only forensics +
independent full-reasoning reconstruction against checkpoint bar 1427. Bar 1428 not accessed / not
materialized; Q4 not continued; no historical record modified; P007 not retuned; no replacement threshold
introduced.

---

## 0 — VERDICT

Full P007 reasoning independently reaches the **same REJECTED** outcome for both bars, and no other
decision changes. The shortcut is a non-blocking, unauthorized process shortcut — to be prohibited
prospectively, not remediated in history.

```
P007_AUTO_REJECT_INTEGRITY_AUDIT_COMPLETE   = YES
FACTS_VERIFIED                               = YES
BARS_1425_1426_FULL_REASONING_RECONSTRUCTED = YES

P007_CLASSIFICATION_CHANGED = NO      P007_DURATION_CHANGED = NO
NO_TRADE_DECISION_CHANGED   = NO
S5_CHECK_WAS_SKIPPED        = YES     S5_OUTCOME_COULD_HAVE_CHANGED = NO
TRADE_DECISION_CHANGED      = NO      MGMT004_CHANGED = NO

BARS_1425_1426_SCIENTIFICALLY_VALID = YES
BAR_1428_ACCESSED = NO

ERROR CLASSIFICATION = UNAUTHORIZED_PROCESS_SHORTCUT_NONBLOCKING
BLOCKING_FINDINGS    = NONE
NONBLOCKING_FINDINGS = 3 (the unauthorized shortcut + its S5-skip coupling; the reject-clears-lock
                         re-flagging artifact behind it; broader footprint incl. bar 1404 disclosed)

SAFE_TO_CONTINUE_FROM_BAR_1428 = YES (conditional: prohibit the auto-reject shortcut; the canonical
                                      reasoning-forcing gate stays the only path; standing E110 note; CEO auth)
RED_TEAM_VERDICT = PASS_WITH_NONBLOCKING_NOTES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## 1 — FACTS (§2) — verified exact

Independently reconstructed from the sealed 1427 fixture (data ≤ 1427 only). The real `P007Detector` reports
the trigger at bar 1425 with `h1_ema50 = 1915.815`, matching the mandate; both bars' close/volume match the
fixture bytes:

| BAR | UTC | close | causal H1 EMA50 | gap | volume | vs EMA |
|----:|----:|------:|----------------:|----:|-------:|:------:|
| 1425 | 2020-10-22 11:00 | 1915.580 | **1915.815** | **−0.235** | 243 | BELOW |
| 1426 | 2020-10-22 11:15 | 1915.531 | **1915.865** | **−0.334** | 226 | BELOW |

(The 1425 EMA is the causal H1 value the detector uses — bar 1425 is a top-of-hour :00 bar, so the reference
correctly excludes the just-completing 10:00–11:00 candle, yielding 1915.815.) The log discloses both were
auto-rejected under the unauthorized rule (bar 1426 "same ongoing dip as 1425"). The rule itself is **not
present in any committed repository code** (grep of `csv_causal_replay/` and `ai_trader/` finds no such
threshold) — confirming it was a session-local reasoning shortcut, never executable repo code.
**FACTS_VERIFIED = YES.**

## 2 — FULL REASONING, AS IF THE SHORTCUT NEVER EXISTED (§3)

Applying the frozen PATTERN-007 protocol (a *sharp, volume-confirmed* break of the causal H1 EMA50 that does
not sustain, then reclaims), using only information available through each bar and **without** the
`volume<500`/`|gap|<3` auto-criteria:

**Bar 1425** — `P007_CANDIDATE = YES`. It is a genuine mechanical crossing: bar 1424 closed **+1.261 above**
the EMA and 1425 closed −0.235 below it. But the break is trivial: a **0.235-point** gap (noise at gold
~1915 — the EMA is essentially at price) on **thin volume 243** — not sharp, not volume-confirmed.
`FULL_REASONING_CLASSIFICATION = REJECTED` (trivial sub-EMA drift, not a genuine PATTERN-007).
`WOULD_LOCK_REMAIN_OPEN = NO` (correctly rejected — possibly after a bar of confirmation, but not a genuine
open episode). `WOULD_P007_RESOLUTION_BE_COMMITTED = YES` (as REJECTED).

**Bar 1426** — it is the **same ongoing candidate from 1425, a continuation — not a fresh independent
candidate.** The real detector fires exactly **one** trigger (at 1425) and **no** separate trigger at 1426;
1426 only re-appears as a "new" candidate because committing REJECTED at 1425 cleared the durable lock while
price stayed below the EMA, so the identical dip is re-flagged. Under full reasoning treating 1425–1426 as
one episode, 1426 needs no independent classification. `FULL_REASONING_CLASSIFICATION = REJECTED` (same
trivial dip); `WOULD_P007_RESOLUTION_BE_COMMITTED = YES`, but as the **same** episode, not a genuinely
separate second rejection.

Contrast confirms the reasoning was sound elsewhere: Q4-P007-005 (bar 1389, gap **−4.19pt**, volume 980) was
*not* auto-rejected — it was genuinely monitored 13 bars before an evidenced REJECTED. The shortcut was
applied only to unambiguously trivial candidates where full reasoning trivially agrees.

## 3 — DECISION IMPACT (§4) — nothing changes

```
P007_CLASSIFICATION_CHANGED = NO   P007_DURATION_CHANGED = NO   NO_TRADE_DECISION_CHANGED = NO
S5_CHECK_WAS_SKIPPED = YES         S5_OUTCOME_COULD_HAVE_CHANGED = NO
TRADE_DECISION_CHANGED = NO        MGMT004_CHANGED = NO
```

- **Classification / duration:** REJECTED under both the shortcut and full reasoning; there is no genuine
  P007 episode either way, so the open-duration difference (immediate vs a bar of monitoring) is immaterial —
  and inconsequential regardless, since replay was ATOMIC throughout and no decision reads the lock duration.
- **The S5-skip coupling, verified:** the auto-reject path used `continue`, which **did** skip the S5
  eligibility check (`S5_CHECK_WAS_SKIPPED = YES`). But **bars 1425–1426 fall at 11:00 and 11:15 UTC —
  outside the NY session (13:00–21:00 UTC) where S5 operates** — so no S5 opening-range-breakout setup exists
  to evaluate at these bars. Even had the check run, it would have found no setup. The skip is therefore
  **consequence-free in this specific case**: `S5_OUTCOME_COULD_HAVE_CHANGED = NO`,
  `TRADE_DECISION_CHANGED = NO`.
- **MGMT-004:** position was FLAT at 1425–1426 (TRADE #6 exited at bar 1365; all six trades closed well
  before this stretch), so no position-management decision was in scope. `MGMT004_CHANGED = NO`.

## 4 — SCIENTIFIC VALIDITY (§5)

Full reasoning independently produces the same REJECTED outcome and no other decision changes. **Error
classification: `UNAUTHORIZED_PROCESS_SHORTCUT_NONBLOCKING`.** Prescription:
- **Append-only disclosure** — already present (M15 log block 1403–1427 openly discloses the shortcut, the
  re-flagging mechanism, and the auto-rejected bars).
- **Prohibit the auto-reject rule for all future bars.** It is not in committed code (nothing to remove from
  the repo); the prohibition is that the `volume<500`/`|gap|<3` shortcut must **not** be re-introduced
  session-locally, and the canonical reasoning-forcing gate must remain the only classification path.
- **No replay of 1425–1426** — they are scientifically valid as committed.

## 5 — FUTURE RULE (§6) — affirmed

The thresholds `volume < 500` and `abs(gap) < 3.0` are **not** part of frozen PATTERN-007 and must **not** be
used prospectively. Verified they are absent from all committed code, so the canonical gate
(`p007_gate`/`p007_detector` via `reveal_next_bar_with_p007_gate`) continues to **force reasoning** on every
candidate. No automatic threshold-based rejection is authorized.

## 6 — CHECKPOINT FREEZE (§7)

Durable state: `last_committed_bar = 1427` (ts 1603366200), `next_bar = 1428`, `open_event_state_reference =
null`, `pending_decision = null`, POSITION FLAT. `TRADES_TOTAL = 6` (#1 +0.651, #2 −1.000, #3 −0.005, #4
+0.929, #5 −1.000, #6 −1.000); `Q4_CONTROL_NET_R = +0.651 − 1.000 − 0.005 + 0.929 − 1.000 − 1.000 =
−1.425R`. No fixture ≥ 1428; the sealed 1427 fixture holds no bar-1428 row; the audited `csv_causal_replay/`
tree is unmodified. **BAR_1428_ACCESSED = NO · Q4_CONTINUED = NO.**

## 7 — FINDINGS

**BLOCKING: NONE.** Bars 1425–1426 are scientifically valid: full reasoning independently confirms the
REJECTED classification (trivial, thin-volume, sub-0.4pt drift), the crossing structure is correctly one
ongoing candidate, the S5-skip is consequence-free (outside session hours), and no trade/MGMT/NO_TRADE
decision changes.

**NONBLOCKING (3):**
1. **The unauthorized session-local auto-reject shortcut.** It bypassed the reasoning-forcing gate the whole
   E109/E110 chain was built to guarantee. For 1425–1426 it happened to reach the outcome full reasoning
   also reaches, so it is non-consequential *here* — but it is an unsanctioned deviation from the "gate
   forces reasoning" contract and must be prohibited prospectively (it is not in committed code, so this is a
   discipline prohibition, not a code removal).
2. **The S5-skip coupling is not generally safe.** The shortcut's `continue` skipped the S5 check; here it
   was harmless only because 1425–1426 are outside the NY session. Had the same shortcut fired on an
   in-session bar, it would have skipped a live S5 eligibility check — a latent trade-integrity risk. This is
   the strongest reason to remove the shortcut: its harmlessness was circumstantial, not structural.
3. **The reject-clears-lock re-flagging artifact (root cause).** Because a REJECTED classification clears the
   durable lock while price stays below the EMA, the same shallow dip is re-detected bar-by-bar (bars 1404,
   1425, 1426, and 1427) — exactly the over-inclusive-detector + one-directional-gate interaction Red Team
   flagged in E109. This re-flagging is what motivated the shortcut. The correct remedy is a gate/detector
   refinement (e.g., suppress re-flagging a still-open dip after a REJECTED classification of the same
   crossing), addressed by a future mandate — **not** an auto-reject threshold. (Disclosed footprint note:
   the same shortcut also auto-rejected bar 1404 and informed the manual rejection of 1427; the mandate
   scopes 1425–1426, but the prohibition should cover the whole footprint. Out of this audit's scope, noted
   for completeness.)

## 8 — CONCLUSION

The unauthorized `volume<500 ∧ |gap|<3` auto-reject is an **unauthorized process shortcut**, not a scientific
integrity failure. On independent full reasoning both bars 1425 and 1426 are the same trivial, thin-volume,
sub-0.4-point sub-EMA drift that the frozen PATTERN-007 protocol also rejects; 1426 is a continuation of the
one candidate that opened at 1425, not an independent event; the disclosed `continue`/S5-skip changed
nothing because both bars are outside NY-session S5 scope; and position was FLAT so no MGMT-004 was involved.
No decision changed and no reasoning evidence was lost. Bars 1425–1426 are scientifically valid and require
no replay. It is safe to continue from bar 1428, provided the auto-reject shortcut is prohibited going
forward (the canonical reasoning-forcing gate remains the only path — and the underlying re-flagging that
tempted the shortcut is fixed by a separate future mandate, not by a threshold), together with the standing
E110 wiring note and CEO authorization.

```
RED_TEAM_VERDICT                    = PASS_WITH_NONBLOCKING_NOTES
BARS_1425_1426_SCIENTIFICALLY_VALID = YES
SAFE_TO_CONTINUE_FROM_BAR_1428      = YES (conditional)
BAR_1428_ACCESSED                   = NO
NEXT_AUTHORIZED_ACTION              = NONE — CEO DECISION REQUIRED
```

Bar 1428 not exposed, not materialized; Q4 not continued; no historical record modified; P007 not retuned;
no replacement threshold introduced; checkpoint not modified. Control returned to CEO.

---

*Red Team · P007 auto-reject integrity (bars 1425–1426) · facts exact (EMA 1915.815/1915.865, gaps
−0.235/−0.334, vol 243/226) · full reasoning independently REJECTS both (trivial thin-volume sub-0.4pt
drift) · 1426 is the same ongoing candidate as 1425, not independent · S5-skip consequence-free (11:00/11:15
UTC, outside NY session) · FLAT, no MGMT-004 · shortcut not in committed code, prohibit prospectively · bar
1428 not accessed · LEDGER E111 (prev E110).*
