#!/usr/bin/env bash
# 把本仓库的主页同步到 <username>.github.io 用户站点仓库的 docs/ 发布目录。
# 用法（在 Git Bash / macOS / Linux 下）：
#   ./sync-to-root.sh /path/to/Jellyliu97.github.io
# 同步后脚本会打印后续的 git 提交命令。
set -euo pipefail

SITE_ROOT="${1:-}"
if [ -z "$SITE_ROOT" ] || [ ! -d "$SITE_ROOT/.git" ]; then
  echo "用法: $0 /path/to/Jellyliu97.github.io"
  echo "参数必须是用户站点仓库（Jellyliu97.github.io）的本地克隆路径。"
  exit 1
fi

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$SITE_ROOT/docs"
ROOT_URL="https://jellyliu97.github.io/"
PROJECT_URL="https://jellyliu97.github.io/academic-homepage/"

mkdir -p "$DEST"
for f in index.html stylesheet.css sitemap.xml robots.txt; do
  sed "s#${PROJECT_URL}#${ROOT_URL}#g" "$SRC/$f" > "$DEST/$f"
done
cp "$SRC/.nojekyll" "$DEST/.nojekyll"
mkdir -p "$DEST/images"
cp -r "$SRC/images/." "$DEST/images/"

echo "已同步到 $DEST"
echo "规范网址已替换为 $ROOT_URL"
echo ""
echo "接下来执行："
echo "  cd \"$SITE_ROOT\" && git add -A && git commit -m 'Sync academic homepage' && git push"
