Below, every ξ is a fresh random number, uniform in (0, 1]. Lengths are in mm and coefficients in 1/mm.

#### 1. Step length (optical depth)

$$\tau = -\ln \xi, \qquad s = \frac{\tau}{\mu_s}$$

τ is exponentially distributed: in a medium with scattering coefficient μs, the mean free path is 1/μs. After moving a distance L, the remaining depth is $\tau \leftarrow \tau - \mu_s L$.

#### 2. Absorption (continuous absorption weighting)

$$\Delta W = W\left(1 - e^{-\mu_a L}\right), \qquad W \leftarrow W - \Delta W$$

ΔW is added to the voxel where the step happens. This is the Beer–Lambert law applied along the path, as in mcxyz.

#### 3. Scattering direction: Henyey–Greenstein phase function

$$\cos\theta = \frac{1}{2g}\left[1 + g^2 - \left(\frac{1 - g^2}{1 - g + 2g\,\xi}\right)^2\right], \qquad \psi = 2\pi\xi$$

g is the mean cosine of the scattering angle. g = 0 is isotropic (then cos θ = 2ξ − 1); biological tissue has g ≈ 0.8–0.95, mostly forward. The new direction is built from unit vectors perpendicular to the old one, which stays numerically safe when the old direction is close to the z axis.

#### 4. Boundaries: Fresnel reflection and Snell refraction

$$n_1 \sin\theta_i = n_2 \sin\theta_t$$

$$R = \frac{1}{2}\left[\left(\frac{n_1\cos\theta_i - n_2\cos\theta_t}{n_1\cos\theta_i + n_2\cos\theta_t}\right)^2 + \left(\frac{n_1\cos\theta_t - n_2\cos\theta_i}{n_1\cos\theta_t + n_2\cos\theta_i}\right)^2\right]$$

Draw ξ: reflect if ξ < R, otherwise refract. When $\frac{n_1}{n_2}\sin\theta_i \ge 1$ there is total internal reflection. θ is measured from the normal of the voxel face, so curved boundaries are treated as "staircases" (see "Optimization directions").

#### 5. Russian roulette

$$W \le W_{th}:\quad W \leftarrow \begin{cases} W / p, & \xi < p \\ 0, & \text{otherwise} \end{cases}$$

Currently $W_{th} = 0.001$ and $p = 0.1$. The expected value is $p \cdot W/p = W$, so the average result does not change.

#### 6. Converting to physical quantities

$$A = \frac{\sum \Delta W}{N\,V_{voxel}}\ \left[\mathrm{mm^{-3}}\right], \qquad \varphi = \frac{A}{\mu_a}\ \left[\mathrm{mm^{-2}}\right]$$

N is the number of photons and V the voxel volume. φ is the fluence per unit incident energy. Multiply by the power P (W) for W/mm², then by 100 for W/cm², and by the exposure time for J/cm². Air voxels have no absorption, so their fluence comes from path lengths (track-length estimator): $\varphi = \sum W L / (N V)$.

#### 7. Statistical error

Photons run in batches. Each batch gives one estimate, and the spread between batches is the statistical error. The error falls as $1/\sqrt{N}$: four times the photons halves the error. The z value on the "Validation" page is (Monte Carlo − adding–doubling) ÷ combined standard error.
