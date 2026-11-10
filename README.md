# Guodong Liu (Eric Liu) — Academic Homepage

静态学术主页，规范网址 **<https://jellyliu97.github.io/>**（旧的 `/homepage/` 与项目页地址不再使用）。

> 🧩 **内容已经全部搬到 `content/` 的 XML 里了。**
> `index.html` 现在是**构建产物**，请勿手工编辑——下次 `./deploy.sh` 会覆盖它。
> 以后加论文、改 News、换邮箱，只需要动一个小小的 XML 文件。

---

## 🗂️ 想改什么，改哪个文件

| 想改的内容 | 编辑文件 | 说明 |
| --- | --- | --- |
| **新增 / 修改一篇论文** | `content/publications/<slug>.xml` + `index.xml` | 一篇一个文件，新增后要在清单末尾登记，见下节 |
| 论文在页面上的顺序 | `content/publications/index.xml` | **清单行顺序**就是页面顺序；想插队直接挪行，不用改数字 |
| 个人简介、研究兴趣、邮箱、头像、外链 | `content/profile.xml` | 页面顶部与底部 Contact 共用这一份数据 |
| News | `content/news.xml` | 一条 `<item>` = 一行，`date` 是日期徽标 |
| 工作 / 实习经历 | `content/experience.xml` | `<body>` 里可直接写 HTML |
| 研究项目 / 词云 / 提示 | `content/projects.xml` | `<items>` 里一条 `<item>` = 一行项目；`<hint>` 是词云上方居中提示（字体与项目不同）；`cloud` 的 `tag` 对应筛选键 |
| 学术服务 / 教学 | `content/service.xml` | 一条 `<item>` 一个 `<li>` |
| 奖项荣誉 | `content/awards.xml` | 同上 |
| 网址、SEO 文案、导航、筛选标签、页脚 | `content/site.xml` | **改网址只改 `<url>` 一处** |
| 配色、字体、间距 | `stylesheet.css` | 纯样式 |
| 页面骨架、区块结构、交互脚本 | `index.template.html` | 只在改版式时动它 |

### 目录结构

```
academic-homepage/
├── index.html              ← 构建产物（线上就是它；别手改）
├── index.template.html     ← 风格 / 骨架 / 脚本 + {{BLOCK:...}} 占位符
├── build.py                ← 读取 XML → 渲染出完整静态 HTML
├── content/                ← ✅ 日常只需要改这里
│   ├── README.md           #   所有 XML 的字段速查 / schema 说明
│   ├── site.xml            #   网址、SEO、导航、筛选标签、页脚
│   ├── profile.xml         #   简介、兴趣、联系方式、头像
│   ├── news.xml            #   News
│   ├── experience.xml      #   经历
│   ├── projects.xml        #   项目列表 + 词云 + 居中提示
│   ├── service.xml         #   服务 / 教学
│   ├── awards.xml          #   奖项
│   └── publications/       #   一篇论文一个 XML（29 篇）
│       ├── index.xml       #   ⭐ 总清单：行顺序 = 页面顺序，含 order / file / title
│       ├── _template.xml   #   新增论文时复制它（下划线开头，不参与构建）
│       └── mobicom2026-accspeech.xml  …
├── images/                 ← 图片，直接覆盖同名文件即可
├── cv/index.html           ← CV 占位页
├── deploy.sh               ← 一键：构建 + 同步 + 推送两个仓库
├── sync-to-root.sh         ← 只同步、不提交的底层脚本
└── tools/                  ← 一次性迁移脚本，日常不用管
```

---

## ✍️ 新增一篇论文（最常用的操作）

```bash
cp content/publications/_template.xml content/publications/mobicom2028-xxx.xml
# 编辑这个新文件，填好字段（不用写 order）
# 在 content/publications/index.xml 末尾加一行：
#   <paper file="mobicom2028-xxx.xml" title="Paper title"/>
# 把配图放到 images/paper/mobicom2028-xxx.png（可以先放占位图）
python build.py --list      # 确认总数与编号
./deploy.sh
```

