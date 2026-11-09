# Guodong Liu (Eric Liu) — Academic Homepage

Personal academic homepage for **Guodong Liu (Eric Liu)**, a Ph.D. student in computer
science at the **State Key Laboratory for Novel Software Technology, Nanjing University**.
Content is mirrored from <https://jellyliu97.github.io/homepage/> and rendered with a
static, single-page HTML template.

**Live URL (once GitHub Pages is enabled):**
<https://jellyliu97.github.io/academic-homepage/>

## Local preview

```bash
python3 -m http.server 8080 --bind 127.0.0.1
# open http://127.0.0.1:8080/
```

## What's in the page

`index.html` contains: profile / research interests / contact links → News →
Publications (29 entries with a topic filter) → Work and Intern Experiences →
Research Projects & Directions (interactive tag cloud) → Service and Teaching →
Awards and Honors → Contact Me → footer.

The page is plain static HTML: all content is in the markup (not injected by JS), so
search engines can index the full publication list.

## Images — replace these at your convenience

Every image already exists as a neutral placeholder with the **exact final filename**,
so you can simply overwrite the file; no HTML edits are required.

| File | Replace with |
| --- | --- |
| `images/portrait.png` | Your portrait photo (recommended ~600×760, portrait) |
| `images/institute.svg` | Nanjing University / company logo (currently a generic emblem) |
| `images/favicon.svg` | Your own favicon (currently a "GL" monogram) |
| `images/paper/<slug>.png` | Teaser figure for each paper — 29 files |
| `images/experience/background-*.webp`, `background.jpeg` | Footer landscape (optional) |
| `images/icon/cursor*.png` | Custom cursor (optional) |

To map a placeholder to a paper, search `index.html` for `id="pub-<slug>"`; the image
directly below it is `images/paper/<slug>.png`. For example,
`id="pub-mobicom2026-accspeech"` → `images/paper/mobicom2026-accspeech.png`.
If you prefer a different format (e.g. `.jpg`), just update that one `src`.

## Make it public and discoverable

1. **Enable GitHub Pages** — repo `Jellyliu97/academic-homepage` →
   `Settings` → `Pages` → `Build and deployment` → `Deploy from a branch` →
   branch `main`, folder `/ (root)` → `Save`. Wait ~1 minute, then check the URL above.
   (`.nojekyll` is already present so GitHub serves the files verbatim.)
2. **Set the repo so people can find it** — add a short description and set the
   website field to the live URL in the repo's "About" section; update your GitHub
   profile README and Google Scholar "Homepage" field with the same link.
3. **Google Search Console** — create a *URL prefix* property for
   `https://jellyliu97.github.io/academic-homepage/`. Copy the verification code into
   `<meta name="google-site-verification" content="YOUR_CODE">` in the `<head>` of
   `index.html` (there is a comment marking the spot), push, then verify.
   Submit `https://jellyliu97.github.io/academic-homepage/sitemap.xml` and request
   indexing for the homepage.
4. **Bing Webmaster Tools** — import the property from Search Console, or submit the
   sitemap directly. Also add the link to your ORCID / DBLP / old
   `jellyliu97.github.io/homepage/` site; inbound links are the fastest way to get
   a new GitHub Pages site crawled.

Note: with a project page (`/academic-homepage/`), crawlers read the host-level
`robots.txt`, not this subpath one. Submitting the sitemap in Search Console is the
authoritative step; `robots.txt` is kept for custom-domain / root-site use.

### If you rename the repo to `Jellyliu97.github.io`

The site would then live at `https://jellyliu97.github.io/`. Replace
`https://jellyliu97.github.io/academic-homepage/` with `https://jellyliu97.github.io/`
in these four places: `index.html` (canonical, og:url, og:image, twitter:image, JSON-LD),
`sitemap.xml`, `robots.txt`, and this README.

## Updating content

- Text, papers, news, awards and links: edit `index.html` directly.
- Research-topic filter buttons and publication `data-tags` must use the same tag keys
  (`speech`, `sensing`, `rf`, `security`, `medical`, `meta`, `embodied`).
- Tag-cloud entries live in the `myProjects` array in `index.html`.
- After any content change, update `Last updated` in the footer, `<lastmod>` in
  `sitemap.xml`, and `dateModified` in the JSON-LD block.
