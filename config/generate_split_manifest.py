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
            {"version": "2.5.3", "commit": "a0295d8", "content": "Mandate 3.10: lifts D3_block_reset to full RATIFIED on VE's real-data blind-window audit (MK-01 Step 2, commit 260c4e3 -- bear 0.0305%/bull 0.0170%/correction 0.0396%, all far below the 1% low-cost threshold); corrects Statistician's own '8 structures' count to the correct '6' (3 discovery blocks x 2 swing types -- the fourth M15_v2 segment has no discovery_range); declares the half-open [start_epoch,end_epoch) boundary_convention as a single mechanical rule (resolves the recurring VE-vs-Research-Lab one-bar discrepancy, verified directly against OANDA_XAUUSD_M15.csv); rules CROSS_VERIFICATION_SPEC scope (applies to derived data artifacts, not generically to verification/measurement code reading only through an already-safe discovery mask -- explicit limit stated); registers the re_arming_bug_MK02 fix specification (found by VE, MK-01/MK-02 Step 1 commit 6b7948f) and confirms the D3 volume audit remains valid (mk_d3_volume_audit.py never imports detect_breaks, verified directly)"},
            {"version": "2.5.4", "commit": "04c096e", "content": "Mandate 5.1/5.2: registers LM-001's real-data geometry audit (VE, commit f901e3f, N=34,670 valid wick-sweeps, 86.7% of displacements <40 pips) and the resulting risk-framework decision (STAT-LM001-RISK-FRAMEWORK-DECISION-v1.0) -- SUPERSEDES the fixed stop_official=4.00/stop_sensitivity=5.00 execution layer: R is now geometry-derived per trade (never widened, same D2 anti-pattern at 8x scale if it were); a displacement_filter (>=10.1 pips, excludes 34.0% aggregate) derived from the lab's already-existing 3x cost-stress convention (alpha_lab.py:197), not chosen from reference points; a rejection_ceiling (>=65 pips, tail-only, CONFIRMED not re-derived) stays as originally proposed; statistical_test replaces the fixed-w*-vs-binomial-winrate test with mean net_R>0 (a single win-rate threshold cannot exist when R varies continuously per trade). Also confirms D-BPR's three-tolerance count + freeze-rule (VE's skeleton, commit 306d1dc) is NOT overridden, and reconfirms D3_bis/D-WEEK unchanged."},
            {"version": "2.5.5", "commit": "1d03e4f", "content": "Mandate 3.13: formulates LM-001's testable hypothesis against the 40-V0 5-criteria standard. Corrects the order's stated population (22,887) to the true combined-filter figure (21,048, 60.7% of 34,670) -- 22,887 was the displacement floor alone, never reduced by the 1,839 events also excluded by the 65-pip ceiling. Derives the decisive horizon (20 M15 bars) from the correct comparison family (_profile.HORIZONS, immediate-reaction, not TRACK_HORIZON/REVISIT_HORIZON's multi-day level-revisit family) linked to an already-real boundary (london session length, mtf.py:37-38); secondary horizons (1,3,5,10,50) reused verbatim, descriptive only, family stays 1. Declares no take-profit (pure time-exit). Discloses exit=time's 1.6x concentration vs exit=rr2 (OUTCOME_DISTRIBUTION_v1.0.md, 0.628 vs 0.387) as a mandatory accompanying diagnostic, not a blocker. Declines to confirm block_bootstrap@v1 (still textually UNVALIDATED, n=21,048 far beyond its calibrated range) or substitute matched_null@v1 (ATR-scaled-only, wrong regime per D2_CLOSURE_SIZING_v1.0.md) -- specifies a due-diligence calibration extension instead, with a pre-registered acceptance band and a named (not invented) structural-calibration fallback (WP-5')."},
            {"version": "2.5.6", "commit": "00dfa6f", "content": "Mandate 3.14: resolves all nine open questions from the MK-03/MK-04 partial implementation (VE, commit 7984670). Family 1 (Q5 MK-03/MK-04): D7-consumption confirmed, but rejects an added 'session/day' lifetime clause not present in D7 -- PDH consumed at first same-day touch, no new dimension. Family 2 (Q6/Q4 MK-03): wick/close asymmetry now grounded in direct code precedent (e015's wick touch_mask for mitigation, e010/e012's close-based violation for polarity flips) -- 3-tier gradient specified (CE-50 touch / full fill / inversion). Family 3: FVGs don't survive a block boundary (D4-analog); Q3-week derived from the already-resolved Q3-day via a gap-detection rule, not a new clock. Resolves MK-03 Q4 (IFVG inversion, the only fully-blocking primitive) by reusing verbatim an identical definition independently found in two already-frozen V0s (E010, E012). Ratifies the three small mechanically-forced items (MK-03 Q1, MK-04 Q4, reconfirms MK-04 Q3-day)."},
            {"version": "2.5.7", "commit": "9c02af7", "content": "Mandate 3.17: block_bootstrap@v1 verdict INVALIDATED_FOR_THIS_SCALE for LM-001 (measured S8 curve nominal through phi=0.50, anti-conservative at phi=0.60, e441bcf) -- declines to map density (8.64 avg concurrent, e441bcf) onto the AR(1) curve, both because the derive-before-seeing-the-result ordering was violated (disclosed) and because the AR(1) parametrization is structurally the wrong instrument for LM-001's finite-memory overlapping-window dependency (a 28-bar block fully contains a 20-bar true dependency window, unlike any AR(1)). Closes the (0.50,0.55] threshold gap via fail_closed_default. WP-5' concretely sized: rebuild the null generator to match the true overlap mechanism, reusing the existing S8 FPR-measurement harness. MK-03/MK-04 FULLY RATIFIED at commit 1930467 after a full (not just report) code read -- 34 tests verified, mypy --strict clean. Registers the SMC_S1/S2/S3/S13/S16 nomenclature under a rigid protected prefix (verified collision against the legacy grammar, including two production strategy_runtime files), connects them to the Open-R risk framework, and mandates D11/SS F dedup pre-screening before enrollment."},
            {"version": "2.5.8", "commit": "74de879", "content": "Mandate 3.18: formalizes all 20 SMC_S* families (verified in code/mstrat.py's ECON dict -- S1-S20 is the legacy grammar's full family list). Flags that validation_engine/capabilities.json is the wrong registration target (its own deliberately_absent field excludes hypothesis-specific event primitives by design) -- registers here instead. Closes the horizon arithmetic gap (20 families, 4 session constants) via 4 declared groups: A=20 bars (LM-001's own immediate-reaction derivation, reused), B=native session length (asia/ny=32, london=20, late=12, from mtf.py), C=empirical day/week length independently computed (day=92, week=460 bars, median, matching institutional_levels.py's own '92 is not a constant' caveat), D=no horizon forced where the primitive itself is missing. 9 families fully state-machine-specified on only the 4 ratified modules (SMC_S1=LM-001, S2, S3, S7, S10 with a disclosed substitution, S11, S13, S16, S17). 11 honestly flagged as not forced: 3 cheap gaps (S5/S6/S19, near-trivial missing extensions), 6 genuine primitive-class gaps (S4/S8/S9/S14/S15/S20), 1 partial gap (S12), 1 reclassified as a stratification dimension not a standalone family (S18). Flags conceptual dedup-collision risk pairs for mandatory hash verification once code exists, declines to report a distinct-family count before trade logs exist. All formalized families AWAITING_VALIDATION_ENGINE_CODE; none promoted to VALIDATED until WP-5' delivers the oracle."},
            {"version": "2.5.9", "commit": "444e0e8", "content": "Mandate 3.19: Q1 (fully blocks WP-5's sample_event_positions) resolved -- reproduce the FULL empirical spacing/degree distribution, not just the mean, to avoid hiding regime-dependent behavior (the same failure mode that partially sank the AR(1) battery). Q2-Q6 resolved: fixed segment allocation + excluded boundary windows; session-stratified not aggregate-only density; 69% shared-horizon as a derived consequence not an imposed invariant; empirical (not normal) iid shocks; shock-sum aggregation scoped explicitly to FPR calibration only. L stays variable downstream. Ratifies Definition 1 (LiquiditySweep=D6, confirmation not new) and Definition 4 (PDH/PDL/Weekly=already-ratified detect_level_touches) unchanged. Derives Definition 3 (LiquidityVoid) as a hybrid temporal-OR-size criterion ($1.20, 3x cost-stress, reused derivation logic) after empirically proving neither criterion alone covers the intended concept (248 size-only vs 119 time-only qualifying transitions, verified on the actual 84,152-bar tested dataset). Fixes Definition 2 (Order Block/Breaker)'s zone contradiction (body [Close,Open], not body+wick) and specifies a validity-window/measurement-window separation before implementation to pre-empt E010's exact circularity defect. Scopes missing primitives to only the actually-blocked SMC_S* families: Range (S12, resolved via recomposition, upgraded to formalized) and MTF-Trend (S9/S20, resolved via recomposition of already-validated H1/H4/D1_from_M15_v2 context) need no new primitive; Volatility/Expansion (S4/S8) gets its measure defined (reusing the lab's official E000 Parkinson standard) with the threshold deferred to its own derivation; S14/S15 remain genuinely gapped (no primitive in either given module); S5/S6/S19 confirmed as a cheap Module-4 extension, not Module 5/6. Order Block/Breaker/Mitigation/Rejection and Compression confirmed NOT needed by any blocked family, not constructed."},
            {"version": "2.6.0", "commit": "4c9c20f", "content": "Mandate 3.20: block_bootstrap@v1 ratified VALIDATED for the finite-memory overlap mechanism (n~21,048, L>=H=20 -- VE's pre-registered prediction confirmed exactly: FPR@0.05 nominal at L=10/20/28/40, 0.0450/0.0400/0.0400/0.0400), scoped as an explicit field coexisting with the unchanged AR(1)-regime INVALIDATED_FOR_THIS_SCALE verdict -- two regimes, two verdicts, no ambiguity. Reconciles the Q4 spacing-metric discrepancy (not just flags it): traces the exact mechanical cause of 6.2-vs-8.52 bars (same-bar duplicate events inflate the naive bars/events ratio; the corrected figure excludes zero-length gaps between co-located events, verified directly: only 15,305 of 21,045 possible gaps are nonzero) and declares 8.52 bars/57.4% the new authoritative figure, superseding 6.2/69%, with the scope of the correction stated explicitly (does not affect the session-derived 20-bar horizon or the exact-position-conditioned FPR results). Confirms the Void-discrepancy resolution and the still-open, non-blocking OB-formation criterion. Confirms Q5's real-return shocks as calibration input (same category as the geometry/density audits) with an explicit written boundary. Rules that code/order_block_void.py TRIGGERS the CROSS_VERIFICATION_SPEC persistent-artifact exception flagged at Mandate 3.10 (VE both designed and implemented it, unlike D1-D7's Architect/VE cross-check) -- requires independent test verification by a different division before any hypothesis relies on it. UNBLOCKS LM-001: frozen v2.5.5 spec confirmed unchanged, execution assigned to Validation Engine (not Flow A), holdout confirmed untouched, the other 11 not-yet-formalized SMC_S* families explicitly deferred per instruction until LM-001's end-to-end run reports back."},
            {"version": "2.6.1", "commit": "2fb948f", "content": "Mandate 3.21: resolves 4 chosen-not-derived parameters and Module 7's nature before CTO's Module 5/6/7 implementation proceeds. Volume filter for Order Block ELIMINATED from the core primitive (not included-with-caveat) -- unlike E022/E031's per-hypothesis caveat, baking an unconfirmed-provenance data dependency into a persistent foundational primitive would propagate the risk silently to every future consumer. Expansion threshold RESOLVED by reusing E010's already-frozen displacement-bar criterion verbatim (range>1.5x ATR14[i-1] AND body>=0.5x range) -- rejects the ungrounded 2.5x and a naive REACTION_THRESHOLD=1.0 substitution (wrong category of measurement). Compression's lookahead risk RESOLVED via a rolling, strictly causal 460-bar window (the empirical median week length already derived at Mandate 3.18/3.19, reused verbatim) -- the same window closes the threshold Mandate 3.19 deferred for SMC_S4/S8's Volatility/Expansion measure. Sessions CORRECTED -- no 'Cash' session exists (confirmed exactly 4: asia/london/ny/late); use 'london'/'ny'. Module 7 RULED a generic parametrizable confluence locator, not a hardcoded hypothesis -- the given example lacks all 5 pre-registration criteria and is not formalized as one; any specific combination wanting to become its own hypothesis needs full separate pre-registration. Anchoring question answered per-primitive: Trend/Volatility/Session are already anchored to concrete blocked families; three of Module 5's four named primitives (Breaker/Mitigation/Rejection) turn out to already be fully defined via reuse of already-ratified mechanics, not new abstractions; only Compression and the still-open OB formation criterion remain genuinely unanchored, accepted as abstract definitions with the risk explicitly disclosed. LM-001 remains blocked by the CTO's library-first sequencing, not by any statistical issue -- oracle ratification and VE execution assignment stand unchanged. Holdout SEALED."},
            {"version": "2.7.6", "commit": "1c0c272", "content": "SMC_S1 (=LM-001) real-data verdict: REJECTED_NET_OF_COST (new scoped sub-label, distinguishing a mechanically-demonstrated positive gross edge smaller than execution cost from 'no edge at all'). Statistician independently re-ran code/lm001_s1_execution.py (commit 0702958) and reproduced all figures exactly: n=9,247/7,181/4,614 (=21,042=21,048-6 excluded at horizon boundary), expectancy -0.1677/-0.1845/-0.2234 R, p_wp5 1.0/1.0/0.996. Verified mechanically (not chosen): best trade is 1.29% of total absolute loss (cost drag, not concentration), and net+cost=gross holds exactly at all three regimes (+0.072/+0.055/+0.017 R gross, monotonically decreasing). Oracle domain (block_bootstrap calibrated on horizon-sums, applied to net_R) CONFIRMED PARTIALLY: overlap mechanism transfers, but the battery's homogeneous-variance assumption was not tested against net_R's real heteroskedasticity -- doesn't change today's overwhelming non-rejection (any residual bias would work in the safer direction), and the per-regime n's fall within the range the same battery already validated via session stratification; states a standing asymmetric rule that a FUTURE positive result from this pipeline would need the gap closed first. SMC_S13 premise corrected: the order's 'exploit the 85% generic fill rate' is backwards -- E004 (same FVG-fill construct) already established 85% as baseline (OBSERVED_NOT_DISTINCTIVE) and E004's own gaps fill LESS often than that baseline (71.48%, z~8.75). Reformulates SMC_S13 as an execution-economics hypothesis only (does NOT claim above-baseline fill rates), fixing two technical problems: next-open market entry (not a CE-50 limit order, eliminating M15 fill-ambiguity, consistent with every other Open-R family) and reconfirming the 20-bar Group-A horizon (the implemented 12 bars was an error applying Group B's rule to a point-event family). Notes SMC_S10's concept-reloop (Research Lab: 'BOS-as-displacement decouples magnitude from structure') as acknowledged, explicitly deferred."},
            {"version": "2.7.18", "commit": "PENDING (this version)", "content": "Mandate 3.32: fixes family size and ordering for a ten-zone-type survey before any measurement, nothing authorized to run. Verified all ten cited primitives exist exactly as claimed (Order Block, Breaker, Demand/Supply, FVG, CE-50, IFVG, BPR, Liquidity Void, PDH/PDL, PWH/PWL), zero new code needed for any, and confirmed Session Open as a level has zero occurrences anywhere in code. Distinguishes two family questions: the descriptive MAE/MFE measurement itself does not consume family for any of the ten types (same reasoning as the touch funnel and Measurement A'), but fixes family=10 now for any eventual formal hypothesis arising from this survey regardless of how many types look promising descriptively -- the actual guard against the 1972-hypothesis-campaign trap, since it corrects for how many candidates were surveyed, not how many survived first impressions. Notes the OB x DemandZone result already in hand from OBDZ-001/002 counts as element 1 of the ten, not a fresh re-measurement. Confirms the three-wave ordering with explicit structural justification (wave 1: eight interval-based zone types; wave 2: PDH/PDL and PWH/PWL split out because single-price levels have genuinely different touch/mitigation semantics; wave 3: three new primitives, gated on waves 1-2 showing promise). Verifies in code that detect_mitigations/detect_rejections are reaction-event detectors bound to an already-existing OrderBlock, not standalone zone-forming primitives -- concludes Mitigation Block/Rejection Block are not the same thing renamed, but their intended definition needs CEO's clarification before specification. Reaffirms the pending paired test remains the priority."},
            {"version": "2.7.17", "commit": "81eeb7b", "content": "Mandate 3.31: frequency-constraint addendum, does not relax anything or choose a lever. Verifies CEO's ~5-trades/week gap directly against manifest discovery-block durations, confirming roughly 2.1-2.2/week aggregate (about half the target), with a minor refinement to the correction-regime rate (2.77/wk from the exact 1.068y duration, not 3.0/wk from an assumed flat 1.0y). Confirms CEO's own self-correction that the population funnel mixes units across its three steps (bars, zones, trigger-events -- no valid survival rate between them) is accurate, and independently verifies this specific unit-mixing claim was never made in any Statistician document (CEO's own prior error, not Statistician's). Specifies a new, cheap, read-only, consistent-unit (zone-level) touch funnel -- zones ever touched, of those how many have a cross-candle unmitigated OB overlapping at first touch, of those how many have aligned bias, reported by polarity as well as regime -- requested to run NOW in parallel with the still-pending paired test, since it relaxes nothing. Frames, without selecting, three possible frequency levers: H4-only bias (specifies re-measuring whether the effect survives a relaxed bias condition or whether dual alignment is itself part of the mechanism); additional zone types (each to be measured entirely separately, never pooled); and M15-native zones (explicitly flagged as reversing a deliberate original design choice, not a neutral option). States plainly that frequency remains undecided pending the paired test's verdict, and that a rare-but-confirmed edge is a legitimate outcome if no lever preserves the effect while raising frequency."},
            {"version": "2.7.16", "commit": "37b48ee", "content": "Mandate 3.30: reads the corrected 3-arm grid VE delivered (code/obdz_three_arm_windows.py, commit d869177) after independently re-running it and reproducing every cited figure exactly (100% A-to-C match; MFE median at [+2,+5] A=0.97/B=0.81/C=0.76 aggregate, a 28% zone-over-pullback gap, with bull/correction individually clearing the pre-registered 25% threshold and bear falling short at 13% though directionally consistent; the effect narrows somewhat at [+2,+10]). Declares the result a descriptive OBSERVATION, not yet a validated finding, per explicit instruction. Raises and answers a new oracle-domain question: block_bootstrap@v1 was calibrated for a single overlapping-window net_R series, not the matched 1:1 paired A-vs-C comparison actually needed here -- recommends a paired test on the per-pair MFE difference, reusing the block-bootstrap resampling mechanics (not its net_R calibration) alongside a plain iid bootstrap as a sensitivity check, not yet executed. Independently checked CEO's own stated premise for the demand/supply asymmetry (bear=100% supply, bull/correction=100% demand) and found it FALSE -- all three regimes are actually mixed-polarity (37-46% minority class each) -- resolving the open polarity-vs-regime question directly from existing data via re-stratification by direction, no contra-trend collection needed. Specifies the ordering if the paired test confirms: paired test and polarity re-stratification in parallel (gating), then MAE-derived SL/TP, then a separate confirmed-entry re-measurement for the confirmation variant, then the still-held H1/H4 count last. Does not authorize formulating OBDZ-002."},
            {"version": "2.7.15", "commit": "9b4af52", "content": "Mandate 3.29: corrects two design errors CEO found in the prior MAE/MFE measurement, both Statistician's own, not VE execution errors. Independently re-ran obdz_mae_mfe_control.py (commit b233c83), confirming median bar_MAE/bar_MFE of 32-45 bars (second-trading-day moves, not immediate reaction) and near-indistinguishable zone-vs-control results on the 92-bar window. Error 1: the 92-bar window was reused verbatim from an unrelated compression-measure derivation and mechanically cannot see any reaction-specific information; corrects to four windows starting at entry+1 ([+2,+3]/[+2,+5]/[+2,+10]/[+2,+20] in touch-relative notation), with [+2,+5]/[+2,+10] as the primary decisive read; keeps the 92-bar result but relabels it explicitly as a general volatility reference, not a reaction measure. Error 2: the existing bias-matched control conflates the zone's contribution with the simple fact that zone entries are always at a pullback; specifies a third arm (pullback-without-zone) using the already-established market_structure Swing/StructureLabel primitive to define pullback depth mechanically (reused from SMC_S1_v2's Measurement A, not invented), matched to each zone trigger within a disclosed tolerance, with unmatched triggers reported not dropped. Specifies a pre-registered interpretation grid (pullback-matters-zone-doesn't / zone-adds-beyond-pullback / neither-matters / mixed) with disclosed 15%/25% thresholds. Confirms the OBDZ verdict remains deferred and the H1/H4 population count stays held pending this corrected measurement."},
            {"version": "2.7.14", "commit": "5dd3825", "content": "Mandate 3.28: corrects the Diagnostic A' verdict, specifies the MAE/MFE+randomized-control measurement, and frames (without numerically specifying) the confirmation-based OBDZ-002 hypothesis. Independently re-ran obdz_sltp_diagnostic.py (commit 465eb38), reproducing every cited figure exactly (MAE p50=4.4x ATR vs the 0.7 anchor, a 6.3x ratio; timeout fractions 0.96-0.99 at p75/p90; TP1->TP2 conversion 0.0/None at wide candidates; best_over_sumR=9.64 at correction p90; literal mechanical verdict MERITA IPOTEZA NOUA). Invalidates that literal verdict: at the wide candidates TP1/TP2 are essentially unreachable and 95.6-98.9% of trades resolve only via the fixed 20-bar timeout, meaning the diagnostic degenerated into a drift measurement rather than testing the SL/TP ratio -- a specification gap Statistician owns, not a VE error (VE flagged all three limitations unprompted and correctly declined to patch by widening the horizon). Notes the one candidate still structurally testing the ratio (p25) fails the pre-registered 2-of-3-regimes threshold anyway. Reclassifies to TESTABLE BUT INSUFFICIENT EVIDENCE for the ratio question; declines to formulate OBDZ-002 from this trigger. Specifies a randomized bias-aligned control (matched count, same direction convention, no ATR floor, fixed seed) to test whether MAE=4.4x ATR is a zone property or a market property, directly paralleling the E004 fill-rate control precedent. Specifies MAE+MFE+bar-of-touch measurement applied to both the actual triggers and the control, with three named interpretation patterns (early-MAE-late-MFE supporting a timing fix; MAE-dominant-MFE-small meaning the zone doesn't predict; simultaneous-comparable meaning generic volatility only). Confirms Variant 3 (engulfing+magnitude confirmation) requires zero new primitives (the already-ratified OB formation criterion, reused as a post-entry confirmation gate) and specifies its structural mechanic without numeric parameters; confirms Variants 1 (pinbar) and 2 (inside bar) require new geometry via exhaustive code search and holds them per CEO's own suggestion pending Variant 3's result. Confirms the H1/H4 detector wiring gap is real (never run on those timeframes) and requires a population-count-only script there before any new state-machine build, flagging a real INSUFFICIENT_N risk given H4's only 12,832 total bars. Declines to specify OBDZ-002's SL/TP/horizon now, deferring to the measurements above. Confirms family=2 with OBDZ-001 -- a bigger mechanism change informed by the same discovery data deserves more caution, not an exemption."},
            {"version": "2.7.13", "commit": "25781e8", "content": "Mandate 3.27: specifies the OBDZ SL/TP ratio diagnostic (Measurement A' precedent, adapted from SMC_S1_v2). Independently recomputes the required-winrate figures directly from raw per-trade net_R (not aggregate back-solving), confirming CEO's cited thresholds (38.6/41.7/37.4%) to within 0.1pp -- notes the cited 'W' column does not reconcile exactly with mean_win computed this way, immaterial since the decision-relevant threshold is confirmed. Specifies Measurement A': Maximum Adverse Excursion in ATR-multiples measured on the 275/223/156 raw cross-candle composite triggers (pre-ATR-floor, avoiding circularity since the floor itself depends on SL_MULT), over a 92-bar window (the established empirical day length) kept separate from the 20-bar trading horizon. Derives 5 SL candidates (p25/p50/p75/p90 of the MAE distribution + the 0.7 anchor) with TP1/TP2 fixed at 2x/3x each candidate, isolating the ratio question. Notes the eligibility floor must be re-derived per candidate. Resolves the three required items: horizon held fixed at 20-bar/EOD with mandatory timeout-fraction reporting; full outcome-bucket breakdown and TP1->TP2 conversion rate required at every cell; and a pre-registered decision rule (closed permanently if net dollar expectancy<=0 at all 15 cells; merits a new hypothesis only if positive at 2+ wider candidates in 2+ regimes; otherwise TESTABLE BUT INSUFFICIENT EVIDENCE) with dollars as the primary decision variable, reusing the SMC_S1_v2 precedent exactly. Confirms the diagnostic itself does not consume the multiple-testing family. Recommends deferring the correction-regime oracle recalibration until after the diagnostic, since it would need redoing regardless of outcome."},
            {"version": "2.7.12", "commit": "58799fa", "content": "Mandate 3.26: FINAL VERDICT on OBDZ-001, the first composite hypothesis executed end-to-end. Independently re-ran code/run_obdz001.py (commit 0d40212), reproducing every figure exactly (n=261/194/154, winrate 0.3908/0.4021/0.4026, expectancy_R +0.0122/-0.0400/+0.0845, p_wp5 0.5007/0.8256/0.1859 -- H0 not rejected in any regime). Issues REJECTED_AT_DECLARED_PARAMETRIZATION (new scoped sub-label): rejects the exact SL=0.7xATR/TP1=1.4xATR/TP2=2.1xATR/partial-exit construction, explicitly does NOT reject the underlying compound entry signal itself, since the risk multiples were declared design choices, never derived. Confirms the mechanical diagnosis: realized horizon collapsed from a nominal median of 20 bars to a realized median of 1-2 (88-90% resolve under 10 bars) because SL=0.7xATR sits inside one average bar's true range, causing near-instant stop-outs (58-61%) and a low TP1 hit rate (36-38%). Confirms the CEO-flagged bear/correction asymmetry (bear's positive expectancy is a single-trade concentration artifact, correction's is genuinely distributed) as real but not verdict-changing. Resolves the required-winrate puzzle: realized average win is only ~1.4-1.7R (not the assumed 2.25R, since only 68-73% of TP1-reachers reach TP2), so the corrected breakeven thresholds (~37-42%, not ~35-37%) land almost exactly at the observed winrates, fully explaining the near-zero-to-modest expectancies. Engages the oracle-domain question (realized 1-2 bar horizon vs the L>=H=20 calibration's nominal worst case) -- reasons a miscalibrated null would likely be too conservative not too permissive, meaning today's null results are robust but the correction regime's p=0.186 needs a dedicated recalibration before being trusted as a positive lean if revisited. Recommends a diagnostic-first (not guess-and-check) path for any wider-SL/TP follow-up, as family=2 with OBDZ-001 if pursued. No new run authorized."},
            {"version": "2.7.11", "commit": "f782f0d", "content": "Mandate 3.25: ratifies VE's self-caught bias-source governance fix and authorizes OBDZ-001 implementation. VE found (before running anything) that the spec's bare citation to code/mtf.py for h1_trend_up/h4_trend_up was ambiguous and would, if followed literally into mtf.py::load_mtf(), have sourced bias from native H1/H4/D1 CSVs read with zero holdout masking -- native H1 is AWAITING_REGIME_MAP, 100% sealed. VE self-corrected to H1_from_M15_v2/H4_from_M15_v2 (CONTEXT_DERIVED_VALIDATED), same formula, discovery-safe loader, forward-safe merge; independently verified _first_mitigation's exact equivalence to the frozen detect_mitigations[0] logic before running. Statistician independently re-verified the whole chain (read mtf.py directly, confirmed the manifest status split, re-ran task_obdz_population.py reproducing every figure exactly) and ratifies: the context-derived path is correct, native H1 is impossible to make discovery-safe (not a real choice). Searched all specs for similar risk -- none found elsewhere, but flags a separate legacy code cluster (s1.py/mstrat.py/run_mtf.py/wave1_harness.py) that actively calls the unsafe path, verified to NOT affect any ratified verdict (trading_strategies.py::detect_s1, behind every SMC_S1 verdict, has zero mtf dependency), recommending a governance label (not implemented here). Population count clears INSUFFICIENT_N in all 3 regimes (261/194/154, >=10x threshold); the prior mandate's own concern about the variable horizon did not materialize (>94% of survivors get the full 20-bar horizon in every regime). Recomputes the required-winrate range precisely on real survivor ATR (median-based ~[35%,37%] vs mean-based ~[34%,36%] matching CEO's cited figure, right-skew explained, median recommended) while reiterating the actual test is mean(net_R)>0, not a winrate threshold. AUTHORIZES VE to implement the full state machine and run the block_bootstrap test on discovery data only, holdout untouched."},
            {"version": "2.7.10", "commit": "75deeca", "content": "Mandate 3.24: formal pre-registration of the composite hypothesis (proposed namespace OBDZ-001), closing all six items CEO flagged as remaining. Verifies CEO's SL/TP arithmetic exactly (50-60 pips=0.68-0.81xATR, 100-120 pips=1.35-1.62xATR at the cited ~74-pip current ATR; same pips would be 2.9x/5.9xATR on discovery-era volatility, demonstrating why ATR-relative sizing is necessary) -- confirms 0.7/1.4/2.1 as a declared design choice with disclosed rationale, still not a statistical derivation. Corrects the required-winrate figure from a single ~31% point (CEO's zero-cost limit) to a range (~31-38%) depending on current ATR's effect on cost/R, consistent with the standing no-single-w*-when-R-varies rule. Resolves: (1) eligibility filter = ATR floor alone, no ceiling -- R is proportional to ATR by construction, unlike the old fixed-geometry filter, so no analogous tail-concentration risk exists; (2) variable horizon aggregated for the primary test (the variable horizon is part of the strategy's own definition, not a nuisance), with mandatory session/horizon-bucket stratified diagnostics; (3) cross-candle intersection fully specified mechanically (same-kind, different formation event, forward-safe, bounded to 460 bars reusing the already-established median-week constant, same discovery block, interval overlap); (4) correction family confirmed separate at 1, distinct from the Block-3 family of 8; (5) declines to fabricate a population estimate (four compounding unmeasured rates would produce false precision) and instead pre-registers INSUFFICIENT_N>=25/regime now, requiring a dedicated VE population-count script before any statistical test. Proposes namespace OBDZ-001, checked for collision, pending CEO ratification."},
            {"version": "2.7.9", "commit": "4216040", "content": "Mandate 3.23 (3 blocks). Block 1: ratifies VE's scan-start-at-formation_idx+2 fix for the Mitigation/Rejection circularity in order_flow.py (the impulse bar engulfs the zone by construction, guaranteeing a spurious visit-1) -- generalizes VE's own finding, verifying the same guarantee holds for Rejection, not just Mitigation as originally flagged. No retroactive effect. Block 2: confirms DemandZone x OrderBlock intersection is trivial as implemented (same anchor bar, A=B), ratifies the cross-candle (A!=B) reading as operative for the new hypothesis; ratifies stop_before_target=True and tp1_tp2_same_bar=True (the latter shown to be logically forced by TP1<TP2 monotonicity, not merely a default). Block 3: independently re-ran task1_atr_eligibility.py and task2_cost_rerun.py, reproducing every cited figure exactly. Reclassifies SMC_S1 FINAL_VERDICT from REJECTED_NET_OF_COST to STATISTICALLY REJECTED (corrected edge_brut_$ is near-zero/inconsistent-sign across regimes, not the previously-claimed small positive monotonic edge) -- Statistician's own prior '6/8 families would pass' estimate is disclosed as not reproduced (actual: 4/8 with only one qualifying cell each). S7/S11 classified TESTABLE BUT INSUFFICIENT EVIDENCE per the Constitution (non-significance is not active disproof), with S7-bear flagged for extreme single-trade concentration (best/sumR=13.6). S16/S17 marked NOT TESTABLE -- the block_bootstrap oracle is validated only for L>=H=20 and these run L=28<H=92/460, invalidating any p-value including S17's deceptively low figures. New re-derived filter ([0.58,6.50)$) ratified authoritative over the old one regardless of which flatters a given cell. Multiple-testing family fixed at 8 (pooled-per-family, matching S1's own precedent), with the pooled test itself still owed by VE for S7/S11. Retracts Statistician's own v2.7.8 ATR-floor 'hypothesis-threatening' flag as a self-caught pip-unit mismatch (comparing a new-TICK 86-pip figure against an old-TICK 74-pip figure) -- VE's independently-reproduced feasibility check confirms 89.75% of discovery bars clear the floor. Resolves the variable-horizon-vs-oracle-coverage question (upper-bounded at 20 bars, so L>=28 coverage still holds)."},
            {"version": "2.7.8", "commit": "e66664c", "content": "Mandate 3.22 (4 parts). Part 1: TICK verified at source (real 2-decimal broker quoting) -- 0.10 was 10x wrong; corrected to 0.01. cost_round_trip corrected 0.40->0.20 (spread_ticks=slip_ticks=5, from the midpoint of CEO's stated 5-15 tick spread range + CEO's slip=spread convention). Verified R does NOT 10x-inflate (R_dollars=distance_dollars+2*TICK, only the small buffer term scales with TICK) -- a self-corrected finding after an initial miscalculation. Exhaustive REOPEN enumeration across 3 mechanism-channels (cost-only, TICK-as-pip-divisor-only, compound): REOPENS displacement_filter, rejection_ceiling (label only, real distance unchanged), break_even_thresholds_SUPERSEDED, FINAL_VERDICT (REJECTED_NET_OF_COST + its CLOSED_DEFINITIVELY status), the 7-family descriptive table (commit 741e272, CEO instructs NOT to hand-adjust these figures -- re-run from raw geometry), LiquidityVoid's $1.20 threshold (->$0.60). Confirms oracle status, market_structure D1-D7, session/horizon derivations, D-BPR tolerances, and SMC_S1_v2 (v2.7.7, now explicitly GATED pending this correction) as unaffected in mechanism though S1_v2 stays blocked. Ratifies CEO's 'verify every constant at the instrument-spec source, not the code' rule, extended to also check code lines adjacent to the cited ones. Part 2: ratifies Order Block formation criterion (E010 displacement/expansion qualifier + body-engulfment of the prior opposite candle, no volume filter) -- clarifies this does not contradict IFVG's inversion rule (different question: formation vs inversion). Part 3: specifies DemandZone as a new, non-consuming primitive ([High,Low], distinct from OrderBlock's consuming [Close,Open]), with a mechanical intersection condition (trivial same-candle vs substantive cross-candle reading flagged, cross-candle recommended) and the anti-E010 window separation extended to the compound object. Part 4: pre-registers a new ATR-based partial-exit hypothesis -- corrects the order's own weighted-RR arithmetic (2.25R, not 1.58R, since TP1/TP2 are ATR-multiples not R-multiples given R=0.7xATR); specifies breakeven-at-entry-exactly, a variable (not fixed) horizon from min(20-bar,EOD-close), a new partial-exit net_R formula, and a freshly-derived ATR-based eligibility floor (~86 pips) FLAGGED as potentially exceeding even current market ATR (~74 pips) -- a hypothesis-threatening finding requiring direct population verification before execution, not assumed resolved."},
            {"version": "2.7.7", "commit": "b98070c", "content": "SMC_S1_v2 stop-geometry design (specification only, nothing executed): CTO proposes moving the stop from spike+2 pips to the prior major swing, to dilute cost as a fraction of R -- no one had measured the resulting distance before this design. Specifies Measurement A (distance from next-open entry to the nearest prior CLASSIFIED market_structure.py swing that is more extreme than the basin's own swing, on the 34,670 RAW wick-sweep events not the already-filtered 21,048, reporting the full percentile distribution plus fractions exceeding 65/under 10.1 pips). Rules the sensitivity map DIAGNOSTIC not FITTING, and pre-registers -- before any number exists -- a decision rule on 5 derived stop points (p25/p50/p75/p90 of the new distribution plus the 14.7-pip anchor): closed permanently if net dollar expectancy <=0 at all 5 stops in all 3 regimes; merits a new hypothesis only if net dollar expectancy >0 at 2+ wider stops in 2+ regimes (a pattern, not an isolated point); anything mixed is TESTABLE BUT INSUFFICIENT EVIDENCE. Mandates dual R-and-dollar reporting at every cell, with DOLLARS as the primary decision variable, since a wider stop can show a better R-normalized edge while losing more real money (cost/R shrinking doesn't mean fewer dollars lost). Locks in SMC_S1_v2's required pre-registration if the diagnostic passes: derived stop with written justification, re-derived eligibility filter, reconfirmed-or-re-derived horizon, and a family-of-2 multiple-testing correction with SMC_S1 (same discovery consumed a second time for a near-identical hypothesis, same precedent as B.1/B2). Confirms SMC_S13's variant-3 formulation and the 12->20 horizon correction as accepted/necessary. S10 remains open."},
        ],
    }

    manifest: dict[str, Any] = {
        "manifest_id": "STAT-SPLIT-MANIFEST",
        "version": "2.7.18",
        "published_date": "2026-07-30",
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
        "changelog_v2_7_18": (
            "Mandate 3.32 -- fixes the multiple-testing family size and the measurement ordering for a "
            "ten-zone-type survey, entirely before any of the ten are actually measured, in direct response "
            "to CEO noticing that the prior mandate's rule (measure each zone type separately, never "
            "pooled) left an important gap unaddressed: with ten types each assessed across three arms, "
            "the raw comparison count (thirty, plus whatever had already been done) risked repeating the "
            "exact failure mode of the earlier 1972-hypothesis campaign, where the required significance "
            "threshold had collapsed to roughly 0.000032 and effectively nothing could clear it. Before "
            "answering the family-size question, verified every one of the ten zone types CEO listed "
            "against the actual codebase rather than assuming the list was accurate: confirmed Order Block, "
            "Breaker Block, Demand/Supply, Fair Value Gap, its CE-50 reaction level, Inverse Fair Value Gap, "
            "Balanced Price Range, Liquidity Void, prior-day levels, and prior-week levels all already exist "
            "as working functions requiring zero new code, and separately confirmed via an exhaustive search "
            "that no notion of a session's own opening price as a standalone level exists anywhere in the "
            "codebase. Resolved what had looked like a single family-size question into two genuinely "
            "distinct ones: the descriptive three-arm MAE/MFE characterization of each zone type does NOT "
            "consume any family allocation at all, for exactly the same reason the touch funnel and the "
            "original Measurement A' did not -- none of these are hypothesis tests carrying their own null "
            "hypothesis, alternative, or verdict, so the 'thirty comparisons' concern does not apply to the "
            "measurement phase itself, regardless of how many of the ten types happen to show an "
            "interesting-looking pattern. The family size that DOES need fixing, and is fixed now rather "
            "than left until results are in hand, applies only to whatever formal, pre-registered hypothesis "
            "tests might eventually follow from this survey -- set at ten, matching the full count of "
            "candidates being looked at, regardless of how many ultimately look promising enough to be "
            "formalized, since the entire lesson of the 1972-hypothesis campaign was that surveying many "
            "candidates and then testing only the ones that survived a first look, without correcting for "
            "the act of looking itself, is precisely the selection-bias trap a fixed-in-advance family size "
            "exists to prevent. Noted an important overlap that would otherwise have led to quietly "
            "double-counting evidence: two of the ten listed types, Order Block and Demand/Supply, are "
            "exactly the construction already measured in the OBDZ-001/002 three-arm result from the prior "
            "mandates -- that existing result is counted as the first of the ten data points in this survey "
            "rather than being treated as unrelated to it or being measured again from scratch, leaving nine "
            "types genuinely new to measure. Confirmed, with an explicit structural rationale rather than "
            "simply accepting the suggested grouping, the three-wave ordering CEO proposed: a first wave "
            "covering the eight types that share a common geometric nature as intervals with their own low "
            "and high bounds (or close and open bounds), the most natural and homogeneous group to measure "
            "together; a second wave covering the four prior-day and prior-week level types separately, "
            "justified specifically because a single reference price behaves differently under repeated "
            "testing than a bounded interval zone does, not because of any arbitrary priority ranking "
            "between the two groups; and a third wave covering the three types requiring genuinely new "
            "code, deliberately gated on the first two waves showing a promising pattern before any "
            "implementation effort is spent, matching the same discipline already applied to holding two "
            "other proposed confirmation variants until a related measurement justified building them. "
            "Investigated directly in code whether two of the three new-primitive candidates, described as "
            "a 'Mitigation Block' and a 'Rejection Block', are actually identical in substance to the "
            "existing detectors that already carry similar names, and found they are not: the existing "
            "mitigation and rejection detectors both take an already-formed Order Block as their input and "
            "return reaction events tied to that pre-existing zone, rather than defining any zone boundary "
            "of their own directly from raw price the way every other primitive on the list does. Concluded "
            "that if the intended meaning is a new zone anchored at the reaction bar itself, independently "
            "testable rather than merely an event flag on someone else's zone, that would be a genuinely "
            "new primitive requiring its own boundary definition and validity/measurement-window separation "
            "with the same rigor the Order Block and Demand Zone primitives received earlier -- and declined "
            "to invent that definition unilaterally, leaving it as an open clarification needed from CEO "
            "before either candidate can be properly specified, rather than assumed resolved by name alone. "
            "Reaffirmed throughout that the pending paired significance test from two mandates prior remains "
            "the actual priority, and that nothing in this document authorizes running any of the ten "
            "zone-type measurements -- the family size and wave ordering are being fixed now purely so they "
            "are ready to apply the moment that pending test confirms the underlying methodology is finding "
            "something real, rather than the same noise repeated across ten different constructions."
        ),
        "changelog_v2_7_17": (
            "Mandate 3.31 -- an addendum to the pending grid verdict from Mandate 3.30, prompted by an "
            "operational constraint CEO raised: the desired frequency for a discretionary M15 strategy is "
            "roughly 5 trades per week, while OBDZ-001 as measured produces far fewer. Verified this gap "
            "directly rather than accepting the stated figures at face value: confirmed the exact discovery-"
            "block durations from the manifest itself (bear 794.0 days, bull 816.1 days, correction 390.2 "
            "days, totaling 2000.4 days across all three regimes) and recomputed the trade frequency from "
            "first principles -- bear approximately 2.31 trades/week, bull approximately 1.67, correction "
            "approximately 2.77 (a small refinement from the previously-cited 3.0, which had assumed the "
            "correction regime spans exactly one year rather than its true 1.068 years), and an aggregate "
            "of approximately 2.14 trades/week -- confirming the actual frequency sits at roughly half the "
            "stated target. Separately, confirmed CEO's own self-correction regarding the earlier population-"
            "count funnel: its three steps are expressed in three genuinely different units (a count of "
            "individual bars at the first step, a count of formed zones at the second, and a count of OB-"
            "mitigation trigger events at the third), so no valid survival or collapse rate can be computed "
            "by dividing one step's count by another's, since a single zone might be touched by price zero, "
            "one, or many times over the discovery period. Independently verified that the specific claim "
            "being corrected (that the collapse occurs at the third step, with only a few hundred of several "
            "thousand zones surviving) was never actually made in any Statistician document, confirming this "
            "was CEO's own earlier error being corrected, not something requiring correction on Statistician's "
            "side. Specifies a new touch funnel expressed in a single consistent unit throughout, at the "
            "level of individual zones rather than mixing levels: first, how many of the formed DemandZones "
            "are ever touched by price at all after their formation; second, of those, how many have a "
            "cross-candle unmitigated Order Block overlapping at the moment of that first touch, using "
            "exactly the already-ratified overlap mechanics; and third, of those, how many have aligned H1 "
            "and H4 bias at that same touch bar -- with results reported broken out by polarity (demand "
            "versus supply) as well as by regime, tying directly into the polarity re-stratification already "
            "specified in the prior mandate and into the bear-regime asymmetry flagged in this mandate's own "
            "context. Requests that this funnel be measured NOW, running in parallel with the still-pending "
            "paired significance test from the prior mandate, on the grounds that it is purely descriptive, "
            "read-only counting that touches no part of the actual entry or exit mechanism and therefore "
            "does not conflict with the standing instruction not to relax anything before a verdict exists. "
            "Explains why the location of the collapse in this funnel matters for choosing among possible "
            "frequency levers: a collapse at the first step would mean the zones themselves are rarely "
            "revisited by price at all, pointing toward reconsidering the zone construction itself rather "
            "than any relaxation of the composite entry condition; a collapse at the second step would mean "
            "genuine confluence with an unmitigated Order Block is the rare ingredient, pointing toward "
            "either additional zone types or a reconsidered overlap window; and a collapse concentrated at "
            "the third step would point most directly at the bias-alignment requirement itself as the "
            "binding constraint. Frames, without selecting or authorizing, three specific levers CEO raised "
            "as candidates once and if the pending verdict confirms a real effect: relaxing bias to H4 alone, "
            "for which the correct measurement is not whether frequency rises (it almost certainly would) "
            "but whether the previously-measured effect survives under that relaxed condition, since its "
            "disappearance would indicate the H1 alignment requirement is itself part of the mechanism "
            "rather than merely a frequency filter; adding further zone types such as fair-value gaps, "
            "breakers, or prior-day-high/low levels, each of which must be measured entirely independently "
            "with its own compound trigger construction before any question of combining them is even "
            "considered, since pooling structurally distinct primitives together would obscure which one "
            "if any actually carries the effect; and reverting to zones detected natively on the M15 "
            "timeframe rather than on the higher timeframes, which is flagged explicitly and pointedly as "
            "not a neutral option alongside the other two, since it would reverse a deliberate design choice "
            "made earlier in this same hypothesis's own history specifically to obtain larger and more "
            "reliable zones, moving back toward a construction closer to the original OBDZ-001 already "
            "rejected at its declared parametrization. States plainly, as instructed, that the frequency "
            "question remains entirely undecided pending the outcome of the pending paired test, and that "
            "if none of the three levers turns out to preserve the underlying effect while raising trade "
            "frequency, a rare but genuinely confirmed edge remains a legitimate and acceptable outcome for "
            "a discretionary strategy rather than a failure of the research effort."
        ),
        "changelog_v2_7_16": (
            "Mandate 3.30 -- reads the grid on the corrected 3-arm windowed measurement VE delivered "
            "(code/obdz_three_arm_windows.py, commit d869177), answers a new oracle-domain question raised "
            "in the course of doing so, and independently checks a stated premise about the demand/supply "
            "asymmetry rather than accepting it. Statistician re-ran the script directly and reproduced "
            "every cited figure exactly: the pullback-depth matching between arm A and arm C achieved a "
            "clean 100% (275/223/156 matched, zero unmatched, zero pullback-undefined -- the comparison is "
            "complete, not thinned by exclusions); at the primary window ([entry+1,entry+4], i.e. "
            "[touch+2,touch+5]), median MFE in ATR multiples for zone/random-control/pullback-control is "
            "0.85/0.80/0.75 in bear, 1.06/0.80/0.77 in bull, 1.11/0.90/0.76 in correction, and 0.97/0.81/0.76 "
            "in aggregate -- a zone-over-pullback gap of roughly 13%/38%/46%/28% respectively; at the "
            "longer window ([entry+1,entry+9]) the aggregate gap narrows to roughly 20%, still positive in "
            "direction but no longer clearing the pre-registered 25% threshold as cleanly. This CONFIRMS "
            "the prior mandate's window-correction diagnosis directly: on the blind 92-bar window zone and "
            "control were indistinguishable, while on the corrected short window a real gap of the "
            "magnitude anticipated appears. Reads the pre-registered grid honestly rather than forcing it "
            "into either extreme: this is neither a clean unanimous pass (bear alone falls short of the "
            "25% threshold, though still directionally consistent) nor a null-everywhere result -- it is a "
            "consistent-direction pattern of varying magnitude across regimes, precisely the ambiguous "
            "middle case the declared thresholds exist to name rather than force a premature call on. "
            "States plainly, per direct instruction, that this remains a descriptive OBSERVATION and not "
            "yet a validated finding. In the course of considering how to test this pattern for "
            "significance, identifies and answers a genuinely new oracle-domain question: block_bootstrap@v1 "
            "was calibrated specifically for a single outcome series (net_R) whose values are correlated "
            "because their measurement windows overlap and share future shocks -- the actual object needed "
            "here, an A-versus-C comparison, is different in kind, since every zone trigger is matched 1:1 "
            "to exactly one pullback-control partner by the matching procedure itself, making this a PAIRED "
            "comparison rather than a one-sample test against zero. Reasons that the correct target is "
            "therefore the per-pair difference (zone MFE minus matched-control MFE) rather than the two "
            "distributions considered separately, for which a paired test (a signed-rank test, or a "
            "bootstrap directly on the paired difference) is both more appropriate and more statistically "
            "powerful, automatically controlling for anything shared by a matched pair such as regime or "
            "approximate timing. Flags a residual concern that nearby trigger events might still be "
            "correlated with each other through shared market conditions, meaning the pairs themselves "
            "could fail to be independent draws -- recommends reusing the block-bootstrap resampling "
            "mechanism itself (not its net_R-specific calibration) on the time-ordered sequence of paired "
            "differences, run alongside a plain independent-draws bootstrap as a baseline, so that close "
            "agreement between the two would indicate the finding is robust to this dependence question "
            "while a substantial divergence would itself be the informative result -- explicitly has NOT "
            "run this test, so today's percentage gaps remain an observation only. States that this whole "
            "diagnostic chain, including the paired test once it runs, does not consume the multiple-"
            "testing family count, matching the precedent already established for Measurement A' -- it "
            "decides whether a real hypothesis is worth formulating, it is not that hypothesis test itself. "
            "Separately, rather than accepting the CEO-offered explanation for the bear regime's own "
            "internal asymmetry (worse MFE-to-MAE ratio than its own matched pullback control, unlike bull "
            "and correction) at face value, independently verified the stated premise that bear consists "
            "entirely of supply-side (short) triggers while bull and correction consist entirely of "
            "demand-side (long) ones -- found this premise to be FALSE: a direct count shows all three "
            "regimes are substantially mixed in polarity, with the minority direction making up 37-46% of "
            "triggers in every regime, not the assumed clean split. This resolves what had been posed as an "
            "open, possibly undecidable question -- since real polarity variation already exists within "
            "every regime, the polarity-versus-regime question can be answered directly by re-stratifying "
            "the SAME already-collected trigger events by direction, pooled across all three regimes, "
            "rather than by regime as originally measured, with no need to collect any new contra-trend "
            "data as had been assumed necessary. Specifies the ordering to follow if the paired test "
            "confirms the pattern: the paired test and the polarity re-stratification can run in parallel, "
            "since they answer different questions on already-collected data; only if the paired test "
            "confirms should SL/TP candidates be derived from the newly-measured, much tighter MAE "
            "distribution (median 0.88-1.09x ATR, far more informative than either the original 0.7x "
            "anchor or the blind 92-bar-window's 4.4x figure); the confirmation-based entry variant would "
            "then require its own separate re-measurement from the confirmed-entry point rather than "
            "assuming these figures carry over; and the H1/H4 population count remains held until all of "
            "the above establish that the underlying mechanism is worth building further. Does not "
            "authorize formulating OBDZ-002 in this document."
        ),
        "changelog_v2_7_15": (
            "Mandate 3.29 -- corrects two design errors in the MAE/MFE/control measurement specified in "
            "v2.7.14, both identified by CEO and confirmed independently by Statistician, both Statistician's "
            "own specification mistakes rather than execution errors by VE, which implemented exactly what "
            "was asked (code/obdz_mae_mfe_control.py, commit b233c83). Statistician re-ran the script "
            "directly and confirmed the diagnostic evidence for both errors precisely: median bar_MAE "
            "(35.0/32.0/41.0 across bear/bull/correction) and bar_MFE (41.0/45.0/35.5) all land in the "
            "second half of the 92-bar window -- second-trading-day price movement, not an immediate "
            "reaction to the zone -- and the zone's MAE/MFE distributions are nearly indistinguishable from "
            "the bias-aligned control's on that same window (aggregate MAE median 4.40 vs 4.82, MFE median "
            "4.67 vs 4.46). Error 1: the 92-bar window itself was reused verbatim from an unrelated "
            "derivation (the empirical trading-day length, originally derived for a compression/volatility "
            "measure at Mandate 3.18/3.19) without reconsidering whether it fit THIS purpose -- it "
            "mechanically measures general volatility over roughly a full trading day following any point, "
            "carrying no reaction-specific information regardless of what it is compared against, which is "
            "exactly why zone and control came out indistinguishable. Corrects this by specifying four new "
            "windows, all starting one bar after the actual trade entry (which itself is one bar after the "
            "zone touch) rather than at the touch or entry bar directly, since both of those still reflect "
            "proximity to the zone rather than the market's subsequent reaction to it: in the notation CEO "
            "used relative to the touch bar, [+2,+3], [+2,+5], [+2,+10], and [+2,+20] (the real 20-bar "
            "trading horizon), translated precisely into the code's existing entry-relative indexing so "
            "there is no ambiguity for implementation. States explicitly that [+2,+5] and [+2,+10] are the "
            "PRIMARY decisive windows, per CEO's own reasoning that if the zone produces any effect it will "
            "show there or nowhere, with the shortest and longest windows reported only as context. Does "
            "NOT retract the original 92-bar result -- keeps it as Statistician's own explicit decision, as "
            "requested -- but relabels its scope precisely as a general ~1-day volatility profile (zone "
            "versus bias-aligned control), not a reaction measure, specifically so it cannot be misread "
            "later as evidence about reaction timing. Error 2: the existing bias-matched control (arm B) "
            "correctly isolates the compound zone's contribution over plain bias alignment, but conflates a "
            "second variable Statistician had not accounted for -- zone entries are, by construction, "
            "always at a pullback or retracement (a Mitigation touch requires price to have moved against "
            "the bias direction to reach the zone in the first place), while arm B's bias-aligned bars "
            "include any point at all, including fresh local extremes with no pullback whatsoever. If "
            "pullbacks within a trend behave systematically worse than randomly-timed entries -- plausible, "
            "since buying into a still-falling price is a real risk -- then 'zone approximately equals "
            "random' could actually conceal 'zone beats a simple pullback', a distinction the existing "
            "two-arm design cannot make. Specifies a third arm (pullback without zone) to resolve this: "
            "defines pullback depth mechanically by reusing the ALREADY-ESTABLISHED market_structure.py "
            "Swing/StructureLabel primitive -- the exact same one used for SMC_S1_v2's own 'prior major "
            "swing' measurement -- as the distance from the nearest prior classified swing extreme against "
            "the bias direction, in ATR units, rather than inventing a new rolling-window definition. "
            "Specifies the matching procedure precisely: for each zone trigger with a defined pullback "
            "depth, find a bias-aligned, non-zone-trigger bar whose own pullback depth falls within a "
            "disclosed tolerance (25% relative or 0.5x ATR absolute, whichever is wider), widening "
            "progressively up to a hard cap if no match is found, with any triggers still unmatched at the "
            "cap reported explicitly rather than silently dropped or force-matched -- one match selected at "
            "random per trigger, same seeding convention as the existing control. Specifies that the "
            "resulting arm-A-versus-arm-C comparison must be restricted to the subset of triggers with a "
            "defined pullback depth (reported distinctly as 'A_subset_matched'), kept separate from the "
            "already-measured full-population 'A_full' still used for the existing arm-A-versus-arm-B "
            "comparison, so the two are never conflated. Specifies a pre-registered interpretation grid, "
            "read primarily from median MFE at the two decisive windows, with four named outcomes (pullback "
            "matters and the zone adds nothing beyond it; the zone adds something beyond a matched pullback; "
            "neither the pullback nor the zone matters, closing the entire line rather than just the "
            "zone-specific angle; or a mixed pattern warranting no premature call), using disclosed 15% and "
            "25% threshold conventions rather than derived constants, in the same spirit as other pragmatic "
            "thresholds already accepted throughout this lab. Confirms the OBDZ verdict remains deferred -- "
            "today's result answers a narrower question than the one that actually matters -- and that the "
            "H1/H4 population count stays held, unchanged, pending this corrected measurement's result."
        ),
        "changelog_v2_7_14": (
            "Mandate 3.28 -- corrects the Diagnostic A' mechanical verdict, specifies the follow-on "
            "MAE/MFE-plus-randomized-control measurement, and frames the confirmation-based OBDZ-002 "
            "hypothesis without numerically specifying it. VE delivered Measurement A' and the SL/TP ratio "
            "diagnostic (code/obdz_sltp_diagnostic.py, commit 465eb38), flagging three limitations "
            "unprompted (timeout fractions of 0.96-0.99 at the wide candidates, TP1-to-TP2 conversion "
            "collapsing to 0.0 there, and extreme single-trade concentration up to best_over_sumR=9.64) "
            "without patching them by widening the horizon, which would have reintroduced the exact "
            "confound the diagnostic was designed to avoid. Statistician independently re-ran the script "
            "directly and reproduced every cited figure exactly, including the MAE median of 4.4x ATR "
            "against the original 0.7 anchor (a 6.3x ratio) and the literal mechanical verdict of MERITA "
            "IPOTEZA NOUA. Determined that this literal verdict is NOT usable as an answer to the question "
            "the diagnostic was built to ask: at the p75/p90 candidates, TP1 (17-27x ATR away) is "
            "essentially unreachable and 95.6-98.9% of trades resolve only by hitting the fixed 20-bar "
            "timeout, meaning the SL/TP mechanism itself is no longer the active driver of the outcome -- "
            "what is actually being measured there is drift over a fixed window at an effectively-infinite "
            "stop and target, a different question than 'does the ratio matter'. This is a gap in "
            "Statistician's own v2.7.13 specification (it should have included a minimum-resolution-rate "
            "guard on which candidates count as genuinely testing the ratio), not an error by VE, which "
            "correctly surfaced the limitation and deferred the call rather than silently patching it. "
            "Further notes that even the one candidate still structurally testing the intended mechanism "
            "(p25, with a much more reasonable 0.356-0.444 timeout fraction) fails the pre-registered "
            "2-of-3-regimes threshold regardless (positive dollar expectancy in only the correction "
            "regime). Reclassifies the diagnostic's answer to the SL/TP-ratio question as TESTABLE BUT "
            "INSUFFICIENT EVIDENCE rather than MERITA IPOTEZA NOUA, and declines to formulate OBDZ-002 from "
            "this literal trigger. Separately addresses whether MAE=4.4x ATR is a property of the compound "
            "zone or of general market volatility over a 92-bar window -- specifies a randomized control "
            "(bars drawn without replacement from each regime's own bias-aligned population, matched "
            "exactly in count to the raw triggers, same direction convention, no ATR floor, fixed seed "
            "reused from the WP-5' bootstrap convention) with an explicit three-way reading rule, directly "
            "paralleling the E004 fill-rate control precedent (which found the specific construct's rate "
            "BELOW, not above, its generic baseline). Specifies a combined Maximum Favorable Excursion and "
            "bar-of-touch measurement, applied identically to both the real triggers and the randomized "
            "control, with three named interpretation patterns matching what the CEO laid out: early "
            "adverse excursion followed by a later, comparable favorable one supports a timing/confirmation "
            "fix; a large adverse excursion with a systematically small favorable one means the zone does "
            "not predict a reversal at all regardless of timing; and simultaneous, comparably-sized "
            "excursions in both directions would mean only generic volatility is being measured. Reviews "
            "the three confirmation variants CEO proposed: confirms Variant 3 (impulse-candle "
            "engulfment plus magnitude) requires zero new primitives, being exactly the already-ratified "
            "Order Block formation criterion reused as a post-entry confirmation gate, and specifies its "
            "structural mechanic (wait for a new qualifying impulse candle at or after the original trigger "
            "bar, entering next-open after that confirmation) without committing to any numeric stop, "
            "target, or horizon; confirms, via exhaustive code search, that Variants 1 (pinbar) and 2 "
            "(inside bar) both require genuinely new geometry not present anywhere in the codebase, and "
            "agrees with CEO's own suggestion to hold them until Variant 3's measured effect on MAE is "
            "known, rather than building two new primitives for a question not yet answered. Confirms, via "
            "the same exhaustive search, that the H1/H4 zone-detection wiring gap CEO flagged is real -- "
            "the existing, already-ratified Order Block and DemandZone detectors have never once been run "
            "on H1_from_M15_v2 or H4_from_M15_v2, only ever on M15 bars -- and specifies that a read-only "
            "population-count-only script (structurally identical to the existing population-count "
            "precedent) must run on those higher timeframes BEFORE any effort is invested in building a "
            "full cross-timeframe entry state machine, flagging a genuine risk that the population there "
            "could already fail the INSUFFICIENT_N threshold given H4 carries only 12,832 bars across the "
            "entire discovery period. Explicitly declines to specify OBDZ-002's actual stop, target, or "
            "horizon multiples in this document, per direct instruction -- states only the method by which "
            "they will be derived once the measurements above return real numbers, rather than chosen from "
            "intuition as the original 0.7x ATR figure was. Confirms the new hypothesis, however it is "
            "eventually specified, remains family=2 with OBDZ-001 -- reasoning that the size of the "
            "mechanism change is not the relevant test; what matters is that its entire justification is "
            "derived from a diagnostic run on OBDZ-001's own discovery data, so a larger pivot informed by "
            "the same data warrants MORE caution under the multiple-testing discipline, not an exemption "
            "from it. No execution authorized in this document."
        ),
        "changelog_v2_7_13": (
            "Mandate 3.27 -- specifies the SL/TP ratio diagnostic recommended (not yet designed) in the "
            "prior mandate's OBDZ-001 final verdict. Before the design work, independently re-verified the "
            "prior mandate's required-winrate figures by computing them directly from raw per-trade net_R "
            "(via a temporary, uncommitted script running the frozen state machine and separating winners "
            "from losers exactly) rather than the aggregate back-solving used before: mean_win/mean_loss/"
            "breakeven_winrate = bear 1.8184/-1.1464/38.67%, bull 1.6884/-1.2022/41.59%, correction "
            "1.8499/-1.1052/37.40% -- confirms the cited thresholds (38.6/41.7/37.4%) to within 0.1pp. "
            "Notes the previously-cited 'W' figures (1.89/1.84/1.97) do not reconcile exactly with mean_win "
            "computed this most-precise way, but the decision-relevant threshold is independently confirmed "
            "regardless, so the discrepancy is flagged without further pursuit. Specifies Measurement A' "
            "(directly adapting the SMC_S1_v2 stop-geometry precedent to a NEW variable, the SL/TP RATIO "
            "rather than absolute stop size): Maximum Adverse Excursion in ATR14[t]-multiples, measured on "
            "the 275/223/156 RAW cross-candle composite triggers (before any ATR-floor filtering -- "
            "necessary because the eligibility floor itself is a function of SL_MULT via the 3x-cost-"
            "stress-saturation formula, so filtering first would be circular exactly as SMC_S1_v2's own "
            "Measurement A discovered), over a 92-bar window (the already-established empirical day length, "
            "reused verbatim rather than invented) kept deliberately separate from the 20-bar trading "
            "horizon -- Measurement A' characterizes market behavior after the trigger, not the exit rule. "
            "Derives a 5-point SL candidate set (p25/p50/p75/p90 of the MAE distribution plus the original "
            "0.7 anchor) and fixes TP1/TP2 at 2x/3x each candidate, preserving the already-established "
            "1x/2x/3x progression -- this isolates the ratio question cleanly from a second, unrelated "
            "question about whether the RR itself should change. Flags, as a necessary technical point not "
            "explicitly requested, that the ATR eligibility floor must be RE-DERIVED per SL candidate (it "
            "shrinks as SL widens), admitting a somewhat larger population at wider candidates -- reported "
            "explicitly, not hidden. Resolves the three items required: the 20-bar/EOD horizon stays FIXED "
            "as a controlled condition across all candidates, with the unresolved-timeout fraction reported "
            "as a mandatory diagnostic at every cell rather than silently patched by also varying the "
            "horizon; the full outcome-bucket breakdown AND the explicit TP1->TP2 conversion rate are "
            "required at every cell, not just expectancy, since the conversion rate is expected to shift as "
            "TP2 moves farther from a wider stop; and a decision threshold is PRE-REGISTERED now, before any "
            "number exists, reusing the SMC_S1_v2 asymmetric structure exactly (closed permanently only on "
            "unanimous non-positive dollar expectancy across all 15 cells; merits a new hypothesis only on a "
            "PATTERN of positive dollar expectancy at 2+ of the wider candidates in 2+ regimes, not an "
            "isolated point; anything mixed is TESTABLE BUT INSUFFICIENT EVIDENCE) with DOLLARS as the "
            "explicit primary decision variable, since a wider stop will show better R-normalized numbers "
            "almost mechanically while each stop-out grows proportionally larger in real money. States "
            "explicitly why this is DIAGNOSTIC and not FITTING, and why the temptation toward fitting is "
            "higher here than usual (an existing positive, distributed cell already exists at the "
            "correction regime) -- the decision rule is fixed before any Measurement A' or re-run number "
            "exists specifically to prevent that temptation from corrupting the read. CONFIRMS the "
            "diagnostic itself does not consume the multiple-testing family count (a measurement plus a "
            "pre-registered decision rule, not a hypothesis test with its own H0/H1/verdict, same precedent "
            "as SMC_S1_v2's own Measurement A) -- family remains 1 unless and until the diagnostic produces "
            "a new, formally pre-registered hypothesis, at which point it becomes 2 with OBDZ-001 and the "
            "significance threshold narrows accordingly. Recommends DEFERRING the correction regime's "
            "oracle recalibration until after the diagnostic concludes, reasoning sequentially that any "
            "recalibration matched to today's realized 1-2 bar horizon would become obsolete if the "
            "diagnostic yields a new (likely longer-horizon) hypothesis, and would become practically moot "
            "if the diagnostic instead shows null everywhere and the line closes -- either way, recalibrating "
            "now would be wasted or duplicated effort. No execution authorized in this document."
        ),
        "changelog_v2_7_12": (
            "Mandate 3.26 -- the final verdict on OBDZ-001, the first composite hypothesis in the project "
            "to run end-to-end (bias -> cross-candle intersection -> ATR risk -> partial exit -> "
            "block-bootstrap test). VE implemented the state machine (code/obdz001.py, commit 1146124) and "
            "ran it on the 130,491 M15_v2 discovery bars (code/run_obdz001.py, commit 0d40212), reporting "
            "results uncommitted and stopping for verdict, per instruction. Statistician independently "
            "re-ran the execution directly and reproduced every figure exactly: n=261/194/154 across "
            "bear/bull/correction, winrate 0.3908/0.4021/0.4026, expectancy_R +0.0122/-0.0400/+0.0845, "
            "p_wp5 (H0: mean(net_R)<=0, block_bootstrap L=28) 0.5007/0.8256/0.1859 -- H0 is NOT rejected "
            "in any regime. Issues a new scoped sub-label, REJECTED_AT_DECLARED_PARAMETRIZATION (same "
            "precedent as REJECTED_NET_OF_COST): rejects H1:mu_netR>0 at the EXACT tested construction "
            "(SL=0.7xATR/TP1=1.4xATR/TP2=2.1xATR/75-25 partial exit) but explicitly does NOT reject the "
            "compound entry signal itself (H1/H4 bias + cross-candle DemandZone + unmitigated OB) as a "
            "source of directional information -- the risk multiples were declared design choices "
            "(Mandate 3.24), never derived from any property of the signal, so a null under this specific "
            "choice is not evidence against the signal that carries it. Confirms the mechanical diagnosis "
            "precisely: the realized horizon collapsed from a nominal median of 20 bars (per the population "
            "count) to a realized median of just 1-2 bars, with 88-90% of trades resolving under 10 bars in "
            "every regime -- because SL=0.7xATR sits inside a single average bar's true range, a single "
            "adverse bar of typical size can blow through the stop, explaining the 58-61% stop-out rate and "
            "its near-immediacy; reaching TP1 (2R) requires price to travel twice the stop distance without "
            "first retracing the smaller stop distance, a rarer event, explaining the 36-38% TP1 hit rate. "
            "Confirms the bear/correction asymmetry flagged in the mandate as real and mechanically "
            "demonstrated (bear's modest positive expectancy is a single-trade concentration artifact, "
            "best_over_sumR=0.686, collapsing on removal of the top trade; correction's is genuinely "
            "distributed, best_over_sumR=0.170, surviving removal) but does not change the verdict since "
            "neither rejects H0. Resolves the apparent required-winrate paradox (observed winrates above "
            "the v2.7.11-estimated ~35-37% threshold, yet near-zero expectancy): the realized average win "
            "is only approximately 1.4-1.7R, not the assumed 2.25R, since only 68-73% of TP1-reachers in "
            "each regime go on to TP2 rather than settling for the 1.5R breakeven leg -- recomputing the "
            "breakeven threshold directly from the actual outcome-bucket breakdown gives approximately "
            "[37%,42%], not [35%,37%], and the observed winrates land almost exactly relative to these "
            "corrected per-regime thresholds, fully explaining the marginal-to-modest expectancies with no "
            "residual puzzle. Engages, without resolving, a genuine oracle-domain question raised in the "
            "mandate: block_bootstrap@v1 was validated for L>=H=20, and L=28 nominally satisfies this since "
            "20 is the maximum possible horizon here, but the REALIZED horizon (median 1-2 bars) is far "
            "shorter than the worst case the calibration assumed -- reasons that a null calibrated on "
            "longer-than-real dependency would generally be MORE conservative, not less, meaning today's "
            "negative/null results (bear, bull) remain robust to this uncertainty while the correction "
            "regime's p=0.186 (the least overwhelming non-rejection) would need a dedicated recalibration "
            "matched to the realized horizon distribution before being trusted as a positive lean if the "
            "family is ever revisited -- does not change today's verdict, since none of the three p-values "
            "approach any plausible rejection threshold regardless. Recommends, as a process suggestion not "
            "an authorization, that any wider-SL/TP follow-up (e.g. 1.5x/3.0x ATR, same 1:2 RR) reuse the "
            "SMC_S1_v2 diagnostic-first precedent (a dedicated excursion-distribution measurement with a "
            "pre-registered decision threshold) rather than a second blind guess-and-check, and that it be "
            "treated as family=2 with OBDZ-001 if pursued, fixed before any new run. No new execution "
            "authorized in this document."
        ),
        "changelog_v2_7_11": (
            "Mandate 3.25 -- a formal ratification, closing the last gate before OBDZ-001 can be "
            "implemented. VE delivered the population count (code/task_obdz_population.py, commits "
            "51d02a4/cfb8c8b) and, in the course of writing it, caught a real governance issue before "
            "running anything: the spec's bias-source citation ('h1_trend_up/h4_trend_up exist in "
            "code/mtf.py') was ambiguous about which loading path to use, and code/mtf.py::load_mtf() "
            "reads the native H1/H4/D1 CSVs via a bare pd.read_csv -- no discovery-safe loader, no split "
            "id, no cutoff, zero holdout masking. The native H1 timeframe carries status "
            "AWAITING_REGIME_MAP (no regime map ever assigned), meaning it is entirely sealed -- following "
            "the citation literally would have sourced this entire hypothesis's bias signal from sealed "
            "data, a real contamination. VE self-corrected to H1_from_M15_v2/H4_from_M15_v2 (the "
            "already-CONTEXT_DERIVED_VALIDATED, discovery-safe proxy timeframes), applying the identical "
            "ema20>ema50 formula through the standard discovery-safe loader with the same forward-safe "
            "merge convention already used throughout mtf.py itself, and independently verified its own "
            "_first_mitigation helper is logically identical to the frozen, already-fixed "
            "detect_mitigations[0] (post the v2.7.9 formation_idx+2 circularity fix) before running "
            "anything. Statistician independently re-verified the entire chain rather than accepting the "
            "self-correction at face value: read code/mtf.py directly (confirms the unmasked-read claim "
            "exactly), confirmed the manifest's own status split (native H1 = AWAITING_REGIME_MAP, "
            "H1_from_M15_v2/H4_from_M15_v2 = CONTEXT_DERIVED_VALIDATED), re-verified the mitigation-"
            "equivalence claim line by line, and independently re-ran the population script itself, "
            "reproducing every cited figure exactly. RATIFIES the context-derived path as the sole correct "
            "one (native H1 is impossible to make discovery-safe, not a genuine choice between two valid "
            "options) and amends the spec accordingly. Searched every Statistician document for the same "
            "risk pattern -- found no other instance outside this hypothesis's own evolving spec chain, but "
            "surfaced a SEPARATE, previously-unflagged legacy code cluster (code/s1.py, code/mstrat.py, "
            "code/run_mtf.py, code/wave1_harness.py) that actively calls the unsafe native-CSV path -- "
            "verified this does NOT affect any ratified verdict (code/trading_strategies.py::detect_s1, "
            "the function actually behind every SMC_S1 verdict issued this session, imports none of it), "
            "and recommends (without implementing) an explicit 'legacy pre-mask, do not use' label for that "
            "cluster to prevent recurrence -- noting that 2 of the 4 standing pre-existing test failures "
            "live in test_wave1_harness.py, consistent with an unmaintained legacy module. Confirms "
            "INSUFFICIENT_N triggers in NO regime (261/194/154 survivors, all >=10x the n>=25 threshold) "
            "and that Statistician's own prior concern about the variable horizon did not materialize -- "
            "over 94% of survivors in every regime receive the full 20-bar horizon. Recomputes the "
            "required-winrate range precisely on the real survivor ATR distribution rather than accepting "
            "CEO's cited figure at face value: median-based gives approximately [35%,37%] (recommended, "
            "more robust to the right-skewed ATR tail present in all 3 regimes) versus mean-based "
            "approximately [34%,36%] (matches CEO's own figure) -- explains the discrepancy and reiterates "
            "that neither range is the actual decision criterion, which remains mean(net_R)>0 computed "
            "per-trade, per the standing rule against any single frozen win-rate threshold. AUTHORIZES VE "
            "to implement the full state machine (bias -> cross-candle intersection -> ATR SL/TP1/TP2 -> "
            "partial exit -> net_R) and run the WP-5' block_bootstrap test (L>=28) strictly on the 130,491 "
            "M15_v2 discovery bars -- holdout remains sealed throughout, untouched by this authorization or "
            "by the population count itself."
        ),
        "changelog_v2_7_10": (
            "Mandate 3.24 -- formal pre-registration closing the composite hypothesis (proposed namespace "
            "OBDZ-001: Order Block x Demand Zone), the last open item flagged after Mandate 3.23. All "
            "primitives and prior decisions now exist; this mandate resolves the six remaining questions "
            "and locks the five-criteria pre-registration. Verified CEO's SL/TP arithmetic exactly: 50-60 "
            "pips = 0.68-0.81x ATR and 100-120 pips = 1.35-1.62x ATR at the cited current ~74-pip ATR "
            "(0.7 and 1.4 both fall inside these ranges); the SAME pip figures on discovery-era ATR "
            "(~17 pips) would be 2.94x/5.88x ATR -- a materially different, much-wider-relative-to-"
            "volatility strategy, independently confirming why ATR-relative sizing (not fixed pips) is "
            "necessary. Ratifies 0.7/1.4/2.1 as a declared design choice with disclosed rationale (a "
            "trader's pip intuition converted portably), explicitly still not a statistical derivation, "
            "per CEO's own stated preference for honest labeling over false rigor. Corrects the "
            "required-winrate framing: CEO's cited ~31% is the zero-cost limit (1/(RR+1) at RR=2.25), not "
            "the real value at any finite R -- computed the actual range using per-regime median ATR "
            "(~$1.99/$1.23/$2.16): required winrate moves in approximately [31%,38%], reported as a range "
            "per the standing no-single-w*-when-R-varies rule (Mandate 3.13). Resolves the six open "
            "decisions: (1) the ATR floor ($0.857) is ratified SUFFICIENT alone, no ceiling -- structural "
            "reason (R is proportional to ATR by construction here, unlike the old fixed-geometry filter "
            "which needed a ceiling against tail-concentration risk; extreme-bar risk is handled elsewhere "
            "by LiquidityVoid/maintenance-window exclusion); (2) the variable horizon is AGGREGATED for the "
            "primary H0 test (it is a property of the strategy's own mandatory-EOD-close definition, not a "
            "nuisance to control away -- stratifying by entry hour would test a different strategy), with "
            "a MANDATORY secondary diagnostic broken out by session and by realized-horizon bucket; (3) the "
            "cross-candle DemandZone x OB intersection is specified fully mechanically for the first time: "
            "same polarity, different formation event, forward-safe (DemandZone must predate the entry "
            "trigger bar), bounded to 460 bars (reusing the already-established empirical median-week "
            "constant rather than inventing a new number), same discovery block, standard interval overlap "
            "(not full containment); (4) the multiple-testing correction family is CONFIRMED SEPARATE at 1, "
            "distinct from the Block-3 family of 8 -- this construction shares no near-duplicate "
            "relationship with the Open-R S1-S20 grammar; (5) DECLINES to produce a numeric population "
            "estimate -- four compounding unmeasured rates (OB-formation, mitigation, cross-candle overlap, "
            "bias alignment), each individually uncertain by 2-5x, would compound to an order-of-magnitude-"
            "unreliable figure if multiplied by hand; instead PRE-REGISTERS the INSUFFICIENT_N>=25/regime "
            "threshold now, before any count exists, and requires a dedicated VE read-only population-"
            "count script (analogous to task1_atr_eligibility.py) applying the full compound filter chain "
            "before the statistical test itself may run. Proposes namespace OBDZ-001, checked for "
            "collision against the protected E0xx/S0xx/LM-00x prefixes, pending CEO ratification before VE "
            "uses it. Holdout SEALED, nothing executed."
        ),
        "changelog_v2_7_9": (
            "Mandate 3.23, three blocks, following directly from v2.7.8's cost correction. Block 1: VE "
            "(implementing Piece 1, code/order_flow.py commit 3fad03e) found the Mitigation/Rejection "
            "scan window (_scan_reactions, starting at formation_idx+1 = the impulse bar) is corrupted by "
            "construction -- the impulse candle's engulfment of the zone guarantees a spurious 'visit 1' "
            "on the bar that FORMED the OB, the same category of defect as E010 (a window containing the "
            "event it claims to measure). Statistician verified this algebraically and GENERALIZED it: "
            "the same guarantee holds for Rejection too, not only Mitigation as VE's own framing "
            "suggested. Ratifies VE's proposed fix (scan from formation_idx+2, skipping the impulse bar) "
            "as minimal and sufficient -- confirms no retroactive effect (neither function has run on "
            "real data or is consumed by any formalized family yet). Block 2: confirms the DemandZone x "
            "OrderBlock intersection is trivial exactly as VE implemented it (both primitives share the "
            "same anchor bar, so the geometric superset relation holds identically to plain OB) -- "
            "ratifies the cross-candle (different formation events) reading as the OPERATIVE one for the "
            "new hypothesis, since the same-candle reading adds no information. Ratifies both partial-"
            "exit open questions: stop-before-target on an ambiguous TP1 bar (consistent extension of the "
            "existing worst-case convention), and TP1+TP2 filling in the same bar (shown to be logically "
            "FORCED by TP1<TP2 monotonic ordering, not merely a permissive default). Block 3: "
            "independently re-executed both of VE's read-only scripts (task1_atr_eligibility.py, "
            "task2_cost_rerun.py) and reproduced every cited figure exactly, including the p-values, "
            "concentration ratios, and cell counts. Reclassifies SMC_S1's FINAL_VERDICT from "
            "REJECTED_NET_OF_COST to STATISTICALLY REJECTED: at the corrected cost and re-derived filter, "
            "the gross edge itself is near-zero and inconsistent in sign across the three regimes, not "
            "the small-positive-monotonic pattern the original scoped label depended on -- the "
            "distinction that label protected no longer applies. Discloses that Statistician's own prior "
            "estimate (6 of 8 families would clear the new cost bar) did not reproduce -- the real figure "
            "is 4 of 8 families with exactly one qualifying cell each, not general family-level "
            "profitability. Classifies S7 and S11 as TESTABLE BUT INSUFFICIENT EVIDENCE rather than "
            "REJECTED, per the lab's own Constitution (non-significance is not active disproof when the "
            "point estimate is positive) -- flags S7's bear cell for a mandatory concentration caveat "
            "(a single trade equals 13.6x the entire net sum; removing it flips the cell strongly "
            "negative). Marks S16 and S17 NOT TESTABLE on oracle grounds independent of any p-value: "
            "block_bootstrap@v1 is validated strictly for L>=H=20, and these two families run the SAME "
            "L=28 at their own much longer horizons (H=92, H=460), meaning L<H -- exactly the condition "
            "that invalidated the AR(1) regime at Mandate 3.17. This explicitly includes rejecting S17's "
            "deceptively low p-values (0.019-0.027) as usable evidence -- a low p from an uncalibrated "
            "estimator is a trap, not a finding. Declines to commission a fresh WP-5' recalibration at "
            "L>=92/L>=460 inline (a validation effort of comparable scope to the original, not a "
            "relabeling) -- leaves S16/S17 formally uncalibrated pending a dedicated future task. Rules "
            "the re-derived filter ([0.58,6.50)$, from the corrected cost/TICK) unconditionally "
            "authoritative over the old one, explicitly regardless of which one flatters any given cell -- "
            "the S16-correction sign flip this causes is disclosed as an expected dilution effect, not an "
            "error. Fixes the multiple-testing correction unit at family=8, extending SMC_S1's own "
            "already-established 'pooled across regimes' convention (not per-cell testing) uniformly to "
            "the other 7 families now tested in the same pass -- requests the pooled statistic itself "
            "from VE before any final (non-interim) call on S7/S11. Separately, RETRACTS Statistician's "
            "own v2.7.8 ATR-eligibility-floor 'hypothesis-threatening' finding as a self-caught error: the "
            "86-pip floor figure was computed at the corrected TICK=0.01 convention ($0.86), while the "
            "74-pip 'current market ATR' it was compared against was CEO's original citation in the OLD "
            "TICK=0.10 convention used throughout the session before this mandate ($7.40 real) -- an "
            "apples-to-oranges unit comparison, the exact class of mistake this entire correction effort "
            "exists to prevent, made by Statistician itself one mandate after demanding it of others. "
            "VE's independently-reproduced feasibility check confirms 89.75% of the 130,491 discovery "
            "bars clear the real $0.857 floor -- the population is not near-empty, it is the majority. "
            "Also resolves the variable-horizon-vs-oracle-coverage question: the new hypothesis's horizon "
            "is upper-bounded at 20 bars (min(entry+20,EOD) never exceeds 20), so the SAME L>=28 coverage "
            "already established for LM-001 continues to hold despite the horizon varying per trade."
        ),
        "changelog_v2_7_8": (
            "Mandate 3.22, four parts, cost-constant correction gating everything downstream (per CEO's "
            "explicit closing instruction: nothing re-runs until the cost is established). Part 1: TICK "
            "verified at the instrument-spec source (CEO's real Fusion Markets Classic account, XAUUSD "
            "quoted to 2 decimals) -- code/mstrat.py's TICK=0.10 is a 10x error, corrected to 0.01. "
            "cost_round_trip corrected 0.40->0.20 via spread_ticks=slip_ticks=5 (midpoint of CEO's stated "
            "5-15-tick spread range, combined with CEO's slip=spread convention, reconciled against the "
            "code's existing 2*(spread_ticks+slip_ticks)*TICK round-trip structure -- verified by reading "
            "one line further than the order's own citation, code/mstrat.py:63, which applies 2*cost, "
            "resolving an internal ambiguity in Statistician's own prior citations and catching a small "
            "slip in the order's own arithmetic). Verifies algebraically that R does NOT inflate 10x "
            "(R_dollars=distance_dollars+2*TICK -- only the small buffer term scales with TICK), a "
            "self-caught correction after an initial miscalculation suggested a near-degenerate eligible "
            "band. Organizes the exhaustive REOPEN enumeration across three mechanism-channels "
            "(cost-only, TICK-as-pip-divisor-only, compound) rather than a flat list: REOPENS "
            "displacement_filter (compound), rejection_ceiling (label-only, real distance unchanged, "
            "65->~650 pips), break_even_thresholds_SUPERSEDED, FINAL_VERDICT (REJECTED_NET_OF_COST and "
            "its CLOSED_DEFINITIVELY status), the 7-family descriptive table (commit 741e272 -- CEO "
            "explicit instruction NOT to hand-recalculate these figures, since edge_brut already carries "
            "the wrong-cost error; re-run from raw geometry instead), and LiquidityVoid's size threshold "
            "($1.20->$0.60). Confirms unaffected: the oracle (block_bootstrap@v1, a dependency-structure "
            "property with zero dollar dependency), market_structure D1-D7, session/horizon derivations, "
            "D-BPR tolerances (reinforced, not contradicted), and SMC_S1_v2 (v2.7.7) -- explicitly GATED "
            "pending this correction, per CEO's own closing instruction, not executed. Ratifies CEO's "
            "proposed rule (verify every model constant at the instrument-spec source, not the code), "
            "extended by Statistician to also require checking code lines adjacent to the cited ones. "
            "Part 2: ratifies the Order Block formation criterion (E010's already-frozen displacement/"
            "expansion qualifier + full body-engulfment of the prior OPPOSITE candle's body, no volume "
            "filter) -- explicitly distinguishes this from IFVG's inversion rule (formation vs inversion "
            "are different questions, not a contradiction as the order worried). Part 3: specifies "
            "DemandZone as a new, non-consuming, [High,Low]-bounded primitive, distinct from OrderBlock's "
            "consuming [Close,Open] body -- derived from the CEO's own subset framing (the subset relation "
            "only holds if DemandZone is the full range, not the body). Mechanical intersection condition "
            "specified with the trivial-same-candle-vs-substantive-cross-candle ambiguity flagged and the "
            "cross-candle reading recommended (not assumed) pending confirmation. Extends the anti-E010 "
            "validity/measurement window separation to this compound object. Part 4: pre-registers a new "
            "ATR-based partial-exit hypothesis (H1/H4 trend bias, M15 DemandZone/unmitigated-OB entry, "
            "0.7/1.4/2.1xATR stop/TP1/TP2, 75%/25% partial exit, variable horizon). CORRECTS the order's "
            "own weighted-RR arithmetic: 2.25R (not the order's stated 1.58R), since TP1/TP2 are stated as "
            "ATR-multiples while R is defined as SL=0.7xATR, not 1xATR -- 1.4xATR and 2.1xATR are actually "
            "2R and 3R once correctly converted, a favorable correction to the hypothesis's real profit "
            "potential. Specifies breakeven-at-entry-exactly (not entry+cost, avoiding double-counting "
            "cost already deducted once in net_R), resolves the 20-bar/end-of-day conflict as a plain "
            "minimum (not a priority ranking) with the resulting horizon explicitly declared VARIABLE (a "
            "deviation from the fixed-bar-count norm, to be reported as a distribution), specifies a new "
            "partial-exit net_R formula (proportional cost split, no double-charging for the extra exit "
            "leg, consistent with the account's zero per-lot commission), and eliminates the old "
            "[10.1,65.0)-pip eligibility filter (wrong on both the old cost AND the displacement-vs-ATR "
            "risk-construction mismatch) in favor of a freshly-derived ATR floor (~86 pips, same 3x-cost-"
            "stress-saturation logic reused from LM-001) -- FLAGGED as a hypothesis-threatening finding "
            "since it exceeds even CEO's own cited current market ATR (~74 pips) and far exceeds the "
            "historical discovery-period median (~17-18 pips), meaning the eligible population on existing "
            "discovery data may be minuscule or empty and must be verified directly before any execution, "
            "not assumed. Pre-registers the resulting hypothesis against the lab's 5 standard criteria, "
            "explicitly flagging the variable horizon and pending population as open items, not resolved "
            "ones. Holdout SEALED throughout; nothing executed in this document."
        ),
        "changelog_v2_7_7": (
            "SMC_S1_v2 stop-geometry design -- specification only, nothing executed, in response to the "
            "CTO's proposal to move the stop from spike+2 pips to the prior major swing (to dilute cost "
            "as a fraction of R). Measurement A specified: distance from next-open entry to the nearest "
            "prior CLASSIFIED market_structure.py swing more extreme than the current basin's own swing "
            "(degrades gracefully to the current stop if none exists), measured on the 34,670 RAW "
            "wick-sweep events (not the already-filtered 21,048, since applying the old filter before "
            "measuring the new geometry would be circular), reporting the full percentile distribution "
            "plus the fractions exceeding 65 and falling under 10.1 pips. Sensitivity-map decision ruled "
            "DIAGNOSTIC not FITTING -- optimizing for 'best stop' would be a second data-mining pass over "
            "already-consumed discovery data. Pre-registers, before any number exists, a decision rule on "
            "5 derived stop points (p25/p50/p75/p90 of the new distribution plus the 14.7-pip anchor): "
            "closed permanently if net dollar expectancy <=0 at all 5 stops in all 3 regimes; merits a "
            "new hypothesis only if net dollar expectancy >0 at 2+ wider stops (p75/p90) in 2+ regimes -- "
            "a pattern in the wide part of the distribution, not an isolated point; anything mixed is "
            "TESTABLE BUT INSUFFICIENT EVIDENCE, not a premature verdict either way. Addresses the "
            "R-vs-dollar concealment directly: mandates dual R-and-dollar reporting at every stop x regime "
            "cell, with DOLLARS as the primary decision variable -- a wider stop can show a better "
            "R-normalized edge while losing more real money, since a shrinking cost/R fraction doesn't "
            "mean fewer dollars lost, and the wider stop also moves the exit further from structural "
            "invalidation. Locks in SMC_S1_v2's required pre-registration if the diagnostic passes: "
            "derived stop with written justification, re-derived eligibility filter, reconfirmed-or-"
            "re-derived horizon, and a family-of-2 multiple-testing correction with SMC_S1 (same "
            "precedent as B.1/B2) with a mandatory declaration that the same discovery data is being "
            "consumed a second time for a near-identical hypothesis. Confirms SMC_S13's variant-3 "
            "formulation and the 12->20 horizon correction as accepted/necessary, unchanged. S10 remains "
            "open. Holdout SEALED throughout, no execution in this document."
        ),
        "changelog_v2_7_6": (
            "SMC_S1 (=LM-001) real-data verdict + SMC_S13 premise correction. Statistician independently "
            "re-ran VE's real-data execution (code/lm001_s1_execution.py, commit 0702958) directly -- "
            "reproduced every reported figure exactly: n=9,247/7,181/4,614 bear/bull/correction "
            "(=21,042=21,048-6 excluded at horizon boundary), expectancy -0.1677/-0.1845/-0.2234 R, "
            "p_wp5 1.0/1.0/0.996. Introduces REJECTED_NET_OF_COST, a new scoped sub-label distinguishing "
            "'no edge at all' from 'a mechanically-demonstrated positive gross edge smaller than "
            "execution cost' -- verified directly: best trade is 1.29% of total absolute loss (cost "
            "drag, not concentration), and net+cost=gross holds exactly at all three regimes "
            "(+0.072/+0.055/+0.017 R gross, monotonically decreasing bear->correction). Explicit "
            "delimitation: rejects H1:mu_netR>0 at the current cost/construction only, not the "
            "underlying sweep-reject mechanism or the gross edge's existence. Confirms the oracle's "
            "domain PARTIALLY for this application: the overlap-dependence mechanism transfers to "
            "net_R, but the WP-5' battery's homogeneous-variance assumption was never tested against "
            "net_R's real heteroskedasticity (R_i varies $1.21-$6.50, plus direction sign) -- doesn't "
            "change today's overwhelming non-rejection (any residual anti-conservative bias works in "
            "the safer direction here), and the per-regime n's fall within the range the same battery "
            "already validated via session stratification (asia/london/ny/late, all nominal). States a "
            "standing asymmetric rule: negative results from this pipeline are robust to the gap; a "
            "future POSITIVE result would not be, and must close the heteroskedasticity gap first, "
            "written now so it is not re-litigated per result. SMC_S13: catches that the order's stated "
            "motivation ('exploit the 85% generic gap-fill rate') is backwards -- verified directly that "
            "E004 (the same FVG-fill construct) already established 85% as the GENERIC BASELINE "
            "(OBSERVED_NOT_DISTINCTIVE) and that E004's own gaps fill LESS often than that baseline "
            "(71.48%, z~8.75) -- the opposite direction from any 'exploit the rate' framing. Rejects the "
            "'fills-more-than-baseline' reformulation on this evidence, notes 'continuation vs rejection "
            "at CE-50' as a separate untouched future direction, and adopts an execution-economics-only "
            "reformulation (does NOT claim above-baseline fill rates -- tests only whether the wider "
            "B1-anchored stop's geometry produces net_R>0 after cost at the unchallenged baseline). "
            "Fixes two technical problems in that reformulation: replaces the CE-50 limit order (M15 "
            "fill-ambiguity) with next-open market entry, consistent with every other Open-R family; "
            "reconfirms the 20-bar Group-A horizon (an implementation's '12 bars' was an error applying "
            "Group B's session-native rule to a point-event-triggered family, not a new decision). Notes "
            "SMC_S10's concept-reloop (Research Lab's cross-verification: BOS-as-displacement decouples "
            "magnitude from structure) as acknowledged, explicitly deferred, not resolved here."
        ),
        "changelog_v2_6_1": (
            "Mandate 3.21: resolves 4 chosen-not-derived parameters plus Module 7's nature before the "
            "CTO's Module 5/6/7 implementation proceeds -- VE had already refused to choose these four "
            "times, correctly routing them here instead. (1) Order Block volume filter ELIMINATED from "
            "the core primitive (verified: the volume column is of unconfirmed OTC tick-count-proxy "
            "provenance; E022/E031 sit in a 'testable but caveat every verdict' tier, E020 is held "
            "entirely on this issue) -- a persistent foundational primitive must not silently inherit a "
            "data-provenance risk that individual hypotheses each carry explicitly. (2) Expansion "
            "threshold resolved by reusing E010's already-frozen displacement-bar criterion verbatim "
            "(range>1.5x ATR14[i-1] AND body>=0.5x range) -- rejects the ungrounded 2.5x and a category-"
            "mismatched REACTION_THRESHOLD=1.0 substitution (forward reaction magnitude, not single-bar "
            "size). (3) Compression's lookahead risk (a full-history percentile would classify a 2013 "
            "bar using 2021 data) resolved via a rolling, strictly causal 460-bar window -- the empirical "
            "median week length already derived at Mandate 3.18/3.19, reused verbatim, also closing the "
            "threshold Mandate 3.19 deferred for SMC_S4/S8's Volatility/Expansion measure. (4) Sessions "
            "corrected -- confirmed exactly 4 exist (asia/london/ny/late, code/mtf.py:38), no 'Cash' "
            "session; use 'london'/'ny'. (5) Module 7 ruled a generic parametrizable confluence locator "
            "(analogous to count_bpr's tolerance parametrization), not a hardcoded hypothesis -- the "
            "given example lacks all 5 pre-registration criteria; any specific combination wanting to "
            "become its own hypothesis needs full separate pre-registration. Anchoring question answered "
            "per-primitive: Trend/Volatility/Session are already anchored to concrete blocked families "
            "(SMC_S9/S20, S4/S8, S5/S6/S19); three of Module 5's four named primitives (Breaker/"
            "Mitigation/Rejection) turn out to already be fully defined via reuse of already-ratified "
            "mechanics (E010/E012 inversion, the OB validity window's own touch event, D6 wick-sweep-"
            "reject), not new abstractions; only Compression and the still-open OB formation criterion "
            "remain genuinely unanchored, accepted as abstract definitions with the risk explicitly "
            "disclosed. LM-001 remains blocked by the CTO's library-first sequencing decision, not by "
            "any statistical issue -- oracle ratification and VE execution assignment stand unchanged. "
            "Holdout SEALED."
        ),
        "changelog_v2_6_0": (
            "Mandate 3.20: the oracle is ratified and LM-001 is unblocked. VE delivered all three WP-5' "
            "steps (commits 96d31ad/2935e81/edca965); Statistician verified by reading code directly, "
            "then independently reconstructed the exact 21,048-event population and reproduced both the "
            "buggy and corrected mean-spacing computations exactly matching VE's figures. (1) "
            "block_bootstrap@v1 ratified VALIDATED for the finite-memory overlap mechanism (n~21,048, "
            "L>=H=20) -- the pre-registered prediction confirmed exactly (FPR@0.05 nominal at all tested "
            "L, including L=10<H, strengthening the 3.17 argument that this was about the wrong CATEGORY "
            "of null process, not just a wrong L). Scoped as an explicit field, coexisting without "
            "ambiguity with the unchanged AR(1)-regime INVALIDATED_FOR_THIS_SCALE verdict. (2) Three "
            "findings: Void discrepancy confirmed resolved (VE's reproduction matches exactly); Q4 "
            "spacing metric genuinely RECONCILED (not left open) -- traced the exact mechanical cause "
            "(same-bar duplicate events inflate the naive 130,491/21,048=6.2 ratio; the corrected 8.52 "
            "excludes zero-length gaps between co-located events, verified directly), declares 8.52/"
            "57.4% authoritative, 6.2/69% superseded, scope of the correction stated explicitly (horizon "
            "derivation and FPR results unaffected); OB formation criterion confirmed still open, non-"
            "blocking. (3) Two governance rulings: Q5's real-return shocks confirmed as the same "
            "permitted calibration-input category as the geometry/density audits, with an explicit "
            "written boundary; code/order_block_void.py ruled to TRIGGER the CROSS_VERIFICATION_SPEC "
            "persistent-artifact exception flagged at Mandate 3.10 (VE both designed and implemented it "
            "with no independent check, unlike D1-D7's genuine Architect/VE cross-check) -- requires "
            "independent test verification by a different division before use. LM-001 UNBLOCKED: the "
            "frozen v2.5.5 spec confirmed unchanged, execution assigned to Validation Engine (already "
            "built and tested the entire adjacent infrastructure) not Flow A, holdout confirmed "
            "untouched (M15_v2 discovery blocks only), the other 11 not-yet-formalized families "
            "explicitly deferred per instruction until LM-001's end-to-end result reports back."
        ),
        "changelog_v2_5_9": (
            "Mandate 3.19: three deliverables. (1) Q1 (fully blocks WP-5's sample_event_positions, "
            "answered first per priority): reproduce the FULL empirical spacing/degree distribution "
            "(the existing spacing_histogram config field), not just the mean (7.64) -- avoids hiding "
            "regime-dependent behavior, the same failure mode that partially sank the original AR(1) "
            "battery. Q2-Q6 resolved: segment allocation fixed at empirical counts with boundary "
            "windows excluded (reusing the real audit's own rule); session-stratified density (not "
            "aggregate-only, direct precedent from the AR(1) battery's own regime-dependence); the 69% "
            "shared-horizon figure treated as a derived consequence, not an independently-imposed "
            "invariant; empirical (bootstrap-resampled) iid shocks, not normal, given this lab's "
            "repeatedly-documented heavy tails; shock-sum horizon aggregation, explicitly scoped to "
            "FPR calibration only, not the full net_R pipeline. L stays variable {10,20,28,40} "
            "downstream. (2) Four axiomatic definitions: Definition 1 (LiquiditySweep) and Definition 4 "
            "(PDH/PDL/Weekly fixed reference) RATIFIED as confirmations of already-implemented D6/"
            "detect_level_touches, verified directly in code. Definition 3 (LiquidityVoid) DERIVED as "
            "a hybrid temporal-OR-size criterion ($1.20 size threshold from the already-established 3x "
            "cost-stress convention, reused verbatim gapfind.py temporal rule) -- proven empirically "
            "that neither criterion alone covers the intended concept (248 size-only vs 119 time-only "
            "qualifying transitions on the actual 84,152-bar tested dataset, independently reproduced "
            "exactly). Definition 2 (Order Block/Breaker) FIXED on two problems: the zone contradiction "
            "(body=[Close,Open], not body+wick, preserving the wick's exclusive touch-mechanic role per "
            "MK-03 Q4/Q6 discipline) and E010's exact circularity risk, pre-empted by specifying a "
            "structurally-separate validity window (active until touched=consumed OR closed-through="
            "breaker) and measurement window (starts only at the qualifying event, never at OB "
            "formation) BEFORE any implementation. (3) Missing primitives scoped to only the actually-"
            "blocked SMC_S* families: Range (SMC_S12, upgraded to fully formalized) and MTF-Trend "
            "(SMC_S9/S20) resolved via recomposition of already-ratified/validated primitives, no new "
            "primitive needed; Volatility/Expansion (SMC_S4/S8) measure defined (reusing the lab's "
            "official E000 Parkinson standard), exact threshold deferred to its own derivation; SMC_S14/"
            "S15 confirmed still genuinely gapped (no primitive in either given module); SMC_S5/S6/S19 "
            "confirmed as a cheap Module-4 extension, not Module 5/6; Order Block/Breaker/Mitigation/"
            "Rejection and Compression confirmed NOT needed by any blocked family, not constructed. All "
            "families remain AWAITING_VALIDATION_ENGINE_CODE. Holdout SEALED, no backtest run."
        ),
        "changelog_v2_5_8": (
            "Mandate 3.18: formalizes all 20 SMC_S* families (S1-S20, verified as the legacy grammar's "
            "own full family list in code/mstrat.py's ECON dict -- not just the 15 'remaining' the order "
            "assumed). Flags that validation_engine/capabilities.json is the WRONG registration target -- "
            "its own deliberately_absent field explicitly excludes 'hypothesis-specific event primitives' "
            "and 'predefined session definitions' by design -- registers here instead (same authority/"
            "versioning as every prior LM-001/MK-03/MK-04 entry). Closes the horizon arithmetic gap (20 "
            "families cannot derive 20 distinct horizons from 4 session constants) via 4 declared groups: "
            "A=20 bars (LM-001's own immediate-reaction derivation, reused, not re-derived); B=native "
            "session length (asia/ny=32 bars, london=20, late=12, from the 4 already-established mtf.py "
            "boundaries); C=empirical day/week length, independently computed by Statistician by "
            "reconstructing the 17:00-NY day anchor and the derive_week_index gap rule directly on the "
            "130,491 discovery bars (median day=92 bars, median week=460 bars -- exactly matching "
            "institutional_levels.py's own '92 is just the most common value, not a constant' caveat); "
            "D=no horizon forced where the underlying primitive is missing. 9 families fully state-"
            "machine-specified using only the 4 ratified modules: SMC_S1 (=LM-001, referenced not "
            "re-derived), S2 (BOS+CHoCH fade), S3 (BOS+retest continuation), S7 (trend-pullback via "
            "swing sequence), S10 (displacement redefined as BOS, substitution disclosed transparently), "
            "S11 (CHoCH-primary reversal), S13 (FVG CE-50 reaction), S16 (PDH/PDL rejection, horizon "
            "group C), S17 (Weekly H/L rejection, COMPLETE-only population, horizon group C). 11 "
            "families honestly NOT forced: S5/S6/S19 (cheap gaps -- near-trivial missing extensions of "
            "institutional_levels' own day/week pattern to opening-range/session-level/session-open-"
            "close); S4/S8/S9/S14/S15/S20 (genuine primitive-class gaps -- volatility regime, ATR-"
            "relative distance, MTF trend, momentum/ROC, swing acceleration, all absent from the 4 "
            "ratified modules); S12 (partially gapped -- sweep-reject exists per end but no 'paired-"
            "basins-define-a-range' primitive); S18 (reclassified as a stratification dimension, not a "
            "standalone family, consistent with the already-documented 'S18 = 3 signals x 2 exits' "
            "finding from Mandate 3.10). Flags conceptual dedup-collision risk pairs (S2/S11 both CHoCH-"
            "based, S3/S7 both continuation-flavored) for mandatory hash verification once VE builds "
            "code -- declines to report a distinct-family count now, since D11/SS F requires a measured "
            "trade-log hash, not a guess. All 9 formalized families AWAITING_VALIDATION_ENGINE_CODE; "
            "none promoted to VALIDATED until WP-5' (Mandate 3.17) delivers the oracle. Holdout SEALED "
            "throughout, no backtest run."
        ),
        "changelog_v2_5_7": (
            "Mandate 3.17: three deliverables. (1) block_bootstrap@v1 VERDICT: INVALIDATED_FOR_THIS_"
            "SCALE for LM-001. VE delivered both a completed S8 curve (phi=0.40/0.0500, 0.45/0.0433, "
            "0.50/0.0467 all nominal, 0.60/0.0767 anti-conservative -- boundary ~phi=0.55, DERIVED not "
            "assumed, commit e441bcf) and a temporal density audit (8.64 avg concurrent events, 99.1% "
            "overlapping, degree mean 7.64/p90 13/max 26, same commit) in the same delivery, but "
            "declined VE's requested density->phi mapping onto the AR(1) curve -- explicitly disclosing "
            "the ordering problem (the mapping was supposed to be derived BEFORE seeing the density, "
            "never was) AND a deeper structural reason: the classical overlapping-window formula "
            "(rho_1=(20-6.2)/20=69%, cross-checked against VE's measured degree_mean) describes a "
            "FINITE-MEMORY process, unlike AR(1)'s infinite geometric decay -- a 28-bar block fully "
            "contains a 20-bar true dependency window in a way no AR(1) at any block length does, so "
            "lag-1-matching onto this curve targets the wrong instrument, not just an ill-timed one. "
            "Closes the order's own gap in the threshold rule ((0.50,0.55] unspecified) by reusing the "
            "manifest's own fail_closed_default: phi<=0.50 unblocks, phi>0.50 (including the untested "
            "band) routes to WP-5'. WP-5' concretely sized for LM-001: rebuild the S8 harness's null "
            "generator to simulate the TRUE overlapping-window mechanism (iid per-bar shocks, 20-bar "
            "sums at the real empirical inter-event-spacing distribution) instead of AR(1), re-run FPR "
            "across block lengths with the acceptance band fixed before running. (2) MK-03/MK-04 FULLY "
            "RATIFIED at commit 1930467 -- code read in full (not just the report, per explicit "
            "instruction), confirming detect_inverse_fvgs/detect_fvg_reactions/derive_week_index/"
            "detect_level_touches all implement the ratified decisions exactly; 34 tests independently "
            "reproduced (11+8+10+5), mypy --strict clean, the 4 pre-existing repo failures confirmed to "
            "import neither module; one cosmetic docstring-header nit flagged, non-blocking. (3) "
            "Registers SMC_S1/S2/S3/S13/S16 (Liquidity Sweep Reversal / Failed Breakout / Breakout "
            "Retest Continuation / Liquidity Void-Imbalance Fill / Previous Day Levels) under a rigid "
            "protected prefix -- verified the naming collision directly against the legacy grammar "
            "(code/mstrat.py) AND two production strategy_runtime implementation files (S13, S16); "
            "short form permanently banned for new families. Connects them to the 'Open-R' risk "
            "framework (CEO's name for the already-ratified LM-001 construction): the 10.1-pip floor is "
            "PORTABLE (derived from the cost/R formula alone) but the 65-pip ceiling is NOT (LM-001's "
            "own empirical p90) -- treated as a placeholder for the other four families pending their "
            "own geometry audits. Mandates the PROJECT_AUDIT.md D11/SS F trade-log-hash dedup pre-"
            "screening before enrollment, not after, given the legacy grammar's own already-measured "
            "27.0%-redundant/87%-single-parameter collapse. Status: AWAITING_VALIDATION_ENGINE_CODE. "
            "Holdout SEALED throughout, no backtest run."
        ),
        "changelog_v2_5_6": (
            "Mandate 3.14: resolves all nine open questions from VE's partial MK-03/MK-04 "
            "implementation (commit 7984670 -- implements only what is ratified, self-classifies each "
            "question by how much it blocks; BPR tolerance freeze rule confirmed intact through a "
            "third attempt). See mk03_mk04_ratification for the full field-by-field registration: "
            "Family 1 (D7-consumption, no invented session/day dimension), Family 2 (wick/close "
            "asymmetry now grounded directly in e015's touch_mask and e010/e012's close-based "
            "violation convention, both already-frozen code, not analogy alone), Family 3 (FVG "
            "block-boundary non-survival, D-WEEK reconfirmed, Q3-week derived from Q3-day via a gap "
            "rule), the sole fully-blocking primitive MK-03 Q4 (IFVG inversion) resolved by reusing "
            "E010/E012's frozen definition verbatim, and the three small mechanically-forced "
            "ratifications (MK-03 Q1, MK-04 Q4, MK-04 Q3-day reconfirmed)."
        ),
        "changelog_v2_5_5": (
            "Mandate 3.13: formulates LM-001's testable hypothesis against the same 5 criteria imposed "
            "on the 40 V0s (explicit numeric threshold, horizon as bar count, declared population/"
            "denominator, classification threshold, zero free parameters). Three flags resolved: (1) "
            "'12 bars' was a categorical error, not just underived -- TRACK_HORIZON/REVISIT_HORIZON "
            "(960/480) answer a different question (waiting for an OLD level to be revisited) than "
            "LM-001's immediate post-sweep reaction; the correct family is _profile.HORIZONS (1,3,5,10,"
            "20,50), already used for this exact measurement across all 40 edges. Decisive horizon = 20 "
            "bars, DERIVED by linking an already-real horizon value to an already-real boundary (london "
            "session length, mtf.py:37-38, exactly 5h = 20 M15 bars) -- not picked. Secondary horizons "
            "(1,3,5,10,50) reused verbatim, descriptive only, family stays 1 (same K6-decisive/K12-"
            "descriptive precedent as DC-0004). (2) No take-profit declared explicitly -- pure time-exit "
            "at the horizon. (3) exit=time's 1.6x concentration vs exit=rr2 (OUTCOME_DISTRIBUTION_v1.0.md, "
            "median net1 0.628 vs 0.387) confirmed directly and disclosed as a mandatory accompanying "
            "diagnostic (reusing NET_CONCENTRATION_INVENTORY_v1.0.md's own metrics), not a blocker -- "
            "time-exit is kept because it is the only construction coherent with continuous geometry-"
            "derived R. Corrects the order's stated population (22,887, floor-only) to the true "
            "combined-filter figure: N=21,048 (60.7% of 34,670) -- independently verified by "
            "reconstructing all 34,670 events with both bounds applied together; the order's number had "
            "not yet subtracted the 1,839 events (5.3%) also excluded by the 65-pip ceiling. Declines to "
            "confirm block_bootstrap@v1 by extrapolation (still textually UNVALIDATED per its own "
            "calibration record, and n=21,048 is >10x the largest calibrated point where even phi=0.6 "
            "had not fully converged to nominal) or substitute matched_null@v1 (verified ATR-scaled-only "
            "per D2_CLOSURE_SIZING_v1.0.md, wrong regime for LM-001's structural/geometric R) -- specifies "
            "a due-diligence calibration extension on the existing S8 harness instead, with a pre-"
            "registered acceptance band and the already-identified (not newly invented) WP-5' structural "
            "calibration as the named fallback."
        ),
        "changelog_v2_5_4": (
            "Mandate 5.1/5.2: registers LM-001's real-data geometry audit (VE, commit f901e3f) -- "
            "N=34,670 valid wick-sweeps on the 130,491 M15_v2 discovery bars (N excluded=1, boundary "
            "constraint fired exactly once as designed); AGGREGATE displacement fractions <40 pips=86.7%, "
            "[40,65)=8.0%, >=65=5.3% (worst cell ny=79.2%<40) -- confirms a 40-pip fixed floor would "
            "IMPOSE risk on the large majority instead of deriving it from geometry (D2's mechanic at 8x "
            "scale, $4.00 vs D2's $0.50 floor); CTO's rejection of the fixed floor is correct. Resulting "
            "risk-framework decision (STATISTICIAN_LM001_RISK_FRAMEWORK_DECISION_v1.0.md): (1) no single "
            "break-even win-rate threshold can exist -- w*(R)=(R+cost)/((RR+1)*R) is a continuous function "
            "of the geometry-derived R, not a frozen number (the same STAT-EXEC-CONTRACT SS7 formula, "
            "independently reproduced exactly across all six reference rows); outcome variable becomes "
            "mean net_R per trade, tested via the lab's existing bootstrap/permutation framework, not a "
            "win-rate-vs-threshold binomial test. (2) A displacement_filter (exclude <10.1 pips, R<$1.21) "
            "is RATIFIED, DERIVED (not chosen from the 18.0/14.0/10.1-pip reference points offered) from "
            "the lab's ALREADY-EXISTING 3x cost-stress convention (alpha_lab.py:197) reaching cost/R=100% "
            "-- excludes 34.0% aggregate (11,783/34,670; independently reconstructed by Statistician "
            "directly from code/lm001_geometry_audit.py:collect(), exact count not a percentile estimate; "
            "by-regime 25.7%/47.1%/23.2% bear/bull/correction, by-session 45.2%/30.5%/23.0%/50.4% "
            "asia/london/ny/late -- disclosed, not hidden). (3) The 65-pip rejection_ceiling is CONFIRMED "
            "(not re-derived) as tail-only exclusion (sits above aggregate p90=46.98, cuts 5.3% aggregate) "
            "-- does not share the fixed-floor's D2 mechanic since it excludes trades rather than "
            "widening R, and pre-empts the already-documented single-trade NET-concentration pathology. "
            "(4) R stays geometry-derived per eligible trade, confirmed never widened -- the displacement "
            "filter decides eligibility only, never modifies R of a trade that passes it. Also confirms "
            "D-BPR's three-tolerance count + smallest-tolerance-clearing-n>=25 freeze rule (already written "
            "into the skeleton by VE, commit 306d1dc) is NOT overridden, and reconfirms D3_bis/D-WEEK "
            "unchanged from the prior mandate."
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
            "geometry_audit": {
                "status": "COMPLETE",
                "source": "code/lm001_geometry_audit.py (commit f901e3f), STAT-LM001-GEOMETRY-MK03-MK04-v1.0 (49d0a14); independently reconstructed by Statistician directly from the same collect() path on real data -- percentiles matched VE's report to the 4th decimal.",
                "n_valid": 34670, "n_excluded_no_next_open": 1,
                "aggregate_fractions_pips": {"<40": 86.7, "[40,65)": 8.0, ">=65": 5.3},
                "aggregate_percentiles_pips": {"min": -3.58, "p10": 4.44, "p25": 7.96, "median": 14.68, "p75": 26.76, "p90": 46.98, "max": 607.55},
                "finding": "86.7% of displacements fall under 40 pips (worst cell ny=79.2%) -- a 40-pip fixed floor would IMPOSE risk on the large majority instead of deriving it from geometry, the D2 mechanic at 8x scale ($4.00 vs D2's $0.50 floor). CTO rejected the fixed floor on this basis.",
            },
            "execution_layer": {
                "entry": "next-bar-open after the maturation (wick-sweep) bar, direction determined mechanically by basin type (support matured -> long, resistance matured -> short) -- not a free choice, does not multiply the family.",
                "cost_round_trip": 0.40,
                "cost_round_trip_REOPENED": "See cost_constant_correction_v2_7_8 (top-level) -- TICK was verified at the wrong source (code, not the instrument spec) and is 10x too large; cost_round_trip is corrected to $0.20 (was $0.40). This field (0.40) is kept UNEDITED, marked REOPENED not deleted, per standing documentation discipline -- every dependent figure computed from it (displacement_filter, rejection_ceiling's pip labeling, break_even_thresholds_SUPERSEDED, FINAL_VERDICT) is REOPENED, not yet re-run.",
                "risk_construction": (
                    "RATIFIED (STAT-LM001-RISK-FRAMEWORK-DECISION-v1.0): GEOMETRY-DERIVED PER TRADE, not "
                    "fixed. R_i = (displacement_i + 2 pips buffer) * TICK, displacement_i = distance from "
                    "next-open entry to the manipulation wick extreme, measured directly per trade "
                    "(STAT-LM001-GEOMETRY-MK03-MK04-v1.0). NEVER widened to a floor for any trade that "
                    "passes the displacement_filter below -- widening is exactly the D2 mechanic (engine "
                    "imposes a risk the setup didn't request), here at 8x the scale that produced D2 "
                    "originally. The displacement_filter decides ELIGIBILITY only; it never modifies R of "
                    "an eligible trade."
                ),
                "stop_official_SUPERSEDED": {
                    "value": 4.00, "status": "SUPERSEDED",
                    "reason": "See geometry_audit.finding above -- kept here, marked SUPERSEDED not deleted, per standing documentation discipline.",
                },
                "displacement_filter": {
                    "status": "RE-DERIVED AND RATIFIED (Mandate 3.23) -- superseded the REOPENED state from v2.7.8. VE re-ran on raw dollar geometry (code/task2_cost_rerun.py, commit 64c4f1f, independently re-executed by Statistician with identical results): NEW filter = spike_$ in [0.58, 6.50) (was [1.01,6.50) at the wrong cost/TICK) -- floor re-derived from the corrected 3x-cost-stress saturation ((3*0.20-2*0.01)/0.01=58 pips = $0.58), ceiling unchanged in real dollars ($6.50, LM-001's own empirical p90, never cost-derived) -- pure unit relabeling to ~650 pips at TICK=0.01. NEW filter is authoritative unconditionally -- see FINAL_VERDICT_RECLASSIFIED_v2_7_9 for why the resulting dilution (more small-displacement events now eligible) is an expected mechanical consequence of the lower floor, not an error.",
                    "rule": "EXCLUDE trades with displacement < 10.1 pips (R < $1.21). A filter on ELIGIBILITY, not a floor on RISK -- never touches R of a trade that passes it.",
                    "derivation": (
                        "Derived, NOT chosen from the reference points offered (18.0/14.0/10.1 pips at "
                        "20%/25%/33% cost/R): the threshold is the displacement at which the lab's "
                        "ALREADY-EXISTING 3x cost-stress convention (code/alpha_lab.py:197, c2: "
                        "spread_ticks*=3, slip_ticks*=3 -> cost_stress=3*0.40=1.20, already used for "
                        "sensitivity testing per STATISTICIAN_NET_OF_COST_OUTCOME_DEFINITION_v1.0.md SS5) "
                        "would consume the ENTIRE risk of the trade (cost_stress/R=100%): "
                        "(displacement+2)*0.10=1.20 -> displacement=10.0 pips (10.1 on discrete data). At "
                        "1x/default cost this is cost/R=33.1% -- coincides with the loosest of the three "
                        "reference points, not because it was picked among them, but because that IS "
                        "where the existing stress convention saturates."
                    ),
                    "exclusion_fraction": {
                        "aggregate": {"n": 34670, "excluded": 11783, "excluded_pct": 34.0, "kept": 22887, "kept_pct": 66.0},
                        "by_regime": {
                            "bear": {"n": 13863, "kept": 10299, "kept_pct": 74.3, "excluded_pct": 25.7},
                            "bull": {"n": 14190, "kept": 7509, "kept_pct": 52.9, "excluded_pct": 47.1},
                            "correction": {"n": 6617, "kept": 5079, "kept_pct": 76.8, "excluded_pct": 23.2},
                        },
                        "by_session": {
                            "asia": {"n": 11219, "kept": 6153, "kept_pct": 54.8, "excluded_pct": 45.2},
                            "london": {"n": 8796, "kept": 6117, "kept_pct": 69.5, "excluded_pct": 30.5},
                            "ny": {"n": 12228, "kept": 9412, "kept_pct": 77.0, "excluded_pct": 23.0},
                            "late": {"n": 2427, "kept": 1205, "kept_pct": 49.6, "excluded_pct": 50.4},
                        },
                        "note": "bull and asia/late lose disproportionately more (structurally smaller displacements, per the geometry_audit percentiles -- bull median 10.7 pips, only marginally above the 10.1 threshold) -- disclosed, not hidden; does not change the threshold (derived from cost-stress, not class-balancing), but any future per-regime/session statistical test must read these post-filter N, not the raw geometry-audit counts.",
                        "verification": "Independently reconstructed by Statistician directly from code/lm001_geometry_audit.py:collect() on real data (exact count, not a percentile-table estimate).",
                        "CAUTION": "This 'kept'=22,887 is the FLOOR ONLY (>=10.1 pips, unbounded above) -- it does NOT yet subtract the rejection_ceiling exclusion below. The TRUE final population (both bounds) is combined_population.n=21,048, not this number. Kept here unedited (it is a correct floor-only figure) precisely so the two are never conflated again -- see combined_population.",
                    },
                },
                "combined_population": {
                    "rule": "The actual LM-001 hypothesis population is BOTH filters together: 10.1 <= displacement < 65.0 pips.",
                    "n": 21048, "pct_of_total": 60.7,
                    "by_regime": {
                        "bear": {"n": 13863, "kept": 9248, "kept_pct": 66.7},
                        "bull": {"n": 14190, "kept": 7186, "kept_pct": 50.6},
                        "correction": {"n": 6617, "kept": 4614, "kept_pct": 69.7},
                    },
                    "correction_note": "STAT-LM001-HYPOTHESIS-v1.0 (Mandate 3.13) caught and corrected an order-stated population of 22,887 for this exact population -- that figure was the displacement_filter's floor-only count (see its CAUTION field above), never reduced by the 1,839 events (5.3%) also excluded by rejection_ceiling. Independently verified by reconstructing all 34,670 events directly.",
                },
                "rejection_ceiling": {
                    "status": "RATIFIED_VALUE_STANDS_LABEL_REOPENED -- see cost_constant_correction_v2_7_8. The real dollar distance (65 pips x old TICK 0.10 = $6.50) is UNCHANGED (this bound was derived from LM-001's own empirical p90 displacement, never from cost) -- only its PIP LABEL changes under the corrected TICK: the same $6.50 relabels to approx 650 pips at TICK=0.01. A pure unit relabeling, not a re-derivation.",
                    "rule": "EXCLUDE trades with displacement >= 65 pips (TICK=0.10 labeling; approx 650 pips at corrected TICK=0.01, same real distance) -- tail rejection, not a floor. CEO's original proposal CONFIRMED on review, not re-derived.",
                    "reasoning": (
                        "65 pips sits above aggregate p90 (46.98) -- cuts only the genuine tail (5.3% "
                        "aggregate, 2.1%-8.4% per cell), not the distribution's mass (unlike the rejected "
                        "40-pip floor, which cut below the median). Pre-empts the already-documented "
                        "single-trade NET-concentration pathology (NET_CONCENTRATION_INVENTORY_v1.0.md) "
                        "rather than introducing a new risk."
                    ),
                },
                "targets": "Reward = 2 x R_i, R_i geometry-derived per trade (see risk_construction) -- RR=2.0 only, the fixed-stop RR_1.5 variant is dropped with the superseded stop.",
                "targets_SUPERSEDED": {
                    "stop_4.00": {"RR_1.5": 6.00, "RR_2.0": 8.00},
                    "stop_5.00": {"RR_1.5": 7.50, "RR_2.0": 10.00},
                },
                "break_even_thresholds_SUPERSEDED": {
                    "status": "SUPERSEDED -- a single w* cannot exist when R varies continuously per trade (STAT-LM001-RISK-FRAMEWORK-DECISION-v1.0)",
                    "formula": "w* = (1 + cost/S) / (RR + 1)",
                    "stop_4.00": {"RR_1.5": 0.44, "RR_2.0": 0.3667},
                    "stop_5.00": {"RR_1.5": 0.432, "RR_2.0": 0.36},
                },
                "horizon": {
                    "status": "RATIFIED (STAT-LM001-HYPOTHESIS-v1.0, Mandate 3.13)",
                    "primary_decisive": 20,
                    "unit": "M15 bars",
                    "derivation": (
                        "'12 bars' (as originally floated) was a categorical error, not just underived: "
                        "TRACK_HORIZON/REVISIT_HORIZON (960/480, edge_research/e015_order_block_"
                        "remitigation.py:47, e010/e012) answer 'how long to wait for an OLD level to be "
                        "revisited' -- a different mechanism than LM-001's immediate post-sweep reaction. "
                        "The correct comparison family is edge_research/_profile.py:11 HORIZONS=(1,3,5,10,"
                        "20,50), already built for exactly this measurement across all 40 edges "
                        "(movement_profile). 20 is DERIVED, not picked: it is the value in HORIZONS that "
                        "equals one full trading session's exact length (london=UTC[8,13)=5h=20 M15 bars, "
                        "code/mtf.py:37-38) -- reaction measured within a session-comparable window, not "
                        "smeared across sessions with different dynamics. No new number invented."
                    ),
                    "secondary_descriptive": [1, 3, 5, 10, 50],
                    "secondary_note": "Reused verbatim from _profile.HORIZONS, reported but NOT part of the tested family -- same precedent as DC-0004's K6-decisive/K12-descriptive split.",
                    "exit_boundary_safety": "Exit bar c+horizon must remain within the SAME discovery_range as the sweep bar c (same quarantine rule as the next-open entry) -- events where it does not are EXCLUDED, count disclosed by VE at execution, not hidden.",
                },
                "no_take_profit": "RATIFIED (STAT-LM001-HYPOTHESIS-v1.0): pure time-exit at the horizon (20 bars primary) -- NO take-profit target exists. Outcome is the price at close[c+20] regardless of intermediate path. Stated explicitly so this is never silently assumed either way by a future reader.",
                "exit_concentration_disclosure": {
                    "status": "MANDATORY, RATIFIED (STAT-LM001-HYPOTHESIS-v1.0)",
                    "finding": "Confirmed directly in docs/OUTCOME_DISTRIBUTION_v1.0.md: exit=time carries 1.6x the net concentration of exit=rr2 across the measured strategy corpus (median net1 0.628 vs 0.387). Time-exit is kept anyway (the only construction coherent with continuous geometry-derived R), but this is a known, accepted tradeoff, not an oversight.",
                    "requirement": "Any verdict on LM-001 must be accompanied by the same concentration diagnostics already used in NET_CONCENTRATION_INVENTORY_v1.0.md (best-trade share of total net_R, best-trade-removal collapse check) -- if the result is driven by 1-2 extreme net_R values, that must be visible alongside any positive verdict, never hidden behind a mean.",
                },
                "outcome_variable": (
                    "net_R per trade, NOT win-rate-vs-frozen-threshold. Formula (STAT-LM001-HYPOTHESIS-"
                    "v1.0): net_R_i = direction_i * (close[c+20] - open[c+1]) / R_i - cost/R_i, "
                    "direction_i = +1 (lower basin -> LONG) / -1 (upper basin -> SHORT), R_i computed from "
                    "that trade's own geometry-derived displacement and the already-established "
                    "cost_round_trip=0.40 (STATISTICIAN_NET_OF_COST_OUTCOME_DEFINITION_v1.0.md) -- avoids "
                    "discretizing a continuously-varying w*(R)=(R+cost)/((RR+1)*R) into one frozen number."
                ),
                "tie_break": "worst-case (stop-first) default, mandatory worst/best bracket per STATISTICIAN_M5_INDETERMINACY_THRESHOLD_SPEC_v1.0.md SS7c for any combination whose status depends on treatment.",
            },
            "family": "1 member (1 detector x 1 decisive horizon (20 bars) x RR=2.0-equivalent via net_R). Direction is mechanical, does not multiply the family. Secondary horizons (1,3,5,10,50) are descriptive only, excluded from the family by design (STAT-LM001-HYPOTHESIS-v1.0).",
            "statistical_test": (
                "RATIFIED (STAT-LM001-RISK-FRAMEWORK-DECISION-v1.0 + STAT-LM001-HYPOTHESIS-v1.0): "
                "H0: mu_netR<=0 vs H1: mu_netR>0 (one-sided), bootstrap/permutation on the continuous "
                "net_R series, BH-FDR alpha=0.05 over family of 1 (trivial, no adjustment needed at "
                "family size 1). REPLACES the exact one-sided binomial win-rate test -- a win-rate-vs-"
                "threshold test assumes a single frozen w*, which cannot exist when R varies continuously "
                "per trade.",
            ),
            "bootstrap_method": {
                "status": "FINAL (Mandate 3.20, STAT-ORACLE-RATIFICATION-LM001-UNLOCK-v1.0): block_bootstrap@v1 has TWO COEXISTING, NON-OVERLAPPING verdicts across two different regimes -- see calibration_status_by_regime below. LM-001 is UNBLOCKED.",
                "calibration_status_by_regime": {
                    "AR1_regime": {"status": "INVALIDATED_FOR_THIS_SCALE", "unchanged_since": "Mandate 3.17 -- infinite-memory phi parametrization, wrong instrument for LM-001's actual dependence."},
                    "overlap_mechanism_regime": {
                        "status": "VALIDATED",
                        "domain": "finite-memory overlapping-horizon dependence (LM-001's REAL mechanism, NOT AR(1)) -- n~21,048, L>=H=20 M15 bars.",
                        "evidence": "VE, commits 96d31ad/2935e81 (WP-5' battery): FPR@0.05 = 0.0450 (L=10, L<H) / 0.0400 (L=20,28,40, L>=H) -- pre-registered prediction ('L>=H fully contains the finite-memory dependence -> FPR should land nominal') CONFIRMED exactly, including the honest observation that L=10<H is ALSO nominal (finite-memory dependence is easier for block bootstrap than AR(1) regardless of L -- strengthens the 3.17 argument as being about the wrong CATEGORY of instrument, not just a wrong number).",
                    },
                    "explicit_non_interaction": "Ratifying the overlap-mechanism regime as VALIDATED does NOT overturn or narrow the AR(1)-regime INVALIDATED_FOR_THIS_SCALE verdict -- two different null processes, two different verdicts, both must remain readable without ambiguity in this registry.",
                },
                "q4_spacing_metric_RECONCILED": {
                    "status": "RECONCILED (Mandate 3.20), not merely left open",
                    "old_figure_SUPERSEDED": "6.2 bars / 69% shared horizon (Mandate 3.13) = 130,491 total discovery bars / 21,048 filtered events -- counts EVERY filtered event as its own density 'slot', INCLUDING multiple events co-located on the exact same bar (a single bar can produce simultaneous qualifying sweeps on different basins).",
                    "new_authoritative_figure": "8.52 bars mean spacing / 57.4% shared horizon -- computed directly from the EXACT empirical event positions (the same positions the WP-5' null generator conditions on), excluding zero-length gaps between co-located same-bar events. Verified directly by Statistician: of 21,045 theoretically possible gaps (21,048 events - 3 segments), only 15,305 are nonzero -- the other 5,740 are same-bar duplicate events.",
                    "scope_of_correction": "Affects ONLY the descriptive spacing/overlap-fraction summary figure. Does NOT affect the 20-bar horizon (derived independently from london session length, Mandate 3.13, never from this spacing figure) NOR the FPR battery results (the null generator conditions on exact positions, never on this summary statistic, confirmed directly by re-deriving both the buggy and corrected values from real data).",
                },
                "wp5_battery_raw_results": {
                    "source": "VE, commit 2935e81, edge_research/wp5_battery_results.json -- independently reproduced by Statistician (exact match on n_events, buggy mean_spacing=3.82, corrected mean_spacing=8.52).",
                    "fpr_by_L": {"10": 0.045, "20": 0.04, "28": 0.04, "40": 0.04},
                    "fpr_by_session_at_L28": {"asia": 0.015, "london": 0.025, "ny": 0.055, "late": 0.045},
                },
                "ob_formation_criterion_still_open": "RESOLVED (Mandate 3.22) -- see order_block_formation_criterion_v2_7_8 (top-level) and module_5_6_7_parameters.definition_2_OrderBlock_Breaker.implementation_status. Still non-blocking (no formalized family requires it), but no longer open.",
                "q5_calibration_input_boundary_CONFIRMED": (
                    "CONFIRMED (Mandate 3.20): Q5's real-M15-return shocks are the SAME permitted category as the geometry/density audits' price reads, "
                    "with an explicit boundary written so it is not silently extended: reading real prices is permitted when it characterizes STRUCTURE/SHAPE "
                    "(event positions, displacement geometry, the shape of a return distribution) WITHOUT touching LM-001's actual outcome (net_R sign, "
                    "direction, profitability) -- which stays sealed until the real net_R test (see execution_assignment below) actually runs. It would STOP "
                    "being the same category if prices were used to compute or preview the real net_R outcome ahead of that test."
                ),
                "curve_measured": {
                    "source": "VE, commit e441bcf: S8 curve completion at n=21,048 (edge_research/lm001_s8/complete_curve.py, B=10000, L=28, n_series=300) -- fills the gap where the originally-proposed phi=0.45 falls.",
                    "points": {"0.40": 0.0500, "0.45": 0.0433, "0.50": 0.0467, "0.60": 0.0767},
                    "boundary": "Nominal through phi=0.50; anti-conservative at phi=0.60. Boundary empirically between 0.50 and 0.60, approx phi~0.55 -- DERIVED from measurement, not assumed.",
                },
                "threshold_gap_closed": "The original rule (phi<=0.50 unblocks, phi>0.55 switches to WP-5') left (0.50,0.55] unspecified -- exactly where the measured boundary falls. Closed by reusing the manifest's own fail_closed_default principle, not a new tie-break: the untested band groups with the CONSERVATIVE side -- phi<=0.50 (the one measured nominal point) unblocks; phi>0.50, INCLUDING the untested (0.50,0.55] band, routes to WP-5'.",
                "density_measured": {
                    "source": "VE, commit e441bcf: code/lm001_density_audit.py on the 21,048-event [10.1,65.0] population.",
                    "aggregate": {"n": 21054, "avg_concurrent": 8.64, "pct_overlapping": 99.1, "degree_mean": 7.64, "degree_p90": 13, "degree_max": 26},
                    "cross_check": "Statistician's own overlap-fraction reference (marked as a benchmark, not a result): (20-6.2)/20=69% shared measurement window between consecutive events (21,048 events / 130,491 bars = 1 per 6.2 bars); independently cross-checked against VE's measured degree_mean=7.64 in a +/-20-bar window (expectation ~6.5 other events) -- consistent.",
                },
                "ordering_problem_disclosed": "Statistician was asked (prior mandate) to derive the density->phi mapping BEFORE seeing the measured density, so the mapping would not be modeled by the result. That derivation was never written; density and the completed phi curve arrived in the same delivery. Any mapping produced now cannot be shown independent of the result -- disclosed explicitly, same category as prior self-caught ordering issues (ratifying unread code, the 8->6 count correction), per Statistician's own standing discipline.",
                "why_no_mapping_was_produced": (
                    "Beyond the ordering problem: a density->phi mapping onto this AR(1) curve is not just untimely, it targets the WRONG INSTRUMENT. The classical overlapping-window "
                    "autocorrelation formula (rho_1=(k-m)/k, k=20-bar horizon, m=6.2-bar average spacing =~69%) describes a FINITE-MEMORY process -- "
                    "autocorrelation hits exactly zero beyond lag~20. AR(1)'s phi describes INFINITE geometric decay. Matching only the lag-1 correlation ignores exactly "
                    "the property that matters for a block bootstrap with L=28: a 28-bar block fully CONTAINS a 20-bar-wide true dependency window, something no finite "
                    "block length achieves against a true AR(1) (which never fully decays). A lag-1-matched phi could overstate OR understate the real risk -- the AR(1) "
                    "curve answers a different question than the one LM-001's actual overlap mechanism poses. This is why the resolution is a new, purpose-built "
                    "calibration (WP-5'), not a mapping onto the existing curve."
                ),
                "matched_null_v1": "Confirmed still NOT a valid substitute (D2_CLOSURE_SIZING_v1.0.md lines 27-32: ATR-scaled-only, wrong regime for LM-001's structural/geometric R) -- unchanged from the prior mandate's finding.",
                "wp5_prime_sizing_for_lm001": (
                    "Concretely sized, not just named (per explicit instruction): (1) build a null generator matching LM-001's REAL dependency mechanism -- "
                    "iid per-bar shocks, 20-bar-horizon overlapping sums, sampled at the TRUE empirical inter-event-spacing distribution (VE's own degree "
                    "histogram, not just the mean 6.2 bars); (2) run block_bootstrap@v1 (L in {10,20,28,40}) against this null at n~21,048, measuring FPR@0.05 "
                    "via the SAME harness already built (ve/calibration/synthetic_block_bootstrap.py, only the null generator changes -- no new infrastructure "
                    "beyond that swap); (3) acceptance band fixed BEFORE running this time (same nominal convention already used, ~FPR CI overlapping 0.05); "
                    "(4) if nominal at L>=28, block_bootstrap@v1 becomes validated specifically for the TRUE overlap mechanism -- a stronger result than any "
                    "AR(1) mapping could have given; if still anti-conservative, escalate L further or reconsider the estimator."
                ),
                "r_variance_note": "Connects to the still-open question in D2_CLOSURE_SIZING_v1.0.md line 55 (is R the right outcome variable when risk->0 -- explosive variance is a property of the statistic, not data resolution): LM-001's displacement_filter (R>=$1.21) already excludes the near-zero-risk regime (original D2 family's ~$0.05-0.12 stops) where that concern is sharpest -- does not resolve the general question, but LM-001 specifically does not inherit its worst case.",
                "wp5_prime_open_questions_RESOLVED": {
                    "status": "RESOLVED (Mandate 3.19, STAT-WP5-Q1-DEFINITIONS-PRIMITIVES-v1.0), read VE's skeleton (code/wp5_null_generator.py, commit db249ee) in full, mypy --strict verified directly before answering.",
                    "Q1_fully_blocking": "sample_event_positions reproduces the FULL empirical spacing/degree distribution (the existing spacing_histogram config field), NOT just the mean (7.64) -- matching only the mean risks hiding regime-dependent behavior in the degree tail, the exact failure mode that partially sank the original AR(1) battery (phi=0.4 nominal, phi=0.6 anti-conservative, hidden by a single-phi summary). Mean is reproduced automatically as a consequence of matching the full distribution -- not a separate target.",
                    "Q2_partial": "Event counts per discovery segment (bear/bull/correction) FIXED at empirical counts (9,254/7,186/4,614), not re-sampled -- consistency with the already-stratified-by-regime audit. Boundary window [c,c+H] exceeding the segment end: EXCLUDED, not truncated -- same rule as the real audit's own 6-excluded-at-horizon-boundary.",
                    "Q3_partial": "STRATIFIED by session, not aggregate-only -- direct precedent: the AR(1) battery's own regime-dependent FPR (phi=0.4 passes, phi=0.6 fails) shows aggregate summaries can hide anti-conservative pockets. Reproduce session densities (london 9.85/ny 9.36 vs asia 6.92/late 6.27); report FPR both aggregate and per-session.",
                    "Q4_clarification": "'69% shared horizon' is a DERIVED CONSEQUENCE of spacing+H=20, not an independently-imposed invariant -- algebraically (H-spacing)/H. Treated as a post-generation verification check (confirms Q1 was implemented correctly), not an input constraint (imposing it separately risks an over-constrained, potentially inconsistent system).",
                    "Q5_partial": "Shocks drawn via bootstrap resampling of REAL empirical M15 per-bar returns from the discovery bars -- NOT assumed normal. Heavy tails are an already-repeatedly-documented property of this lab's own trade/return data; a normal assumption would understate tail risk in the dangerous (over-confident) direction.",
                    "Q6_clarification": "Shock-sum aggregation, consistent with Q5 -- under empirically-resampled shocks (not an artificial proxy), the shock-sum over the window IS the faithful price-move reproduction (close[c+H]-open[c+1] literally equals the sum of intermediate returns), so there is no real tension between 'sum' and 'faithful reproduction' once Q5 is resolved empirically. Explicit scope: this calibrates the DEPENDENCE STRUCTURE for FPR only, not the full net_R pipeline (R-normalization, cost, direction) -- that remains the substantive LM-001 test itself.",
                    "L_stays_variable": "L in {10,20,28,40} remains a downstream estimator parameter, not fixed by this resolution, per VE's own skeleton design.",
                },
            },
            "success_failure_criteria_preregistered": {
                "success": "Mean net_R significantly > 0 (BH-FDR alpha=0.05, family of 1) on pooled counts across ELIGIBLE regimes (see insufficient_n_rule).",
                "failure": "Does not pass BH-FDR, PROVIDED at least one regime had sufficient n -- a failure on insufficient data is a different category, not a statistical failure.",
            },
            "UNBLOCKED_status": "UNBLOCKED (Mandate 3.20) -- block_bootstrap@v1 VALIDATED for the overlap mechanism at this exact scale/L (see lm_001_preregistration parent -> execution_layer.bootstrap_method). Frozen spec (v2.5.5) CONFIRMED UNCHANGED: population 21,048 filtered [10.1,65.0) pips, mechanical direction, 20-bar horizon (london-session-derived), pure time-exit at c+20 (no take-profit), net_R outcome, block bootstrap L>=28 vs H0:mu_netR<=0 (one-sided), family=1.",
            "execution_assignment": {
                "executor": "Validation Engine, NOT Flow A",
                "reasoning": "VE already built and tested the entire adjacent infrastructure specific to LM-001 (geometry audit, density audit, WP-5' null generator, the wired block_bootstrap/wp5_battery.py harness) -- executing the real test is a minimal, natural extension of already-verified code, reusing block_bootstrap.run() on the REAL net_R series instead of a synthetic null. Flow A's infrastructure (_profile.py, movement/context/robustness battery) is scoped to the original 40 E0xx hypotheses' template, not to Open-R/net_R/block-bootstrap testing.",
                "holdout_confirmation": "LM-001's population is entirely within the M15_v2 discovery blocks (130,491 bars) -- execution does not touch the sealed holdout.",
                "scope_note": "Per explicit instruction, the other 11 not-yet-formalized SMC_S* families (S4/S8 awaiting the Parkinson threshold, S5/S6/S19 cheap gaps, S14/S15 genuinely gapped) are NOT completed now -- LM-001 (=SMC_S1) runs first, end to end, as a test of the whole chain before investing in formalizing the remaining nineteen.",
            },
            "FINAL_VERDICT": {
                "status": "REJECTED_NET_OF_COST -- SUPERSEDED (Mandate 3.23, see FINAL_VERDICT_RECLASSIFIED_v2_7_9 top-level field): re-run at the corrected cost=0.20 on re-derived raw-geometry filters shows edge_brut_$ near-zero and inconsistent in sign across regimes (not the small-positive-monotonic pattern this original verdict was based on) -- the REJECTED_NET_OF_COST label no longer applies (its whole point was distinguishing a real-but-uneconomic gross edge from no edge; that distinction no longer holds). New label: STATISTICALLY REJECTED. This entry kept UNEDITED as the historical record of what was measured at the wrong cost, per standing documentation discipline (mark SUPERSEDED, never silently delete or patch numbers in place).",
                "verified_by": "Statistician independently re-ran code/lm001_s1_execution.py (commit 0702958) directly -- all reported figures reproduced exactly.",
                "results_by_regime": {
                    "bear": {"n_trades": 9247, "winrate": 0.473, "expectancy_R": -0.1677, "net_sumR": -1550.8, "p_wp5": 1.0, "gross_edge_R_est": 0.072},
                    "bull": {"n_trades": 7181, "winrate": 0.458, "expectancy_R": -0.1845, "net_sumR": -1324.7, "p_wp5": 1.0, "gross_edge_R_est": 0.055},
                    "correction": {"n_trades": 4614, "winrate": 0.490, "expectancy_R": -0.2234, "net_sumR": -1030.6, "p_wp5": 0.996, "gross_edge_R_est": 0.017},
                },
                "population_confirmed": "9,247+7,181+4,614=21,042 = 21,048-6 (excluded at horizon boundary, Q2) -- matches exactly.",
                "scope_delimitation": (
                    "REJECTED_NET_OF_COST is a NEW scoped sub-label (same delimited-scope discipline as the 47 exclusion-dependent hypotheses "
                    "and the 3 structural-V1 edges), distinguishing 'no edge at all' from 'a mechanically-demonstrated positive gross edge smaller "
                    "than execution cost'. What IS rejected: H1: mu_netR>0 at the current $0.40 round-trip cost, on the frozen Open-R construction "
                    "(spike+2 pips, no floor, [10.1,65.0) filter, 20-bar horizon, pure time-exit), on the 3 M15_v2 discovery regimes. What is NOT "
                    "rejected: the sweep-reject mechanism itself, or the existence of a gross geometric edge -- verified mechanically (not chosen): "
                    "the single best trade is only 1.29% of total absolute loss (cost drag distributed across the population, not concentration/"
                    "fragility -- opposite of the NET_CONCENTRATION_INVENTORY collapse pattern), and net+cost=gross arithmetic holds exactly at all "
                    "three regimes (gross_edge_R_est above, monotonically decreasing bear->correction). This verdict does not extrapolate to a "
                    "different cost structure or a different risk construction -- either would require re-testing, not inference from this result."
                ),
                "oracle_domain_question": {
                    "status": "CONFIRMED PARTIALLY, with explicit limits",
                    "confirmed": "The overlap-dependence mechanism (what WP-5' calibrated) transfers to net_R -- R-normalization and direction are per-event scalars that don't change WHICH events share future shocks, only how the shared-shock sum converts to R units.",
                    "not_tested": "The WP-5' battery used a relatively homogeneous-variance outcome series (raw shock-sums); net_R introduces real heteroskedasticity (R_i varies $1.21-$6.50 per trade) and sign changes (direction) not explicitly represented in that battery -- a genuine methodological gap, disclosed not hidden.",
                    "why_todays_verdict_stands": "The result is an OVERWHELMING non-rejection (p~1.0/1.0/0.996, far from any decision threshold), not a borderline call sensitive to a small calibration error. Any residual anti-conservative bias (the theoretical risk of the method) would make the test MORE likely to find false positives, not more likely to hide a real negative -- so residual miscalibration risk would work in the SAFER direction for this specific negative conclusion.",
                    "n_scope_already_partially_covered": "The three regime n's (4,614/7,181/9,247) fall within the range already tested via the SAME WP-5' battery's session-stratified FPR results (Mandate 3.20): asia n=5,915/london n=5,635/ny n=8,386/late n=1,118, all nominal. The smallest regime (correction, 4,614) is comparable to ny (8,386) and above late (1,118) -- not a fresh extrapolation.",
                    "standing_asymmetric_rule": "NEGATIVE results from this pipeline are robust to the heteroskedasticity gap (per the argument above). A FUTURE POSITIVE result from the SAME pipeline would NOT be equally robust -- it must close the heteroskedasticity/exact-n gap via a dedicated WP-5' battery extension (real R_i/direction, not homogeneous shock-sums) before being trusted. Written now as a standing rule, not to be re-litigated per future result.",
                },
            },
            "SMC_S1_v2_stop_geometry_design": {
                "status": "SPECIFICATION ONLY -- nothing executed. CTO proposes moving the stop from spike+2 pips to the prior major swing, to dilute cost. No one had measured the resulting distance before this design.",
                "measurement_A_spec": {
                    "population": "The 34,670 RAW wick-sweep events (D6/D7), not the already-filtered 21,048 -- applying the OLD [10.1,65.0) filter before measuring the NEW geometry would be circular, since the whole point is to check whether that filter still holds.",
                    "geometric_definition": "'Prior major swing' (market_structure.py Swing/StructureLabel, already ratified) = the nearest CLASSIFIED swing of the appropriate side (LOW for a support-side sweep, HIGH for resistance) that is STRICTLY EARLIER than AND MORE EXTREME than the swing that formed the current basin. If no such swing exists in the same block (D4), the reference degrades gracefully to the basin's own swing -- no artificial widening. Flagged explicitly: 'major' is interpreted as magnitude (more extreme), not mere chronological precedence -- if CTO intended the latter, this needs reconfirmation before VE codes it.",
                    "distribution_to_report": "min/p10/p25/median/p75/p90/max of the new distance (pips), aggregate and per-regime, plus the fraction exceeding 65 pips (old ceiling) and the fraction under 10.1 pips (old floor).",
                    "edge_case": "Events with no prior CLASSIFIED swing in-block (near a block's start, D3_bis) are EXCLUDED and counted separately, not silently dropped.",
                    "consequence_already_specified": "If the majority exceed 65 pips, the [10.1,65.0) eligibility filter (derived for the OLD spike-based stop) no longer applies mechanically and must be RE-DERIVED for the new geometry, not reused blindly.",
                },
                "sensitivity_map_decision": {
                    "ruling": "DIAGNOSTIC, not FITTING -- unambiguously. Optimizing for 'best stop' would be a second data-mining pass over already-consumed discovery data, with zero evidentiary value.",
                    "stop_set": "5 points, DERIVED from measurement_A_spec's own resulting distribution, not chosen freely: p25/p50/p75/p90 of the new distance distribution, plus the original 14.7-pip stop as a reference anchor.",
                    "decision_rule_PRE_REGISTERED_BEFORE_ANY_NUMBER": {
                        "CLOSED_PERMANENTLY": "Net DOLLAR expectancy <=0 at ALL 5 stops, in ALL 3 regimes -- negative everywhere regardless of stop; no SMC_S1_v2 is formulated.",
                        "MERITS_NEW_HYPOTHESIS": "Net DOLLAR expectancy >0 at 2+ of the wider stops (p75, p90), in 2+ of the 3 regimes -- a PATTERN in the wide part of the distribution (where the cost-dilution mechanism should act if real), not a single isolated point.",
                        "AMBIGUOUS_NEITHER": "Any mixed pattern (single isolated positive point, or positive in only one regime) -- labeled TESTABLE BUT INSUFFICIENT EVIDENCE, not a premature verdict either way. Requires further data, not a re-test on the same discovery.",
                    },
                },
                "dollar_vs_R_reporting_rule": {
                    "problem_confirmed": "Verified CEO's arithmetic exactly: stop 14.7 pips -> R=$1.67 -> cost 24%; 30 pips -> R=$3.20 -> cost 12%; 45 pips -> R=$4.70 -> cost 8.5%. The same +0.072 R gross edge (bear) is ~12 cents/trade at the 14.7-pip stop but ~34 cents at a 45-pip stop ONLY IF the gross R-edge stays constant as the stop widens -- an untested, likely-false assumption (win rate and outcome distribution plausibly change with stop width, and a wider stop also moves the exit further from structural invalidation, increasing realized dollar loss on stop-outs at a given failure rate).",
                    "rule": "Every stop x regime cell in the sensitivity map reports BOTH expectancy_R AND expectancy_dollars. DOLLARS is the PRIMARY decision variable for the pre-registered thresholds above -- R improving while dollars do not must NOT be read as passing the 'merits new hypothesis' bar.",
                },
                "if_premise_survives_SMC_S1_v2_requirements": {
                    "stop": "DERIVED (not picked from the sensitivity map itself, which would be fitting in disguise) from the actual measured geometry, with written justification.",
                    "eligibility_filter": "RE-DERIVED for the new geometry, not the reused [10.1,65.0) blindly.",
                    "horizon": "RECONFIRMED or RE-DERIVED -- a wider stop may change how long the thesis needs to play out; the 20-bar horizon is not assumed to carry over automatically.",
                    "family_correction": "SMC_S1 and SMC_S1_v2 are treated as a FAMILY OF 2 for any multiple-testing correction -- same precedent already applied to the B.1/B2 near-duplicate hypotheses. Two in-sample tests on the same discovery data for closely-related hypotheses are NOT two independent proofs, regardless of how different the numeric results look.",
                    "mandatory_declaration": "Any SMC_S1_v2 pre-registration document must explicitly state the discovery data (130,491 bars) is being consumed a SECOND time for a near-identical hypothesis.",
                },
                "full_design_document": "ai_quant_lab statistician/STATISTICIAN_STOP_GEOMETRY_SENSITIVITY_DESIGN_v1.0.md",
            },
            "insufficient_n_rule": (
                "Reused convention: n>=25 (Discovery Screen V1 / persistence-leaderboard threshold), not a "
                "new number. Evaluated on the POST-FILTER population (displacement in [10.1,65) pips), NOT "
                "the raw wick-sweep count -- the filter changes the actual eligible/tradeable universe. "
                "Per-regime: <25 qualifying events -> that regime marked INSUFFICIENT_N for this "
                "hypothesis, EXCLUDED from the pooled count (never treated as zero or as failure), fraction "
                "disclosed explicitly. Pooled: if total n across eligible regimes stays <25 after exclusions, "
                "the whole hypothesis's verdict is TESTABLE BUT INSUFFICIENT EVIDENCE (established "
                "vocabulary, e.g. DC-0004) -- NOT REJECTED, with the D3 blind window recorded explicitly as "
                "the likely primary cause if applicable, not hidden."
            ),
            "workflow_confirmed": "Validation Engine implements after this ratification; a different division (not the producer) verifies conformance per CROSS_VERIFICATION_SPEC; execution on real data awaits both -- not triggered by this registration.",
            "full_preregistration_document": "ai_quant_lab statistician/STATISTICIAN_MARKET_STRUCTURE_RATIFICATION_AND_PREREG_v1.0.md",
            "full_risk_framework_decision_document": "ai_quant_lab statistician/STATISTICIAN_LM001_RISK_FRAMEWORK_DECISION_v1.0.md",
            "full_hypothesis_formulation_document": "ai_quant_lab statistician/STATISTICIAN_LM001_HYPOTHESIS_FORMULATION_v1.0.md",
        },
        "mk03_mk04_ratification": {
            "status": "FULLY RATIFIED (Mandate 3.17, STAT-BLOCKBOOTSTRAP-MK-SMC-v1.0), code-complete at commit 1930467",
            "code_verification": "Statistician read code/imbalance_mechanics.py and code/institutional_levels.py IN FULL at commit 1930467 (not just the diff/report, per explicit instruction) -- confirmed detect_inverse_fvgs, detect_fvg_reactions, derive_week_index, detect_level_touches all implement exactly the ratified decisions below, no silently-introduced new conventions. mypy --strict clean; 34 tests pass (test_mk03_mk04.py + test_mk03_mk04_closures.py + test_structure.py + test_detect_breaks_rearm.py = 11+8+10+5, exact count independently reproduced); the 4 pre-existing repo test failures confirmed (grep) to import neither module. One cosmetic nit found by reading the code, non-blocking: institutional_levels.py's header docstring still says 'IMPLEMENTARE PARTIALA' though every decision inside is RATIFICAT/RESOLVED.",
            "source": "CEO Mandate 3.14 -- VE's partial implementation (commit 7984670, code/imbalance_mechanics.py + code/institutional_levels.py): implements only what is ratified, leaves the rest NotImplementedError, self-classifies each open question by how much it blocks. Statistician verified the commit directly (git show, no checkout -- discovery-mk-matrix-v1 occupied by a sibling worktree) before ratifying.",
            "bpr_tolerance_freeze_confirmed": "count_bpr's tolerances=(0.0,0.10,0.25) verified intact in commit 7984670 -- survived a third attempt to hard-freeze a single tolerance. The smallest-tolerance-reaching-n>=25 freeze rule (STAT-LM001-GEOMETRY-MK03-MK04-v1.0) stays the consumer's decision, not re-litigated.",
            "family_1_consumption": {
                "status": "RATIFIED",
                "rule": "MK-03 Q5 (FVG mitigation) and MK-04 Q5 (PDH/PDL level touch) both resolve as D7-analog: consumed once, never re-armed. Lifetime stays IDENTICAL to D7 -- consumed within the entity's already-established existence window (current discovery block for FVGs; current-day availability window for PDH/PDL, already fixed by D3_bis/MK-04 Q4) -- NO new 'session/day' lifetime dimension is added.",
                "rejected_addition": "The originally-proposed 'eliminated from the active matrix for the rest of the session/day' clause is REJECTED as stated -- D7 specifies no session/day-scoped lifetime, and inventing one for FVGs (which have no natural session boundary) would need its own derivation that was never given.",
                "pdh_real_question_answered": "VE's actual question (not the tautological daily-recompute fact) was: within the SAME day, does a matured PDH survive a second touch? Answer: NO -- consumed at first touch within its existing daily availability window. Not a new dimension, just D7 applied to the window already fixed elsewhere.",
            },
            "family_2_wick_close_asymmetry": {
                "status": "RATIFIED, now grounded in direct code precedent, not analogy alone",
                "gradient": {
                    "1_ce50_mitigation_wick": "low[i]<=ce_50 (bullish) / high[i]>=ce_50 (bearish) -- a touch, matches the wick-based touch_mask ALREADY used in edge_research/e015_order_block_remitigation.py:98 ((low<=zone_high)&(high>=zone_low)), applied at the CE-50 level.",
                    "2_full_fill_wick": "low[i]<=lower (bullish) / high[i]>=upper (bearish) -- deeper touch, still wick, not yet inversion.",
                    "3_inversion_close": "close[i]<lower (bullish) / close[i]>upper (bearish) -- REUSED VERBATIM from two already-frozen V0s, edge_research/e010_breaker_block_snatch.py and e012_inverted_fvg.py, both independently using 'the first later bar's close beyond the zone edge -- a decisive violation, not just an intrabar wick' for their own polarity-flip event. Not derived anew -- identical wording confirmed in both files.",
                },
                "reasoning": "A touch (wick) shows only that price momentarily revisited the zone -- says nothing about which side won that bar. A close beyond the far edge shows the opposite side WON that bar -- a capitulation, not a visit. Same mechanic D6 already uses (wick for penetration, close for return), now doubly corroborated by two frozen V0s using an identical convention for the analogous event.",
                "consumption_link": "The original FVG consumes (Family 1/D7) at first CE-50 touch, regardless of later full-fill or inversion (those are additional recorded properties, not re-arm events). An inverted IFVG is a FRESH entity with its own independent consumption cycle for reaction in the new direction -- matches E010/E012's own 'revisit and react in the new, flipped-polarity direction' design exactly.",
            },
            "family_3_block_boundary_and_week_anchor": {
                "status": "RATIFIED, unconditional support",
                "fvg_block_survival": "FVGs do NOT survive a discovery-block boundary -- exact D4-analog: a zone whose formation depends on bars from one block cannot be tracked/acted upon in a later block without violating quarantine. At block end, the FVG (mitigated or not) simply exits scope -- not marked 'expired unmitigated', just no longer a trackable entity, same as a swing that doesn't survive D4.",
                "discrete_weeks_partial_flag": "Reconfirmed, unchanged from D-WEEK: discrete weeks anchored to the block calendar, days_contributing + COMPLETE/PARTIAL.",
                "q3_week_resolved": "MK-04 Q3-week (week boundary) resolved by DERIVING from the already-resolved Q3-day (17:00 NY DST-aware anchor, code/resample_ny.py), not a new independent clock: week_index increments at the first bar whose day_index follows a >1-calendar-day gap from the prior in-block day (the weekend) -- does not block the module (which takes week_index from the caller) but specifies the caller-side derivation so it is not chosen ad hoc.",
            },
            "mk03_q4_ifvg_inversion_RESOLVED": {
                "status": "RESOLVED -- the only fully-blocking primitive, per VE's own classification",
                "definition": "Bullish FVG inverts the first time a LATER bar has close < lower (the zone's far/low edge) -- a decisive violation via CLOSE, not an intrabar wick. Bearish symmetric: close > upper. Resolves both ambiguities: (a) NOT single-bar body-engulfment -- the first later close beyond the edge, however many bars it takes; (b) CLOSE, not wick.",
                "source": "Reused verbatim from two already-frozen V0 hypotheses (edge_research/e010_breaker_block_snatch.py 'Breaker flip', edge_research/e012_inverted_fvg.py 'Inversion') -- not derived anew, independently confirmed identical in both files.",
                "unblocks": "code/imbalance_mechanics.py:detect_inverse_fvgs",
            },
            "small_ratified_items": {
                "mk03_q1_lookahead": {"status": "RATIFIED", "rule": "confirmed_idx=i+1, mechanically forced -- a 3-bar window cannot be known before bar i+1, exact D1 analog, no lookahead-safe alternative."},
                "mk04_q4_availability": {"status": "RATIFIED", "rule": "available_idx = first bar of the current period (prior period is fully known at current period's open) -- same forced mechanic as D1, applied to daily/weekly levels."},
                "mk04_q3_day": {"status": "RECONFIRMED, already CEO-resolved", "rule": "17:00 New York, DST-aware anchor (code/resample_ny.py) -- non-blocking for the module, which takes day_index from the caller."},
            },
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_MK03_MK04_NINE_QUESTIONS_RESOLUTION_v1.0.md",
            "full_code_ratification_document": "ai_quant_lab statistician/STATISTICIAN_BLOCK_BOOTSTRAP_VERDICT_MK_RATIFICATION_SMC_NOMENCLATURE_v1.0.md",
        },
        "smc_s_nomenclature": {
            "status": "REGISTERED (Mandate 3.17) -- AWAITING_VALIDATION_ENGINE_CODE, no detector built yet for any of the 5 families",
            "collision_verified": "Confirmed directly in code/mstrat.py's legacy REGISTRY: S1='liquidity-sweep mean-reversion', S2='failed-breakout fade', S3='breakout-retest momentum', S13 (FVG grid: fvg/mode/stop/exit), S16 (levels grid: pdh/pdl/pd_open/pd_close/pd_mid) all already exist. S13 and S16 additionally have real PRODUCTION implementation files (ai_trader/strategy_runtime/families/s13_imbalance_fill.py, s16_previous_day_levels.py, plus their own tests) -- a bare-form collision would hit production code, not just research naming.",
            "families": {
                "SMC_S1": "Liquidity Sweep Reversal",
                "SMC_S2": "Failed Breakout / Failed Sweep",
                "SMC_S3": "Breakout Retest Continuation",
                "SMC_S13": "Liquidity Void / Imbalance Fill",
                "SMC_S16": "Previous Day Levels",
            },
            "naming_rule": "RIGID, PROTECTED PREFIX, MANDATORY. The short form (S1, S13, etc.) is NEVER used for these or any future SMC family -- always SMC_S13, never S13. S1-S51 without a prefix refer PERMANENTLY to the decommissioned legacy grammar corpus (code/mstrat.py), never to any new SMC family, regardless of conceptual similarity.",
            "open_r_framework": {
                "name_note": "'Open-R' is CEO's name, adopted here -- it labels the risk construction already ratified across Mandates 3.11-3.13 for LM-001, now given a reusable label for cross-family application, not a new framework.",
                "construction": "Geometric stop = the family's own structural 'spike' distance (e.g. wick extreme for SMC_S1's sweep, zone edge for SMC_S13's FVG -- each family instantiates its own geometric spike, the PRINCIPLE is shared, not the specific measurement) + 2 pips buffer, NEVER widened to a floor. net_R as the outcome variable throughout.",
                "floor_portable": "10.1-pip minimum displacement filter REUSED AS-IS across all 5 families -- it is derived purely from the cost/R formula (cost_stress_3x/R=100%), a property of the shared risk-construction formula (cost=$0.40, TICK=$0.10), not of LM-001's own empirical displacement distribution. Portable by construction.",
                "ceiling_NOT_portable": "65-pip rejection ceiling is NOT assumed to transfer as-is to SMC_S2/S3/S13/S16 -- it was derived from LM-001's OWN empirical p90 (46.98 pips), a data-dependent quantity. Treated as a PLACEHOLDER for the other four families pending their own geometry audits (same method as LM001_GEOMETRY_AUDIT_STEP1.md), not assumed final.",
            },
            "dedup_prescreening_mandatory_before_enrollment": (
                "PROJECT_AUDIT.md D11/SS F (ai_quant_lab) applies MECHANICALLY, BEFORE any variant is enrolled for testing, not after: identity criterion = "
                "bit-identical realized trade log (SHA-256 over entry_epoch,exit_epoch,R per trade), never summary statistics; canonical ID = "
                "lexicographically lowest in an equivalence class; mandatory dual reporting (raw ID count + deduplicated distinct count), and the "
                "deduplicated count is what's used for any future FDR correction. Verified directly (ai_quant_lab/PROJECT_AUDIT.md): the legacy grammar's "
                "own dedup audit found 27.0% redundancy (532/1972 IDs) and 87% of clusters from a single conditionally-inert parameter -- if the 20 "
                "combinatorial variants across these 5 families (crossed with existing grammar dimensions -- reference type, lookback, exit) are enumerated "
                "naively, the SAME mechanism can recur. This is a real, already-materialized risk in this exact lab, not a theoretical one."
            ),
            "full_registration_document": "ai_quant_lab statistician/STATISTICIAN_BLOCK_BOOTSTRAP_VERDICT_MK_RATIFICATION_SMC_NOMENCLATURE_v1.0.md",
        },
        "smc_s_state_machines": {
            "source": "CEO Mandate 3.18 -- formalizes all 20 SMC_S* families (verified directly in code/mstrat.py's ECON dict: S1-S20 is the legacy grammar's own full family list, not just the 5 already named as nomenclature at Mandate 3.17).",
            "capabilities_json_mismatch_flagged": (
                "Read validation_engine/capabilities.json directly before writing anything into it. Its own "
                "deliberately_absent field explicitly lists 'Hypothesis-specific event primitives (sweep_reject, "
                "liquidity_grab, compression)' and 'Predefined session definitions (NY/London/Asia)' as deliberately "
                "excluded by design -- it is a hypothesis-agnostic statistical-methods grammar (test_methods, "
                "variable_primitives, population_predicates), not a place for 20 hypothesis-specific SMC_S* "
                "families. Registered here (split_manifest.json, v2.5.8) instead -- same authority/versioning "
                "scheme as every prior LM-001/MK-03/MK-04 registration -- rather than forcing content into a file "
                "whose own documented design principle it would violate."
            ),
            "open_r_shared_template": "R_i=(spike_i+2 pips)*TICK($0.10), never widened; eligibility filter spike_i in [10.1,65.0) pips (floor portable, ceiling placeholder per family per Mandate 3.17); net_R_i=direction_i*(exit_price-entry_price)/R_i - cost/R_i, cost=$0.40.",
            "horizon_groups": {
                "A_immediate_reaction": {"bars": 20, "source": "Reused verbatim from LM-001's own derivation (Mandate 3.13): _profile.HORIZONS linked to london session length (5h=20 M15 bars, mtf.py:37-38). Used by families whose trigger is a POINT event (sweep/BOS/CHoCH/FVG formation) testing immediate reaction."},
                "B_native_session_length": {"asia": 32, "london": 20, "ny": 32, "late": 12, "source": "Native bar-length of the 4 already-established UTC session boundaries (mtf.py:37-38): asia<8h=8h=32 bars, london[8,13)=5h=20 bars, ny[13,21)=8h=32 bars, late>=21h=3h=12 bars. Used by families whose trigger IS a specific session."},
                "C_empirical_period_length": {
                    "day_bars": 92, "week_bars": 460,
                    "source": "Independently computed by Statistician (not assumed) by reconstructing the 17:00-NY DST-aware day anchor (code/resample_ny.py's own logic) and the derive_week_index gap rule (MK-04 Q3-week) directly on the 130,491 M15_v2 discovery bars: day length median=92 (mean 91.9, mode 92, matches institutional_levels.py's own '92 is just the most common value' caveat exactly); week length median=460 (mean 451.5, mode 460). Used by families anchored to PDH/PDL/Weekly levels.",
                },
                "D_no_horizon_no_primitive": "Not derived -- see gapped families below. No horizon is forced where the underlying event primitive itself does not exist in the 4 ratified modules.",
            },
            "families_formalized": {
                "SMC_S1": {"status": "AWAITING_VALIDATION_ENGINE_CODE", "note": "= LM-001, referenced not re-derived. See full_hypothesis_formulation_document and full_risk_framework_decision_document.", "horizon_group": "A"},
                "SMC_S2": {
                    "status": "AWAITING_VALIDATION_ENGINE_CODE", "concept": "Failed Breakout / Failed Sweep",
                    "primitives": ["market_structure (BOS on close, CHoCH)"],
                    "mechanics": "BOS at bar b in direction D (close beyond a CLASSIFIED swing) -> a CHoCH (opposite structural break) occurs within <=20 bars (group A, reused as the qualification window) -> entry at next-open after the CHoCH bar, direction = OPPOSITE of the original BOS (fade). No CHoCH in window -> event not eligible (excluded, not a separate failure outcome).",
                    "threshold": "spike = distance from entry to the broken BOS-level extremum + 2 pips.",
                    "population": "BOS events on M15_v2 discovery bars followed by a qualifying within-window CHoCH, minus the [10.1,65.0) filter.",
                    "horizon_group": "A (both the CHoCH-qualification window and the net_R measurement window)",
                },
                "SMC_S3": {
                    "status": "AWAITING_VALIDATION_ENGINE_CODE", "concept": "Breakout Retest Continuation",
                    "primitives": ["market_structure (BOS)", "D6 wick/close asymmetry re-applied to the BOS level itself"],
                    "mechanics": "BOS at bar b in direction D -> a later bar's WICK touches the broken level within <=20 bars but its CLOSE stays on the breakout side (does not close back through) -> entry at next-open, direction = SAME as BOS (continuation). Mechanically distinct from SMC_S2 on the same retest bar (a bar cannot simultaneously close-through and not-close-through), though both can originate from the same BOS.",
                    "threshold": "spike = distance from entry to the retested level + 2 pips.",
                    "horizon_group": "A",
                },
                "SMC_S7": {
                    "status": "AWAITING_VALIDATION_ENGINE_CODE", "concept": "Trend-Pullback Continuation",
                    "primitives": ["market_structure (>=2 consecutive same-direction CLASSIFIED swings, e.g. HH+HL or LH+LL)"],
                    "mechanics": "Once a trend is established (>=2 consecutive same-direction swings), the NEXT swing continues it (a new HL higher / LH lower, no CHoCH triggered) -> entry at next-open after that swing's confirmed_idx, direction = the established trend.",
                    "threshold": "spike = distance from entry to the new swing extreme + 2 pips.",
                    "horizon_group": "A (default, no family-specific derivation given -- declared as such, not hidden)",
                },
                "SMC_S10": {
                    "status": "AWAITING_VALIDATION_ENGINE_CODE -- VERDICT OPEN, RELOOP ACKNOWLEDGED, NOT RESOLVED", "concept": "Displacement Continuation",
                    "substitution_disclosed": "The legacy 'displacement' concept (range bar >1.5x ATR) uses ATR, outside the 4 ratified modules. Substitutes market_structure's own BOS (an already-decisive directional close-break) as the trigger instead -- flagged transparently, a reader may reject this substitution as too far from the original concept.",
                    "reloop_acknowledged": "Research Lab's cross-verification (code/trading_strategies.py, commit 136fadc) found the BOS-substitution DECOUPLES magnitude from structure: trigger is a pure structural body-BOS, but the magnitude gate is the shared absolute pip band [10.1,65.0), not volatility-relative -- 'not an approximation, a hypothesis substitution'. Acknowledged, explicitly deferred to a future mandate, NOT resolved here.",
                    "mechanics": "Confirmed BOS -> entry at next-open, direction = BOS direction, tests CONTINUATION (unlike SMC_S2's fade).",
                    "threshold": "spike = distance from entry to the BOS level + 2 pips.",
                    "horizon_group": "A",
                },
                "SMC_S11": {
                    "status": "AWAITING_VALIDATION_ENGINE_CODE", "concept": "Structure-Break Reversal",
                    "primitives": ["market_structure (CHoCH as the PRIMARY signal, not following a recently-failed BOS -- explicit distinction from SMC_S2)"],
                    "mechanics": "CHoCH occurs at the end of an established trend sequence -> entry at next-open after the CHoCH's confirmed_idx, direction = the NEW direction (opposite the prior trend).",
                    "threshold": "spike = distance from entry to the CHoCH extreme + 2 pips.",
                    "horizon_group": "A",
                },
                "SMC_S13": {
                    "status": "AWAITING_VALIDATION_ENGINE_CODE", "concept": "Liquidity Void / Imbalance Fill",
                    "primitives": ["imbalance_mechanics (detect_fvgs, ce50_touch_idx = the D7 consumption point, detect_fvg_reactions)"],
                    "mechanics": "FVG forms -> CE-50 touch (wick, D7 consumption) -> entry at NEXT-OPEN MARKET after the touch bar (RECONFIRMED, not a limit order at CE-50 -- see premise_correction below), direction = BACK toward the FVG's ORIGINAL direction (bet that the gap holds as support/resistance).",
                    "threshold": "spike = distance from entry to CE-50 + 2 pips.",
                    "horizon_group": "A (RECONFIRMED 20 bars -- an implementation used 12 bars, the 'late'-session length, an ERROR applying Group B's rule to a point-event-triggered Group A family; not a new decision).",
                    "premise_correction": (
                        "RATIFIED (Mandate: SMC_S1 verdict/SMC_S13 premise): the order's stated motivation ('exploit the massive 85% generic gap-fill "
                        "rate') is backwards -- verified directly that E004 ('US Market Open First FVG', the same FVG-fill construct) already "
                        "established 85% as the GENERIC BASELINE (OBSERVED_NOT_DISTINCTIVE, pre-registered band (0.512,0.886)), and that E004's own "
                        "gaps fill LESS often than that baseline (71.48%, z~8.75, opposite direction from any 'exploit the rate' framing). SMC_S13 "
                        "does NOT claim FVGs fill more often than the established baseline. It tests EXECUTION ECONOMICS ONLY: at the unchallenged "
                        "baseline fill rate, does the geometry of a B1-anchored stop (structurally wider than SMC_S1's, per the correct risk-design "
                        "intuition in the order) produce net_R>0 after cost -- a claim about geometry, not about fill-rate predictability. The "
                        "'fills significantly more than 85%' variant is REJECTED (E004 is the closest tested precedent and shows the opposite); "
                        "'continuation vs. rejection at CE-50' is noted as a separate, untouched, possible future direction, not adopted here."
                    ),
                },
                "SMC_S16": {
                    "status": "AWAITING_VALIDATION_ENGINE_CODE", "concept": "Previous Day Levels",
                    "primitives": ["institutional_levels (compute_prior_day_levels, detect_level_touches -- D7 consumption already implemented)"],
                    "mechanics": "PDH/PDL available (Q4) -> wick touch (already implemented, consumed at first touch) -> entry at next-open, direction = AWAY from the level (rejection, analog to SMC_S1 but on institutional levels not swing-derived basins).",
                    "threshold": "spike = distance from entry to PDH/PDL + 2 pips.",
                    "horizon_group": "C (day_bars=92)",
                },
                "SMC_S17": {
                    "status": "AWAITING_VALIDATION_ENGINE_CODE", "concept": "Weekly Levels",
                    "primitives": ["institutional_levels (compute_prior_week_levels, D-WEEK)"],
                    "mechanics": "Identical to SMC_S16 on Weekly H/L. MANDATORY restriction: only COMPLETE levels (>=5 days) enter the PRIMARY population -- PARTIAL levels excluded from the primary population (disclosed as a separate stratum per D-WEEK, never silently pooled).",
                    "threshold": "spike = distance from entry to Weekly H/L + 2 pips.",
                    "horizon_group": "C (week_bars=460)",
                },
                "SMC_S12": {
                    "status": "AWAITING_VALIDATION_ENGINE_CODE", "concept": "Range Rotation",
                    "upgraded_at": "Mandate 3.19 (STAT-WP5-Q1-DEFINITIONS-PRIMITIVES-v1.0) -- corrects Statistician's own 3.18 'partially gapped' classification; no new primitive needed after all.",
                    "primitives": ["liquidity_mechanics (paired basins) + market_structure (classified swings, block confinement D4)"],
                    "range_definition": "A pair of basins (one support-side, one resistance-side) that are BOTH: (a) from CLASSIFIED swings in the SAME discovery block (D4); (b) UNCONSUMED (neither swept yet, D7); (c) adjacent -- no OTHER classified swing of greater extremity exists between their formation and the current bar (ensures they are the current nearest bounding structure, not stale/superseded levels).",
                    "mechanics": "Sweep-reject (D6/D7) at either basin of a qualifying pair -> entry at next-open, direction = mechanical (away from swept basin, same as SMC_S1), 'rotation' = repeated alternating sweep-reject cycles between the same pair over time.",
                    "threshold": "spike = distance from entry to the swept basin + 2 pips.",
                    "horizon_group": "A",
                },
            },
            "families_gapped_or_different_nature": {
                "cheap_gaps_near_trivial_extension": {
                    "SMC_S5": "Opening-Range Momentum -- needs a 'first-K-bars-of-session high/low' computation, absent from all 4 modules (institutional_levels only does day/week, not opening range). Same missing-extension family as S6/S19 -- Module 4's day/week OHLC pattern applied at session granularity, not a new Module 5/6 primitive.",
                    "SMC_S6": "Session-Transition Momentum -- needs 'previous SESSION high/low' (analog to PDH/PDL but per-session), same missing extension as S5/S19.",
                    "SMC_S19": "Session Gap -- needs session open/close price, same missing-extension family as S5/S6.",
                },
                "genuine_gaps_missing_primitive_class": {
                    "SMC_S4": "Volatility-Regime Expansion -- MEASURE now defined (Mandate 3.19): reuses the lab's own OFFICIAL E000 standard (Parkinson log-range ln(H/L), primary). 'Expansion regime' = current volatility in the upper percentile of its own trailing distribution. The exact percentile threshold is DEFERRED to its own dedicated derivation (analogous to the LM-001 geometry audit) -- not invented now.",
                    "SMC_S8": "Extension Mean-Reversion -- MEASURE now defined (Mandate 3.19): distance from a reference normalized by the same Parkinson volatility measure as S4. Threshold likewise deferred to its own derivation. Smaller gap than S9/S14/S15/S20 -- the underlying measure (volatility) is an already-official lab standard, just not part of the 4 MK-01..04 modules.",
                    "SMC_S9": "MTF-Trend Momentum -- RESOLVED VIA RECOMPOSITION (Mandate 3.19), no new primitive needed: market_structure's own swing/HH-HL-LH-LL classification applied to the already-CONTEXT_DERIVED_VALIDATED H1_from_M15_v2/H4_from_M15_v2/D1_from_M15_v2 context bars, requiring trend-direction alignment across >=2 resolutions. Composition of already-ratified/validated pieces, not a new research primitive.",
                    "SMC_S14": "Momentum Exhaustion -- needs a ROC/RSI-type indicator. STILL GENUINELY GAPPED after Modules 5-6 (Mandate 3.19 checked): this concept does not appear in either module's given list -- not force-fit into Volatility or Trend.",
                    "SMC_S15": "Trend Acceleration -- needs a swing-to-swing rate-of-change measure. STILL GENUINELY GAPPED after Modules 5-6 (Mandate 3.19 checked): Trend (Module 6) classifies direction, not its rate of change -- neither module covers acceleration.",
                    "SMC_S20": "Hybrid Sweep+MTF -- RESOLVED VIA THE SAME RECOMPOSITION AS S9 (Mandate 3.19): depends on the identical already-ratified MTF-Trend composition, no separate new primitive.",
                },
                "not_a_standalone_family": {
                    "SMC_S18": "Time-of-Day -- confirmed the legacy S18 was always a STRATIFICATION dimension (hour/session) applied to OTHER signals, not its own trigger -- consistent with the already-documented 'S18 = 3 signals x 2 exits' finding (Mandate 3.10). Recommendation: NOT a 20th independent hypothesis -- remains a reporting stratification (asia/london/ny/late, already applied to SMC_S1/LM-001) over the other families.",
                },
            },
            "dedup_prescreening": {
                "status": "MANDATORY BEFORE ENROLLMENT, per PROJECT_AUDIT.md D11/SS F (ai_quant_lab) -- cannot yet run mechanically (no trade logs exist, AWAITING_VALIDATION_ENGINE_CODE for all families).",
                "conceptual_collision_risk_flagged_for_hash_verification": {
                    "SMC_S2_vs_SMC_S11": "Both CHoCH-based, deliberately differentiated (S2 requires a specific recently-failed BOS; S11 requires only a CHoCH at trend end) but run on the same market_structure code -- real overlap risk, mandatory hash check once implemented.",
                    "SMC_S3_vs_SMC_S7": "Both continuation-flavored, differentiated (S3 requires an explicit BOS+retest; S7 requires an established trend + next swing, no new BOS) -- same shared code risk.",
                    "SMC_S1_S13_S16": "All three are sweep-reject-flavored but on geometrically distinct entities (swing-derived basin / FVG CE-50 / institutional PDH-PDL) -- lower collision risk but still to be hash-verified, not assumed.",
                },
                "distinct_count_not_reportable_yet": "No distinct-family count is reported here -- D11/SS F requires a measured trade-log hash, not a guess; reporting a number now would be assumption presented as measurement.",
            },
            "status_rule": "ALL formalized families: AWAITING_VALIDATION_ENGINE_CODE. Gapped families: GAPPED (missing primitive, specified per family above). SMC_S18: NOT_A_STANDALONE_FAMILY. NONE may be promoted to VALIDATED until WP-5' (Mandate 3.17) delivers the oracle.",
            "full_state_machines_document": "ai_quant_lab statistician/STATISTICIAN_SMC_S_STATE_MACHINES_v1.0.md",
        },
        "axiomatic_definitions_module5_6": {
            "source": "CEO Mandate 3.19, four axiomatic definitions proposed for ratification; Statistician verified each directly against code before ratifying or fixing.",
            "definition_1_LiquiditySweep": {
                "status": "RATIFIED -- confirmation, not a new definition",
                "verification": "Verified directly in code/liquidity_mechanics.py:detect_sweeps -- formula matches exactly: low[c]<p AND close[c]>p (BELOW basin), symmetric high[c]>p AND close[c]<p (ABOVE). Identical to D6. The require_close_back_inside=False parameter already exists precisely for the 'if close breaks beyond, label moves to BOS' distinction.",
            },
            "definition_4_PDH_PDL_Weekly_fixed_reference": {
                "status": "RATIFIED -- unchanged",
                "verification": "Confirmed consistent with detect_level_touches (Mandate 3.14/3.17): consumed at first wick touch within the current day/week's availability window, no re-arming.",
            },
            "definition_3_LiquidityVoid": {
                "status": "RATIFIED -- threshold DERIVED, hybrid criterion (not size alone, not time alone). size_threshold REOPENED (Mandate 3.22, cost_constant_correction_v2_7_8): derived from cost_round_trip=0.40 (now corrected to $0.20) -- fresh value is $0.60 (3x $0.20), not $1.20. Pure dollar figure, no TICK-relabeling channel involved (unlike the LM-001 pip filter). hybrid rule structure (temporal OR size) is unaffected, only the size constant.",
                "verification": "Independently reproduced CEO's exact figures on the actual 84,152-bar dataset tested (data/market/OANDA_XAUUSD_M15__SUPERSEDED_v1_2022-12-16_to_2026-07-13_R03terminal.csv, NOT the current 355,696-bar M15.csv): 48,321 (57.4%) strict-inequality bars, median $0.02, p90 $0.095, p99 $0.55, >$1.00=377, >$5.00=123 -- exact match.",
                "size_threshold_derived": "$1.20 = 3x the already-established cost_round_trip ($0.40), same logic as the LM-001 displacement floor derivation -- 344 bars at this threshold, not chosen from the $1.00 eyeballed figure.",
                "why_hybrid_not_size_alone": "Empirically decomposed on the same 84,152 bars: 248 bars are SIZE-only gaps (>$1.20, no time discontinuity -- the CPI-slippage pattern, invisible to a time-only criterion); 119 bars are TIME-only gaps (temporal discontinuity, no large jump -- weekend reopens, invisible to a size-only criterion); 96 overlap. Neither criterion alone covers the intended concept.",
                "final_definition": "A bar transition (c->c+1) qualifies as a LiquidityVoid iff EITHER: (temporal) time[c+1]-time[c] > 900s, excluding the already-documented daily maintenance window (~20:00-21:59 UTC, <=75min -- reused verbatim from code/gapfind.py's own existing rule); OR (size) |Open[c+1]-Close[c]| > $1.20. 463 qualifying transitions on the same 84,152-bar dataset (215 temporal + 344 size - 96 overlap).",
            },
            "definition_2_OrderBlock_Breaker": {
                "status": "RATIFIED WITH TWO FIXES, specified before any implementation",
                "problem_1_zone_contradiction_fixed": "For a bearish OB, body=[Close,Open] (Open>Close). The proposed formula [Open,Low] covers body PLUS the lower wick, a materially larger zone than 'the body' the text claims. DECIDED: active zone = the BODY, [Close_Bdown,Open_Bdown] -- the text's stated intent is correct, the formula is the error, formula corrected not the concept. Reasoning: the wick already has an established, exclusive role in this lab (D6: wick=penetration/touch, close=confirmation) -- including the wick in the OB zone itself would make 'touching the OB' ambiguous (wick-touch vs body-touch would mean different things), breaking the discipline already applied at MK-03 Q4/Q6.",
                "problem_2_E010_circularity_preempted": (
                    "E010 failed because its selection window ('OB not yet violated within the test horizon') and measurement window ('did price continue within the SAME horizon') were IDENTICAL "
                    "(min(idx+1+480,n) both places). Specified now, before VE implements, to prevent the same defect: "
                    "(1) VALIDITY window -- an OB stays active from formation until EITHER (a) a wick touch in the zone (D7-analog consumption, used once, no re-arm) OR (b) a decisive CLOSE beyond the zone "
                    "(becomes a 'breaker' -- reused verbatim from the already-ratified E010/E012 inversion criterion, Mandate 3.14). (a) and (b) are DIFFERENT events; (a) does not imply (b). "
                    "(2) MEASUREMENT window -- begins ONLY at the qualifying event bar (a) or (b), never at OB formation, running the group-A horizon (20 bars) forward from THAT point. "
                    "By construction these two windows cannot collapse into the same window computed twice, unlike E010's identical selection/measurement windows."
                ),
                "implementation_status": "IMPLEMENTED (code/order_block_void.py, commit edca965) -- zone + window separation frozen exactly as specified above. OB formation criterion (which candle becomes an OB) was NotImplementedError -- RATIFIED at Mandate 3.22, see order_block_formation_criterion_v2_7_8 (top-level) for the specification (E010 displacement/expansion qualifier + body-engulfment of the prior opposite candle's body, no volume filter). Still not implemented in code as of this manifest version; VE implements per the ratified spec.",
                "cross_verification_spec_TRIGGERED": {
                    "status": "TRIGGERED (Mandate 3.20) -- this is the first concrete instance of the persistent-artifact exception flagged at Mandate 3.10.",
                    "ruling": (
                        "code/order_block_void.py is NOT a one-time diagnostic (unlike the geometry/density audit scripts) -- it is a PERSISTENT PRIMITIVE MODULE, "
                        "structurally identical in role to the four already-ratified modules (market_structure/liquidity_mechanics/imbalance_mechanics/"
                        "institutional_levels): future hypotheses will import and call it repeatedly, reading through the manifest's mask each time. Unlike D1-D7 "
                        "(Architect wrote the implementation, VE wrote independent tests -- a genuine cross-check), order_block_void.py was BOTH designed and "
                        "implemented by VE with no independent verification. This satisfies the explicit limit written at Mandate 3.10 ('if this code becomes a "
                        "persistent, widely-relied-upon artifact, the calculus changes') -- it is not a generic extension of CROSS_VERIFICATION_SPEC to code, it "
                        "is this specific, previously-flagged condition being met."
                    ),
                    "requirement": "An independent test suite, written by a division OTHER than VE, verifying mechanically: zone=body not body+wick; validity/measurement window separation (cannot collapse into the same window); the hybrid Void criterion (temporal OR size, with maintenance-window exclusion) -- REQUIRED before any formalized hypothesis relies on this module. Which division is an operational assignment, not specified here.",
                },
            },
            "missing_primitives_module5_6": {
                "not_needed_by_any_blocked_family_not_constructed": "Order Block/Breaker/Mitigation/Rejection (Module 5 -- handled separately above via Definition 2, for its own reasons, not because any blocked SMC_S* family needs it); Compression (Module 6 -- no family names it).",
                "resolved_via_recomposition_no_new_primitive": {
                    "Range": "Needed by SMC_S12 (upgraded from partially-gapped to fully formalized, see smc_s_state_machines.families_formalized.SMC_S12) -- a pair of unconsumed, same-block, structurally-adjacent basins. Built entirely from already-ratified liquidity_mechanics/market_structure, no new primitive.",
                    "MTF_Trend": "Needed by SMC_S9/SMC_S20 -- market_structure's own swing classification applied to the already-CONTEXT_DERIVED_VALIDATED H1/H4/D1_from_M15_v2 bars, requiring cross-resolution alignment. Composition of already-ratified/validated pieces, not new research.",
                },
                "new_primitive_measure_and_threshold_RESOLVED": {
                    "Volatility_Expansion": "Needed by SMC_S4/SMC_S8 -- measure = the lab's own OFFICIAL E000 standard (Parkinson log-range ln(H/L), primary). THRESHOLD WINDOW RESOLVED (Mandate 3.21): rolling, strictly causal 460-bar window (empirical median week length, already derived Mandate 3.18/3.19's derive_week_index rule, reused verbatim, not re-derived) -- same window that resolves Module 6 Compression's lookahead risk (module_5_6_7_parameters.problem_3_compression). Percentile level (10th) stays the spec's own disclosed default.",
                },
                "still_genuinely_gapped_after_modules_5_6": {
                    "SMC_S14": "Momentum Exhaustion -- needs ROC/RSI-type indicator. Does not appear in either Module 5 or Module 6's given list -- not force-fit.",
                    "SMC_S15": "Trend Acceleration -- needs swing-to-swing rate-of-change. Trend (Module 6) alone classifies direction, not its rate of change.",
                },
                "cheap_extension_of_module4_not_module5_6": "SMC_S5/S6/S19 need session-level OHLC (open/high/low/close per session) -- a mechanical extension of institutional_levels' existing day/week pattern to session granularity (mtf.py's already-established boundaries), not a genuine new Module 5/6 primitive.",
            },
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_WP5_Q1_DEFINITIONS_MISSING_PRIMITIVES_v1.0.md",
        },
        "module_5_6_7_parameters": {
            "source": "CEO Mandate 3.21 -- CTO requested Module 5/6/7 implementation; Statistician held it because the spec contained four CHOSEN (not derived) parameters plus a data dependency the lab refuses elsewhere. VE had already refused to choose four times that day -- routed to Statistician instead of letting VE pick.",
            "problem_1_volume_filter": {
                "status": "ELIMINATED from the core Order Block primitive, not included-with-caveat",
                "verification": "Confirmed directly in EDGE_DISCOVERY_REGISTRY_v1.md/ROADMAP.md: volume column is 'of unconfirmed provenance (likely OTC tick-count proxy, not verified exchange volume)'; E022/E031 sit in Tier 3 ('testable today, but every Final Verdict must caveat the proxy'); E020 is held entirely on this issue.",
                "reasoning": "E022/E031's caveat is carried once, at the individual-hypothesis level. Baking a volume dependency into a PERSISTENT, foundational primitive (Order Block, Module 5) would propagate the provenance risk silently to every future consumer -- the base OB geometry (body engulfed by the next opposite-direction body) is already complete without volume; no SMA window is derived since the filter is not included.",
            },
            "problem_2_expansion_threshold": {
                "status": "RESOLVED -- reuses E010's already-frozen displacement-bar criterion verbatim, not the ungrounded 2.5x nor a naive REACTION_THRESHOLD=1.0 substitution",
                "rejected_2_5": "No derivation exists for 2.5x ATR anywhere in the lab.",
                "rejected_reaction_threshold_1_0": "edge_research/_profile.py:13 REACTION_THRESHOLD=1.0 measures a DIFFERENT category -- forward reaction magnitude over a horizon (movement_profile), not single-bar range/body size. Wrong instrument for this question, same class of error as mapping AR(1) phi onto a finite-memory dependence.",
                "resolution": "Reuses E010's own already-frozen displacement-bar criterion: range[i]=high[i]-low[i] > 1.5x ATR14[i-1] (prior bar's ATR) AND |close[i]-open[i]| >= 0.5x range[i]. Same underlying concept ('a bar signals decisive market force') already used as the source for the Breaker inversion criterion -- consistency requires the criterion that FORMS an Order Block to reuse the same source as the criterion that FLIPS it.",
            },
            "problem_3_compression": {
                "status": "RESOLVED -- rolling, strictly causal window, length DERIVED not chosen",
                "lookahead_risk_confirmed": "A percentile computed over the full available history would classify a 2013 bar using 2021 data -- confirmed a real risk, not hypothetical.",
                "window_derived": "460 bars -- the empirical median week length, already derived at Mandate 3.18/3.19 (derive_week_index's weekend-gap rule), reused verbatim, not re-calculated. Reasoning: volatility/compression regimes are discussed at a days-to-weeks cadence, not hours -- one week is long enough for a stable percentile, short enough to stay local to the current regime (unlike full-history, which would blend unrelated market eras).",
                "shared_with_S4_S8": "The SAME window resolves the threshold Mandate 3.19 deferred for SMC_S4/S8's Volatility/Expansion measure -- one derivation, two consumers (see missing_primitives_module5_6.new_primitive_measure_and_threshold_RESOLVED above).",
                "percentile_level_unchanged": "The 10th-percentile LEVEL stays the spec's own disclosed default (same convention as ATR_THRESHOLDS/REACTION_THRESHOLD, 'disclosed, not tuned') -- only the WINDOW (the actual lookahead risk) needed resolving, not the percentile level itself.",
            },
            "problem_4_sessions": {
                "status": "CORRECTED -- no 'Cash' session exists",
                "verification": "Confirmed directly, code/mtf.py:38: exactly 4 sessions -- asia (hh<8), london (hh<13), ny (hh<21), late (default). No fifth session anywhere in the codebase.",
                "ruling": "Use the real labels 'london' and 'ny' -- the cash-vs-futures distinction (meaningful for equities/indices with closed market hours) does not map naturally onto a near-24/5 OTC-traded instrument like XAUUSD. No new session introduced.",
            },
            "problem_5_module_7": {
                "status": "RULED -- a GENERIC parametrizable confluence locator, NOT a hardcoded hypothesis",
                "reasoning": "The given example (next-open touches a validated OB, in an active external basin, during london/ny sessions) is a complete trading hypothesis -- entry, condition, window -- missing all 5 criteria already imposed on the 40 V0s and applied to LM-001 (population/horizon/success-criterion/family). Not formalized as a hypothesis here.",
                "implementation": "A generic function taking a SET of primitive conditions as parameters (e.g. 'validated OB', 'active external basin', 'session in {X}'), checking co-occurrence at the same bar/window, returning qualifying events -- analogous to count_bpr's tolerance parametrization, not a single hardcoded combination.",
                "future_hypothesis_path": "The specific OB+basin+london/ny combination remains a possible USAGE EXAMPLE, not the default behavior. If ever wanted as its own hypothesis, it requires full separate pre-registration (population/horizon/success/family), reusing the generic locator as its detection mechanism -- same discipline as any of the 20 SMC_S* families.",
            },
            "anchoring_question_ANSWERED_PER_PRIMITIVE": {
                "status": "ANSWERED per-primitive, not with one blanket verdict -- checked each of the 7 named Module 5/6 primitives directly against the 20 SMC_S* families",
                "already_anchored_to_concrete_blocked_families": "Trend/MTF-Trend (SMC_S9/S20), Volatility/Expansion (SMC_S4/S8), Session-OHLC (SMC_S5/S6/S19) -- not abstract definitions, each has a named concrete consumer (Mandate 3.19).",
                "already_defined_via_reuse_not_new_abstractions": "Of Module 5's four named primitives (Order Block, Breaker, Mitigation, Rejection), THREE are already fully defined by reusing already-ratified mechanics, not new invention: Breaker = the already-frozen E010/E012 inversion criterion (code/order_block_void.py, Mandate 3.20); Mitigation = exactly event (a) of the OB validity window (wick touch = D7 consumption, Mandate 3.20) -- needs only a formal name, not a new derivation; Rejection = the D6 wick-sweep-reject mechanic already used throughout (LM-001, PDH/PDL) -- name, not derivation. Only Order Block itself needed new decisions (zone at 3.20; volume filter and expansion threshold here at 3.21).",
                "still_genuinely_unanchored_abstract_definition_accepted_with_disclosed_risk": "Compression (Module 6 -- no SMC_S* family names it, though its lookahead-window risk is now resolved, reducing but not eliminating the 'ten plausible variants' concern) and the Order Block FORMATION criterion (still open since Mandate 3.20, which candle becomes an OB candidate). For these two only, abstract definition is accepted (the CTO's library-first position is defensible) -- risk stated explicitly, not hidden.",
            },
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_MODULE5_6_7_PARAMETERS_v1.0.md",
        },
        "cost_constant_correction_v2_7_8": {
            "source": "CEO Mandate 3.22 -- CEO independently verified in code/mstrat.py that TICK=0.10 is wrong for XAUUSD (quoted to 2 decimals -> TICK=0.01), a 10x error inherited via copy-paste into code/alpha_lab.py and code/lm001_geometry_audit.py, and used in TWO distinct roles: (a) converting spread/slip tick-counts to a dollar cost, (b) converting raw dollar distances to 'pips' throughout the LM-001/SMC pipeline.",
            "verification": "Statistician independently confirmed code/mstrat.py:10 (TICK=0.1), :45 (cost=(spread_ticks+slip_ticks)*TICK), :53 (min_exec=max(2*spread_ticks*TICK,5*TICK,0.10*atr)), AND, going one line further than the order's own citation, :63 (Rs.append((dirn*(ex-entry)-2*cost)/risk)) -- the round-trip deduction is 2*cost, not cost. This resolves an internal ambiguity in Statistician's own prior citations of this formula, and catches a small slip in the order's own arithmetic (its written '(spread_ticks+slip_ticks)*TICK=2x0.1=0.40' literally equals 0.20, not 0.40 -- the true 0.40 only emerges via the code's separate 2*cost multiplier, which the order's walkthrough did not unpack).",
            "TICK_corrected": {"old": 0.10, "new": 0.01, "source": "Instrument spec verified via CEO's real account (Fusion Markets Classic): XAUUSD quoted to 2 decimals (e.g. 4033.84/4033.89), confirmed at the SOURCE (the account), not the code that copies the constant."},
            "cost_round_trip_corrected": {
                "old": 0.40, "new": 0.20,
                "spread_ticks": {"old": 1, "new": 5}, "slip_ticks": {"old": 1, "new": 5},
                "derivation": "Real account: zero commission per lot, typical spread 5-15 ticks (at corrected TICK, $0.05-$0.15). Uses the MIDPOINT of the stated range (10 ticks, $0.10 full spread), not the single tightest observed example ($0.05) -- conservative-when-uncertain, the same convention applied throughout this lab. Slippage = spread (CEO's stated convention) -> spread_ticks=slip_ticks=5 (half of the 10-tick full spread each, preserving the code's existing per-side structure). cost_round_trip = 2*(5+5)*0.01 = $0.20. slip_ticks=1 does NOT survive at the corrected scale (would represent $0.01 of slip, unrealistically tight for a real OTC/CFD account) -- corrected to 5.",
            },
            "why_R_does_not_10x": "Verified algebraically, not assumed: R_dollars=(displacement_pips+2)*TICK=(distance_dollars/TICK+2)*TICK=distance_dollars+2*TICK. The raw geometric distance term is TICK-INVARIANT; only the small '+2 pip buffer' term scales with TICK (0.20->0.02, a $0.18 shift per trade, not a 10x blowup). Self-corrected during this mandate after an initial miscalculation suggested a near-degenerate eligible band -- resolved via this exact algebra.",
            "three_channel_taxonomy": {
                "channel_A_cost_only": "Pure dollar figures never expressed in pips -- e.g. LiquidityVoid size threshold ($1.20->$0.60). Recompute directly from corrected cost, no relabeling needed.",
                "channel_B_TICK_pip_divisor_only": "Pure unit relabeling of an already-real dollar distance -- e.g. LM-001 rejection_ceiling's pip label (65->approx 650 pips, same real $6.50). No fresh computation needed, exact algebraic relabeling: percentile(X/TICK_new)=(TICK_old/TICK_new)*percentile(X/TICK_old).",
                "channel_C_compound": "Both cost-formula-derived AND pip-labeled simultaneously -- e.g. LM-001 displacement_filter's floor (10.1->approx 58 pips). Requires fresh computation from raw geometry, not a manual relabeling of the old percentile table.",
            },
            "reopened_verdicts": [
                "lm_001_preregistration.execution_layer.displacement_filter (channel C)",
                "lm_001_preregistration.execution_layer.rejection_ceiling (channel B, value/real-distance unchanged, label only)",
                "lm_001_preregistration.execution_layer.break_even_thresholds_SUPERSEDED (channel A+B compound, already SUPERSEDED for a different reason -- doubly stale)",
                "lm_001_preregistration.FINAL_VERDICT (channel A -- REJECTED_NET_OF_COST and its CLOSED_DEFINITIVELY status, reached entirely on cost=0.40)",
                "legacy 7-family descriptive table (S2/S3/S7/S11/S13/S16/S17 edge_brut, commit 741e272) -- all measured under cost=0.40, all under the old $0.40 threshold; CEO explicit instruction: do NOT recalculate on these figures (edge_brut was derived by subtracting the wrong cost, carries the error) -- re-run from raw geometry with the corrected cost, not adjusted on paper.",
                "definition_3_LiquidityVoid.size_threshold_derived (channel A, $1.20->$0.60)",
                "SS9 C(S,RR) criterion (channel A+B, indirectly via break_even_thresholds)",
            ],
            "stays_unchanged": [
                "block_bootstrap@v1 oracle status (VALIDATED for the overlap mechanism) -- about dependency/autocorrelation structure, zero dollar dependency",
                "market_structure D1-D7, re-arming bug fix, half-open [start,end) boundary convention",
                "session definitions (asia/london/ny/late), all time-derived horizons (20/32/92/460 bars)",
                "D-BPR freeze-rule tolerances (0.00/0.10/0.25) -- REINFORCED not contradicted, already assumed cent-level (2-decimal) precision",
                "SMC_S18 reclassification, SMC_S9/S20 MTF-Trend and SMC_S12 Range recompositions (structural)",
                "Order Block zone definition (body vs wick) and validity/measurement window separation (structural/temporal)",
                "E010 displacement/expansion criterion (ATR-relative, not cost-relative)",
                "volume-filter-elimination decision (data-provenance reasoning, unrelated to cost)",
                "SMC_S13's premise correction and 12->20 horizon fix (bar-count/session-based)",
                "SMC_S1_v2 stop-geometry sensitivity design (v2.7.7) -- ALSO explicitly GATED by this correction per CEO's closing instruction, not executed until cost is re-established here",
            ],
            "rerun_order": ["1. Confirm corrected constants (this entry)", "2. Re-diagnose D2 execution floor across the full historical ATR range (dominant term may shift)", "3. Re-run raw geometry audit with corrected TICK -> fresh displacement_filter floor/ceiling", "4. Re-run SMC_S1 and the 7 families with cost=0.20, including the CLOSED_DEFINITIVELY verdict", "5. Only then resume SMC_S1_v2 (v2.7.7), gated until now"],
            "rule_ratified": "CEO's proposed rule ADOPTED: any model constant entering a derivation is verified at the SOURCE -- the instrument specification / real account, not the code that uses it. Extended by Statistician: verification must also check code lines ADJACENT to the cited constant (line 63's 2*cost, one line past the cited lines 10/45/53) -- a constant can be individually correct and still misapplied one line down.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_COST_CONSTANT_CORRECTION_OB_DEMANDZONE_HYPOTHESIS_v1.0.md",
        },
        "order_block_formation_criterion_v2_7_8": {
            "status": "RATIFIED",
            "rule": "A candle forms an Order Block iff: (a) it qualifies as an 'impulse' candle by the already-ratified E010 displacement/expansion criterion (range[i]>1.5*ATR14[i-1] AND |close[i]-open[i]|>=0.5*range[i], Mandate 3.21) -- reused verbatim, not re-derived; AND (b) its body [min(O,C),max(O,C)] fully engulfs the body of the immediately preceding OPPOSITE-direction candle. No volume filter (consistent with the volume-filter-elimination already ratified for the core OB primitive, Mandate 3.21). The OB's zone/anchor is the ENGULFED candle's own body (unchanged from Mandate 3.20), not the impulse candle's body.",
            "not_a_contradiction_with_IFVG": "The order flagged apparent tension with IFVG's inversion rule ('NOT single-bar body-engulfment'). Not a contradiction: IFVG answers WHEN an already-existing zone INVERTS (can be many bars after formation, first qualifying close beyond the zone); this criterion answers WHICH candle BECOMES a zone in the first place (a single-bar formation event, by construction). Different questions, legitimately different answers.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_COST_CONSTANT_CORRECTION_OB_DEMANDZONE_HYPOTHESIS_v1.0.md",
        },
        "demandzone_primitive_v2_7_8": {
            "status": "RATIFIED, new primitive, distinct from OrderBlock",
            "boundaries": "[High,Low] (full candle range, wick included) -- NOT [Close,Open]. Derived from the CEO's own stated subset relationship: OrderBlock's body [Close,Open] is ALWAYS a geometric subset of [High,Low] for any candle by construction; the subset relation only holds if DemandZone=[High,Low] (if DemandZone were also [Close,Open] it would be identical to OrderBlock, not a distinct macro concept).",
            "consumption": "DemandZone does NOT consume -- persistent, re-testable repeatedly (CEO's explicit framing). The nested OrderBlock DOES consume via D7 (unchanged). Two different lifecycle rules on nested-but-semantically-distinct objects -- intentional design, not an inconsistency: DemandZone is the macro/persistent reference (like a classical S/R level); OrderBlock is the narrower, single-use claim ('this exact body, as impulse origin, valid once').",
            "intersection_mechanical": "Entry condition: price in [DemandZone_low, DemandZone_high] for a formation event A, AND price in [OB_close,OB_open] for an unmitigated OrderBlock from a formation event B. TRIVIAL reading (A=B, same candle): always true by the subset relation, adds no information beyond the OB alone. SUBSTANTIVE reading (A != B, a DIFFERENT/older DemandZone geometrically overlapping a DIFFERENT, still-unmitigated OrderBlock): the reading that gives 'intersection' genuine meaning. RECOMMENDED: the substantive (A!=B) reading -- flagged explicitly for CEO/VE confirmation before implementation, not assumed.",
            "anti_E010_window_separation": "Extended to the compound object: DemandZone's validity = active for its entire containing block (D4), never expires early (non-consuming). Measurement window begins ONLY at the COMPOUND entry event (price inside an active DemandZone AND inside an unmitigated OB simultaneously), never at either primitive's own formation bar.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_COST_CONSTANT_CORRECTION_OB_DEMANDZONE_HYPOTHESIS_v1.0.md",
        },
        "next_hypothesis_atr_partial_exit_v2_7_8": {
            "status": "FINAL_VERDICT: REJECTED_AT_DECLARED_PARAMETRIZATION (Mandate 3.26) -- see obdz001_final_verdict_v2_7_12 (top-level). Namespace OBDZ-001 (Order Block x Demand Zone). H0 not rejected in any regime at this exact SL/TP/partial-exit construction; the compound entry signal itself (bias+DemandZone+unmitigated-OB) remains UNTESTED as an independent signal, since the risk construction (declared, not derived) dominates the outcome.",
            "bias": "H1 and H4 trend (ema20>ema50), AMENDED (Mandate 3.25, see bias_source_governance_fix_v2_7_11) -- SOURCE IS H1_from_M15_v2/H4_from_M15_v2 (context-derived, CONTEXT_DERIVED_VALIDATED), NOT code/mtf.py::load_mtf's native-CSV path (native H1 is AWAITING_REGIME_MAP, 100% sealed, unmaskable). The original spec's bare citation to 'code/mtf.py' for h1_trend_up/h4_trend_up was ambiguous and would have led to the unsafe path if followed literally -- VE caught this before running anything and self-corrected; Statistician independently verified and ratified.",
            "entry": "M15, in bias direction, at the compound DemandZone/unmitigated-OB intersection (see demandzone_primitive_v2_7_8), next-open.",
            "stop_and_targets_ATR_multiples": {
                "status": "CHOSEN, NOT DERIVED -- CONFIRMED (Mandate 3.24) with a disclosed rationale, still not a statistical derivation",
                "values": "SL=0.7xATR(14) (defines R), TP1=1.4xATR (close 75%, move stop to breakeven), TP2=2.1xATR (close remaining 25%)",
                "structural_note": "Not three independently-arbitrary picks -- 0.7/1.4/2.1 = 0.7x{1,2,3}, i.e. SL, 2xSL, 3xSL. A coherent 1x/2x/3x progression, still a declared design choice, not an empirically-derived threshold.",
                "arithmetic_verified_v2_7_10": "CEO's original pip-based intent (SL 50-60, TP1 100-120 pips) at the CEO-cited current ATR (~74 pips): 50/74=0.676, 60/74=0.811 (matches CEO's stated 0.68-0.81); 100/74=1.351, 120/74=1.622 (matches 1.35-1.62). 0.7 and 1.4 both fall inside these ranges -- verified exactly. Contrast (also verified): the SAME pip figures on discovery-era ATR (~17 pips) would be 50/17=2.94x and 100/17=5.88x ATR -- a materially different, much-wider-relative-to-volatility strategy. This is the demonstration of why ATR-relative sizing is necessary, not merely convenient. The 0.7/1.4/2.1 figures remain a declared design choice (a rationalized trader intuition converted portably), not a statistical derivation.",
            },
            "weighted_RR_CORRECTED": {
                "status": "CORRECTION to the order's own arithmetic, verified not just confirmed",
                "order_stated": "0.75x1.4R + 0.25x2.1R = 1.575 approx 1.58R -- treats 1.4 and 2.1 directly as R-multiples.",
                "error": "R = SL = 0.7xATR, NOT 1xATR. In true R-units: TP1 = 1.4xATR/0.7xATR = 2.0R (not 1.4R); TP2 = 2.1/0.7 = 3.0R (not 2.1R). The order's own figures are ATR-multiples, not R-multiples -- conflating the two understates the real payoff.",
                "corrected": "0.75x2.0R + 0.25x3.0R = 2.25R (not 1.58R) -- a favorable correction, real profit potential is larger than the order's own estimate.",
                "required_winrate_formula": "w* = (1+cost/R)/(RR_eff+1) = (1+cost/R)/3.25 -- NOT a single number, R=0.7xATR varies with current ATR (same lesson as Mandate 3.13's R-heterogeneity finding, re-applies identically here).",
                "required_winrate_range_v2_7_10": "At cost/R->0 (large ATR), w*->1/3.25=30.77% approx 31% (CEO's cited figure -- the zero-cost limit, not the real value at any finite R). At per-regime median atr14 ($1.99/$1.23/$2.16, from task1_atr_eligibility.py): R=0.7*ATR approx $1.39/$0.86/$1.51, cost/R approx 14.3%/23.3%/13.2%, w* approx 35.2%-37.9%. Real threshold moves in approximately [31%,38%] depending on current ATR -- reported as a range, not a point, per the same no-single-w*-when-R-varies rule.",
            },
            "breakeven_after_TP1": "Stop moves to ENTRY PRICE EXACTLY, not entry+cost. Cost is already deducted once, in aggregate, from net_R -- moving the protective stop itself to a cost-adjusted level would double-count the same cost.",
            "horizon_variable_not_fixed": {
                "status": "DEVIATION FROM STANDARD, disclosed explicitly -- horizon is NOT a fixed bar count for this hypothesis",
                "rule": "Exit at min(entry+20 M15 bars, last bar of the trading day) -- resolved as a plain minimum of the two independent time constraints, not a priority ranking between them.",
                "consequence": "Effective horizon becomes VARIABLE (a trade entered near end-of-day may have only a few bars; one entered in the morning may have the full 20) -- must be reported as a DISTRIBUTION of realized horizon lengths, not a single N, an explicit deviation from the 'horizon as fixed bar count' criterion this Statistician normally imposes.",
                "aggregation_decision_v2_7_10": "RESOLVED (Mandate 3.24): the PRIMARY H0 test runs AGGREGATED across all entry hours -- the variable horizon is a property of the strategy's own definition (mandatory intraday close), not a nuisance to control away; stratifying by entry hour would test a DIFFERENT strategy. MANDATORY secondary diagnostic (not part of the decision criterion): net_R reported broken out by session (asia/london/ny/late) AND by realized-horizon bucket (short <10 bars vs long >=10 bars), same transparency discipline as NET_CONCENTRATION_INVENTORY and the oracle's own session-stratified checks -- if the aggregate result is driven by one session or by short-horizon trades, it must be visible, not averaged away.",
            },
            "partial_exit_mechanism": {
                "status": "NEW -- specified here, does not exist anywhere in code (not in the 9 SMC_S* state machines, not in the SS9.4 contract)",
                "formula": "net_R = 0.75*(R_leg1_in_R - cost_frac_leg1) + 0.25*(R_leg2_in_R - cost_frac_leg2)",
                "cost_modeling_choice": "Total round-trip cost stays the SAME aggregate ($0.20-equivalent-in-R, per current cost_constant_correction_v2_7_8), split proportionally across the two exit legs (0.75/0.25), NOT doubled for having two separate exit tickets -- cost is modeled as proportional to notional traded (consistent with CEO's stated zero-per-lot-commission account: no fixed per-ticket fee that would penalize splitting into two orders). Stated explicitly as a modeling choice, open to revision if per-ticket costs are ever confirmed to apply.",
            },
            "eligibility_filter": {
                "status": "OLD [10.1,65.0) PIPS FILTER ELIMINATED (unchanged) -- RATIFIED as an ATR floor (Mandate 3.23), CONFIRMED FEASIBLE on real data, superseding the v2.7.8 hypothesis-threatening flag below (kept UNEDITED, see retraction).",
                "new_filter_derived": "Reuses the SAME 3x-cost-stress-saturation logic (the general stress-testing convention, not specific to the old displacement construction) applied to R=0.7xATR: saturation at 3*cost_corrected=R -> 3*0.20=0.7*ATR_min -> ATR_min approx $0.857 approx 86 pips.",
                "CRITICAL_FLAG_hypothesis_threatening_RETRACTED": "RETRACTED (Mandate 3.23) -- this was Statistician's OWN unit-mismatch error, not a real finding: '86 pips' was computed at the CORRECTED TICK=0.01 convention ($0.857), while the '74 pips' compared against it was CEO's original citation in the OLD TICK=0.10 pip convention used throughout the session before this mandate's correction (real value $7.40, not $0.74) -- an apples-to-oranges comparison across two different pip-unit systems, the exact class of error this whole cost-correction exercise exists to prevent. VE independently ran the real feasibility check (code/task1_atr_eligibility.py, commit 2944dfc, independently re-executed by Statistician with identical results): 89.75% of the 130,491 M15_v2 discovery bars clear the $0.857 floor (bear 94.11%, bull 81.37%, correction 98.27%; median atr14 per regime $1.99/$1.23/$2.16, all comfortably above the floor). Population is NOT near-empty -- it is the majority of the discovery set. Kept here UNEDITED per standing documentation discipline (mark RETRACTED, don't silently delete the original claim).",
                "sufficiency_decision_v2_7_10": "RATIFIED (Mandate 3.24): the ATR floor ALONE is sufficient -- no ceiling added. Structural reason, not an oversight: in the OLD spike-based construction, R was a FIXED geometric distance independent of current volatility, so a ceiling was needed to exclude the extreme tail (concentration risk). Here R=0.7*ATR is PROPORTIONAL to current volatility by construction -- an extreme-ATR bar does not produce a disproportionately risky R in normalized terms, R simply scales with it. Extreme-bar/news-gap risk is already handled elsewhere (LiquidityVoid, maintenance-window exclusion), not a function of this eligibility filter.",
            },
            "five_criteria_status": {
                "numeric_threshold": "H0: mu_netR<=0 vs H1: mu_netR>0, one-sided, alpha=0.05, family=1 (FIXED, Mandate 3.24 -- see multiple_testing_family_v2_7_10).",
                "horizon_as_bars": "VARIABLE (see horizon_variable_not_fixed), UPPER-BOUNDED AT 20 -- min(entry+20,EOD) never exceeds 20 bars, so the true dependency window is bounded by the SAME H=20 already covered by block_bootstrap@v1's L>=28 validation (Mandate 3.20). Primary test AGGREGATED across entry hours (Mandate 3.24, see horizon_variable_not_fixed.aggregation_decision_v2_7_10); mandatory session/horizon-bucket diagnostic, not part of the decision.",
                "population": "NOT YET MEASURED (Mandate 3.24) -- Statistician explicitly declines to fabricate a compounded estimate (OB-formation rate x mitigation rate x cross-candle-overlap rate x bias-alignment rate is 4 unknown factors, each uncertain by 2-5x, compounding to order-of-magnitude uncertainty). Requires a dedicated VE population-count script (analogous to task1_atr_eligibility.py) applying the full compound filter chain per regime BEFORE any statistical test runs. INSUFFICIENT_N (n>=25/regime, the lab's standing convention) is PRE-REGISTERED now, before the count exists -- any regime below threshold is marked NOT TESTABLE ON THIS DATA, not a failure of the hypothesis.",
                "classification_threshold": "alpha=0.05, family of 1, CONFIRMED SEPARATE from the Block-3 family of 8 (Mandate 3.24) -- structurally distinct construction (not a near-duplicate of the Open-R S1-S20 grammar), tested alone, not alongside 7 variants in the same pass. Namespace proposed: OBDZ-001 (Order Block x Demand Zone), pending CEO ratification, checked for collision against E0xx/S0xx/LM-00x.",
                "zero_free_parameters": "CONFIRMED (Mandate 3.24) -- ATR multiples declared chosen with disclosed rationale (arithmetic_verified_v2_7_10), eligibility filter fixed (ATR floor alone, sufficiency_decision_v2_7_10), cross-candle intersection fully specified mechanically (demandzone_ob_intersection_and_partial_exit_defaults_v2_7_9, extended by cross_candle_mechanical_spec_v2_7_10), horizon aggregation resolved. Nothing left undecided that would affect execution.",
            },
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_COST_CONSTANT_CORRECTION_OB_DEMANDZONE_HYPOTHESIS_v1.0.md + STATISTICIAN_COMPOSITE_HYPOTHESIS_FORMAL_PREREGISTRATION_v1.0.md (Mandate 3.24, formal close)",
        },
        "composite_hypothesis_formalization_v2_7_10": {
            "status": "FORMALLY PRE-REGISTERED (Mandate 3.24) -- proposed namespace OBDZ-001",
            "cross_candle_mechanical_spec_v2_7_10": {
                "OB_B": "An OrderBlock (detect_order_blocks) with kind matching the current H1/H4 bias direction, UNMITIGATED at evaluation bar t (no Mitigation event with event_idx<t, no Breaker before t).",
                "trigger_bar_t": "The bar at which OB_B has its own qualifying Mitigation event (scan from formation_idx+2, per mitigation_rejection_circularity_fix_v2_7_9).",
                "DemandZone_A_conditions": [
                    "kind_A == kind_B (same polarity -- a long needs bullish zone+OB, a short needs bearish)",
                    "formation_idx_A != formation_idx_B (genuinely a different formation event -- cross-candle by construction)",
                    "formation_idx_A < t (DemandZone_A must already be formed/observable before the trigger bar -- forward-safety, no lookahead)",
                    "abs(formation_idx_A - formation_idx_B) <= 460 M15 bars (the already-established empirical median-week window, reused verbatim from Compression/Volatility Mandate 3.21 -- not a newly invented constant)",
                    "same discovery block (D4) as B -- no cross-block pairing",
                ],
                "geometric_overlap": "OB_B.zone_lower <= DemandZone_A.zone_upper AND OB_B.zone_upper >= DemandZone_A.zone_lower (standard interval-overlap test, not full containment).",
                "entry_rule": "If at least one qualifying DemandZone_A exists at bar t, the compound condition is satisfied; entry = next-open after t, in the bias direction.",
            },
            "eligibility_sufficiency": "ATR floor alone (no ceiling) -- see next_hypothesis_atr_partial_exit_v2_7_8.eligibility_filter.sufficiency_decision_v2_7_10.",
            "horizon_aggregation": "Primary test aggregated across entry hours; mandatory session/horizon-bucket stratified diagnostic -- see next_hypothesis_atr_partial_exit_v2_7_8.horizon_variable_not_fixed.aggregation_decision_v2_7_10.",
            "multiple_testing_family_v2_7_10": "Family=1, CONFIRMED SEPARATE from the Block-3 family of 8 -- this construction shares no primitives or near-duplicate relationship with the Open-R S1-S20 grammar; bundling it with family=8 would be as arbitrary as excluding S1 from that family would have been.",
            "population_estimate_declined": "Statistician explicitly declines to produce a numeric population estimate -- compounding 4 unmeasured rates (OB-formation, mitigation, cross-candle DemandZone overlap, bias alignment), each individually uncertain by a factor of 2-5x, would produce an order-of-magnitude-unreliable figure presented with false precision. Requires a dedicated VE read-only population-count script (analogous to task1_atr_eligibility.py) applying the FULL compound filter chain per regime, BEFORE the statistical test runs.",
            "insufficient_n_prereg": "n>=25/regime (the lab's standing convention) FIXED NOW, before the count exists. Any regime falling short is marked NOT TESTABLE ON THIS DATA -- an insufficiency-of-events classification, not a rejection of the underlying idea (same category distinction already applied to S17-correction's n=27).",
            "namespace_proposal": "OBDZ-001 (Order Block x Demand Zone) -- proposed by Statistician, checked for collision against E0xx/S0xx/LM-00x protected prefixes (Mandate 3.17 grammar registration), pending CEO ratification before VE uses it in code/reports.",
            "execution_order": "First permitted VE execution is the population-count script ONLY -- the full statistical test (state machine + block-bootstrap) does not run until INSUFFICIENT_N is cleared per regime.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_COMPOSITE_HYPOTHESIS_FORMAL_PREREGISTRATION_v1.0.md",
        },
        "bias_source_governance_fix_v2_7_11": {
            "status": "RATIFIED (Mandate 3.25)",
            "found_by": "VE, while writing code/task_obdz_population.py (commit 51d02a4) -- self-caught before running anything, flagged for Statistician confirmation rather than deciding unilaterally.",
            "defect": "The spec's bias-source citation ('h1_trend_up/h4_trend_up exist in code/mtf.py') was ambiguous about WHICH loading path to use. code/mtf.py::load_mtf() reads OANDA_XAUUSD_H1/H4/D1.csv via bare pd.read_csv -- no load(), no data_split_id, no cutoff, zero holdout masking. The native H1 timeframe entry is status AWAITING_REGIME_MAP (no regime map ever assigned = 100% sealed, unmaskable). Following the citation literally into load_mtf() would have sourced the entire hypothesis's bias signal from sealed data -- a real contamination, not hypothetical.",
            "fix_ratified": "Bias source AMENDED to ema20>ema50 (same formula, code/mtf.py:_ind, unchanged) computed on H1_from_M15_v2/H4_from_M15_v2 (context_derived_htf.entries, status CONTEXT_DERIVED_VALIDATED), loaded via the SAME load(data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC) path used everywhere else in this lab, merged forward-safe (avail=time.shift(-1), identical convention to mtf.py's own _htf_feat). Native H1/H4/D1 is confirmed impossible to make discovery-safe -- not a choice between two valid options.",
            "verified_independently": "Statistician re-read code/mtf.py:29-38 directly (confirms the bare-CSV-read claim exactly), confirmed the manifest's H1 status (AWAITING_REGIME_MAP) vs H1_from_M15_v2/H4_from_M15_v2 (CONTEXT_DERIVED_VALIDATED) directly, and re-verified _first_mitigation's equivalence to the frozen detect_mitigations[0] logic line-by-line (post formation_idx+2 fix).",
            "other_specs_checked": "Searched all Statistician documents for mtf.py/load_mtf/h1_trend_up/h4_trend_up references -- all OTHER hits are pure session-boundary arithmetic (asia/london/ny/late UTC-hour cutoffs, zero HTF-file dependency, no risk). The only risky references were within this SAME hypothesis's own evolving spec documents, not a new instance elsewhere.",
            "separate_legacy_cluster_flagged": "Found code/s1.py and code/run_mtf.py calling load_mtf() directly (a real, active usage, not just a stale reference) -- verified this is a COMPLETELY SEPARATE, older module (load_s1/generate/backtest/_pool, a pre-market_structure-era exploratory engine), distinct from code/trading_strategies.py::detect_s1 (the function actually behind every SMC_S1 verdict issued this session, which imports only market_structure/liquidity_mechanics/imbalance_mechanics/institutional_levels, zero mtf dependency). NO ratified verdict is affected. code/wave1_harness.py also references h4_trend_up from an unspecified source -- plausibly the same legacy cluster; notably 2 of the 4 standing pre-existing test failures live in test_wave1_harness.py, consistent with an unmaintained legacy module. RECOMMENDATION (not implemented here, a code-organization decision for CEO/Architect): label code/s1.py, code/mstrat.py, code/run_mtf.py, code/wave1_harness.py explicitly as LEGACY PRE-MASK -- DO NOT USE FOR RATIFIED HYPOTHESES.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_OBDZ001_BIAS_SOURCE_RATIFICATION_AND_IMPLEMENTATION_AUTHORIZATION_v1.0.md",
        },
        "population_count_results_v2_7_11": {
            "status": "MEASURED (Mandate 3.25) -- code/task_obdz_population.py, commit 51d02a4/cfb8c8b, independently re-executed by Statistician with identical results",
            "filter_chain_survivors": {
                "bear": {"step1_bias_aligned_bars": 35454, "step2_demandzones": 2275, "step3_composite_cross_candle": 275, "step4_after_atr_floor": 261},
                "bull": {"step1_bias_aligned_bars": 37707, "step2_demandzones": 2107, "step3_composite_cross_candle": 223, "step4_after_atr_floor": 194},
                "correction": {"step1_bias_aligned_bars": 17145, "step2_demandzones": 1178, "step3_composite_cross_candle": 156, "step4_after_atr_floor": 154},
            },
            "INSUFFICIENT_N": "TRIGGERS IN NO REGIME -- 261/194/154, all >=10x the n>=25 threshold.",
            "atr_at_survivors_dollars": {"bear": {"median": 2.11, "mean": 2.447}, "bull": {"median": 1.346, "mean": 1.555}, "correction": {"median": 2.203, "mean": 2.573}},
            "effective_horizon_distribution": {
                "bear": {"median": 20.0, "lt10": 6, "ge10": 255}, "bull": {"median": 20.0, "lt10": 10, "ge10": 184}, "correction": {"median": 20.0, "lt10": 8, "ge10": 146},
                "finding": "Statistician's own prior concern about the variable horizon did NOT materialize -- over 94% of survivors in every regime get the full 20-bar horizon (255/261=97.7%, 184/194=94.8%, 146/154=94.8%); only entries very close to end-of-day are truncated. The hypothesis measures what it claims to measure, not a truncation artifact.",
            },
            "required_winrate_range_RECOMPUTED": {
                "via_median_ATR": "Bear 34.9%, bull 37.3%, correction 34.8% -- range approx [35%,37%].",
                "via_mean_ATR": "Bear 34.4%, bull 36.4%, correction 34.2% -- range approx [34%,36%] (matches CEO's cited figure).",
                "discrepancy_explained": "ATR distribution is right-skewed in all 3 regimes (mean > median everywhere), so the mean-based range understates the threshold a typical eligible trade actually faces. RECOMMENDS the median-based range (~35-37%) as the more representative interpretive aid.",
                "caveat": "Neither range is the actual decision criterion -- the pre-registered test is H0: mean(net_R)<=0 computed directly per-trade with each trade's own R, not a comparison against any single aggregate winrate threshold (same rule established Mandate 3.13). The range is reported for interpretive calibration only.",
            },
            "implementation_authorization": "AUTHORIZED (Mandate 3.25) -- VE may implement the full state machine (bias -> cross-candle intersection -> ATR SL/TP1/TP2 -> partial exit -> net_R) and run the WP-5' block_bootstrap test (L>=28, H0: mean(net_R)<=0, family=1), STRICTLY on the 130,491 M15_v2 discovery bars. Holdout remains SEALED, untouched by this authorization or by the population count itself.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_OBDZ001_BIAS_SOURCE_RATIFICATION_AND_IMPLEMENTATION_AUTHORIZATION_v1.0.md",
        },
        "obdz001_final_verdict_v2_7_12": {
            "status": "REJECTED_AT_DECLARED_PARAMETRIZATION (Mandate 3.26) -- new scoped sub-label, same precedent as REJECTED_NET_OF_COST",
            "verified_by": "Statistician independently re-ran code/run_obdz001.py (commit 0d40212) directly -- every reported figure reproduced exactly.",
            "results_by_regime": {
                "bear": {"n_trades": 261, "reach_TP1": 94, "reach_TP2": 69, "breakeven_after_TP1": 20, "stopped_full": 158, "winrate": 0.3908, "expectancy_R": 0.0122, "net_sum_dollars": 9.26, "best_over_sumR": 0.6861, "wo1_netR": 1.00, "p_wp5": 0.5007, "realized_horizon_median": 1.0},
                "bull": {"n_trades": 194, "reach_TP1": 72, "reach_TP2": 49, "breakeven_after_TP1": 22, "stopped_full": 114, "winrate": 0.4021, "expectancy_R": -0.0400, "net_sum_dollars": -7.40, "best_over_sumR": -0.2802, "wo1_netR": -9.94, "p_wp5": 0.8256, "realized_horizon_median": 2.0},
                "correction": {"n_trades": 154, "reach_TP1": 58, "reach_TP2": 40, "breakeven_after_TP1": 16, "stopped_full": 89, "winrate": 0.4026, "expectancy_R": 0.0845, "net_sum_dollars": 26.06, "best_over_sumR": 0.1697, "wo1_netR": 10.81, "p_wp5": 0.1859, "realized_horizon_median": 2.0},
            },
            "scope_delimitation": (
                "REJECTS: H1: mu_netR>0 at the EXACT construction (SL=0.7xATR/TP1=1.4xATR/TP2=2.1xATR/"
                "75-25 partial exit), on the 3 M15_v2 discovery regimes (p=0.501/0.826/0.186, family=1). "
                "DOES NOT REJECT: the compound entry signal (H1/H4 bias + cross-candle DemandZone + "
                "unmitigated OB) as an independent source of directional information -- the SL/TP/partial-"
                "exit multiples were explicitly DECLARED design choices (Mandate 3.24), never derived from "
                "any property of the signal itself, so a null result under this specific choice is not "
                "evidence against the underlying signal. Verdict does not extrapolate to a different risk "
                "construction -- that would require its own pre-registration and test (see next_hypothesis "
                "below), not inference from this result."
            ),
            "mechanical_diagnosis_confirmed": (
                "Realized horizon collapsed from a median of 20 bars (available, per the population count) "
                "to a median of 1-2 bars (realized) -- over 88-90% of trades in every regime resolve in "
                "under 10 bars. Mechanism, verified: SL=0.7xATR is LESS than one average bar's true range "
                "(ATR), so a single adverse bar of average size can blow through the stop -- explaining why "
                "58-61% of trades stop out, and do so almost immediately. Reaching TP1 (2R) requires price "
                "to travel twice the stop distance without first retracing the (smaller) stop distance -- a "
                "rarer event, explaining the 36-38% TP1 hit rate. The SL/TP ratio is imbalanced: the stop "
                "sits inside a single bar's typical amplitude."
            ),
            "bear_correction_asymmetry_confirmed_not_verdict_changing": (
                "Confirmed CEO's own flagged observation, mechanically: bear's modest positive expectancy "
                "is a SINGLE-TRADE artifact (best_over_sumR=0.686, wo1 collapses 3.19->1.00, the "
                "NET_CONCENTRATION_INVENTORY pattern) -- fragile, not a repeatable phenomenon. Correction's "
                "positive expectancy is genuinely DISTRIBUTED (best_over_sumR=0.170, wo1 stays strongly "
                "positive 13.02->10.81 after removing the best trade). The two positive cells are not "
                "structurally equivalent -- worth noting for any future revisit, but neither rejects H0, so "
                "this does not change today's verdict."
            ),
            "required_winrate_puzzle_RESOLVED": {
                "issue": "Observed winrates (39.1%/40.2%/40.3%) sit ABOVE the v2.7.11 estimated threshold (~35-37%), yet expectancy is near-zero -- apparently paradoxical.",
                "resolution": "The realized average win is only ~1.4-1.7R, NOT the assumed 2.25R -- only 68-73% of TP1-reachers go on to TP2 in each regime (the rest settle for the 1.5R breakeven leg). Recomputed thresholds directly from the actual bucket breakdown (avg_loss approx 1R, since the stopped_full fraction matches 1-winrate almost exactly in every regime): bear 38.6%, bull 41.9%, correction 37.1% -- a range of approximately [37%,42%], not [35%,37%]. Observed winrates land almost exactly relative to these corrected thresholds (bear +0.5pp -> marginal positive expectancy, bull -1.7pp -> negative, correction +3.2pp -> clearly positive) -- fully explains the result, no residual paradox. Approximation, not exact (ignores the small ~5-6% plasa/EOD bucket's variable R), stated explicitly; the formal decision criterion remains mean(net_R)>0 computed per-trade, not any winrate threshold.",
            },
            "oracle_domain_question_UNRESOLVED_not_verdict_changing": {
                "issue": "block_bootstrap@v1 was validated for L>=H=20 (Mandate 3.20); L=28 nominally satisfies this since the MAXIMUM possible horizon is 20. But the REALIZED horizon (median 1-2 bars) is far shorter than the H=20 worst-case the calibration assumed -- true cross-trade dependency may be much thinner than what the null generator represents.",
                "likely_direction": "A null calibrated on longer-than-real dependency generally produces MORE resampling variance than warranted -- making the test MORE conservative (harder to reject H0 in either direction), not less. If so, true p-values under a correctly-recalibrated null (matched to the realized ~1-2 bar dependency) would likely be SMALLER than reported, not larger -- most relevant to the correction regime (p=0.186, the least overwhelming non-rejection).",
                "standing_asymmetric_rule_applied": "Same rule as LM-001 (Mandate 3.22): negative/null results (bear, bull) are robust to this uncertainty (a possibly-too-conservative null works in the safe direction for a negative conclusion). The correction regime's p=0.186 is NOT equally robust -- a dedicated recalibration (null generator matched to the realized horizon distribution, not the nominal H=20 ceiling) is required before that figure is trusted as a positive lean, if the OBDZ family is ever revisited. Does not change TODAY's verdict: none of the 3 p-values approach any plausible rejection threshold (~0.05) regardless.",
            },
            "next_hypothesis_recommendation": {
                "status": "PROCESS RECOMMENDATION, not an authorization -- no new run commissioned here",
                "mechanical_rationale": "SL=1.5xATR/TP1=3.0xATR (same 1:2 RR) would require an adverse move exceeding one average bar to be stopped -- mechanically plausible to reduce the stop-out rate, at the cost of larger per-stop dollar losses and a harder-to-reach TP1. Net direction unknown without measurement.",
                "recommended_path": "Reuse the SMC_S1_v2 precedent (Mandate 5.12/v2.7.7): a dedicated DIAGNOSTIC measurement of the real adverse/favorable excursion distribution after an OBDZ trigger, with a decision threshold PRE-REGISTERED before any number exists -- not a second blind SL/TP guess tested directly on the same data.",
                "family_if_pursued": "family=2 with OBDZ-001 (same discovery consumed a second time for a near-identical signal, same precedent as SMC_S1/SMC_S1_v2) -- MUST be fixed before any new run, per explicit instruction.",
                "if_not_pursued": "The correct reason is NOT 'p too large' generically -- it is that none of the 3 cells approach any plausible rejection threshold, and the mechanical diagnosis (stop narrower than typical bar amplitude) already fully explains the null with no unexplained residual warranting further investigation out of curiosity alone.",
                "diagnostic_now_specified": "See obdz_sltp_ratio_diagnostic_spec_v2_7_13 (top-level) -- the recommended diagnostic path is now fully specified (Mandate 3.27), not merely proposed.",
            },
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_OBDZ001_FINAL_VERDICT_v1.0.md + STATISTICIAN_OBDZ_SLTP_RATIO_DIAGNOSTIC_SPEC_v1.0.md (Mandate 3.27, diagnostic spec)",
        },
        "obdz_sltp_ratio_diagnostic_spec_v2_7_13": {
            "status": "EXECUTED BY VE, VERDICT CORRECTED (Mandate 3.28) -- see obdz_mae_mfe_control_confirmation_v2_7_14 (top-level). The literal mechanical verdict (MERITA IPOTEZA NOUA) was invalidated as an answer to the SL/TP-ratio question -- see that section for the full reasoning.",
            "w_threshold_independent_reverification": "Statistician recomputed W/breakeven-winrate DIRECTLY from raw per-trade net_R (not aggregate back-solving) via a temporary, uncommitted verification script: mean_win/mean_loss/breakeven_winrate = bear 1.8184/-1.1464/38.67%, bull 1.6884/-1.2022/41.59%, correction 1.8499/-1.1052/37.40% -- CONFIRMS the cited thresholds (38.6/41.7/37.4%) to within 0.1pp. The cited 'W' column (1.89/1.84/1.97) does not reconcile exactly with mean_win computed this way; the decision-relevant threshold figure is independently confirmed regardless.",
            "measurement_A_prime": {
                "population": "The 275/223/156 RAW cross-candle composite triggers (population_count_results_v2_7_11.filter_chain_survivors.step3_composite_cross_candle), NOT the 261/194/154 already ATR-floor-filtered -- the eligibility floor itself depends on SL_MULT (ATR_min=3*cost/SL_MULT), so applying the OLD floor before measuring geometry for NEW SL candidates would be circular (same principle as SMC_S1_v2's Measurement A).",
                "definition": "Maximum Adverse Excursion (MAE) in ATR14[t]-multiples, measured over [entry_idx+1, entry_idx+1+92] (92 bars = the already-established empirical day length, Mandate 3.18/3.19, reused verbatim) -- separate from the 20-bar trading horizon, which characterizes the exit RULE, not market behavior.",
                "candidate_set": "5 points: p25/p50/p75/p90 of the MAE-in-ATR distribution PLUS the original 0.7 anchor -- same 5-point structure as SMC_S1_v2's stop-geometry sensitivity design.",
                "TP_construction": "TP1=2x SL_candidate, TP2=3x SL_candidate for every candidate (preserves the exact 1x/2x/3x progression already established for 0.7/1.4/2.1) -- isolates the ratio question cleanly from a second, unrelated RR-redesign question.",
                "eligibility_floor_per_candidate": "ATR_min RE-DERIVED per SL candidate via the same 3x-cost-stress-saturation formula (3*cost/SL_MULT) -- shrinks as SL widens, admitting a slightly larger eligible population at wider candidates; reported explicitly per cell, not hidden.",
            },
            "three_required_items": {
                "horizon": "HELD FIXED at min(entry+20,EOD) across all 5 SL candidates (a controlled condition, isolating 'does the ratio matter' from 'did it also get more time') -- MANDATORY diagnostic: timeout fraction (unresolved, neither TP nor SL) reported at every candidate x regime cell; if it grows materially at wider candidates, disclosed as a known limitation of this diagnostic, not silently patched by also varying the horizon.",
                "payoff_structure": "MANDATORY full outcome-bucket breakdown (SL/TP1-then-TP2/TP1-then-breakeven/TP1-then-timeout/never-TP1-timeout) AND the explicit TP1->TP2 conversion rate at EVERY cell, not just expectancy -- the conversion rate (68-73% at SL=0.7) is expected to shift as TP2 moves farther away with wider SL, and must be visible, not inferred from expectancy alone.",
                "decision_threshold_PRE_REGISTERED": {
                    "CLOSED_PERMANENTLY": "Net DOLLAR expectancy <=0 at ALL 5 SL candidates, in ALL 3 regimes.",
                    "MERITS_NEW_HYPOTHESIS": "Net DOLLAR expectancy >0 at 2+ of the wider SL candidates (p75, p90), in 2+ of the 3 regimes -- a pattern in the wide part of the MAE distribution, not an isolated point.",
                    "AMBIGUOUS": "Anything mixed -- TESTABLE BUT INSUFFICIENT EVIDENCE, not a premature call either way.",
                    "dollars_primary_rule": "Reuses the SMC_S1_v2 rule verbatim: DOLLARS are the decision variable, not R -- a wider stop will show better R-normalized numbers almost mechanically (cost/R shrinks) while each stop-out is proportionally larger in real dollars. An R-only improvement does not clear the 'merits new hypothesis' bar.",
                },
            },
            "diagnostic_not_fitting": "The question is 'does the result depend on the ratio, or is it null everywhere', NOT 'which ratio gives the best result' -- the decision threshold above is fixed BEFORE any Measurement A' or re-run number exists, specifically because the temptation to read favorably is higher here (an existing positive, distributed cell already exists at correction). Same state machine (obdz001.py) runs for every candidate; the difference is that the decision rule was fixed before execution, not chosen after seeing results.",
            "multiple_testing_family": "CONFIRMED: the diagnostic itself (Measurement A' + the pre-registered decision rule) does NOT consume family count -- it is a measurement + decision rule, not a hypothesis test with its own H0/H1/verdict (same precedent as SMC_S1_v2's own Measurement A). Family remains 1 (OBDZ-001, already closed) unless and until the diagnostic produces a formally pre-registered new hypothesis -- only then does family become 2 (OBDZ-001 + successor), narrowing the significance threshold accordingly.",
            "oracle_recalibration_timing": "DEFER until after the diagnostic, not before -- reasoned sequentially: if the diagnostic yields a new hypothesis (wider SL), that hypothesis will have its own, likely much longer, realized-horizon distribution, making any recalibration done now (matched to the CURRENT 1-2 bar realized horizon) obsolete and requiring redoing anyway; if the diagnostic shows null everywhere (line closes permanently), the correction regime's p=0.186 recalibration becomes practically moot for any decision. Either way, recalibrating now would be wasted or duplicated effort.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_OBDZ_SLTP_RATIO_DIAGNOSTIC_SPEC_v1.0.md",
        },
        "obdz_mae_mfe_control_confirmation_v2_7_14": {
            "status": "EXECUTED BY VE (commit b233c83), TWO DESIGN ERRORS FOUND AND CORRECTED (Mandate 3.29) -- see obdz_mae_mfe_window_pullback_control_correction_v2_7_15 (top-level). Both errors are Statistician's own specification, confirmed directly, not VE execution errors.",
            "diagnostic_A_prime_verdict_CORRECTED": {
                "verified_by": "Statistician independently re-ran code/obdz_sltp_diagnostic.py (commit 465eb38) directly -- every cited figure reproduced exactly (MAE p50=4.399x ATR, timeout fractions 0.956-0.989 at p75/p90, conv_TP1_to_TP2=0.0/None at wide candidates, best_over_sumR=9.643 at correction p90, literal mechanical verdict MERITA IPOTEZA NOUA).",
                "why_invalidated": "At p75/p90 (SL=8.56x/13.61x ATR), TP1 (17-27x ATR) is essentially unreachable (reach_TP1 approx 0-3 out of 156-275 per cell) and 95.6-98.9% of trades resolve ONLY via the 20-bar timeout -- this measures generic drift over a fixed window at an effectively-infinite stop/target, not the SL/TP RATIO the diagnostic was designed to test. A specification gap Statistician owns (should have included a minimum-resolution-rate guard when writing v2.7.13), not a VE execution error -- VE flagged all three limitations (timeout fraction, zero conversion, extreme concentration) unprompted and correctly declined to patch by widening the horizon, which would have reintroduced the confound.",
                "p25_also_fails": "The one candidate still structurally testing the ratio (p25, SL=1.965x ATR, timeout 0.356-0.444, a reasonable range) shows positive dollar expectancy in only 1 of 3 regimes (correction, +$9.7; bear -$85.5, bull -$39.7) -- short of the pre-registered 2+ threshold.",
                "reclassification": "TESTABLE BUT INSUFFICIENT EVIDENCE for the SL/TP-ratio question specifically -- 'insufficient' here means the tested construction stopped representing the intended mechanism at the wide end, not that more data would resolve it. OBDZ-002 is NOT formulated from this literal threshold trigger.",
            },
            "mae_as_zone_property_or_market_property": "Open question, requires the control below -- MAE=4.4x ATR alone cannot distinguish 'the compound trigger identifies unusually exposed moments' from 'any bias-aligned bar over 92 bars shows this much adverse excursion'. Same category of question as the E004 fill-rate control (85% baseline; 71% for the specific construct, BELOW not above baseline).",
            "randomized_control_spec": {
                "population": "Randomly sampled M15 bars from each regime's OWN bias-aligned population (population_count_results_v2_7_11 step1_bias_aligned_bars: 35,454/37,707/17,145), WITHOUT replacement, matched in COUNT exactly to the raw triggers (275/223/156) -- isolates the SPECIFIC contribution of the cross-candle DemandZone x unmitigated-OB intersection versus plain bias alignment, not versus an unconstrained random bar.",
                "direction": "= the bias direction at the sampled bar (same convention as OBDZ triggers).",
                "no_atr_floor": "Same convention as Measurement A' -- clean raw-to-raw comparison.",
                "seed": "20260729 (reused from the WP-5' bootstrap convention, for reproducibility).",
                "reading_rule": "MAE-control approx MAE-triggers -> the zone adds nothing beyond bias alignment; 4.4x ATR is a market-volatility property, not a zone property. MAE-control materially SMALLER -> triggers are systematically MORE exposed than a random bias-aligned bar, supporting the 'zone identifies exposed, not protected, moments' theory. MAE-control materially LARGER -> triggers are relatively protected versus random, undermining the case for any confirmation fix.",
            },
            "mae_mfe_bar_of_touch_spec": {
                "definition": "For every event (trigger AND control), on the same [entry+1, entry+1+92] window: MAE (already defined) AND MFE (Maximum Favorable Excursion, symmetric definition) in ATR14[entry]-multiples, PLUS bar_MAE and bar_MFE -- the bar index (relative to entry) where each extremum is FIRST reached.",
                "required_reporting": ["MAE distribution (already have)", "MFE distribution (p25/p50/p75/p90)", "per-event MFE/MAE ratio distribution", "fraction of events with bar_MAE<bar_MFE vs bar_MAE>bar_MFE vs tied", "bar_MAE and bar_MFE distributions (as bar counts from entry)"],
                "interpretation_grid": {
                    "early_MAE_late_MFE_MFE_not_small": "Entered too early, the directional idea is correct -- supports pursuing a timing/confirmation fix.",
                    "MAE_large_MFE_systematically_small": "The zone does not predict a real reversal, not merely a bad moment -- a confirmation fix would not help either.",
                    "bar_MAE_approx_bar_MFE_both_early_comparable_magnitude": "Measuring generic volatility, not a directional pattern -- no amount of waiting for confirmation would help.",
                },
                "apply_to_both_populations": "Run identically on triggers AND on the randomized control -- distinguishes whether the SEQUENCING pattern (not just MAE magnitude) is zone-specific or a generic property of any bias-aligned bar.",
            },
            "confirmation_variants_reviewed": {
                "variant_3_engulfing_magnitude": "CONFIRMED to require ZERO new primitives -- exactly the already-ratified OB formation criterion (E010 displacement/expansion + body engulfment). Structural mechanic specified: after the compound trigger at bar t, wait for the first bar j>=t where a NEW impulse (same range>1.5xATR14[j-1] AND body>=0.5xrange criterion) occurs in the bias direction; entry becomes j+1, not t+1. Numeric parameters (SL/TP/horizon) explicitly NOT specified here -- to be derived from the measurements above, applied to the CONFIRMED-entry population.",
                "variant_1_pinbar": "Confirmed via exhaustive code search to require NEW geometry (detect_rejections' wick-sweep-reject definition is different from close-in-upper-third + wick>=60%-of-range). HELD, per CEO's own suggestion, pending Variant 3's result.",
                "variant_2_inside_bar": "Confirmed zero occurrences of inside_bar anywhere in code -- requires new geometry entirely. HELD, same reasoning as Variant 1.",
            },
            "h1_h4_wiring_gap_confirmed_and_gated": {
                "confirmed": "Exhaustive search: detect_order_blocks/detect_demand_zones have NEVER been called on H1_from_M15_v2 or H4_from_M15_v2 -- only ever on M15 bars (obdz001.py, task_obdz_population.py, obdz_sltp_diagnostic.py, synthetic tests). Not a missing primitive -- the same functions apply to any OHLC; a genuine wiring gap, confirmed real not merely flagged.",
                "required_before_full_implementation": "A READ-ONLY population-count-only script (analogous to task_obdz_population.py) running the EXISTING, already-ratified formation criteria directly on H1_from_M15_v2 (49,580 bars) and H4_from_M15_v2 (12,832 bars total across the whole discovery period), reporting zone/OB counts per regime -- BEFORE any effort to build the full cross-timeframe entry state machine.",
                "insufficient_n_risk_flagged": "M15's full compound condition yielded only 275/223/156 raw triggers out of 130,491 bars (approx 0.2-0.3% rate); H4 has only 12,832 total bars for the whole period -- the same formation rate applied there could plausibly yield a population below the n>=25/regime threshold, especially in the already-smallest regime (correction). INSUFFICIENT_N applies AT THIS COUNTING STEP, not deferred to the end -- if the H1/H4 population is already insufficient, report and stop before building further mechanics.",
            },
            "obdz002_parameters_DEFERRED": "SL, TP1/TP2, and horizon for the confirmation-based hypothesis are explicitly NOT specified in this document, per direct instruction -- they will be derived from the measurements above (confirmed-entry MAE/MFE distribution informs the stop; MFE ratio informs whether 2x/3x still holds; the actual SL/TP-resolution-bar distribution under candidate parameters informs the horizon), not chosen from intuition as 0.7xATR originally was.",
            "multiple_testing_family_confirmed": "Family=2 with OBDZ-001, NOT separated. The test is not 'how mechanically different is the new entry rule' -- it is 'was this hypothesis's design informed by looking at results from the SAME discovery data'. The confirmation mechanism's entire justification (the MAE=4.4x-ATR finding) comes directly from a diagnostic run on OBDZ-001's own discovery-based measurement -- exactly the SMC_S1/SMC_S1_v2 precedent. A MORE substantial mechanism change informed by the same data deserves MORE caution, not an exemption from the family rule.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_OBDZ_MAE_MFE_CONTROL_AND_CONFIRMATION_SPEC_v1.0.md + STATISTICIAN_OBDZ_MAE_MFE_WINDOW_AND_PULLBACK_CONTROL_CORRECTION_v1.0.md (Mandate 3.29, corrects two design errors CEO found)",
        },
        "obdz_mae_mfe_window_pullback_control_correction_v2_7_15": {
            "status": "EXECUTED BY VE (commit d869177), GRID READ (Mandate 3.30) -- see obdz_three_arm_grid_reading_v2_7_16 (top-level). Result: zone beats matched pullback descriptively (aggregate + 2/3 regimes clear the pre-registered threshold), NOT yet formally tested -- an observation, not a proven finding.",
            "verified_by": "Statistician independently re-ran code/obdz_mae_mfe_control.py (commit b233c83) directly -- confirms both errors precisely: median bar_MAE=35.0/32.0/41.0 and bar_MFE=41.0/45.0/35.5 across bear/bull/correction (all 'second trading day' moves, not immediate reaction); zone vs bias-aligned control nearly indistinguishable on the aggregate 92-bar window (MAE median 4.40 zone vs 4.82 control; MFE median 4.67 vs 4.46).",
            "error_1_measurement_window": {
                "diagnosis": "The 92-bar window was reused verbatim from an unrelated derivation (the empirical trading-day length, originally for a compression/volatility measure, Mandate 3.18/3.19) -- it measures general ~1-day volatility after ANY point, not reaction to the zone specifically. This mechanically explains why zone and control looked identical: the measure carried no reaction-specific information regardless of what it was compared against.",
                "corrected_windows": "Four windows starting one bar after entry (touch+2 in CEO's notation = entry+1 in the code's existing convention, since entry=touch+1 already): [entry+1,entry+2] (touch [+2,+3]), [entry+1,entry+4] (touch [+2,+5]), [entry+1,entry+9] (touch [+2,+10]), [entry+1,entry+19] (touch [+2,+20], the real 20-bar trading horizon). MAE/MFE reference price stays entry_price (unchanged); only which bars get scanned changes. [+2,+5] and [+2,+10] are the PRIMARY decisive windows per CEO's own framing ('if the zone produces anything, it shows there or nowhere'); [+2,+3] and [+2,+20] are reported as context.",
                "92_bar_result_disposition": "KEPT, not retracted -- Statistician's own call as explicitly requested. Relabeled explicitly as a general ~1-day volatility profile (zone vs bias-aligned control), NOT an immediate-reaction measure, so it cannot be misread later as evidence about reaction timing.",
            },
            "error_2_missing_pullback_control": {
                "diagnosis": "The existing bias-matched control (arm B) isolates the zone's contribution over plain bias alignment, but conflates a second variable: zone entries are, by construction, always at a pullback/retracement (a Mitigation touch requires price to have moved against the bias to reach the zone), while arm B includes any bias-aligned bar, including fresh local extremes with zero pullback. If pullbacks in-trend behave systematically worse than random entries (plausible -- buying into a still-falling price), 'zone approx random' could actually mean 'zone beats simple pullback', which the current design cannot distinguish.",
                "pullback_depth_definition": "Reuses the already-established market_structure.py Swing/StructureLabel primitive (the same one used in SMC_S1_v2's Measurement A 'prior major swing') rather than inventing a new rolling-window measure: pullback_depth(j) = (nearest prior CLASSIFIED swing extreme against the bias direction, price - price[j]) / ATR14[j] -- swing HIGH for bullish bias, swing LOW for bearish, strictly earlier, same discovery block (D4). Undefined (and excluded, count reported separately) if no such swing exists in-block, same edge-case discipline as SMC_S1_v2.",
                "arm_C_construction": "Source pool = the same bias-aligned pool used for arm B, MINUS the 275/223/156 zone-trigger bars themselves. For each zone trigger with a defined pullback_depth, match to a candidate bar whose pullback_depth falls within 25% relative OR 0.5xATR absolute tolerance (whichever is wider, a disclosed convention not derived), widening progressively (doubling the band) up to a hard cap (100%/2xATR) if no match found -- triggers still unmatched at the cap are reported explicitly, never silently dropped or force-matched. One candidate selected at random per trigger (seed 20260729+regime_index, matching the arm-B convention), without replacement within the regime. Entry mechanics (entry=matched_bar+1, direction=bias, ATR at matched_bar) identical to arms A/B -- only the selection criterion differs.",
                "A_vs_C_comparison_scope": "Arm A, for the A-vs-C comparison specifically, is restricted to the subset of triggers with a defined pullback_depth (may exclude a few per the edge case above) -- reported distinctly as 'A_subset_matched', separate from the already-measured 'A_full' (all 275/223/156) used for the existing A-vs-B comparison, so the two are never conflated.",
            },
            "interpretation_grid_PRE_REGISTERED": {
                "primary_read_windows": "[+2,+5] and [+2,+10] median MFE -- the windows CEO identified as decisive for whether the zone produces an early reaction.",
                "pullback_matters_zone_does_not": "A_subset approx C (median MFE within 15% of each other) AND both A_subset and C exceed B by more than 25% -- closes the zone-specific (DemandZone x OB) angle; a separate 'pullback alone, no zone' hypothesis remains a distinct, undecided possible direction.",
                "zone_adds_beyond_pullback": "A_subset exceeds C by more than 25% in median MFE -- the confirmation-timing idea (Variant 3) remains worth pursuing.",
                "neither_matters": "A_subset approx C approx B (all three within 15% of each other) -- closes the entire OBDZ line, not just the zone-specific angle.",
                "otherwise": "TESTABLE BUT INSUFFICIENT EVIDENCE -- no premature call.",
                "thresholds_disclosed": "15%/25% are disclosed conventions, not derived constants -- same category as other pragmatic thresholds already accepted in this lab (n>=25, alpha=0.05).",
            },
            "obdz_verdict_status": "REMAINS DEFERRED -- today's result (zone approx control on the 92-bar window) answers a narrower question than the one that matters ('does the zone beat an unconstrained bias-aligned entry on 1-day volatility' -- no), not whether the zone beats a matched pullback, and the immediate reaction (windows +2 through +20) has not yet been measured at all.",
            "task_2_H1_H4_count_status": "REMAINS HELD, unchanged -- conditional on this corrected measurement's result, not run prematurely on a signal whose predictive capacity is still undetermined.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_OBDZ_MAE_MFE_WINDOW_AND_PULLBACK_CONTROL_CORRECTION_v1.0.md + STATISTICIAN_OBDZ_THREE_ARM_GRID_READING_v1.0.md (Mandate 3.30, grid reading)",
        },
        "obdz_three_arm_grid_reading_v2_7_16": {
            "status": "GRID READ (Mandate 3.30) -- descriptive pattern found, NOT yet formally tested; new oracle-domain question raised and answered; CEO's stated polarity premise checked and found incorrect",
            "verified_by": "Statistician independently re-ran code/obdz_three_arm_windows.py (commit d869177) directly -- every cited figure reproduced exactly: 100% A-to-C match (275/223/156, 0 unmatched, 0 pullback-undefined); MFE median at [entry+1,entry+4]: A=0.85/1.06/1.11, B=0.80/0.80/0.90, C=0.75/0.77/0.76 (bear/bull/correction); aggregate A=0.97/B=0.81/C=0.76; [entry+1,entry+9]: A=1.39 vs B=C=1.16; bear's MAE/ratio asymmetry (A_MAE=1.09/C_MAE=0.84, A_ratio=0.43/C_ratio=0.68).",
            "grid_reading": {
                "primary_window_result": "Aggregate (+27.6%) and 2 of 3 regimes (bull +38%, correction +46%) clear the pre-registered 25% 'zone adds beyond pullback' threshold at [+2,+5]. Bear (+13%) is directionally consistent but below threshold. At [+2,+10] the aggregate gap narrows to approx 20%, still positive but not clearly clearing 25%.",
                "characterization": "NOT a clean unanimous pass, NOT a null-everywhere close -- a consistent-direction pattern with regime-varying magnitude, exactly the ambiguous middle case the 25%/15% thresholds were written to catch rather than force into either extreme.",
            },
            "new_oracle_domain_question_ANSWERED": {
                "question": "Is block_bootstrap@v1 (validated for a single overlapping-window net_R series) the right tool for an A-vs-C comparison?",
                "answer": "NO, not directly -- A-vs-C is a matched 1:1 PAIRED comparison (each zone trigger matched to exactly one pullback-control partner by construction), a different statistical object than a one-sample overlapping-net_R mean test. The correct question is on the per-pair difference d_i = MFE_A_i - MFE_C_i, not on the two distributions separately -- a paired test (Wilcoxon signed-rank, or bootstrap on the paired mean/median difference) is both more appropriate and more powerful, since it automatically controls for anything common to a matched pair.",
                "residual_dependence_flagged": "Nearby trigger events could still be correlated in time (shared market conditions), meaning the PAIRS themselves might not be independent draws -- an analogous, not identical, concern to net_R's overlap dependence. RECOMMENDS reusing the block_bootstrap RESAMPLING MECHANICS (not its net_R calibration) applied to the time-ordered d_i series, run ALONGSIDE a plain iid bootstrap as a baseline -- if the two agree closely the finding is robust to the dependence-calibration question; if they diverge, that divergence is itself the informative result (same category of reasoning as LM-001's own r_variance_note).",
                "not_yet_run": "This paired test has NOT been executed. Today's +28%/+38%/+46% pattern is an OBSERVATION, not a validated finding, per explicit instruction to say so plainly if that is the honest characterization. This diagnostic (like Measurement A' before it) does not consume the multiple-testing family -- it decides whether a real hypothesis is worth formulating, it is not the hypothesis test itself.",
            },
            "polarity_premise_CORRECTED": {
                "ceo_stated_premise": "bear regime = 100% supply (short) triggers; bull/correction = 100% demand (long) triggers, implying regime and polarity are confounded and cannot be separated without contra-trend data.",
                "independently_verified_FALSE": "Ran a direct count of A_full trigger direction per regime (temporary, uncommitted script): bear 57.8% demand/42.2% supply; bull 54.7% demand/45.3% supply; correction 62.2% demand/37.8% supply -- all THREE regimes are substantially mixed-polarity, not clean splits.",
                "consequence": "Polarity-versus-regime CAN be distinguished directly from the ALREADY-COLLECTED data by re-stratifying the SAME A/C events by polarity (demand vs supply) POOLED ACROSS regimes, rather than by regime -- no contra-trend data collection is needed, resolving the open question CEO left undecided.",
            },
            "next_steps_ordering_IF_paired_test_confirms": [
                "1. Paired test (iid + block-resampled) on d_i at [+2,+5]/[+2,+10], aggregate and per-regime -- GATES everything below.",
                "2. Polarity re-stratification (existing events, resliced by direction not regime) -- runs IN PARALLEL with step 1, decides demand-only vs both-polarities scope for any resulting hypothesis.",
                "3. ONLY IF step 1 confirms: derive SL/TP candidates from the [entry+1,entry+4] MAE distribution (now measured: median 0.88-1.09x ATR per regime -- far tighter and more informative than either the original 0.7x anchor or the blind 92-bar-window 4.4x figure).",
                "4. Confirmation mechanism (Variant 3) requires its OWN separate MAE/MFE re-measurement from the confirmed-entry point, not an assumed carryover of the touch-based figures above.",
                "5. H1/H4 population count remains HELD, unchanged -- relevant only once 1-4 establish the base mechanism is worth building.",
            ],
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_OBDZ_THREE_ARM_GRID_READING_v1.0.md + STATISTICIAN_OBDZ_FREQUENCY_CONSTRAINT_AND_TOUCH_FUNNEL_v1.0.md (Mandate 3.31, frequency-constraint addendum)",
        },
        "obdz_frequency_constraint_touch_funnel_v2_7_17": {
            "status": "SPECIFICATION (Mandate 3.31) -- addendum to the pending grid verdict, does not relax anything, does not choose a frequency lever",
            "frequency_arithmetic_verified": {
                "target": "CEO's operational constraint: approximately 5 trades/week on M15.",
                "actual_confirmed": "Verified directly against manifest discovery-block durations (bear 794.0 days=2.174y, bull 816.1 days=2.234y, correction 390.2 days=1.068y, total 2000.4 days=5.477y): bear 261 trades/2.174y=120.1/yr=2.31/wk; bull 194/2.234y=86.8/yr=1.67/wk; correction 154/1.068y=144.2/yr=2.77/wk (a minor refinement from CEO's cited 3.0/wk, which assumed a flat 1.0y duration rather than the exact 1.068y); aggregate 609/5.477y=111.2/yr=2.14/wk. Confirms roughly HALF the 5/week target.",
            },
            "population_funnel_unit_mismatch_CONFIRMED": {
                "issue": "The population-count funnel mixes units across its three steps: step1 (90,306=35,454+37,707+17,145) is a count of BARS; step2 (5,560=2,275+2,107+1,178) is a count of ZONES formed; step3 (654=275+223+156) is a count of TRIGGER (OB-mitigation) EVENTS. No valid survival rate can be computed between these -- a single zone can be touched zero, one, or many times, so 654/5,560 says nothing about zone survival.",
                "attribution_verified": "Confirmed this specific claim ('collapse happens at step 3, of 2,000+ zones under 300 survive') was never made in any Statistician document -- CEO's own self-correction to a prior claim, independently verified as accurate, not a Statistician error.",
            },
            "touch_funnel_specified_REQUESTED_NOW": {
                "status": "REQUESTED NOW, in parallel with the still-pending paired test (Mandate 3.30) -- purely read-only descriptive counting, relaxes nothing in the entry/exit mechanism.",
                "consistent_unit": "All three steps expressed at ZONE level (not bar, not event), directly comparable to the 5,560 zones-formed baseline: T1 = zones touched at least once (price re-enters [zone_lower,zone_upper] at any point post-formation, same discovery block) -- a zone-level survival count; T2 = of T1, zones whose FIRST touch has a cross-candle unmitigated OB overlapping (exact Decizia 3 mechanics, already ratified); T3 = of T2, zones whose first-touch bar has aligned H1+H4 bias.",
                "reported_by_polarity_too": "Split by demand vs supply, not just regime -- ties directly to the polarity re-stratification already specified in Mandate 3.30 and to the bear/supply MFE-to-MAE asymmetry flagged in context.",
                "why_location_of_collapse_matters": "If collapse is at T1 (zones rarely touched at all), the problem is AVAILABILITY -- the right lever is a different zone construction, not relaxing the composite condition. If collapse is at T2 (confluence itself is rare), Lever 2 (additional zone types) or reconsidering the overlap window is more relevant. If T1/T2 are populous but T3 removes most of it, Lever 1 (H4-only bias) is the most relevant to test first.",
            },
            "three_levers_FRAMED_NOT_CHOSEN": {
                "no_lever_run_before_verdict": "None of the three levers below are authorized or run in this document -- if the paired test (Mandate 3.30) shows noise, no lever matters (frequency cannot rescue an absent signal); if it shows signal, choosing among levers becomes a design decision requiring its own measurement, not an assumption.",
                "lever_1_H4_only_bias": "Redefine bias as H4 alone (drop the H1 alignment requirement), rebuild the composite trigger set under this relaxed condition, re-run the SAME three-arm (A/B/C) measurement at the SAME primary windows. The question is NOT whether frequency rises (it almost certainly would) but whether the ~28% zone-over-pullback effect SURVIVES -- if it does, dual alignment was only a frequency filter; if it shrinks or vanishes, H1 alignment is part of the mechanism itself (plausibly filtering out bars where H4 trend exists but local H1 structure is already turning).",
                "lever_2_additional_zone_types": "FVG, Breaker, and PDH/PDL are already-implemented, untested-for-this-purpose primitives -- each MUST be measured entirely SEPARATELY (its own compound cross-candle-zone x [type]-unmitigated trigger construction, its own three-arm measurement), never pooled together, since each is a structurally distinct primitive with its own properties. Whether combining qualifying types (a union) dilutes or preserves the effect is an explicitly SEPARATE, later question, contingent on the individual results.",
                "lever_3_M15_native_zones_FLAGGED_AS_REGRESSION": "Explicitly NOT a neutral lever among equals -- reverses the original mandate's own deliberate design choice (HTF zones, M15 entry, specifically for larger/rarer/more-reliable zones) back toward something closer to the original OBDZ-001 M15-native construction already rejected at its declared parametrization. If considered, must be treated as a substantive hypothesis change, not a marginal frequency adjustment.",
            },
            "frequency_decision_status": "UNDECIDED, per explicit instruction -- deferred until the paired test (Mandate 3.30) reads out. A legitimate possible outcome, stated explicitly: if no lever preserves the effect while raising frequency, a rare (~2.2/week or less) but real, confirmed edge remains a valid result for a discretionary strategy, not a failure.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_OBDZ_FREQUENCY_CONSTRAINT_AND_TOUCH_FUNNEL_v1.0.md + STATISTICIAN_OBDZ_ZONE_TYPE_SURVEY_FAMILY_SIZE_v1.0.md (Mandate 3.32, family size fixed for the ten-zone-type survey)",
        },
        "obdz_zone_type_survey_family_size_v2_7_18": {
            "status": "SPECIFICATION (Mandate 3.32) -- fixes family size and ordering BEFORE any of the ten zone types are measured; nothing authorized to run",
            "ten_types_verified": {
                "ready_zero_new_code": ["Order Block (detect_order_blocks)", "Breaker Block (track_breaker)", "Demand/Supply (detect_demand_zones)", "FVG (detect_fvgs)", "CE-50 (detect_fvg_reactions)", "IFVG (detect_inverse_fvgs)", "BPR (count_bpr)", "Liquidity Void (detect_liquidity_voids, code/order_block_void.py:66)", "PDH/PDL (compute_prior_day_levels)", "PWH/PWL (compute_prior_week_levels)"],
                "missing_confirmed_via_search": ["Session Open as a level (zero occurrences of session_open/SessionOpen anywhere in code)", "Mitigation Block (see mitigation_rejection_block_determination below)", "Rejection Block (same)"],
            },
            "family_size_two_distinct_questions": {
                "descriptive_measurement_phase": "Does NOT consume family -- same reasoning as the touch funnel and Measurement A' before it: the three-arm MAE/MFE characterization is not a hypothesis test with its own H0/H1/verdict, for any of the ten types. The 'thirty comparisons' (10 types x 3 arms) remain pure diagnostic regardless of how many show a promising descriptive pattern.",
                "eventual_formal_hypothesis_phase": "FIXED NOW at family=10 -- this is the actual guard against the 1972-hypothesis-campaign trap (where alpha collapsed to 0.000032 and nothing could pass). The correction must reflect how many candidates were LOOKED AT, not how many happened to look promising after the fact -- looking at ten and testing only the winners without correcting for the looking is the exact selection-bias trap that campaign fell into.",
                "overlap_with_OBDZ_001_002_noted": "'Order Block' and 'Demand/Supply' in the ten-type list ARE the construction already measured in OBDZ-001/002's three-arm result -- that result counts as element 1 of the ten-type family, NOT a fresh, uncorrelated re-measurement. The remaining nine (Breaker, FVG, CE-50, IFVG, BPR, Liquidity Void, PDH/PDL, PWH/PWL) are genuinely new measurements.",
            },
            "wave_ordering_CONFIRMED_with_justification": {
                "wave_1": "The 8 interval-based zone types (Order Block already measured, Breaker, Demand/Supply, FVG, CE-50, IFVG, BPR, Liquidity Void) -- share the same geometric nature (an own [low,high] or [close,open] interval), the most natural homogeneous group to measure together first.",
                "wave_2": "PDH/PDL, PWH/PWL -- split out on a STRUCTURAL basis, not an arbitrary priority ordering: these are single-price reference LEVELS, not interval zones, so their touch/unmitigated semantics genuinely differ from wave 1's zone concept (a level can be retested repeatedly without the same interval-width ambiguity a zone carries).",
                "wave_3": "The 3 new primitives (Session Open as level, Mitigation Block, Rejection Block) -- GATED on waves 1-2 showing a promising pattern, same discipline already applied to holding confirmation Variants 1/2 pending Variant 3's result. No investment in new code for a question waves 1-2 might already answer negatively.",
            },
            "mitigation_rejection_block_determination": {
                "verified_in_code": "detect_mitigations(ob: OrderBlock, ...) and detect_rejections(ob: OrderBlock, ...) both take an ALREADY-FORMED OrderBlock as input and return list[ReactionEvent] -- these are REACTION-EVENT detectors bound to a pre-existing zone formed by something else (the OB), NOT standalone primitives that define their own zone boundary from raw price (unlike OB/FVG/PDH, each of which derives its own interval directly from bars).",
                "conclusion": "NOT the same thing as the existing detectors under a new name, and NOT resolvable without CEO's own clarification of intent. If 'Mitigation Block'/'Rejection Block' means 'the reaction bar itself becomes a new, independently-testable zone' (analogous to how a Breaker reuses the OB zone with inverted polarity, but here anchored at the reaction bar instead), that IS a genuinely new primitive requiring its own zone-boundary definition and validity/measurement-window separation, with the same rigor OB/DemandZone received -- not invented unilaterally here. Remains in Wave 3, gated on both waves 1-2's result AND this clarification.",
            },
            "pending_paired_test_reaffirmed_priority": "Unchanged -- nothing in this document authorizes running any zone-type measurement. Family size and ordering are fixed now so they are ready the moment the paired test (Mandate 3.30) confirms the methodology finds something real, not noise repeated in ten forms.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_OBDZ_ZONE_TYPE_SURVEY_FAMILY_SIZE_v1.0.md",
        },
        "mitigation_rejection_circularity_fix_v2_7_9": {
            "status": "RATIFIED (Mandate 3.23)",
            "found_by": "VE, while implementing Piece 1 (code/order_flow.py, commit 3fad03e) -- flagged as an unrequested finding, not something asked for.",
            "defect": "_scan_reactions scans from ob.formation_idx+1, which equals i (the IMPULSE bar, since formation_idx=i-1 the anchor bar). By the engulfment condition that defines OB formation, the impulse candle's body always spans the zone -- guaranteeing a spurious 'visit 1' on the very bar that created the OB. Same category of defect as E010: a window that contains, by construction, the event it claims to measure.",
            "generalization_by_statistician": "VE's own finding was framed around Mitigation. Verified directly (algebra on the engulfment inequalities) that the SAME guarantee holds for Rejection too: low[i]<=zl and close[i]=i_hi>=zh>zl (for bullish, nonzero-body case) satisfy the D6 wick-sweep-reject condition on the impulse bar as well. Both event types are corrupted at bar 1, not just Mitigation.",
            "fix_ratified": "Scan starts at formation_idx+2 (skip the impulse bar) for BOTH detect_mitigations and detect_rejections. Minimal fix -- removes exactly the one bar demonstrated responsible, no new degrees of freedom. Does not touch the anti-E010 selection/measurement window separation (unchanged, disjoint by construction).",
            "retroactive_effect": "NONE -- Mitigation/Rejection were implemented this mandate, never run on real data, and no formalized SMC_S* family consumes them yet (verified: no import of detect_mitigations/detect_rejections outside their own test file).",
            "classification": "Blocking-partial status LIFTED -- resolved by specification; VE implements scan_start=formation_idx+2 and re-runs the existing anti-lookahead tests (must stay green).",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_MITREJ_CIRCULARITY_COST_VERDICTS_HYPOTHESIS_v1.0.md",
        },
        "demandzone_ob_intersection_and_partial_exit_defaults_v2_7_9": {
            "status": "RATIFIED (Mandate 3.23)",
            "Q2_intersection": "Confirmed TRIVIAL as implemented (code/order_flow.py detect_demand_zones -- each DemandZone shares its OB's own formation_idx/anchor bar, so DemandZone superset-of-OB-body holds on the SAME bar always, by construction; A=B collapses to plain OB). RATIFIED as operative for next_hypothesis_atr_partial_exit_v2_7_8: the SUBSTANTIAL (A!=B, cross-candle) reading -- an unmitigated OrderBlock from formation event B, geometrically overlapping (interval-overlap, not full containment) an ACTIVE DemandZone from a DIFFERENT formation event A. Entry bar = OB_B's own qualifying Mitigation event (per the circularity-fixed scan), conditioned on DemandZone_A (A!=B) overlap at that bar.",
            "Q3_stop_before_target": "RATIFIED True -- the MIN_STOP_FLOOR_PREREG:31 worst-case convention (stop wins an ambiguous same-bar ordering) is about intrabar-order ambiguity in general, not specific to the final target; applies identically to TP1.",
            "Q4_tp1_tp2_same_bar": "RATIFIED True -- NOT merely a default: TP2>TP1 (same favorable direction) means a bar reaching TP2 mechanically reached TP1 first within the same bar's range (monotonic ordering forces it). Treating them as separate-bar events would introduce an artificial delay where none exists.",
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_MITREJ_CIRCULARITY_COST_VERDICTS_HYPOTHESIS_v1.0.md",
        },
        "FINAL_VERDICT_RECLASSIFIED_v2_7_9": {
            "status": "RATIFIED (Mandate 3.23) -- supersedes lm_001_preregistration.FINAL_VERDICT (kept unedited as historical record)",
            "structural_finding_confirmed": "edge_brut_$ (mean gross $, cost- and TICK-independent) is unchanged by the cost correction -- correcting cost 0.40->0.20 shifts the decision bar and improves net by $0.20/trade, it does NOT create new edge. Without this distinction, cells crossing from below-0.40 to above-0.20 would misread as improved signal quality rather than a lower bar over the SAME edge_brut.",
            "prior_estimate_not_reproduced": "Statistician's own prior estimate (6/8 families would pass) does NOT reproduce -- independently verified: edge_brut_$>=0.40 in 3/24 cells (old bar); >=0.20 in 6/24 cells (new bar); only 4/8 families (S7,S11,S16,S17) have >=1 qualifying cell, not general family profitability. Recorded as Statistician's own missed prediction.",
            "new_filter_authoritative": "The re-derived [0.58,6.50)$ filter (see lm_001_preregistration.execution_layer.displacement_filter) is authoritative UNCONDITIONALLY, regardless of which filter flatters any given cell. S16-correction's sign flip (+0.293 old filter -> -0.077 new filter, both independently reproduced) is an EXPECTED mechanical consequence of the lower floor admitting more small/noisy displacement events -- not an error, not grounds to keep the old (wrong-cost-derived) filter.",
            "SMC_S1_reclassified": {
                "old_label": "REJECTED_NET_OF_COST",
                "new_label": "STATISTICALLY REJECTED",
                "why_relabeled": "REJECTED_NET_OF_COST existed specifically to preserve 'a real, mechanically-demonstrated positive gross edge, just smaller than cost'. At the corrected cost/filter, edge_brut_$ is -0.0007/+0.0214/-0.1128 (old filter) and +0.0312/-0.0072/-0.0582 (new filter) across bear/bull/correction -- near-zero and INCONSISTENT IN SIGN, not the small-positive-monotonic pattern the original label was built on. The distinction the old label protected no longer holds.",
                "p_values": "Overwhelmingly non-significant in all 6 cells (old/new filter x 3 regimes): 0.93/0.88, 0.98/1.0, 0.97/0.89 -- H1:mu_netR>0 nowhere close to rejecting H0.",
                "scope_delimitation": "Rejects H1:mu_netR>0 at the current Open-R construction (mechanical direction, 20-bar horizon, time-exit), both filter variants, on the 3 M15_v2 discovery regimes. Does not extrapolate to a different risk construction (e.g. next_hypothesis_atr_partial_exit_v2_7_8) or detection mechanism.",
            },
            "S7_S11_reclassified": {
                "label": "TESTABLE BUT INSUFFICIENT EVIDENCE (per the Constitution's own rule: non-significance alone is not active disproof)",
                "S7": "Positive point estimate (bear net$=+144, edge_brut +0.31/+0.25) but non-significant (p=0.277-0.455). MANDATORY fragility flag: bear cell's best_over_sumR=13.59 (new filter) -- a SINGLE trade equals 13.6x the entire net sum; removing it flips the cell strongly negative (wo1_netR=-39). The apparent positive signal is a demonstrated single-trade artifact, not a repeatable phenomenon. Other S7 regimes (bull, correction) are net-negative in both filters.",
                "S11": "Bull cell positive (net$=+255, edge_brut +0.31/+0.17) but non-significant (p=0.364-0.915); other regimes net-negative. No concentration flag raised (not verified as single-trade-dominated), but not confirmed robust either.",
                "S2_S3_S13": "Net-negative in all 3 regimes, both filters, no qualifying cell -- no live question, classified TESTABLE BUT INSUFFICIENT EVIDENCE by absence of signal, not by active disproof.",
            },
            "S16_S17_NOT_TESTABLE": {
                "reason": "block_bootstrap@v1 is validated STRICTLY for L>=H=20 (Mandate 3.20). S16 (H=92) and S17 (H=460) both ran at the SAME L=28 inherited mechanically from the Group-A Open-R contract -- at these horizons L=28<H, the exact condition (block shorter than the true dependency window) that invalidated the AR(1) regime at Mandate 3.17. block_bootstrap@v1 does not cover this configuration.",
                "consequence": "Every p_wp5 reported for S16/S17 in this run is UNVALIDATED and UNUSABLE for any conclusion -- explicitly including S17's deceptively low figures (bear-new p=0.0265, correction-new p=0.0190). A low p-value from an uncalibrated estimator is not evidence; flagged as a trap, not a finding.",
                "additional_S17_correction_issue": "n=27 at the old filter, below the nt>L=28 requirement -- p correctly returned None (a refusal to run underpowered, not a bug).",
                "recalibration_decision": "NOT commissioned in this document -- a proper WP-5' recalibration at L>=92/L>=460 is a validation effort of similar scope to the original (new null generator sized to the true mechanism, dedicated FPR battery, pre-registered acceptance band), a new VE task, not a relabeling. S16/S17 remain NOT TESTABLE (oracle-uncalibrated) until such a recalibration is separately commissioned and executed.",
            },
            "multiple_testing_family_fixed": {
                "family_size": 8,
                "convention": "Matches SMC_S1's OWN established precedent (Mandate 3.20 success_failure_criteria_preregistered: 'pooled counts across ELIGIBLE regimes', family of 1) -- extended for consistency to all 8 families now tested together in one pass (task2_cost_rerun.py): ONE pooled test per family across its 3 regimes, not 24 independent per-cell tests.",
                "pooled_test_status": "NOT YET COMPUTED by VE for S2/S3/S7/S11/S13/S16/S17 -- required before final (non-interim) verdicts on S7/S11 specifically. SMC_S1 does not need it to close: all 3 regimes are independently negative AND overwhelmingly non-significant, so pooling cannot manufacture a positive result from three individually strongly-non-positive ones.",
                "qualitative_BH_check": "At alpha=0.05/8=0.00625 (strictest BH rank), no available per-cell p (best case 0.0190, itself invalid per S16_S17_NOT_TESTABLE) would clear the bar -- consistent with, though not a substitute for, the required pooled test.",
            },
            "full_resolution_document": "ai_quant_lab statistician/STATISTICIAN_MITREJ_CIRCULARITY_COST_VERDICTS_HYPOTHESIS_v1.0.md",
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
