#### Five points from the talk

1. **What is measured**: more neural activity → neurovascular coupling → local blood flow (CBF) and blood volume (CBV) rise → the concentrations of oxygenated and deoxygenated haemoglobin in tissue change. Continuous-wave NIRS measures **relative changes** of the two (ΔHbO₂, ΔHbR); frequency- and time-domain NIRS can, under model assumptions, also estimate **absolute tissue oxygenation** (StO₂); DCS / SCOS use speckle fluctuations to measure a **blood flow index** (BFI).
2. **Why 700–900 nm**: water absorbs little, so light gets through scalp and skull, and the absorption spectra of the two haemoglobins still differ. Above 900 nm water absorption rises (with a peak near 970 nm); common silicon detectors stop responding near 1100 nm, so longer wavelengths need InGaAs detectors.
3. **Three ways to measure**: continuous wave (CW) measures intensity only; frequency domain (FD) modulates the source brightness as a sine wave and measures amplitude loss and phase delay; time domain (TD) sends very short pulses and measures the distribution of photon arrival times (DTOF). More information lets you solve for more unknowns, at the cost of more complex hardware.
4. **How to invert**: a **forward model** (Monte Carlo, the diffusion approximation or the radiative transfer equation) gives "tissue parameters → detector readings"; then the **inverse problem** (with regularisation and priors) recovers tissue parameters from readings.
5. **Depth**: light from source to detector follows a "banana-shaped" path. The farther apart they are, the deeper the banana and the less light arrives. Very short channels mostly see the scalp and can be used to remove superficial interference.

#### Key formulas, and what they need from Monte Carlo

**Modified Beer–Lambert law (MBLL)**, the standard conversion for CW NIRS. With the change in optical density $\Delta OD = -\Delta \ln I$:

$$\Delta OD(\lambda) = \big(\varepsilon_{\mathrm{HbO_2}}(\lambda)\,\Delta c_{\mathrm{HbO_2}} + \varepsilon_{\mathrm{HbR}}(\lambda)\,\Delta c_{\mathrm{HbR}}\big)\, d \cdot \mathrm{DPF}(\lambda)$$

$\varepsilon$ is the extinction coefficient (natural-log definition; multiply base-10 tables by $\ln 10$) and $d$ the source–detector distance. Two wavelengths (for example 760 and 850 nm) give two equations for $\Delta c_{\mathrm{HbO_2}}$ and $\Delta c_{\mathrm{HbR}}$. The extinction coefficients at the two wavelengths must differ enough, or noise is amplified.

**Differential pathlength factor (DPF) and path per layer**. DPF is the mean distance light actually travels divided by the straight-line distance, $\mathrm{DPF} = \langle L\rangle / d$. In a layered head it is more accurate to split by layer:

$$\Delta OD \approx \sum_k \langle L_k\rangle\, \Delta\mu_{a,k}$$

$\langle L_k\rangle$ is the mean distance detected photons travel in layer $k$ (scalp, skull, CSF, cortex, …). **This is exactly what Monte Carlo is best at**: record how far each detected photon travels in each layer and take the mean.

**Tissue oxygenation**:

$$\mathrm{StO_2} = \frac{c_{\mathrm{HbO_2}}}{c_{\mathrm{HbO_2}} + c_{\mathrm{HbR}}},\qquad \Delta\mathrm{HbT} = \Delta c_{\mathrm{HbO_2}} + \Delta c_{\mathrm{HbR}}$$

**Spatially resolved spectroscopy (SRS)**. Measuring attenuation $A$ (base 10) at several distances $\rho$ at one wavelength, for a semi-infinite homogeneous medium far from the source:

$$\mu_a\,\mu_s' \approx \frac{1}{3}\left(\ln 10\,\frac{\partial A}{\partial \rho} - \frac{2}{\rho}\right)^2$$

With $\mu_s'$ known (or assumed), this gives an absolute $\mu_a$. Whether the approximation holds in a layered head, and how large the error is, can be checked with Monte Carlo.

**Time domain: the distribution of times of flight (DTOF) and its moments**:

