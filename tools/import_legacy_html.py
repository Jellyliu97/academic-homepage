#!/usr/bin/env python3
"""一次性迁移脚本：从旧版 index.html 抽取「常变内容」，生成 content/*.xml。

日常不需要运行它；它只是把 951 行单文件 HTML 无损拆成 XML 数据源。
用法：python tools/import_legacy_html.py
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape as xesc

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "index.html").read_text(encoding="utf-8")
OUT = ROOT / "content"
PUBS = OUT / "publications"
PUBS.mkdir(parents=True, exist_ok=True)


def plain(value: str) -> str:
    """HTML 文本节点 -> XML 文本节点（先还原实体，再按 XML 转义）。"""
    return xesc(html.unescape((value or "").strip()))


def rich(value: str) -> str:
    """HTML 片段 -> CDATA，原样保留标签与 &nbsp; 等实体。"""
    value = (value or "").strip().replace("]]>", "]]]]><![CDATA[>")
    return "<![CDATA[" + value + "]]>"


def node(tag: str, value: str, *, is_rich: bool = False, attrs: str = "") -> str:
    return f"  <{tag}{attrs}>{rich(value) if is_rich else plain(value)}</{tag}>\n"


def grab(pattern: str, text: str, default: str = "") -> str:
    m = re.search(pattern, text, re.S)
    return m.group(1).strip() if m else default


def write(path: Path, body: str) -> None:
    path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + body, encoding="utf-8", newline="\n")
    ET.parse(path)  # 立刻验证 XML 合法
    print(f"  -> {path.relative_to(ROOT)}")


# --------------------------------------------------------------------------
# 1) 论文：一篇一个 XML
# --------------------------------------------------------------------------
rows = re.findall(r'<tr id="pub-([^"]+)"([^>]*)>(.*?)</tr>', SRC, re.S)
assert len(rows) == 29, f"预期 29 篇论文，实际抽到 {len(rows)} 篇"

index_rows: list[tuple[int, str, str]] = []

for order, (slug, attrs, body) in enumerate(rows, 1):
    tags = grab(r'data-tags="([^"]+)"', attrs, "")
    featured = "pub-featured" in attrs
    title_url = grab(r'<a href="([^"]+)"[^>]*>\s*<papertitle>', body)
    title = grab(r"<papertitle>(.*?)</papertitle>", body)
    topic = grab(r'<span class="pub-topic">(.*?)</span>', body)
    venue = grab(r"<em><strong>(.*?)</strong></em>", body)
    role = grab(r'<span class="pub-role">(.*?)</span>', body)
    note = grab(r'<span class="pub-note">(.*?)</span>', body)
    image = grab(r'<img class="pub-thumb" src="([^"]+)"', body)
    image_alt = grab(r'<img class="pub-thumb"[^>]*alt="([^"]+)"', body)
    links_html = grab(r'<div class="pub-links">(.*?)</div>', body)
    links = re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', links_html, re.S)

    x = '<!-- 一篇论文 = 一个文件；顺序由 content/publications/index.xml 决定，本文件不写 order。 -->\n'
    x += f'<paper id="{plain(slug)}"'
    if featured:
        x += ' featured="true"'
    x += f' tags="{plain(tags)}">\n'
    x += node("title", title)
    x += "  <authors></authors>  <!-- 作者名单，留空不显示；可用 CDATA 写 HTML -->\n"
    x += node("topic", topic)
    x += node("venue", venue)
    if role:
        x += node("role", role)
    if note:
        x += node("note", note)
    x += node("image", image)
    x += node("imageAlt", image_alt)
    if title_url:
        x += node("titleUrl", title_url)
    if links:
        x += "  <links>\n"
        for href, label in links:
            x += f'    <link label="{plain(label)}" href="{plain(href)}"/>\n'
        x += "  </links>\n"
    x += "</paper>\n"
    write(PUBS / f"{slug}.xml", x)
    index_rows.append((order, f"{slug}.xml", title))


# --------------------------------------------------------------------------
# 论文总清单（行顺序 = 页面顺序）
# --------------------------------------------------------------------------
index_body = "".join(
    f'  <paper order="{o}" file="{plain(f)}" title="{plain(tp)}"/>\n'
    for o, f, tp in index_rows
)
write(PUBS / "index.xml",
      '<!-- 论文总清单：行顺序 = 页面顺序，order 是给人看的编号。 -->\n'
      "<publications>\n" + index_body + "</publications>\n")


# --------------------------------------------------------------------------
# 2) 站点级配置
# --------------------------------------------------------------------------
buttons = re.findall(r'<button class="tag-btn[^"]*" data-tag="([^"]+)">([^<]+)</button>', SRC)
assert len(buttons) == 8, f"预期 8 个筛选标签，实际 {len(buttons)} 个"

nav_items = re.findall(r'<a href="([^"]+)"([^>]*)>([^<]+)</a>', grab(r'<span class="site-nav-links">(.*?)</span>', SRC))

pub_intro = grab(r"(<p>Author positions are shown.*?</p>)", SRC)
jsonld_text = grab(r'<script type="application/ld\+json">(.*?)</script>', SRC)
jsonld = json.loads(jsonld_text)
person = next(n for n in jsonld["@graph"] if n["@type"] == "Person")

filters = "".join(f'    <filter key="{plain(k)}" label="{plain(v.strip())}"/>\n' for k, v in buttons)
nav_xml = "".join(
    f'    <item label="{plain(label)}" href="{plain(href)}"'
    + (' external="true"' if "target=" in extra else "")
    + "/>\n"
    for href, extra, label in nav_items
)
expertise = "".join(f"    <topic>{plain(t)}</topic>\n" for t in person["knowsAbout"])

site_xml = f"""<!-- 站点级配置：网址、SEO、导航、筛选标签、页脚。改网址只改 <url> 一处。 -->
<site>
  <url>https://jellyliu97.github.io/academic-homepage/</url>
  <title>Guodong Liu (Eric Liu) | Academic Homepage, Nanjing University</title>
  <author>Guodong Liu (Eric Liu)</author>
  <description>Guodong Liu (Eric Liu) is a Ph.D. student in computer science at the State Key Laboratory for Novel Software Technology, Nanjing University. Research on mobile and acoustic sensing, speech reconstruction, mmWave radar, trustworthy voice, embodied intelligence and AI for medicine.</description>
  <keywords>Guodong Liu, Eric Liu, Nanjing University, State Key Laboratory for Novel Software Technology, academic homepage, mobile sensing, speech reconstruction, accelerometer, mmWave radar, embodied intelligence, AI for medicine, MobiCom, UbiComp, IMWUT, CHI, NSDI</keywords>
  <robots>index, follow, max-image-preview:large, max-snippet:-1</robots>
  <themeColor>#294f5c</themeColor>
  <ogSiteName>Guodong Liu (Eric Liu) - Academic Homepage</ogSiteName>
  <ogDescription>Ph.D. student at Nanjing University working on sensing, recognition and cognition toward embodied intelligence and AI agents.</ogDescription>
  <ogImageAlt>Portrait of Guodong Liu (Eric Liu)</ogImageAlt>
  <twitterTitle>Guodong Liu (Eric Liu) | Academic Homepage</twitterTitle>
  <twitterDescription>Ph.D. student at Nanjing University. Mobile sensing, speech reconstruction, mmWave radar, embodied intelligence and AI for medicine.</twitterDescription>
  <inLanguage>en</inLanguage>
  <lastmod>2026-11-10</lastmod>
  <lastUpdatedText>November 10, 2026</lastUpdatedText>

  <nav>
{nav_xml}  </nav>

  <filters>
{filters}  </filters>

  <publicationsIntro>{rich(pub_intro)}</publicationsIntro>

  <footer>
    <title>Keep Exploring</title>
    <subtitle>From sensing and recognition to embodied intelligence and AI agents.</subtitle>
    <ctaLabel>Get in Touch</ctaLabel>
    <footnote><![CDATA[Guodong Liu (Eric Liu) &nbsp;|&nbsp; Nanjing University]]></footnote>
    <credit><![CDATA[&copy; 2026 Guodong Liu. Content hosted on GitHub Pages.]]></credit>
  </footer>
