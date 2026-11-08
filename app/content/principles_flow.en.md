#### Where each step lives in the code

| Step | What it does | Code (`mcsim/`) | Original MATLAB |
|---|---|---|---|
| Source | Oblique incidence, Snell refraction, specular loss | `source.py` `configure_beam()` | `Configure_ObliqueSource.m`, `Light_T.m` |
| ① Launch | Uniform start point in the circular beam | start of `kernel.py` `run_batch()` | `Step4_Launch` |
| ② Hop | Draw a dimensionless optical depth τ | `run_batch()` | `Step5_Hop` |
| ③④ Move and absorb (Drop) | Go to the voxel face or the scattering point, absorbing along the way | inner loop of `run_batch()` | `Step5_Hop`, `Step7_Drop` |
| Boundary | Leave the grid, Fresnel reflect / refract, enter air | `run_batch()`, `_fresnel_reflects()`, `_air_track()` | `Step6_Boundary`, `Step6_AirTrack` |
| ⑤⑥ Spin + roulette | New direction from HG; roulette when the weight is small | `_spin()`, end of `run_batch()` | `Step8_SpinCheck` |
| ⑦ Normalise | Units, fluence, energy check | `results.py` `normalise()` | `Step9_Output` |
| Batches in parallel | Batches, seeds, threads, merge | `runner.py` `simulate()` | `MC_RunBatches.m` |

#### Two modes

- **Skin mode** (skin with vessel, 500 nm): packets start just below the skin surface, already refracted, with the specular reflection taken off their weight. A packet that passes from tissue into air is counted as reflected and no longer tracked. Its straight path through the air layers is recorded separately, to draw the light in the air.
- **Knee mode** (knee, 980 nm): packets start at the source in the air. Air voxels are tracked like tissue, and every change of refractive index goes through a Fresnel check.

#### Why it is built this way

- **Packets, not single photons**: each packet carries a weight W. The absorbed part is taken off continuously along the path (continuous absorption weighting), instead of "absorbed completely or not at all". The same number of packets gives much less noise.
- **The dimensionless step τ carries across voxels**: if τ is not used up in one voxel, the rest goes into the next voxel and is converted to distance with that voxel's μs. This stays exact in non-uniform tissue.
- **Roulette**: tracking packets with a tiny weight is wasteful, but simply dropping them would make energy disappear. Roulette lets a packet survive with probability p and raises its weight to W/p, so on average no energy is gained or lost (unbiased).
- **Energy check**: absorbed + reflected + transmitted + side loss + specular + roulette balance must equal 1 (within 1e−8), or the run stops with an error. This catches many programming mistakes.
