# Strategy Manager v1 — Strategy Lifecycle State Machine (design)

The Strategy Manager assigns every registered strategy a single **operational lifecycle state**. This is the
Manager's runtime classification — it **reflects** the frozen Strategy Interface fields (`lifecycle.status`,
`lifecycle.maturity`, `lifecycle.current_health`) and layers operational states on top; it **never mutates** the
contract. The Manager never self-promotes a strategy's maturity: maturity advances only when a NEW contract
version (produced by the research-gated Library) is reloaded. Design only — no code.

---

## 1. The nine states

| state | meaning | activatable? | source |
|---|---|---|---|
| `NOT_IMPLEMENTED` | stub only — no engine code / no results (e.g. S32–S37) | no | contract `status=NOT_IMPLEMENTED` |
| `INVALID` | failed schema/required-field validation, or contract `status=INVALID`, or `current_health=INVALID` | no | validation / contract |
| `EXPERIMENTAL` | loaded + valid + compatible, but admitted to **sandbox/paper only** — below live-exploratory admission (Manager operational bucket; the post-load resting state of a valid contract) | sandbox only | Manager policy |
| `EXPLORATORY` | active at the exploratory tier (research-segment evidence, no confirmed alpha) | yes (research/limited budget) | contract `maturity=EXPLORATORY` + admitted |
| `CANDIDATE` | active; a stronger exploratory candidate (contract advanced to CANDIDATE) | yes (limited) | contract `maturity=CANDIDATE` |
| `VALIDATED` | active; matched-null + walk-forward passed (per interface §4 maturity gate) | yes | contract `maturity=VALIDATED` |
| `PROMOTED` | active; additionally global-FDR passed + holdout-confirmed | yes (full) | contract `maturity=PROMOTED` |
| `DISABLED` | valid but operationally turned off (operator / kill-switch / Learning-Engine request) | no (until re-enabled) | operational overlay / `status=DISABLED` |
| `RETIRED` | permanently withdrawn within this interface MAJOR | no (terminal) | contract `maturity=RETIRED` / `status=DEPRECATED→RETIRED` / operator |

**Admission policy (Manager, configurable):** only `EXPLORATORY`+ states are admitted to the *live* active set;
`EXPERIMENTAL` runs in sandbox/paper only; `NOT_IMPLEMENTED`, `INVALID`, `DISABLED`, `RETIRED` are never in the
active set. Given today's Library, no strategy exceeds `EXPLORATORY`/`CANDIDATE` (the validation ladder is
`NOT_RUN`), so in practice the live active set is a policy-limited subset of exploratory strategies.

---

## 2. State-machine diagram

```
                         load / reload
                              │
             ┌────────────────┼───────────────────────────────┐
             ▼                ▼                                ▼
      (contract status)  (validation fail)             (status NOT_IMPLEMENTED)
        IMPLEMENTED           │                                │
             │                ▼                                ▼
             │            ┌────────┐   corrected reload   ┌───────────────┐  implemented in a
             │            │ INVALID│◀────────────────────▶│ NOT_IMPLEMENTED│  later Library release
             │            └────────┘                      └───────────────┘         │
             ▼                                                     │ (reload)        │
        ┌──────────────┐        admit (policy)                     └────────────────▶│
        │ EXPERIMENTAL │──────────────────────────────┐                              │
        └──────────────┘                              ▼                              ▼
             ▲   │ demote/withdraw admit         ┌─────────────┐   reload(maturity↑ + gates)
             │   └──────────────────────────────▶│ EXPLORATORY │──────────────┐
             │                                    └─────────────┘              ▼
             │                                          ▲               ┌───────────┐  reload
             │                                          │ reload        │ CANDIDATE │────────┐
   reload(valid)                                        │(maturity↓)    └───────────┘        ▼
             │                                          │                     ▲        ┌───────────┐ reload
             │                                          │                     │ reload │ VALIDATED │──────┐
             │                                          │                     │        └───────────┘      ▼
             │                                          │                     │              ▲       ┌──────────┐
             │                                          │                     │              │ reload│ PROMOTED │
             │                                          │                     │              │       └──────────┘
             │                                          │                     │              │             │
             │        disable (operator/kill-switch)    │                     │              │             │
   any active state  ───────────────────────────────▶  DISABLED  ────re-enable┴──────────────┴─────────────┘
             │                                             │
             └──────────────────────────  retire  ────────┴────────────▶  RETIRED  (terminal within this MAJOR)
```

