"""`AI_TRADER_SHADOW_COST_MODEL_v1` — CEO decision, 2026-08-16 (ratified), amended 2026-08-16 (RATIFIED
status + real wiring): "Costurile pe care le monitorizezi si le calculezi in shadow devin sursa canonica
pentru TOATE strategiile proiectului." This module IS that publication: a single, importable source of
truth so this division, the evaluator, and Alpha all read the exact same numbers, from the exact same
place, with the exact same provenance — never three independent copies that can silently drift (see
`BRIDGE_PY_COST_LITERAL_MISMATCH` below for a real one this canonicalization effort caught and
`new_brain_bridge/bridge.py` now closes by importing this module directly, exclusively).

**Every number below is copied, verbatim, from git-committed sources — never invented, never
recalibrated here.** The spread distribution and BASE/STRESS standard are copied from
`AI_TRADER_MANDATE8_STEP1_COST_CALIBRATION_REPORT.md` (committed `351f789`, git blob
`0e8207a4e81349fae11104db524206910b7b0816` — this module's own tests re-verify that blob hash against the
live file before trusting it, so a future edit to that report can never silently desync from what this
module claims to publish). Re-pulling `spread_collection`'s live SQLite state store to produce FRESH
percentiles was deliberately NOT done — the CEO's own instruction is to publish what is already
git-committed, not to recalibrate against runtime state that was never ratified.

**RATIFIED, 2026-08-16 (second CEO decision)**: `calibration_status` transitions `PROVISIONAL` ->
`RATIFIED` — the exact numeric VALUES are unchanged (CEO: "Pastreaza valorile exacte, dar schimba
semantic"), but `calibration_status` now enters both `content_hash()` and `configuration_fingerprint()`,
so this publication's hash differs from the original v1 PROVISIONAL publication's hash — any result
computed against the OLD hash is `NON_COMPARABLE` with anything computed after this change, exactly as
instructed ("Rezultatele produse cu configurația veche devin automat NON_COMPARABLE prin schimbarea
hash-ului"). `BASE_RATIFIED`'s `0.00`/`0.00` slippage components are the OFFICIAL, RATIFIED value for the
BASE operational scenario — NOT a claim that real fills were measured at zero cost. Zero real fills exist
to date; `real_measured_slippage()` still fails closed unconditionally.

**Fail-closed, not zero-as-fallback** (CEO's own explicit instruction: "Zero NU e fallback"):
`real_measured_slippage()` raises `CostModelUnavailableError` unconditionally today — zero real fills
exist across any live policy (confirmed in the Mandate 8 report, unchanged since: `pdh_pdl_demo/
slippage.py`'s `SlippageLog` is wired into both orchestrators but has never recorded an entry). Treating
that absence as `0.0` would misrepresent "never measured" as "measured, and free" — exactly the failure
mode this module exists to rule out. `full_spread_price`/`entry_slippage_price`/`exit_slippage_price`
likewise never silently substitute a default on an unknown tier or an incompatible caller-supplied
fingerprint — both raise `CostModelUnavailableError`, the ONLY path `new_brain_bridge/bridge.py` accepts
as a signal to degrade that decision cycle to `NO_TRADE`.

**Disclosed discrepancy, found by the first canonicalization exercise, NOW CLOSED**: `bridge.py`'s
`DecisionRequest` construction previously hardcoded `full_spread_price=0.10, entry_slippage_price=0.05,
exit_slippage_price=0.05` (introduced commit `bd59266`, 2026-08-14) — a THIRD, never-ratified number that
matched neither `BASE_RATIFIED` nor `STRESS_RATIFIED`. `bridge.py` now imports this module's own
`full_spread_price()`/`entry_slippage_price()`/`exit_slippage_price()` functions exclusively — no local
literal, no alternate calculator, no manual copy. `BRIDGE_PY_COST_LITERAL_MISMATCH` and
`_BRIDGE_PY_COST_LITERAL` below are kept as a historical record (and a regression guard — a future test
can assert `bridge.py`'s source no longer contains those literals) but are no longer live in
`bridge.py`'s own code path.

**Provenance window, extracted from the ratifying report's own section 1 — nothing invented.** The report
states 4 DISTINCT CALENDAR DAYS with real observations: `2026-08-04`, `2026-08-10`, `2026-08-11`,
`2026-08-12` — explicitly NON-CONTIGUOUS (`2026-08-05` through `2026-08-09` had ZERO observations, the
disclosed operator pause). The report gives no finer-grained (sub-day) timestamps for the overall
monitoring window (only for the specific 2026-08-11 duplicate-bar incident sub-window, which is a
different, narrower fact) — so `COST_PROVENANCE_WINDOW` is deliberately expressed as the exact day-set,
not a smooth start/end range, and `is_within_provenance_window()` checks EXACT calendar-day membership,
not a continuous span. Every real live decision made on any date other than those 4 exact days —
including every decision made today, 2026-08-16, and every date after — is OUTSIDE the provenance window
by this exact, honest definition; callers must surface `COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW` when
that is true, never treat it as silently fine."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone

SHADOW_COST_MODEL_VERSION = "v1"
CALIBRATION_STATUS = "RATIFIED"
"""CEO decision, 2026-08-16 (second directive): was `PROVISIONAL`. Enters both `content_hash()` and
`configuration_fingerprint()` -- the mechanism the CEO's own instruction relies on to make prior results
`NON_COMPARABLE` automatically, without a top-level version bump."""

SOURCE_REPORT_PATH = "AI_TRADER_MANDATE8_STEP1_COST_CALIBRATION_REPORT.md"
SOURCE_REPORT_COMMIT = "351f789"
SOURCE_REPORT_BLOB_SHA1 = "0e8207a4e81349fae11104db524206910b7b0816"
"""`git rev-parse 351f789:AI_TRADER_MANDATE8_STEP1_COST_CALIBRATION_REPORT.md` — the exact content
identity of the ratifying report this module publishes from. `tests/test_shadow_cost_model.py`
independently re-verifies this against the live working-tree file (`git hash-object`) before any test
trusts the numbers below, so an un-noticed edit to the report can never silently desync this module."""

SLIPPAGE_MECHANISM_SOURCE_PATH = "ai_trader/pdh_pdl_demo/slippage.py"
SLIPPAGE_MECHANISM_COMMIT = "351f789"
SLIPPAGE_MECHANISM_BLOB_SHA1 = "4f59f114da73054c0a9dc246fc5d4c153cee057f"

SPREAD_DATA_SOURCE = "spread_collection.observations (SqliteStateStore append_log, all 5 live-process state stores; shared XAUUSD M15 feed's own spread_collection_state/xauusd_m15.db is authoritative)"
SLIPPAGE_DATA_SOURCE = "pdh_pdl_demo.slippage.SlippageLog (wired, zero entries recorded — no real fill has occurred yet)"

BROKER_SERVER = "FusionMarkets-Demo"
BROKER_COMPANY = "Fusion Markets Pty Ltd"
SYMBOL = "XAUUSD"
UNITS = "instrument quote-price units (XAUUSD bid/ask price scale — e.g. spread=0.05 means ask-bid=0.05 in quote price, NOT pips or basis points)"
ENTRY_ORDER_TYPE = "MARKET (unset price field — see request_builder.py; realized fill price read from the order acknowledgement)"
EXIT_ORDER_TYPE = "broker-side SL/TP bracket (BROKER_SLTP) — no discrete closing order is submitted by this codebase today"

MONITORED_CALENDAR_DAYS = ("2026-08-04", "2026-08-10", "2026-08-11", "2026-08-12")
"""4 distinct calendar days, per the ratifying report's own section 1 — 2026-08-04 isolated before the
known operator pause, 08-10 through 08-12 the continuous run that followed."""

COST_PROVENANCE_WINDOW = {
    "observed_calendar_days_utc": list(MONITORED_CALENDAR_DAYS),
    "first_day": MONITORED_CALENDAR_DAYS[0],
    "last_day": MONITORED_CALENDAR_DAYS[-1],
    "contiguous": False,
    "note": "2026-08-05 through 2026-08-09 had ZERO observations (disclosed operator pause, see source "
            "report). Membership is exact-day-set, NOT a continuous [first_day, last_day] range.",
}
"""Enters `content_hash()`/`configuration_fingerprint()` per the CEO's own explicit instruction
("cost_provenance_window intra in config_hash")."""


class CostModelUnavailableError(Exception):
    """Raised whenever a required cost component has no real, git-ratified value to return — fail-closed,
    per the CEO's own explicit instruction. Never caught and silently replaced with `0.0` by this module;
    a caller that wants `NO_TRADE`-on-cost-unavailable behavior gets that from this exception propagating,
    the same fail-closed convention `BarFeedError`/`BrokerOrderSubmissionDisabledError` already use."""


@dataclass(frozen=True, slots=True, kw_only=True)
class CostComponents:
    """One tier of the cost standard — `full_spread_price` is the FULL bid-ask spread (CEO's own already-
    fixed decision, cited in `bridge.py`'s own docstring history: never halved), `entry_slippage_price`/
    `exit_slippage_price` are per-leg, both non-negative price-unit costs `ve_brain.DecisionRequest`
    consumes directly under those exact field names."""

    full_spread_price: float
    entry_slippage_price: float
    exit_slippage_price: float

    @property
    def round_trip_total(self) -> float:
        return self.full_spread_price + self.entry_slippage_price + self.exit_slippage_price


BASE_RATIFIED = CostComponents(full_spread_price=0.05, entry_slippage_price=0.00, exit_slippage_price=0.00)
STRESS_RATIFIED = CostComponents(full_spread_price=0.08, entry_slippage_price=0.08, exit_slippage_price=0.08)
"""Values copied VERBATIM from the ratifying report's own section 3 table (formerly named
`BASE_PROVISIONAL`/`STRESS_PROVISIONAL` — same numbers, `calibration_status` now `RATIFIED` per the CEO's
second decision, 2026-08-16). `BASE_RATIFIED`'s `0.00`/`0.00` slippage is the RATIFIED value for the BASE
operational scenario, explicitly NOT a claim that a real fill was measured at zero cost -- see module
docstring. `STRESS_RATIFIED.round_trip_total == 0.24` (0.08 spread + 0.08 + 0.08 slippage), matching the
report's own stated total exactly."""

