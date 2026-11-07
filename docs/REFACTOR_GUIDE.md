# Monte Carlo 光传输仿真：代码库重构指南

> 分支：`refactor/python-interactive`　|　日期：2026-11-07　|　状态：阶段 1–7 已完成（2026-11-07）
> 本文既是本项目的重构说明，也可作为「科研原型代码 → 可维护工程」的通用模板（见第 9 节）。

---

## 0. 一句话目标

把散落在仓库里的 MATLAB 原型 + 大量第三方资料，整理成**一个 Python 仿真包 + 一个交互界面 + 一套自动验证**，让任何人 clone 后 5 分钟能跑出结果。

---

## 1. 现状诊断

### 1.1 仓库构成（共 863 MB，其中 git 历史 385 MB）

| 类别 | 内容 | 体积 | 问题 |
|---|---|---|---|
| **自有代码** | `matlab/2demo`（皮肤+血管，500 nm，mm）<br>`matlab/5demo`（膝关节，980 nm，cm，含剂量计算） | 2.1 MB，约 3,600 行 | 见 1.2 |
| 第三方源码 | `MCX/` `MMC/` `MCML/` | 54 MB | 原样拷贝，与自有代码混放 |
| 重复压缩包 | `MCML_MCX_MMC_开源代码压缩包.zip`（= 上面三个目录） | 48 MB | **完全重复** |
| 可执行程序 | `MCXStudio-win64-v2025.10/` + 同名 `.zip` | 88 MB | Windows 安装包，**重复且含 32 个 .exe/.dll** |
| 文献 | `论文.zip`、`Parameter_paper.pdf`、`head/*.pdf` | 95 MB | 压缩包无法检索，不应进 git |
| 数据集 | `Parameter_paper_Dataset_invivo_subjects_TDDOS.zip` | 68 MB | 应外部存储，只保留链接 |
| 解剖模型 | `knee-2016-09/`（Slicer 图谱）、`head/`（头部体素 + 25 MB 预渲染 HTML） | 127 MB | 未被仿真代码使用 |
| 说明材料 | `Monte_Carlo流程图.png`、`Monte_Carlo（简单介绍）.pdf` | 1.7 MB | 有价值，应归入 docs |

**结论：自有代码只占仓库 0.25%。**

### 1.2 自有代码的主要问题

| # | 问题 | 例子 |
|---|---|---|
| 1 | **复制粘贴式分叉**：两个 demo 是同一算法的两份拷贝，各自改了几行 | 膝关节版在 `Step6_Boundary` 加了顶部 Fresnel、在 `Step4_Launch` 改成从空气发射；皮肤版没有 |
| 2 | **第三份拷贝**：`2demo/reference_serial_version/` 是旧版串行代码 | 与现行代码部分不同，没人知道该信哪个 |
| 3 | **参数藏在脚本里**，靠 `run()` / `eval(fileread())` 注入变量 | `Prepare_Inputs` 执行 `Tissue.m` 后假设工作区里有 `T, Nx, dx…` |
| 4 | **几何、参数、绘图混在一个文件** | `Tissue.m` 建模型后直接画图；`main.m` 后半段是剂量分析脚本 |
| 5 | **单位不统一**：皮肤 mm、膝关节 cm，靠注释区分 | 光学系数 mm⁻¹ / cm⁻¹ 混用风险 |
| 6 | **文件名含空格/中文**，迫使用 `eval` 绕开 | `Tissue _optical_parameters.m` |
| 7 | **生成物进了 git** | 13 张结果 PNG、`mc_smoke_results.mat`、`.bak`、`.ps` |
| 8 | **调试残留** | `fprintf("11111111111 用到了")`、`clear; clc` 出现在函数文件中 |
| 9 | **无自动测试**：验证靠手动看 `verification.txt` | 能量守恒检查只是运行时 `assert` |

> 值得保留的优点：算法本身清晰（Launch → Hop → Boundary → Drop → Spin → Roulette，与 MCML 一致）；有能量守恒自检；并行时用独立随机子流，结果可复现。**重构是换结构，不是换物理。**

---

## 2. 重构原则