</site>
"""
write(OUT / "site.xml", site_xml)


# --------------------------------------------------------------------------
# 3) 个人简介 / 联系方式
# --------------------------------------------------------------------------
bio = grab(r'(<p>\s*I am a third-year Ph\.D\..*?<p><strong>My current research interests include</strong></p>)', SRC)
interests_html = grab(r'<ol class="interests-list">(.*?)</ol>', SRC)
interests = re.findall(r"<li>(.*?)</li>", interests_html, re.S)
tagline = grab(r'<p class="profile-tagline">(.*?)</p>', SRC)
copy_bio = grab(r'copyText\("(Guodong Liu \(Eric Liu\) is a third-year.*?)", e\)', SRC)

profile_xml = f"""<!-- 个人简介、研究兴趣、联系方式。带 <![CDATA[ ... ]]> 的字段可直接写 HTML。 -->
<profile>
  <name>Guodong Liu (Eric Liu)</name>
  <givenName>{plain(person["givenName"])}</givenName>
  <familyName>{plain(person["familyName"])}</familyName>
  <alias>Eric Liu</alias>
  <jobTitle>{plain(person["jobTitle"])}</jobTitle>
  <shortDescription>{plain(person["description"])}</shortDescription>
  <tagline>{rich(tagline)}</tagline>
  <bio>{rich(bio)}</bio>
  <copyBio>{plain(copy_bio)}</copyBio>
  <photo src="images/portrait.png" alt="Portrait of Guodong Liu (Eric Liu)"/>

  <interests>
{''.join(f'    <item>{rich(i)}</item>' + chr(10) for i in interests)}  </interests>

  <university>{plain(person["affiliation"]["name"])}</university>
  <universityUrl>{plain(person["affiliation"]["sameAs"])}</universityUrl>
  <lab>{plain(person["affiliation"]["department"]["name"])}</lab>
  <city>{plain(person["address"]["addressLocality"])}</city>
  <country>{plain(person["address"]["addressCountry"])}</country>
  <countryName>China</countryName>
  <location><![CDATA[&#128205; Nanjing, China]]></location>

  <primaryEmail>Jellyliu97@foxmail.com</primaryEmail>
  <secondaryEmail>EricLiu@smail.nju.edu.cn</secondaryEmail>
  <links>
    <link kind="cv" label="CV" title="Curriculum Vitae" href="https://jellyliu97.github.io/cv/"/>
    <link kind="scholar" label="Google Scholar" title="Google Scholar" href="https://scholar.google.com/citations?hl=zh-CN&amp;user=ysxUnXsAAAAJ"/>
    <link kind="github" label="GitHub" title="GitHub" href="https://github.com/Jellyliu97"/>
  </links>

  <expertise>
{expertise}  </expertise>
</profile>
"""
write(OUT / "profile.xml", profile_xml)


# --------------------------------------------------------------------------
# 4) News / Service / Awards / Experience / Projects
#    （Contact 区块不单独存 XML：邮箱与外链已在 profile.xml 中，由 build.py 生成）
# --------------------------------------------------------------------------
news_items = re.findall(
    r'<li class="news-entry"><span class="news-date-badge">(.*?)</span>\s*(.*?)</li>',
    grab(r'<ul class="news-plain">(.*?)</ul>', SRC), re.S,
)
assert len(news_items) == 7, f"预期 7 条 News，实际 {len(news_items)} 条"


def simple_list(section_id: str) -> list[str]:
    block = grab(r'<section id="' + section_id + r'".*?<ul class="detail-list">(.*?)</ul>', SRC)
    return re.findall(r"<li[^>]*>(.*?)</li>", block, re.S)


def list_xml(root_tag: str, items: list[str], *, comment: str) -> str:
    body = "".join(f"  <item>{rich(i)}</item>\n" for i in items)
    return f"<!-- {comment} -->\n<{root_tag}>\n{body}</{root_tag}>\n"


write(OUT / "news.xml",
      '<!-- 一条 News = 一个 <item>；date 显示在日期徽标里，正文可直接写 HTML。 -->\n<news>\n'
      + "".join(f'  <item date="{plain(d)}">{rich(t)}</item>\n' for d, t in news_items)
      + "</news>\n")

write(OUT / "service.xml", list_xml("service", simple_list("service"), comment="学术服务 / 教学"))
write(OUT / "awards.xml", list_xml("awards", simple_list("awards"), comment="奖项与荣誉"))

exp_rows = re.findall(r"<tr>(.*?)</tr>", grab(r'<section id="experience".*?<tbody>(.*?)</tbody>', SRC), re.S)
exp_parts = []
for r in exp_rows:
    logo = grab(r'<img src="([^"]+)"', r)
    logo_alt = grab(r'<img[^>]*alt="([^"]+)"', r)
    body_html = grab(r'<td class="exp-body">(.*?)</td>', r)
    exp_parts.append(
        f'  <item logo="{plain(logo)}" logoAlt="{plain(logo_alt)}">\n'
        f'    <body>{rich(body_html)}</body>\n'
        "  </item>\n"
    )
write(OUT / "experience.xml",
      "<!-- 工作 / 实习经历；<body> 里直接写 HTML（<br>、<strong> 均可）。 -->\n<experience>\n"
      + "".join(exp_parts) + "</experience>\n")

project_text = grab(r'<p class="project-note">(.*?)</p>', SRC)
project_only = project_text.split("Click a direction")[0].strip()
cloud_json = grab(r"const myProjects = (\[.*?\]);", SRC)
cloud = json.loads(cloud_json)
cloud_xml = "".join(f'    <item name="{plain(p["name"])}" tag="{plain(p["tag"])}"/>\n' for p in cloud)
write(OUT / "projects.xml", f"""<!-- 研究项目：一条 <item> = 一行；<hint> 是词云上方居中提示。 -->
<projects>
  <items>
    <item date="2026">{rich(project_only)}</item>
  </items>
  <hint><![CDATA[Click a direction below to filter the publication list]]></hint>
  <cloud>
{cloud_xml}  </cloud>
</projects>
""")

print(f"\n完成：{len(rows)} 篇论文 + {len(list(OUT.glob('*.xml')))} 个区块 XML。")
