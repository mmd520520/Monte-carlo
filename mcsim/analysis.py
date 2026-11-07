"""Dose analysis below the skin (port of the analysis blocks in legacy/matlab/5demo/main.m).

Definitions, same as MATLAB:
- skin surface on the axis: top face of the first non-air voxel in the column
  nearest x = y = 0;
- fluence rate (W/cm^2) = phi * power, linearly interpolated at voxel centres;
- accumulated fluence H (J/cm^2) = fluence rate * exposure time
  (this is radiant exposure, NOT absorbed energy density);
- disk mean: mean H over voxel-centre samples within a centred disk;
- disk energy (J) = mean fluence rate * time * disk area, also given as a fraction
  of the delivered energy power * time.
All inputs here are in mm; outputs are in cm-based units (W/cm^2, J/cm^2, J).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy.interpolate import RegularGridInterpolator

from mcsim.geometry import AIR, Volume
from mcsim.results import SimulationResult


def skin_surface_on_axis(volume: Volume) -> float:
    """z (mm) of the skin surface on the beam axis."""
    xc, yc, zc = (volume.centers(a) for a in range(3))
    i, j = int(np.argmin(np.abs(xc))), int(np.argmin(np.abs(yc)))
    column = volume.labels[i, j, :] > AIR
    if not column.any():
        raise ValueError("no tissue on the beam axis")
    k = int(np.argmax(column))
    return float(zc[k] - volume.voxel[2] / 2)


def _interpolators(result: SimulationResult, power_w: float):
    v = result.volume
    axes = tuple(v.centers(a) for a in range(3))
    field = np.nan_to_num(result.phi) * power_w * 100.0  # W/cm^2
    rate = RegularGridInterpolator(axes, field, method="linear", bounds_error=True)
    label = RegularGridInterpolator(axes, v.labels.astype(float), method="nearest", bounds_error=True)
    return rate, label


@dataclass
class DoseRow:
    depth_mm: float
    z_mm: float
    axis_rate_w_cm2: float
    axis_H_j_cm2: float
    disk_mean_H_j_cm2: float
    disk_energy_j: float
    disk_energy_fraction: float
    disk_has_air: bool

    def as_dict(self) -> dict:
        return asdict(self)


def dose_table(
    result: SimulationResult,
    depths_mm: list[float],
    exposure_s: float,
    disk_radius_mm: float,
    power_w: float | None = None,
) -> list[DoseRow]:
    power = power_w if power_w is not None else result.power_w
    if power is None:
        raise ValueError("give power_w: this preset has no beam power")
    v = result.volume
    xc, yc, zc = (v.centers(a) for a in range(3))
    if disk_radius_mm > min(-xc.min(), xc.max(), -yc.min(), yc.max()):
        raise ValueError("disk extends beyond the interpolation range in x-y")
    skin = skin_surface_on_axis(v)
    rate, label = _interpolators(result, power)

    X, Y = np.meshgrid(xc, yc, indexing="ij")
    in_disk = X**2 + Y**2 <= disk_radius_mm**2
    if not in_disk.any():
        raise ValueError("disk too small: no voxel centre inside")
    xq, yq = X[in_disk], Y[in_disk]
    area_cm2 = np.pi * (disk_radius_mm / 10.0) ** 2

    rows = []
    for d in depths_mm:
        z = skin + d
        if not (zc.min() <= z <= zc.max()):
            raise ValueError(f"depth {d} mm is outside the grid")
        axis_rate = float(rate([[0.0, 0.0, z]])[0])
        pts = np.column_stack([xq, yq, np.full(xq.shape, z)])
        disk_rate = rate(pts)
        mean_rate = float(disk_rate.mean())
        energy = mean_rate * exposure_s * area_cm2
        rows.append(DoseRow(
            depth_mm=float(d), z_mm=float(z),
            axis_rate_w_cm2=axis_rate, axis_H_j_cm2=axis_rate * exposure_s,
            disk_mean_H_j_cm2=mean_rate * exposure_s,
            disk_energy_j=energy, disk_energy_fraction=energy / (power * exposure_s),
            disk_has_air=bool(np.any(label(pts) == AIR)),
        ))
    return rows


def axis_profile(result: SimulationResult) -> tuple[np.ndarray, np.ndarray]:
    """Depth below the skin surface (mm) and fluence per unit power (1/mm^2) along the beam axis."""
    v = result.volume
    xc, yc, zc = (v.centers(a) for a in range(3))
    i, j = int(np.argmin(np.abs(xc))), int(np.argmin(np.abs(yc)))
    skin = skin_surface_on_axis(v)
    keep = zc > skin
    return zc[keep] - skin, result.phi[i, j, keep]
