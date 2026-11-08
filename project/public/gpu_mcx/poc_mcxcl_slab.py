"""MCX 可行性检查：同一块均匀平板，三种算法对比。 / MCX feasibility check on one uniform slab.

    uv run --with pmcxcl --with pmcx python project/public/gpu_mcx/poc_mcxcl_slab.py

pmcxcl 是 MCX 的 OpenCL 版，苹果芯片的 Mac 上直接能用（用 GPU）。有 NVIDIA 显卡时可以把
``import pmcxcl as mcx`` 换成 ``import pmcx as mcx``（CUDA 版，更快），cfg 不用改。
MCX 是 GPLv3：这个脚本只在运行时调用它，不随仓库分发 MCX。
"""

from __future__ import annotations

import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
warnings.filterwarnings("ignore")

import pmcxcl as mcx  # noqa: E402

from mcsim import simulate  # noqa: E402
from mcsim.config import Preset, RunConfig, SourceConfig, Tissue  # noqa: E402
from mcsim.geometry import Volume  # noqa: E402

MUA, MUS, G, N_IDX, THICK = 0.1, 10.0, 0.9, 1.4, 1.0  # 1/mm, 1/mm, -, -, mm: tissue-like slab with air on both sides
DZ, TOP = 0.05, 2                                       # voxel depth (mm), air layers above
PHOTONS = 10_000_000


def adding_doubling():
    import iadpython
    r, t, *_ = iadpython.Sample(a=MUS / (MUA + MUS), b=(MUA + MUS) * THICK, g=G, d=THICK, n=N_IDX,
                                n_above=1.0, n_below=1.0, quad_pts=32).rt()
    return 1.0 - r - t


def run_mcx():
    layers, nxy = int(round(THICK / DZ)), 800  # 800 x 0.05 mm = 40 mm wide
    vol = np.zeros((nxy, nxy, TOP + layers + 2), dtype=np.uint8)  # label 0 = air/background
    vol[:, :, TOP:TOP + layers] = 1
    cfg = dict(nphoton=PHOTONS, vol=vol, unitinmm=DZ, prop=[[0, 0, 1, 1], [MUA, MUS, G, N_IDX]],
               srctype="pencil", srcpos=[nxy / 2, nxy / 2, 0], srcdir=[0, 0, 1], issrcfrom0=1,
               tstart=0, tend=5e-9, tstep=5e-9,       # one time gate = continuous light
               isreflect=1, isspecular=1, seed=1, flog=os.devnull)
    t0 = time.perf_counter()
    res = mcx.run(cfg)
    wall = time.perf_counter() - t0
    st = res["stat"]
    # MCX normalises per unit energy that ENTERED (after specular loss); ours per unit INCIDENT energy.
    phi = res["flux"][..., 0] * cfg["tstep"] * st["energytot"] / PHOTONS
    c, w = nxy // 2, 10                                  # 20 x 20 voxels = 1 mm^2 around the axis
    axis = phi[c - w:c + w, c - w:c + w, TOP:TOP + layers].mean(axis=(0, 1))
    return st["energyabs"] / PHOTONS, axis, wall, st["runtime"] / 1000


def run_mcsim():
    layers = int(round(THICK / DZ))
    labels = np.ones((41, 41, TOP + layers + 2), dtype=np.uint8)  # 1 mm wide columns, 41 mm
    labels[:, :, TOP:TOP + layers] = 2
    preset = Preset(name="slab", title="slab", geometry={"type": "custom"},
                    tissues=[Tissue(1, "air", 0, 0, 0, 1.0), Tissue(2, "medium", MUA, MUS, G, N_IDX)],
                    source=SourceConfig(wavelength_nm=500, diameter=0.02, launch_from_air=True, emission_z=0.0, entry_label=2),
                    run=RunConfig(photons=PHOTONS, seed=11, batch_size=200_000, workers=0))
    t0 = time.perf_counter()
    r = simulate(preset, volume=Volume(labels=labels, voxel=(1.0, 1.0, DZ), surface_z=TOP * DZ))
    wall = time.perf_counter() - t0
    return r.energy["absorbed"], r.phi[20, 20, TOP:TOP + layers], wall, r.workers


if __name__ == "__main__":
    a_ref = adding_doubling()
    run_mcx()  # warm-up: builds the OpenCL kernel
    a_mcx, axis_mcx, wall_mcx, kernel_mcx = run_mcx()
    run_mcsim()  # warm-up: Numba compile
    a_ours, axis_ours, wall_ours, workers = run_mcsim()

    print(f"slab: mua={MUA}/mm mus={MUS}/mm g={G} n={N_IDX} thickness={THICK} mm, {PHOTONS:,} photons")
    print(f"  adding-doubling     absorbed {a_ref:.4f}")
    print(f"  MCX-CL (GPU)        absorbed {a_mcx:.4f}   {wall_mcx:5.1f} s wall ({kernel_mcx:.1f} s kernel)")
    print(f"  mcsim ({workers} CPU)     absorbed {a_ours:.4f}   {wall_ours:5.1f} s wall")
    ratio = axis_mcx / axis_ours
    print(f"  on-axis fluence MCX / mcsim over depth: mean {ratio.mean():.3f}, min {ratio.min():.3f}, max {ratio.max():.3f}")
