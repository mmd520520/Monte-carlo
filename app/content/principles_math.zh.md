下面的 ξ 都是 (0, 1] 里均匀分布的随机数，每次重新抽。长度单位 mm，系数单位 1/mm。

#### 1. 步长（光学深度）

$$\tau = -\ln \xi, \qquad s = \frac{\tau}{\mu_s}$$

τ 服从指数分布：光在散射系数为 μs 的介质里，自由程的平均值是 1/μs。走了距离 L 以后，剩下的 τ 是 $\tau \leftarrow \tau - \mu_s L$。

#### 2. 吸收（连续吸收权重）

$$\Delta W = W\left(1 - e^{-\mu_a L}\right), \qquad W \leftarrow W - \Delta W$$

ΔW 加到这一步所在的体素里，也就是比尔–朗伯定律（Beer–Lambert law）沿路径的形式，和 mcxyz 相同。

#### 3. 散射方向：Henyey–Greenstein 相函数

$$\cos\theta = \frac{1}{2g}\left[1 + g^2 - \left(\frac{1 - g^2}{1 - g + 2g\,\xi}\right)^2\right], \qquad \psi = 2\pi\xi$$

g 是平均散射角的余弦：g = 0 各向同性（这时 cos θ = 2ξ − 1），生物组织 g ≈ 0.8–0.95，以向前散射为主。新方向用一组与旧方向垂直的单位向量合成，旧方向接近 z 轴时也不会出现数值问题。

#### 4. 边界：Fresnel 反射和 Snell 折射

$$n_1 \sin\theta_i = n_2 \sin\theta_t$$

$$R = \frac{1}{2}\left[\left(\frac{n_1\cos\theta_i - n_2\cos\theta_t}{n_1\cos\theta_i + n_2\cos\theta_t}\right)^2 + \left(\frac{n_1\cos\theta_t - n_2\cos\theta_i}{n_1\cos\theta_t + n_2\cos\theta_i}\right)^2\right]$$

抽一个 ξ：ξ < R 就反射，否则折射。$\frac{n_1}{n_2}\sin\theta_i \ge 1$ 时是全反射（total internal reflection）。这里的 θ 是相对体素面的法线，所以曲面边界是按“台阶”处理的（见“优化方向”）。

#### 5. 俄罗斯轮盘赌

$$W \le W_{th}:\quad W \leftarrow \begin{cases} W / p, & \xi < p \\ 0, & \text{否则} \end{cases}$$

现在 $W_{th} = 0.001$，$p = 0.1$。期望值 $p \cdot W/p = W$，不改变平均结果。

#### 6. 换算成物理量

$$A = \frac{\sum \Delta W}{N\,V_{voxel}}\ \left[\mathrm{mm^{-3}}\right], \qquad \varphi = \frac{A}{\mu_a}\ \left[\mathrm{mm^{-2}}\right]$$

N 是光子数，V 是体素体积。φ 是每单位入射能量的光注量（fluence）；乘以功率 P（W）得到 W/mm²，再乘 100 得到 W/cm²；乘以照射时间得到能量密度 J/cm²。空气体素没有吸收，用路径长度累计（track-length estimator）：$\varphi = \sum W L / (N V)$。

#### 7. 统计误差

光子按批次计算，每批给出一个估计值，批次之间的离散程度就是统计误差。误差随 $1/\sqrt{N}$ 下降：光子数乘 4，误差减半。“验证”页的 z 值就是 (蒙特卡洛 − 加倍法) ÷ 合并标准误差。
