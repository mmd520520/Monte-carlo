"""Knee: air / soft tissue / patella / bone, built section by section along y.

Reproduces legacy/matlab/5demo/Tissue_knee.m: the outer and bone contours are
closed pchip curves through hand-traced points, the patella is a tilted ellipse,
and each y-section is the x-z outline shrunk towards a pivot by
s = sqrt(1 - (y / taper)^2). The anatomy is approximate (traced from an
annotated drawing, not CT/MRI). Labels: 1 air, 2 soft tissue, 3 patella, 4 bone.
"""

from __future__ import annotations

import numba
import numpy as np
from scipy.interpolate import PchipInterpolator

from mcsim.geometry import Volume, subsample

AIR, SOFT, PATELLA, BONE = 1, 2, 3, 4


def closed_pchip(points: np.ndarray, samples: int = 500) -> np.ndarray:
    """MATLAB: pp=[p(end-1:end,:);p;p(1:2,:)]; q=linspace(3,n+3,500); interp1(1:n+4,pp,q,'pchip')."""
    p = np.asarray(points, dtype=float)
    n = len(p)
    pp = np.vstack([p[-2:], p, p[:2]])
    t = np.arange(1, n + 5, dtype=float)
    q = np.linspace(3, n + 3, samples)
    return np.column_stack([PchipInterpolator(t, pp[:, 0])(q), PchipInterpolator(t, pp[:, 1])(q)])


@numba.njit(cache=True)
def _inside(px, pz, poly_x, poly_z):
    """Even-odd ray casting for a batch of points (MATLAB inpolygon, interior)."""
    out = np.zeros(px.shape[0], dtype=np.bool_)
    m = poly_x.shape[0]
    for k in range(px.shape[0]):
        x = px[k]
        z = pz[k]
        inside = False
        j = m - 1
        for i in range(m):
            zi = poly_z[i]
            zj = poly_z[j]
            if (zi > z) != (zj > z):
                xcross = poly_x[i] + (z - zi) * (poly_x[j] - poly_x[i]) / (zj - zi)
                if x < xcross:
                    inside = not inside
            j = i
        out[k] = inside
    return out


def build_knee(g: dict) -> Volume:
    nx, ny, nz = (int(v) for v in g["shape"])
    d = float(g["voxel"])
    x = (np.arange(1, nx + 1) - 0.5) * d - nx * d / 2
    y = (np.arange(1, ny + 1) - 0.5) * d - ny * d / 2
    z = (np.arange(1, nz + 1) - 0.5) * d
    X, Z = np.meshgrid(x, z, indexing="ij")
    Xf, Zf = X.ravel(), Z.ravel()

    outer = closed_pchip(np.array(g["outer_contour"]))
    bone = closed_pchip(np.array(g["bone_contour"]))
    pat = g["patella"]
    a = np.linspace(0, 2 * np.pi, 400)
    px0, pz0 = float(pat["x"]), float(pat["z"])
    patella = np.column_stack(
        [px0 + pat["half_length"] * np.cos(a), pz0 + pat["half_thickness"] * np.sin(a) + pat["tilt"] * np.cos(a)]
    )
    pivot_x, pivot_z = (float(v) for v in g["taper_pivot"])
    body_ry = float(g["body_half_width_y"])
    pat_ry = float(g["patella_half_width_y"])

    labels = np.full((nx, ny, nz), AIR, dtype=np.uint8)
    for j, yj in enumerate(y):
        s = np.sqrt(max(0.0, 1 - (yj / body_ry) ** 2))
        if s <= 0:
            continue
        xq = pivot_x + (Xf - pivot_x) / s
        zq = pivot_z + (Zf - pivot_z) / s
        body = _inside(xq, zq, outer[:, 0], outer[:, 1])
        in_bone = _inside(xq, zq, bone[:, 0], bone[:, 1])
        section = np.full(Xf.shape, AIR, dtype=np.uint8)
        section[body] = SOFT
        section[body & in_bone] = BONE
        sp = np.sqrt(max(0.0, 1 - (yj / pat_ry) ** 2))
        if sp > 0:
            in_pat = _inside(px0 + (Xf - px0) / sp, pz0 + (Zf - pz0) / sp, patella[:, 0], patella[:, 1])
            section[body & in_pat] = PATELLA
        labels[:, j, :] = section.reshape(nx, nz)

    stride = int(g.get("stride", 1))
    labels = subsample(labels, stride)
    return Volume(labels=labels, voxel=(d * stride,) * 3, surface_z=float(g["surface_z"]))