_BRIDGE_PY_COST_LITERAL = CostComponents(full_spread_price=0.10, entry_slippage_price=0.05, exit_slippage_price=0.05)
"""What `new_brain_bridge/bridge.py`'s `DecisionRequest` construction used to hardcode (commit `bd59266`,
2026-08-14 through the fix committed 2026-08-16) — kept here ONLY as a historical/regression-guard
reference; `bridge.py` no longer contains this literal anywhere in its own source."""

BRIDGE_PY_COST_LITERAL_MISMATCH = _BRIDGE_PY_COST_LITERAL != BASE_RATIFIED
"""`True` — the historical literal never matched the ratified standard. Retained as a standing fact for
audit trail; `bridge.py` itself no longer uses `_BRIDGE_PY_COST_LITERAL` at all (see
`test_bridge_py_contains_no_hardcoded_cost_literals` in `new_brain_bridge/tests/test_bridge.py`)."""


# Real, measured spread distribution — CLEAN (deduplicated), copied verbatim from the ratifying report's
# own section 1 table. Units: instrument quote-price (see UNITS above). n=175 real observations across 4
# distinct calendar days.
SPREAD_DISTRIBUTION_CLEAN = {
    "n": 175, "mean": 0.0809, "median_p50": 0.0700, "p10": 0.0500, "p25": 0.0500,
    "p75": 0.0900, "p90": 0.1240, "p95": 0.2000, "p99": 0.2000, "min": 0.0500, "max": 0.2000,
}
SPREAD_DISTRIBUTION_BY_SESSION = {
    "asia": {"n": 38, "median_p50": 0.0500, "p90": 0.1000, "mean": 0.0647},
    "london": {"n": 33, "median_p50": 0.0700, "p90": 0.1200, "mean": 0.0721},
    "ny": {"n": 83, "median_p50": 0.0800, "p90": 0.1200, "mean": 0.0835},
    "late": {"n": 21, "median_p50": 0.0900, "p90": 0.2000, "mean": 0.1133},
}
SPREAD_DISPERSION_IQR = round(SPREAD_DISTRIBUTION_CLEAN["p75"] - SPREAD_DISTRIBUTION_CLEAN["p25"], 4)
"""Interquartile range, DERIVED from the two already-published, already-ratified percentiles above (p75 -
p25) — not a new measurement, not a recomputation from raw data (the raw 175 observations were never
committed to git, only this aggregate table was). No standard deviation is published: the ratifying
report never computed one, and one cannot be honestly derived from percentiles alone without assuming a
distribution shape this module has no basis to assume. `standard_error` is therefore reported as
unavailable in the manifest, not approximated."""


