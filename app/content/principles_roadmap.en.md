**What is already in place**: continuous absorption weighting, Russian roulette, Numba compilation and threads, fully reproducible batches, the energy check, and automatic tests against adding–doubling and the MATLAB version. Below is what can still be done, in five groups. Any benefit marked "estimated" has not been measured yet.

#### 1. Faster

| ID | Direction | What to do | Benefit | Effort | Priority |
|---|---|---|---|---|---|
| S1 | **Leaner tally memory, less merging** | Tally in float32 instead of float64; tally only the region of interest; let each thread accumulate across batches and merge once at the end (computing the per-batch statistics inside the kernel); or share one grid between threads with atomic adds | Large grids can use every core (the skin model uses 3 of 14 today), and far less merging: on the 1.25 mm knee grid, 10⁶ photons take 9.6 s, of which only 3.0 s is spent tracking photons; most of the rest is merging a whole grid after every batch. Estimated 2–3× faster | Small | **Highest** |
| S2 | **GPU backend** | Connect MCX / MCX-CL as an optional backend, so one model can run on the CPU or the GPU | Measured about 12× on the Apple GPU; estimated tens to hundreds of times on NVIDIA cards | Medium | Later (decided 2026-11-08; see "Parallelism and GPU" for how it works) |
| S3 | Faster voxel traversal | Find the next voxel face with the incremental DDA algorithm (Amanatides–Woo) and precompute 1/u, instead of recomputing three face distances every time | Face crossings take most of the time; estimated 1.5–2× | Small | **High** (most useful at 10⁷–10⁸ photons) |
| S4 | Faster random numbers | Switch to an xorshift / xoroshiro generator (the kind MCX uses) | Estimated 10–20% | Small | Low |
| S5 | Adaptive stopping | Stop when the quantity of interest (for example the dose at one depth) has an error below a set value (for example 1%) | No wasted photons; a more responsive app | Small | Medium |
| S6 | Caching and precomputation | Compute common settings in advance and store results by their parameters | Results appear immediately once deployed | Small | Medium (at deployment) |

#### 2. Same accuracy with fewer photons (variance reduction)

| ID | Direction | What to do | Benefit | Effort | Priority |
|---|---|---|---|---|---|
| V1 | **White Monte Carlo / scaling** | Run once and record each packet's path length in each tissue; for a new μa, only reweight by $W\,e^{-\sum \mu_{a,i} L_i}$ instead of running again | Comparing wavelengths (for example 810 / 980 / 1064 nm) at the target depth and sweeping absorption cost almost nothing | Medium | **High** |
| V2 | Perturbation Monte Carlo | The same packets also give the derivatives of the result with respect to μa and μs | Sensitivity analysis; fitting tissue optical properties to measurements | Medium | Medium |
| V3 | Importance sampling / splitting | Split packets that go deep (for example 2–3 cm in the knee) into several with shared weight | Much less noise at depth | Medium | Medium |
| V4 | Detector records (detected photons) | Record packets leaving at a detector position, with their path length in each tissue | Sensitivity maps and "banana" paths for the headband (fNIRS-like); MCX supports this natively | Medium | Medium (needed for the headband) |

#### 3. More accurate (physics)

| ID | Direction | What to do | Benefit | Effort | Priority |
|---|---|---|---|---|---|
| A1 | **Complete the tissue layers** | Add skin and fat layers to the knee model, with literature values for each wavelength | Today only relative comparisons are possible; with the layers, dose numbers become meaningful in absolute terms | Small | **High** |
| A2 | **Temperature: bioheat model** | Solve the Pennes bioheat equation on the same voxel grid, with heat source = absorbed A × power | Estimate the tissue temperature rise and whether it stays within safe limits; screen settings before bench tests | Medium | **High** |
| A3 | Parameter uncertainty | Literature μa, μs′ and g often differ by a factor of two; draw parameters within their ranges and run many times | A band instead of a single line, so conclusions are more reliable | Medium | Medium |
| A4 | Curved boundaries (staircase error) | Vessels and the skin surface become "staircases" of voxels, so the Fresnel normal is wrong. Options: finer voxels near interfaces, split-voxel Monte Carlo (SVMC, Yan & Fang 2020), or mesh-based Monte Carlo (MMC, Fang 2010) | More accurate near curved interfaces | Medium to large | Medium |
| A5 | Phase function | Only Henyey–Greenstein today; some tissues are better described by modified HG or Mie theory | More accurate small-angle scattering | Small | Low |
| A6 | Time-resolved | Record each packet's time of flight | Future time-domain NIRS (TD-NIRS); MCX supports this natively | Medium | Low |

#### 4. Better validation

| ID | Direction | What to do | Priority |
|---|---|---|---|
| T1 | More benchmarks | MCML multilayer benchmarks, comparison with mcxyz, and a cross-check against MCX after every change once it is connected | Medium |
| T2 | Voxel convergence | Refine the voxels of one model step by step until the result stops changing | Medium |
| T3 | **Bench measurements** | Compare with measurements on phantoms or ex vivo tissue: the only check against the real world | **High** |

#### 5. Engineering

| ID | Direction | What to do | Priority |
|---|---|---|---|
| E1 | Backend interface | `simulate(preset, backend="numba" or "mcx")` with the same result format (needed for S2) | Later, with S2 |
| E2 | Deployment | Run on a server, queue long jobs, precompute common results (S6) | Medium |

#### Suggested first four

1. **S1 leaner tally memory, less merging**: a small change; on fine grids merging now takes about two thirds of the time, and large grids could use every core.
2. **A1 complete the knee layers + V1 white Monte Carlo**: answers the 980 nm rehab-laser questions directly (dose at the target depth for different wavelengths and settings).
3. **A2 bioheat model**: estimates whether the temperature rise stays within safe limits; screen settings by simulation first, then on the bench.
4. **S3 faster voxel traversal + S5 adaptive stopping**: once runs reach 10⁷–10⁸ photons, every minute on the CPU counts.

The GPU (S2, E1) comes later, when runs above 10⁸ photons or repeated parameter sweeps become routine.
