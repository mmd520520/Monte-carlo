# 用 GPU 加速：MCX 调研与接入方案

> MCX（Qianqian Fang 教授团队）和我们的引擎算的是同一套物理，而且已经有能在苹果 GPU 上跑的 Python 接口。建议把它接成我们框架里的一个可选“计算后端”：预设、剂量分析、画图、界面都不变，只把“跑光子”这一步交给 GPU。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 调研完成；可行性已在 Mac 上验证；接入还没开始 | 【马孟帝】、Eden Huang | 2026-11-07 |

---

## 1. 先看实测（2026-11-07，Apple M4 Pro，14 核 CPU，20 核 GPU）

同一块均匀平板：厚 1 mm，μa = 0.1/mm，μs = 10/mm，g = 0.9，折射率 1.4，上下都是空气；1,000 万个光子。

| 方法 | 吸收比例 | 用时 |
|---|---|---|
| 加倍法（确定性算法，作参照） | 0.2784 | — |
| MCX-CL，苹果 GPU（OpenCL） | 0.2784 | 0.4 s（GPU 计算 0.3 s） |
| 我们的引擎，14 核 CPU | 0.2784 | 4.8 s |

- **结果一致**：三种方法的吸收比例相同；中心轴光注量逐层相比，MCX / 我们 = 0.999–1.001。
- **归一化不同，要换算**：MCX 的光注量按“进入组织的能量”归一（已扣除表面镜面反射），我们按“入射能量”归一。乘以 `energytot / nphoton`（这里是 0.9722 = 1 − 镜面反射率）就对上了。
- **这次大约快 12 倍**。只是一个简单算例，苹果 GPU 也不是最快的。MCX 官方的说法是在 NVIDIA GPU 上“通常比充分优化的 CPU 程序快几百到一千倍”（pmcx 说明），这和我们这台机器的情况不是一回事，需要在 NVIDIA 机器上自己测。

自己重跑：

```bash
uv run --with pmcxcl --with pmcx python project/public/gpu_mcx/poc_mcxcl_slab.py
```

## 2. 他是谁、做了什么

Qianqian Fang，美国东北大学（Northeastern University）生物工程系副教授。2009 年发表 MCX（Fang & Boas, *Optics Express* 2009），此后十几年一直维护，NIH/NIGMS 资助（R01-GM114365）。最新的 MCX 3.0（v2026）在 2026-11-01 发布；我们 `references/third_party/MCX/` 里就是这个版本。

| 项目 | 是什么 | 对我们有什么用 |
|---|---|---|
| **MCX**（CUDA） | GPU 上的体素蒙特卡洛，和我们同一类模型；GitHub 197 星 | 有 NVIDIA 显卡时的主力后端 |
| **MCX-CL** / `pmcxcl` | OpenCL 版；Python 包有苹果芯片、Linux、Windows 的预编译版本（0.8.1） | Mac 上直接能用，本次实测用的就是它 |
| `pmcx` | MCX 的 Python 接口；Linux/Windows 带 CUDA，macOS 只有工具函数 | NVIDIA 机器上用 |
| **μMCX**（umcx） | 不到 1000 行的可移植重写，支持 CPU（OpenMP）、NVIDIA（OpenACC）、AMD（ROCm）；v0.5，没有 Python 接口 | 学习 GPU 蒙特卡洛写法的好材料；暂不接入 |
| **MMC** / `pmmc` | 四面体网格蒙特卡洛，弯曲边界比体素准 | 头部、弯曲皮肤面需要更高精度时考虑 |
| Iso2Mesh、Brain2Mesh、pyiso2mesh | 网格生成；Brain2Mesh 一行生成脑网格 | 建头部模型 |
| Redbird / RedbirdPy | 漫射光学成像（DOT）的建模和重建 | 将来做测量反演时参考 |
| MCX Cloud | 免费的在线 MCX 服务 | 只适合公开模型（数据会上传到外部服务器） |

## 3. MCX 和我们的引擎比较

