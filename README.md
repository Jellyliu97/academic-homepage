# Guodong Liu (Eric Liu) — Academic Homepage

Personal academic homepage for **Guodong Liu (Eric Liu)**, a Ph.D. student in computer
science at the **State Key Laboratory for Novel Software Technology, Nanjing University**.
Content is mirrored from <https://jellyliu97.github.io/homepage/> and rendered with a
static, single-page HTML template.

**规范网址（canonical）：<https://jellyliu97.github.io/>**

## 为什么根域名需要单独的仓库

GitHub Pages 的 URL 由**仓库名**决定，不是由设置项决定：

| 仓库名 | 发布源 | 访问地址 |
| --- | --- | --- |
| `Jellyliu97.github.io`（用户站点，每个账号仅一个） | `main` / `docs` | `https://jellyliu97.github.io/` ✅ |
| 任意其他仓库（项目站点） | `main` / `/(root)` | `https://jellyliu97.github.io/<仓库名>/` |

也就是说，想去掉 `/academic-homepage/` 这段路径，只能把内容放进名为
`Jellyliu97.github.io` 的仓库；改 DNS、加 `CNAME`、改 `baseurl` 都没用。
该仓库在账号里**已经存在**（2026-05 创建，是一套从 AcademicPages 模板复制的旧 Jekyll
站点，从未启用 Pages），因此不能把本仓库直接改名成它 —— 名字已被占用。

## 当前部署架构

| 仓库 | 角色 | 状态 |
| --- | --- | --- |
| `Jellyliu97/Jellyliu97.github.io` | **正式站点**，主页在仓库根目录（`docs/` 有等价副本） | ✅ Pages 已自动启用，根域名已上线 |
| `Jellyliu97/academic-homepage`（本仓库） | 源文件 + 项目页镜像 | Pages 已启用，位于 `/academic-homepage/` |

用户站点的 `robots.txt` 与 `sitemap.xml` 落在真正的根路径（项目页做不到），
搜索引擎可直接读取。`homepage/index.html` 是旧地址 `/homepage/` 的跳转页：
用户站点启用后该路径会被接管，跳转页保证旧链接不再 404。

## 上线状态（无需手动操作）

✅ **已完成。** 往 `<username>.github.io` 仓库推送时，GitHub 自动启用了 Pages，
发布源为 `main / (root)`，`https://jellyliu97.github.io/` 现在直接返回本主页。
根目录的 `.nojekyll` 禁用了旧模板的 Jekyll 构建（否则会渲染出别人的
AcademicPages 页面并覆盖主页）；`docs/` 中另存一份等价副本。
如需查看或切换发布源：<https://github.com/Jellyliu97/Jellyliu97.github.io/settings/pages>，
把 folder 改成 `/docs` 也能正常显示。

## 以后怎么同步内容

改完本仓库的 `index.html` / CSS / 图片后，运行（参数是用户站点仓库的本地克隆路径）：

```bash
./sync-to-root.sh /path/to/Jellyliu97.github.io
cd /path/to/Jellyliu97.github.io && git add -A && git commit -m "Sync academic homepage" && git push
```

脚本会复制全部文件、把 `https://jellyliu97.github.io/academic-homepage/` 替换为根域名，
并同步 `images/`；**同时写入用户站点仓库的根目录与 `docs/`**（无论 Pages 选哪个发布源都能生效）。
**两个仓库都要提交**，否则线上不会更新。

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

## 让搜索引擎收录

1. 仓库 About 里设置 description 与 Website = `https://jellyliu97.github.io/`；
   同步更新 GitHub 个人主页 README、Google Scholar 的 Homepage 字段。
2. **Google Search Console** 建 `https://jellyliu97.github.io/` 的 *网址前缀*资源，
   把验证码填进 `index.html` `<head>` 中标注了 `YOUR_CODE` 的
   `<meta name="google-site-verification">`（在**两个仓库**里都改并同步），
   然后提交 `https://jellyliu97.github.io/sitemap.xml` 并请求编入索引。
   > 注意：旧仓库根目录的 `googlea34440bfd0246b9e.html` 是从别人模板复制来的验证文件，
   > 不是你的，不要用它。
3. **Bing Webmaster Tools** 可从 GSC 导入；ORCID / DBLP / 旧 `homepage/` 站点加上新链接，
   外链是新站被抓取最快的途径。
4. **避免重复内容**：根站点上线后，`/academic-homepage/` 仍是同内容的镜像。推荐二选一：
   在本仓库 `Settings → Pages` 里关掉 Pages（最干净），或把本仓库 `index.html` 的
   canonical 改成根域名。别让两个 URL 长期同时被索引。

## 更新内容时的清单

- 文字、论文、News、奖项、链接：改 `index.html`；改完运行 `sync-to-root.sh`。
- 筛选按钮与论文 `data-tags` 需使用同一组键：
  `speech`、`sensing`、`rf`、`security`、`medical`、`meta`、`embodied`。
- 3D 词云条目在 `index.html` 的 `myProjects` 数组里。
- 内容变动后同步更新页脚 `Last updated`、`sitemap.xml` 的 `<lastmod>`、
  JSON-LD 的 `dateModified`。
