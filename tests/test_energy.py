import pytest

from mcsim import simulate
from mcsim.results import ENERGY_TOLERANCE


def test_skin_energy_bookkeeping(skin_smoke):
    r = simulate(skin_smoke)
    assert abs(r.energy["bookkeeping"] - 1) < ENERGY_TOLERANCE
    assert r.energy["specular"] == pytest.approx(((1 - 1.4) / (1 + 1.4)) ** 2)
    assert 0 < r.energy["absorbed"] < 1


def test_skin_oblique_energy_bookkeeping(skin_smoke):
    skin_smoke.source.theta_deg = 45.0
    r = simulate(skin_smoke)
    assert abs(r.energy["bookkeeping"] - 1) < ENERGY_TOLERANCE
    assert r.energy["specular"] > 0.0278  # oblique incidence reflects more


def test_knee_energy_bookkeeping(knee_coarse):
    r = simulate(knee_coarse)
    assert abs(r.energy["bookkeeping"] - 1) < ENERGY_TOLERANCE
    assert r.energy["specular"] == 0.0  # knee mode: reflection happens at the voxel faces
    assert r.energy["absorbed"] > 0.5
