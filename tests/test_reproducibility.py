import numpy as np

from mcsim import simulate


def test_same_seed_same_result(skin_smoke):
    a = simulate(skin_smoke, workers=1)
    b = simulate(skin_smoke, workers=1)
    assert np.array_equal(a.A, b.A) and a.energy == b.energy


def test_serial_and_parallel_are_bit_identical(skin_smoke):
    a = simulate(skin_smoke, workers=1)
    b = simulate(skin_smoke, workers=4)
    assert b.workers > 1
    assert np.array_equal(a.A, b.A) and np.array_equal(a.R2, b.R2) and a.energy == b.energy


def test_different_seed_differs(skin_smoke):
    a = simulate(skin_smoke)
    skin_smoke.run.seed = 2
    b = simulate(skin_smoke)
    assert not np.array_equal(a.A, b.A)
