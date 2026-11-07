# 算法说明：体素蒙特卡洛光传输

> 一个光子包从光斑出发，随机地“走一段、留下一点能量、换个方向”，直到被吸收完或离开计算区域。放出几万到几十万个光子包，统计它们留下的能量，就得到光在组织里的分布。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 与代码 `mcsim/` 一致 | 光学实习生、Eden Huang | 2026-11-07 |

素材：实习生的流程图 [assets/Monte_Carlo流程图.png](assets/Monte_Carlo流程图.png)（依据 Jacques 2023 教程）和综述 [assets/](assets/README.md)。实现是对 `legacy/matlab/` 的逐步移植。

---

## 1. 模型怎么表示

- **组织**：三维体素数组，每个体素一个整数标签（1 = 空气，其余是组织）。每种组织有吸收系数 μa、散射系数 μs、各向异性因子 g、折射率 n。预设里写的是约化散射系数 μs′，载入时换算 μs = μs′ / (1 − g)。
- **单位**：内部一律 mm 和 1/mm。膝关节预设用 cm 书写，载入时换算。
- **坐标**：x、y 以光束轴为中心，z 从网格顶面（z = 0）向下。体素 (i, j, k) 占据 x ∈ [i·dx − nx·dx/2, (i+1)·dx − nx·dx/2]，y、z 同理（z 不减偏移）。

## 2. 一个光子包的一生

| 步骤 | 做什么 | 代码 |
|---|---|---|
| 发射 | 在光斑内均匀取点（半径 = R·√ξ），方向由入射角经 Snell 折射得到 | `kernel.run_batch` 开头；`source.configure_beam` |
| 走一段 | 抽一个光学距离 τ = −ln ξ；在当前体素内走 τ/μs，或先碰到体素面 | `kernel.run_batch` 内层循环 |
| 留一点 | 每走长度 L，吸收 ΔW = W·(1 − e^(−μa·L))，记在当前体素 | 同上 |
| 过边界 | 两侧折射率不同时按非偏振 Fresnel 公式随机决定反射或折射；走出网格则按顶面、底面、侧面记逃逸 | `kernel.run_batch` 边界段；`_fresnel_reflects` |
| 换方向 | Henyey–Greenstein 相函数抽偏转角，方位角均匀 | `kernel._spin` |
| 轮盘赌 | 权重 ≤ 0.001 时，以 10% 概率存活（权重 ×10），否则结束 | `kernel.run_batch` 末段 |

ξ 是 (0, 1) 上的均匀随机数。

## 3. 两种发射方式

| | 皮肤模式（`launch_from_air: false`） | 膝关节模式（`launch_from_air: true`） |
|---|---|---|
| 从哪发射 | 表皮内，紧贴表面 | 网格顶部的空气里（z = 0） |
| 表面反射 | 发射前按 Fresnel 一次扣除（镜面反射，垂直入射时 2.78%） | 在真实的弯曲皮肤面上逐个体素面处理 |
| 从组织进入空气 | 记为“从表面反射”，并沿直线统计它在空气层中的路径 | 继续在空气中传播，空气中的路径都统计 |
| 对应 MATLAB | `2demo` | `5demo` |

## 4. 统计量和归一化

N 个光子包发射后：

- 吸收能量密度 A = 体素累计吸收 / (N · 体素体积)，单位 1/mm³
- 光注量 Φ = A / μa（组织）；空气中用路径长度估计（膝关节），或解析入射光束 + 镜面反射 + 逃逸光路径（皮肤）。单位 1/mm²，即每单位入射能量
- 光注量率（W/cm²）= Φ × 功率 × 100
- 能量收支：吸收 + 反射 + 透射 + 侧面逃逸 + 镜面反射 + 轮盘赌修正 = 1，误差超过 10⁻⁸ 即报错

剂量（`mcsim/analysis.py`，与 `5demo/main.m` 一致）：

