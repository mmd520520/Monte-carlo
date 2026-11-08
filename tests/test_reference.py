"""Independent check without MATLAB: total reflection and transmission of a uniform slab.

Adding-doubling (Prahl, ``iadpython``) solves the same transport problem deterministically,
so a Monte Carlo result that agrees with it within statistical error confirms the physics
on its own. The slab is wide (41 mm) and thin, so it behaves like an infinite slab.
"""

import numpy as np
import pytest
import iadpython

from mcsim import simulate
from mcsim.config import Preset, RunConfig, SourceConfig, Tissue
from mcsim.geometry import Volume

PHOTONS = 200_000
DZ = 0.05  # mm; lateral voxels are 1 mm wide

# name, mua [1/mm], mus [1/mm], g, n, thickness [mm], launch_from_air
CASES = [
    ("tissue-like, index 1.4", 0.1, 10.0, 0.9, 1.4, 1.0, True),
    ("isotropic, thin, index 1.4", 1.0, 5.0, 0.0, 1.4, 0.5, True),
    ("epidermis-like, index 1.4", 2.0, 20.0, 0.9, 1.4, 0.2, True),
    ("index-matched, skin launch", 0.1, 10.0, 0.5, 1.0, 1.0, False),
]


def slab(mua, mus, g, n, d, launch_from_air):
    # Air mode: air above and below, Fresnel on both faces (adding-doubling n_above = n_below = 1).
    # Skin mode counts any step into air as reflection, so there the medium runs to the grid bottom
    # and only the index-matched case (n = 1) is comparable.
    top, layers = 2, int(round(d / DZ))
    labels = np.ones((41, 41, top + layers + (2 if launch_from_air else 0)), dtype=np.uint8)
    labels[:, :, top:top + layers] = 2
    volume = Volume(labels=labels, voxel=(1.0, 1.0, DZ), surface_z=top * DZ)
    preset = Preset(
        name="reference-slab", title="reference slab", geometry={"type": "custom"},
        tissues=[Tissue(1, "air", 0.0, 0.0, 0.0, 1.0), Tissue(2, "medium", mua, mus, g, n)],
        source=SourceConfig(wavelength_nm=500, diameter=0.2, launch_from_air=launch_from_air,
                            emission_z=0.0, entry_label=2),
        run=RunConfig(photons=PHOTONS, seed=11, batch_size=5000, workers=0),
    )
    return simulate(preset, volume=volume)


def adding_doubling(mua, mus, g, n, d):
    """(R, T, uncertainty): total reflection/transmission for normal incidence. The spread between
    16 and 32 quadrature points stands in for its own error (iadpython is unstable above ~48)."""
    out = [iadpython.Sample(a=mus / (mua + mus), b=(mua + mus) * d, g=g, d=d, n=n,
                            n_above=1.0, n_below=1.0, quad_pts=q).rt()[:2] for q in (16, 32)]
    (r16, t16), (r32, t32) = out
    return float(r32), float(t32), max(abs(r32 - r16), abs(t32 - t16))


@pytest.mark.parametrize("name, mua, mus, g, n, d, launch_from_air", CASES, ids=[c[0] for c in CASES])
def test_slab_matches_adding_doubling(name, mua, mus, g, n, d, launch_from_air):
    r = slab(mua, mus, g, n, d, launch_from_air)
    R_ref, T_ref, ref_err = adding_doubling(mua, mus, g, n, d)

    bs = r.batch_stats  # per-batch fractions -> standard error of the mean
    se = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x)))
    R_mc = r.energy["reflected"] + r.energy["specular"]
    T_mc = r.energy["transmitted"]

    assert r.energy["side"] < 1e-3, "slab not wide enough to act as infinite"
    for label, mc, ref, s in (("R", R_mc, R_ref, se(bs["reflected"])), ("T", T_mc, T_ref, se(bs["transmitted"]))):
        tol = 4.0 * np.hypot(s, ref_err)
        assert abs(mc - ref) <= tol, f"{name}: {label} Monte Carlo {mc:.4f} vs adding-doubling {ref:.4f} (tolerance {tol:.4f})"
