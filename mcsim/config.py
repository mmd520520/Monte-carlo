"""Preset loading and validation.

A preset is one YAML file in ``presets/`` that holds the geometry, the optical
properties of every tissue (with sources), the light source and run settings.
The YAML may use mm or cm (``length_unit``); everything is converted to mm here,
so the rest of the package only ever sees mm and 1/mm.
"""

from __future__ import annotations

import copy
import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

PRESET_DIR = Path(__file__).resolve().parent.parent / "presets"
TO_MM = {"mm": 1.0, "cm": 10.0}

# Geometry keys that are counts or flags, not lengths (never unit-converted).
_GEOMETRY_NON_LENGTH = {"type", "shape", "stride"}


@dataclass(frozen=True)
class Tissue:
    """Optical properties of one tissue label. Coefficients in 1/mm."""

    label: int
    name: str
    mua: float
    mus: float
    g: float
    n: float
    source: str = ""


@dataclass
class SourceConfig:
    """Uniform circular beam. Lengths in mm, angles in degrees."""

    wavelength_nm: float
    diameter: float
    x: float = 0.0
    y: float = 0.0
    theta_deg: float = 0.0
    phi_deg: float = 0.0
    power_w: float | None = None
    launch_from_air: bool = False
    emission_z: float = 0.0
    entry_label: int = 2

    @property
    def radius(self) -> float:
        return self.diameter / 2.0


@dataclass
class RunConfig:
    photons: int = 10_000
    seed: int = 1
    batch_size: int = 5_000
    workers: int = 1
    roulette_threshold: float = 0.001
    roulette_chance: float = 0.10


@dataclass
class Preset:
    name: str
    title: str
    geometry: dict[str, Any]
    tissues: list[Tissue]
    source: SourceConfig
    run: RunConfig
    display_unit: str = "mm"
    notes: list[str] = field(default_factory=list)
    based_on: str = ""

    def tissue(self, label: int) -> Tissue:
        for t in self.tissues:
            if t.label == label:
                return t
        raise KeyError(f"no tissue with label {label}")

    def to_dict(self) -> dict[str, Any]:
        """Plain dict of the resolved preset (mm units), for saving next to results."""
        return dataclasses.asdict(self)


def _scale_lengths(value: Any, factor: float) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return value * factor
    if isinstance(value, list):
        return [_scale_lengths(v, factor) for v in value]
    if isinstance(value, dict):
        return {k: _scale_lengths(v, factor) for k, v in value.items()}
    return value


def _tissue_from_yaml(item: dict[str, Any], to_mm: float) -> Tissue:
    g = float(item["g"])
    if "mus" in item and "musp" in item:
        raise ValueError(f"tissue {item['name']}: give mus or musp, not both")
    if "musp" in item:
        mus_native = float(item["musp"]) / (1.0 - g) if g < 1 else 0.0
    else:
        mus_native = float(item.get("mus", 0.0))
    return Tissue(
        label=int(item["label"]),
        name=str(item["name"]),
        mua=float(item["mua"]) / to_mm,
        mus=mus_native / to_mm,
        g=g,
        n=float(item["n"]),
        source=str(item.get("source", "")),
    )


def resolve_preset_path(name_or_path: str | Path) -> Path:
    p = Path(name_or_path)
    if p.suffix in {".yaml", ".yml"} and p.exists():
        return p
    candidate = PRESET_DIR / f"{name_or_path}.yaml"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"preset not found: {name_or_path} (looked in {PRESET_DIR})")


def list_presets() -> list[str]:
    return sorted(p.stem for p in PRESET_DIR.glob("*.yaml"))


def load_preset(name_or_path: str | Path, **overrides: Any) -> Preset:
    """Load a preset and convert it to mm.

    ``overrides`` may set any RunConfig or SourceConfig field (source lengths in
    mm), plus ``stride`` to coarsen the geometry, e.g.
    ``load_preset("skin_500nm", photons=2000, stride=10)``.
    """
    path = resolve_preset_path(name_or_path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    unit = raw.get("length_unit", "mm")
    if unit not in TO_MM:
        raise ValueError(f"length_unit must be one of {sorted(TO_MM)}, got {unit!r}")
    f = TO_MM[unit]

    geometry = copy.deepcopy(raw["geometry"])
    for key in list(geometry):
        if key not in _GEOMETRY_NON_LENGTH:
            geometry[key] = _scale_lengths(geometry[key], f)
    geometry.setdefault("stride", 1)

    tissues = [_tissue_from_yaml(t, f) for t in raw["tissues"]]
    labels = [t.label for t in tissues]
    if len(set(labels)) != len(labels):
        raise ValueError("duplicate tissue labels in preset")

    s = dict(raw["source"])
    for key in ("diameter", "x", "y", "emission_z"):
        if key in s and s[key] is not None:
            s[key] = float(s[key]) * f
    source = SourceConfig(**s)
    run = RunConfig(**raw.get("run", {}))

    for key, value in overrides.items():
        if value is None:
            continue
        if key == "stride":
            geometry["stride"] = int(value)
        elif hasattr(run, key):
            setattr(run, key, type(getattr(run, key))(value))
        elif hasattr(source, key):
            setattr(source, key, value)
        else:
            raise KeyError(f"unknown override: {key}")

    preset = Preset(
        name=str(raw["name"]),
        title=str(raw.get("title", raw["name"])),
        geometry=geometry,
        tissues=tissues,
        source=source,
        run=run,
        display_unit=str(raw.get("display_unit", unit)),
        notes=list(raw.get("notes", [])),
        based_on=str(raw.get("based_on", "")),
    )
    validate(preset)
    return preset


def validate(p: Preset) -> None:
    r = p.run
    if r.photons <= 0 or r.batch_size <= 0:
        raise ValueError("photons and batch_size must be positive")
    if not (0 <= r.seed < 2**32):
        raise ValueError("seed must be in [0, 2**32)")
    if not (0 < r.roulette_chance <= 1) or r.roulette_threshold <= 0:
        raise ValueError("invalid roulette settings")
    s = p.source
    if not (0 <= s.theta_deg < 90):
        raise ValueError("theta_deg must be in [0, 90)")
    if s.diameter <= 0:
        raise ValueError("beam diameter must be positive")
    labels = {t.label for t in p.tissues}
    if 1 not in labels:
        raise ValueError("label 1 must be air")
    if s.entry_label not in labels:
        raise ValueError(f"entry_label {s.entry_label} has no tissue")
    for t in p.tissues:
        if t.mua < 0 or t.mus < 0 or not (-1 < t.g <= 1) or t.n < 1:
            raise ValueError(f"invalid optical properties for {t.name}")