1. **一套引擎，多个预设。** 皮肤和膝关节只是「几何 + 光学参数 + 光源」的不同组合，算法代码只写一次。差异（是否从空气发射、顶部是否做 Fresnel）变成配置开关。
2. **数据与代码分离。** 光学参数、几何尺寸、光源设置写在 YAML/TOML 配置里，每个数值附文献出处。改参数不改代码。
3. **一个函数只做一件事。** 建模、仿真、后处理、绘图四层分开；仿真内核不画图、不写文件。
4. **单位唯一。** 内部统一用 **mm**，只在输入/输出边界换算并显式标注。
5. **物理不变，用测试证明。** 每次改动都要通过：能量守恒（误差 < 1e-8）+ 与 MATLAB 原结果对比（R / A / T 在统计误差内一致）。
6. **性能靠编译不靠妥协。** 逐光子循环用 Numba JIT 编译，批次用多进程并行；保持「固定种子 → 结果可复现」。
7. **仓库只放源代码和小型参考数据。** 大文件、安装包、压缩包、文献走外部存储，仓库里留链接和校验值。
8. **旧代码冻结不删除。** MATLAB 原版移入 `legacy/`，作为对照基准，不再修改。
9. **小步提交，每步可运行。** 每个 commit 只做一类事（搬文件 / 拆模块 / 加测试），信息写清楚「为什么」。
10. **每个文件夹都有 README。** 统一结构：是什么、状态 / 负责人、里面有什么、怎么用、更新记录、给 AI 的说明。人能看懂，AI 也能据此蒸馏和更新（格式见根目录 README）。

---

## 3. 目标结构

```
monte-carlo/
├── README.md                 # 5 分钟上手：安装、运行、截图
├── pyproject.toml            # 依赖与版本（uv 管理）
├── mcsim/                    # Python 仿真包
│   ├── geometry/             #   体素模型：skin.py, knee.py（只建 T 数组）
│   ├── optics.py             #   组织光学参数加载、mus = musp/(1-g)
│   ├── source.py             #   光源：圆斑、斜入射、Fresnel 镜面反射
│   ├── kernel.py             #   光子传输内核（Numba）：launch/hop/boundary/drop/spin
│   ├── runner.py             #   分批、并行、随机子流、结果合并
│   ├── results.py            #   归一化：A、Φ、R、T、能量收支
│   ├── analysis.py           #   剂量：中心轴 / 圆面平均 J/cm²、光斑大小对比
│   └── plotting.py           #   截面图、3D 组织图（Plotly）
├── presets/                  # 配置文件（含文献出处）
│   ├── skin_500nm.yaml
│   └── knee_980nm.yaml
├── app/
│   └── streamlit_app.py      # 交互界面
├── tests/                    # 能量守恒、物理极限、MATLAB 对比
├── slides/                   # 分享 PPT，一场一个文件夹（只在本地，不进公开仓库）
├── docs/
│   ├── REFACTOR_GUIDE.md     # 本文
│   ├── algorithm.md          # 算法说明（整合原流程图与 PDF）
│   ├── optical_parameters.md # 参数来源（整合原「光学参数文献」）
│   └── assets/               # 流程图等
├── legacy/matlab/            # 原 MATLAB 代码，冻结
└── references/               # 第三方资料（不进 git，见 4.2）
    └── README.md             # 下载链接 + 用途说明
```

---

## 4. 文件处置清单

### 4.1 自有代码

| 原位置 | 处置 |
|---|---|
| `matlab/2demo/*.m`、`matlab/5demo/*.m` | → `legacy/matlab/`，冻结；作为 Python 版的对照基准 |
| `matlab/2demo/reference_serial_version/` | 删除（被现行版本取代，git 历史可查） |
| `*.png` `*.mat` `*.ps` `verification*.txt` | 删除并加入 `.gitignore`；需要的对照数值转成测试用例 |
| `5demo/光学参数文献_原说明.md` | → `docs/optical_parameters.md`，参数值同步进 `presets/*.yaml` |
| `Monte_Carlo流程图.png`、简介 PDF | → `docs/assets/`，并写成 `docs/algorithm.md` |
| `head/D3D.m` | → `legacy/matlab/head/`（头部模型，后续可做第三个预设） |

### 4.2 第三方与大文件