- **Upward maturity transitions** (`EXPLORATORY→CANDIDATE→VALIDATED→PROMOTED`) happen ONLY via **reload of a new,
  research-gated contract version** whose `maturity` advanced AND whose validation-ladder gates satisfy the
  interface rule (VALIDATED needs matched-null PASS + walk-forward PASS; PROMOTED additionally global-FDR PASS +
  holdout-confirmed). The Manager verifies the gate on load and refuses to reflect a maturity the ladder does not
  support (→ stays at the highest supportable state, flagged).
- **Downward transitions** happen on reload if a new contract lowers maturity, or on a failed re-validation
  (→ `INVALID`/`INCOMPATIBLE`).
- **DISABLED** is an operational overlay reachable from any active state and returns to the prior state on
  re-enable.
- **RETIRED** is terminal within an interface MAJOR (never hard-deleted — references may exist).

---

## 3. Transition table

| # | from | to | trigger | guard | effect |
|---|---|---|---|---|---|
| T1 | — | INVALID | load/reload | schema or required-field validation fails, or contract INVALID | quarantine; error record; not activatable |
| T2 | — | NOT_IMPLEMENTED | load | contract `status=NOT_IMPLEMENTED` | register as stub; never activate |
| T3 | — | EXPERIMENTAL | load/reload | valid + compatible contract (`status=IMPLEMENTED`) | initial operational resting state; sandbox-eligible |
| T4 | EXPERIMENTAL | EXPLORATORY | admit | activation policy admits AND `maturity≥EXPLORATORY` | join live active set (exploratory tier); triggers Context re-aggregation |
| T5 | EXPLORATORY | EXPERIMENTAL | demote/withdraw-admit | operator or policy withdraws live admission | leave live active set; back to sandbox |
| T6 | EXPLORATORY | CANDIDATE | reload | new contract `maturity=CANDIDATE` | reflect higher tier |
| T7 | CANDIDATE | VALIDATED | reload | new contract `maturity=VALIDATED` AND matched-null PASS ∧ walk-forward PASS | reflect VALIDATED (gate-checked) |
| T8 | VALIDATED | PROMOTED | reload | new contract `maturity=PROMOTED` AND global-FDR PASS ∧ holdout-confirmed | reflect PROMOTED (gate-checked) |
| T9 | any maturity tier | (lower tier) | reload | new contract lowers `maturity` | reflect the lower tier |
| T10 | any active/experimental | DISABLED | disable | operator / kill-switch / Learning-Engine request | remove from active set; Context re-aggregation |
| T11 | DISABLED | prior state | enable | operator re-enables AND still valid/compatible | restore prior state; Context re-aggregation |
| T12 | any | RETIRED | retire | contract retired (Library) or operator retirement | terminal within MAJOR; removed from active set |
| T13 | INVALID | EXPERIMENTAL | reload | corrected contract now validates + compatible | recover; re-admittable |
| T14 | NOT_IMPLEMENTED | EXPERIMENTAL | reload | later Library release implements it (valid contract) | recover |
| T15 | any | INCOMPATIBLE(→INVALID health) | reload | interface/runtime/MarketContext incompatibility | quarantine; not activatable (health `INCOMPATIBLE`) |

Every transition that changes the active set (T4, T5, T10, T11, T12) triggers a **Context Aggregator recompute**
and a fresh `register_requirements()` to the Market Scanner.

---

## 4. Mapping to the frozen Strategy Interface (no contract change)

| Manager lifecycle | Interface `lifecycle.status` | Interface `lifecycle.maturity` | Interface `current_health` |
|---|---|---|---|
| NOT_IMPLEMENTED | NOT_IMPLEMENTED | (EXPLORATORY, unused) | — |
| INVALID | INVALID (or valid-but-failed-validation) | any | INVALID |
| EXPERIMENTAL | IMPLEMENTED | EXPLORATORY/CANDIDATE | OK/UNKNOWN |
| EXPLORATORY | IMPLEMENTED | EXPLORATORY | OK |
| CANDIDATE | IMPLEMENTED | CANDIDATE | OK |
| VALIDATED | IMPLEMENTED | VALIDATED | OK |
| PROMOTED | IMPLEMENTED | PROMOTED | OK |
| DISABLED | DISABLED (or overlay) | (unchanged) | DISABLED |
| RETIRED | DEPRECATED→retired | RETIRED | — |

The Manager's lifecycle is a **derived, operational** view. `EXPERIMENTAL`, admission, and `DISABLED` are Manager
operational concepts (no contract mutation); `EXPLORATORY..PROMOTED`, `NOT_IMPLEMENTED`, `INVALID`, `RETIRED`
mirror contract fields. Where the contract and the ladder disagree (e.g. a contract claims VALIDATED but
`walk_forward_status=NOT_RUN`), the guard on T7/T8 fails and the Manager holds the strategy at the highest state
the ladder actually supports, raising a health warning — the interface's honesty rule enforced at runtime.
