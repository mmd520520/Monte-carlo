# tests/data：基准数据

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 1 个 MATLAB 基准 | 光学实习生 | 2026-11-07 |

## 里面有什么

| 文件 | 说明 |
|---|---|
| `matlab_skin_smoke.json` | MATLAB 皮肤模型粗网格结果（40³ 体素、0.1 mm、2,000 光子、种子 1、垂直入射）：各项能量、各组织吸收、逐层吸收 |

由 `tools/extract_matlab_baseline.py` 从本地 `outputs/legacy_matlab/2demo/mc_smoke_results.mat` 生成。

## 给 AI 的说明

- 不要手改这里的数字；需要更新时重新运行提取脚本。