def full_spread_price(*, tier: str = "BASE") -> float:
    """`tier` is `"BASE"` or `"STRESS"` — any other value fails closed via `CostModelUnavailableError`,
    never silently defaults to BASE."""
    return _components_for_tier(tier).full_spread_price


def entry_slippage_price(*, tier: str = "BASE") -> float:
    return _components_for_tier(tier).entry_slippage_price


def exit_slippage_price(*, tier: str = "BASE") -> float:
    return _components_for_tier(tier).exit_slippage_price


def round_trip_cost(*, tier: str = "BASE") -> float:
    return _components_for_tier(tier).round_trip_total


def resolve_cost_components(*, tier: str = "BASE") -> CostComponents:
    """The single call `new_brain_bridge/bridge.py` uses to resolve all three cost fields at once --
    raises `CostModelUnavailableError` (never returns a partial or zeroed result) on any unknown tier."""
    return _components_for_tier(tier)


def _components_for_tier(tier: str) -> CostComponents:
    if tier == "BASE":
        return BASE_RATIFIED
    if tier == "STRESS":
        return STRESS_RATIFIED
    raise CostModelUnavailableError(
        f"COST_MODEL_UNAVAILABLE: unknown tier {tier!r} — only 'BASE' or 'STRESS' are published"
    )


