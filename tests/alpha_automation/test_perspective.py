from alpha_automation.perspective import PerspectiveGenerator
from alpha_automation import schemas


def test_perspective_is_deterministic():
    g1 = PerspectiveGenerator(20260721)
    g2 = PerspectiveGenerator(20260721)
    for p in range(20):
        assert g1.generate(p) == g2.generate(p)


def test_perspective_is_schema_valid():
    g = PerspectiveGenerator(1)
    schema = schemas.load_schema("perspective")
    for p in range(30):
        assert schemas.is_valid(g.generate(p), schema)


def test_consecutive_perspectives_vary_the_whole_stance():
    # Rotation must not converge: consecutive passes should differ on the lens.
    g = PerspectiveGenerator(42)
    lenses = [g.generate(p)["lens"] for p in range(9)]
    # walking stride 1 over 9 lenses -> all 9 distinct across a cycle
    assert len(set(lenses)) == 9


def test_avoids_recent_stances():
    g = PerspectiveGenerator(99)
    p0 = g.generate(0)
    recent = [(p0["lens"], p0["analytical_style"], p0["framing"])]
    # Ask for a perspective that would (in raw rotation) collide, forcing avoidance.
    # Generating pass 0 again but telling it p0 is recent must change lens or framing.
    p0b = g.generate(0, recent_stances=recent)
    assert not (p0b["lens"] == p0["lens"] and p0b["framing"] == p0["framing"])


def test_different_seeds_explore_different_phases():
    a = [PerspectiveGenerator(1).generate(p) for p in range(10)]
    b = [PerspectiveGenerator(2).generate(p) for p in range(10)]
    # Seed-derived per-axis offsets should make the two runs explore the space differently.
    assert a != b
