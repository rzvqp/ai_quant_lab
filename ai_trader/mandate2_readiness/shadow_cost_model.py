"""`AI_TRADER_SHADOW_COST_MODEL_v1` — CEO decision, 2026-08-16: "Costurile pe care le monitorizezi si le
calculezi in shadow devin sursa canonica pentru TOATE strategiile proiectului." This module IS that
publication: a single, importable source of truth so this division, the evaluator, and Alpha all read the
exact same numbers, from the exact same place, with the exact same provenance — never three independent
copies that can silently drift (see `_DISCLOSED_DISCREPANCY` below for a real one this canonicalization
effort caught).

**Every number below is copied, verbatim, from git-committed sources — never invented, never
recalibrated here.** The spread distribution and BASE_PROVISIONAL/STRESS_PROVISIONAL standard are copied
from `AI_TRADER_MANDATE8_STEP1_COST_CALIBRATION_REPORT.md` (committed `351f789`, git blob
`0e8207a4e81349fae11104db524206910b7b0816` — this module's own tests re-verify that blob hash against the
live file before trusting it, so a future edit to that report can never silently desync from what this
module claims to publish). Re-pulling `spread_collection`'s live SQLite state store to produce FRESH
percentiles was deliberately NOT done — the CEO's own instruction is to publish what is already
git-committed, not to recalibrate against runtime state that was never ratified.

**Fail-closed, not zero-as-fallback** (CEO's own explicit instruction, 2026-08-16: "Zero NU e
fallback"): `real_measured_slippage()` raises `CostModelUnavailableError` unconditionally today — zero
real fills exist across any live policy (confirmed in the Mandate 8 report, unchanged since: `pdh_pdl_demo
/slippage.py`'s `SlippageLog` is wired into both orchestrators but has never recorded an entry). Treating
that absence as `0.0` would misrepresent "never measured" as "measured, and free" — exactly the failure
mode this module exists to rule out.

**Disclosed discrepancy, found by this canonicalization exercise, NOT resolved here** (`NU recalibra`
applies to this module too — silently changing either side to make them agree would itself be an
undisclosed recalibration): `ai_trader/new_brain_bridge/bridge.py`'s own `DecisionRequest` construction
uses a literal cost triple — `full_spread_price=0.10, entry_slippage_price=0.05, exit_slippage_price=
0.05` (introduced commit `bd59266`, 2026-08-14) — that does NOT match this module's own
`BASE_PROVISIONAL` (`0.05/0.00/0.00`) despite a nearby test fixture's comment
(`mandate2_readiness/tests/test_brain_functional_proofs.py`, committed `f4859a5`, ten hours earlier the
SAME day) explicitly (and incorrectly) citing those bridge.py numbers as "BASE_PROVISIONAL... from
AI_TRADER_MANDATE8_STEP1_COST_CALIBRATION_REPORT.md". The report's own table never contained `0.10/0.05/
0.05` at all. This means `bridge.py`'s currently-running `new_brain_bridge` path is NOT actually feeding
N6 the ratified BASE_PROVISIONAL standard today — it is feeding a THIRD, uncited number nobody
independently ratified. Flagged here as `BRIDGE_PY_COST_LITERAL_MISMATCH` for CEO/Red Team decision;
`bridge.py` is deliberately left unmodified by this module (fixing it would itself be a recalibration
decision, not an export task)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

SHADOW_COST_MODEL_VERSION = "v1"

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


BASE_PROVISIONAL = CostComponents(full_spread_price=0.05, entry_slippage_price=0.00, exit_slippage_price=0.00)
STRESS_PROVISIONAL = CostComponents(full_spread_price=0.08, entry_slippage_price=0.08, exit_slippage_price=0.08)
"""Copied VERBATIM from the ratifying report's own section 3 table — `BASE_PROVISIONAL`/
`STRESS_PROVISIONAL`, "Approved provisionally (CEO, this mandate)... explicitly NOT empirical
calibration". `STRESS_PROVISIONAL.round_trip_total == 0.24` (0.08 spread + 0.08 + 0.08 slippage),
matching the report's own stated total exactly."""

_BRIDGE_PY_COST_LITERAL = CostComponents(full_spread_price=0.10, entry_slippage_price=0.05, exit_slippage_price=0.05)
"""What `new_brain_bridge/bridge.py`'s `DecisionRequest` construction ACTUALLY uses today (commit
`bd59266`) — NOT this module's `BASE_PROVISIONAL`. Exposed here, read-only, purely so a consumer (or a
test) can compare against it programmatically; never returned as this module's own recommended value."""

