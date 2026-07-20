# Edge Research Protocol

**Program**: 40-Edge Alpha Discovery Program. **Applies to**: every edge in
`EDGE_DISCOVERY_REGISTRY_v1.md`, without exception. **Status**: protocol definition only — no edge has
been run through any stage of this protocol yet.

## 0. Purpose and philosophy

The 40 entries in the registry are raw research hypotheses, not strategies. This protocol exists so
that all 40 are studied under one identical, disciplined procedure — so results are comparable across
edges and so no edge is quietly implemented, adjusted, or declared "true" without having earned it
through the same gates as every other edge.

Two rules govern everything that follows, restated here because they are the ones most likely to be
violated by accident under normal research pressure:

1. **The goal is discovery, not confirmation.** An edge's initial description (however it is worded in
   the registry, however confidently the CEO or anyone else states it) is a starting hypothesis, not a
   fact. If the CEO says "it only works on Tuesday," the correct response is to test whether that is
   true — not to encode it as a filter and move on. The research may discover the real condition is
   different (only Tuesday *and* Wednesday; only after the Asia range; only in low volatility; only
   without news nearby) — or that no real condition exists and the edge should be refuted outright.
2. **An edge's job in this program is to survive falsification, not to be made profitable.** No edge may
   be tuned, filtered, or parameter-searched until it "works." If the raw hypothesis loses money, that
   is a valid, complete, and useful result — not a reason to keep adjusting until it doesn't.

## 1. Mandatory permanent record — kept for every edge, forever

For every edge, from the moment it enters Discovery, the following must exist and must never be
deleted, overwritten, or retroactively rewritten:

- **V0** — the original hypothesis exactly as registered in `EDGE_DISCOVERY_REGISTRY_v1.md`. Frozen at
  registration. Never edited.
- **All observations** — every data point/finding produced during Discovery, whether it supports,
  contradicts, or is neutral to the hypothesis. Negative and null observations are recorded with the
  same weight as positive ones and are never removed once recorded, at any later stage.
- **All discovered conditions** — every condition found to matter (day, session, volatility regime, news
  proximity, filter, instrument state, etc.), including conditions that *reduce* the edge's apparent
  value, not only ones that improve it.
- **All exceptions** — specific instances where the edge behaved unlike the general pattern, kept as
  data even if they cannot yet be explained.
- **All falsifications** — every test, control comparison, or out-of-sample check that failed to
  confirm the edge, recorded with the same rigor as a successful test. A falsification is not evidence
  to be argued away; it stands as part of the edge's permanent record.
