"""Voxel volumes. Each builder returns a :class:`Volume` in mm.

Coordinate frame (same as the MATLAB code): x and y are centred on the beam axis,
z points into the tissue and starts at 0 on the top face of the grid. Voxel
(i, j, k) spans x in [i*dx - nx*dx/2, (i+1)*dx - nx*dx/2], and so on.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

AIR = 1


@dataclass
class Volume:
    labels: np.ndarray  # uint8, shape (nx, ny, nz)
    voxel: tuple[float, float, float]  # mm
    surface_z: float  # nominal skin surface depth, mm

    @property
    def shape(self) -> tuple[int, int, int]:
        return tuple(int(s) for s in self.labels.shape)  # type: ignore[return-value]

    @property
    def offset(self) -> np.ndarray:
        nx, ny, _ = self.shape
        dx, dy, _ = self.voxel
        return np.array([nx * dx / 2.0, ny * dy / 2.0, 0.0])

    @property
    def voxel_volume(self) -> float:
        return float(np.prod(self.voxel))

    @property
    def voxel_area(self) -> float:
        return float(self.voxel[0] * self.voxel[1])

    def centers(self, axis: int) -> np.ndarray:
        n = self.shape[axis]
        d = self.voxel[axis]
        return (np.arange(n) + 0.5) * d - self.offset[axis]

    @property
    def air_layers(self) -> int:
        """Number of whole voxel layers above the nominal surface (MATLAB airLayerCount)."""
        return int(matlab_round(self.surface_z / self.voxel[2]))


def matlab_round(x):
    """MATLAB round(): halves go away from zero (Python's round() goes to even)."""
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def subsample(labels: np.ndarray, stride: int) -> np.ndarray:
    """MATLAB T(s:s:end, s:s:end, s:s:end): keep every stride-th voxel, starting at the stride-th."""
    if stride == 1:
        return labels
    s = stride
    return np.ascontiguousarray(labels[s - 1 :: s, s - 1 :: s, s - 1 :: s])


def build_volume(geometry: dict) -> Volume:
    kind = geometry["type"]
    if kind == "skin":
        from mcsim.geometry.skin import build_skin

        return build_skin(geometry)
    if kind == "knee":
        from mcsim.geometry.knee import build_knee

        return build_knee(geometry)
    if kind == "slab":
        from mcsim.geometry.slab import build_slab

        return build_slab(geometry)
    raise ValueError(f"unknown geometry type: {kind}")
