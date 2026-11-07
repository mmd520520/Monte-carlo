# tests：自动测试

> 证明“物理没变”：能量守恒、物理极限、可复现、和 MATLAB 结果对比。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 35 个测试全部通过，约 11 秒 | 光学实习生 | 2026-11-07 |

## 里面有什么

| 文件 | 检查什么 |
|---|---|
| `test_config.py` | 预设读取、cm→mm 换算、参数校验 |
| `test_geometry.py` | 模型的层数、体素数与 MATLAB 一致 |
| `test_energy.py` | 能量收支误差 < 10⁻⁸（皮肤、斜入射、膝关节） |
| `test_physics.py` | 比尔–朗伯定律、无吸收、Fresnel 反射 |
| `test_reproducibility.py` | 同种子同结果；单线程与并行逐位相同 |
| `test_matlab_parity.py` | 与 MATLAB 粗网格结果在 3σ 内一致 |
| `test_analysis.py` | 剂量计算的定义和边界情况 |
| `test_app.py` | 交互界面无头运行两个预设 |
| `data/` | MATLAB 基准数值 |

## 怎么用

```bash
uv run pytest            # 全部
uv run pytest -m "not slow"   # 跳过界面测试
```

## 更新记录

- 2026-11-07：建立。

## 给 AI 的说明

- 测试失败时先看是不是物理变了，不要为了通过而放宽阈值。
