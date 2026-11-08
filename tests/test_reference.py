"""Independent check without MATLAB: total reflection and transmission of a uniform slab.

Adding-doubling (Prahl, ``iadpython``) solves the same transport problem deterministically,
so a Monte Carlo result that agrees with it within statistical error confirms the physics
on its own. The slab is wide (41 mm) and thin, so it behaves like an infinite slab.
Setup and reference live in ``mcsim/reference.py`` (also used by the app's Validation page).
"""

import pytest

from mcsim.reference import compare_slab

# name, mua [1/mm], mus [1/mm], g, n, thickness [mm], launch_from_air
CASES = [
    ("tissue-like, index 1.4", 0.1, 10.0, 0.9, 1.4, 1.0, True),
    ("isotropic, thin, index 1.4", 1.0, 5.0, 0.0, 1.4, 0.5, True),
    ("epidermis-like, index 1.4", 2.0, 20.0, 0.9, 1.4, 0.2, True),
    ("index-matched, skin launch", 0.1, 10.0, 0.5, 1.0, 1.0, False),
]


@pytest.mark.parametrize("name, mua, mus, g, n, d, launch_from_air", CASES, ids=[c[0] for c in CASES])
def test_slab_matches_adding_doubling(name, mua, mus, g, n, d, launch_from_air):
    c = compare_slab(mua, mus, g, n, d, launch_from_air, photons=200_000, seed=11)
    assert c.side < 1e-3, "slab not wide enough to act as infinite"
    for q in ("R", "T"):
        assert abs(c.z(q)) <= 4.0, f"{name}: {q} z = {c.z(q):+.2f}"
