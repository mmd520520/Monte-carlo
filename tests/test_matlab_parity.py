"""Compare with the MATLAB skin smoke test (tests/data/matlab_skin_smoke.json).

The MATLAB numbers carry the noise of one run with N_m photons. We run 200
Python batches of 2,000 photons, estimate the per-photon standard deviation from
the batch spread, and require |MATLAB - Python| < 3 combined standard errors:
se = sd_photon * sqrt(1/N_m + 1/N_python). Works for any N_m in the baseline file.
"""

import json
import math
from pathlib import Path

import pytest

from mcsim import load_preset, simulate

BASELINE = json.loads((Path(__file__).parent / "data" / "matlab_skin_smoke.json").read_text(encoding="utf-8"))
LABELS = {"blood": 3, "dermis": 4, "epidermis": 5}
BATCH, N_BATCHES = 2000, 200


@pytest.fixture(scope="module")
def python_runs():
    s = BASELINE["settings"]
    p = load_preset(s["preset"], stride=s["stride"], photons=BATCH * N_BATCHES, batch_size=BATCH,
                    seed=s["seed"], theta_deg=s["theta_deg"])
    return simulate(p, workers=0)


def _z(matlab_value, batch_values):
    n_m = BASELINE["settings"]["photons"]
    n_p = BATCH * N_BATCHES
    sd_photon = batch_values.std(ddof=1) * math.sqrt(BATCH)
    se = sd_photon * math.sqrt(1 / n_m + 1 / n_p)
    return (matlab_value - batch_values.mean()) / se


@pytest.mark.parametrize("key", ["absorbed", "reflected", "transmitted", "side"])
def test_energy_terms_within_3_sigma(python_runs, key):
    z = _z(BASELINE["energy"][key], python_runs.batch_stats[key])
    assert abs(z) < 3, f"{key}: MATLAB {BASELINE['energy'][key]:.5f}, z={z:+.2f}"


@pytest.mark.parametrize("name", list(LABELS))
def test_absorption_by_tissue_within_3_sigma(python_runs, name):
    z = _z(BASELINE["absorbed_by_label"][name], python_runs.batch_stats["absorbed_by_label"][:, LABELS[name]])
    assert abs(z) < 3, f"{name}: z={z:+.2f}"


def test_specular_identical(python_runs):
    assert python_runs.energy["specular"] == pytest.approx(BASELINE["energy"]["specular"], abs=1e-15)