BRIDGE_PY_COST_LITERAL_MISMATCH = _BRIDGE_PY_COST_LITERAL != BASE_PROVISIONAL
"""`True` today — see this module's own docstring, "Disclosed discrepancy" section. A future fix to
either side would flip this to `False`; this module does not attempt to force that itself."""


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


def _components_for_tier(tier: str) -> CostComponents:
    if tier == "BASE":
        return BASE_PROVISIONAL
    if tier == "STRESS":
        return STRESS_PROVISIONAL
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


def content_hash() -> str:
    """A single, reproducible sha256 over every published numeric field this module exposes — the
    'hash de continut' the CEO's directive requires. Recomputed from the module's OWN in-memory constants
    (not re-read from disk), so it is stable across processes and only ever changes if this module's own
    published values change (which requires a new version, per the CEO's own 'niciodata o modificare
    tacita' instruction)."""
    payload = {
        "version": SHADOW_COST_MODEL_VERSION,
        "base_provisional": {
            "full_spread_price": BASE_PROVISIONAL.full_spread_price,
            "entry_slippage_price": BASE_PROVISIONAL.entry_slippage_price,
            "exit_slippage_price": BASE_PROVISIONAL.exit_slippage_price,
        },
        "stress_provisional": {
            "full_spread_price": STRESS_PROVISIONAL.full_spread_price,
            "entry_slippage_price": STRESS_PROVISIONAL.entry_slippage_price,
            "exit_slippage_price": STRESS_PROVISIONAL.exit_slippage_price,
        },
        "spread_distribution_clean": SPREAD_DISTRIBUTION_CLEAN,
        "spread_distribution_by_session": SPREAD_DISTRIBUTION_BY_SESSION,
        "source_report_blob_sha1": SOURCE_REPORT_BLOB_SHA1,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def configuration_fingerprint() -> str:
    """The identity fields governing THIS publication — commit + version + source blob, distinct from
    `content_hash()` (which covers the numeric payload only). Truncated to 16 hex chars, matching this
    codebase's own established `_fp()` convention (`new_brain_bridge/bridge.py`)."""
    payload = f"{SHADOW_COST_MODEL_VERSION}|{SOURCE_REPORT_COMMIT}|{SOURCE_REPORT_BLOB_SHA1}|{SLIPPAGE_MECHANISM_BLOB_SHA1}"
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
        "broker_server": BROKER_SERVER,
        "broker_company": BROKER_COMPANY,
        "symbol": SYMBOL,
        "units": UNITS,
        "entry_order_type": ENTRY_ORDER_TYPE,
        "exit_order_type": EXIT_ORDER_TYPE,
        "monitored_calendar_days": list(MONITORED_CALENDAR_DAYS),
        "base_provisional": {
            "full_spread_price": BASE_PROVISIONAL.full_spread_price,
            "entry_slippage_price": BASE_PROVISIONAL.entry_slippage_price,
            "exit_slippage_price": BASE_PROVISIONAL.exit_slippage_price,
            "round_trip_total": BASE_PROVISIONAL.round_trip_total,
        },
        "stress_provisional": {
            "full_spread_price": STRESS_PROVISIONAL.full_spread_price,
            "entry_slippage_price": STRESS_PROVISIONAL.entry_slippage_price,
            "exit_slippage_price": STRESS_PROVISIONAL.exit_slippage_price,
            "round_trip_total": STRESS_PROVISIONAL.round_trip_total,
        },
        "formula": {
            "base_once_real_slippage_exists": "BASE = median(spread) + median(slippage), per execution, both legs",
            "stress_once_real_slippage_exists": "STRESS = upper percentiles -- threshold set by Statistician + Red Team, not this division",
            "currently_in_effect": "BASE_PROVISIONAL/STRESS_PROVISIONAL (above) -- explicitly NOT empirical, unchanged until real slippage data exists and a ratified calibration supersedes them",
        },
        "spread_distribution_clean": SPREAD_DISTRIBUTION_CLEAN,
        "spread_distribution_by_session": SPREAD_DISTRIBUTION_BY_SESSION,
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
        "bridge_py_cost_literal_mismatch": BRIDGE_PY_COST_LITERAL_MISMATCH,
        "bridge_py_cost_literal": {
            "full_spread_price": _BRIDGE_PY_COST_LITERAL.full_spread_price,
            "entry_slippage_price": _BRIDGE_PY_COST_LITERAL.entry_slippage_price,
            "exit_slippage_price": _BRIDGE_PY_COST_LITERAL.exit_slippage_price,
            "note": "new_brain_bridge/bridge.py commit bd59266 -- does NOT match BASE_PROVISIONAL despite "
                    "a nearby test comment mis-citing it as such; flagged for CEO/Red Team, not resolved here",
        },
    }
