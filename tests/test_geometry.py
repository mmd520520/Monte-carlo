import numpy as np

from mcsim import load_preset
from mcsim.geometry import build_volume, matlab_round


def test_matlab_round_halves_away_from_zero():
    assert matlab_round(2.5) == 3 and matlab_round(-2.5) == -3 and matlab_round(0.5) == 1


def test_skin_smoke_grid_matches_matlab_layers():
    v = build_volume(load_preset("skin_500nm", stride=10).geometry)
    assert v.shape == (40, 40, 40) and v.voxel == (0.1, 0.1, 0.1)
    assert v.air_layers == 10
    assert np.all(v.labels[:, :, :10] == 1)        # air above 1 mm
    assert np.all(v.labels[:, :, 10] == 5)         # one epidermis layer (100 um)
    counts = dict(zip(*np.unique(v.labels, return_counts=True)))
    assert counts == {1: 16000, 3: 3160, 4: 43240, 5: 1600}  # vessel = 79 x-z cells x 40 y


def test_skin_full_resolution_layers():
    v = build_volume(load_preset("skin_500nm", stride=4).geometry)
    assert v.shape == (100, 100, 100)
    assert set(np.unique(v.labels)) == {1, 3, 4, 5}


def test_knee_labels_and_shape():
    v = build_volume(load_preset("knee_980nm", stride=2).geometry)
    assert v.shape == (80, 48, 84)
    assert set(np.unique(v.labels)) == {1, 2, 3, 4}
    # skin surface on the beam axis is curved; on axis it starts near the nominal 4 cm
    j = v.shape[1] // 2
    i = np.argmin(np.abs(v.centers(0)))
    first_tissue_z = v.centers(2)[np.argmax(v.labels[i, j, :] > 1)]
    assert 35 < first_tissue_z < 50  # mm
