"""Extract the MATLAB skin smoke-test numbers into tests/data/matlab_skin_smoke.json.

Source: outputs/legacy_matlab/2demo/mc_smoke_results.mat (local only, not in git),
written by the serial MATLAB version on 2026-10-22 (Windows, R2023a):
Step4_Main(2000, true, 1, true) -> 40^3 grid, 0.1 mm voxels, normal incidence.
Run:  uv run --with h5py python tools/extract_matlab_baseline.py
"""

import json
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "outputs/legacy_matlab/2demo/mc_smoke_results.mat"
DST = ROOT / "tests/data/matlab_skin_smoke.json"


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))
    from mcsim import load_preset
    from mcsim.geometry import build_volume

    r = h5py.File(SRC, "r")["results"]
    A = r["A"][()].transpose(2, 1, 0)  # MATLAB column-major -> (x, y, z)
    v = float(r["dy"][()].item()) ** 3
    labels = build_volume(load_preset("skin_500nm", stride=10).geometry).labels
    names = {3: "blood", 4: "dermis", 5: "epidermis"}
    out = {
        "source": "outputs/legacy_matlab/2demo/mc_smoke_results.mat (MATLAB serial version, 2026-10-22)",
        "settings": {"preset": "skin_500nm", "stride": 10, "photons": int(r["Nphotons"][()].item()),
                     "seed": int(r["seed"][()].item()), "theta_deg": 0.0},
        "energy": {
            "absorbed": r["absorbedFraction"][()].item(),
            "reflected": r["reflectance"][()].item(),
            "transmitted": r["transmittance"][()].item(),
            "side": r["sideEscape"][()].item(),
            "specular": r["specular"][()].item(),
            "bookkeeping": r["bookkeepingTotal"][()].item(),
        },
        "absorbed_by_label": {names[k]: float((A[labels == k] * v).sum()) for k in names},
        "absorbed_by_depth_layer": [float(x) for x in (A * v).sum(axis=(0, 1))],
    }
    DST.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", DST)


if __name__ == "__main__":
    main()
