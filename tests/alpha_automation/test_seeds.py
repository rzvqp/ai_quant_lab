from alpha_automation import seeds


def test_pass_seed_is_deterministic_and_positive():
    a = seeds.pass_seed(20260721, 0)
    b = seeds.pass_seed(20260721, 0)
    assert a == b
    assert 0 <= a < (1 << 63)


def test_different_passes_give_different_seeds():
    s = [seeds.pass_seed(1, i) for i in range(50)]
    assert len(set(s)) == 50  # no collisions across a run


def test_different_master_seeds_diverge():
    assert seeds.pass_seed(1, 5) != seeds.pass_seed(2, 5)


def test_sub_seed_labels_are_independent():
    a = seeds.sub_seed(7, 3, "task")
    b = seeds.sub_seed(7, 3, "window")
    assert a != b
    assert seeds.sub_seed(7, 3, "task") == a  # stable


def test_rng_is_reproducible():
    r1 = seeds.rng_labelled(7, 3, "x")
    r2 = seeds.rng_labelled(7, 3, "x")
    assert [r1.random() for _ in range(5)] == [r2.random() for _ in range(5)]
