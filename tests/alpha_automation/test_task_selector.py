from alpha_automation.perspective import PerspectiveGenerator
from alpha_automation.task_selector import ResearchTaskSelector, normalize_question
from alpha_automation import schemas


def _persp(seed=7, p=0):
    return PerspectiveGenerator(seed).generate(p)


def test_task_is_deterministic_under_fixed_seed():
    persp = _persp()
    s1 = ResearchTaskSelector(7)
    s2 = ResearchTaskSelector(7)
    t1 = s1.select(persp, 0, asked_norms=[], task_id="INV-000001")
    t2 = s2.select(persp, 0, asked_norms=[], task_id="INV-000001")
    assert t1 == t2


def test_task_is_schema_valid():
    schema = schemas.load_schema("research_task")
    sel = ResearchTaskSelector(3)
    for p in range(15):
        persp = _persp(3, p)
        t = sel.select(persp, p, asked_norms=[], task_id=f"INV-{p:06d}")
        assert schemas.is_valid(t, schema)


def test_avoids_reasking_the_same_question():
    persp = _persp(11, 0)
    sel = ResearchTaskSelector(11)
    first = sel.select(persp, 0, asked_norms=[], task_id="INV-000001")
    # Now tell the selector that question was already asked; it must pick a different one.
    second = sel.select(persp, 0, asked_norms=[first["question_norm"]], task_id="INV-000002")
    assert second["question_norm"] != first["question_norm"]


def test_selection_reason_present():
    persp = _persp()
    t = ResearchTaskSelector(7).select(persp, 0, asked_norms=[], task_id="INV-000001")
    assert t["selection_reason"]
    assert t["window_hint"]["prefer_regime"] == persp["regime_bias"]


def test_normalize_question_collapses_variants():
    a = normalize_question("During the NY session, does price behave differently?")
    b = normalize_question("during   the ny session  does price behave differently")
    assert a == b
