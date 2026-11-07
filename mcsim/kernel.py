"""Photon-packet transport kernel (Numba).

One-to-one port of the legacy MATLAB steps:
  Step4_Launch -> launch(), Step5_Hop + Step7_Drop -> the hop loop,
  Step6_Boundary -> boundary(), Step6_AirTrack -> air_track(),
  Step8_SpinCheck -> spin() + roulette.

Two modes, selected by ``launch_from_air``:
  skin (False): start inside the tissue; a packet that crosses from tissue into
      air is counted as reflected and its straight path through the air layers
      is tallied (MATLAB 2demo).
  knee (True): start in the air; air voxels are tracked like any other medium,
      path length in air is tallied everywhere, and leaving the top face goes
      through a Fresnel check (MATLAB 5demo).

Counters (per batch, float64[8]):
  0 side escape weight, 1 roulette balance (old - new weight), 2 launched,
  3 terminated, 4 boundary events, 5 scattering events, 6 air-escaped packets.
"""

from __future__ import annotations

import math

import numba
import numpy as np

C_SIDE, C_ROULETTE, C_LAUNCHED, C_TERMINATED, C_BOUNDARY, C_SCATTER, C_AIR_ESCAPED = range(7)
N_COUNTERS = 8
AIR = 1
TINY = 2.2250738585072014e-308  # MATLAB realmin


@numba.njit(cache=True, inline="always")
def _face_distance(p, u, lo, hi):
    if u > 0.0:
        d = (hi - p) / u
    elif u < 0.0:
        d = (lo - p) / u
    else:
        return math.inf
    return d if d > 0.0 else 0.0


@numba.njit(cache=True)
def _fresnel_reflects(n1, n2, cos_i):
    """Return (reflected, cos_t). Draws one random number unless total internal reflection."""
    if cos_i > 1.0:
        cos_i = 1.0
    eta = n1 / n2
    st2 = eta * eta * max(0.0, 1.0 - cos_i * cos_i)
    if st2 >= 1.0:
        return True, 0.0
    ct = math.sqrt(1.0 - st2)
    rs = ((n1 * cos_i - n2 * ct) / (n1 * cos_i + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * cos_i) / (n1 * ct + n2 * cos_i)) ** 2
    return np.random.random() < (rs + rp) / 2.0, ct


@numba.njit(cache=True)
def _spin(u, g):
    """Henyey-Greenstein deflection (MATLAB Step8_SpinCheck), in place."""
    if abs(g) < 1e-12:
        cost = 2.0 * np.random.random() - 1.0
    elif g >= 1.0:
        cost = 1.0
    else:
        q = (1.0 - g * g) / (1.0 - g + 2.0 * g * np.random.random())
        cost = (1.0 + g * g - q * q) / (2.0 * g)
    cost = min(1.0, max(-1.0, cost))
    sint = math.sqrt(max(0.0, 1.0 - cost * cost))
    psi = 2.0 * math.pi * np.random.random()
    ux, uy, uz = u[0], u[1], u[2]
    # e1 = cross(a, u) with a = z (or y when u is nearly along z)
    if abs(uz) < 0.9:
        e1x, e1y, e1z = -uy, ux, 0.0
    else:
        e1x, e1y, e1z = uz, 0.0, -ux
    nrm = math.sqrt(e1x * e1x + e1y * e1y + e1z * e1z)
    e1x, e1y, e1z = e1x / nrm, e1y / nrm, e1z / nrm
    e2x = uy * e1z - uz * e1y
    e2y = uz * e1x - ux * e1z
    e2z = ux * e1y - uy * e1x
    cp, sp = math.cos(psi), math.sin(psi)
    nx = cost * ux + sint * (cp * e1x + sp * e2x)
    ny = cost * uy + sint * (cp * e1y + sp * e2y)
    nz = cost * uz + sint * (cp * e1z + sp * e2z)
    nrm = math.sqrt(nx * nx + ny * ny + nz * nz)
    u[0], u[1], u[2] = nx / nrm, ny / nrm, nz / nrm


