"""mcsim: Monte Carlo light transport in voxelised tissue.

Ported from the legacy MATLAB prototype in ``legacy/matlab``. All lengths are
in millimetres internally; presets may be written in cm and are converted on load.

Typical use::

    from mcsim import load_preset, simulate
    preset = load_preset("skin_500nm", photons=10_000)
    result = simulate(preset)
    print(result.summary())
"""

from mcsim.config import Preset, RunConfig, SourceConfig, Tissue, load_preset
from mcsim.runner import simulate

__all__ = ["Preset", "RunConfig", "SourceConfig", "Tissue", "load_preset", "simulate"]
__version__ = "0.1.0"
