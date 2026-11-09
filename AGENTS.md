# AGENTS.md：给 AI 编程工具的说明

## 项目是什么

蒙特卡洛光传输仿真：模拟光在皮肤、膝关节等组织里怎么走、到多深、剂量多大。Python 引擎 + 中英双语网页界面。原始 MATLAB 原型在 `legacy/matlab/`（冻结，只作对照）。

## 怎么运行和测试

```bash
uv sync                                     # 安装依赖
uv run pytest                               # 全部测试，约 13 秒
uv run streamlit run app/streamlit_app.py   # 网页界面，右上角切换中文 / EN
uv run mcsim run knee_980nm --dose 10 20 40 # 命令行
```

## 目录

`mcsim/` 引擎 · `presets/` 参数预设 · `app/` 界面（科普 + 产品两部分，页面在 `app/views/`，长文字在 `app/content/`）· `tests/` 测试 · `docs/` 技术文档 · `project/` 项目资料（`public/` 进 git，`private/` 不进）· `legacy/` 原 MATLAB · `tools/` 脚本 · `tutorial/` 协作教程。各文件夹的 README.md 有详细说明。

## 仓库在哪

- 主仓库：腾讯工蜂 `git@git.code.tencent.com:joulez/monte-carlo.git`（私有，远程名 `origin`）。2026-11-09 起只在工蜂上更新。
- GitHub `mmd520520/Monte-carlo`（远程名 `github`）是之前的公开版本，不再推送。
- 工蜂只认 RSA 密钥、老式 `ssh-rsa` 算法，配置见根目录 README 的“5 分钟上手”。

## 约定

- 先读根目录 README.md 和相关文件夹的 README.md，再动手；遵守各 README 的“给 AI 的说明”。
- 改物理内核必须跑通全部测试；改光学参数必须同时写出处（`source` 和 `source_en`）。
- 界面文字：短的放 `mcsim/i18n.py`，长的放 `app/content/`，都要中英各一份。
- 产品部分只用公开信息。网站有访问密码，工蜂仓库也是私有的，但 GitHub 上的旧版本公开过，而且这类页面以后可能对外：页面上的“我们目前的问题”（`app/content/open_questions_*`）只写高层次的问题，不写人名、会议、内部代号和具体数据。
- 分支：`main` 永远能用，不直接推；新功能从 `main` 建分支（`feature/…`、`fix/…`），在工蜂上发合并请求（MR），测试通过、有人看过再合并。`legacy` 是 2026-11-08 之前的原始仓库，只读。
- 提交说明：`类型: 做了什么`（feat / fix / docs / test / chore），下面写为什么。
- 数字（验证结果、速度、体积）来自实际运行；重测后更新，不要估算。

## 隐私和安全

- 敏感材料只放企业微信微盘。`project/private/`、`rd_medical/`、`references/`、`outputs/` 不进 git（工蜂也不进），内容不能出现在代码、公开文档或提交说明里。判断规则见 `project/README.md`。
- 推送前检查：`tools/pre-push`（安装见 `tools/README.md`），不要绕过。
- 不要把密码、密钥写进任何文件。

## 人员

- 马孟帝：光学研究员（硬件），MATLAB 原型的作者，GitHub mmd520520。不是实习生。
- Eden Huang：负责人、审阅。
- 2026-11-07 的 Python 重构由 Eden Huang 和 Claude 完成。
