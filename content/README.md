# XML 字段速查（字段定义都在这里）

> 本项目**没有 XSD / DTD**，字段是「约定式」的：XML 里写什么由本文件约定，
> 怎么读取、怎么渲染由仓库根目录的 `build.py` 决定。
> 换句话说：**改内容 → 改这里的 XML；改字段 → 改 `build.py` 的渲染函数**。

---

## 论文：`content/publications/<slug>.xml`（一篇一个文件）

复制 `_template.xml` 改名即可。`<slug>` 必须与 `id` 一致。
**页面顺序不在论文 XML 里配**，统一由 `content/publications/index.xml` 的行顺序决定；
新增论文后必须在清单末尾登记一行，否则 `build.py` 会报错。

### 根元素 `<paper>` 的属性

| 属性 | 必填 | 说明 |
| --- | --- | --- |
| `id` | ✅ | 与文件名一致；生成 `<tr id="pub-<id>">`，全站唯一 |
| ~~`order`~~ | — | **已移除**：顺序统一由 `index.xml` 决定 |
| `tags` | ✅ | 逗号分隔，每个键都要在 `site.xml` 的 `<filters>` 里定义 |
| `featured` | — | `"true"` 时淡黄高亮 + 190px 大图；不写为普通条目（155px） |

### 子元素

| 字段 | 必填 | 类型 | 渲染位置 / 说明 |
| --- | --- | --- | --- |
| `title` | ✅ | 纯文本 | 论文标题 |
| `authors` | — | **富文本（建议 CDATA）** | 标题下方的作者行；**留空则整行不渲染** |
| `topic` | ✅ | 纯文本 | 顶部方向徽标，如 `Speech Recovery`；多分类可用 ` · ` 连接 |
| `venue` | ✅ | 纯文本 | 期刊 / 会议 + 年份（斜体加粗） |
| `role` | — | 纯文本 | 作者位次，如 `First Author`（橙色加粗） |
| `note` | — | 纯文本 | 备注，如 `CCF-A, Acceptance Rate: 14% (88/628)` |
| `image` | ✅ | 路径 | 论文配图，通常 `images/paper/<slug>.png`；**尺寸无需统一**，页面会按 3:2 比例白底居中显示 |
| `imageAlt` | ✅ | 纯文本 | 图片替代文字 |
| `titleUrl` | — | URL | 有值时标题变成超链接 |
| `links/link` | — | `label` + `href` | 底部 Paper / PDF / Code 等按钮，可多条 |

`authors` 示例（CDATA 里可以写 HTML）：

```xml
<!-- 最简单：只加粗自己 -->
<authors><![CDATA[<strong>Guodong Liu</strong>, Jane Doe, John Smith]]></authors>

<!-- 完整：共同一作 †、共同通讯 *、末尾脚注 -->
<authors><![CDATA[<strong>Guodong Liu</strong><sup>†</sup>, Jane Doe<sup>†</sup>, John Smith<sup>*</sup><span class="author-note">† Equal contribution. * Corresponding author.</span>]]></authors>
```

- **加粗自己**：`<strong>Guodong Liu</strong>`，显示为主题深蓝 + 加粗（`.pub-authors strong`）；
  想只加粗不变色，把该规则的 `color` 改成 `inherit`。
- **共同一作 / 共同通讯**：名字后接上标 `<sup>†</sup>` / `<sup>*</sup>`，作者行末用
  `<span class="author-note">` 写脚注。符号可自选（`†`、`‡`、`#`），只要与脚注一一对应。
- **样式**：`.pub-authors sup`（上标不撑行高）和 `.pub-authors .author-note`（小一号灰字、独占一行）
  在 `stylesheet.css`；渲染逻辑在 `build.py` 的 `make_paper_row()`。
