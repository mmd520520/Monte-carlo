#### 流程图每一步在代码里的位置

| 步骤 | 做什么 | 代码（`mcsim/`） | 原 MATLAB |
|---|---|---|---|
| 光源 | 斜入射、Snell 折射、镜面反射损失 | `source.py` `configure_beam()` | `Configure_ObliqueSource.m`、`Light_T.m` |
| ① 发射 Launch | 在圆形光斑内均匀取起点 | `kernel.py` `run_batch()` 开头 | `Step4_Launch` |
| ② 抽步长 Hop | 抽一个无量纲光学深度 τ | `run_batch()` | `Step5_Hop` |
| ③④ 走一步、吸收 Drop | 走到体素面或散射点，沿路吸收 | `run_batch()` 内层循环 | `Step5_Hop`、`Step7_Drop` |
| 边界 Boundary | 出网格、Fresnel 反射 / 折射、进入空气 | `run_batch()`、`_fresnel_reflects()`、`_air_track()` | `Step6_Boundary`、`Step6_AirTrack` |
| ⑤⑥ 散射 Spin + 轮盘赌 | HG 抽新方向；权重太小就轮盘赌 | `_spin()`、`run_batch()` 末尾 | `Step8_SpinCheck` |
| ⑦ 汇总 Normalise | 单位换算、光注量、能量守恒检查 | `results.py` `normalise()` | `Step9_Output` |
| 分批并行 | 批次、随机种子、多线程、合并 | `runner.py` `simulate()` | `MC_RunBatches.m` |

#### 两种模式

- **皮肤模式**（皮肤血管 500 nm）：光子从皮肤表面下方出发，已经折射过，权重扣掉镜面反射。光子一旦从组织进入空气，就记为反射，不再追踪；它在空气层里的直线路径另外记下来，用来画空气中的光。
- **膝关节模式**（膝关节 980 nm）：光子从空气里的光源出发，空气体素和组织一样追踪；所有折射率变化的地方都做 Fresnel 判定。

#### 为什么这样设计

- **光子包，而不是单个光子**：每个包带一个权重 W，沿路连续扣掉被吸收的部分（连续吸收权重 continuous absorption weighting），而不是“要么全吸收、要么不吸收”。同样的光子数，噪声小得多。
- **无量纲步长 τ 跨体素使用**：τ 在一个体素里没用完，就带着剩下的部分进入下一个体素，用新体素的 μs 换算距离。这样在不均匀组织里也是精确的。
- **轮盘赌**：权重很小的包继续追踪很浪费，直接丢掉又会让能量凭空消失。轮盘赌让它以概率 p 存活并把权重放大到 W/p，平均来看能量不多不少（无偏）。
- **能量守恒检查**：吸收 + 反射 + 透射 + 侧漏 + 镜面反射 + 轮盘赌差额，必须等于 1（误差小于 1e−8），否则直接报错。这一条能抓住很多编程错误。
