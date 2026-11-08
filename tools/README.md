# tools：一次性脚本

| 状态 | 负责人 | 最后更新 |
|---|---|---|
| 3 个脚本 | 马孟帝、Eden Huang | 2026-11-07 |

## 里面有什么

| 文件 | 作用 |
|---|---|
| `extract_matlab_baseline.py` | 从 MATLAB 结果文件提取基准数值到 `tests/data/matlab_skin_smoke.json` |
| `pre-push` | 推送保护：不让内部材料、第三方文件和运行产物推到公开仓库 |
| `sync_private.sh` | 可选：把当前代码 + `internal/`、`references/`、`outputs/` 备份到私有仓库的 `private/full` 分支 |

## 提取 MATLAB 基准（可选）

物理是否正确已由 `tests/test_reference.py` 与加倍法独立核对，不需要 MATLAB。下面几步只用于确认 Python 版与 MATLAB 原版逐项一致。

1. 在 MATLAB 里运行 `Step4_Main(100000, true, 1, true)`（`legacy/matlab/2demo` 目录下），得到 `mc_smoke_results.mat`。
2. 把它放到本地 `outputs/legacy_matlab/2demo/`。
3. 运行 `uv run --with h5py python tools/extract_matlab_baseline.py`，再跑 `uv run pytest tests/test_matlab_parity.py`。

## 推送保护（每台电脑装一次）

```bash
cp tools/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push
```

装好后，推送前会检查两件事，任何一条不满足就整个推送取消：

- 要推上去的每个提交（不只是最新的）里都没有 `internal/`、`slides/`、`outputs/`，`references/` 里只有 `README.md`。
- 不推 `private/*` 分支。

只有登记过的私有远程不受限制：`git config mcsim.privateRemotes "远程名"`。

## 私有备份（可选）

内部材料正式存放在企业微信网盘。有私有仓库的，可以再留一份带版本的备份：

```bash
tools/sync_private.sh [远程名，默认 mine]
```

它把当前代码和三个本地文件夹做成快照，放在 `private/full` 分支并推送；工作区、暂存区和当前分支都不动。第一次推到某个远程时会先确认它是私有仓库（GitHub 不登录访问返回 404），非 GitHub 的远程要先手动登记。新电脑从备份取回文件：

```bash
git fetch mine private/full && git archive mine/private/full internal references outputs | tar -x
```

## 给 AI 的说明

- 这里的脚本不进主程序，只用于准备数据和管理仓库。
- 不要把 `private/full` 合并进代码分支，也不要在代码分支上 `git add -f` 那三个文件夹。
- 快照是本地文件夹的镜像：本地删掉的文件，下一次快照里也会删掉。三个文件夹缺任何一个时，脚本会停止。
