"""Compare with the MATLAB skin smoke test (tests/data/matlab_skin_smoke.json).

MATLAB used 2000 photons, so its numbers carry the noise of one 2000-photon run.
We run many 2000-photon batches in Python and require each MATLAB value to lie
within 3 standard deviations of the Python batch distribution.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from mcsim import load_preset, simulate

BASELINE = json.loads((Path(__file__).parent / "data" / "matlab_skin_smoke.json").read_text(encoding="utf-8"))
LABELS = {"blood": 3, "dermis": 4, "epidermis": 5}


@pytest.fixture(scope="module")
def python_runs():
    s = BASELINE["settings"]
    p = load_preset(s["preset"], stride=s["stride"], photons=200 * s["photons"], batch_size=s["photons"],
                    seed=s["seed"], theta_deg=s["theta_deg"])
    return simulate(p, workers=0)


@pytest.mark.parametrize("key", ["absorbed", "reflected", "transmitted", "side"])
def test_energy_terms_within_3_sigma(python_runs, key):
    x = python_runs.batch_stats[key]
    z = (BASELINE["energy"][key] - x.mean()) / x.std(ddof=1)
    assert abs(z) < 3, f"{key}: MATLAB {BASELINE['energy'][key]:.5f}, Python {x.mean():.5f}, z={z:+.2f}"


@pytest.mark.parametrize("name", list(LABELS))
def test_absorption_by_tissue_within_3_sigma(python_runs, name):
    x = python_runs.batch_stats["absorbed_by_label"][:, LABELS[name]]
    z = (BASELINE["absorbed_by_label"][name] - x.mean()) / x.std(ddof=1)
    assert abs(z) < 3, f"{name}: z={z:+.2f}"


def test_specular_identical(python_runs):
    assert python_runs.energy["specular"] == pytest.approx(BASELINE["energy"]["specular"], abs=1e-15)