@numba.njit(cache=True)
def _air_track(p, u, w, idx, spacing, offset, shape, air_layers, AIR_T):
    """Straight path of an escaping packet through the top air layers (MATLAB Step6_AirTrack)."""
    px, py, pz = p[0], p[1], p[2]
    ix, iy, iz = idx[0], idx[1], idx[2]
    while 0 <= ix < shape[0] and 0 <= iy < shape[1] and 0 <= iz < air_layers:
        lo0 = ix * spacing[0] - offset[0]
        lo1 = iy * spacing[1] - offset[1]
        lo2 = iz * spacing[2] - offset[2]
        d0 = _face_distance(px, u[0], lo0, lo0 + spacing[0])
        d1 = _face_distance(py, u[1], lo1, lo1 + spacing[1])
        d2 = _face_distance(pz, u[2], lo2, lo2 + spacing[2])
        axis = 0
        L = d0
        if d1 < L:
            axis, L = 1, d1
        if d2 < L:
            axis, L = 2, d2
        if not math.isfinite(L):
            break
        AIR_T[ix, iy, iz] += w * L
        px += L * u[0]
        py += L * u[1]
        pz += L * u[2]
        if axis == 0:
            ix += 1 if u[0] > 0 else -1
        elif axis == 1:
            iy += 1 if u[1] > 0 else -1
        else:
            iz += 1 if u[2] > 0 else -1


