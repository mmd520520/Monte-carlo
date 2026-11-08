#### How it runs today: CPU cores, no GPU

- **Numba just-in-time compilation (JIT)**: the kernel is written in plain Python. The first run compiles it to machine code and caches it on disk, and later runs reuse that.
- **Threads**: photons are split into fixed-size batches, each with its own random seed. One thread runs one batch and writes into its own tally grid, so no locks are needed, and the batches are merged in order at the end. The result therefore depends only on the seed and the batch size: 1 core or 14 cores give exactly the same numbers.
- **Memory limit**: every thread needs a full copy of the tally grid. On a large grid, the number of threads is capped by the memory budget (2 GB by default, environment variable `MCSIM_BUFFER_GB`).

#### Measured speed (2026-11-08, Apple M4 Pro, 14 CPU cores, 200,000 photons each)

| Model | Grid | Voxel | Time | Photons per second | Threads used | Voxel faces crossed / scatterings per photon |
|---|---|---|---|---|---|---|
| Knee 980 nm | 80 × 48 × 84 | 2.5 mm | 2.2 s | about 92,000 | 14 | 86 / 328 |
| Knee 980 nm | 160 × 96 × 168 | 1.25 mm | 3.4 s | about 60,000 | 14 | 173 / 326 |
| Skin with vessel 500 nm | 400 × 400 × 400 | 0.01 mm | 20.1 s | about 10,000 | **3** | **476 / 116** |

The table and a further measurement show three things:

1. **The skin model used only 3 of the 14 cores**: one 400³ tally grid takes about 0.5 GB, so the 2 GB budget allows only 3 copies.
2. **Photons cross more voxel faces than they scatter**: in the skin model each photon crosses 476 voxel faces but scatters only 116 times. Finer voxels mean more crossings and slower runs.
3. **Merging the tally grids takes a lot of time**: on the 1.25 mm knee grid, 10⁶ photons take 9.6 s in total, of which only 3.0 s is spent tracking photons; most of the rest is merging a whole grid after every batch. This is the first thing worth optimizing (see S1 under "Optimization directions").

The button below measures the speed on **the machine serving this page**, so once the app runs on a server, you can see that server's speed directly.

#### How many photons? In practice 10⁶–10⁸

- The statistical error scales roughly as 1/√N: 100 times the photons gives one tenth of the error.
- Published work typically uses 10⁶–10⁸ photons, and GPU programs often run 10⁸ or more. The app now goes up to 10⁸; from 10⁶ upwards the sidebar shows the estimated time, and a progress bar appears while it runs.
- On this Mac (knee, 2.5 mm voxels): 10⁶ photons took 9.6 s (about 100,000 per second). At that speed 10⁷ would take about 1.6 minutes, but a laptop slows down under long full load; one measured run took 8.6 minutes (with the battery very low). By the same numbers 10⁸ takes 15 minutes to 1.5 hours, which is better run on a server.
- Suggestion: check the settings with 10⁴–10⁵, draw conclusions from 10⁶–10⁷, and keep 10⁸ for where a very small error matters, such as the dose deep in the tissue.
- Finer voxels are slower; the 10 μm skin grid is the slowest (see the table above).
