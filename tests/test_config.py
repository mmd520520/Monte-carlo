import math

import pytest

from mcsim import load_preset
from mcsim.config import list_presets


def test_presets_listed():
    assert {"skin_500nm", "knee_980nm"} <= set(list_presets())


def test_skin_units_and_scattering():
    p = load_preset("skin_500nm")
    blood = p.tissue(3)
    assert blood.mua == pytest.approx(11.20)            # already 1/mm
    assert blood.mus == pytest.approx(1.00 / (1 - 0.9))  # mus = musp / (1 - g)
    assert p.geometry["voxel"] == pytest.approx(0.010)
    assert p.source.diameter == pytest.approx(1.0)


def test_knee_converted_from_cm_to_mm():
    p = load_preset("knee_980nm")
    soft = p.tissue(2)
    assert soft.mua == pytest.approx(0.060)               # 0.60 /cm -> 0.060 /mm
    assert soft.mus == pytest.approx(6.10 / 0.1 / 10)     # musp 6.10 /cm, g 0.9 -> 6.1 /mm
    assert p.geometry["voxel"] == pytest.approx(1.25)
    assert p.geometry["outer_contour"][0] == pytest.approx([-30.0, 65.0])
    assert p.source.diameter == pytest.approx(80.0)
    assert p.source.power_w == pytest.approx(20.0)        # power is not a length


def test_overrides():
    p = load_preset("skin_500nm", photons=123, seed=9, stride=4, theta_deg=30.0)
    assert (p.run.photons, p.run.seed, p.geometry["stride"], p.source.theta_deg) == (123, 9, 4, 30.0)
    with pytest.raises(KeyError):
        load_preset("skin_500nm", nonsense=1)


def test_validation_rejects_bad_angle():
    with pytest.raises(ValueError):
        load_preset("skin_500nm", theta_deg=95.0)
