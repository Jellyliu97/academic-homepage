# Guodong Liu (Eric Liu) — Academic Homepage

Personal academic homepage for **Guodong Liu (Eric Liu)**, a Ph.D. student in computer
science at the **State Key Laboratory for Novel Software Technology, Nanjing University**.
Content was adapted from the author's earlier AcademicPages site and rendered with a
static, single-page HTML template.

**规范网址（canonical）：<https://jellyliu97.github.io/>** — 旧的 `/homepage/` 与项目页地址不再使用。

## 为什么根域名需要单独的仓库

GitHub Pages 的 URL 由**仓库名**决定，不是由设置项决定：

| 仓库名 | 发布源 | 访问地址 |
| --- | --- | --- |
| `Jellyliu97.github.io`（用户站点，每账号仅一个） | `main` / `(root)` | `https://jellyliu97.github.io/` ✅ |
| 任意其他仓库（项目站点） | `main` / `/(root)` | `https://jellyliu97.github.io/<仓库名>/` |

改 DNS、加 `CNAME`、改 `baseurl` 都去不掉项目路径。该用户站点仓库在账号里
**早已存在**（2026-05 创建，从 AcademicPages 模板复制的旧 Jekyll 站点），因此不能把本仓库
改名成它 —— 名字已被占用。

## 当前部署架构

| 仓库 | 角色 | 公开性 |
| --- | --- | --- |
| `Jellyliu97/Jellyliu97.github.io` | **正式站点**，主页在根目录，`docs/` 有等价副本 | 必须保持 public（见下） |
| `Jellyliu97/academic-homepage`（本仓库） | 源文件 / 历史备份 | **可安全设为 private** |

用户站点的 `robots.txt` 与 `sitemap.xml` 落在真正的根路径（项目页做不到），
搜索引擎可直接读取。CV 入口指向 `/cv/`，目前是一个占位页（放上 `cv.pdf` 后可改链）。

✅ Pages 已由 GitHub 在首次推送时自动启用，发布源 `main / (root)`，无需在 Settings 里开启。
根目录的 `.nojekyll` 禁用了旧模板的 Jekyll 构建（否则会渲染出别人的模板页面并覆盖主页）。

## 🔴 关于「把仓库设为私有」

**先分清两件事**，这决定了你能不能达成目的：

| 想隐藏的东西 | 能否做到 |
| --- | --- |
| 仓库里的源码、旧文件、提交历史 | ✅ 设为 private 即可 |
| **已经发布的网页 `https://jellyliu97.github.io/`** | ❌ **做不到**。GitHub 官方明确说明：即使源仓库是私有的，Pages 站点仍然对全网公开 |

另外两条硬约束：

1. **GitHub Free 套餐**：Pages 只对 public 仓库可用。把站点仓库改成 private 会**直接让主页下线（404）**。
   只有 GitHub Pro / Team / Enterprise（含学生开发者包）才允许私有仓库继续发布 Pages。
2. 即使有 Pro，若从 Pro 降级回 Free，私有仓库发布的 Pages 会被自动下线。

**因此建议这样处理：**

- `academic-homepage`（本仓库 / 源文件）→ 放心设为 **private**。它的 Pages 会随之停止，
  正好去掉 `/academic-homepage/` 这份重复内容镜像，对 SEO 还有好处。
- `Jellyliu97.github.io`（正式站点仓库）→ **保持 public**。如果嫌里面 59MB 旧 Jekyll 模板、
  `.idea/`、`google_scholar_crawler/` 被人看到，正确做法是**清理这些旧文件**，而不是改成私有。
- 若你确实需要「网页也不给别人看」，只能关掉 Pages 或改用带鉴权的自建托管，
  GitHub Pages 不提供访问控制。

**网页设置方法**（需要管理员权限，助手没有改仓库可见性的 API 权限）：
仓库 → `Settings` → `General` → 最底部 `Danger Zone` → `Change repository visibility`
→ `Make private` → 按提示输入仓库名确认。

## 🚀 本地改完怎么发布（重要）

**只在本仓库执行 `git push` 不会更新线上主页** —— 线上内容来自
`Jellyliu97.github.io` 仓库，不是本仓库。两种方式任选其一：

### 方式 A：一键部署（推荐，继续在本仓库编辑）