@numba.njit(cache=True)
def run_batch(
    labels, mua, mus, g, n, spacing, offset,
    beam_xy_r, start_z, launch_z, u0, w0,
    launch_from_air, air_layers, roulette_threshold, roulette_chance,
    n_photons, seed,
    A, R, T, AIR_T, C,
):
    """Transport ``n_photons`` packets into the given (zeroed) tally arrays."""
    np.random.seed(seed)
    shape = labels.shape
    p = np.empty(3)
    u = np.empty(3)
    idx = np.empty(3, dtype=np.int64)
    nxt = np.empty(3, dtype=np.int64)

    for _ in range(n_photons):
        # ---- launch (Step4_Launch) ----
        rr = beam_xy_r[2] * math.sqrt(np.random.random())
        az = 2.0 * math.pi * np.random.random()
        sx = beam_xy_r[0] + rr * math.cos(az)
        sy = beam_xy_r[1] + rr * math.sin(az)
        u[0], u[1], u[2] = u0[0], u0[1], u0[2]
        inward = (launch_z - start_z) / u[2]
        p[0], p[1], p[2] = sx + inward * u[0], sy + inward * u[1], start_z + inward * u[2]
        for a in range(3):
            idx[a] = int(math.floor((p[a] + offset[a]) / spacing[a]))
            if idx[a] < 0 or idx[a] >= shape[a]:
                raise ValueError("launch point outside the grid")
        label = labels[idx[0], idx[1], idx[2]]
        if launch_from_air:
            if label != AIR:
                raise ValueError("emission point must be in air")
        elif label == AIR:
            raise ValueError("launch point must be inside tissue")
        w = w0
        alive = True
        C[C_LAUNCHED] += 1.0

        while alive:
            # ---- hop + drop (Step5_Hop, Step7_Drop) ----
            tau = -math.log(max(np.random.random(), TINY))
            reached_scatter = False
            while alive and not reached_scatter:
                label = labels[idx[0], idx[1], idx[2]]
                ma = mua[label]
                ms = mus[label]
                lo0 = idx[0] * spacing[0] - offset[0]
                lo1 = idx[1] * spacing[1] - offset[1]
                lo2 = idx[2] * spacing[2] - offset[2]
                d0 = _face_distance(p[0], u[0], lo0, lo0 + spacing[0])
                d1 = _face_distance(p[1], u[1], lo1, lo1 + spacing[1])
                d2 = _face_distance(p[2], u[2], lo2, lo2 + spacing[2])
                axis = 0
                bd = d0
                if d1 < bd:
                    axis, bd = 1, d1
                if d2 < bd:
                    axis, bd = 2, d2
                sd = tau / ms if ms > 0.0 else math.inf
                hit = bd <= sd
                L = bd if hit else sd
                if not math.isfinite(L):
                    raise ValueError("non-finite step length")
                absorbed = w * (-math.expm1(-ma * L))
                w -= absorbed
                A[idx[0], idx[1], idx[2]] += absorbed
                if launch_from_air and label == AIR:
                    AIR_T[idx[0], idx[1], idx[2]] += w * L
                p[0] += L * u[0]
                p[1] += L * u[1]
                p[2] += L * u[2]
                tau = max(0.0, tau - ms * L)
                if not hit:
                    reached_scatter = True
                    continue

                # ---- boundary (Step6_Boundary) ----
                C[C_BOUNDARY] += 1.0
                if axis == 0:
                    p[0] = lo0 + spacing[0] if u[0] > 0 else lo0
                elif axis == 1:
                    p[1] = lo1 + spacing[1] if u[1] > 0 else lo1
                else:
                    p[2] = lo2 + spacing[2] if u[2] > 0 else lo2
                step = 1 if u[axis] > 0 else -1
                nxt[0], nxt[1], nxt[2] = idx[0], idx[1], idx[2]
                nxt[axis] += step
                if nxt[axis] < 0 or nxt[axis] >= shape[axis]:
                    if launch_from_air and axis == 2 and u[2] < 0:
                        refl, _ct = _fresnel_reflects(n[label], n[AIR], abs(u[2]))
                        if refl:
                            u[2] = -u[2]
                            continue
                    if axis == 2 and u[2] > 0:
                        T[idx[0], idx[1]] += w
                    elif axis == 2:
                        R[idx[0], idx[1]] += w
                    else:
                        C[C_SIDE] += w
                    alive = False
                    break
                nlabel = labels[nxt[0], nxt[1], nxt[2]]
                n1 = n[label]
                n2 = n[nlabel]
                reflected = False
                if n1 != n2:
                    reflected, ct = _fresnel_reflects(n1, n2, abs(u[axis]))
                    if not reflected:
                        eta = n1 / n2
                        for a in range(3):
                            if a != axis:
                                u[a] *= eta
                        u[axis] = ct if u[axis] > 0 else -ct
                        nrm = math.sqrt(u[0] * u[0] + u[1] * u[1] + u[2] * u[2])
                        u[0] /= nrm
                        u[1] /= nrm
                        u[2] /= nrm
                if reflected:
                    u[axis] = -u[axis]
                elif (not launch_from_air) and nlabel == AIR and label != AIR:
                    R[idx[0], idx[1]] += w
                    C[C_AIR_ESCAPED] += 1.0
                    _air_track(p, u, w, nxt, spacing, offset, shape, air_layers, AIR_T)
                    alive = False
                else:
                    idx[0], idx[1], idx[2] = nxt[0], nxt[1], nxt[2]

            if alive:
                # ---- spin + roulette (Step8_SpinCheck) ----
                _spin(u, g[labels[idx[0], idx[1], idx[2]]])
                C[C_SCATTER] += 1.0
                if w <= roulette_threshold:
                    old = w
                    if np.random.random() < roulette_chance:
                        w = w / roulette_chance
                    else:
                        w = 0.0
                        alive = False
                    C[C_ROULETTE] += old - w
        C[C_TERMINATED] += 1.0


@numba.njit(parallel=True, cache=True)
def run_wave(
    labels, mua, mus, g, n, spacing, offset,
    beam_xy_r, start_z, launch_z, u0, w0,
    launch_from_air, air_layers, roulette_threshold, roulette_chance,
    counts, seeds, A, R, T, AIR_T, C,
):
    """Run len(counts) batches in parallel, each into its own slice of the tally buffers."""
    for k in numba.prange(counts.shape[0]):
        A[k, :, :, :] = 0.0
        R[k, :, :] = 0.0
        T[k, :, :] = 0.0
        AIR_T[k, :, :, :] = 0.0
        C[k, :] = 0.0
        run_batch(
            labels, mua, mus, g, n, spacing, offset,
            beam_xy_r, start_z, launch_z, u0, w0,
            launch_from_air, air_layers, roulette_threshold, roulette_chance,
            counts[k], seeds[k], A[k], R[k], T[k], AIR_T[k], C[k],
        )