- 皮肤表面：光束轴上第一个组织体素的上表面
- 累计光注量 H = 光注量率 × 照射时间（J/cm²），是到达该处的光，不是被吸收的能量
- 圆面平均 H：圆面内体素中心处 H 的平均；圆面能量 = 平均光注量率 × 时间 × 圆面积（J）

## 5. 随机数和可复现

光子分成固定大小的批次，每批的种子由 `numpy.random.SeedSequence(seed).spawn(...)` 生成。批次以“波”的方式并行，每批写入自己的缓冲区，最后按批次顺序合并。所以结果只取决于（种子，批大小），单线程和并行结果逐位相同。

## 6. 验证结果（2026-11-07）

| 检查 | 结果 |
|---|---|
| 能量守恒 | 所有测试中误差 < 10⁻⁸（`tests/test_energy.py`） |
| 无散射时的比尔–朗伯定律 | 透射率与 e^(−μa·d) 一致到 10⁻⁸（两种发射方式） |
| 表面 Fresnel 反射 | 与 ((n−1)/(n+1))² 在统计误差内一致 |
| 可复现 | 同种子两次结果、单线程与并行结果逐位相同 |
| 几何与 MATLAB 一致 | 皮肤粗网格 18,900 个吸收体素的组织标签与 MATLAB 结果逐个一致 |
| 与 MATLAB 结果对比 | MATLAB 粗网格 2,000 光子的各项能量和各组织吸收，都在 Python 2,000 光子运行分布的 3σ 以内；偏离最大的是血液吸收（MATLAB 高 2.3σ）和反射率（低 2.3σ），见第 7 节 |
| 速度（14 核 Mac） | 10 万光子：皮肤 10 μm 全分辨率 7.9 s，20 μm 1.2 s，40 μm 0.6 s；膝关节 2.5 s |

## 7. 已知差异和待确认

- **随机数不同**：MATLAB 用 mrg32k3a / twister，Python 用 Numba 的 Mersenne Twister。两边结果只会在统计误差内一致，不会逐位相同。
- **MATLAB 基准光子数太少**：唯一可用的 MATLAB 数值结果只有 2,000 个光子。血液吸收和反射率偏离约 2σ，大约 2–3% 的 2,000 光子运行会偏离这么远，所以不能确认有系统差异，也不能排除。**请用 MATLAB 以相同设置跑 10 万光子**（`Step4_Main(100000, true, 1, true)`），用 `tools/extract_matlab_baseline.py` 更新基准后重跑测试。
- **膝关节没有 MATLAB 数值基准**：几何按 MATLAB 规则生成；多边形内外判断边界点的处理可能与 MATLAB `inpolygon` 有个别体素差异。剂量结果与实习生 11 月的光斑对比结果数量级一致，但那些运行的光斑和统计方式不同，只能作参考。
- **膝关节光源参数有三个版本**，见 `presets/knee_980nm.yaml` 的 notes。

## 8. MATLAB 到 Python 对照

| MATLAB（legacy/matlab/） | Python |
|---|---|
| `Tissue.m`、`Tissue_knee.m` | `mcsim/geometry/skin.py`、`knee.py` |
| `Tissue _optical_parameters.m`、`Light_T.m` | `presets/*.yaml`、`mcsim/config.py` |
| `Configure_ObliqueSource.m` | `mcsim/source.py` |
| `Step4_Launch` … `Step8_SpinCheck` | `mcsim/kernel.py` |
| `MC_RunBatch(es)`、`MC_*Tallies` | `mcsim/runner.py` |
| `Step9_Output`、`AddIncidentAirBeam` | `mcsim/results.py` |
| `5demo/main.m` 剂量分析 | `mcsim/analysis.py` |
| `Step10_Plot`、`Plot_Tissue3D` | `mcsim/plotting.py`、`app/streamlit_app.py` |

## 给 AI 的说明

- 改动 `mcsim/kernel.py` 时同步更新第 2、3 节，并重跑 `uv run pytest`。
- 第 6 节的数字来自实际运行；重新测量后更新，不要估算。
