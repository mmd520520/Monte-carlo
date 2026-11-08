# mcsim：Python 仿真包

> 体素蒙特卡洛光传输引擎：读预设、建模型、跑光子、出结果、算剂量、画图。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 可用；35 个测试通过 | 马孟帝、Eden Huang | 2026-11-07 |

## 里面有什么

| 文件 | 作用 |
|---|---|
| `config.py` | 读 `presets/*.yaml`，换算成 mm，校验参数 |
| `geometry/` | 组织模型：皮肤、膝关节、测试用平板 |
| `optics.py` | 按标签整理 μa、μs、g、n |
| `source.py` | 光源：斜入射、Snell 折射、Fresnel 镜面反射 |
| `kernel.py` | 光子传输内核（Numba 编译），逐步对应 MATLAB 的 Step4–Step8 |
| `runner.py` | 分批、并行、随机种子、按顺序合并 |
| `results.py` | 归一化、能量收支检查、保存 `.npz` |
| `analysis.py` | 剂量：中心轴、圆面平均、圆面能量 |
| `plotting.py` | Plotly 图 |
| `cli.py` | 命令行 `mcsim` |

## 怎么用

```python
from mcsim import load_preset, simulate
from mcsim.analysis import dose_table

preset = load_preset("knee_980nm", photons=50_000)
result = simulate(preset, workers=0)          # 0 = 用全部 CPU 核
print(result.summary())
rows = dose_table(result, depths_mm=[10, 20, 40], exposure_s=300, disk_radius_mm=10)
```

命令行：`uv run mcsim run knee_980nm --photons 50000 --dose 10 20 40`

## 更新记录

- 2026-11-07：从 MATLAB 移植（阶段 2–6）。

## 给 AI 的说明

- 内部单位一律 mm；换算只在 `config.py`（输入）和 `analysis.py`、`plotting.py`（输出）里做。
- 改 `kernel.py` 后必须跑 `uv run pytest`，并同步 `docs/algorithm.md`。
- 结果要与 `legacy/matlab/` 在统计误差内一致；不一致先怀疑这里。
