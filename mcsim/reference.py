"""Uniform-slab reference: adding-doubling (Prahl, ``iadpython``) and the matching Monte Carlo run.

Adding-doubling solves the same transport problem deterministically, so agreement within Monte Carlo
error confirms the physics without MATLAB. Used by ``tests/test_reference.py`` and the app's Validation page.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mcsim.config import Preset, RunConfig, SourceConfig, Tissue
from mcsim.geometry import Volume
from mcsim.runner import simulate

DZ = 0.05     # mm, voxel depth; the slab thickness is rounded to a whole number of voxels
WIDTH = 41    # lateral voxels of 1 mm: wide enough to act as an infinite slab


@dataclass
class SlabComparison:
    R_mc: float
    T_mc: float
    A_mc: float
    R_se: float
    T_se: float
    R_ad: float
    T_ad: float
    ad_err: float      # spread between 16 and 32 quadrature points
    side: float        # fraction lost through the sides; should be ~0
    elapsed_s: float

    @property
    def A_ad(self) -> float:
        return 1.0 - self.R_ad - self.T_ad

    def z(self, quantity: str) -> float:
        """(Monte Carlo − reference) / combined standard error, for "R", "T" or "A"."""
        mc, ad = {"R": (self.R_mc, self.R_ad), "T": (self.T_mc, self.T_ad), "A": (self.A_mc, self.A_ad)}[quantity]
        se = {"R": self.R_se, "T": self.T_se, "A": float(np.hypot(self.R_se, self.T_se))}[quantity]
        return (mc - ad) / float(np.hypot(se, self.ad_err))


def slab_run(mua: float, mus: float, g: float, n: float, d: float, launch_from_air: bool = True,
             photons: int = 200_000, seed: int = 11):
    """Monte Carlo of a uniform slab (coefficients 1/mm, thickness mm).

    Air mode: air above and below, Fresnel on both faces (adding-doubling n_above = n_below = 1).
    Skin mode counts any step into air as reflection, so there the medium runs to the grid bottom and
    only the index-matched case (n = 1) is comparable.
    """
    top, layers = 2, max(1, int(round(d / DZ)))
    labels = np.ones((WIDTH, WIDTH, top + layers + (2 if launch_from_air else 0)), dtype=np.uint8)
    labels[:, :, top:top + layers] = 2
    volume = Volume(labels=labels, voxel=(1.0, 1.0, DZ), surface_z=top * DZ)
    preset = Preset(
        name="reference-slab", title="reference slab", geometry={"type": "custom"},
        tissues=[Tissue(1, "air", 0.0, 0.0, 0.0, 1.0), Tissue(2, "medium", mua, mus, g, n)],
        source=SourceConfig(wavelength_nm=500, diameter=0.2, launch_from_air=launch_from_air,
                            emission_z=0.0, entry_label=2),
        run=RunConfig(photons=photons, seed=seed, batch_size=5000, workers=0),
    )
    return simulate(preset, volume=volume)


def adding_doubling(mua: float, mus: float, g: float, n: float, d: float) -> tuple[float, float, float]:
    """(R, T, error): total reflection/transmission for normal incidence. The spread between 16 and 32
    quadrature points stands in for its own error (iadpython is unstable above ~48)."""
    import iadpython

    out = [iadpython.Sample(a=mus / (mua + mus), b=(mua + mus) * d, g=g, d=d, n=n,
                            n_above=1.0, n_below=1.0, quad_pts=q).rt()[:2] for q in (16, 32)]
    (r16, t16), (r32, t32) = out
    return float(r32), float(t32), max(abs(r32 - r16), abs(t32 - t16))


def compare_slab(mua: float, mus: float, g: float, n: float, d: float, launch_from_air: bool = True,
                 photons: int = 200_000, seed: int = 11) -> SlabComparison:
    d = max(1, int(round(d / DZ))) * DZ  # the thickness the grid actually has
    r = slab_run(mua, mus, g, n, d, launch_from_air, photons, seed)
    R_ad, T_ad, err = adding_doubling(mua, mus, g, n, d)
    bs = r.batch_stats  # per-batch fractions -> standard error of the mean
    se = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else float("nan")
    R_mc = r.energy["reflected"] + r.energy["specular"]
    return SlabComparison(R_mc=R_mc, T_mc=r.energy["transmitted"], A_mc=r.energy["absorbed"],
                          R_se=se(bs["reflected"]), T_se=se(bs["transmitted"]),
                          R_ad=R_ad, T_ad=T_ad, ad_err=err, side=r.energy["side"], elapsed_s=r.elapsed_s)