- ⚠️ `<sup>`、`<span>` 必须写在 CDATA 里；裸写在 `<authors>` 里会被 XML 当成子元素，后面的文字会丢。
- `role` 是纯文本字段（会被转义），不能写上标；共同贡献信息统一放 `authors`。
- 纯文本写法也可以，但作者名里若含 `&` 要写成 `&amp;`；**留空写成 `<authors></authors>` 即可**。

---

## 论文总清单：`content/publications/index.xml`

**这是全站论文的唯一顺序表**，也解决了「新增时不知道该写第几号」的问题：
行顺序 = 页面顺序，`order` 只是给人看的编号（**可以省略**，省略时自动按行号编号）。

```xml
<publications>
  <paper order="1" file="admt2023-metasureface.xml" title="Indoor Positioning ..."/>
  <paper order="2" file="advs2022-prosthesis.xml" title="Non-contact ..."/>
  ...
</publications>
```

| 属性 | 必填 | 作用 |
| --- | --- | --- |
| `file` | ✅ | 论文 XML 文件名，必须与磁盘上的文件一致 |
| `title` | — | 标题摘要，只用于清单查看，不影响页面 |
| `order` | — | 显示编号；省略则自动取行号，写 `order="30"` 便于统计 |

新增流程：复制 `_template.xml` → 改名 → 填字段 → **在 `index.xml` 末尾加一行**
`<paper file="new-slug.xml" title="Paper title"/>` → `./deploy.sh`。
想插队就把那一行挪到目标位置，不用改任何数字。
`build.py --check` 会校验：清单里的文件都存在、`file` / `order` 不重复、磁盘上没有「漏登记」的论文 XML。

查看总览（输出「共 29 篇 / 下一篇编号 30」的编号表）：

```bash
python build.py --list
```

---

## 站点级：`site.xml`

| 字段 | 作用 |
| --- | --- |
| `url` | **单点驱动** canonical / OG / JSON-LD / sitemap / robots；同步到站点仓库时会被替换成根域名 |
| `title` / `author` / `description` / `keywords` / `robots` / `themeColor` | `<head>` 基础 meta |
| `ogSiteName` / `ogDescription` / `ogImageAlt` / `twitterTitle` / `twitterDescription` | 社交预览卡片 |
| `inLanguage` / `lastmod` / `lastUpdatedText` | 语言、`sitemap.xml` 与 JSON-LD 的 `dateModified`、页脚「Last updated」 |
| `nav/item` | 导航：`label`、`href`、`external="true"`（新窗口 + noopener） |
| `filters/filter` | 论文筛选按钮：`key`、`label`；论文 `tags` 只能引用这里的 `key` |
| `publicationsIntro` | 富文本，Publications 区块的说明段 |
| `footer/{title,subtitle,ctaLabel,footnote,credit}` | 页脚文案；`footnote` / `credit` 是富文本 |

## 个人：`profile.xml`

`name` / `givenName` / `familyName` / `alias` / `jobTitle` / `shortDescription`（JSON-LD 描述）/
`tagline`（富文本）/ `bio`（富文本）/ `copyBio`（点火箭按钮复制的纯文本）/
`photo`（`src` + `alt`）/ `interests/item`（富文本列表）/
`university` / `universityUrl` / `lab` / `city` / `country` / `countryName` / `location`（富文本）/
`primaryEmail` / `secondaryEmail` /
`links/link`（`kind` = `cv` / `scholar` / `github`，另有 `label`、`title`、`href`）/ `expertise/topic`（JSON-LD `knowsAbout`）。

> 顶部联系方式图标、页脚 CTA、底部 Contact 区块、JSON-LD 都从这一份数据生成，
> **换邮箱只需改一处**。`kind` 决定用哪个内置 SVG 图标。

## 其余区块

