# Monte Carlo 光传输仿真

> 用蒙特卡洛（MC）方法模拟光在人体组织里怎么走、在哪里被吸收，回答“光能到多深、剂量多大”。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| Python 版和交互界面可用（阶段 1–7 完成）；45 个测试通过，物理结果已与独立方法（加倍法）核对，不需要 MATLAB。分支 `refactor/python-interactive` | 马孟帝（光学研究员，GitHub: mmd520520）、Eden Huang（审阅） | 2026-11-07 |

## 5 分钟上手

需要 [uv](https://docs.astral.sh/uv/)（Python 环境管理工具，Mac 上 `brew install uv`）。

```bash
uv sync                                       # 安装依赖（第一次约 1 分钟）
uv run streamlit run app/streamlit_app.py     # 打开交互界面：http://localhost:8501（右上角切换中文 / EN）
uv run mcsim run knee_980nm --dose 10 20 40   # 命令行：跑膝关节模型并打印剂量表
uv run pytest                                 # 跑全部测试
```

## 先看这几样

1. **重构指南**：[project/public/REFACTOR_GUIDE.md](project/public/REFACTOR_GUIDE.md)。仓库现状、10 条原则、目标结构、分阶段计划。给不看代码的同事准备了网页版（见 [project/public/README.md](project/public/README.md)）。
2. **算法和验证结果**：[docs/algorithm.md](docs/algorithm.md)。每一步对应哪段代码、和 MATLAB 怎么对比的、还有哪些没确认。
3. **协作教程**：[tutorial/README.md](tutorial/README.md)。这个项目怎么从散落的文件变成团队能用的工具，以及新项目怎么从第一天就这样做。
4. **第三方资料清单**：[references/README.md](references/README.md)。开源程序、论文和数据集的版本、许可和下载地址；文件本身只在本地。

## 目录地图

| 文件夹 | 是什么 | 在 git 里吗 |
|---|---|---|
| [docs/](docs/README.md) | 技术文档：算法说明、参数说明、流程图 | 是 |
| [project/](project/README.md) | 项目资料。`public/`：重构指南（含网页版）等可公开的；`private/`：敏感材料，只放企业微信微盘 | `public/` 是；`private/` 否 |
| [legacy/](legacy/README.md) | 冻结的 MATLAB 原型：皮肤（2demo）、膝关节（5demo）、头部图谱可视化（head） | 是，只读 |
| [references/](references/README.md) | 第三方资料：MCX、MMC、MCML、安装包、论文、数据集、解剖图谱 | 只有 README；文件在本地 |
| `outputs/` | 运行产物：结果图、`.mat` 数据、核验记录 | 否，只在本地 |
| [mcsim/](mcsim/README.md) | Python 仿真包：几何、内核、并行、结果、剂量、画图 | 是 |
| [presets/](presets/README.md) | 参数预设（皮肤 500 nm、膝关节 980 nm），每个数字带出处 | 是 |
| [app/](app/README.md) | Streamlit 交互界面，中英双语 | 是 |
| [tests/](tests/README.md) | 自动测试：能量守恒、物理极限、与独立方法（加倍法）对比、可复现、MATLAB 对比、界面 | 是 |
| [tools/](tools/README.md) | 一次性脚本：提取 MATLAB 基准；推送保护 | 是 |
| [tutorial/](tutorial/README.md) | AI 时代的研发协作教程，以这个项目为例：分工、git、文档、隐私、分享、新项目模板 | 是 |
| `AGENTS.md` | 给 AI 编程工具（Cursor、Claude Code 等）的总说明 | 是 |

## 写作约定（这个仓库也是 AI 时代写作方式的示范）

- **每个文件夹都有 README.md**，用同一个结构：
  1. 一句话说明这里是什么
  2. 状态 / 负责人 / 最后更新
  3. 里面有什么（文件表）
  4. 怎么用
  5. 更新记录
  6. 给 AI 的说明：哪些是权威来源、哪些不要改、改了要同步哪里
- **先写文档，再动代码。** 大改动先在 `docs/` 写方案，看过再做。
- **AI 起草，人来核对。** 物理结果对不对，靠测试判断（和独立的加倍法、和 MATLAB 原版对比），不靠肉眼。
- **【】表示待填。** 文档和 PPT 里凡是带【】的，都是还没确认的内容。
- **文件命名**：`日期_主题_作者_版本`，例如 `20261107_蒙特卡洛阶段分享_框架_v1.pptx`；定稿加 `_定稿`。

## 给 AI 的说明

- 项目全貌以 `project/public/REFACTOR_GUIDE.md` 为准；本文件只做导航，两者冲突时改本文件。
- 新增文件夹时同步更新上面的“目录地图”，并在新文件夹里按约定写 README.md。
- 仓库是**公开**的：个人信息、未公开的数据和内部材料不进 git。敏感材料放 `project/private/`（只放企业微信微盘，几个人共享），第三方资料放 `references/`，运行产物放 `outputs/`，三者都已被 `.gitignore` 忽略。
- 不要 `git add -f` 这三个文件夹。推送保护钩子 `tools/pre-push` 会拦住含它们的提交推到公开仓库，安装方法见 [tools/README.md](tools/README.md)。
