#!/usr/bin/env bash
# 把本仓库「构建产物」（index.html / CSS / sitemap / robots / 图片）同步到
# Jellyliu97.github.io 用户站点仓库，并把项目页 URL 替换成根域名。
# 根目录与 docs/ 各写一份；XML 数据源和 build.py 不需要部署到线上。
# 用法（在 Git Bash / macOS / Linux 下）：
#   ./sync-to-root.sh /path/to/Jellyliu97.github.io
# 日常发布请直接用 ./deploy.sh（它会先运行 build.py，再同步 + 提交 + 推送）。
set -euo pipefail

SITE_ROOT="${1:-}"
if [ -z "$SITE_ROOT" ] || [ ! -d "$SITE_ROOT/.git" ]; then
  echo "用法: $0 /path/to/Jellyliu97.github.io"
  echo "参数必须是用户站点仓库（Jellyliu97.github.io）的本地克隆路径。"
  exit 1
fi

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_URL="https://jellyliu97.github.io/"
PROJECT_URL="https://jellyliu97.github.io/academic-homepage/"

# 用户站点仓库的 Pages 实际发布源是 main / (root)；docs/ 保留一份等价副本，
# 方便以后把发布源切换成 main / docs。两处都写，避免改设置后线上不更新。
for TARGET in "" "docs"; do
  if [ -z "$TARGET" ]; then DEST="$SITE_ROOT"; else DEST="$SITE_ROOT/$TARGET"; fi
  mkdir -p "$DEST"
  for f in index.html stylesheet.css sitemap.xml robots.txt; do
    sed "s#${PROJECT_URL}#${ROOT_URL}#g" "$SRC/$f" > "$DEST/$f"
  done
  cp "$SRC/.nojekyll" "$DEST/.nojekyll"
  mkdir -p "$DEST/images"
  cp -r "$SRC/images/." "$DEST/images/"
  echo "已同步到 $DEST"
done

echo "规范网址已替换为 $ROOT_URL"
echo ""
echo "日常发布建议直接运行 ./deploy.sh（同步 + 提交 + 推送两个仓库一次完成）。"
echo "若手动提交："
echo "  cd \"$SITE_ROOT\" && git add -A && git commit -m 'Sync academic homepage' && git push"