一个完整的论文 XML 长这样：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<paper id="mobicom2026-accspeech" featured="true" tags="speech,sensing">
  <title>General Speech Reconstruction for Voice Calls Using Smartphone's Built-in Accelerometer</title>
  <authors><![CDATA[<strong>Guodong Liu</strong>, Jane Doe, John Smith]]></authors>
  <topic>Speech Recovery</topic>
  <venue>MobiCom 2026</venue>
  <role>First Author</role>
  <note>CCF-A, Acceptance Rate: 14% (88/628)</note>
  <image>images/paper/mobicom2026-accspeech.png</image>
  <imageAlt>Teaser figure placeholder for MobiCom 2026</imageAlt>
  <titleUrl>https://doi.org/10.1145/xxxxx</titleUrl>       <!-- 可省略：标题不加链接 -->
  <links>                                                   <!-- 可整块省略 -->
    <link label="Paper" href="https://doi.org/10.1145/xxxxx"/>
  </links>
</paper>
```

| 字段 / 属性 | 必填 | 作用 |
| --- | --- | --- |
| `id` | ✅ | 必须与文件名一致；生成 `<tr id="pub-<id>">` |
| 顺序 | — | **不在本文件配置**，见 `content/publications/index.xml` |
| `tags` | ✅ | 逗号分隔；每个键必须在 `site.xml` 的 `<filters>` 里定义 |
| `featured="true"` | — | 淡黄高亮 + 大图（190px）；不写就是普通条目（155px） |
| `title` / `topic` / `venue` | ✅ | 标题 / 方向标签 / 期刊会议 |
| `authors` | — | 作者名单，显示在标题下方；**留空则不渲染**，可用 CDATA 写 `<strong>` 标出自己 |
| `role` / `note` | — | 作者位次 / 备注（CCF 等级、录用率等） |
| `image` / `imageAlt` | ✅ | 配图路径与替代文字 |
| `titleUrl` | — | 有值时标题变成超链接 |
| `links` | — | 底部 `Paper` / `PDF` / `Code` 等按钮 |

**写 XML 的两条约定**（记住这两条就够了）：

1. 普通字段写**纯文本**，`&`、`<` 由程序自动转义；想加 `<strong>`、`<a>` 这类 HTML，用 `<![CDATA[ ... ]]>` 包起来（News、简介、经历、奖项里的富文本就是这么写的）。
2. `build.py --check` 会检查：清单登记是否齐全、id 重复、未知标签、配图缺失、XML 语法。有问题会直接报错，不会生成半截页面。它还会提示「作者字段已填写 N/29 篇」，方便逐个补全。
3. **新增论文必须登记 `index.xml`**：磁盘上有论文 XML 却没写进清单，构建会直接报错；`python build.py --list` 可随时查看总数、编号与标题。

> 📖 **字段定义在哪**：所有 XML 的完整字段速查在 [content/README.md](content/README.md)，
> 想新增字段看它的最后一节（改 `_template.xml` → `build.py` 渲染函数 → CSS/校验 → 文档）。

---

## 🚀 三步发布

```bash
# 1. 改 content/ 下的 XML
# 2.（可选）本地看效果：直接双击 index.html，或
python build.py                      # 重新生成 index.html / sitemap.xml / robots.txt
python build.py --list               # 查看论文总数、编号、文件名、标题
python -m http.server 8080           # 打开 http://127.0.0.1:8080/