def real_measured_slippage(*, leg: str) -> float:
    """`leg` is `"entry"` or `"exit"`. Fails closed UNCONDITIONALLY today — zero real
    `SlippageObservation` entries exist in any live process's `SlippageLog` (see module docstring). This
    function exists so a future consumer has the correct call shape ready; it must keep raising until a
    real fill genuinely produces at least one observation and a NEW, separately-versioned publication
    (never a silent edit to `v1`) incorporates it."""
    if leg not in ("entry", "exit"):
        raise CostModelUnavailableError(f"COST_MODEL_UNAVAILABLE: unknown leg {leg!r}")
    raise CostModelUnavailableError(
        "COST_MODEL_UNAVAILABLE: zero real slippage observations exist yet — "
        "pdh_pdl_demo/slippage.py's SlippageLog is wired into every live orchestrator but has never "
        "recorded an entry (zero policy fills to date). Never fabricated as 0.0."
    )


def is_within_provenance_window(as_of_epoch_seconds: int) -> bool:
    """`True` only if `as_of_epoch_seconds`'s own UTC calendar date is EXACTLY one of
    `MONITORED_CALENDAR_DAYS` -- membership in the discrete day-set, never a continuous range (the window
    is genuinely non-contiguous; see module docstring). A caller (`bridge.py`) that resolves cost
    components for a date outside this window must surface
    `COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW` -- this function only answers the membership question,
    it never blocks or degrades anything itself."""
    day = datetime.fromtimestamp(as_of_epoch_seconds, tz=timezone.utc).strftime("%Y-%m-%d")
    return day in MONITORED_CALENDAR_DAYS


