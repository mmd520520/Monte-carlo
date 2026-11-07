"""Light source set-up: oblique incidence, Snell refraction and specular loss.

Port of legacy/matlab/*/Configure_ObliqueSource.m and Light_T.m.
- Skin mode (launch_from_air = False): photons start just below the surface,
  already refracted, with weight 1 - R_specular (unpolarised Fresnel).
- Knee mode (launch_from_air = True): photons start in the air at emission_z
  with weight 1; reflection/refraction happen at the actual voxel faces.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from mcsim.config import SourceConfig
from mcsim.geometry import Volume
from mcsim.optics import OpticsTable

LAUNCH_EPS_MM = 1e-9


@dataclass
class Beam:
    x: float
    y: float
    radius: float
    start_z: float  # z of the sampled start point (surface or emission plane)
    launch_z: float  # z the photon is moved to along its direction before tracking
    ux: float
    uy: float
    uz: float
    u_air: tuple[float, float, float]
    w0: float
    specular: float
    theta_tissue_deg: float
    launch_from_air: bool


def fresnel_unpolarised(n1: float, n2: float, cos_i: float) -> tuple[float, float]:
    """Return (R, cos_t). R = 1 for total internal reflection."""
    sin_t2 = (n1 / n2) ** 2 * max(0.0, 1 - cos_i**2)
    if sin_t2 >= 1:
        return 1.0, 0.0
    ct = math.sqrt(1 - sin_t2)
    rs = ((n1 * cos_i - n2 * ct) / (n1 * cos_i + n2 * ct)) ** 2
    rp = ((n2 * cos_i - n1 * ct) / (n2 * cos_i + n1 * ct)) ** 2
    return (rs + rp) / 2, ct


def configure_beam(src: SourceConfig, optics: OpticsTable, volume: Volume) -> Beam:
    theta = math.radians(src.theta_deg)
    phi = math.radians(src.phi_deg)
    n1 = float(optics.n[1])
    n2 = float(optics.n[src.entry_label])
    u_air = (math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta))

    nx, ny, _ = volume.shape
    if src.radius + abs(src.x) >= nx * volume.voxel[0] / 2 or src.radius + abs(src.y) >= ny * volume.voxel[1] / 2:
        raise ValueError("beam does not fit inside the grid (radius + offset >= half width)")

    if src.launch_from_air:
        return Beam(
            x=src.x, y=src.y, radius=src.radius,
            start_z=src.emission_z, launch_z=src.emission_z + LAUNCH_EPS_MM,
            ux=u_air[0], uy=u_air[1], uz=u_air[2], u_air=u_air,
            w0=1.0, specular=0.0, theta_tissue_deg=float("nan"), launch_from_air=True,
        )

    sin_t = n1 / n2 * math.sin(theta)
    if sin_t >= 1:
        raise ValueError("total internal reflection at the entry surface")
    theta_t = math.asin(sin_t)
    r, _ = fresnel_unpolarised(n1, n2, math.cos(theta))
    return Beam(
        x=src.x, y=src.y, radius=src.radius,
        start_z=volume.surface_z, launch_z=volume.surface_z + LAUNCH_EPS_MM,
        ux=math.sin(theta_t) * math.cos(phi), uy=math.sin(theta_t) * math.sin(phi), uz=math.cos(theta_t),
        u_air=u_air, w0=1 - r, specular=r, theta_tissue_deg=math.degrees(theta_t), launch_from_air=False,
    )
