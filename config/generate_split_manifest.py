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
                "file_path": "data/market/OANDA_XAUUSD_H4_from_M15_v2.csv",
                "window_convention": "Anchored 17:00 America/New_York (DST-aware), per code/resample_ny.py. sub = count of constituent M15_v2 bars.",
                "generation": {"bars_with_rule": 12832, "bars_without_rule": 23186, "bars_eliminated": 10354,
                               "generated_by": "Data Acquisition, Mandate 2.7"},
                "data_file_sha256": {
                    "value": sha256_file(os.path.join(_ROOT, "data", "market", "OANDA_XAUUSD_H4_from_M15_v2.csv")),
                    "status": "CONFIRMED_BY_STATISTICIAN",
                    "source": "Independently computed by Statistician directly against the physical file at generation time; matches Data Acquisition's reported value exactly.",
                },
                "rule_compliance_note": (
                    "Boundary compliance (no HTF bar straddles a discovery-block edge) rests on Data "
                    "Acquisition's own test suite (tests/test_loader_holdout_boundary.py, 28/28 passing, "
                    "including dedicated straddle/coverage-gap/bar-count checks) -- NOT independently "
                    "re-derived here. A naive UTC-aligned spot-check by Statistician flagged false "
                    "positives because the real windowing is 17:00-America/New_York DST-aware, not "
                    "simple UTC alignment; reimplementing that check correctly was out of scope for this "
                    "ratification. File integrity (hash, row count) IS independently verified above."
                ),
                "status": "CONTEXT_DERIVED_VALIDATED",
            },
            "D1_from_M15_v2": {
                "aggregation_bars": 96, "bar_seconds": 86400,
                "file_path": "data/market/OANDA_XAUUSD_D1_from_M15_v2.csv",
                "window_convention": "Anchored 17:00 America/New_York (DST-aware), per code/resample_ny.py. sub = count of constituent M15_v2 bars.",
                "generation": {"bars_with_rule": 2141, "bars_without_rule": 3878, "bars_eliminated": 1737,
                               "generated_by": "Data Acquisition, Mandate 2.7"},
                "data_file_sha256": {
                    "value": sha256_file(os.path.join(_ROOT, "data", "market", "OANDA_XAUUSD_D1_from_M15_v2.csv")),
                    "status": "CONFIRMED_BY_STATISTICIAN",
                    "source": "Independently computed by Statistician directly against the physical file at generation time; matches Data Acquisition's reported value exactly.",
                },
                "rule_compliance_note": "See H4_from_M15_v2.rule_compliance_note -- identical basis.",
                "status": "CONTEXT_DERIVED_VALIDATED",
            },
            "H1_from_M15_v2": {
                "aggregation_bars": 4, "bar_seconds": 3600,
                "file_path": "data/market/OANDA_XAUUSD_H1_from_M15_v2.csv",
                "file_path_note": (
                    "RELOCATED (commit d99d241, Data Acquisition hotfix). v2.4.1 incorrectly registered "
                    "this entry's file_path as acquisition_staging/..._UNREGISTERED.csv -- a staging path "
                    "whose own filename said UNREGISTERED, while status simultaneously read "
                    "CONTEXT_DERIVED_VALIDATED and another changelog said the opposite (not registered). "
                    "v2.4.2 reverted to pending; Data Acquisition then moved the file to "
                    "data/market/OANDA_XAUUSD_H1_from_M15_v2.csv (clean name) with .gitattributes pinned "
                    "-text (LF) BEFORE the move specifically to prevent a CRLF conversion changing the "
                    "hash (the same lesson as the legacy M15 8f865b87-vs-c777cb9c incident). The "
                    "recomputed hash is BYTE-IDENTICAL to the pre-move staging value -- confirmed "
                    "independently by Statistician re-hashing the file at its NEW path, not by reusing "
                    "the remembered value; the two only coincide because the move was truly byte-"
                    "preserving here, not assumed."
                ),
                "window_convention": "Anchored UTC hour (matches native H1), per code/resample_ny.py. sub = count of constituent M15_v2 bars.",
                "generation": {"bars_with_rule": 49580, "bars_without_rule": 89549, "bars_eliminated": 39969,
                               "generated_by": "Data Acquisition, Mandate 2.7 (on separate CEO instruction); relocated Mandate hotfix d99d241"},
                "data_file_sha256": {
                    "value": sha256_file(os.path.join(_ROOT, "data", "market", "OANDA_XAUUSD_H1_from_M15_v2.csv")),
                    "status": "CONFIRMED_BY_STATISTICIAN",
                    "source": "Independently computed by Statistician directly against the physical file AT ITS NEW LOCATION at generation time; matches Data Acquisition's reported post-move value (commit d99d241) exactly.",
                },
                "rule_compliance_note": "See H4_from_M15_v2.rule_compliance_note -- identical basis.",
                "classification_delimitation": (
                    "H1_from_M15_v2 is a CONTEXT-DERIVED ARTIFACT (identical mechanical rule as H4/D1 "
                    "above -- no new methodology), registered for the interval M15_v2's discovery blocks "
                    "happen to cover (roughly 2011-2021), specifically to unblock Research Lab's mstrat "
                    "context guard. It does NOT substitute for, replace, or speak to the status of the "
                    "separately-acquired NATIVE H1 dataset (its own timeframe entry above, still "
                    "AWAITING_REGIME_MAP, untouched by this registration)."
                ),
                "governance_note_operational_motivation_disclosed": (
                    "Flagged explicitly, per instruction, rather than accepted silently: the REASON this "
                    "entry is registered now is operational (unblocking a downstream consumer) rather "
                    "than a property of the data reaching some qualification threshold on its own -- the "
                    "native H1 dataset has not completed its own regime-map registration path, and this "
                    "derived proxy is being registered instead of waiting for it. This is the first "
                    "instance in this project of a classification driven by a desired outcome rather "
                    "than by what the data represents. It is accepted here ONLY because: (1) it uses the "
                    "exact same, already-validated mechanical rule as H4/D1, introducing no new method; "
                    "(2) it is explicitly and permanently labeled as distinct from and non-substitutive "
                    "of the native H1 entry, which remains untouched and separately trackable; (3) no "
                    "information about the native H1 dataset's own status is obscured or implied resolved "
                    "by this registration. This is NOT a template: a future request to register a derived "
                    "proxy specifically to bypass a pending native dataset's own qualification path must "
                    "be justified anew on its own facts, not assumed permitted by this precedent."
                ),
                "status": "CONTEXT_DERIVED_VALIDATED",
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
            "This section governs H4/D1/H1 CONTEXT bars resampled from M15_v2 -- it is unrelated to the "
            "separately-acquired NATIVE H1 dataset (its own file, its own data_file_sha256, currently "
            "AWAITING_REGIME_MAP as its own timeframe entry above). H1_from_M15_v2 in particular does "
            "NOT substitute for or resolve the native H1 entry's own status -- see its own "
            "classification_delimitation and governance_note above. Do not conflate any of the three "
            "with the native entries, same discipline as the M15/M15_v2 identifier resolution."
        ),
        "unblocks": "Research Lab's context guard -- H4_from_M15_v2, D1_from_M15_v2, and H1_from_M15_v2 are all status CONTEXT_DERIVED_VALIDATED. Statistician confirms to CEO when Research Lab's guard may actually start -- promotion here does not auto-trigger it.",
        "version_history": [
            {"version": "2.2.0", "commit": "4e1f550", "content": "M15_v2 + M5 regime segments"},
            {"version": "2.3.0", "commit": "a4c0baf", "content": "HTF context resample rule specified"},
            {"version": "2.3.1", "commit": "774acea", "content": "H4/D1 hashes supplied by Data Acquisition, GENERATED_PENDING_RATIFICATION (Data-Acquisition-authored injection, not a Statistician version)"},
            {"version": "2.4.0", "commit": "9286981", "content": "E001/E002/E004 candidate verdicts; H4/D1 ratified to CONTEXT_DERIVED_VALIDATED"},
            {"version": "2.4.1", "commit": "ab0e823", "content": "H1_from_M15_v2 registered and ratified (file_path/hash later found to be incorrect -- see v2.4.2); commit-citation correction recorded (an order incorrectly cited 4e1f550 as v2.4.0 -- it is v2.2.0, three mandates earlier)"},
            {"version": "2.4.2", "commit": "2c7b2c7", "content": "Hotfix: reconciles the v2.4.1 self-contradiction on H1_from_M15_v2 (registered as CONTEXT_DERIVED_VALIDATED with a staging/UNREGISTERED file_path while another changelog said unregistered) -- Data Acquisition relocated the file (commit d99d241) within the same hotfix window, hash independently re-verified at the new path (byte-identical), entry promoted to CONTEXT_DERIVED_VALIDATED with the correct canonical path; added mechanical consistency checks to this generator (validate_context_derived_consistency)"},
            {"version": "2.5.0", "commit": "da7ca85", "content": "Registers legacy_428_atr_persistence_verdicts (367 ZERO_ALPHA_BASE_RATE / 58 REGIME_PERSISTENCE_FAILURE / 3 EXTREME_CONCENTRATION_FRAGILITY_wo1) and the deduplication_prescreening_rule (PROJECT_AUDIT.md D11/SSF); confirms M5 stays in the repository, its own AWAITING_REGIME_MAP status unchanged, while the separate M5-aligned HTF context effort is CANCELLED (CTO decision) -- distinct facts, not to be conflated"},
            {"version": "2.5.1", "commit": "f08c254", "content": "Ratifies 6 of 7 market_structure/liquidity_mechanics design decisions (D1/D2/D4/D5/D6/D7); holds D3's cost-acceptability pending a real-data blind-window measurement (principle ratified, synthetic 16-bar estimate explicitly not sufficient); pre-registers LM-001 (Liquidity Basin Wick-Sweep-Reject), a new namespace chosen instead of the requested 'E001_v2' naming to avoid implying resuscitation of a REJECTED candidate"},
            {"version": "2.5.2", "commit": "00af4b1", "content": "Closes E004's fill-rate PENDING_CONTROL note: Flow A executed STATISTICIAN_E004_FILL_CONTROL_SPEC_v1.0.md exactly (commit b4d5f89) -- control rate 0.850 falls in the pre-registered (0.512,0.886) band, mechanical label OBSERVED_NOT_DISTINCTIVE, read off the table not chosen post-hoc"},
            {"version": "2.5.3", "commit": "PENDING (this version)", "content": "Mandate 3.10: lifts D3_block_reset to full RATIFIED on VE's real-data blind-window audit (MK-01 Step 2, commit 260c4e3 -- bear 0.0305%/bull 0.0170%/correction 0.0396%, all far below the 1% low-cost threshold); corrects Statistician's own '8 structures' count to the correct '6' (3 discovery blocks x 2 swing types -- the fourth M15_v2 segment has no discovery_range); declares the half-open [start_epoch,end_epoch) boundary_convention as a single mechanical rule (resolves the recurring VE-vs-Research-Lab one-bar discrepancy, verified directly against OANDA_XAUUSD_M15.csv); rules CROSS_VERIFICATION_SPEC scope (applies to derived data artifacts, not generically to verification/measurement code reading only through an already-safe discovery mask -- explicit limit stated); registers the re_arming_bug_MK02 fix specification (found by VE, MK-01/MK-02 Step 1 commit 6b7948f) and confirms the D3 volume audit remains valid (mk_d3_volume_audit.py never imports detect_breaks, verified directly)"},
        ],
    }

    manifest: dict[str, Any] = {
        "manifest_id": "STAT-SPLIT-MANIFEST",
        "version": "2.5.3",
        "published_date": "2026-07-28",
        "authority": (
            "Statistician (ai_quant_lab, branch statistician-foundation) -- design/specification "
            "authority only, per Contract Statistician<->Validation Engine SS1.7. Generated by "
            "config/generate_split_manifest.py, not hand-transcribed."
        ),
        "generator": "config/generate_split_manifest.py",
        "changelog_v2_4_1": (
            "Records a commit-citation correction: a CTO order cited 'manifest v2.4.0, commit 4e1f550' "
            "-- 4e1f550 is v2.2.0, three mandates earlier (see version_history above for the real "
            "chain). Freezing state by citing that commit would freeze a stale version; recorded here "
            "so the correction is durable, not just conversational. Registers H1_from_M15_v2 under "
            "context_derived_htf.entries (hash 524977d0...f660, 49,580 bars, independently verified "
            "directly against the physical file, cross-checked against Data Acquisition's "
            "DATA_ACQUISITION_FINAL_REPORT.md line 140 -- not copied from any relayed message), with an "
            "explicit classification_delimitation and governance_note disclosing that this is the first "
            "registration in the project driven by an operational need (unblocking Research Lab's "
            "mstrat context guard) rather than by the data reaching a qualification threshold on its "
            "own -- accepted only because it reuses the already-validated H4/D1 mechanism unchanged, "
            "stays permanently distinct from the native H1 entry, and is explicitly NOT a template for "
            "future convenience-driven classifications. Promotes H4/D1/H1_from_M15_v2 status from "
            "VALIDATED to the more specific CONTEXT_DERIVED_VALIDATED (matching provenance_key exactly, "
            "avoiding confusion with base-timeframe VALIDATED). Statistician ratifies hashes only, not "
            "rule-conformance (which rests on Data Acquisition's own 28/28-passing test suite) -- stated "
            "explicitly, again, as a real structural gap being addressed separately (CROSS_VERIFICATION_"
            "SPEC_v1.0), not a weakness papered over."
        ),
        "changelog_v2_5_3": (
            "Mandate 3.10: four determinations. (1) Lifts D3_block_reset from PRINCIPLE_RATIFIED_COST_"
            "PENDING to full RATIFIED, on VE's real-data blind-window audit (MK-01 Step 2, commit 260c4e3) "
            "of the 3 M15_v2 discovery blocks: bear 0.0305%, bull 0.0170%, correction 0.0396% -- worst "
            "block ~126x below the 5% not-ratified threshold, all three deep in the <=1% low-cost tier. "
            "(2) Corrects market_structure_ratification.corrected_reading from '8 structures' to the "
            "correct '6' (3 discovery blocks x 2 swing types -- the fourth M15_v2 regime segment has no "
            "discovery_range, TOO_SHORT_FULLY_SEALED) -- Statistician's own counting error, not a relayed "
            "misreading, corrected here explicitly. Adds boundary_convention: declares half-open "
            "[start_epoch, end_epoch) as the single mechanical rule for every epoch range in this "
            "manifest, verified by direct bar-recount against data/market/OANDA_XAUUSD_M15.csv (matches "
            "Research Lab's published 52,403/52,851/25,237 exactly; closed-both-ends reproduces VE's "
            "52,404 on bear only) -- resolves the recurring VE-vs-Research-Lab one-bar discrepancy "
            "mechanically, specifies an in_range() function contract for edge_research/split_manifest.py "
            "(not owned by Statistician, not implemented here) so it is never recalculated ad hoc again. "
            "(3) Adds cross_verification_spec_scope_ruling: the spec governs derived DATA artifacts at "
            "risk of sealed-data leakage via manifest-boundary construction, not verification/measurement "
            "CODE reading only through an already-safe discovery mask -- VE's Step 1/Step 2 on MK-01/MK-02 "
            "do not trigger it; explicit limit stated (a persistent, widely-reused verification tool would "
            "change this) so the ruling is not silently widened later. Confirms F1 (absolute import in "
            "liquidity_mechanics.py is consistent with code/'s own no-package convention, not an "
            "exception to it). (4) Registers market_structure_ratification.re_arming_bug_MK02: fix "
            "specification for VE's independently-verified detect_breaks re-arming defect (MK-01/MK-02 "
            "Step 1, commit 6b7948f) -- consumed-set filtered at the candidate-pool level before live_hh/"
            "live_ll assignment, never a downstream nulling; acceptance test = single-HH repro must yield "
            "exactly one break post-patch. Confirms the D3 volume audit remains valid, unaffected by this "
            "bug: mk_d3_volume_audit.py verified (direct read) to import only detect_swings/label_structure, "
            "never detect_breaks -- code-path isolation, not coincidental non-manifestation."
        ),
        "changelog_v2_5_2": (
            "Closes candidate_verdicts.verdicts.E004.fill_rate_note, discovered mid-work merging remote "
            "changes: Flow A executed STATISTICIAN_E004_FILL_CONTROL_SPEC_v1.0.md exactly and mechanically "
            "(commit b4d5f89) -- E004 fill 0.7148 (n=1164) vs. generic-gap control 0.8500 (n=1660), Fisher "
            "exact one-sided p=1.000 (does not reject; E004 fills LESS than control, not more). Control "
            "rate falls in the pre-registered (0.512,0.886) band -> OBSERVED_NOT_DISTINCTIVE, read off the "
            "table fixed before this run, not chosen after seeing the number. Confirms the original "
            "reserve against CONFIRMED_STRUCTURAL_ANOMALY was correct."
        ),
        "changelog_v2_5_1": (
            "Registers market_structure_ratification: 6 of 7 market_structure.py/liquidity_mechanics.py "
            "design decisions ratified (D1 lookahead, D2 tie-break, D4 basin-no-survive-gap, D5 M15_v2-"
            "only scope, D6 current-bar wick-sweep, D7 basin-consumed); D3 (block-boundary reset) ratified "
            "in principle only, cost-acceptability withheld pending a real-data blind-window measurement "
            "(a synthetic 16-bar estimate is explicitly not sufficient) -- a decision threshold (<=1%/1-5%/"
            ">5% of a block's own discovery bar count) specified since none was given. Registers "
            "lm_001_preregistration: a new hypothesis (renamed from the requested 'E001_v2_Wick_Sweep_"
            "Execution' to avoid implying resuscitation of a REJECTED candidate at a narrower "
            "parameterization) with full execution layer, family size, statistical test, pre-registered "
            "success/failure criteria, and an explicit insufficient-N rule (reusing the established n>=25 "
            "convention, TESTABLE BUT INSUFFICIENT EVIDENCE rather than REJECTED on low data)."
        ),
        "changelog_v2_5_0": (
            "Registers legacy_428_atr_persistence_verdicts: granular REJECTED labels for the 428 ATR "
            "hypotheses' three-regime persistence run (367 ZERO_ALPHA_BASE_RATE / 58 REGIME_PERSISTENCE_"
            "FAILURE / 3 EXTREME_CONCENTRATION_FRAGILITY_wo1), each with an explicit scope delimitation "
            "(rejects the tested parameterization on these 3 regimes with this outcome variable, not the "
            "underlying market concepts). Registers deduplication_prescreening_rule (PROJECT_AUDIT.md D11/"
            "SSF): mandatory mechanical pre-screening (trade-log hash identity, not summary-stat matching) "
            "before any future multiple-testing correction, with Research Lab's already-executed results "
            "folded in (1972->1440 distinct, 428->360 distinct). Adds m5_status_note distinguishing M5's "
            "own unchanged status from the separately CANCELLED M5-aligned-HTF-context effort -- two "
            "distinct facts, recorded so neither is later conflated with the other."
        ),
        "changelog_v2_4_2": (
            "Hotfix. Research Lab found a genuine internal self-contradiction: the same v2.4.1 document "
            "asserted, in one changelog, that H1_from_M15_v2 'is NOT registered here... stays in "
            "acquisition_staging/, unregistered' while another changelog said 'Registers H1_from_M15_v2', "
            "and the entry's own file_path pointed at a staging file whose name says UNREGISTERED while "
            "its status read CONTEXT_DERIVED_VALIDATED. Neither Statistician nor CEO verified the "
            "resulting manifest before it was relayed to Research Lab as fact -- the fourth time in one "
            "day a claim taken from a report proved inexact on checking the source. Root cause: two "
            "changelogs describing the same entity from different versions, with nothing checking "
            "consistency between them or against the live entry. Fix, in two steps within this same "
            "version: (1) H1_from_M15_v2 first reverted to status AWAITING_FILE_RELOCATION, file_path "
            "and data_file_sha256 cleared -- the old staging hash 524977d0...f660 explicitly NOT reused "
            "on the (correct) assumption that a move might change file bytes; (2) Data Acquisition then "
            "completed the relocation (commit d99d241, data/market/OANDA_XAUUSD_H1_from_M15_v2.csv, "
            ".gitattributes pinned -text BEFORE the move to prevent a CRLF conversion) and Statistician "
            "re-verified by independently re-hashing the file at its NEW path -- the recomputed hash "
            "turned out byte-identical to the old staging value, confirmed rather than assumed, so the "
            "entry is promoted straight to CONTEXT_DERIVED_VALIDATED with the correct canonical path. "
            "Both prior changelogs kept verbatim, each now carries an explicit *_correction sibling field "
            "marking what is superseded and why, "
            "same treatment as superseded_regime_map_v2_0_0. governance_note_operational_motivation_"
            "disclosed and classification_delimitation are UNCHANGED -- still valid, not affected by the "
            "file-path bug. Added mechanical consistency checks (validate_context_derived_consistency, "
            "run before every write) so this class of error -- an unverified claim propagating through "
            "the manifest -- cannot recur silently: verifies every CONTEXT_DERIVED_VALIDATED entry has a "
            "non-null hash matching a fresh recomputation against its own file_path, and that no such "
            "entry's file_path contains 'acquisition_staging' or 'UNREGISTERED' (the exact pattern that "
            "caused this bug). Mechanical, not by reading -- the second time this project has published "
            "a manifest claim nobody verified (the first was the M15 entry describing the superseded "
            "file)."
        ),
        "changelog_v2_4_1_correction": {
            "status": "PARTIALLY_SUPERSEDED_BY_v2_4_2",
            "reason": (
                "changelog_v2_4_1's H1_from_M15_v2 file_path (acquisition_staging/..._UNREGISTERED.csv) "
                "and hash (524977d0...f660) were the pre-relocation staging file's -- registering them "
                "as file_path/data_file_sha256 on a CONTEXT_DERIVED_VALIDATED entry, while the filename "
                "itself said UNREGISTERED and an earlier changelog (changelog_v2_4_htf_ratification) said "
                "the opposite, was an internal contradiction Research Lab caught by reading the resulting "
                "manifest -- neither Statistician nor CEO verified it beforehand. Everything else in "
                "changelog_v2_4_1 (the commit-citation correction, the CONTEXT_DERIVED_VALIDATED renaming, "
                "the H4/D1 ratification) remains accurate and unchanged. Only the H1_from_M15_v2 file_"
                "path/hash claim is corrected -- see the H1_from_M15_v2 entry above (status "
                "AWAITING_FILE_RELOCATION) and changelog_v2_4_2 below."
            ),
        },
        "changelog_v2_4": (
            "Registers the Mandate 4.1 transactional-evaluation verdicts (Flow A commit 1a64812, "
            "verified directly by Statistician against the source report/script/results, not merely "
            "accepted) under candidate_verdicts: E001/E002/E004 REJECTED -- NEGATIVE_EXPECTANCY_UNDER_"
            "COST at the SS9.4.1 parameterization (stop $4/$5, RR 1:1/1:2) -- winrate below the cost-"
            "adjusted break-even in all 3 regimes tested (bear/bull/correction, 2011-2021; the 2022-2026 "
            "regime is excluded as SAME-WINDOW-RESAMPLED, Statistician's own earlier 4-regime mandate "
            "was in error, corrected here), BH-FDR family of 6 passing none. Scope explicitly delimited: "
            "this rejects the SS9.4.1 stop/RR parameterization, not the underlying ICT concepts -- a "
            "differently-parameterized candidate would need its own full review. E004's fill rate "
            "(0.662-0.736) is registered PENDING_CONTROL, not as CONFIRMED_STRUCTURAL_ANOMALY -- no "
            "denominator exists yet for how often a comparable, non-FVG-selected gap fills over the "
            "same window; a specific control is registered as required before any anomaly label."
        ),
        "changelog_v2_4_htf_ratification": (
            "Also ratifies Data Acquisition's H4/D1_from_M15_v2 generation (Mandate 2.7, commit "
            "774acea, arrived via merge while preparing this version): both data_file_sha256 values "
            "independently recomputed by Statistician directly against the physical files and matched "
            "exactly. H4/D1_from_M15_v2 promoted CONTEXT_DERIVED_VALIDATED (status VALIDATED). Boundary-"
            "compliance (no HTF bar straddles a discovery block edge) relies on Data Acquisition's own "
            "test suite (28/28 passing) rather than an independent re-derivation of the 17:00-America/"
            "New_York DST-aware windowing logic -- disclosed explicitly, not silently assumed. An "
            "H1_from_M15_v2 file was also generated (on separate CEO instruction, per Data Acquisition's "
            "commit) but is NOT registered here -- no mandate has covered its registration; it stays in "
            "acquisition_staging/, unregistered, pending a future decision."
        ),
        "changelog_v2_4_htf_ratification_correction": {
            "status": "SUPERSEDED_IN_FRAMING_BY_LATER_VERSIONS",
            "reason": (
                "This entry's 'H1_from_M15_v2 is NOT registered here' claim was accurate when written "
                "(v2.4.0). v2.4.1 then registered it, but with a stale staging file_path/hash -- itself "
                "corrected in v2.4.2 (see changelog_v2_4_1_correction and changelog_v2_4_2). As of this "
                "version, H1_from_M15_v2 IS a real entry under context_derived_htf.entries, status "
                "AWAITING_FILE_RELOCATION -- read this changelog as a historical snapshot of v2.4.0, not "
                "the current state."
            ),
        },
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
        "candidate_verdicts": {
            "source": "Flow A Mandate 4.1 (commit 1a64812, edge_research/MANDATE41_TRANSACTIONAL_EVAL.md), verified directly by Statistician against the report, evaluation script, and results JSON before this registration.",
            "statistical_test": {
                "method": "exact one-sided binomial (scipy.stats.binom.sf), not a normal approximation",
                "break_even_threshold": "w* = (1 + cost/S) / (RR + 1); cost=0.4, so RR1:1 -> 0.550 at S=4.00 / 0.540 at S=5.00; RR1:2 -> 0.367 at S=4.00 / 0.360 at S=5.00",
                "family": "3 contracts x 2 RR = 6, trial counts pooled across all tested regimes per contract-RR pair before testing (regime is a descriptive robustness breakdown, not a test multiplier)",
                "ratified_in": "ai_quant_lab statistician/STATISTICIAN_EXECUTION_CONTRACT_STRUCTURAL_V1_v1.0.md SS7 (v1.2)",
            },
            "regimes_tested": "3 (bear, bull, correction; 2011-07-26 to 2021-09-03) -- NOT 4. The 2022-2026 regime is M15-legacy territory that informed V1's own parameterization and falls under same_window_resampled_predicate; Statistician's original 4-regime mandate was in error, corrected here per explicit instruction.",
            "verdicts": {
                "E001": {"label": "REJECTED", "reason_code": "NEGATIVE_EXPECTANCY_UNDER_COST",
                          "scope": "Rejects the SS9.4.1 parameterization (stop $4.00/$5.00, RR 1:1/1:2) only -- not the underlying Asia-range sweep-and-reverse concept. A differently-parameterized candidate would be new, requiring its own full review."},
                "E002": {"label": "REJECTED", "reason_code": "NEGATIVE_EXPECTANCY_UNDER_COST",
                          "scope": "Rejects the SS9.4.1 parameterization only -- not the underlying Frankfurt-aggressive-move-reverses-in-London concept."},
                "E004": {"label": "REJECTED", "reason_code": "NEGATIVE_EXPECTANCY_UNDER_COST",
                          "scope": "Rejects the SS9.4.1 parameterization only -- not the underlying FVG follow-through concept.",
                          "fill_rate_note": {
                              "observed_mandate_4_1": {"bear": 0.718, "bull": 0.736, "correction": 0.662},
                              "control_mandate_4_2": {
                                  "source": "Flow A, commit b4d5f89, executing STATISTICIAN_E004_FILL_CONTROL_SPEC_v1.0.md (b02c5a1) exactly, mechanically",
                                  "e004_fill_pooled": 0.7148, "e004_n": 1164,
                                  "control_fill_pooled": 0.8500, "control_n": 1660,
                                  "fisher_exact_one_sided_p": 1.000,
                                  "note": "E004 fills LESS than the generic-gap control (0.7148 vs 0.8500), not more.",
                              },
                              "status": "OBSERVED_NOT_DISTINCTIVE",
                              "status_derivation": (
                                  "Control rate 0.850 falls within the pre-registered (0.512, 0.886) band -> "
                                  "OBSERVED_NOT_DISTINCTIVE, read mechanically off the pre-registered table, not "
                                  "chosen after seeing the result (the table was fixed before this run). Did NOT "
                                  "reach OBSERVED_BELOW_BASELINE (would require control >=0.886) despite the "
                                  "point estimate showing E004 below control -- the pre-registered band, not the "
                                  "raw point estimate, is the deciding rule."
                              ),
                              "reason_for_original_reserve": (
                                  "Gaps in general are known to fill often over a generous horizon on any "
                                  "instrument/timeframe; without a baseline fill rate for a comparable, non-"
                                  "FVG-selected gap over the same 50-bar horizon and regimes, the raw E004 rate "
                                  "could not be distinguished from 'gaps just fill, E004 shows nothing "
                                  "distinctive' -- confirmed correct by the control result itself."
                              ),
                          }},
            },
            "full_verdict_document": "ai_quant_lab statistician/STATISTICIAN_STRUCTURAL_V1_FINAL_VERDICT_v1.0.md",
        },
        "legacy_428_atr_persistence_verdicts": {
            "source": "Research Lab three-regime persistence run (commit 7927441, docs/THREE_REGIME_PERSISTENCE_RESULT_v1.0.md), verified directly by Statistician before this registration -- a descriptive measurement, not a per-hypothesis significance test.",
            "regimes_tested": "3 (bear, bull, correction; 2011-2021, M15_v2 discovery) -- NOT 4. The 2022-2026 regime is excluded as SAME-WINDOW-RESAMPLED, independently confirmed via changelog_v2_4 in this manifest.",
            "counts": {"profitable_in_3_of_3": 3, "profitable_in_2_of_3": 7, "profitable_in_1_of_3": 51, "profitable_in_0_of_3": 367, "total": 428},
            "verdicts": {
                "profitable_in_0_of_3": {"n": 367, "label": "REJECTED", "reason_code": "ZERO_ALPHA_BASE_RATE",
                    "scope": (
                        "Fails the descriptive profitability screen (n>=25, sumR>0, exp>0, pf>1.00) in all 3 "
                        "tested regimes, at this frozen parameterization, with R (ATR-scaled) as the outcome "
                        "variable. Does NOT mean the underlying S1-S51 family/market concept is permanently "
                        "falsified -- a different parameterization, or the same parameterization on untested "
                        "regimes, remains untested by this specific result. Based on a DESCRIPTIVE screen, not "
                        "a per-hypothesis significance test with BH-FDR (unlike the SS7 binomial-tested E001/"
                        "E002/E004 rejections) -- a real but evidentially different-weight finding."
                    )},
                "profitable_in_1_or_2_of_3": {"n": 58, "label": "REJECTED", "reason_code": "REGIME_PERSISTENCE_FAILURE",
                    "scope": (
                        "Profitable in 1 or 2 of 3 regimes but fails the persistence-across-regime-diversity "
                        "bar (profitable in ALL tested regimes). Does not invalidate the regime(s) where it "
                        "was profitable -- that result may be real -- only the claim of regime-general "
                        "robustness."
                    )},
                "profitable_in_3_of_3": {"n": 3, "label": "REJECTED", "reason_code": "EXTREME_CONCENTRATION_FRAGILITY_wo1",
                    "scope": (
                        "Profitable in aggregate across all 3 regimes, but at least one regime's profitability "
                        "is entirely one trade (wo1<=0). Does not invalidate the underlying market mechanism "
                        "(failed breakout fade at PDH/PDL for S2; pw_high rejection for S17) -- rejects the "
                        "claim that CURRENT evidence supports a distributed, robust edge. After deduplication "
                        "(see deduplication_prescreening_rule below), these 3 IDs are 2 distinct strategies: "
                        "S2 (92481423c6b8, duplicate a53441048c3c -- lb inert under ref=pdh_pdl) and S17 "
                        "(f5afb9813f83), both exit=time. S2 is distributed in 2/3 regimes (concentrated only "
                        "in correction, net1=2.80, wo1=-0.031); S17 is distributed in only 1/3 (concentrated "
                        "in BOTH bull, net1=4.96/wo1=-0.037, AND correction, net1=23.9/wo1=-0.064) -- "
                        "structurally more fragile than S2, though both receive the same label since neither "
                        "is distributed across all three regimes."
                    )},
            },
            "full_verdict_document": "ai_quant_lab statistician/STATISTICIAN_LEGACY428_PERSISTENCE_VERDICT_v1.0.md",
            "base_rate_question": (
                "CEO separately asked whether 3 observed all-3-regime persisters vs. 428*p^3=0.08 expected "
                "under naive independence (~37x) warrants a formal correction. Statistician's answer (full "
                "reasoning in the verdict document): almost certainly a dependence artifact from cross-regime "
                "heterogeneity in latent per-strategy quality (thickens the all-regimes-profitable tail even "
                "under a pure null) plus the 428 IDs not being 428 independent units (exact duplicates being "
                "the extreme case, partial correlation from shared entries with different exits being the "
                "pervasive one) -- both push the true expected count up, not down. No formal numeric "
                "correction built now (n=2-3 has ~zero power to distinguish correlation from real edge "
                "regardless of method) -- registered as a standing principle instead: any future formal "
                "regime-persistence significance test at larger scale must use a null model accounting for "
                "both correlation sources, never the naive m*p^k calculation."
            ),
        },
        "deduplication_prescreening_rule": {
            "rule": (
                "Two hypothesis IDs are duplicates iff their realized trade logs (ordered entry_epoch/"
                "exit_epoch/R tuples) are bit-for-bit identical over the same evaluated dataset -- NOT "
                "matching summary statistics (exp/win/pf/n), which can coincidentally match or coincidentally "
                "differ despite identical underlying trades. Mandatory pre-screening BEFORE any future "
                "multiple-testing correction on any hypothesis-ID corpus: family size (m) must be the "
                "deduplicated distinct-strategy count, never the raw ID count."
            ),
            "specified_in": "ai_quant_lab PROJECT_AUDIT.md D11 / SSF (deduplication algorithm: identity criterion, mechanical hash-based detection, canonical-ID retention via lexicographically-lowest tie-break, dual raw/deduplicated reporting requirement)",
            "executed_result": {
                "source": "Research Lab full duplicate audit (commit 80fb243, docs/DUPLICATE_AUDIT_v1.0.md), run against the exact specified criterion via an efficient two-stage implementation (summary-fingerprint pre-filter, trade-log-hash confirmation on candidates)",
                "full_1972_corpus": {"ids": 1972, "distinct_strategies": 1440, "redundant": 532, "redundancy_pct": 27.0},
                "atr_428_corpus": {"ids": 428, "distinct_strategies": 360, "redundant": 68, "redundancy_pct": 15.9},
                "root_cause": "SYSTEMATIC, not accidental -- 87% of clusters (444/508) from lookback (liq_lb/lb) conditionally inert whenever liq_ref != 'swing', a structural code property; smaller config-specific collapses in exit (rr2/rr3), mode (S5), target (S12).",
            },
            "scope_limit": "Catches only exact duplication (correlation=1.0). Does NOT address the pervasive partial-correlation problem from IDs sharing the same entries with different exit rules (the already-documented S18 3-signals-x-2-exits pattern) -- necessary but not sufficient for a fully correct future family size.",
        },
        "m5_status_note": (
            "M5 (native dataset, its own timeframe entry below) is UNCHANGED and stays in the repository -- "
            "its own status (AWAITING_REGIME_MAP) is unaffected by anything in this version. Separately, the "
            "effort to build M5-ALIGNED HTF context (H*_from_M5, block-local on M5's own discovery blocks, "
            "needed for families S7/S9/S11/S15/S20) is CANCELLED (CTO decision) -- not merely blocked or "
            "deferred. M5 itself remains necessary and undeprecated because DC-0008's R variable (the G6 "
            "structural blocker) needs raw M5 data directly, independent of the cancelled HTF-context effort. "
            "These are two distinct facts about two distinct things -- do not conflate M5's own status with "
            "the cancelled context-derivation project."
        ),
        "market_structure_ratification": {
            "source": "CEO Mandate 3.9 -- reference modules market_structure.py/liquidity_mechanics.py, draft, synthetic-data-tested only, not in this repository. Statistician has not read the modules themselves; ratification is against the seven decisions as described.",
            "corrected_reading": "D3 loses 6 structures TOTAL (3 discovery blocks x 2 swing types), not 8 -- the fourth M15_v2 regime segment (2022-10 pre-overlap sliver, 'bull_partial') has no discovery_range at all (TOO_SHORT_FULLY_SEALED) and contributes zero to the discovery set. The prior '8' figure counted a block that is not in discovery; this was Statistician's own counting error, corrected in v2.5.3, not merely a relayed misreading.",
            "decisions": {
                "D1_lookahead": {"status": "RATIFIED", "note": "confirmed_idx=idx+k; breaks use only confirmed_idx<c. No safer construction exists."},
                "D2_tiebreak": {"status": "RATIFIED", "note": "Strict inequality both sides. Mentioned-not-implemented alternative (strict-left/non-strict-right) requires its own synthetic verification before ever replacing this, not a silent swap."},
                "D3_block_reset": {
                    "status": "RATIFIED",
                    "principle_note": "Reset at block boundary, first-per-type UNCLASSIFIED, is the only lookahead-safe construction given the already-established discovery-block quarantine architecture -- no safer alternative to ratify against.",
                    "cost_measurement": "Real-data blind-window audit on the 3 M15_v2 discovery blocks (VE, MK-01 Step 2, commit 260c4e3): bear 16/52,404 discovery bars = 0.0305%; bull 9/52,851 = 0.0170%; correction 10/25,237 = 0.0396%. Worst block (correction) is ~126x below the 5% NOT-ratified threshold and ~26x below the 1% low-cost threshold -- deep in the low-cost tier on all three blocks, no per-block disclosure required.",
                    "decision_threshold_applied": "blind window <=1% of block's discovery bars -> ratified low-cost (all three blocks land here, max 0.0396%).",
                    "status_history": "v2.5.1: PRINCIPLE_RATIFIED_COST_PENDING (synthetic 16-bar estimate explicitly insufficient). v2.5.3: RATIFIED, lifted on the real-data measurement above.",
                },
                "D4_basin_no_survive_gap": {"status": "RATIFIED", "note": "Consistent with D3 -- a basin that cannot exist without a reference that doesn't cross quarantine cannot survive across it either."},
                "D5_no_m5_m15_mapping": {"status": "RATIFIED", "note": "Scopes LM-001 to M15_v2 discovery blocks only -- NOT M5 -- until/unless a working cross-resolution structure mapping exists."},
                "D6_wick_sweep_current_bar": {"status": "RATIFIED", "note": "low[c]<basin AND close[c]>basin (support; symmetric for resistance), entirely on bar c, no lookahead."},
                "D7_basin_consumed": {"status": "RATIFIED", "note": "Matured basin consumed, not re-armed. Mentioned-not-implemented re-arming alternative needs its own verification before ever replacing this, same discipline as D2."},
            },
            "full_ratification_document": "ai_quant_lab statistician/STATISTICIAN_D3_FULL_RATIFICATION_AND_GOVERNANCE_v1.0.md (supersedes the D3/count sections of STATISTICIAN_MARKET_STRUCTURE_RATIFICATION_AND_PREREG_v1.0.md; that document's other six decisions D1/D2/D4-D7 stand unchanged)",
            "re_arming_bug_MK02": {
                "found_by": "Validation Engine, MK-01/MK-02 Step 1 (commit 6b7948f) -- verified independently by Statistician, not merely accepted.",
                "defect": "detect_breaks's activation loop re-assigns live_hh/live_ll at every bar without excluding already-consumed swings, contradicting its own docstring ('a swing is consumed by the first break, never reused'). Reproduction: a single HH produces multiple BOS_BULL breaks (VE: 3, referencing idx6; CEO's independent repro: 4, referencing idx7) all pointing at the same already-broken swing, instead of exactly one.",
                "fix_rule": "Maintain an explicit consumed set/flag on the Swing record itself (not merely nulling a downstream live_hh/live_ll pointer). A swing enters the consumed set the instant a break is recorded against it. The activation loop must FILTER the candidate pool to exclude consumed swings BEFORE selecting/assigning live_hh/live_ll -- filtering happens at the pool/index level, upstream of assignment, never as a downstream nulling that the next iteration can silently overwrite. A consumed swing never re-enters the active pool for the remainder of its block (consistent with D3/D4 -- it does not survive a block boundary anyway).",
                "acceptance_test": "Re-run the existing single-HH synthetic reproduction after the patch: must show exactly one break referencing that swing, never more.",
                "volume_audit_validity": "D3's real-data volume audit (MK-01 Step 2, commit 260c4e3) remains VALID and is NOT redone by this bug. Verified directly: code/mk_d3_volume_audit.py imports only detect_swings and label_structure from market_structure -- detect_breaks (where the defect lives) is never imported or called on that code path. This is code-path isolation, not coincidental non-manifestation.",
            },
        },
        "boundary_convention": {
            "rule": "All epoch ranges in this manifest (discovery_range, intra_segment_embargo, sealed_range, and any other {start_epoch, end_epoch} pair) are HALF-OPEN: a bar at epoch t belongs to the range iff start_epoch <= t < end_epoch.",
            "verification": "Directly recomputed bar counts for all three M15_v2 regime discovery blocks from data/market/OANDA_XAUUSD_M15.csv using the manifest's own discovery_range epochs. Half-open gives bear=52,403 / bull=52,851 / correction=25,237, exactly matching Research Lab's already-published, invariant-checked figures (sum 130,491). Closed-both-ends gives bear=52,404 (matching VE's independent count) with bull/correction unchanged -- confirming the recurring one-bar discrepancies (VE vs Research Lab on this block; historically Set A 67,321 vs 67,322 and Set B 16,830 vs 16,831) are half-open-vs-closed ambiguity, not a data error.",
            "why_half_open_is_correct": "Adjacent sub-ranges within a segment (discovery_range -> intra_segment_embargo -> sealed_range) share boundary epochs. Only half-open partitions them cleanly, with no bar double-counted at a shared boundary and no gap.",
            "shared_function_contract": "Specified for edge_research/split_manifest.py (the shared reader module; Statistician does not own this file and does not implement it there): def in_range(epoch: int, range_dict: dict) -> bool: return range_dict['start_epoch'] <= epoch < range_dict['end_epoch']. Every division counting bars within a manifest range calls this rather than reimplementing the inequality -- the convention is declared once, mechanically, and is not to be recalculated or re-litigated per discrepancy.",
            "not_retroactively_resolved": "Set A (67,321 vs 67,322) and Set B (16,830 vs 16,831) are from an earlier pipeline already closed through discussion at the time; not reopened. This rule governs all ranges in this manifest going forward.",
        },
        "cross_verification_spec_scope_ruling": {
            "question": "Does CROSS_VERIFICATION_SPEC (containment / aggregation correspondence / non-overlap / negative completeness / absence of orphans) apply to verification/measurement CODE, or only to derived DATA artifacts? Concrete tension: under Path A, Validation Engine both writes the tests and runs the Step 2 volume-audit measurement on its own test/measurement code, with no independent third-party check of that code.",
            "ruling": "CROSS_VERIFICATION_SPEC applies to derived DATA ARTIFACTS at risk of silent sealed-data leakage via incorrect manifest-boundary construction (its five properties are all about verifying an HTF-resampled bar against the manifest's discovery-block boundaries). It does NOT generically apply to verification/measurement code that only reads through an already-established, mechanically-safe discovery_range mask -- such code cannot leak sealed data by construction, regardless of who wrote it. VE's Step 1 (independent test-writing against Architect's/CEO's modules) and Step 2 (volume-audit measurement, confirmed to read only through the manifest's own discovery mask) do not trigger the spec; no third-party formal re-run of the five properties is required.",
            "explicit_limit": "This ruling does not extend to code in general. If VE's test/measurement code is ever reused as a PERSISTENT artifact that other divisions rely on for OTHER hypotheses (not this one-time D3 diagnostic), the calculus changes -- a repeatedly-relied-upon verification tool warrants independent review even though it is not itself an HTF-resampled data artifact. Written explicitly so this scope is not reinterpreted or widened later without re-deciding it.",
            "f1_absolute_import_confirmed": "Separately confirmed (not by analogy): liquidity_mechanics.py's absolute import of market_structure is consistent with code/'s actual convention -- code/ has no __init__.py and all of its modules (including mstrat.py's 'from alpha_lab import CFG') import absolutely. Statistician's earlier premise ('the rest of the repo uses packages + relative imports') held only for validation_engine/ve/, not for code/. VE's finding stands as correctly nuanced.",
        },
        "lm_001_preregistration": {
            "name": "LM-001 (Liquidity Basin Wick-Sweep-Reject)",
            "naming_note": (
                "CEO's mandate requested 'E001_v2_Wick_Sweep_Execution'; Statistician objected to the name, "
                "not the hypothesis. E001 was REJECTED at its specific parameterization (Asia-range sweep, "
                "London-open reversal, hourly window, session clause) -- a generic any-basin/any-session/no-"
                "window wick-sweep detector is structurally broader, not a revision. Naming it _v2 would "
                "misleadingly suggest resuscitation of a rejected candidate. LM (liquidity mechanics) is a "
                "new namespace, outside the already-claimed E0xx (all 40 original V0s) and S0xx (S1-S51) "
                "spaces. The conceptual kinship to E001 (shared sweep-and-reject mechanism) is recorded as "
                "PROVENANCE, not version."
            ),
            "scope": "M15_v2 discovery blocks only (D5), excluding the 2022-2026 regime as SAME-WINDOW-RESAMPLED, same 3 regimes as the SS9.4.1 structural contracts.",
            "execution_layer": {
                "entry": "next-bar-open after the maturation (wick-sweep) bar, direction determined mechanically by basin type (support matured -> long, resistance matured -> short) -- not a free choice, does not multiply the family.",
                "stop_official": 4.00, "stop_sensitivity": 5.00, "cost_round_trip": 0.40,
                "targets": {
                    "stop_4.00": {"RR_1.5": 6.00, "RR_2.0": 8.00},
                    "stop_5.00": {"RR_1.5": 7.50, "RR_2.0": 10.00},
                },
                "break_even_thresholds": {
                    "formula": "w* = (1 + cost/S) / (RR + 1)",
                    "stop_4.00": {"RR_1.5": 0.44, "RR_2.0": 0.3667},
                    "stop_5.00": {"RR_1.5": 0.432, "RR_2.0": 0.36},
                },
                "tie_break": "worst-case (stop-first) default, mandatory worst/best bracket per STATISTICIAN_M5_INDETERMINACY_THRESHOLD_SPEC_v1.0.md SS7c for any combination whose status depends on treatment.",
            },
            "family": "2 members (1 detector x 2 RR); direction is mechanical, not a free parameter, so it does not multiply the family; the 5.00 stop is a sensitivity variant, not a third family member.",
            "statistical_test": "Exact one-sided binomial (ratified SS7), pooled trial counts across the 3 tested regimes per RR member, BH-FDR at alpha=0.05 over the family of 2.",
            "success_failure_criteria_preregistered": {
                "success": "Passes BH-FDR at alpha=0.05 over the family of 2, on pooled counts across ELIGIBLE regimes (see insufficient_n_rule).",
                "failure": "Does not pass BH-FDR, PROVIDED at least one regime had sufficient n -- a failure on insufficient data is a different category, not a statistical failure.",
            },
            "insufficient_n_rule": (
                "Reused convention: n>=25 (Discovery Screen V1 / persistence-leaderboard threshold), not a "
                "new number. Per-regime: <25 qualifying events -> that regime marked INSUFFICIENT_N for this "
                "hypothesis, EXCLUDED from the pooled count (never treated as zero or as failure), fraction "
                "disclosed explicitly. Pooled: if total n across eligible regimes stays <25 after exclusions, "
                "the whole RR member's verdict is TESTABLE BUT INSUFFICIENT EVIDENCE (established vocabulary, "
                "e.g. DC-0004) -- NOT REJECTED. If both RR members land here, the whole LM-001 line gets this "
                "verdict, with the D3 blind window recorded explicitly as the likely primary cause, not hidden."
            ),
            "workflow_confirmed": "Validation Engine implements after this ratification; a different division (not the producer) verifies conformance per CROSS_VERIFICATION_SPEC; execution on real data awaits both -- not triggered by this registration. D3's cost measurement is a separate precondition, not gated by this workflow but not yet satisfied either.",
            "full_preregistration_document": "ai_quant_lab statistician/STATISTICIAN_MARKET_STRUCTURE_RATIFICATION_AND_PREREG_v1.0.md",
        },
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


class ManifestConsistencyError(ValueError):
    """Raised when context_derived_htf entries are internally inconsistent -- never written to disk."""


def validate_context_derived_consistency(manifest: dict[str, Any]) -> None:
    """Mechanical checks, not by reading. Added after a real incident: v2.4.1 registered
    H1_from_M15_v2 as CONTEXT_DERIVED_VALIDATED with a staging/UNREGISTERED file_path while a
    changelog said the opposite -- nobody verified the generated file before it was relayed as
    fact. This function makes that specific class of error impossible to publish silently again.
    """
    entries = manifest["context_derived_htf"]["entries"]
    for key, entry in entries.items():
        status = entry.get("status")
        file_path = entry.get("file_path")
        sha_block = entry.get("data_file_sha256", {})
        if status == "CONTEXT_DERIVED_VALIDATED":
            if not file_path:
                raise ManifestConsistencyError(
                    f"{key}: status is CONTEXT_DERIVED_VALIDATED but file_path is missing/null."
                )
            lowered = file_path.lower()
            if "acquisition_staging" in lowered or "unregistered" in lowered:
                raise ManifestConsistencyError(
                    f"{key}: status is CONTEXT_DERIVED_VALIDATED but file_path ({file_path}) looks like "
                    "a staging/unregistered path -- the exact pattern that caused the v2.4.1 incident."
                )
            stored_hash = sha_block.get("value")
            if not stored_hash:
                raise ManifestConsistencyError(
                    f"{key}: status is CONTEXT_DERIVED_VALIDATED but data_file_sha256.value is missing/null."
                )
            recomputed = sha256_file(os.path.join(_ROOT, file_path))
            if recomputed != stored_hash:
                raise ManifestConsistencyError(
                    f"{key}: stored hash {stored_hash} does not match a fresh recomputation "
                    f"{recomputed} against {file_path} -- file changed since the hash was recorded, or "
                    "the hash was never real."
                )
        else:
            # Not validated: file_path/hash MAY be present as pending-relocation metadata, but must
            # never masquerade as ready -- no live consumer should read a hash off a non-validated entry.
            if sha_block.get("status") == "CONFIRMED_BY_STATISTICIAN" and status != "CONTEXT_DERIVED_VALIDATED":
                raise ManifestConsistencyError(
                    f"{key}: data_file_sha256.status is CONFIRMED_BY_STATISTICIAN but entry status is "
                    f"'{status}', not CONTEXT_DERIVED_VALIDATED -- a confirmed hash implies the entry "
                    "should be validated; if it isn't, either promote it or downgrade the hash status."
                )


def main() -> None:
    manifest = build_manifest()
    validate_context_derived_consistency(manifest)
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
