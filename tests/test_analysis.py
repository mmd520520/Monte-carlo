import numpy as np
import pytest

from mcsim import simulate
from mcsim.analysis import axis_profile, dose_table, skin_surface_on_axis


@pytest.fixture(scope="module")
def knee_result():
    from mcsim import load_preset
    return simulate(load_preset("knee_980nm", photons=20000, stride=2, batch_size=2000), workers=0)


def test_skin_surface_on_axis_is_a_voxel_face(knee_result):
    v = knee_result.volume
    z = skin_surface_on_axis(v)
    assert z == pytest.approx(round(z / v.voxel[2]) * v.voxel[2])
    assert 35 < z < 50  # mm; nominal knee contact depth is 40 mm


def test_dose_definitions(knee_result):
    rows = dose_table(knee_result, depths_mm=[10, 20], exposure_s=300, disk_radius_mm=10)
    r = rows[0]
    assert r.axis_H_j_cm2 == pytest.approx(r.axis_rate_w_cm2 * 300)
    area_cm2 = np.pi * 1.0**2
    assert r.disk_energy_j == pytest.approx(r.disk_mean_H_j_cm2 * area_cm2)
    assert r.disk_energy_fraction == pytest.approx(r.disk_energy_j / (20 * 300))
    assert rows[1].disk_mean_H_j_cm2 < rows[0].disk_mean_H_j_cm2  # less light deeper


def test_dose_needs_power_for_skin():
    from mcsim import load_preset
    r = simulate(load_preset("skin_500nm", photons=500, stride=10, batch_size=500))
    with pytest.raises(ValueError):
        dose_table(r, [0.5], 60, 0.2)
    rows = dose_table(r, [0.5], 60, 0.2, power_w=0.1)
    assert rows[0].axis_H_j_cm2 > 0


def test_axis_profile_starts_below_skin(knee_result):
    depth, phi = axis_profile(knee_result)
    assert depth[0] > 0 and np.all(np.diff(depth) > 0)
    assert np.all(np.isfinite(phi))


def test_disk_outside_grid_rejected(knee_result):
    with pytest.raises(ValueError):
        dose_table(knee_result, [10], 300, disk_radius_mm=500)