$$M_0 = \int H(t)\,dt,\qquad \langle t\rangle = \frac{1}{M_0}\int t\,H(t)\,dt,\qquad V = \frac{1}{M_0}\int (t-\langle t\rangle)^2 H(t)\,dt$$

In Monte Carlo, a detected photon's time of flight is its total path divided by the speed of light in tissue: $t = nL/c$ ($n$ the refractive index). A histogram of these times is the DTOF. The amplitude and phase measured in the frequency domain are the Fourier transform of the DTOF at the modulation frequency $f$, $\tilde H(f) = \int H(t)\,e^{-i2\pi f t}\,dt$, so the DTOF also gives the frequency domain.

**Sensitivity (Jacobian) and inversion**. With the head cut into voxels, the change in channel $i$ is approximately a weighted sum of absorption changes in each voxel:

$$\Delta OD_i \approx \sum_j J_{ij}\,\Delta\mu_{a,j},\qquad J_{ij} = \langle L_{ij}\rangle$$

$J_{ij}$ is the mean distance photons detected in channel $i$ travel in voxel $j$, given directly by Monte Carlo. Solving back for $\Delta\mu_a$ needs regularisation, since there are fewer channels than unknowns:

$$\Delta\boldsymbol{\mu}_a = \left(\mathbf{J}^\mathsf{T}\mathbf{J} + \lambda\mathbf{I}\right)^{-1}\mathbf{J}^\mathsf{T}\,\Delta\mathbf{OD}$$

**Blood flow (DCS)**: $g_2(\tau) = 1 + \beta\,|g_1(\tau)|^2$; fitting the decay of $g_1$ gives the blood flow index BFI. Monte Carlo would also have to record each photon's scattering angles (momentum transfer), so this comes later.

#### How it connects to this engine

| What NIRS needs | How Monte Carlo provides it | The engine today | Next |
|---|---|---|---|
| Mean path per layer, DPF | Record the path detected photons travel in each layer | Counts absorption over the whole volume; no detectors | **V4 detector records** |
| Depth sensitivity per distance, the "banana" map | Accumulate detected photons' path per voxel (Jacobian) | None | V4 + sensitivity maps |
| TD: DTOF; FD: amplitude and phase | Total path of detected photons → time of flight | None | **A6 time-resolved** |
| Two or more wavelengths | μa from HbO₂, HbR, water and lipid concentrations × extinction spectra | One wavelength at a time, values typed in | Spectral module + **V1 white Monte Carlo** (all wavelengths in one run) |
| Scalp, skull, CSF, grey and white matter | Layered or realistic head geometry | Only the skin and knee models; the head atlas from the MATLAB era (`legacy/matlab/head/`) is not connected yet | A 5-layer slab head first, then the atlas |
| Blood flow (DCS) | Record each photon's momentum transfer | None | Later |
| Machine-learning inversion | Many simulations as training data | Not fast enough yet | After S1 or GPU |

#### What to do next, in three steps

1. **Add "detectors" first (V4 + A6).** Place a few detectors on the scalp, for example 10, 20 and 30 mm from the source, and record each detected photon's path per layer and total path. That gives DPF, sensitivity per layer, the banana-shaped paths and the DTOF, and with it the frequency-domain amplitude and phase. This step matters most for the headband, so V4 is now high priority under "Optimization directions".
2. **Then the "head model" and "spectra".** Start with a 5-layer slab (scalp, skull, CSF, grey matter, white matter; literature values, each with its source), then connect the head atlas from the MATLAB era. Compute absorption from haemoglobin, water and lipid concentrations and their extinction spectra, and use V1 white Monte Carlo to cover several wavelengths in one run. That answers what the headband needs most: how much light reaches the brain, which source–detector distance is most sensitive to the cortex, and how much hair, skin tone and skull thickness matter.
3. **Finally inversion and validation.** Use the Jacobian for MBLL and tomographic (DOT) inversion, and try machine-learning inversion on simulated data. Validate in the order the talk suggested: phantom → layered model → people. Blood flow (DCS) comes later.
