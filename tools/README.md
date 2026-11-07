# tools：一次性脚本

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 1 个脚本 | 光学实习生 | 2026-11-07 |

## 里面有什么

| 文件 | 作用 |
|---|---|
| `extract_matlab_baseline.py` | 从 MATLAB 结果文件提取基准数值到 `tests/data/matlab_skin_smoke.json` |

## 怎么用

1. 在 MATLAB 里运行 `Step4_Main(100000, true, 1, true)`（`legacy/matlab/2demo` 目录下），得到 `mc_smoke_results.mat`。
2. 把它放到本地 `outputs/legacy_matlab/2demo/`。
3. 运行 `uv run --with h5py python tools/extract_matlab_baseline.py`，再跑 `uv run pytest tests/test_matlab_parity.py`。

## 给 AI 的说明

- 这里的脚本不进主程序，只用于准备数据。