| 文件 | 结构 | 备注 |
| --- | --- | --- |
| `news.xml` | `<news><item date="2026">富文本</item>…` | `date` 显示在日期徽标 |
| `experience.xml` | `<experience><item logo="…" logoAlt="…"><body>富文本</body></item>…` | `body` 里可写 `<br>` / `<strong>` |
| `projects.xml` | `<projects><items><item date="…">富文本</item>…</items><hint>富文本</hint><cloud><item name="…" tag="…"/>…</cloud></projects>` | 一条 `item` = 一行项目；`hint` 是词云上方居中提示（斜体浅灰，与项目字体不同）；`tag` 必须有效 |
| `service.xml` | `<service><item>富文本</item>…` | 一条 = 一个 `<li>` |
| `awards.xml` | `<awards><item>富文本</item>…` | 同上 |

---

## 两类字段的写法（只需要记这一条）

| 类型 | 写法 | 处理 |
| --- | --- | --- |
| **纯文本** | `<title>...文字...</title>` | `build.py` 自动转义 `&` `<` `>` |
| **富文本** | `<tag><![CDATA[ ...HTML... ]]></tag>` | 原样输出，可写 `<strong>`、`<a>`、`&nbsp;` 等实体 |

富文本字段清单：论文 `authors`、`news/item`、`profile` 的 `tagline`/`bio`/`interests/item`/`location`、
`experience/item/body`、`projects/items/item` 与 `projects/hint`、`site` 的 `publicationsIntro`/`footer/footnote`/`footer/credit`、
`service/item`、`awards/item`。

---

## 换行怎么写（很容易踩坑）

| 想要的效果 | 正确写法 |
| --- | --- |
| XML **源码**里给字段分行、缩进，方便阅读 | 直接按回车即可，那只是源码排版，**不会**显示成网页换行 |
| 网页上**换行** | 在富文本字段的 CDATA 里写 `<br>`（或 `<br/>`） |
| 网页上**分段** | CDATA 里写多个 `<p>……</p>` |
| 列表里新起一条 | 再加一个 `<item>`，每条 = 一个 `<li>`，不要在同一条里塞 `<br>` |

示例：

```xml
<item date="2026"><![CDATA[第一行文字<br>第二行文字]]></item>
```

⚠️ **三个坑**：

1. **HTML 会把源码换行折叠成空格**。XML 里按回车只是让文件好看，浏览器不会换行；
   `&#10;` / `&#xA;` 也一样是空白，除非元素设了 `white-space: pre-line`（本项目没设）。
2. **不要在普通元素里直接写 `<br/>`**：XML 会把它当成子元素，`build.py` 只读 `.text`，
   后面的文字会被丢掉。实测 `<x>AAA<br/>BBB</x>` 解析出来只有 `'AAA'`。
   必须放进 `<![CDATA[ ... ]]>`，或写成转义形式 `&lt;br/&gt;`（解析后同样是字符串 `<br/>`）。
3. **纯文本字段不支持换行标签**：`title` / `topic` / `venue` / `role` / `note` / `imageAlt` 等会被
   `esc()` 转义，写 `<br>` 只会在页面上显示成字面的 `<br>`。要换行只能在富文本字段里做。

> `experience.xml` 的 `<body>` 就是现成范例：里面用 `<br>` 分隔单位、时间和职位。

---

## 想再加一个新字段，改这 4 个地方

1. **`content/publications/_template.xml`**（或其他对应模板）→ 加一行示例 + 注释。
2. **`build.py`** → 论文字段在 `make_paper_row()`，其他区块在各自的 `make_*()`；
   用 `field(node, "字段名")` 读取，纯文本再套 `esc()` 转义，富文本直接输出。
3. **`stylesheet.css`** → 需要新样式就加 class（如这次的 `.pub-authors`）；
   需要校验就在 `build.py` 的 `validate()` / `load_papers()` 里加规则。
4. **本文件 + 根目录 `README.md`** → 补字段表，避免以后忘了。

改完跑 `python build.py --check` 校验，再 `python build.py` 看生成的 `index.html`，最后 `./deploy.sh` 发布。
