"""Homogeneous slab under an air layer. Used by the physics-limit tests.

Labels: 1 air (z < surface_z), 2 medium (surface_z <= z < surface_z + thickness),
1 air again below the slab if the grid is deeper than the slab.
"""

from __future__ import annotations

import numpy as np

from mcsim.geometry import Volume, matlab_round


def build_slab(g: dict) -> Volume:
    nx, ny, nz = (int(v) for v in g["shape"])
    d = float(g["voxel"])
    zsurf = float(g["surface_z"])
    thick = float(g["thickness"])
    top = int(matlab_round(zsurf / d))
    bottom = int(matlab_round((zsurf + thick) / d))
    labels = np.ones((nx, ny, nz), dtype=np.uint8)
    labels[:, :, top:bottom] = 2
    return Volume(labels=labels, voxel=(d, d, d), surface_z=zsurf)
