# Discovery Candidates

Alpha -> Red Team handoff package. Each subfolder `DC-XXXX_<slug>/` holds one Discovery
Candidate: a frozen, immutable observation produced by Alpha's discretionary market-observation
process, submitted for independent review by later, separate divisions.

- `DISCOVERY_CANDIDATE_TEMPLATE.md` -- the official empty template every candidate is authored
  from. Do not add sections beyond what it defines.
- `DISCOVERY_CANDIDATE_INDEX.md` -- master, authoritative registry of every Discovery Candidate
  ID ever assigned, and each candidate's *current* lifecycle status.
- `HANDOFF_LOG.md` -- append-only audit trail of every freeze / new-version / addendum event.

## What a Discovery Candidate is not

A Discovery Candidate is **not** an Edge, is **not** validated, and is **not** a trade idea. It
records only what Alpha directly observed, why it seemed noteworthy, and why it may deserve
further, independent investigation. Hypotheses, red-team critique, information-gap analysis, and
required-observable specification are the responsibility of later, independent divisions -- not
of the Discovery Candidate document itself.

## Immutability

Once a candidate version is frozen and its freeze event is recorded in `HANDOFF_LOG.md`, that
version file is never edited. Corrections or new evidence are filed as a separately dated
addendum in the same folder, or as a new version file -- the prior version always remains,
untouched, alongside it. See `DISCOVERY_CANDIDATE_TEMPLATE.md` for the exact mechanics.

## Two-flow separation

This directory belongs to Flow A (Alpha Discovery Laboratory) exclusively. It contains no
references to, and is never read by, Flow B (`ai_trader/`).
