"""F3 — infrastructura de audit: manifest, checksums, ledger, integritate, verify.

Toate rulările folosesc directoare temporare (runs_dir, ledger în tmp_path) și
timestamp/run_id injectate — deci deterministe și fără a atinge arborele real VE.
"""

import json
from pathlib import Path

import pytest

from ve import paths
from ve.audit import checksums, ledger, repo_integrity
from ve.rng import streams
from ve.run.runner import audit_run
from ve.verify.replay import verify_bundle

FIX = paths.VE_ROOT / "tests" / "fixtures"


@pytest.fixture
def env(tmp_path):
    return {
        "runs_dir": tmp_path / "runs",
        "ledger_jsonl": tmp_path / "run_ledger.jsonl",
        "ledger_md": tmp_path / "RUN_LEDGER.md",
    }


def _run(env, spec="reference_spec_dc0004.json", rid="VE-RUN-T-0001"):
    return audit_run(FIX / spec, run_id=rid, timestamp="2026-07-25T00:00:00Z", **env)


# ───────────────────────── criteriile de acceptare F3 ─────────────────────────

def test_audit_run_produces_a_complete_manifest(env):
    r = _run(env)
    man = json.loads((r.bundle_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    for field in ("run_id", "engine_version", "status", "code", "spec", "data",
                  "execution", "environment", "repo_integrity", "replay_command"):
        assert field in man, field
    assert man["execution"]["methods_executed"] == 0


def test_audit_run_touches_no_data(env):
    r = _run(env)
    assert r.data_accesses == []
    man = json.loads((r.bundle_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    assert man["data"]["data_accesses"] == 0
    assert man["data"]["sealed_resources_touched"] == []


def test_audit_run_external_writes_zero(env):
    """Bundle scris în tmp → arborele real VE rămâne byte-identic."""
    before = repo_integrity.digest_of(repo_integrity.snapshot())
    r = _run(env)
    after = repo_integrity.digest_of(repo_integrity.snapshot())
    assert before == after
    assert r.external_writes == 0


def test_halted_spec_still_produces_a_bundle(env):
    """O rulare oprită pe calibrare produce tot un manifest complet."""
    r = _run(env)
    assert r.status == "HALTED"          # DC-0004 se oprește pe poarta de calibrare
    assert (r.bundle_dir / "MANIFEST.json").exists()
    val = json.loads((r.bundle_dir / "VALIDATION.json").read_text(encoding="utf-8"))
    assert set(val["codes"]) == {"E3"}


def test_pre_manifest_written_before_manifest(env):
    r = _run(env)
    assert (r.bundle_dir / "PRE_MANIFEST.json").exists()
    pre = json.loads((r.bundle_dir / "PRE_MANIFEST.json").read_text(encoding="utf-8"))
    assert "NU execută" in pre["note"] and "NU atinge date" in pre["note"]


def test_spec_received_is_bit_identical(env):
    r = _run(env)
    received = json.loads((r.bundle_dir / "SPEC_RECEIVED.json").read_text(encoding="utf-8"))
    original = json.loads((FIX / "reference_spec_dc0004.json").read_text(encoding="utf-8"))
    assert received == original


# ───────────────────────────── verify ─────────────────────────────────────────

def test_verify_exact_on_intact_bundle(env):
    r = _run(env)
    rep = verify_bundle(r.bundle_dir)
    assert rep["status"] == "EXACT"
    assert rep["external_writes"] == 0


def test_verify_detects_single_bit_alteration(env):
    r = _run(env)
    mp = r.bundle_dir / "MANIFEST.json"
    mp.write_text(mp.read_text(encoding="utf-8").replace("F3-audit", "TAMPER", 1), encoding="utf-8")
    rep = verify_bundle(r.bundle_dir)
    assert rep["status"] == "MISMATCH"
    assert any(m["issue"] == "altered" for m in rep["checksums"]["mismatches"])


def test_verify_detects_added_file(env):
    r = _run(env)
    (r.bundle_dir / "sneaked.txt").write_text("x", encoding="utf-8")
    rep = verify_bundle(r.bundle_dir)
    assert rep["status"] == "MISMATCH"
    assert any(m["issue"] == "unexpected" for m in rep["checksums"]["mismatches"])


def test_verify_detects_removed_file(env):
    r = _run(env)
    (r.bundle_dir / "environment.json").unlink()
    rep = verify_bundle(r.bundle_dir)
    assert rep["status"] == "MISMATCH"


# ───────────────────────────── ledger ─────────────────────────────────────────

def test_ledger_is_append_only(env):
    _run(env, rid="VE-RUN-T-0001")
    _run(env, rid="VE-RUN-T-0002")
    entries = ledger.read_all(env["ledger_jsonl"])
    assert len(entries) == 2
    assert [e["run_id"] for e in entries] == ["VE-RUN-T-0001", "VE-RUN-T-0002"]
    for e in entries:
        assert e["data_accesses"] == 0
        assert e["external_writes"] == 0


def test_ledger_records_every_run_including_halted(env):
    _run(env)
    entries = ledger.read_all(env["ledger_jsonl"])
    assert entries[0]["status"] == "HALTED"


# ───────────────────────── bundle write-once ──────────────────────────────────

def test_bundle_is_write_once(env):
    _run(env, rid="VE-RUN-DUP")
    with pytest.raises(FileExistsError):
        _run(env, rid="VE-RUN-DUP")   # același run_id + candidat → nu suprascrie


# ───────────────────────── determinism al conținutului ────────────────────────

def test_seed_derivation_is_deterministic():
    a = streams.derive_seeds("a" * 64, ["T1", "T2"])
    b = streams.derive_seeds("a" * 64, ["T1", "T2"])
    assert a == b
    assert a["streams"]["T1"] != a["streams"]["T2"]
    assert streams.derive_seeds("b" * 64, ["T1"])["root_seed"] != a["root_seed"]


def test_checksums_reproducible(env):
    r = _run(env)
    h1 = checksums.bundle_sha256(r.bundle_dir)
    h2 = checksums.bundle_sha256(r.bundle_dir)
    assert h1 == h2 and len(h1) == 64


# ───────────────── domeniul F3 nu atinge invarianții F2 ────────────────────────

def test_f3_leaves_registry_unexecutable(env):
    from ve.spec import registry_validator
    _run(env)
    reg = registry_validator.load_registry()
    # Statusul e stabilit de CEO (PARTIALLY_EXECUTABLE din 2026-07-25); F3 nu îl modifică.
    assert reg["status"] == "PARTIALLY_EXECUTABLE"
    # F3 nu modifică niciun status de calibrare: matched_null@v1 rămâne VALIDATED (CEO), restul UNVALIDATED.
    for s in ("test_methods", "correction_methods"):
        for mid, m in reg[s].items():
            expected = "VALIDATED" if mid == "matched_null@v1" else "UNVALIDATED"
            assert m["calibration_status"] == expected, mid
