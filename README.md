# Monte Carlo 光传输仿真

> 用蒙特卡洛（MC）方法模拟光在人体组织里怎么走、在哪里被吸收，回答“光能到多深、剂量多大”。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 阶段 1（整理仓库）已完成；阶段 2（Python 骨架）待开始。分支 `refactor/python-interactive` | 光学实习生（GitHub: mmd520520）、Eden Huang（审阅） | 2026-11-07 |

## 先看这三样

1. **重构指南**：[docs/REFACTOR_GUIDE.md](docs/REFACTOR_GUIDE.md)。仓库现状、10 条原则、目标结构、分阶段计划。给不看代码的同事准备了网页版（见 [docs/README.md](docs/README.md)）。
2. **能跑的代码**：目前是 MATLAB 版，冻结在 [legacy/matlab/](legacy/matlab/README.md)。Python 版按指南第 8 节分阶段迁移。
3. **第三方资料清单**：[references/README.md](references/README.md)。开源程序、论文和数据集的版本、许可和下载地址；文件本身只在本地。

## 目录地图

| 文件夹 | 是什么 | 在 git 里吗 |
|---|---|---|
| [docs/](docs/README.md) | 重构指南（含网页版）、参数说明、流程图 | 是 |
| [legacy/](legacy/README.md) | 冻结的 MATLAB 原型：皮肤（2demo）、膝关节（5demo）、头部图谱可视化（head） | 是，只读 |
| [references/](references/README.md) | 第三方资料：MCX、MMC、MCML、安装包、论文、数据集、解剖图谱 | 只有 README；文件在本地 |
| `outputs/` | 运行产物：结果图、`.mat` 数据、核验记录 | 否，只在本地 |
| `slides/` | 分享 PPT；含个人信息和内部材料 | 否，只在本地（`.git/info/exclude`） |
| 规划中：`mcsim/` `presets/` `app/` `tests/` | Python 仿真包、参数预设、交互界面、自动测试 | 阶段 2 起 |

## 写作约定（这个仓库也是 AI 时代写作方式的示范）

- **每个文件夹都有 README.md**，用同一个结构：
  1. 一句话说明这里是什么
  2. 状态 / 负责人 / 最后更新
  3. 里面有什么（文件表）
  4. 怎么用
  5. 更新记录
  6. 给 AI 的说明：哪些是权威来源、哪些不要改、改了要同步哪里
- **先写文档，再动代码。** 大改动先在 `docs/` 写方案，看过再做。
- **AI 起草，人来核对。** 物理结果对不对，靠测试和与 MATLAB 结果对比来判断，不靠肉眼。
- **【】表示待填。** 文档和 PPT 里凡是带【】的，都是还没确认的内容。
- **文件命名**：`日期_主题_作者_版本`，例如 `20261107_蒙特卡洛阶段分享_框架_v1.pptx`；定稿加 `_定稿`。

## 给 AI 的说明

- 项目全貌以 `docs/REFACTOR_GUIDE.md` 为准；本文件只做导航，两者冲突时改本文件。
- 新增文件夹时同步更新上面的“目录地图”，并在新文件夹里按约定写 README.md。
- 仓库是**公开**的：个人信息、未公开的数据和内部材料一律只放本地（`slides/` 已通过 `.git/info/exclude` 忽略），不要提交。
- `references/`、`outputs/` 已被 `.gitignore` 忽略；第三方文件和运行产物不要提交。
