import math

import pytest

from mcsim import simulate
from mcsim.config import SourceConfig
from mcsim.geometry import build_volume
from mcsim.optics import OpticsTable
from mcsim.source import configure_beam, fresnel_unpolarised


@pytest.mark.parametrize("launch_from_air", [False, True])
def test_beer_lambert_without_scattering(make_slab, launch_from_air):
    """No scattering, matched index: every packet goes straight down, T = exp(-mua * d)."""
    mua, d = 0.7, 2.0
    r = simulate(make_slab(mua=mua, mus=0.0, thickness=d, launch_from_air=launch_from_air, photons=500))
    assert r.energy["transmitted"] == pytest.approx(math.exp(-mua * d), abs=1e-8)
    assert r.energy["reflected"] == 0.0 and r.energy["side"] == 0.0


def test_no_absorption_means_nothing_absorbed(make_slab):
    r = simulate(make_slab(mua=0.0, mus=5.0, g=0.8, n_medium=1.4, thickness=1.0, photons=2000))
    assert r.energy["absorbed"] == 0.0
    assert r.energy["roulette_correction"] == 0.0  # weights never drop below the roulette threshold
    total = r.energy["reflected"] + r.energy["transmitted"] + r.energy["side"] + r.energy["specular"]
    assert total == pytest.approx(1.0, abs=1e-12)


def test_matched_index_has_no_specular_loss(make_slab):
    p = make_slab(mua=0.1, mus=1.0, n_medium=1.0, n_air=1.0)
    v = build_volume(p.geometry)
    beam = configure_beam(p.source, OpticsTable.from_tissues(p.tissues), v)
    assert beam.specular == 0.0 and beam.w0 == 1.0


def test_fresnel_known_values():
    assert fresnel_unpolarised(1.0, 1.4, 1.0)[0] == pytest.approx((0.4 / 2.4) ** 2)
    assert fresnel_unpolarised(1.4, 1.0, math.cos(math.radians(60)))[0] == 1.0  # beyond critical angle (45.6 deg)


def test_specular_reflection_on_top_face_in_air_mode(make_slab):
    """Knee mode, no scattering, n mismatch: the fraction reflected at the surface matches Fresnel."""
    n = 1.4
    r = simulate(make_slab(mua=0.0, mus=0.0, n_medium=n, launch_from_air=True, photons=20000))
    expected = ((n - 1) / (n + 1)) ** 2
    assert r.energy["reflected"] == pytest.approx(expected, abs=4 * math.sqrt(expected * (1 - expected) / 20000))
