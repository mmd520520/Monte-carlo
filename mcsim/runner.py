"""Batching, parallel waves and reproducible random streams (port of MC_RunBatches.m).

Photons are split into fixed batches; batch k gets its own seed from
numpy.random.SeedSequence(run.seed).spawn(...). Batches run in parallel waves
(one Numba thread per batch) and are merged in batch order, so the result
depends only on (seed, batch_size) and is bit-identical for any worker count.
"""

from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable

import numba
import numpy as np

from mcsim.config import Preset
from mcsim.geometry import Volume, build_volume
from mcsim.kernel import (
    C_ROULETTE, C_SIDE, N_COUNTERS, run_wave,
)
from mcsim.optics import OpticsTable
from mcsim.results import SimulationResult, normalise
from mcsim.source import configure_beam

ProgressFn = Callable[[int, int], None]


def batch_plan(photons: int, batch_size: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    n_batches = -(-photons // batch_size)
    counts = np.full(n_batches, batch_size, dtype=np.int64)
    counts[-1] = photons - batch_size * (n_batches - 1)
    seeds = np.array(
        [s.generate_state(1, dtype=np.uint32)[0] for s in np.random.SeedSequence(seed).spawn(n_batches)],
        dtype=np.int64,
    )
    return counts, seeds


BUFFER_BUDGET_BYTES = float(os.environ.get("MCSIM_BUFFER_GB", "2")) * 1e9

# Numba's default "workqueue" threading layer must not be entered by two Python threads at once
# (the process aborts). A web server runs each visitor in its own thread, so runs take turns here.
# On a shared server, set MCSIM_LOCK_TIMEOUT_S so a visitor waits at most that long for another run.
_RUN_LOCK = threading.Lock()
LOCK_TIMEOUT_S = float(os.environ.get("MCSIM_LOCK_TIMEOUT_S", "inf"))


class BusyError(RuntimeError):
    """Another run is in progress and did not finish within MCSIM_LOCK_TIMEOUT_S."""


def resolve_workers(requested: int, n_batches: int, bytes_per_batch: int = 0) -> int:
    """Parallel batches per wave: requested (0 = all cores), capped by batches, threads and memory."""
    w = requested if requested and requested > 0 else (os.cpu_count() or 1)
    if bytes_per_batch > 0:
        w = min(w, max(1, int(BUFFER_BUDGET_BYTES // bytes_per_batch)))
    return max(1, min(w, n_batches, numba.config.NUMBA_NUM_THREADS))


def simulate(
    preset: Preset,
    *,
    workers: int | None = None,
    volume: Volume | None = None,
    progress: ProgressFn | None = None,
) -> SimulationResult:
    timeout = -1 if LOCK_TIMEOUT_S == float("inf") else LOCK_TIMEOUT_S
    if not _RUN_LOCK.acquire(timeout=timeout):
        raise BusyError(f"another simulation is still running (waited {LOCK_TIMEOUT_S:g} s)")
    try:
        return _simulate(preset, workers=workers, volume=volume, progress=progress)
    finally:
        _RUN_LOCK.release()


def _simulate(
    preset: Preset,
    *,
    workers: int | None,
    volume: Volume | None,
    progress: ProgressFn | None,
) -> SimulationResult:
    t0 = time.perf_counter()
    run = preset.run
    volume = volume if volume is not None else build_volume(preset.geometry)
    optics = OpticsTable.from_tissues(preset.tissues)
    optics.check_labels(volume.labels)
    beam = configure_beam(preset.source, optics, volume)

    counts, seeds = batch_plan(run.photons, run.batch_size, run.seed)
    shape = volume.shape
    # Skin mode only tallies air paths in the top air layers; knee mode needs the whole volume.
    nz_air = shape[2] if beam.launch_from_air else max(1, volume.air_layers)
    air_shape = (shape[0], shape[1], nz_air)
    bytes_per_batch = 8 * (int(np.prod(shape)) + int(np.prod(air_shape)) + 2 * shape[0] * shape[1])
    W = resolve_workers(workers if workers is not None else run.workers, len(counts), bytes_per_batch)
    numba.set_num_threads(W)

    labels = np.ascontiguousarray(volume.labels, dtype=np.uint8)
    spacing = np.array(volume.voxel, dtype=float)
    offset = volume.offset
    beam_xy_r = np.array([beam.x, beam.y, beam.radius])
    u0 = np.array([beam.ux, beam.uy, beam.uz])

    A = np.zeros(shape)
    R = np.zeros(shape[:2])
    T = np.zeros(shape[:2])
    AIR_T = np.zeros(air_shape)
    C = np.zeros(N_COUNTERS)
    A_buf = np.empty((W, *shape))
    R_buf = np.empty((W, *shape[:2]))
    T_buf = np.empty((W, *shape[:2]))
    AIR_buf = np.empty((W, *air_shape))
    C_buf = np.empty((W, N_COUNTERS))

    n_labels = len(optics.mua)
    flat_labels = labels.ravel()
    stats = {k: [] for k in ("photons", "absorbed", "reflected", "transmitted", "side", "roulette")}
    stats["absorbed_by_label"] = []

    done = 0
    transport_s = 0.0
    for start in range(0, len(counts), W):
        m = min(W, len(counts) - start)
        tw = time.perf_counter()
        run_wave(
            labels, optics.mua, optics.mus, optics.g, optics.n, spacing, offset,
            beam_xy_r, beam.start_z, beam.launch_z, u0, beam.w0,
            beam.launch_from_air, volume.air_layers, run.roulette_threshold, run.roulette_chance,
            counts[start : start + m], seeds[start : start + m],
            A_buf[:m], R_buf[:m], T_buf[:m], AIR_buf[:m], C_buf[:m],
        )
        transport_s += time.perf_counter() - tw
        for j in range(m):  # merge in batch order: identical sums for any W
            A += A_buf[j]
            R += R_buf[j]
            T += T_buf[j]
            AIR_T += AIR_buf[j]
            C += C_buf[j]
            nb = float(counts[start + j])
            stats["photons"].append(nb)
            stats["absorbed"].append(A_buf[j].sum() / nb)
            stats["reflected"].append(R_buf[j].sum() / nb)
            stats["transmitted"].append(T_buf[j].sum() / nb)
            stats["side"].append(C_buf[j, C_SIDE] / nb)
            stats["roulette"].append(C_buf[j, C_ROULETTE] / nb)
            stats["absorbed_by_label"].append(
                np.bincount(flat_labels, weights=A_buf[j].ravel(), minlength=n_labels) / nb
            )
        done += int(counts[start : start + m].sum())
        if progress is not None:
            progress(done, run.photons)

    result = normalise(preset, volume, optics, beam, A, R, T, AIR_T, C, run.photons)
    result.batch_stats = {k: np.array(v) for k, v in stats.items()}
    result.elapsed_s = time.perf_counter() - t0
    result.transport_s = transport_s
    result.workers = W
    return result