- **All successive versions** — V1, V2, V3, … each one a new, dated, appended entry representing a
  refinement of the hypothesis based on what Discovery found (e.g. V0 "works on Tuesday" → V1 "works
  Tuesday and Wednesday, conditional on low ADR consumption"). A new version is *added*, never a
  replacement that erases what came before.
- **Final Verdict** — the terminal classification once (and only once) the edge completes every stage
  below (§3).

This record lives in a per-edge, append-only research log. This protocol defines the requirement; the
log files themselves are created only when an edge actually enters Discovery (not created by this
protocol document itself — see §6).

## 2. Required study horizon

Every edge must be studied across **approximately 5-6 years of history** before a Final Verdict may be
issued. A shorter window may be used for an early Discovery pass (to cheaply check whether an edge is
even worth the full study), but no Frozen Candidate, Validation, or Walk Forward stage may complete, and
no Final Verdict may be issued, on less than the full ~5-6 year horizon. This is a materially longer
window than any prior study in this project (all prior Strategy/Root-Cause/Atlas work used a single
fixed 1-year window) — the data-acquisition implications of this are addressed as a prerequisite in
`EDGE_DISCOVERY_ROADMAP.md`, not resolved here.

## 3. The six mandatory stages

Every edge must pass through these stages, in this order, with no stage skipped and no stage re-entered
after a Final Verdict is issued (a refuted or inconclusive edge does not get silently re-tried under a
new hypothesis without registering that as a new, separate V-version with its own visible history).

### Stage 1 — V0 (Registration)

The raw hypothesis as written in the registry. No data has been examined yet. Entry condition: the edge
exists in `EDGE_DISCOVERY_REGISTRY_v1.md`. Exit condition: a Discovery study is authorized to begin.

### Stage 2 — Discovery

An open-ended, exploratory pass across the available history, answering — for this specific edge — all
nine questions in §4 below. Discovery is where the hypothesis is allowed to change shape: the edge may
turn out to work under a narrower, wider, or entirely different condition than V0 stated. Every such
finding is recorded as a new version per §1, with the evidence that produced it.

Discovery ends in one of two ways:
- **Promotion to Frozen Candidate** — a specific, precisely-worded version of the hypothesis (which
  condition, which filter, which regime) is written down, based only on the data examined so far.
- **Early Refutation** — Discovery itself can be enough to issue a Final Verdict of REFUTED if the edge
  shows no signal whatsoever across a reasonably thorough look, without needing to proceed through
  Frozen Candidate/Validation/Walk Forward. This is explicitly allowed so that a clearly dead edge is
  not dragged through unnecessary later stages — but the same permanent-record requirements (§1) still
  apply, and REFUTED is still a Final Verdict subject to §3 Stage 6's own rules.

### Stage 3 — Frozen Candidate

The specific hypothesis version selected at the end of Discovery is **frozen**: its exact wording,
conditions, and parameters are written down and locked before any further data is examined. This is the
control against p-hacking — once frozen, the candidate's definition cannot be adjusted based on how
Validation or Walk Forward results come out. If Validation fails, the correct response is a Final
Verdict reflecting that failure (or, if warranted, a **new**, separately-versioned candidate re-entering
Discovery) — never a silent edit to the frozen definition.

### Stage 4 — Validation

The frozen candidate is tested against the remaining, previously-unexamined portion of the ~5-6 year
history (data not used to shape the Discovery-stage findings). This is the first point at which the
frozen, specific version of the hypothesis is checked against data it was not built from.

### Stage 5 — Walk Forward

The frozen candidate is tested in a rolling, sequential fashion across the full history (train-on-past,
test-on-next-unseen-slice, repeated forward through time) — checking not just "does it work once
out-of-sample" but "does it keep working as time moves forward," and whether performance is stable or
decaying/regime-dependent.

### Stage 6 — Final Verdict

One terminal classification, chosen from the taxonomy in §5, written with the same numeric/evidentiary
rigor already established as house convention in this project (see `MECHANISM_REGISTRY.md` for the
existing style this program's verdicts should match). A Final Verdict is not the end of the permanent
record (§1 continues to apply — the full V0→verdict history stays attached to the edge forever) — it is
the end of *this* research cycle for *this* version of the edge.

## 4. The nine questions every edge's Discovery stage must answer

Regardless of category, Discovery must produce an explicit, evidenced answer to each of the following
for that specific edge — "not enough data to tell" is an acceptable answer to any of these, but it must
be stated, not left implicit:

1. Does the edge exist at all (any signal distinguishable from noise)?
2. How often does it occur (frequency)?
3. On which days does it work?
4. On which days does it fail?
5. In which sessions does it work?
6. In which volatility regimes does it work?
7. Are there filters that improve it?
8. Are there conditions that invalidate it?
9. Does it survive out-of-sample testing?

These questions are deliberately open (§0.1) — e.g. question 3/4 do not presume "Tuesday" or any other
specific day is either the answer or excluded; the answer is whatever Discovery finds, including "no day
dependency detected" or "a day dependency exists but disappears once [X] is controlled for."

## 5. Final Verdict taxonomy

A dedicated taxonomy for this program (distinct from, but modeled after, the existing
`MECHANISM_REGISTRY.md` taxonomy already in use in this repository, for consistency of house style):

| Verdict | Meaning |
|---|---|
| **CONFIRMED-ROBUST** | Survives Validation and Walk Forward across the full history with a stable, well-characterized condition set; no material regime-dependence found |
| **CONFIRMED-CONDITIONAL** | Real signal exists, but only under specific, precisely-stated conditions discovered during research (a narrower or different condition than V0) |
| **INCONCLUSIVE** | Data insufficient, contradictory, or too thin to support any of the other verdicts |
| **OVERFIT-IN-SAMPLE-ONLY** | Appeared to work during Discovery/Frozen Candidate definition but failed Validation and/or Walk Forward |
| **REFUTED** | No signal found; the hypothesis, in every version tested, does not distinguish from noise/cost drag |

None of these five verdicts is itself authorization to implement anything. Per the CEO's explicit
instruction opening this program, moving from a Final Verdict to actual implementation is a separate,
future, separately-authorized decision — not an automatic next step of this protocol.

## 6. Where future research artifacts will live (not created by this document)

This protocol only defines the procedure. The per-edge, append-only research logs required by §1 do not
exist yet — none will be created until an edge is actually authorized to enter Discovery. When that
happens, the expected convention (for consistency, not yet enforced by any code or tooling) is one
file per edge, e.g. `edge_research/E0XX_<slug>.md`, containing that edge's full V0→verdict history in
one place. No such file, or `edge_research/` directory, has been created as part of this protocol
document.

## 7. Explicit prohibitions (restated verbatim from the CEO's own program directive)

- No edge may be optimized until it becomes profitable.
- No negative examples/observations may be removed from an edge's record, at any stage.
- The hypothesis may not be modified retroactively after seeing results — refinements are new, appended
  versions (§1), never edits to a prior version.
- No edge may skip a stage in §3.
- A Final Verdict does not authorize implementation, strategy creation, or any code change — that
  requires a separate, future, explicitly-authorized decision.
