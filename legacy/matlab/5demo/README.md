# 5demo：膝关节模型（980 nm）

> 空气 / 软组织 / 髌骨 / 骨，光从空气照到弯曲的膝盖上，算各深度的光注量和累计剂量（J/cm²）。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 冻结，可运行；光源参数待确认 | 马孟帝 | 2026-11-07 |

## 里面有什么

| 文件 | 作用 |
|---|---|
| `main.m` | 入口；后半段是剂量分析（中心轴、圆面平均） |
| `Tissue_knee.m` | 按示意图手绘的膝关节几何，单位 cm |
| `Tissue _optical_parameters.m` | 980 nm 光学参数和文献出处 |
| `Light_T.m` | 光源：光斑、功率、从空气发射 |
| `Compare_SpotSize*.m`、`total*.m` | 光斑大小对比、剂量统计脚本 |
| `Plot_Tissue3D.m` | 三维组织模型查看 |
| `README_简约版.txt` | 原作者写的调用关系说明 |

参数来源说明已移到 [docs/optical_parameters.md](../../../docs/optical_parameters.md)。运行产物（`knee_*_fluence*.png`、光斑对比结果、`deepth/untitled.fig`）在本地 `outputs/legacy_matlab/`，不在 git 里。

## 怎么用

在 MATLAB 里进入本文件夹，运行 `main`。10⁵ 光子耗时较长，先用 10⁴ 试跑。

## 待确认

- 光源参数三处说法不同：`Light_T.m` 是直径 8 cm、20 W；`README_简约版.txt` 是直径 2.5 cm、0.1 W/cm²；`docs/optical_parameters.md` 是直径 2 cm、0.1 W/cm²。
- 髌骨参数借用胫骨测量值；g = 0.9、n = 1.4 是假设值。

## 更新记录

- 2026-11-06：调整光源参数。
- 2026-11-07：移到 `legacy/`；参数说明移到 `docs/`；运行产物移出 git。

## 给 AI 的说明

- 阶段分享 PPT（内部材料，仅本地）里的剂量数字从这里的 `main.m` 算出。参数改了要同步更新那份 PPT。
