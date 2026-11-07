"""Skin with one blood vessel: air / epidermis / dermis + a cylinder along y.

Reproduces legacy/matlab/2demo/Tissue.m exactly, including its coordinate
conventions (x at the voxel's +x edge, z at the voxel's deep edge) so that the
voxel labels match the MATLAB model one for one.
Labels: 1 air, 3 blood, 4 dermis, 5 epidermis (2 is unused, as in MATLAB).
"""

from __future__ import annotations

import numpy as np

from mcsim.geometry import Volume, matlab_round, subsample

AIR, BLOOD, DERMIS, EPIDERMIS = 1, 3, 4, 5


def build_skin(g: dict) -> Volume:
    nx, ny, nz = (int(v) for v in g["shape"])
    d = float(g["voxel"])
    zsurf = float(g["surface_z"])
    epi = float(g["epidermis_thickness"])
    vessel = g.get("vessel") or {}
    xc = float(vessel.get("x", 0.0))
    zc = vessel.get("z")
    zc = nz / 2 * d if zc is None else float(zc)
    r = float(vessel.get("radius", 0.0))

    ix = np.arange(1, nx + 1)
    iz = np.arange(1, nz + 1)
    x = (ix - nx / 2) * d
    z = iz * d

    labels = np.full((nx, ny, nz), DERMIS, dtype=np.uint8)
    air_n = matlab_round(zsurf / d)
    epi_n = matlab_round((zsurf + epi) / d)
    labels[:, :, iz <= air_n] = AIR
    labels[:, :, (iz > air_n) & (iz <= epi_n)] = EPIDERMIS
    if r > 0:
        in_vessel = np.hypot(x[:, None] - xc, z[None, :] - zc) <= r  # (nx, nz)
        labels[np.broadcast_to(in_vessel[:, None, :], labels.shape)] = BLOOD

    stride = int(g.get("stride", 1))
    labels = subsample(labels, stride)
    return Volume(labels=labels, voxel=(d * stride,) * 3, surface_z=zsurf)
