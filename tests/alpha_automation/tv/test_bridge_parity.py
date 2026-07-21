"""The Node bridge dispatch table and the Python capability registry must not drift apart."""
import pathlib
import re

from alpha_automation.tv import capabilities as caps

BRIDGE = pathlib.Path(caps.__file__).resolve().parent / "bridge" / "tv_exec.mjs"


def _bridge_verbs():
    text = BRIDGE.read_text(encoding="utf-8")
    block = text.split("const DISPATCH = {", 1)[1]
    # take up to the line that closes the dispatch object
    block = block.split("\n  };", 1)[0]
    return set(re.findall(r"^\s*([a-z_]+):", block, flags=re.MULTILINE))


def test_bridge_verbs_match_capability_registry():
    bridge = _bridge_verbs()
    known = set(caps.VERB_CLASS) | {"health"}
    # Every bridge verb must be a known capability (or health). No stray/undeclared verbs.
    assert bridge - known == set(), f"bridge has undeclared verbs: {bridge - known}"


def test_bridge_has_no_prohibited_verbs():
    bridge = _bridge_verbs()
    assert bridge & caps.DENY_VERBS == set(), "bridge must not dispatch prohibited verbs"
