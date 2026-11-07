# 2demo：皮肤血管模型（500 nm）

> 空气 / 表皮 / 真皮 + 一根直径 1 mm 的血管，看可见光在皮肤里怎么分布、血管怎么“挡光”。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 可运行（并行版） | 光学实习生 | 2026-11 |

## 里面有什么

| 文件 | 作用 |
|---|---|
| `main.m` | 入口：光子数、并行设置、入射角 |
| `Tissue.m`、`Tissue _optical_parameters.m`、`Light_T.m` | 几何、光学参数、光源（文件名里有空格，被 `eval` 读取） |
| `Step4_*` – `Step10_*`、`MC_*` | 算法各步骤和分批并行 |
| `README.txt`、`README_parallel.txt` | 原作者写的说明 |
| `reference_serial_version/` | 旧的串行版本，已被取代，重构时删除 |
| `fluence_section*.png`、`mc_smoke_results.mat`、`*.ps`、`verification*.txt` | 运行产物，重构时移出 git |

## 怎么用

在 MATLAB 里进入本文件夹，运行 `main`。先用小光子数（如 2000）试跑。

## 更新记录

- 2026-11-07：补 README.md（原有说明见 README.txt）。

## 给 AI 的说明

- 参数的权威来源是 `Tissue _optical_parameters.m`，迁移到 `presets/skin_500nm.yaml` 时逐项核对。