```bash
./deploy.sh                                  # 默认同步到同级 ../user-site
./deploy.sh /path/to/Jellyliu97.github.io "更新了论文列表"   # 自定义路径 / 提交信息
```

`deploy.sh` 会依次：同步文件到站点仓库的根目录与 `docs/`、把 URL 改写为根域名、
同步 CV 占位页、提交并推送**两个**仓库。一次命令全部完成，之后 Pages 约 30–60 秒构建。

### 方式 B：最快（直接在站点仓库编辑）

```bash
cd /path/to/Jellyliu97.github.io
# 编辑 index.html（注意：改【根目录】那份，不要改 docs/ 里的副本）
git add -A && git commit -m "Update homepage" && git push
```

因为发布源是 `main / (root)`，这一次 push 就会让线上生效。此方式下本仓库会落后于线上，
建议偶尔用 `deploy.sh` 把两边对齐。**两种方式不要混用**：`deploy.sh` 会用本仓库内容覆盖站点仓库。

`sync-to-root.sh` 是只同步、不提交的底层脚本，供排查用；日常用 `deploy.sh` 即可。

## 本地预览

```bash
python3 -m http.server 8080 --bind 127.0.0.1
# 打开 http://127.0.0.1:8080/
```

## 页面内容

`index.html`：简介 / 研究兴趣 / 联系方式 → News → Publications（29 篇，按研究方向筛选）
→ Work and Intern Experiences → Research Projects & Directions（3D 词云）→
Service and Teaching → Awards and Honors → Contact Me → 页脚。
全部内容都写在静态 HTML 里（不靠 JS 注入），搜索引擎可索引完整论文列表。

SEO 已配置：title/description/keywords/robots/canonical、Open Graph、Twitter Card、
JSON-LD（ProfilePage + Person）、`sitemap.xml`、`robots.txt`、`.nojekyll`。

## 图片 — 可随时替换

占位图的文件名就是最终文件名，**直接覆盖同名文件即可，不用改 HTML**。

| 文件 | 替换为 |
| --- | --- |
| `images/portrait.png` | 个人照片（建议约 600×760） |
| `images/institute.svg` | 南京大学 / 单位 logo（现为通用建筑图标） |
| `images/favicon.svg` | 自己的 favicon（现为 "GL" 字母） |
| `images/paper/<slug>.png` | 29 篇论文的配图 |
| `images/experience/background-*.webp`、`background.jpeg` | 页脚山景（可选） |
| `images/icon/cursor*.png` | 自定义光标（可选） |

论文与图片的对应关系：在 `index.html` 搜 `id="pub-<slug>"`，其下方的
`images/paper/<slug>.png` 就是对应配图。例如 `id="pub-mobicom2026-accspeech"`
→ `images/paper/mobicom2026-accspeech.png`。

CV 页在 `cv/index.html`：把 `cv.pdf` 放进同目录，再把主页里 3 处 CV 链接
（导航、联系方式、Contact Me）指向该文件即可。

## 让搜索引擎收录

1. 仓库 About 里设置 description 与 Website = `https://jellyliu97.github.io/`；
   同步更新 GitHub 个人主页 README、Google Scholar 的 Homepage 字段。
2. **Google Search Console** 建 `https://jellyliu97.github.io/` 的 *网址前缀*资源，
   把验证码填进 `index.html` `<head>` 中标注了 `YOUR_CODE` 的
   `<meta name="google-site-verification">`（改完用 `deploy.sh` 发布），
   然后提交 `https://jellyliu97.github.io/sitemap.xml` 并请求编入索引。
   > 旧仓库根目录的 `googlea34440bfd0246b9e.html` 是从别人模板复制来的验证文件，不是你的，不要用。
3. **Bing Webmaster Tools** 可从 GSC 导入；ORCID / DBLP / Scholar 加上新链接，
   外链是新站被抓取最快的途径。

## 更新内容时的清单

- 文字、论文、News、奖项、链接：改 `index.html`；改完运行 `./deploy.sh`。
- 筛选按钮与论文 `data-tags` 需使用同一组键：
  `speech`、`sensing`、`rf`、`security`、`medical`、`meta`、`embodied`。
- 3D 词云条目在 `index.html` 的 `myProjects` 数组里。
- 内容变动后同步更新页脚 `Last updated`、`sitemap.xml` 的 `<lastmod>`、
  JSON-LD 的 `dateModified`。