| | 我们的引擎（mcsim） | MCX |
|---|---|---|
| 物理 | 体素蒙特卡洛：Fresnel 边界、Henyey–Greenstein 散射、轮盘赌 | 相同 |
| 硬件 | CPU 多核（Numba） | GPU（CUDA）；OpenCL 版也能用 CPU、苹果和 AMD GPU |
| 可复现 | 同种子逐位相同，和线程数无关 | 默认只保证统计一致；`autopilot=0` + 固定种子 + 固定线程设置才逐位相同 |
| 光源 | 圆形准直光斑，可斜入射 | 十几种：笔形、圆盘、平面、图案、等向等 |
| 输出 | 吸收、光注量、反射和透射、空气中的光、剂量分析 | 光注量（可按时间分辨）、探测光子的路径、灵敏度（Jacobian）、偏振 |
| 归一化 | 每单位入射能量 | 每单位进入组织的能量；乘 `energytot / nphoton` 换算 |
| 许可 | 【我们的仓库还没有许可证】 | GPLv3 |

## 4. 在我们的框架里怎么接

原则：**只换“跑光子”这一层**，其余都不动。

```
presets/*.yaml → load_preset → build_volume ──→ simulate(preset, backend=...)
                                                   ├─ "numba"：mcsim/kernel.py（现在）
                                                   └─ "mcx"：  mcsim/backends/mcx.py → pmcx 或 pmcxcl
                                              ──→ SimulationResult（吸收、光注量、反射、透射、能量）
                                              ──→ analysis（剂量）、plotting、app（不用改）
```

**数据怎么对应**

| 我们 | MCX 的 cfg | 说明 |
|---|---|---|
| `volume.labels`（1 = 空气） | `vol`（0 = 背景） | 皮肤模式：空气改成 0，光出去就算反射。膝关节模式：空气保留为真实介质（n = 1，μa = μs = 0），光离开皮肤后还能在弯曲表面重新进入组织 |
| 光学参数表（1/mm） | `prop`：每行 [μa, μs, g, n]，行号 = 标签，第 0 行是背景 | 单位相同，不用换算 |
| 体素大小 | `unitinmm` | MCX 体素是立方体；我们现在也是 |
| 光斑直径、位置、入射角 | `srctype="disk"`、`srcparam1=[半径（体素数）]`、`srcpos`、`srcdir` | 斜入射时的方向和折射要核对 |
| `launch_from_air` | 光源放在组织外，`isspecular=1` | MCX 自己找到第一个组织体素，并扣除镜面反射 |
| Fresnel 边界 | `isreflect=1` | 内部界面和外边界都按折射率做 Fresnel（源码 `src/mcx_core.cu` 第 2885 行附近） |
| 光子数、种子 | `nphoton`、`seed`、`autopilot=0` | 要逐位复现就设 `autopilot=0` |
| 光注量 `phi` | `flux × tstep × energytot / nphoton` | 一个时间窗（`tstart=0`，`tend=tstep=5e-9` s）就是连续光；换算已实测 |
| 吸收 `A` | `phi × μa` | 和现在一样 |
| 反射、透射 | `issaveref=1` 得到 `dref`（网格外要补一层 0）；或用 `cfg.bc` 把面设成探测器 | 要实现并测试 |
| 能量收支 | `stat.energyabs / stat.energytot` | 上下、侧面逃逸要从 `dref` 或探测面拿 |

**代码草图**（还没实现，只说明思路）：

```python
# mcsim/backends/mcx.py（草图）
def run_mcx(preset, volume, optics, beam):
    try:
        import pmcx as mcx            # 有 NVIDIA 显卡
    except ImportError:
        import pmcxcl as mcx          # Mac、AMD、Intel
    vol = volume.labels.copy()
    if not beam.launch_from_air:
        vol[vol == AIR] = 0           # 皮肤模式：空气当背景
    prop = np.column_stack([optics.mua, optics.mus, optics.g, optics.n])   # 行号 = 标签
    prop[0] = [0, 0, 1, 1]
    cfg = dict(nphoton=preset.run.photons, vol=vol, prop=prop, unitinmm=volume.voxel[2],
               srctype="disk", srcparam1=[beam.radius / volume.voxel[0], 0, 0, 0],
               srcpos=..., srcdir=..., issrcfrom0=1,
               tstart=0, tend=5e-9, tstep=5e-9, isreflect=1, isspecular=1, issaveref=1,
               seed=preset.run.seed, autopilot=0)
    res = mcx.run(cfg)
    phi = res["flux"][..., 0] * cfg["tstep"] * res["stat"]["energytot"] / cfg["nphoton"]
    ...  # 组装成 SimulationResult
```

## 5. 接入后怎么验收

