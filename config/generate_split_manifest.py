"""Generator for config/split_manifest.json (Statistician-authored, v2.2.0).

Recomputes every discovery/embargo/sealed boundary from first principles instead of hand-
transcribing epoch arithmetic into JSON. Run as a script: `python config/generate_split_manifest.py`
from the repository root. Writes config/split_manifest.json in place and prints the resulting
content_hash for commit-message verification.

This module is the WRITER (Statistician's authoring tool). It is distinct from
edge_research/split_manifest.py, which is the loader-side READER (Data Acquisition's, verifies and
never writes). Neither module imports the other.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final, Optional

_ROOT: Final[str] = os.path.dirname(os.path.abspath(__file__)) + os.sep + ".."
MANIFEST_PATH: Final[str] = os.path.join(_ROOT, "config", "split_manifest.json")

EMBARGO_SECONDS: Final[int] = 900_000
"""1000 M15 bars * 900s/bar = 900,000s. The single calendar-duration embargo width used at every
resolution (M15: 1000 bars, M5: 3000 bars, H1: 250 bars all equal this same 900,000s), per the
margin_factor (25/24) derivation already established."""

M15_BAR_SECONDS: Final[int] = 900
M5_BAR_SECONDS: Final[int] = 300
H1_BAR_SECONDS: Final[int] = 3600


def iso(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class Range:
    start_epoch: int
    end_epoch: int

    def to_json(self) -> dict[str, object]:
        return {
            "start_epoch": self.start_epoch,
            "start_iso": iso(self.start_epoch),
            "end_epoch": self.end_epoch,
            "end_iso": iso(self.end_epoch),
        }

    def days(self) -> float:
        return (self.end_epoch - self.start_epoch) / 86400.0

    def bars(self, bar_seconds: int) -> float:
        return (self.end_epoch - self.start_epoch) / bar_seconds


def count_data_rows(csv_path: str) -> int:
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader)  # header
        return sum(1 for _ in reader)


def first_last_bar_epoch(csv_path: str) -> tuple[int, int]:
    """Read only the header, first data row, and last data row -- not the whole file into memory."""
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        assert header[0] == "time", f"unexpected header in {csv_path}: {header}"
        first_row = next(reader)
        first_epoch = int(first_row[0])
        last_epoch = first_epoch
        for row in reader:
            last_epoch = int(row[0])
    return first_epoch, last_epoch


def month_end_close_epoch(csv_path: str, year_month: str) -> tuple[int, float]:
    """Find the last bar of the given 'YYYY-MM' month and return (epoch, close)."""
    last_epoch: Optional[int] = None
    last_close: Optional[float] = None
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader)  # header
        for row in reader:
            epoch = int(row[0])
            key = datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m")
            if key == year_month:
                last_epoch = epoch
                last_close = float(row[4])
    if last_epoch is None or last_close is None:
        raise ValueError(f"month {year_month} not found in {csv_path}")
    return last_epoch, last_close


@dataclass(frozen=True)
class SegmentSplit:
    """A fully computed 50/50-with-embargo split of one segment (or None if too short to split)."""
    discovery: Optional[Range]
    intra_embargo: Optional[Range]
    sealed: Optional[Range]
    too_short_reason: Optional[str]

    def to_json(self) -> dict[str, object]:
        if self.too_short_reason is not None:
            return {"split": "TOO_SHORT_FULLY_SEALED", "reason": self.too_short_reason}
        assert self.discovery is not None and self.intra_embargo is not None and self.sealed is not None
        return {
            "discovery_range": self.discovery.to_json(),
            "intra_segment_embargo": self.intra_embargo.to_json(),
            "sealed_range": self.sealed.to_json(),
        }


MIN_USABLE_BARS: Final[int] = 1000
"""Disclosed materiality convention, not a mathematically derived figure (unlike the embargo
widths): the floor below which a discovery or sealed sub-range is too thin to trust for real
statistical work, even if it technically clears the embargo-fits-at-all check. Chosen as a round
number comfortably above this lab's n>=25 minimum-N convention and its ~15-20-event power
thresholds, since a rare-event hypothesis needs many raw bars to yield enough qualifying events."""


def split_segment(
    disc_start: int,
    seg_end: int,
    leading_embargo_taken: bool,
    trailing_embargo_needed: bool,
    bar_seconds: int,
    min_bars: int = MIN_USABLE_BARS,
) -> SegmentSplit:
    """Split [disc_start, seg_end) 50/50 with an embargo band around the midpoint.

    disc_start is where THIS segment's own discovery may begin (already past any leading
    inter-segment embargo, applied by the caller). seg_end is this segment's own boundary
    (before any trailing inter-segment embargo, applied by the caller only if
    trailing_embargo_needed). Too-short is decided on the RESULTING discovery/sealed bar counts,
    not merely on whether the segment is nominally wider than the embargo band -- a segment can
    clear that coarse check and still leave each side too thin to be useful (caught the hard way
    once during generation; fixed here rather than left as a silent under-check).
    """
    sealed_end = seg_end - EMBARGO_SECONDS if trailing_embargo_needed else seg_end
    available = sealed_end - disc_start
    if available <= 2 * EMBARGO_SECONDS:
        return SegmentSplit(None, None, None, (
            f"available span {available/86400.0:.2f} days does not even fit the embargo band "
            f"(disc_start={iso(disc_start)}, sealed_end={iso(sealed_end)})."
        ))
    mid = disc_start + (sealed_end - disc_start) // 2
    discovery = Range(disc_start, mid - EMBARGO_SECONDS)
    intra_embargo = Range(mid - EMBARGO_SECONDS, mid + EMBARGO_SECONDS)
    sealed = Range(mid + EMBARGO_SECONDS, sealed_end)
    disc_bars = discovery.bars(bar_seconds)
    sealed_bars = sealed.bars(bar_seconds)
    if disc_bars < min_bars or sealed_bars < min_bars:
        return SegmentSplit(None, None, None, (
            f"resulting discovery ({disc_bars:.0f} bars) or sealed ({sealed_bars:.0f} bars) falls "
            f"below the {min_bars}-bar usability floor -- too short to leave a useful split even "
            "though it technically fits the embargo band; defaults to fully sealed per the "
            "conservative-when-inadequate-length principle."
        ))
    return SegmentSplit(discovery, intra_embargo, sealed, None)


def build_manifest() -> dict[str, Any]:
    data_dir = os.path.join(_ROOT, "data", "market")
    staging_dir = os.path.join(_ROOT, "acquisition_staging")

    m15_legacy_path = os.path.join(
        data_dir, "OANDA_XAUUSD_M15__SUPERSEDED_v1_2022-12-16_to_2026-07-13_R03terminal.csv"
    )
    m15_v2_path = os.path.join(data_dir, "OANDA_XAUUSD_M15.csv")
    m5_path = os.path.join(data_dir, "OANDA_XAUUSD_M5.csv")
    h1_path = os.path.join(staging_dir, "OANDA_XAUUSD_H1.csv")

    m15_legacy_first, m15_legacy_last = first_last_bar_epoch(m15_legacy_path)
    m15_v2_first, m15_v2_last = first_last_bar_epoch(m15_v2_path)
    m5_first, m5_last = first_last_bar_epoch(m5_path)
    h1_first, h1_last = first_last_bar_epoch(h1_path)

    m15_legacy_n = count_data_rows(m15_legacy_path)
    m15_v2_n = count_data_rows(m15_v2_path)
    m5_n = count_data_rows(m5_path)
    h1_n = count_data_rows(h1_path)

    # M15 (existing) cutoff: pre-existing, ratified, unchanged.
    m15_cutoff = 1761210900  # 2025-10-23T09:15:00Z

    # Authoritative 5-segment map, Verification 7, monthly closes, 15% threshold -- boundaries
    # located as exact month-end-close bars in the real M15_v2 file (not calendar-rounded).
    b_2011_08, close_2011_08 = month_end_close_epoch(m15_v2_path, "2011-08")
    b_2015_12, close_2015_12 = month_end_close_epoch(m15_v2_path, "2015-12")
    b_2020_07, close_2020_07 = month_end_close_epoch(m15_v2_path, "2020-07")
    b_2022_10, close_2022_10 = month_end_close_epoch(m15_v2_path, "2022-10")
    b_2026_02, close_2026_02 = month_end_close_epoch(m15_v2_path, "2026-02")
    b_2026_06, close_2026_06 = month_end_close_epoch(m15_v2_path, "2026-06")

    expected_closes = {
        "2011-08": (close_2011_08, 1827.0), "2015-12": (close_2015_12, 1061.0),
        "2020-07": (close_2020_07, 1976.0), "2022-10": (close_2022_10, 1633.0),
        "2026-02": (close_2026_02, 5279.0), "2026-06": (close_2026_06, 4006.0),
    }
    for label, (actual, expected) in expected_closes.items():
        assert abs(actual - expected) < 1.0, f"{label}: close {actual} does not match authoritative map's {expected}"

    # ---- M15_v2 segments (own jurisdiction only; overlap range [m15_cutoff-side] is inherited) ----
    seg1 = split_segment(m15_v2_first, b_2015_12, leading_embargo_taken=False, trailing_embargo_needed=True, bar_seconds=M15_BAR_SECONDS)
    seg2 = split_segment(b_2015_12 + EMBARGO_SECONDS, b_2020_07, leading_embargo_taken=True, trailing_embargo_needed=True, bar_seconds=M15_BAR_SECONDS)
    seg3 = split_segment(
        b_2020_07 + EMBARGO_SECONDS, b_2022_10, leading_embargo_taken=True, trailing_embargo_needed=True, bar_seconds=M15_BAR_SECONDS
    )
    # segment-4 prefix: b_2022_10 -> m15_legacy_first. Needs BOTH a leading embargo (entry from
    # segment 3's sealed tail) AND a trailing one-sided embargo (handoff into M15's own inherited
    # discovery start, full margin taken from this segment's side per CEO's instruction that M15's
    # own dataset start is never shifted).
    seg4_prefix = split_segment(
        b_2022_10 + EMBARGO_SECONDS, m15_legacy_first, leading_embargo_taken=True, trailing_embargo_needed=True, bar_seconds=M15_BAR_SECONDS
    )
    # tail beyond legacy M15's own end, within M15_v2's own dataset:
    # M15 (existing) is untouched and was not designed to leave a leading-embargo margin for this
    # tail -- the only place a margin can be taken is on M15_v2's own side. Applied uniformly with
    # the rest of this generator (embargo assumed needed at every transition, never skipped on a
    # downstream-outcome prediction): confirmed too short even under this one-sided assumption.
    seg5_tail = split_segment(
        m15_legacy_last + EMBARGO_SECONDS, m15_v2_last, leading_embargo_taken=True, trailing_embargo_needed=False, bar_seconds=M15_BAR_SECONDS
    )

    # ---- M5 segments (own, full jurisdiction -- no inheritance, M5 is not the same timeframe as M15) ----
    m5_segA = split_segment(m5_first, b_2022_10, leading_embargo_taken=False, trailing_embargo_needed=True, bar_seconds=M5_BAR_SECONDS)
    m5_segB = split_segment(b_2022_10 + EMBARGO_SECONDS, b_2026_02, leading_embargo_taken=True, trailing_embargo_needed=True, bar_seconds=M5_BAR_SECONDS)
    m5_segC = split_segment(b_2026_02 + EMBARGO_SECONDS, b_2026_06, leading_embargo_taken=True, trailing_embargo_needed=True, bar_seconds=M5_BAR_SECONDS)
    m5_tail = split_segment(b_2026_06 + EMBARGO_SECONDS, m5_last, leading_embargo_taken=True, trailing_embargo_needed=False, bar_seconds=M5_BAR_SECONDS)

    # ---- M15_v2 discovery blocks (every disjoint discovery sub-range: the M15_v2-owned segments'
    # own discovery portions, plus the inherited M15 discovery range for the overlap window) --
    # gathered mechanically, not re-typed, so the HTF resample rule below operates on the exact
    # same ranges already computed above.
    m15_v2_discovery_blocks: list[Range] = [
        seg for seg in (seg1.discovery, seg2.discovery, seg3.discovery) if seg is not None
    ] + [Range(m15_legacy_first, m15_cutoff - EMBARGO_SECONDS)]  # inherited from M15 (existing), unchanged

    htf_resample_rule: dict[str, Any] = {
        "provenance_key": "CONTEXT_DERIVED_VALIDATED",
        "source_timeframe": "M15_v2",
        "source_file_sha256": sha256_file(m15_v2_path),
        "principle": (
            "An HTF bar is a deterministic aggregation (OHLCV rollup) of its constituent M15_v2 bars. "
            "If even one constituent bar is sealed or in an embargo band, the aggregate's O/H/L/C/V "
            "values are mathematically a function of that sealed information -- this is not a possible "
            "leak, it is a certain one (e.g. a D1 high is max() over its 96 M15 highs; if any one of "
            "those 96 is sealed and happens to be the day's high, the D1 'high' passed to context IS "
            "the sealed value, directly). A 'mark it but keep the tainted value' rule would still leak "
            "to any consumer that reads OHLCV without checking the flag -- the same fragility this "
            "manifest's fail-closed design already rejects elsewhere. Exclusion is therefore not merely "
            "preferred, it is the only rule consistent with the rest of this system."
        ),
        "mechanical_rule": (
            "For an HTF bar of N M15_v2 bars (H4: N=16, D1: N=96) with a fixed, calendar-aligned window "
            "[w_start, w_end): construct it if and only if all N M15_v2 bars whose timestamps fall in "
            "[w_start, w_end) exist AND belong entirely to a SINGLE discovery block from "
            "m15_v2_discovery_blocks below (never spanning two separate discovery blocks, even though "
            "both are 'discovery' -- removes any ambiguity at the source rather than relying on the "
            "embargo gap between them to catch it incidentally). If any of the N required bars is "
            "missing, or belongs to an embargo band, or belongs to the sealed range, the HTF bar for "
            "that window is NOT constructed -- absent from the output file entirely, never null-filled, "
            "never present-but-flagged. No partial or truncated HTF bar (fewer than N components) is "
            "ever emitted, regardless of how many of the N components happen to be valid discovery bars."
        ),
        "segment_vs_quarantine_boundary_note": (
            "A segment-to-segment (regime-type) transition and a discovery/quarantine transition are "
            "the SAME thing under this rule, not two cases needing separate treatment: every inter-"
            "segment transition in M15_v2's own regime_segments already carries its own embargo band "
            "(see STATISTICIAN_H1_PREREGISTRATION_PROTOCOL_v1.0.md / the M15_v2 segments above), so an "
            "HTF bar straddling a segment boundary is, by construction, also straddling a quarantine "
            "band and is excluded by the same mechanical rule -- no additional case distinction exists."
        ),
        "incomplete_edge_bars_note": (
            "HTF bar boundaries are fixed by calendar/session convention (independent of where a "
            "discovery block happens to start or end), so a discovery block's first and last calendar-"
            "aligned HTF windows will typically NOT align exactly with the block's own start/end epoch. "
            "Any such boundary-adjacent HTF window that would need bars outside the block is excluded "
            "under the same rule -- it is not truncated to whatever partial data exists inside the "
            "block."
        ),
        "m15_v2_discovery_blocks": [b.to_json() for b in m15_v2_discovery_blocks],
        "entries": {
            "H4_from_M15_v2": {
                "aggregation_bars": 16, "bar_seconds": 14400,
                "data_file_sha256": {"value": None, "status": "AWAITING_DATA_ACQUISITION_GENERATION"},
                "status": "AWAITING_GENERATION",
            },
            "D1_from_M15_v2": {
                "aggregation_bars": 96, "bar_seconds": 86400,
                "data_file_sha256": {"value": None, "status": "AWAITING_DATA_ACQUISITION_GENERATION"},
                "status": "AWAITING_GENERATION",
            },
        },
        "who_does_what": (
            "Statistician specifies this rule and registers it here. Data Acquisition executes the "
            "generation and supplies the resulting data_file_sha256 for H4_from_M15_v2 and "
            "D1_from_M15_v2 -- Statistician does not generate these files and does not ratify a hash it "
            "produced itself, same separation already applied to the four base data-file hashes "
            "(Statistician ratifies, Data Acquisition measures)."
        ),
        "distinct_from_native_H1": (
            "This section governs H4/D1 CONTEXT bars resampled from M15_v2 -- it is unrelated to the "
            "separately-acquired NATIVE H1 dataset (its own file, its own data_file_sha256, currently "
            "AWAITING_REGIME_MAP as its own timeframe entry above). Do not conflate the two, same "
            "discipline as the M15/M15_v2 identifier resolution."
        ),
        "unblocks": "Research Lab's context guard, once both H4_from_M15_v2 and D1_from_M15_v2 reach status VALIDATED.",
    }

    manifest: dict[str, Any] = {
        "manifest_id": "STAT-SPLIT-MANIFEST",
        "version": "2.3.0",
        "published_date": "2026-07-27",
        "authority": (
            "Statistician (ai_quant_lab, branch statistician-foundation) -- design/specification "
            "authority only, per Contract Statistician<->Validation Engine SS1.7. Generated by "
            "config/generate_split_manifest.py, not hand-transcribed."
        ),
        "generator": "config/generate_split_manifest.py",
        "changelog_v2_3": (
            "Adds context_derived_htf: the mechanical rule for resampling H4/D1 context bars from "
            "M15_v2 (CTO-approved Option B, since the lab's existing H1/H4/D1 context files were "
            "already resamples of M15 -- confirmed by their 7-column format vs. 6). Addresses the "
            "blocking reserve that M15_v2's discovery mask is a union of disjoint blocks separated by "
            "quarantine bands (loader delivers only 130,491 of 355,696 bars) -- an HTF bar aggregating "
            "16 (H4) or 96 (D1) M15 bars whose window straddles a quarantine or sealed boundary would "
            "otherwise encode sealed information directly into its OHLCV values, making context the "
            "leak channel. Rule: exclude any HTF bar not fully constructible from a single discovery "
            "block, no partial/truncated bars, no case distinction between segment-boundary and "
            "discovery/quarantine-boundary straddles (they are the same thing here). Registers "
            "H4_from_M15_v2 and D1_from_M15_v2 under provenance CONTEXT_DERIVED_VALIDATED with the "
            "source file's own hash for traceability; both AWAITING_GENERATION -- Statistician "
            "specifies and registers, Data Acquisition generates and supplies the resulting hashes."
        ),
        "changelog_v2_2": (
            "Ratified all four data_file_sha256 values (independently recomputed by Statistician "
            "directly against the physical files, not merely accepted from Data Acquisition's report -- "
            "all four matched exactly). Replaced the v2.0.0/v2.1.0 pro-forma Jan-1-UTC regime "
            "characterization with Data Acquisition's authoritative 5-segment monthly-close map "
            "(Verification 7, 15% threshold); superseded, not merged (see superseded_regime_map_v2_0_0). "
            "M15_v2 promoted to VALIDATED. Derived and populated the M5 regime map aligned to the same "
            "authoritative segments; M5 promoted to VALIDATED. H1's data_file_sha256 is now confirmed "
            "too, but H1 stays AWAITING_REGIME_MAP -- no mechanical regime characterization has been "
            "delivered for it. Added no_unregistered_research_lines_rule per explicit mandate."
        ),
        "remaining_requests_to_data_acquisition": [
            "Deliver a mechanical, disclosed regime characterization (segment type + boundaries, "
            "monthly-close convention or better) for H1 -- the only remaining gap before H1 can reach "
            "VALIDATED. Connect H1 out of acquisition_staging/ into data/market/ once ready."
        ],
        "authoritative_regime_map_source": (
            "Data Acquisition, Verification 7, monthly closes, 15% threshold. Segment boundaries "
            "located as exact month-end-close bars in the real M15_v2 file (asserted against the "
            "authoritative close prices at generation time, not merely assumed)."
        ),
        "superseded_regime_map_v2_0_0": {
            "status": "SUPERSEDED",
            "reason": (
                "v2.0.0/v2.1.0 used a year-level regime characterization (2011-2015 bear, 2015-2020 "
                "bull, 2020-2022 correction, 2022-2026 bull) operationalized via a disclosed but "
                "PRO-FORMA Jan-1-UTC convention -- never a claim of mechanical precision. CTO resolved "
                "the conflict in favor of the real, monthly-close, 15%-threshold authoritative map "
                "(5 segments) delivered at Verification 7. The pro-forma table is not merged or "
                "reconciled with the real one -- it is superseded outright, same treatment as SS3 in "
                "STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES_v1.0.md."
            ),
        },
        "no_unregistered_research_lines_rule": {
            "rule": (
                "No unregistered Research Question structure and no autonomous exploratory engine is "
                "authorized to touch data or exist in the codebase. This is a RULE, not a note: any "
                "new research line -- exactly like any individual hypothesis -- requires a pre-"
                "registration (population, threshold, config, split) BEFORE touching data. The canonical "
                "lines are the 1972 S1-S51 hypotheses and Flow A's active contracts; nothing else is "
                "authorized by this manifest or any Statistician document."
            ),
            "provenance": "CTO veto (ratified) on the 54-RQ autonomous-engine proposal in a prior mandate; recorded here per explicit instruction.",
        },
        "fail_closed_default": {
            "rule": (
                "A timeframe entry is loadable ONLY if its top-level \"status\" field is exactly "
                "\"VALIDATED\". Every other value means the loader MUST treat 100% of that timeframe's "
                "bars as SEALED."
            ),
            "exception_for_already_operating_entries": (
                "M15 (current) stays VALIDATED though its data_file_sha256 was, until this version, "
                "unconfirmed. Now confirmed (see M15.data_file_sha256) -- ratified by Statistician's own "
                "independent SHA-256 computation against the physical file, not merely accepted from "
                "Data Acquisition's report."
            ),
        },
        "dataset_identity_resolution": {
            "rule_1_no_implicit_default": "\"M15\" and \"M15_v2\" are distinct keys; an unqualified request is a hard error.",
            "rule_2_overlap_inheritance_not_arbitration": (
                f"For [{m15_legacy_first}, {m15_legacy_last}] (M15's own dataset span), M15_v2 inherits "
                "M15's discovery/embargo/sealed classification verbatim -- not independently recomputed."
            ),
        },
        "same_window_resampled_predicate": {
            "formula": (
                "overlap_seconds = max(0, min(parameterization_window.end_epoch, test_window.end_epoch) "
                "- max(parameterization_window.start_epoch, test_window.start_epoch))"
            ),
            "predicate": "is_same_window_resampled := (overlap_seconds > 0)",
            "action_if_true": "Label SAME-WINDOW-RESAMPLED; never an independent confirmation.",
        },
        "margin_factor": {"value": "25/24", "note": "960->1000 M15; 2880->3000 M5; 240->250 H1."},
        "context_derived_htf": htf_resample_rule,
        "timeframes": {
            "M15": {
                "bar_seconds": M15_BAR_SECONDS,
                "dataset": {"n_bars": m15_legacy_n, "start_epoch": m15_legacy_first, "start_iso": iso(m15_legacy_first),
                            "end_epoch": m15_legacy_last, "end_iso": iso(m15_legacy_last)},
                "file_path": "data/market/OANDA_XAUUSD_M15__SUPERSEDED_v1_2022-12-16_to_2026-07-13_R03terminal.csv",
                "split_method": "single_global_cutoff",
                "cutoff_epoch": m15_cutoff, "cutoff_iso": iso(m15_cutoff),
                "embargo_bars": 1000, "embargo_seconds": EMBARGO_SECONDS,
                "discovery_range": Range(m15_legacy_first, m15_cutoff - EMBARGO_SECONDS).to_json(),
                "embargo_range": Range(m15_cutoff - EMBARGO_SECONDS, m15_cutoff + EMBARGO_SECONDS).to_json(),
                "sealed_range": Range(m15_cutoff + EMBARGO_SECONDS, m15_legacy_last).to_json(),
                "regime_segments": None,
                "data_file_sha256": {
                    "value": sha256_file(m15_legacy_path),
                    "status": "CONFIRMED_BY_STATISTICIAN",
                    "source": "Independently computed by Statistician directly against the physical file at generation time.",
                },
                "status": "VALIDATED",
            },
            "M15_v2": {
                "bar_seconds": M15_BAR_SECONDS,
                "dataset": {"n_bars": m15_v2_n, "start_epoch": m15_v2_first, "start_iso": iso(m15_v2_first),
                            "end_epoch": m15_v2_last, "end_iso": iso(m15_v2_last)},
                "file_path": "data/market/OANDA_XAUUSD_M15.csv",
                "split_method": "50_50_stratified_by_regime_segment_with_inherited_overlap",
                "overlap_with_M15": {
                    "range": Range(m15_legacy_first, m15_legacy_last).to_json(),
                    "rule": "Inherits M15's discovery/embargo/sealed classification verbatim.",
                },
                "embargo_bars": 1000, "embargo_seconds": EMBARGO_SECONDS,
                "regime_segments": [
                    {"label": "2011-08 -> 2015-12 bear (-42.0%)", "type": "bear",
                     "segment_range": Range(m15_v2_first, b_2015_12).to_json(), "split_ratio": "50/50",
                     **seg1.to_json()},
                    {"label": "2015-12 -> 2020-07 bull (+86.3%)", "type": "bull",
                     "segment_range": Range(b_2015_12, b_2020_07).to_json(), "split_ratio": "50/50",
                     **seg2.to_json()},
                    {"label": "2020-07 -> 2022-10 correction (-17.4%)", "type": "correction",
                     "segment_range": Range(b_2020_07, b_2022_10).to_json(), "split_ratio": "50/50",
                     **seg3.to_json()},
                    {"label": "2022-10 pre-overlap sliver (part of 2022-10->2026-02 bull +223.3%; "
                              "remainder inherited via overlap_with_M15)", "type": "bull_partial",
                     "segment_range": Range(b_2022_10, m15_legacy_first).to_json(), "split_ratio": "N/A",
                     **seg4_prefix.to_json()},
                ],
                "post_M15_tail": {"range": Range(m15_legacy_last, m15_v2_last).to_json(), **seg5_tail.to_json()},
                "irreplaceable_segment_flag": {
                    "range": Range(h1_first, m15_v2_first).to_json(),
                    "note": "Outside M15_v2's own dataset (starts later) -- see H1.irreplaceable_segment_flag.",
                },
                "data_file_sha256": {
                    "value": sha256_file(m15_v2_path),
                    "status": "CONFIRMED_BY_STATISTICIAN",
                    "source": "Independently computed by Statistician directly against the physical file at generation time.",
                },
                "status": "VALIDATED",
            },
            "M5": {
                "bar_seconds": M5_BAR_SECONDS,
                "dataset": {"n_bars": m5_n, "start_epoch": m5_first, "start_iso": iso(m5_first),
                            "end_epoch": m5_last, "end_iso": iso(m5_last)},
                "file_path": "data/market/OANDA_XAUUSD_M5.csv",
                "split_method": "50_50_stratified_by_regime_segment",
                "embargo_bars": 3000, "embargo_seconds": EMBARGO_SECONDS,
                "regime_segments": [
                    {"label": "2020-07 -> 2022-10 correction (-17.4%) -- M5 catches only the tail", "type": "correction",
                     "segment_range": Range(m5_first, b_2022_10).to_json(), "split_ratio": "50/50",
                     **m5_segA.to_json()},
                    {"label": "2022-10 -> 2026-02 bull (+223.3%) -- full", "type": "bull",
                     "segment_range": Range(b_2022_10, b_2026_02).to_json(), "split_ratio": "50/50",
                     **m5_segB.to_json()},
                    {"label": "2026-02 -> 2026-06 correction (-24.1%) -- full, short (~4 months)", "type": "correction",
                     "segment_range": Range(b_2026_02, b_2026_06).to_json(), "split_ratio": "50/50",
                     "usability_check": (
                         f"After embargo accounting: discovery {m5_segC.discovery.bars(M5_BAR_SECONDS) if m5_segC.discovery else 0:.0f} "
                         f"bars, sealed {m5_segC.sealed.bars(M5_BAR_SECONDS) if m5_segC.sealed else 0:.0f} bars. "
                         "Comfortably above any minimum-N threshold used elsewhere in this lab (n>=25; power "
                         "thresholds ~15-20 events) -- kept at 50/50, not downgraded to 60/40 or marked unusable."
                     ) if m5_segC.discovery is not None else "TOO SHORT -- see split field.",
                     **m5_segC.to_json()},
                ],
                "post_map_tail": {"range": Range(b_2026_06, m5_last).to_json(), **m5_tail.to_json()},
                "data_file_sha256": {
                    "value": sha256_file(m5_path),
                    "status": "CONFIRMED_BY_STATISTICIAN",
                    "source": "Independently computed by Statistician directly against the physical file at generation time.",
                },
                "status": "VALIDATED",
            },
            "H1": {
                "bar_seconds": H1_BAR_SECONDS,
                "dataset": {"n_bars": h1_n, "start_epoch": h1_first, "start_iso": iso(h1_first),
                            "end_epoch": h1_last, "end_iso": iso(h1_last)},
                "file_path": "acquisition_staging/OANDA_XAUUSD_H1.csv",
                "split_method": "50_50_stratified_by_regime_segment",
                "embargo_bars": 250, "embargo_seconds": EMBARGO_SECONDS,
                "regime_segments": "AWAITING_REGIME_MAP",
                "discovery_range": None, "embargo_range": None, "sealed_range": None,
                "irreplaceable_segment_flag": {
                    "range": Range(h1_first, m15_v2_first).to_json(),
                    "note": "Never observed at any resolution, in this lab, ever.",
                },
                "data_file_sha256": {
                    "value": sha256_file(h1_path),
                    "status": "CONFIRMED_BY_STATISTICIAN",
                    "source": "Independently computed by Statistician directly against the physical file at generation time.",
                },
                "status": "AWAITING_REGIME_MAP",
                "loader_contract": "H1 not connected (acquisition_staging/); regime map not yet delivered. 100% sealed.",
            },
        },
        "content_hash": {"algorithm": "sha256", "computed_over": "this exact file with content_hash.value blanked", "value": ""},
    }
    return manifest


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    manifest = build_manifest()
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    text_blanked = text.replace('"value": ""', '"value": ""')  # placeholder already blank
    digest = hashlib.sha256(text_blanked.encode("utf-8")).hexdigest()
    manifest["content_hash"]["value"] = digest
    final_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(final_text)
    print("content_hash:", digest)


if __name__ == "__main__":
    main()