# 3. 一键发布
./deploy.sh
./deploy.sh /path/to/Jellyliu97.github.io "新增 MobiCom 2028 论文"
```

`deploy.sh` **每次都会先自动跑一遍 `build.py --check` + `build.py`**，所以只想发布时可以直接执行它，不会漏构建。它会依次：同步到站点仓库根目录与 `docs/`、把 URL 改写成根域名、同步 CV 页、提交并推送**两个**仓库。

> ⚠️ **只 `git push` 本仓库不会更新线上主页**——线上内容来自 `Jellyliu97.github.io` 仓库。
> 也别在站点仓库里手改 `index.html` 后又用 `deploy.sh`：脚本会用本仓库内容覆盖它（脚本会先检测站点仓库有未提交改动并中止，避免误覆盖）。

线上是**完整静态 HTML**：29 篇论文、News、奖项全都在 HTML 源码里，不依赖 JS 注入，搜索引擎能直接索引；禁用 JS、本地双击打开也正常。`content/` 与 `build.py` 不需要部署到站点仓库。

### 为什么不让浏览器直接 fetch XML？

| 方案 | 结果 |
| --- | --- |
| ✅ 现在：`XML → build.py → 静态 index.html` | SEO / JSON-LD / OG 预览卡片完整；无 JS 可用；`file://` 双击可看；Pages 无需部署 XML |
| ⚠️ 运行时 `fetch()` XML 再渲染 | 百度/必应等爬虫看不到论文列表、首屏空白、`file://` 下 CORS 直接失败 |

所以「index 负责加载 XML」由 **`index.template.html` + `build.py`** 承担：模板里只有风格、布局和 `{{BLOCK:news}}` / `{{BLOCK:papers}}` 这类占位符，`build.py` 把 XML 灌进去。如果以后确实需要浏览器运行时加载版，可以再加一个 `live.html`，**现有 XML 一个字都不用改**。

---

## 🌐 部署架构（两个仓库）

GitHub Pages 的 URL 由**仓库名**决定，不是设置项：`<username>.github.io` 仓库对应根域名，其他仓库对应 `/<repo>/`。

| 仓库 | 角色 | 公开性 |
| --- | --- | --- |
| `Jellyliu97/Jellyliu97.github.io` | **正式站点**，主页在根目录，`docs/` 有等价副本 | 必须保持 public |
| `Jellyliu97/academic-homepage`（本仓库） | 源文件 / XML / 历史备份 | 可设为 private |

- Pages 已由 GitHub 自动启用，发布源 `main / (root)`；根目录 `.nojekyll` 禁用旧模板的 Jekyll 构建。
- `sync-to-root.sh` 会把 `https://jellyliu97.github.io/academic-homepage/` 统一替换成 `https://jellyliu97.github.io/`，所以 `site.xml` 里写项目页 URL 即可，线上自动变成根域名。
- CV 入口指向 `/cv/`（目前是占位页，放上 `cv.pdf` 后改链即可）。
- Pages CDN 缓存约 10 分钟（`Cache-Control: max-age=600`），改完短时间看到旧内容可加 `?v=<时间戳>` 绕过。

### 🔴 关于「把仓库设为私有」

- 设为 private 只隐藏**仓库源码 / 历史**；Pages 发布的网页**永远对全网公开**。
- GitHub Free 下 Pages 只对 public 仓库可用：把站点仓库改 private 会让主页 **404**；Pro / Team / Enterprise 才允许私有仓库发 Pages，且降级回 Free 会自动下线。
- 本仓库可以安全设为 private（它的 Pages 随之下线，正好去掉 `/academic-homepage/` 重复镜像）；嫌站点仓库里 59MB 旧 Jekyll 模板、`.idea/`、`google_scholar_crawler/` 被人看到，正确做法是**清理文件**而不是改私有。
- ⚠️ 两个仓库目前都是 **fork**，GitHub 官方规则是 `You cannot change the visibility of a fork by itself.`，所以网页端 `Change repository visibility` 会不可用。要私有化需新建独立 private 仓库后 `git clone --bare` + `git push --mirror` 迁移，或联系 GitHub Support 脱离 fork 网络。

---

## 🖼️ 图片 — 可随时替换

占位图的文件名就是最终文件名，**直接覆盖同名文件即可，不用改 HTML / XML**。

