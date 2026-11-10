#!/usr/bin/env python3
"""一次性迁移脚本：把旧 index.html 的「数据」挖空，只留风格 / 骨架 / 脚本，
生成 index.template.html。配合 build.py 使用；日常不需要运行它。
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / "index.html").read_text(encoding="utf-8")


def sub(pattern: str, repl: str, count: int = 1, *, expand: bool = False) -> None:
    """expand=True 时用 re 的字符串替换（支持 \\1 / \\2 / \\n），否则按字面替换。"""
    global s
    if expand:
        s2, n = re.subn(pattern, repl, s, count=count, flags=re.S)
    else:
        s2, n = re.subn(pattern, lambda _m: repl, s, count=count, flags=re.S)
    assert n == count, f"替换失败（命中 {n}/{count}）：{pattern[:70]}"
    s = s2


# ---- head / SEO -----------------------------------------------------------
sub(r"<title>.*?</title>", "<title>{{site.title}}</title>")
sub(r'<meta name="author" content="[^"]*">', '<meta name="author" content="{{site.author}}">')
sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="{{site.description}}">')
sub(r'<meta name="keywords" content="[^"]*">', '<meta name="keywords" content="{{site.keywords}}">')
sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="{{site.robots}}">')
sub(r'<meta name="theme-color" content="[^"]*">', '<meta name="theme-color" content="{{site.themeColor}}">')
sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="{{site.url}}">')
sub(r'<meta property="og:site_name" content="[^"]*">', '<meta property="og:site_name" content="{{site.ogSiteName}}">')
sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="{{site.title}}">')
sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="{{site.ogDescription}}">')
sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="{{site.url}}">')
sub(r'<meta property="og:image" content="[^"]*">', '<meta property="og:image" content="{{site.url}}images/portrait.png">')
sub(r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="{{site.ogImageAlt}}">')
sub(r'<meta property="profile:first_name" content="[^"]*">', '<meta property="profile:first_name" content="{{profile.givenName}}">')
sub(r'<meta property="profile:last_name" content="[^"]*">', '<meta property="profile:last_name" content="{{profile.familyName}}">')
sub(r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="{{site.twitterTitle}}">')
sub(r'<meta name="twitter:description" content="[^"]*">', '<meta name="twitter:description" content="{{site.twitterDescription}}">')
sub(r'<meta name="twitter:image" content="[^"]*">', '<meta name="twitter:image" content="{{site.url}}images/portrait.png">')
sub(r'<script type="application/ld\+json">.*?</script>',
    '<script type="application/ld+json">\n{{BLOCK:jsonld}}\n  </script>')

# ---- 导航 / 简介 ----------------------------------------------------------
sub(r'<span class="site-nav-brand">.*?</span>', '<span class="site-nav-brand">{{profile.name}}</span>')
sub(r'<span class="site-nav-links">.*?</span>',
    '<span class="site-nav-links">\n        {{BLOCK:nav}}\n      </span>')
sub(r'(<td style="padding:2.5%;width:68%;vertical-align:middle">).*?(</td>)',
    r'\1\n              {{BLOCK:profileText}}\n            \2', expand=True)
sub(r'<img class="profile-photo"[^>]*>',
    '<img class="profile-photo" style="width:85%;max-width:85%;border-radius:8px;"\n'
    '                   alt="{{profile.photoAlt}}" src="{{profile.photoSrc}}">')

# ---- News / Publications --------------------------------------------------
sub(r'<ul class="news-plain">.*?</ul>', '<ul class="news-plain">\n{{BLOCK:news}}\n          </ul>')
sub(r"<p>Author positions are shown.*?</p>", "{{BLOCK:publicationsIntro}}")
sub(r'(<div class="tag-filter" id="tagFilter">).*?(</div>)',
    r'\1\n{{BLOCK:filters}}\n          \2', expand=True)
sub(r'(<table class="publications-table"[^>]*><tbody>).*?(</tbody></table>)',
    r'\1\n{{BLOCK:papers}}\n          \2', expand=True)

# ---- JS 里硬编码的两段文案 ------------------------------------------------
sub(r'copyText\("[^"]*", e\)', 'copyText({{profile.copyBioJs}}, e)')
sub(r"copyText\('[^']*', e\)", "copyText({{profile.primaryEmailJs}}, e)")

# ---- Experience / Projects -----------------------------------------------
sub(r'(<table width="100%" align="center" border="0" cellpadding="10"><tbody>).*?(</tbody></table>)',
    r'\1\n{{BLOCK:experience}}\n          \2', expand=True)
sub(r'<p class="project-note">.*?</p>', "{{BLOCK:projectsIntro}}")
sub(r"const myProjects = \[.*?\];", "const myProjects = {{projects.cloudJson}};")

# ---- Service / Awards / Contact ------------------------------------------
# 三个区块标签相同，必须一次扫描按出现顺序替换；分三次 sub 会反复命中第一个。
detail_names = iter(("service", "awards", "contact"))


def detail_repl(_m: re.Match) -> str:
    name = next(detail_names)
    return '<ul class="detail-list">\n{{BLOCK:' + name + '}}\n          </ul>'


s, n = re.subn(r'<ul class="detail-list">.*?</ul>', detail_repl, s, flags=re.S)
assert n == 3, f"预期 3 个 detail-list 区块，实际 {n} 个"

# ---- Footer ---------------------------------------------------------------
sub(r"<h2>Keep Exploring</h2>", "<h2>{{footer.title}}</h2>")
sub(r'<p class="mountain-sub">.*?</p>', '<p class="mountain-sub">{{footer.subtitle}}</p>')
sub(r'<span>Get in Touch</span>', '<span>{{footer.ctaLabel}}</span>')
sub(r'href="mailto:Jellyliu97@foxmail\.com" class="mountain-cta"',
    'href="mailto:{{profile.primaryEmail}}" class="mountain-cta"')
sub(r'<span>Guodong Liu \(Eric Liu\).*?</span>', '<span>{{footer.footnote}}</span>')
sub(r'<span class="mountain-template">.*?</span>', '<span class="mountain-template">{{footer.credit}}</span>')
sub(r'(<!-- LAST_UPDATED_START -->).*?(<!-- LAST_UPDATED_END -->)',
    r'\1{{site.lastUpdatedText}}\2', expand=True)

# ---- 断言：模板里不应再残留任何内容数据 -----------------------------------
for leftover in ("MobiCom 2026", "Our project", "Jellyliu97@foxmail.com",
                 "Nanjing University</a>", "pub-mobicom2026", "2022 China National"):
    assert leftover not in s, f"模板仍残留数据：{leftover}"

out = ROOT / "index.template.html"
out.write_text(s, encoding="utf-8", newline="\n")
print(f"已生成 {out.name}：{len(s.splitlines())} 行（原 index.html 951 行）")
