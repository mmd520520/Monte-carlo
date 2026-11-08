"""Normalised results, energy bookkeeping and saving (port of Step9_Output.m).

Units: lengths in mm. Every quantity is per unit launched energy, i.e. per
photon packet of weight 1 averaged over all launched packets:
  A    absorbed energy density            [1/mm^3]
  phi  fluence (A / mua, or air path)      [1/mm^2]
  R2   diffuse reflectance per area (top)  [1/mm^2]
  T2   transmittance per area (bottom)     [1/mm^2]
Multiply phi by the beam power in W to get W/mm^2 (x100 for W/cm^2).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from mcsim.config import Preset
from mcsim.geometry import AIR, Volume
from mcsim.optics import OpticsTable
from mcsim.source import Beam

ENERGY_TOLERANCE = 1e-8


class EnergyBookkeepingError(RuntimeError):
    pass


@dataclass
class SimulationResult:
    preset: Preset
    volume: Volume
    optics: OpticsTable
    beam: Beam
    n_photons: int
    A: np.ndarray
    phi: np.ndarray
    R2: np.ndarray
    T2: np.ndarray
    air_phi: np.ndarray
    energy: dict[str, float]
    counters: dict[str, float]
    batch_stats: dict[str, np.ndarray] = field(default_factory=dict)
    elapsed_s: float = 0.0
    transport_s: float = 0.0  # time inside the transport kernel only (no set-up, merging or output)
    finished_at: float = 0.0  # time.time() when the run finished
    workers: int = 1

    # ---------- derived ----------
    @property
    def power_w(self) -> float | None:
        return self.preset.source.power_w

    def fluence_w_cm2(self) -> np.ndarray:
        """Fluence rate in W/cm^2 for the preset's beam power."""
        if self.power_w is None:
            raise ValueError("preset has no power_w; fluence is only available per unit power")
        return self.phi * self.power_w * 100.0

    def absorbed_by_label(self) -> dict[str, float]:
        frac = np.bincount(
            self.volume.labels.ravel(), weights=self.A.ravel() * self.volume.voxel_volume,
            minlength=len(self.optics.mua),
        )
        return {self.optics.names.get(i, str(i)): float(frac[i]) for i in range(len(frac)) if i in self.optics.names}

    def summary(self) -> str:
        e = self.energy
        lines = [
            f"{self.preset.title}: {self.n_photons} photons, seed {self.preset.run.seed}, "
            f"{self.elapsed_s:.1f} s on {self.workers} worker(s)",
            f"  absorbed {e['absorbed']:.5f}  reflected {e['reflected']:.5f}  transmitted {e['transmitted']:.5f}",
            f"  side {e['side']:.5f}  specular {e['specular']:.5f}  roulette {e['roulette_correction']:+.2e}",
            f"  total with roulette correction {e['bookkeeping']:.12f}",
        ]
        return "\n".join(lines)

    # ---------- persistence ----------
    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        meta = {
            "preset": self.preset.to_dict(),
            "energy": self.energy,
            "counters": self.counters,
            "n_photons": self.n_photons,
            "elapsed_s": self.elapsed_s,
            "voxel_mm": list(self.volume.voxel),
            "units": "lengths mm; A 1/mm^3; phi, R2, T2 1/mm^2; per unit launched energy",
        }
        np.savez_compressed(
            path, labels=self.volume.labels, A=self.A, phi=self.phi, R2=self.R2, T2=self.T2,
            air_phi=self.air_phi, meta=np.array(json.dumps(meta, ensure_ascii=False)),
        )
        return path


def incident_air_beam(volume: Volume, beam: Beam) -> np.ndarray:
    """Analytic incident + specular fluence in the air layers (MATLAB 2demo AddIncidentAirBeam)."""
    out = np.zeros(volume.shape)
    ux, uy, uz = beam.u_air
    area = np.pi * beam.radius**2
    scale = 1.0 / (area * uz)
    xc, yc, zc = (volume.centers(a) for a in range(3))
    X, Y = np.meshgrid(xc, yc, indexing="ij")
    for k in np.nonzero(zc < volume.surface_z)[0]:
        travel = (volume.surface_z - zc[k]) / uz
        inc = (X + travel * ux - beam.x) ** 2 + (Y + travel * uy - beam.y) ** 2 <= beam.radius**2
        spec = (X - travel * ux - beam.x) ** 2 + (Y - travel * uy - beam.y) ** 2 <= beam.radius**2
        out[:, :, k] = scale * (inc + beam.specular * spec)
    return out


def normalise(
    preset: Preset, volume: Volume, optics: OpticsTable, beam: Beam,
    A_raw: np.ndarray, R_raw: np.ndarray, T_raw: np.ndarray, air_raw: np.ndarray,
    counters: np.ndarray, n: int,
) -> SimulationResult:
    from mcsim.kernel import (
        C_AIR_ESCAPED, C_BOUNDARY, C_LAUNCHED, C_ROULETTE, C_SCATTER, C_SIDE, C_TERMINATED,
    )

    if counters[C_LAUNCHED] != n or counters[C_TERMINATED] != n:
        raise RuntimeError("launched/terminated packet counts do not match the photon count")
    if not np.all(np.isfinite(A_raw)) or np.any(A_raw < 0):
        raise RuntimeError("absorption tally has negative or non-finite values")

    v = volume.voxel_volume
    energy = {
        "absorbed": float(A_raw.sum() / n),
        "reflected": float(R_raw.sum() / n),
        "transmitted": float(T_raw.sum() / n),
        "side": float(counters[C_SIDE] / n),
        "specular": float(beam.specular),
    }
    energy["total"] = sum(energy.values())
    energy["roulette_correction"] = float(counters[C_ROULETTE] / n)
    energy["bookkeeping"] = energy["total"] + energy["roulette_correction"]
    if abs(energy["bookkeeping"] - 1.0) >= ENERGY_TOLERANCE:
        raise EnergyBookkeepingError(f"energy bookkeeping off by {energy['bookkeeping'] - 1:.3e}")

    A = A_raw / (n * v)
    phi = np.full(volume.shape, np.nan)
    for label in np.unique(volume.labels):
        if label == AIR:
            continue
        mua = optics.mua[label]
        if mua > 0:
            mask = volume.labels == label
            phi[mask] = A[mask] / mua
    air_phi = np.zeros(volume.shape)
    air_phi[:, :, : air_raw.shape[2]] = air_raw / (n * v)  # skin mode tallies only the top air layers
    air = volume.labels == AIR
    if beam.launch_from_air:
        phi[air] = air_phi[air]
    else:
        phi[air] = (incident_air_beam(volume, beam) + air_phi)[air]

    counters_d = {
        "boundary_events": float(counters[C_BOUNDARY]),
        "scattering_events": float(counters[C_SCATTER]),
        "air_escaped_packets": float(counters[C_AIR_ESCAPED]),
    }
    return SimulationResult(
        preset=preset, volume=volume, optics=optics, beam=beam, n_photons=n,
        A=A, phi=phi, R2=R_raw / (n * volume.voxel_area), T2=T_raw / (n * volume.voxel_area),
        air_phi=air_phi, energy=energy, counters=counters_d,
    )
