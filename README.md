# Monte Carlo 光传输仿真

> 用蒙特卡洛（MC）方法模拟光在人体组织里怎么走、在哪里被吸收，回答“光能到多深、剂量多大”。

> **主仓库在腾讯工蜂**：`git.code.tencent.com/joulez/monte-carlo`（私有，找负责人开权限）。2026-11-09 起只在工蜂上更新。GitHub 上的 `mmd520520/Monte-carlo` 保留之前的历史，不再更新。

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| Python 版和交互界面可用，并已部署成在线版（见下）；57 个测试通过，物理结果已与独立方法（加倍法）核对，不需要 MATLAB。主分支 `main`；原来的仓库内容保留在 `legacy` 分支；主仓库在腾讯工蜂 | 马孟帝（光学研究员，GitHub: mmd520520）、Eden Huang（审阅） | 2026-11-09 |

## 在线版：打开网页就能用

交互界面已经部署在公司的服务器上，团队成员用浏览器打开就能用，手机也可以，不用装任何东西。**网址和密码不写在这里**（GitHub 上的旧版本是公开的），向负责人要。

### 大家一起用时要知道的事

在线版是**一台服务器、一个共用密码、大家共用**。浏览可以同时进行，**计算要排队**。下面的速度是 2026-11-08 在服务器上实测的。

| 情况 | 实际是怎样 | 怎么办 |
|---|---|---|
| 多人同时打开 | 没问题：浏览、看图、切换语言互不影响 | — |
| 多人同时点“运行” | 整台服务器**同一时间只算一个仿真**，其他人排队；排队超过 60 秒会提示“服务器忙” | 过一会儿再点。10⁵ 个光子以内几秒钟就算完，很少撞上 |
| 大计算会挡住所有人 | 仿真在服务器上只用 2 个 CPU 线程。实测膝关节 1.25 mm 网格 2×10⁵ 个光子用 10.8 秒；按这个速度推算，10⁶ 约 1 分钟，10⁷ 约 9 分钟，10⁸ 约 1.5 小时。这段时间里别人都算不了 | **10⁶ 以上在自己电脑上跑**（见下面“5 分钟上手”）。一定要在服务器上跑，先在群里说一声 |
| 关掉网页 | 已经开始的计算不会马上停，会继续占着服务器 | 先用小光子数试，确认设置对了再加大 |
| 参数完全相同 | 参数和随机种子都一样时，直接显示最近一次的结果（同参数同种子，结果逐位相同），不占服务器 | 想重新算，换一个随机种子 |
| 下载 3D 结果 | 服务器带宽小（3 Mbps，和公司其他服务共用）。导出的数据文件实测：膝关节 1.25 mm 约 7 MB，皮肤 20 μm 约 51 MB（下载 2 分钟以上）；光子越多文件越大。下载时整台服务器的网络都会变慢 | 要完整的 3D 数据，在自己电脑上跑。在线版用来看图和剂量表 |
| 服务器更新 | 更新时应用会重启约 20 秒：正在用的人会断开，正在跑的计算会丢 | 更新前在群里说一声，避开别人正在用的时候 |
| 共用一个密码 | 大家用同一个用户名和密码，看不出谁在用，也不能单独取消某个人 | 只发给需要的人；有人离开团队就换密码 |

**和本地版的区别**：在线版隐藏了最细的皮肤网格（10 μm，一次要 2.5–3 GB 内存），只保留最近 2 份结果，计算设成低优先级，让同一台服务器上的其他服务先用 CPU。本地版没有这些限制。

### 怎么更新在线版

代码合并进工蜂的 `main` 分支后，服务器**不会自动更新**：

1. 推之前在本地跑通 `uv run pytest`。
2. 在群里说一声“几点更新在线版”。
3. 由有服务器权限的人在服务器上拉取新代码、重启应用（具体步骤在私有部署说明 `project/private/deploy/`，不在这个仓库里）。
4. 打开网页确认能用。

## 5 分钟上手

第一次用工蜂：用微信扫码登录 git.code.tencent.com，在「账号初始化」里设好 Git 用户名，再加一把 SSH 密钥。**工蜂只认 RSA 密钥**，而且服务器用的是老式的 `ssh-rsa` 算法，新版 Mac 默认不接受。在 `~/.ssh/config` 里加上这一段：

```
Host git.code.tencent.com
  IdentityFile ~/.ssh/id_rsa_gongfeng
  IdentitiesOnly yes
  HostKeyAlgorithms +ssh-rsa
  PubkeyAcceptedAlgorithms +ssh-rsa
```

（密钥用 `ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_gongfeng` 生成，把 `.pub` 文件的内容贴到工蜂「个人设置 → SSH 密钥」。）然后：

```bash
git clone git@git.code.tencent.com:joulez/monte-carlo.git
cd monte-carlo
```

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
| [app/](app/README.md) | 交互界面，中英双语：科普（论文、仿真、验证）+ 产品（从研发到产品、Muse 案例、脑环闭环设计、康复激光） | 是 |
| [tests/](tests/README.md) | 自动测试：能量守恒、物理极限、与独立方法（加倍法）对比、可复现、MATLAB 对比、界面 | 是 |
| [tools/](tools/README.md) | 一次性脚本：提取 MATLAB 基准；推送保护 | 是 |
| [tutorial/](tutorial/README.md) | AI 时代的研发协作教程，以这个项目为例：分工、git、文档、隐私、分享、新项目模板 | 是 |
| `AGENTS.md` | 给 AI 编程工具（Cursor、Claude Code 等）的总说明 | 是 |

## 协作约定（这个仓库也是 AI 时代协作方式的示范）

核心是两件事：**用 git 管住每一次改动**，**用固定的习惯管项目**。人和 AI 都按同一套规矩做，谁接手都能看懂。

**用 git 管改动**

- **`main` 永远能用，不直接往上推。** 做一件事就从 `main` 新建一个分支（例如 `feature/head-model`、`fix/dose-table`），做完在工蜂上发合并请求（MR，GitHub 上叫 PR）。`uv run pytest` 全部通过、至少一个人看过，再合进 `main`。
- **一次提交只做一件事。** 提交说明写 `类型: 做了什么`（feat / fix / docs / test / chore），下面写为什么。半年后翻历史，每一步都看得懂。
- **分支各有用途。** `main` 是当前版本；`legacy` 是 2026-11-08 之前的原始仓库（MATLAB 时期），只读、原样保留。Python 重构在 `refactor/python-interactive` 分支上完成，2026-11-08 变成了 `main`。
- **敏感材料不进 git。** 个人信息和内部材料放企业微信微盘；推送保护钩子 `tools/pre-push` 会拦住误推（见下面“给 AI 的说明”）。

**用固定的习惯管项目**

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
- 主仓库在工蜂（私有），但 2026-11-09 之前的历史在 GitHub 上公开；而且按约定，敏感材料只放企业微信微盘：个人信息、未公开的数据和内部材料不进 git。敏感材料放 `project/private/`（只放企业微信微盘，几个人共享），第三方资料放 `references/`，运行产物放 `outputs/`，三者都已被 `.gitignore` 忽略。
- 不要 `git add -f` 这三个文件夹。推送保护钩子 `tools/pre-push` 会拦住含它们的提交推到任何没登记的远程（包括工蜂和 GitHub），安装方法见 [tools/README.md](tools/README.md)。