| 原位置 | 处置 | 理由 |
|---|---|---|
| `MCML_MCX_MMC_开源代码压缩包.zip` | 删除 | 与目录完全重复 |
| `MCXStudio-win64-v2025.10/` + `.zip` | 删除，README 留官方下载链接 | 安装包和 exe 不该进源码库 |
| `MCX/` `MMC/` `MCML/` | 移出 git，README 写明上游仓库与版本 | 上游在 GitHub 持续维护，fork 无意义 |
| `论文.zip`、`Parameter_paper*.pdf/zip` | 移到团队网盘，`references/README.md` 列出文献清单 + 链接 | 压缩包不可检索；数据集太大 |
| `knee-2016-09/`、`head/head_atlas_3d.html` | 移到网盘，保留链接 | 当前仿真未使用 |

> **执行情况（2026-11-07）：** 第三方资料和大文件已移出 git，暂存在本地 `references/`（清单见 `references/README.md`），共享盘链接待补。
>
> **说明：** 以上只在新分支上整理，git 历史中的旧文件仍在。如需真正缩小仓库体积（历史 385 MB），需另行用 `git filter-repo` 改写历史，属于不可逆操作，须团队确认后单独执行。

### 4.3 新增 `.gitignore`

已执行；实际内容以仓库根目录的 `.gitignore` 为准，下面是初稿。

```gitignore
# 仿真结果
*.mat
results/
outputs/
# 大文件 / 二进制
*.zip
*.exe
*.dll
references/*
!references/README.md
# 环境
.venv/
__pycache__/
.ipynb_checkpoints/
*.asv
*.bak
```

---

## 5. 代码映射：MATLAB → Python

| MATLAB 文件 | Python 位置 | 调整要点 |
|---|---|---|
| `Tissue.m` / `Tissue_knee.m` | `geometry/skin.py` / `geometry/knee.py` | 只返回体素数组，不画图；参数来自 YAML |
| `Tissue _optical_parameters.m` | `presets/*.yaml` + `optics.py` | 参数表化，强制每项带 `source` 字段 |
| `Light_T.m` + `Configure_ObliqueSource.m` | `source.py` | 合并；「从空气发射」变成 `launch_from_air: true` |
| `MC_Settings.m` | 配置数据类（dataclass / pydantic） | 类型校验替代 `validateattributes` |
| `Prepare_Inputs.m` | `runner.build_simulation()` | 去掉 `run` / `eval`，显式传参 |
| `Step4_Launch` `Step5_Hop` `Step6_Boundary` `Step6_AirTrack` `Step7_Drop` `Step8_SpinCheck` | `kernel.py` | 合并两个 demo 的差异为开关；Numba 编译 |
| `MC_RunBatch(es)` `MC_CreateTallies` `MC_MergeTallies` | `runner.py` | 多进程 + `numpy.random.SeedSequence` 独立子流 |
| `Step9_Output` `AddIncidentAirBeam` | `results.py` | 能量收支检查保留，失败时报错 |
| `Step10_Plot` `Plot_Tissue3D` `PlotIncidentAirBeam` | `plotting.py` | Plotly，可交互缩放、悬停读数 |
| `main.m` 后半段、`total.m`、`total2.m`、`Compare_SpotSize*.m` | `analysis.py` | 中心轴剂量、圆面平均剂量、光斑大小对比做成函数 |
| `test.m`、`Test_*.m` | `tests/` | 改为 pytest 自动测试 |

---

## 6. 交互界面（Streamlit）

| 区域 | 内容 |
|---|---|
| 侧边栏 | 预设（皮肤 / 膝关节）、波长、光子数、光斑直径、入射角 θ/φ、功率、照射时间 |
| 主区 · 模型 | 组织截面图 + 3D 视图，确认几何正确再跑 |
| 主区 · 结果 | log 光通量截面热图、能量收支表（吸收 / 反射 / 透射 / 侧逃逸 / 镜面） |
| 主区 · 剂量 | 指定深度的中心轴 / 圆面平均累计光注量（J/cm²）曲线 |
| 导出 | 结果 `.npz`、图片、本次运行的完整配置（保证可复现） |

光子数较多时在后台运行并显示进度；相同配置的结果缓存复用。

---

## 7. 验收标准

