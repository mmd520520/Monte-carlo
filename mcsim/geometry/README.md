# mcsim/geometry：组织模型

> 把预设里的几何参数变成体素标签数组（`Volume`）。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 可用 | 光学实习生 | 2026-11-07 |

## 里面有什么

| 文件 | 模型 | 对应 MATLAB |
|---|---|---|
| `__init__.py` | `Volume`（标签、体素尺寸、坐标）、`build_volume` 分派、MATLAB 式四舍五入、抽稀 | — |
| `skin.py` | 空气 / 表皮 / 真皮 / 血管 | `2demo/Tissue.m`（逐体素一致，已对照验证） |
| `knee.py` | 空气 / 软组织 / 髌骨 / 骨 | `5demo/Tissue_knee.m` |
| `slab.py` | 空气下的均匀平板 | 无，测试专用 |

## 怎么加一个新模型

1. 写 `xxx.py`，提供 `build_xxx(geometry: dict) -> Volume`，单位 mm。
2. 在 `__init__.py` 的 `build_volume` 里登记 `type: xxx`。
3. 在 `presets/` 写对应 YAML，并在 `tests/test_geometry.py` 加检查。

## 更新记录

- 2026-11-07：建立。

## 给 AI 的说明

- 标签 1 必须是空气。几何坐标约定见 `__init__.py` 文件头。