1. **加倍法平板**：`tests/test_reference.py` 按后端参数化，MCX 也要全部通过。
2. **和我们的引擎对比**：皮肤、膝关节两个预设，能量各项和中心轴光注量在统计误差内一致。
3. **复现**：`autopilot=0` 时，同种子两次结果相同。
4. **速度**：记录 10⁶、10⁷、10⁸ 光子的用时（这台 Mac；有 NVIDIA 机器时也记录）。
5. **退回**：没有 GPU 或没装 MCX 时，自动用我们的引擎，界面照常可用。

## 6. 硬件怎么选

| 方案 | 能跑什么 | 适合 | 注意 |
|---|---|---|---|
| 苹果芯片的 Mac | `pmcxcl`（OpenCL） | 日常开发、中等规模计算 | 实测见第 1 节；苹果已宣布 OpenCL 只维护、不再更新 |
| 带 NVIDIA 显卡的 Linux 或 Windows 工作站 | `pmcx`（CUDA），最快 | 参数扫描、给机器学习造数据 | 需要采购或借用 |
| 国内云 GPU（按小时租） | `pmcx` | 偶尔的大批量计算；国内同事也能用 | 数据离开公司：只放公开的模型和参数 |
| MCX Cloud | MCX | 试用、教学 | 数据上传到外部服务器，敏感模型不能用 |

## 7. 许可（GPLv3）和数据安全

- MCX、MCX-CL、`pmcx`、`pmcxcl`、μMCX 都是 GPLv3（或更新版本）。**内部研究用没有问题。** 如果把 MCX 的代码或二进制随我们的软件、设备一起分发，就要按 GPL 公开相应源代码；用进产品之前先请法务确认。
- 做法：MCX 只作为**可选依赖**，不放进默认依赖；没装时一切照常。本文件夹的脚本只在运行时调用它，仓库里不带 MCX。
- 我们自己的仓库目前没有许可证文件。要不要加、加哪一种，【待定】。
- 用任何在线服务（MCX Cloud、云 GPU、在线 AI 工具）时，只放公开的模型和参数。产品相关的几何、参数、测量数据不上传。判断规则见 [project/README.md](../../README.md)。

## 8. 分步计划

| 阶段 | 内容 | 完成标准 | 负责人 / 时间 |
|---|---|---|---|
| 0 可行性 | 本文；Mac 上 MCX-CL 跑通平板 | 与加倍法、我们的引擎一致 ✓ | 已完成 2026-11-07 |
| 1 接入后端 | `mcsim/backends/mcx.py`；`simulate(backend=...)`；数据对应和归一化 | 第 5 节 1–3 条通过 | 【】 |
| 2 界面 | 加“计算后端：CPU / GPU”，自动检测 | 第 5 节第 5 条 | 【】 |
| 3 批量计算 | 参数扫描脚本（波长、光斑、组织参数），结果存盘 | 一次扫描 ≥ 100 组参数 | 【】 |
| 4 新能力 | 时间分辨、探测器（源–探测距离的灵敏度）、网格模型（MMC） | 按产品需求定 | 【】 |

## 9. 还没确认的

- MCX 在 μa = 0 的空气体素里怎么统计光注量（我们的膝关节模式要统计空气中的光）。
- 斜入射时，光源在空气中的方向和进入组织的折射是否和我们一致。
- 苹果 GPU 上大网格（例如 400³ 的皮肤全分辨率模型）的内存和速度。
- 由谁负责；要不要采购或租用 NVIDIA 机器。

## 10. 来源

- MCX 主页：https://mcx.space/（2026-11-07 访问）
- Qianqian Fang 的 GitHub：https://github.com/fangq?tab=repositories（2026-11-07 访问；星数为当天数据）
- μMCX：https://github.com/fangq/umcx
- pmcxcl：https://pypi.org/project/pmcxcl/（0.8.1，2026-11-01）
- 本地源码 `references/third_party/MCX/`（MCX v2026 / 3.0）：`LICENSE.txt`、`ChangeLog.txt`、`pmcx/README.md`、`mcxlab/mcxlab.m`、`src/mcx_core.cu`
- Fang Q, Boas DA. Monte Carlo simulation of photon migration in 3D turbid media accelerated by graphics processing units. *Optics Express* 2009; 17(22): 20178–20190. doi:10.1364/OE.17.020178

## 给 AI 的说明

- 第 1 节的数字来自 `poc_mcxcl_slab.py` 的实际运行；重测后更新，不要估算。
- 接入时先写第 5 节的测试，再写后端代码。