| 检查 | 通过条件 |
|---|---|
| 能量守恒 | 吸收 + 反射 + 透射 + 侧逃逸 + 镜面 + 轮盘修正 = 1（误差 < 1e-8） |
| 物理极限 | 无散射介质 → 吸收符合 Beer–Lambert；折射率匹配 → 无边界反射 |
| MATLAB 对比 | 同一预设、同光子数下，R / A / T 与 `legacy/` 结果在 3σ 统计误差内一致 |
| 可复现 | 同种子运行两次结果逐位相同；串行与并行结果一致 |
| 性能 | 10⁵ 光子（皮肤预设）在笔记本上 < 1 分钟 |
| 上手 | 新人按 README 从 clone 到出图 ≤ 5 分钟 |

---

## 8. 执行计划与协作约定

| 阶段 | 内容 | 产出 |
|---|---|---|
| 1. 整理仓库 ✓ | 按第 4 节搬移/删除文件，加 `.gitignore`、README 骨架 | 已完成 2026-11-07：git 跟踪 72 个文件、2.4 MB；第三方资料在本地 `references/`，运行产物在本地 `outputs/` |
| 2. 搭骨架 ✓ | `pyproject.toml`、包结构、配置格式、预设 YAML | 已完成：`mcsim/`、`presets/`，uv 管理依赖 |
| 3. 移植内核 ✓ | `kernel.py` + `runner.py` + `results.py`，先跑通皮肤预设 | 已完成：能量误差 < 10⁻⁸，单线程与并行逐位相同 |
| 4. 对比验证 ✓ | 在 MATLAB 侧跑固定参数基准，写入测试 | 已完成：用现有 2,000 光子结果，全部在 3σ 内；建议补跑 10 万光子（见 `docs/algorithm.md` 第 7 节） |
| 5. 膝关节 + 剂量 ✓ | 膝关节预设、`analysis.py` | 已完成：中心轴、圆面平均、圆面能量三种算法与 `main.m` 定义一致；无 MATLAB 数值基准可对 |
| 6. 交互界面 ✓ | Streamlit 应用 | 已完成：`uv run streamlit run app/streamlit_app.py` |
| 7. 文档 ✓ | README、`algorithm.md`、`optical_parameters.md` | 已完成：根目录 README 有 5 分钟上手步骤 |

**协作约定**

- 长期分支：`refactor/python-interactive`；每阶段一个 PR 合入，便于评审。
- commit 信息格式：`类型: 做了什么`（`chore` 整理 / `feat` 新功能 / `fix` 修复 / `test` 测试 / `docs` 文档）。
- 改光学参数必须同时更新出处；改内核必须跑通全部测试。
- `legacy/` 只读；发现原代码有 bug，在 `docs/` 记录，不改原文件。

---

## 9. 通用模板：科研原型代码重构清单

可直接复制到其他项目使用。

**盘点**
- [ ] 按「自有代码 / 第三方 / 数据 / 文献 / 生成物」给每个顶层文件归类，记录体积
- [ ] 找出重复（压缩包与解压目录、多份相似代码、旧版本备份）
- [ ] 列出代码中的硬编码参数、单位、魔法数字

**原则**
- [ ] 一套核心逻辑，差异做成配置
- [ ] 参数与代码分离，每个参数注明出处
- [ ] 计算 / 后处理 / 可视化分层
- [ ] 单位统一，边界换算
- [ ] 用自动测试证明「行为不变」，不靠肉眼对图

**仓库卫生**
- [ ] 不提交：压缩包、安装包、二进制、结果文件、大数据集
- [ ] 第三方代码用链接或子模块，不复制
- [ ] 原版代码冻结到 `legacy/` 作为基准

**交付**
- [ ] README：一条命令安装、一条命令运行
- [ ] 验收标准写成可执行测试
- [ ] 分阶段提交，每阶段可运行、可评审

---

## 10. 待确认事项

| 事项 | 本文默认方案 | 备选 |
|---|---|---|
| 第三方资料去向 | 移出 git，网盘 + 链接 | 保留在 `references/` 但不再新增 |
| 是否改写 git 历史以缩小体积 | 暂不改写 | `git filter-repo` 清理（不可逆，需全员重新 clone） |
| 交互形式 | Streamlit | Jupyter + ipywidgets，或两者都做 |
| 首个移植目标 | 皮肤（简单，便于校验）→ 膝关节 | 直接膝关节 |
| 是否接入 MCX（GPU） | 第二期评估 | 用 `pmcx` 作为高性能后端 |
