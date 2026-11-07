"""Per-label optical property arrays for the kernel (index = tissue label).

Labels that no tissue defines get the MATLAB struct defaults: mua = mus = g = 0, n = 1.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mcsim.config import Tissue


@dataclass
class OpticsTable:
    mua: np.ndarray
    mus: np.ndarray
    g: np.ndarray
    n: np.ndarray
    names: dict[int, str]

    @classmethod
    def from_tissues(cls, tissues: list[Tissue]) -> "OpticsTable":
        size = max(t.label for t in tissues) + 1
        mua = np.zeros(size)
        mus = np.zeros(size)
        g = np.zeros(size)
        n = np.ones(size)
        names = {}
        for t in tissues:
            mua[t.label], mus[t.label], g[t.label], n[t.label] = t.mua, t.mus, t.g, t.n
            names[t.label] = t.name
        return cls(mua, mus, g, n, names)

    def check_labels(self, labels: np.ndarray) -> None:
        present = np.unique(labels)
        missing = [int(v) for v in present if int(v) not in self.names]
        if missing:
            raise ValueError(f"volume uses labels with no tissue defined: {missing}")
