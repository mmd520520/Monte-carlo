# legacy：冻结的旧代码

> 原型阶段的 MATLAB 代码，作为 Python 新版的对照基准，只读。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 冻结（2026-11-07 起） | 马孟帝 | 2026-11-07 |

## 里面有什么

| 文件夹 | 内容 |
|---|---|
| [matlab/](matlab/README.md) | 皮肤（2demo）、膝关节（5demo）两个 MATLAB 模型，头部图谱可视化（head） |

## 规则

- 不改这里的代码。发现问题记到 `docs/`，在 Python 版里修。
- 在这里运行 MATLAB 产生的图片和数据会被 `.gitignore` 忽略；需要保留的放到本地 `outputs/`。

## 更新记录

- 2026-11-07：从仓库根目录的 `matlab/`、`head/` 移入；运行产物移到本地 `outputs/legacy_matlab/`；旧的串行版本删除（git 历史可查）。

## 给 AI 的说明

- Python 版结果与这里不一致时，先怀疑 Python 版。
