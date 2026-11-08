"""A web server runs every visitor in its own thread. Two runs started at the same moment must take turns:
Numba's default "workqueue" threading layer aborts the whole process if two threads enter it at once."""

import threading

import numpy as np

from mcsim import load_preset, simulate


def test_runs_started_together_take_turns():
    results, errors = [], []

    def visitor():
        try:
            results.append(simulate(load_preset("knee_980nm", photons=4_000, seed=3, stride=2), workers=0))
        except Exception as exc:  # noqa: BLE001 - any failure fails the test
            errors.append(exc)

    threads = [threading.Thread(target=visitor) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, errors
    assert len(results) == 3
    for r in results[1:]:  # same seed, so each run is identical
        assert np.array_equal(r.A, results[0].A)
