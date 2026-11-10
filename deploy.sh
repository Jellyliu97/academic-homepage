#!/usr/bin/env bash
# 改完 content/*.xml、stylesheet.css 或图片后，运行此脚本即可发布到 https://jellyliu97.github.io/
# 脚本会先从 XML 重新生成 index.html，再同步并推送两个仓库。
# 用法：
#   ./deploy.sh                                   # 默认同步到同级 ../user-site
#   ./deploy.sh /path/to/Jellyliu97.github.io "更新了论文列表"
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_ROOT="${1:-$(dirname "$SRC")/user-site}"
MSG="${2:-Update academic homepage}"

# 0) 每次发布前从 content/*.xml 重建静态页面，避免「改了 XML 却忘了构建」
PYTHON="${PYTHON:-python}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  PYTHON=python3
fi
"$PYTHON" "$SRC/build.py" --check
"$PYTHON" "$SRC/build.py"

if [ ! -d "$SITE_ROOT/.git" ]; then
  echo "找不到用户站点仓库：$SITE_ROOT" >&2
  echo "用法: $0 [/path/to/Jellyliu97.github.io] [commit message]" >&2
  exit 1
fi

# 防止覆盖站点仓库里尚未提交的手工改动
if [ -n "$(cd "$SITE_ROOT" && git status --porcelain)" ]; then
  echo "站点仓库有未提交改动，请先提交或撤销，避免被同步覆盖：" >&2
  (cd "$SITE_ROOT" && git status --short) >&2
  exit 1
fi

# 1) 同步主页文件到站点仓库的根目录与 docs/，并把 URL 改写成根域名
"$SRC/sync-to-root.sh" "$SITE_ROOT" >/dev/null
for d in "$SITE_ROOT/cv" "$SITE_ROOT/docs/cv"; do
  mkdir -p "$d"
  cp "$SRC/cv/index.html" "$d/index.html"
done

# 2) 提交并推送源仓库（备份 / 历史）
cd "$SRC"
git add -A
if ! git diff --cached --quiet; then
  git commit -m "$MSG"
  git push origin main
  echo "✓ 源仓库已推送"
else
  echo "· 源仓库无改动"
fi

# 3) 提交并推送站点仓库 —— 这一步才会更新线上页面
cd "$SITE_ROOT"
git add -A
if ! git diff --cached --quiet; then
  git commit -m "$MSG"
  git push origin main
  echo "✓ 站点仓库已推送 → https://jellyliu97.github.io/"
else
  echo "· 站点仓库无改动（线上已是最新）"
fi

echo "完成。GitHub Pages 通常 30-60 秒内完成构建。"
