# legacy/matlab：MATLAB 原型代码

> 实习生写的蒙特卡洛光传输原型。两个示例共用同一套算法，只是几何、参数和光源不同。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 冻结，作为 Python 版的对照基准；代码可运行 | 光学实习生 | 2026-11-07 |

## 里面有什么

| 文件夹 | 模型 | 波长 | 单位 | 体素 |
|---|---|---|---|---|
| [2demo/](2demo/README.md) | 皮肤：空气 / 表皮 / 真皮 / 一根血管 | 500 nm | mm | 400³，10 μm |
| [5demo/](5demo/README.md) | 膝关节：空气 / 软组织 / 髌骨 / 骨，含剂量分析 | 980 nm | cm | 160×96×168，1.25 mm |
| [head/](head/README.md) | 头部图谱三维可视化（尚未接入仿真） | — | — | — |

## 算法（两个示例相同）

`main` → `Step4_Main` → 准备输入（几何、光学参数、光源）→ 分批并行运行：
发射 `Step4_Launch` → 走一段 `Step5_Hop` + 吸收 `Step7_Drop`（遇边界 `Step6_Boundary`）→ 散射与轮盘赌 `Step8_SpinCheck` → 循环 → 汇总 `Step9_Output`（含能量守恒自检）→ 出图 `Step10_Plot`。

## 怎么用

需要 MATLAB；有 Parallel Computing Toolbox 可并行，没有就在 `main.m` 里设 `options.useParallel = false`。进入任一 demo 文件夹，运行 `main`。结果图会写在 demo 文件夹里，已被 `.gitignore` 忽略。

## 已知问题（在 Python 版里处理，原文件不改）

- 两个 demo 是复制后分别修改的，差异见 `docs/REFACTOR_GUIDE.md` 1.2 节。
- `5demo/MC_RunBatch.m` 有调试输出 `fprintf("11111111111 用到了")`。
- 膝关节光源参数前后不一致，见 `5demo/README.md`。

## 更新记录

- 2026-11-06：最后一次修改（膝关节光源参数）。
- 2026-11-07：从根目录 `matlab/` 移到 `legacy/matlab/`；结果图、`.mat`、`.ps`、核验记录移到本地 `outputs/legacy_matlab/`。

## 给 AI 的说明

- 这里是物理行为的基准。Python 版的结果要和这里在统计误差内一致，不一致时先怀疑 Python 版。
- 不要修改这里的 `.m` 文件；发现 bug 记到 `docs/`。