| 文件 | 替换为 |
| --- | --- |
| `images/portrait.png` | 个人照片（建议约 600×760） |
| `images/institute.svg` | 南京大学 / 单位 logo |
| `images/favicon.svg` | 自己的 favicon（现为 "GL" 字母） |
| `images/paper/<slug>.png` | 29 篇论文配图，`<slug>` 与论文 XML 文件名一致 |
| `images/experience/background-*.webp`、`background.jpeg` | 页脚山景（可选） |
| `images/icon/cursor*.png` | 自定义光标（可选） |

论文与配图的对应关系：打开 `content/publications/<slug>.xml` 看 `<image>` 字段即可。
头像路径在 `content/profile.xml` 的 `<photo src="...">`。

CV 页在 `cv/index.html`：把 `cv.pdf` 放进同目录，再把 `content/profile.xml` 里的 CV 链接指向该文件即可（导航、顶部联系方式、底部 Contact 会一起更新）。

---

## 🔍 SEO / 让搜索引擎收录

已配置：title / description / keywords / robots / canonical、Open Graph、Twitter Card、
JSON-LD（`ProfilePage` + `Person`，由 `site.xml` + `profile.xml` 自动生成）、
`sitemap.xml`、`robots.txt`、`.nojekyll`。

1. 仓库 About 里设置 description 与 Website = `https://jellyliu97.github.io/`；同步更新 GitHub 个人主页 README、Google Scholar 的 Homepage 字段。
2. **Google Search Console** 建 `https://jellyliu97.github.io/` 的 *网址前缀*资源，把验证码填进 **`index.template.html`** 的 `<head>`（标注了 `YOUR_CODE` 的注释处）——⚠️ 不要填进 `index.html`，它会被下次构建覆盖——然后 `./deploy.sh`，提交 `https://jellyliu97.github.io/sitemap.xml` 并请求编入索引。
   > 旧站点仓库根目录的 `googlea34440bfd0246b9e.html` 是从别人模板复制来的验证文件，不是你的，不要用。
3. Bing Webmaster Tools 可从 GSC 导入；ORCID / DBLP / Scholar 加上新链接，外链是新站被抓取最快的途径。

---

## ✅ 更新清单

| 动作 | 只需要 |
| --- | --- |
| 加 / 改论文 | 复制 `_template.xml` → 改名 → 填字段 → 配图 → **在 `index.xml` 末尾登记** |
| 查论文总数 / 编号 | `python build.py --list` |
| 调整论文顺序 | 在 `content/publications/index.xml` 里挪动对应行（不用改数字） |
| 补作者名单 | 对应论文 XML 的 `<authors>`（留空不显示，支持 CDATA 富文本） |
| 加 News / 奖项 / Service | 对应 XML 里加一条 `<item>` |
| 换邮箱 / 换 Scholar 链接 | `content/profile.xml`（顶部与底部一起生效） |
| 加一个新的研究方向筛选 | `content/site.xml` 的 `<filters>` 加 `<filter key="..." label="..."/>`，论文 `tags` 里引用它 |
| 改词云条目 | `content/projects.xml` 的 `<cloud>` |
| 加 / 改研究项目 | `content/projects.xml` 的 `<items>` 加一条 `<item>` |
| 改词云上方提示 | `content/projects.xml` 的 `<hint>`（居中斜体浅灰） |
| 改网址 | `content/site.xml` 的 `<url>`（canonical / OG / JSON-LD / sitemap / robots 全部自动跟着变） |
| 改「Last updated」 | `content/site.xml` 的 `lastUpdatedText`；`lastmod` 同时驱动 sitemap 与 JSON-LD 的 `dateModified` |
| 改版式 / 配色 | `stylesheet.css`、`index.template.html` |

---

## 🧰 附录：`tools/` 里的两个一次性脚本

| 脚本 | 作用 |
| --- | --- |
| `tools/import_legacy_html.py` | 从旧版 951 行 `index.html` 抽取数据，生成 `content/*.xml` |
| `tools/make_template.py` | 把旧版 `index.html` 的数据挖空，生成 `index.template.html` |

它们只在最初重构时跑过一次，日常编辑完全用不到；需要重现迁移过程时可以参考，也可以直接删掉。
