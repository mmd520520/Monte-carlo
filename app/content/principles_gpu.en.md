#### Why a GPU suits Monte Carlo

- **Photons do not affect each other**: how photon 1 travels has nothing to do with photon 2. Problems like this are called "embarrassingly parallel": the more workers at once, the faster it goes.
- **CPUs and GPUs are good at different things**: a CPU has a few powerful cores that handle complex, branching work well; a GPU has thousands of simple cores that handle large amounts of repetitive, simple arithmetic. Each step of a photon (draw a random number, compute a distance, take an exponential, change direction) is simple, which suits a GPU.
- **So on a GPU, one thread tracks one photon**, and tens of thousands of photons move through the tissue at the same time. The CPU version gives each core one batch, so 14 cores run 14 photons at a time.

#### Four problems to solve on a GPU

| Problem | Why it happens | Usual solution (the MCX approach) |
|---|---|---|
| Divergence | A GPU runs threads in groups of 32 (a warp) that execute the same instruction at the same moment (SIMT). If one photon is scattering while another is crossing a boundary, they take turns and part of the group waits | Keep each step as uniform as possible with few branches; when a thread finishes a photon it launches the next one immediately (persistent threads), so no thread sits idle |
| Write conflicts | Thousands of threads add energy into the same 3-D grid at once, especially in the crowded voxels near the source, and plain additions can be lost | Atomic add: the hardware guarantees each addition completes. The CPU version gives each core its own grid; GPU memory cannot hold thousands of copies |
| Random numbers | Every thread needs its own independent random sequence | One tiny generator per thread (MCX uses xorshift128+, whose state is only 16 bytes), each with a different seed |
| Precision | Single precision (float32) is much faster on a GPU; double precision is slow on consumer cards | Compute mainly in single precision; check the error of totals such as the energy balance separately |

#### How it differs from our CPU version

- **Reproducibility**: on a GPU the order of the atomic additions changes from run to run, so the last digits differ slightly (statistically equivalent). Our CPU version is reproducible bit for bit. GPU results must therefore be accepted as "agreeing within statistical error", not identical to the last digit.
- **Units**: MCX reports fluence per unit energy entering the tissue. Multiply by `flux × tstep × energytot / nphoton` to get our units. This conversion has been checked on the Mac.
- **Where the speed comes from, and where it stops**: the more photons and the simpler each step, the bigger the GPU's advantage. The main limits are write conflicts near the source, divergence and memory bandwidth.

#### Feasibility test (2026-11-07)

MCX-CL, by Prof. Qianqian Fang (Northeastern University), ran the same slab on the same Mac's GPU (20 cores). 10⁷ photons took 0.4 s, against 4.8 s for our engine on 14 CPU cores, about 12 times faster. Both gave an absorbed fraction of 0.2784, the same as adding–doubling. The MCX authors say it is hundreds of times faster than optimized CPU programs on NVIDIA cards; that needs measuring on our own machine.

#### Current decision: later

On 2026-11-08 we decided not to do GPU acceleration yet. First complete the models (skin and fat layers) and do the CPU-side optimizations (S1, S3 and S5 under "Optimization directions"). When runs of 10⁸ photons or more become routine, or parameters need to be swept many times, connect MCX following the [GPU guide](https://github.com/mmd520520/Monte-carlo/blob/refactor/python-interactive/project/public/gpu_mcx/GUIDE.md) (`project/public/gpu_mcx/GUIDE.md`, in Chinese):

1. Build a "backend" interface first, so one model can run on the CPU (today's engine) or the GPU (MCX) with exactly the same result format.
2. Cross-check every model against adding–doubling and the current engine before using it.
3. MCX is licensed under GPLv3, so it is an optional install, not bundled into our code.
4. Choose the machine (an NVIDIA card) first, measure, then decide.
