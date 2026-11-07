"""Command line: ``uv run mcsim list`` and ``uv run mcsim run <preset> [options]``."""

from __future__ import annotations

import argparse
from pathlib import Path

from mcsim.config import list_presets, load_preset


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="mcsim", description="Monte Carlo light transport in tissue")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list presets")
    run = sub.add_parser("run", help="run a preset")
    run.add_argument("preset")
    run.add_argument("--photons", type=int)
    run.add_argument("--seed", type=int)
    run.add_argument("--batch-size", type=int)
    run.add_argument("--workers", type=int, default=0, help="parallel batches, 0 = all cores")
    run.add_argument("--stride", type=int, help="coarsen the grid by this factor")
    run.add_argument("--theta", type=float, help="incidence angle in air, degrees")
    run.add_argument("--out", type=Path, help="save results (.npz)")
    run.add_argument("--dose", type=float, nargs="*", help="depths below the skin in mm for a dose table")
    run.add_argument("--exposure", type=float, default=300.0, help="exposure time, s")
    run.add_argument("--radius", type=float, default=10.0, help="disk radius for the dose table, mm")
    run.add_argument("--power", type=float, help="beam power in W (needed for presets without power)")
    a = ap.parse_args(argv)

    if a.cmd == "list":
        for name in list_presets():
            print(name, "-", load_preset(name).title)
        return

    from mcsim.runner import simulate

    preset = load_preset(a.preset, photons=a.photons, seed=a.seed, batch_size=a.batch_size,
                         stride=a.stride, theta_deg=a.theta)
    result = simulate(preset, workers=a.workers,
                      progress=lambda done, total: print(f"\r{done}/{total} photons", end="", flush=True))
    print()
    print(result.summary())
    if a.dose:
        from mcsim.analysis import dose_table

        print(f"\ndepth(mm)  axis H (J/cm2)  disk mean H (J/cm2)  disk energy (J)  share   [{a.exposure:g} s, r={a.radius:g} mm]")
        for r in dose_table(result, a.dose, a.exposure, a.radius, power_w=a.power):
            flag = "  disk includes air" if r.disk_has_air else ""
            print(f"{r.depth_mm:9.1f}  {r.axis_H_j_cm2:14.4g}  {r.disk_mean_H_j_cm2:19.4g}  {r.disk_energy_j:15.4g}  {r.disk_energy_fraction:6.2%}{flag}")
    if a.out:
        print("saved", result.save(a.out))


if __name__ == "__main__":
    main()
