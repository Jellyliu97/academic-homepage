#!/usr/bin/env python3
"""学术主页构建器：content/*.xml + index.template.html -> index.html / sitemap.xml / robots.txt

日常用法
--------
    python build.py            # 根据 XML 重新生成静态页面
    python build.py --check    # 只校验数据源，不写文件
    python build.py --list     # 列出论文总数 / 编号 / 文件名 / 标题
    ./deploy.sh                # 自动先构建，再同步并推送两个仓库

设计取舍
--------
线上交付的仍然是**完整静态 HTML**（不是浏览器运行时 fetch XML）：
  * 搜索引擎、预览卡片、JSON-LD 都能直接读到内容；
  * 禁用 JS / 本地双击打开 / GitHub Pages 上都正常；
  * 不需要把 XML 部署到站点仓库。
XML 是唯一数据源，index.template.html 只负责风格、布局与脚本。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
PUBDIR = CONTENT / "publications"
INDEX = PUBDIR / "index.xml"          # 论文总清单：行顺序 = 页面顺序
TEMPLATE = ROOT / "index.template.html"

# 联系方式图标（原本硬编码在 index.html 里，现在由 profile.xml 的 kind 选择）
ICONS = {
    "email": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="m3 7 9 6 9-6"></path></svg>',
    "cv": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"></path><path d="M14 2v6h6"></path><path d="M8 13h8"></path><path d="M8 17h5"></path></svg>',
    "scholar": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3 1.5 9 12 15 22.5 9 12 3Z"></path><path d="M5 12.1v4.2c0 1.2 3.1 3.2 7 3.2s7-2 7-3.2v-4.2l-7 4-7-4Z"></path></svg>',
    "github": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.7.5.6 5.6.6 11.9c0 5 3.3 9.3 7.9 10.8.6.1.8-.3.8-.6v-2c-3.2.7-3.9-1.4-3.9-1.4-.5-1.3-1.3-1.7-1.3-1.7-1.1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 .1.5 2.7 3.2 1.9.1-.8.4-1.3.8-1.6-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.6.1-3.1 0 0 1-.3 3.2 1.2.9-.3 1.9-.4 2.9-.4s2 .1 2.9.4c2.2-1.5 3.2-1.2 3.2-1.2.6 1.5.2 2.8.1 3.1.8.9 1.2 1.8 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.2c0 .3.2.7.8.6 4.6-1.5 7.9-5.8 7.9-10.8C23.4 5.6 18.3.5 12 .5Z"></path></svg>',
}


class BuildError(Exception):
    pass


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------
def load(name: str) -> ET.Element:
    path = CONTENT / name
    if not path.exists():
        raise BuildError(f"缺少数据源：{path}")
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise BuildError(f"{path.name} 不是合法 XML：{exc}") from exc


def field(node: ET.Element | None, path: str, default: str = "") -> str:
    """读取纯文本 / CDATA 字段。CDATA 里的 HTML 实体与标签由 XML 解析器原样保留。"""
    if node is None:
        return default
    found = node.find(path)
    if found is None:
        return default
    return (found.text or "").strip()


def inner(node: ET.Element) -> str:
    return (node.text or "").strip()


def paper_year(p: ET.Element) -> str:
    """年份优先取 <year>，否则从 venue 提取 4 位年份；都没有返回空串。"""
    year = field(p, "year")
    if year:
        return year
    m = re.search(r"(19|20)\d{2}", field(p, "venue"))
    return m.group(0) if m else ""


def esc(value: object) -> str:
    """HTML 转义（不转义单引号，保持与原页面一致）。"""
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def js(value: object) -> str:
    """生成 JS 字符串字面量。"""
    return json.dumps(str(value), ensure_ascii=False)


# ---------------------------------------------------------------------------
# 数据加载与校验
# ---------------------------------------------------------------------------
def load_index() -> list[dict]:
    """论文总清单：行顺序 = 页面顺序；order 只是给人看的编号（可省略）。"""
    if not INDEX.is_file():
        raise BuildError(f"缺少论文总清单：{INDEX}")
    try:
        root = ET.parse(INDEX).getroot()
    except ET.ParseError as exc:
        raise BuildError(f"index.xml 不是合法 XML：{exc}") from exc

    entries: list[dict] = []
    seen_files: set[str] = set()
    seen_orders: set[str] = set()
    for line_no, e in enumerate(root.findall("paper"), 1):
        filename = (e.get("file") or "").strip()
        order = (e.get("order") or str(line_no)).strip()
        title = (e.get("title") or "").strip()
        if not filename.endswith(".xml"):
            raise BuildError(f"index.xml 第 {line_no} 行：file 必须是 .xml 文件名")
        if filename in seen_files:
            raise BuildError(f"index.xml 第 {line_no} 行：重复登记 {filename}")
        if order in seen_orders:
            raise BuildError(f"index.xml 第 {line_no} 行：order 重复 {order}")
        seen_files.add(filename)
        seen_orders.add(order)
        entries.append({"order": order, "file": filename, "title": title})

    if not entries:
        raise BuildError("index.xml 里没有登记任何论文")

    # 磁盘上有、清单里没有的论文必须报错，避免「加了 XML 却忘记登记」
    on_disk = {
        p.name for p in PUBDIR.glob("*.xml")
        if not p.name.startswith("_") and p.name != INDEX.name
    }
    missing = sorted(on_disk - seen_files)
    if missing:
        raise BuildError("以下论文 XML 未在 index.xml 登记：" + ", ".join(missing)
                         + "；请在清单末尾加一行 <paper file=\"...\" title=\"...\"/>")
    return entries


def load_papers(entries: list[dict]) -> list[ET.Element]:
    """按清单顺序加载论文 XML；论文文件本身不再写 order。"""
    papers: list[ET.Element] = []
    seen_ids: set[str] = set()
    for e in entries:
        path = PUBDIR / e["file"]
        if not path.is_file():
            raise BuildError(f"index.xml 登记的文件不存在：{path.name}")
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            raise BuildError(f"{path.name} 不是合法 XML：{exc}") from exc
        slug = root.get("id") or ""
        if slug != path.stem:
            raise BuildError(f"{path.name}: id='{slug}' 必须与文件名一致")
        if slug in seen_ids:
            raise BuildError(f"论文 id 重复：{slug}")
        seen_ids.add(slug)
        papers.append(root)
    return papers


def validate(site: ET.Element, papers: list[ET.Element], projects: ET.Element) -> list[str]:
    """返回警告列表；致命问题直接抛 BuildError。"""
    warnings: list[str] = []
    valid_tags = {f.get("key") for f in site.findall("filters/filter")}
    for p in papers:
        for tag in (p.get("tags") or "").split(","):
            tag = tag.strip()
            if tag and tag not in valid_tags:
                warnings.append(f"{p.get('id')}: 标签 '{tag}' 未在 site.xml 的 <filters> 中定义")
        image = field(p, "image")
        if image and not (ROOT / image).is_file():
            warnings.append(f"{p.get('id')}: 找不到配图 {image}（可先放占位图）")
        if not paper_year(p):
            warnings.append(f"{p.get('id')}: 没识别到年份，年份排序时会排在最后"
                            f"（可在 XML 里加 <year>2026</year>）")
    for item in projects.findall("cloud/item"):
        tag = item.get("tag")
        if tag not in valid_tags:
            warnings.append(f"词云 '{item.get('name')}' 的 tag='{tag}' 未定义")
    return warnings


# ---------------------------------------------------------------------------
# 各区块渲染
# ---------------------------------------------------------------------------
def make_jsonld(site: ET.Element, profile: ET.Element, url: str) -> str:
    S = lambda k: field(site, k)
    P = lambda k: field(profile, k)
    links = {l.get("kind"): l for l in profile.findall("links/link")}

    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "ProfilePage",
                "@id": url + "#webpage",
                "url": url,
                "name": S("ogSiteName"),
                "isPartOf": {
                    "@type": "WebSite",
                    "@id": url + "#website",
                    "url": url,
                    "name": S("ogSiteName"),
                },
                "primaryImageOfPage": {
                    "@type": "ImageObject",
                    "url": url + "images/portrait.png",
                },
                "dateModified": S("lastmod"),
                "inLanguage": S("inLanguage"),
                "mainEntity": {"@id": url + "#person"},
            },
            {
                "@type": "Person",
                "@id": url + "#person",
                "name": P("givenName") + " " + P("familyName"),
                "alternateName": [P("alias"), P("name")],
                "givenName": P("givenName"),
                "familyName": P("familyName"),
                "jobTitle": P("jobTitle"),
                "description": P("shortDescription"),
                "url": url,
                "image": url + "images/portrait.png",
                "email": "mailto:" + P("primaryEmail"),
                "affiliation": {
                    "@type": "CollegeOrUniversity",
                    "name": P("university"),
                    "sameAs": P("universityUrl"),
                    "department": {"@type": "Organization", "name": P("lab")},
                },
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": P("city"),
                    "addressCountry": P("country"),
                },
                "sameAs": [links[k].get("href") for k in ("scholar", "github", "cv")],
                "knowsAbout": [inner(t) for t in profile.findall("expertise/topic")],
            },
        ],
    }
    return json.dumps(graph, indent=2, ensure_ascii=False)


def make_profile_text(profile: ET.Element) -> str:
    P = lambda k: field(profile, k)
    primary = P("primaryEmail")
    secondary = P("secondaryEmail")
    links = {l.get("kind"): l for l in profile.findall("links/link")}

    def icon_link(kind: str) -> str:
        l = links[kind]
        return (
            f'<a href="{esc(l.get("href"))}" target="_blank" rel="noopener" '
            f'title="{esc(l.get("title") or l.get("label"))}">\n'
            f'                  {ICONS[kind]}\n'
            f'                  {esc(l.get("label"))}\n'
            f'                </a>'
        )

    email_link = (
        f'<a href="mailto:{esc(primary)}" id="email-copy" class="email-link" '
        f'title="Click to copy email">\n'
        f'                  {ICONS["email"]}\n'
        f'                  Email: <span class="contact-sub">{esc(primary)}</span>\n'
        f'                </a>'
    )
    first_line = " &nbsp;/&nbsp; ".join(
        [email_link] + [icon_link(k) for k in ("cv", "scholar", "github")]
    )
    interests = "\n".join(
        f"              <li>{inner(i)}</li>" for i in profile.findall("interests/item")
    )

    return "\n".join([
        f'              <h1 class="profile-name"><name>{esc(P("name"))} '
        f'<span id="astronaut-btn" class="copy-bio-btn" title="Copy bio" '
        f'aria-label="Copy bio">&#128640;</span></name></h1>',
        f'              <p class="profile-tagline">{field(profile, "tagline")}</p>',
        field(profile, "bio"),
        '              <ol class="interests-list">',
        interests,
        '              </ol>',
        '              <div class="profile-divider"></div>',
        '              <p class="contact-links">',
        '                <span class="contact-line">',
        f'                  {first_line}',
        '                </span>',
        '                <span class="contact-line">',
        f'                  <span class="contact-plain">{field(profile, "location")}</span> '
        f'&nbsp;/&nbsp;',
        f'                  <a href="mailto:{esc(secondary)}">{esc(secondary)}</a>',
        '                </span>',
        '              </p>',
    ])


def make_paper_row(p: ET.Element) -> str:
    featured = p.get("featured") == "true"
    pad = "18px" if featured else "12px"
    width = "190" if featured else "155"
    cls = ' class="pub-featured"' if featured else ""
    style = ' style="background-color: lightyellow;"' if featured else ""

    year = paper_year(p)
    title_url = field(p, "titleUrl")
    title_html = (
        f'<a href="{esc(title_url)}" target="_blank" rel="noopener">'
        f'<papertitle>{esc(field(p, "title"))}</papertitle></a>'
        if title_url else f'<papertitle>{esc(field(p, "title"))}</papertitle>'
    )

    # <authors> 可选：留空则完全不渲染（页面与加字段之前保持一致）
    # 支持 CDATA 富文本，例如 <![CDATA[<strong>Guodong Liu</strong>, Jane Doe]]>
    authors = field(p, "authors")
    if authors:
        title_html += '\n              <div class="pub-authors">' + authors + "</div>"

    meta_bits = []
    if field(p, "role"):
        meta_bits.append(f'<span class="pub-role">{esc(field(p, "role"))}</span>')
    if field(p, "note"):
        meta_bits.append(f'<span class="pub-note">{esc(field(p, "note"))}</span>')
    meta = " &nbsp;&middot;&nbsp; ".join(meta_bits)

    link_els = p.findall("links/link")
    links = ""
    if link_els:
        anchors = "".join(
            f'<a href="{esc(l.get("href"))}" target="_blank" rel="noopener">'
            f'{esc(l.get("label"))}</a>' for l in link_els
        )
        links = f'<div class="pub-links">{anchors}</div>'

    return "\n".join([
        f'          <tr id="pub-{esc(p.get("id"))}"{cls} '
        f'data-tags="{esc(p.get("tags"))}" data-year="{esc(year)}"{style}>',
        f'            <td class="pub-figure" style="padding:{pad};width:27%;vertical-align:middle">',
        f'              <img class="pub-thumb" src="{esc(field(p, "image"))}" width="{width}"',
        f'                   alt="{esc(field(p, "imageAlt"))}" loading="lazy">',
        '            </td>',
        f'            <td style="padding:{pad};width:73%;vertical-align:middle">',
        f'              <span class="pub-topic">{esc(field(p, "topic"))}</span>',
        f'              {title_html}',
        '              <br>',
        f'              <em><strong>{esc(field(p, "venue"))}</strong></em>',
        '              <br>',
        f'              <span class="pub-meta">{meta}</span>',
        f'              {links}',
        '            </td>',
        '          </tr>',
    ])


def make_projects_body(projects: ET.Element) -> str:
    """项目列表（每条 item 一个 li）+ 词云上方居中的提示（字体另设）。"""
    chunks: list[str] = []
    items = projects.findall("items/item")
    if items:
        lis = []
        for i in items:
            date = i.get("date")
            badge = f'<span class="project-date">{esc(date)}</span> ' if date else ""
            lis.append(f'<li class="project-item">{badge}{inner(i)}</li>')
        chunks.append('<ul class="project-list">\n'
                      + "\n".join("          " + li for li in lis)
                      + "\n          </ul>")
    hint = field(projects, "hint")
    if hint:
        chunks.append(f'<p class="cloud-hint">{hint}</p>')
    return "\n          ".join(chunks)


def make_visitor_map(site: ET.Element) -> str:
    """可选：第三方访客地图（MapMyVisitors / ClustrMaps 等），site.xml 启用后渲染。"""
    node = site.find("visitorMap")
    if node is None or node.get("enabled") != "true":
        return ""
    embed = field(node, "embed")
    if not embed:
        return ""
    provider = node.get("provider") or ""
    note = f'<p class="visitor-note">Visitor map by {esc(provider)}</p>' if provider else ""
    return ('        <section id="visitor-map" class="page-section">\n'
            + embed + "\n" + note + "\n        </section>")


def make_contact(profile: ET.Element) -> str:
    P = lambda k: field(profile, k)
    primary, secondary = P("primaryEmail"), P("secondaryEmail")
    links = {l.get("kind"): l for l in profile.findall("links/link")}

    def anchor(kind: str) -> str:
        l = links[kind]
        return (f'<a href="{esc(l.get("href"))}" target="_blank" rel="noopener">'
                f'{esc(l.get("label"))}</a>')

    items = [
        f'<a href="mailto:{esc(secondary)}">{esc(secondary)}</a>',
        f'<a href="mailto:{esc(primary)}">{esc(primary)}</a>',
        f'{esc(P("lab"))}, {esc(P("university"))}, {esc(P("city"))}, {esc(P("countryName"))}',
        " &nbsp;/&nbsp; ".join(anchor(k) for k in ("scholar", "github", "cv")),
    ]
    return "\n".join(f"              <li>{item}</li>" for item in items)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def build(*, check_only: bool = False, list_only: bool = False) -> None:
    site = load("site.xml")
    profile = load("profile.xml")
    news = load("news.xml")
    service = load("service.xml")
    awards = load("awards.xml")
    experience = load("experience.xml")
    projects = load("projects.xml")
    entries = load_index()
    papers = load_papers(entries)
    if list_only:
        print(f"论文清单（content/publications/index.xml）：共 {len(entries)} 篇，下一篇编号 {len(entries) + 1}\n")
        print(f"  {'#':>3}  {'file':<38}  title")
        for n, e in enumerate(entries, 1):
            title = e["title"] or "(未填标题)"
            if len(title) > 58:
                title = title[:55] + "..."
            print(f"  {n:>3}  {e['file']:<38}  {title}")
        print("\n新增论文：复制 _template.xml → 改名 → 在清单末尾加一行 <paper .../>")
        return
    warnings = validate(site, papers, projects)

    url = field(site, "url").rstrip("/") + "/"
    S = lambda k: field(site, k)
    P = lambda k: field(profile, k)
    F = lambda k: field(site, "footer/" + k)
    photo = profile.find("photo")

    scalars: dict[str, str] = {
        "site.title": esc(S("title")),
        "site.author": esc(S("author")),
        "site.description": esc(S("description")),
        "site.keywords": esc(S("keywords")),
        "site.robots": esc(S("robots")),
        "site.themeColor": esc(S("themeColor")),
        "site.ogSiteName": esc(S("ogSiteName")),
        "site.ogDescription": esc(S("ogDescription")),
        "site.ogImageAlt": esc(S("ogImageAlt")),
        "site.twitterTitle": esc(S("twitterTitle")),
        "site.twitterDescription": esc(S("twitterDescription")),
        "site.url": esc(url),
        "site.lastUpdatedText": esc(S("lastUpdatedText")),
        "profile.name": esc(P("name")),
        "profile.givenName": esc(P("givenName")),
        "profile.familyName": esc(P("familyName")),
        "profile.photoSrc": esc(photo.get("src") if photo is not None else "images/portrait.png"),
        "profile.photoAlt": esc(photo.get("alt") if photo is not None else ""),
        "profile.primaryEmail": esc(P("primaryEmail")),
        "profile.copyBioJs": js(P("copyBio")),
        "profile.primaryEmailJs": js(P("primaryEmail")),
        "footer.title": esc(F("title")),
        "footer.subtitle": esc(F("subtitle")),
        "footer.ctaLabel": esc(F("ctaLabel")),
        "footer.footnote": F("footnote"),
        "footer.credit": F("credit"),
        "projects.cloudJson": json.dumps(
            [{"name": i.get("name"), "tag": i.get("tag")} for i in projects.findall("cloud/item")],
            ensure_ascii=False,
        ),
    }

    blocks: dict[str, str] = {
        "jsonld": make_jsonld(site, profile, url),
        "nav": "\n        ".join(
            f'<a href="{esc(i.get("href"))}"'
            + (' target="_blank" rel="noopener"' if i.get("external") == "true" else "")
            + f'>{esc(i.get("label"))}</a>'
            for i in site.findall("nav/item")
        ),
        "profileText": make_profile_text(profile),
        "news": "\n".join(
            f'              <li class="news-entry"><span class="news-date-badge">'
            f'{esc(i.get("date"))}</span> {inner(i)}</li>'
            for i in news.findall("item")
        ),
        "publicationsIntro": S("publicationsIntro"),
        "filters": "\n".join(
            f'            <button class="{"tag-btn active" if f.get("key") == "all" else "tag-btn"}" '
            f'data-tag="{esc(f.get("key"))}">{esc(f.get("label"))}</button>'
            for f in site.findall("filters/filter")
        ),
        "papers": "\n".join(make_paper_row(p) for p in papers),
        "experience": "\n".join(
            "\n".join([
                '            <tr>',
                '              <td class="exp-logo" style="padding-left:20px;padding-right:20px;width:15%;vertical-align:middle">',
                f'                <img src="{esc(i.get("logo"))}" width="80" alt="{esc(i.get("logoAlt"))}">',
                '              </td>',
                '              <td class="exp-body">',
                f'                {field(i, "body")}',
                '              </td>',
                '            </tr>',
            ])
            for i in experience.findall("item")
        ),
        "projectsBody": make_projects_body(projects),
        "service": "\n".join(f"              <li>{inner(i)}</li>" for i in service.findall("item")),
        "awards": "\n".join(f"              <li>{inner(i)}</li>" for i in awards.findall("item")),
        "contact": make_contact(profile),
        "visitorMap": make_visitor_map(site),
    }

    html_text = TEMPLATE.read_text(encoding="utf-8")
    for key, value in scalars.items():
        html_text = html_text.replace("{{" + key + "}}", value)
    for key, value in blocks.items():
        html_text = html_text.replace("{{BLOCK:" + key + "}}", value)

    leftover = re.findall(r"\{\{[^}]+\}\}", html_text)
    if leftover:
        raise BuildError(f"模板里有未替换的占位符：{sorted(set(leftover))}")

    # 输出自检
    jsonld_text = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_text, re.S)
    if not jsonld_text:
        raise BuildError("生成的 index.html 缺少 JSON-LD")
    json.loads(jsonld_text.group(1))
    if html_text.count('id="pub-') != len(papers):
        raise BuildError("生成的论文条目数与 XML 数量不一致")
    if html_text.count("<html") != 1 or not html_text.rstrip().endswith("</html>"):
        raise BuildError("生成的 HTML 结构不完整")

    sitemap = "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{esc(url)}</loc>',
        f'    <lastmod>{esc(S("lastmod"))}</lastmod>',
        '    <changefreq>monthly</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '</urlset>',
        '',
    ])
    robots = f"User-agent: *\nAllow: /\n\nSitemap: {url}sitemap.xml\n"

    xml_count = len([p for p in CONTENT.rglob("*.xml") if not p.name.startswith("_")])
    print(f"✓ 数据源：{xml_count} 个 XML，{len(papers)} 篇论文"
          f"（清单 index.xml，下一篇编号 {len(papers) + 1}），"
          f"{len(site.findall('filters/filter'))} 个筛选标签")
    filled = sum(1 for p in papers if field(p, "authors"))
    if filled < len(papers):
        print(f"ℹ 作者字段：{filled}/{len(papers)} 篇已填写 "
              f"（在 content/publications/<slug>.xml 的 <authors> 中补，留空则不显示）")
    for w in warnings:
        print(f"⚠ {w}")
    if check_only:
        print("✓ 校验通过（--check，未写文件）")
        return

    (ROOT / "index.html").write_text(html_text, encoding="utf-8", newline="\n")
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8", newline="\n")
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8", newline="\n")
    print(f"✓ 已生成 index.html ({len(html_text.encode('utf-8'))} B) / sitemap.xml / robots.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从 content/*.xml 构建静态学术主页")
    parser.add_argument("--check", action="store_true", help="只校验数据源与模板，不写文件")
    parser.add_argument("--list", action="store_true", help="列出论文总数、编号、文件名与标题")
    args = parser.parse_args()
    try:
        build(check_only=args.check, list_only=args.list)
    except BuildError as exc:
        raise SystemExit(f"✗ 构建失败：{exc}")
