import copy
import json
import sys
from pathlib import Path

import pytest

VE_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
for _p in (VE_ROOT, TESTS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

FIXTURES = Path(__file__).resolve().parent / "fixtures"
BASELINE_PATH = FIXTURES / "fixture_baseline_spec.json"
REFERENCE_PATH = FIXTURES / "reference_spec_dc0004.json"


@pytest.fixture(scope="session")
def baseline_raw() -> dict:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def baseline(baseline_raw) -> dict:
    """Copie proaspătă a specificației minimale, pentru mutații."""
    return copy.deepcopy(baseline_raw)


@pytest.fixture(scope="session")
def reference_raw() -> dict:
    """Specificația de referință: transcrierea unui design real (DC-0004)."""
    return json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def reference(reference_raw) -> dict:
    return copy.deepcopy(reference_raw)
