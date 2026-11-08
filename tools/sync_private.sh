#!/usr/bin/env bash
# 把当前提交 + 只在本地的文件夹（project/private/ references/ outputs/）做成一个快照，
# 放在 private/full 分支，推送到私有远程仓库。工作区、暂存区和当前分支都不动。
#
# 用法（仓库根目录）：tools/sync_private.sh [远程名，默认 mine]
# 第一次运行会安装 tools/pre-push 钩子：private/* 分支、以及含本地文件夹的提交，
# 只能推到 git config mcsim.privateRemotes 里登记的远程。
set -euo pipefail

REMOTE=${1:-mine}
BRANCH=private/full
PATHS=(project/private references outputs)
cd "$(git rev-parse --show-toplevel)"

# 1. 远程必须是私有的
url=$(git remote get-url "$REMOTE")
allowed=" $(git config --get mcsim.privateRemotes || true) "
if [[ $allowed != *" $REMOTE "* ]]; then
  if [[ $url =~ github\.com[:/]([^/]+)/([^/]+)$ ]]; then
    repo="${BASH_REMATCH[1]}/${BASH_REMATCH[2]%.git}"
    # 不带登录访问 GitHub API：公开仓库返回 200，私有仓库返回 404
    code=$(curl -s -o /dev/null -w '%{http_code}' "https://api.github.com/repos/$repo")
    if [[ $code != 404 ]]; then
      echo "停止：$repo 不是私有仓库（GitHub 返回 $code）" >&2; exit 1
    fi
    git config mcsim.privateRemotes "$(echo $allowed $REMOTE)"
    echo "已确认 $repo 是私有仓库，登记 $REMOTE 为私有远程"
  else
    echo "停止：$REMOTE ($url) 还没登记为私有远程。确认它是私有仓库后运行：" >&2
    echo "  git config mcsim.privateRemotes \"$(echo $allowed $REMOTE)\"" >&2
    exit 1
  fi
fi

# 2. 安装推送保护钩子
hook=$(git rev-parse --git-path hooks)/pre-push
if [[ ! -e $hook ]]; then
  cp tools/pre-push "$hook" && chmod +x "$hook" && echo "已安装推送保护钩子 $hook"
elif ! cmp -s tools/pre-push "$hook"; then
  echo "注意：$hook 已存在且与 tools/pre-push 不同，没有覆盖" >&2
fi

# 3. 本地文件夹必须都在：快照会镜像本地，缺一个就等于在 private/full 里把它删掉
for p in "${PATHS[@]}"; do
  if [[ ! -d $p ]]; then
    echo "停止：本地没有 $p/。新电脑先取回内部材料：" >&2
    echo "  git fetch $REMOTE $BRANCH && git archive $REMOTE/$BRANCH ${PATHS[*]} | tar -x" >&2
    exit 1
  fi
done

# 4. 以远程最新的 private/full 为基础，避免覆盖别人的更新
git fetch -q "$REMOTE" "+refs/heads/$BRANCH:refs/remotes/$REMOTE/$BRANCH" 2>/dev/null || true
prev=$(git rev-parse -q --verify "refs/heads/$BRANCH" || true)
remote_prev=$(git rev-parse -q --verify "refs/remotes/$REMOTE/$BRANCH" || true)
if [[ -n $remote_prev ]]; then
  if [[ -z $prev ]] || git merge-base --is-ancestor "$prev" "$remote_prev"; then
    prev=$remote_prev
  elif ! git merge-base --is-ancestor "$remote_prev" "$prev"; then
    echo "停止：本地和 $REMOTE 上的 $BRANCH 分叉了，先人工确认用哪边" >&2; exit 1
  fi
fi

# 5. 快照：HEAD 的文件 + 本地文件夹（用临时暂存区，不碰真正的暂存区）
export GIT_INDEX_FILE
GIT_INDEX_FILE="$(mktemp -d)/index"
git read-tree HEAD
git add -f -- "${PATHS[@]}" ':(exclude,glob)**/.DS_Store' ':(exclude,glob)**/__pycache__/**'
tree=$(git write-tree)
rm -f "$GIT_INDEX_FILE"; unset GIT_INDEX_FILE

if [[ -n $prev && $(git rev-parse "$prev^{tree}") == "$tree" ]]; then
  commit=$prev
  echo "$BRANCH 已是最新"
else
  # 第一父提交是上一个快照，第二父提交是当前代码（代码没变时省略）
  parents=()
  [[ -n $prev ]] && parents+=(-p "$prev")
  if [[ -z $prev ]] || ! git merge-base --is-ancestor HEAD "$prev"; then parents+=(-p HEAD); fi
  msg=${SYNC_MESSAGE:-"private snapshot: $(git rev-parse --short HEAD) + ${PATHS[*]}"}
  commit=$(git commit-tree "$tree" "${parents[@]}" -m "$msg")
  echo "$BRANCH -> $(git rev-parse --short "$commit")"
fi
git update-ref "refs/heads/$BRANCH" "$commit"

# 6. 推送
git push "$REMOTE" "refs/heads/$BRANCH:refs/heads/$BRANCH"
