import copy

import pytest

from mcsim import load_preset
from mcsim.config import Preset, RunConfig, SourceConfig, Tissue


@pytest.fixture
def skin_smoke():
    """MATLAB smokeTest grid: 40^3 voxels of 0.1 mm."""
    return load_preset("skin_500nm", photons=2000, stride=10, batch_size=500)


@pytest.fixture
def knee_coarse():
    return load_preset("knee_980nm", photons=2000, stride=4, batch_size=500)


def slab_preset(*, mua: float, mus: float, g: float = 0.0, n_medium: float = 1.0, n_air: float = 1.0,
                thickness: float = 1.0, launch_from_air: bool = False, photons: int = 2000,
                theta_deg: float = 0.0) -> Preset:
    """Air layer of 1 mm over a medium that runs to the bottom of the grid (0.1 mm voxels)."""
    nz = 10 + int(round(thickness / 0.1))
    return Preset(
        name="slab", title="slab",
        geometry={"type": "slab", "shape": [41, 41, nz], "voxel": 0.1, "surface_z": 1.0,
                  "thickness": thickness, "stride": 1},
        tissues=[Tissue(1, "air", 0.0, 0.0, 0.0, n_air), Tissue(2, "medium", mua, mus, g, n_medium)],
        source=SourceConfig(wavelength_nm=500, diameter=0.2, theta_deg=theta_deg,
                            launch_from_air=launch_from_air, emission_z=0.0, entry_label=2),
        run=RunConfig(photons=photons, seed=7, batch_size=500, workers=1),
    )


@pytest.fixture
def make_slab():
    return slab_preset