def content_hash() -> str:
    """A single, reproducible sha256 over every published numeric/status field this module exposes — the
    'hash de continut' the CEO's directive requires. Recomputed from the module's OWN in-memory constants
    (not re-read from disk), so it is stable across processes and only ever changes if this module's own
    published values (INCLUDING `calibration_status`/`cost_provenance_window`, per the CEO's own second
    decision) change."""
    payload = {
        "version": SHADOW_COST_MODEL_VERSION,
        "calibration_status": CALIBRATION_STATUS,
        "base_ratified": {
            "full_spread_price": BASE_RATIFIED.full_spread_price,
            "entry_slippage_price": BASE_RATIFIED.entry_slippage_price,
            "exit_slippage_price": BASE_RATIFIED.exit_slippage_price,
        },
        "stress_ratified": {
            "full_spread_price": STRESS_RATIFIED.full_spread_price,
            "entry_slippage_price": STRESS_RATIFIED.entry_slippage_price,
            "exit_slippage_price": STRESS_RATIFIED.exit_slippage_price,
        },
        "spread_distribution_clean": SPREAD_DISTRIBUTION_CLEAN,
        "spread_distribution_by_session": SPREAD_DISTRIBUTION_BY_SESSION,
        "cost_provenance_window": COST_PROVENANCE_WINDOW,
        "source_report_blob_sha1": SOURCE_REPORT_BLOB_SHA1,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def configuration_fingerprint() -> str:
    """The identity fields governing THIS publication — commit + version + calibration_status +
    provenance window + source blobs, distinct from `content_hash()` (numeric payload only). Truncated to
    16 hex chars, matching this codebase's own established `_fp()` convention (`new_brain_bridge/
    bridge.py`). Changing `CALIBRATION_STATUS` (PROVISIONAL -> RATIFIED) changes this value -- the exact
    mechanism the CEO's instruction relies on to make old results `NON_COMPARABLE` automatically."""
    payload = (
        f"{SHADOW_COST_MODEL_VERSION}|{CALIBRATION_STATUS}|{SOURCE_REPORT_COMMIT}|{SOURCE_REPORT_BLOB_SHA1}|"
        f"{SLIPPAGE_MECHANISM_BLOB_SHA1}|{json.dumps(COST_PROVENANCE_WINDOW, sort_keys=True)}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def data_identity() -> dict[str, object]:
    """Mirrors `ve_tower.DataIdentity`'s own shape (symbol/source/count/as-of), for the exact same reason:
    a durable, inspectable description of WHICH data this publication's numbers came from."""
    return {
        "symbol": SYMBOL,
        "source_identity": SPREAD_DATA_SOURCE,
        "monitored_calendar_days": list(MONITORED_CALENDAR_DAYS),
        "n_clean_observations": SPREAD_DISTRIBUTION_CLEAN["n"],
        "source_report_commit": SOURCE_REPORT_COMMIT,
        "source_report_blob_sha1": SOURCE_REPORT_BLOB_SHA1,
    }


def manifest() -> dict[str, object]:
    """The complete, single-object publication — every field the CEO's directive requires, in one place.
    This is what `AI_TRADER_SHADOW_COST_MODEL_v1.json` on disk is a frozen snapshot of; this function is
    the LIVE source of truth other code should import and call, not the JSON file (which exists for
    Red Team's own external inspection, per the CEO's own instruction)."""
    return {
        "shadow_cost_model_version": SHADOW_COST_MODEL_VERSION,
        "calibration_status": CALIBRATION_STATUS,
        "broker_server": BROKER_SERVER,
        "broker_company": BROKER_COMPANY,
        "symbol": SYMBOL,
        "units": UNITS,
        "entry_order_type": ENTRY_ORDER_TYPE,
        "exit_order_type": EXIT_ORDER_TYPE,
        "monitored_calendar_days": list(MONITORED_CALENDAR_DAYS),
        "cost_provenance_window": COST_PROVENANCE_WINDOW,
        "base_ratified": {
            "full_spread_price": BASE_RATIFIED.full_spread_price,
            "entry_slippage_price": BASE_RATIFIED.entry_slippage_price,
            "exit_slippage_price": BASE_RATIFIED.exit_slippage_price,
            "round_trip_total": BASE_RATIFIED.round_trip_total,
            "note": "RATIFIED official value for the BASE operational scenario -- zero slippage "
                    "components are NOT a claim of a real fill measured at zero cost (zero real fills "
                    "exist); real_measured_slippage() remains COST_MODEL_UNAVAILABLE unconditionally.",
        },
        "stress_ratified": {
            "full_spread_price": STRESS_RATIFIED.full_spread_price,
            "entry_slippage_price": STRESS_RATIFIED.entry_slippage_price,
            "exit_slippage_price": STRESS_RATIFIED.exit_slippage_price,
            "round_trip_total": STRESS_RATIFIED.round_trip_total,
            "note": "RATIFIED official value for the STRESS scenario.",
        },
        "formula": {
            "base_once_real_slippage_exists": "BASE = median(spread) + median(slippage), per execution, both legs",
            "stress_once_real_slippage_exists": "STRESS = upper percentiles -- threshold set by Statistician + Red Team, not this division",
            "currently_in_effect": "BASE_RATIFIED/STRESS_RATIFIED (above) -- explicitly NOT empirical measurement of real fills, unchanged until real slippage data exists and a new ratified calibration supersedes them",
        },
        "spread_distribution_clean": SPREAD_DISTRIBUTION_CLEAN,
        "spread_distribution_by_session": SPREAD_DISTRIBUTION_BY_SESSION,
        "spread_dispersion_iqr": SPREAD_DISPERSION_IQR,
        "standard_error": "UNAVAILABLE -- not computed in the ratifying source; raw observations were never committed to git, only the aggregate percentile table was, and a stddev/SE cannot be honestly derived from percentiles alone without assuming a distribution shape",
        "slippage_distribution": "COST_MODEL_UNAVAILABLE -- zero real observations",
        "data_source": {"spread": SPREAD_DATA_SOURCE, "slippage": SLIPPAGE_DATA_SOURCE},
        "source_report_path": SOURCE_REPORT_PATH,
        "source_report_commit": SOURCE_REPORT_COMMIT,
        "source_report_blob_sha1": SOURCE_REPORT_BLOB_SHA1,
        "slippage_mechanism_path": SLIPPAGE_MECHANISM_SOURCE_PATH,
        "slippage_mechanism_commit": SLIPPAGE_MECHANISM_COMMIT,
        "slippage_mechanism_blob_sha1": SLIPPAGE_MECHANISM_BLOB_SHA1,
        "data_identity": data_identity(),
        "configuration_fingerprint": configuration_fingerprint(),
        "content_hash": content_hash(),
        "bridge_py_cost_literal_mismatch_historical": BRIDGE_PY_COST_LITERAL_MISMATCH,
        "bridge_py_cost_literal_historical": {
            "full_spread_price": _BRIDGE_PY_COST_LITERAL.full_spread_price,
            "entry_slippage_price": _BRIDGE_PY_COST_LITERAL.entry_slippage_price,
            "exit_slippage_price": _BRIDGE_PY_COST_LITERAL.exit_slippage_price,
            "note": "HISTORICAL ONLY -- new_brain_bridge/bridge.py commit bd59266 through 2026-08-16 used "
                    "this literal; bridge.py now imports this module exclusively and no longer contains it.",
        },
    }
