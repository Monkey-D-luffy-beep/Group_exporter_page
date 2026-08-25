#!/usr/bin/env python3
"""Static page generator for groupexporter.nexoraai.co.in.

Reads Markdown files from content/ and writes static HTML into blog/, then
regenerates blog/index.html and sitemap.xml.

No third-party dependencies, matching the other generators in this project
(make_locales.py, make_icons.py, make_store_assets.py).

    python make_pages.py            build everything
    python make_pages.py --check    parse and validate, write nothing

Front matter (between --- fences at the top of each .md file):

    title:       <str>   required. The <title> and <h1>.
    description: <str>   required. Meta description. 140-165 chars.
    slug:        <str>   required. Output filename, no extension.
    date:        <str>   required. YYYY-MM-DD.
    updated:     <str>   optional. Defaults to date.
    template:    guide | alternatives     default: guide
    keywords:    <str>   optional, comma separated.
    related:     <list>  optional, slugs. Auto-filled if omitted.
    takeaways:   <list>  optional, "Point :: detail" pairs.
    faq:         <list>  optional, "Question :: answer" pairs -> FAQPage schema.

Body Markdown supported: ## / ### headings, paragraphs, - and 1. lists,
> blockquotes, pipe tables, **bold**, `code`, [links](/url), and --- rules.
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import date as _date
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "blog"

SITE = "https://groupexporter.nexoraai.co.in"
BRAND = "Group Contacts Exporter"
STORE = ("https://chromewebstore.google.com/detail/"
         "group-contacts-exporter-%E2%80%94/kmegeibfadlmgejfedidcamnbljekkkp")
RESEARCH = "/whatsapp-group-export-blank-numbers.html"
SOCIAL = f"{SITE}/assets/banner-social.webp"

VALID_TEMPLATES = {"guide", "alternatives"}


# --------------------------------------------------------------------------
# Front matter
# --------------------------------------------------------------------------

def parse_front_matter(raw: str, source: Path) -> tuple[dict, str]:
    if not raw.startswith("---"):
        raise ValueError(f"{source.name}: file must open with a --- front matter fence")
    _, fm, body = raw.split("---", 2)

    meta: dict = {}
    key = None
    for line in fm.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("- ") and key:
            meta.setdefault(key, [])
            if not isinstance(meta[key], list):
                raise ValueError(f"{source.name}: '{key}' mixes a scalar and list items")
            meta[key].append(line.lstrip()[2:].strip())
            continue
        if ":" not in line:
            raise ValueError(f"{source.name}: cannot parse front matter line: {line!r}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        meta[key] = value if value else []

    for required in ("title", "description", "slug", "date"):
        if not meta.get(required):
            raise ValueError(f"{source.name}: missing required front matter '{required}'")

    meta.setdefault("template", "guide")
    if meta["template"] not in VALID_TEMPLATES:
        raise ValueError(f"{source.name}: unknown template {meta['template']!r}")
    meta.setdefault("updated", meta["date"])
    for list_key in ("related", "takeaways", "faq"):
        meta.setdefault(list_key, [])
        if isinstance(meta[list_key], str):
            raise ValueError(f"{source.name}: '{list_key}' must be a list of - items")

    return meta, body.strip()


def split_pair(item: str, source: str, field: str) -> tuple[str, str]:
    if "::" not in item:
        raise ValueError(f"{source}: {field} entry needs 'Left :: right': {item!r}")
    left, right = item.split("::", 1)
    return left.strip(), right.strip()


# --------------------------------------------------------------------------
# Markdown subset -> HTML
# --------------------------------------------------------------------------

def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)
    return out


def render_table(rows: list[str]) -> str:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    header, body = cells[0], cells[2:]          # cells[1] is the --- separator
    head = "".join(f"<th>{inline(c)}</th>" for c in header)
    out = [f'<div class="data-table-wrap"><table class="data-table">',
           f"<thead><tr>{head}</tr></thead><tbody>"]
    for row in body:
        tds = "".join(f"<td>{inline(c)}</td>" for c in row)
        out.append(f"<tr>{tds}</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def markdown(text: str) -> str:
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
        elif stripped.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(render_table(block))
        elif stripped.startswith("### "):
            out.append(f"<h3>{inline(stripped[4:])}</h3>")
            i += 1
        elif stripped.startswith("## "):
            out.append(f"<h2>{inline(stripped[3:])}</h2>")
            i += 1
        elif stripped == "---":
            out.append('<hr class="prose-rule" />')
            i += 1
        elif stripped.startswith("> "):
            block = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                block.append(lines[i].strip()[2:])
                i += 1
            out.append(f'<blockquote class="keytake"><p>{inline(" ".join(block))}</p></blockquote>')
        elif stripped.startswith("- ") or re.match(r"^\d+\. ", stripped):
            ordered = bool(re.match(r"^\d+\. ", stripped))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines):
                s = lines[i].strip()
                if ordered and re.match(r"^\d+\. ", s):
                    items.append(re.sub(r"^\d+\. ", "", s))
                elif not ordered and s.startswith("- "):
                    items.append(s[2:])
                else:
                    break
                i += 1
            body = "".join(f"<li>{inline(x)}</li>" for x in items)
            out.append(f"<{tag}>{body}</{tag}>")
        else:
            block = []
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^\s*(\||#{2,3} |- |\d+\. |> |---$)", lines[i]):
                block.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(block))}</p>")
    return "\n".join(out)


def word_count(text: str) -> int:
    return len(re.sub(r"[#>*`|\[\]()-]", " ", text).split())


# --------------------------------------------------------------------------
# Page shell
# --------------------------------------------------------------------------

def schema_blocks(meta: dict, source: str) -> str:
    url = meta.get("url") or f"{SITE}/blog/{meta['slug']}.html"
    article = {
        "@context": "https://schema.org",
        "@type": meta.get("schema_type", "BlogPosting"),
        "headline": meta["title"],
        "description": meta["description"],
        "url": url,
        "image": SOCIAL,
        "datePublished": meta["date"],
        "dateModified": meta["updated"],
        "author": {"@type": "Organization", "name": "Nexora AI", "url": "https://nexoraai.co.in"},
        "publisher": {"@type": "Organization", "name": "Nexora AI", "url": "https://nexoraai.co.in"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
        ],
    }
    if meta.get("url") != f"{SITE}/blog/":
        crumbs["itemListElement"].append(
            {"@type": "ListItem", "position": 3, "name": meta["title"]})
    blocks = [article, crumbs]

    if meta["faq"]:
        blocks.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in (split_pair(x, source, "faq") for x in meta["faq"])
            ],
        })

    return "\n".join(
        '  <script type="application/ld+json">\n  '
        + json.dumps(b, indent=2, ensure_ascii=False).replace("\n", "\n  ")
        + "\n  </script>"
        for b in blocks
    )


def takeaways_html(meta: dict, source: str) -> str:
    if not meta["takeaways"]:
        return ""
    rows = "".join(
        f"<tr><td><strong>{inline(p)}</strong></td><td>{inline(d)}</td></tr>"
        for p, d in (split_pair(x, source, "takeaways") for x in meta["takeaways"])
    )
    return (
        '<h2 id="key-takeaways">Key takeaways</h2>\n'
        '<div class="data-table-wrap"><table class="data-table">'
        "<thead><tr><th>Point</th><th>Detail</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )


def faq_html(meta: dict, source: str) -> str:
    if not meta["faq"]:
        return ""
    items = "".join(
        f'<details class="faq-item"><summary>{inline(q)}</summary><p>{inline(a)}</p></details>'
        for q, a in (split_pair(x, source, "faq") for x in meta["faq"])
    )
    return f'<h2 id="faq">Frequently asked questions</h2>\n<div class="faq-list">{items}</div>'


def cta_html(meta: dict) -> str:
    if meta["template"] == "alternatives":
        line = ("Every figure on this page comes from reading WhatsApp Web's own local "
                "storage, not from a vendor's marketing copy. If a complete member list "
                "with no monthly cap is what you need, that is what this tool does.")
    else:
        line = ("Group Contacts Exporter does exactly this, free and with no export cap. "
                "It reads WhatsApp Web's own local storage rather than the rendered page, "
                "so the roster is complete without opening or scrolling the group.")
    return (
        '<div class="post-cta">'
        f"<p>{line}</p>"
        f'<a class="btn btn-primary btn-large" href="{STORE}" target="_blank" '
        'rel="noopener">Add to Chrome — It\'s Free</a>'
        "</div>"
    )


def related_html(meta: dict, index: dict[str, dict]) -> str:
    slugs = meta["related"] or [
        s for s in index
        if s != meta["slug"]
    ][:3]
    cards = []
    for slug in slugs[:3]:
        other = index.get(slug)
        if not other:
            continue
        cards.append(
            f'<a class="post-card" href="/blog/{slug}.html">'
            f'<h3>{inline(other["title"])}</h3>'
            f'<p>{inline(other["description"][:110])}…</p></a>'
        )
    if not cards:
        return ""
    return f'<h2>More from the blog</h2>\n<div class="post-grid">{"".join(cards)}</div>'


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title_tag}</title>
  <meta name="description" content="{description}" />
{keywords}  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{url}" />

  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="{brand}" />
  <meta property="og:title" content="{title_tag}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{social}" />
  <meta property="article:published_time" content="{date}" />
  <meta property="article:modified_time" content="{updated}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{description}" />
  <meta name="twitter:image" content="{social}" />

  <link rel="icon" href="/assets/icon.webp" type="image/webp" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/css/style.css" />
  <link rel="stylesheet" href="/css/post.css" />

{schema}
</head>
<body>

  <a class="skip-link" href="#main">Skip to main content</a>

  <header class="site-header">
    <div class="container nav-inner">
      <a href="/" class="brand" aria-label="{brand} home">
        <span class="brand-mark"><img src="/assets/icon.webp" alt="" width="34" height="34" /></span>
        <span class="brand-name">{brand}</span>
      </a>
      <nav class="nav-links" aria-label="Primary">
        <a href="/#how-it-works">How it works</a>
        <a href="/#features">Features</a>
        <a href="/#privacy">Privacy</a>
        <a href="/blog/">Blog</a>
        <a href="{research}">Research</a>
        <a href="/#faq">FAQ</a>
      </nav>
      <a class="btn btn-primary btn-small" href="{store}" target="_blank" rel="noopener">Add to Chrome — Free</a>
    </div>
  </header>
"""

FOOT = """
  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        <a href="/" class="brand">
          <span class="brand-mark"><img src="/assets/icon.webp" alt="" width="34" height="34" /></span>
          <span class="brand-name">{brand}</span>
        </a>
        <p class="footer-disclaimer">
          {brand} is an independent tool and is not affiliated with, endorsed by, sponsored by, or connected to WhatsApp LLC, Meta Platforms Inc., or any Meta product. WhatsApp™ is a trademark of WhatsApp LLC, referenced solely to describe compatibility. You are responsible for the lawful use of exported data.
        </p>
      </div>
      <div class="footer-links">
        <a href="{store}" target="_blank" rel="noopener">Chrome Web Store</a>
        <a href="/blog/">Blog</a>
        <a href="{research}">Research: blank numbers</a>
        <a href="/privacy-policy.html">Privacy Policy</a>
        <a href="https://nexoraai.co.in" target="_blank" rel="noopener">Nexora AI</a>
      </div>
    </div>
    <p class="footer-copy">&copy; <span id="year"></span> Nexora AI. All rights reserved.</p>
  </footer>

  <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
</body>
</html>
"""


def render_page(meta: dict, body_md: str, index: dict, source: str) -> str:
    url = f"{SITE}/blog/{meta['slug']}.html"
    kw = (f'  <meta name="keywords" content="{html.escape(meta["keywords"], quote=True)}" />\n'
          if meta.get("keywords") else "")
    head = HEAD.format(
        title_tag=html.escape(f"{meta['title']} — {BRAND}", quote=True),
        title=html.escape(meta["title"], quote=True),
        description=html.escape(meta["description"], quote=True),
        keywords=kw, url=url, brand=BRAND, social=SOCIAL, store=STORE,
        research=RESEARCH, date=meta["date"], updated=meta["updated"],
        schema=schema_blocks(meta, source),
    )
    parts = [
        head,
        '\n  <main id="main">\n    <article class="section">\n      <div class="container prose">',
        '        <nav class="crumbs" aria-label="Breadcrumb">'
        '<a href="/">Home</a> <span>/</span> <a href="/blog/">Blog</a></nav>',
        f'        <h1>{inline(meta["title"])}</h1>',
        f'        <p class="meta-line">Published {meta["date"]}'
        + (f" · Updated {meta['updated']}" if meta["updated"] != meta["date"] else "")
        + f" · {word_count(body_md) // 200 + 1} min read</p>",
        markdown(body_md),
        takeaways_html(meta, source),
        cta_html(meta),
        faq_html(meta, source),
        related_html(meta, index),
        "      </div>\n    </article>\n  </main>",
        FOOT.format(brand=BRAND, store=STORE, research=RESEARCH),
    ]
    return "\n".join(p for p in parts if p)


# --------------------------------------------------------------------------
# Blog index + sitemap
# --------------------------------------------------------------------------

def render_index(posts: list[dict]) -> str:
    cards = "".join(
        f'<a class="post-card" href="/blog/{p["slug"]}.html">'
        f'<h3>{inline(p["title"])}</h3>'
        f'<p>{inline(p["description"][:150])}…</p>'
        f'<span class="post-date">{p["date"]}</span></a>'
        for p in posts
    )
    meta = {
        "title": "Blog", "slug": "", "date": _date.today().isoformat(),
        "updated": _date.today().isoformat(), "template": "guide",
        "description": ("Guides and original research on exporting WhatsApp group "
                        "contacts — what works, what does not, and why."),
        "keywords": "", "related": [], "takeaways": [], "faq": [],
        "url": f"{SITE}/blog/", "schema_type": "Blog",
    }
    head = HEAD.format(
        title_tag=f"Blog — {BRAND}", title="Blog",
        description=html.escape(meta["description"], quote=True), keywords="",
        url=f"{SITE}/blog/", brand=BRAND, social=SOCIAL, store=STORE,
        research=RESEARCH, date=meta["date"], updated=meta["updated"],
        schema=schema_blocks(meta, "index"),
    )
    return (head
            + '\n  <main id="main">\n    <section class="section">\n      <div class="container">'
            + "\n        <h1>Blog</h1>"
            + f'\n        <p class="lede">{inline(meta["description"])}</p>'
            + f'\n        <div class="post-grid">{cards}</div>'
            + "\n      </div>\n    </section>\n  </main>"
            + FOOT.format(brand=BRAND, store=STORE, research=RESEARCH))


def render_sitemap(posts: list[dict]) -> str:
    today = _date.today().isoformat()
    urls = [(f"{SITE}/", today, "weekly", "1.0"),
            (f"{SITE}/blog/", today, "weekly", "0.8"),
            (f"{SITE}{RESEARCH}", "2026-08-19", "monthly", "0.9"),
            (f"{SITE}/support.html", "2026-08-26", "monthly", "0.5"),
            (f"{SITE}/privacy-policy.html", "2026-08-19", "yearly", "0.3")]
    urls += [(f"{SITE}/blog/{p['slug']}.html", p["updated"], "monthly", "0.7") for p in posts]
    body = "\n".join(
        f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>\n"
        f"    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>"
        for loc, mod, freq, pri in urls
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{body}\n</urlset>\n")


# --------------------------------------------------------------------------

def main() -> int:
    # Windows consoles default to cp1252 and will crash on non-ASCII output.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    check_only = "--check" in sys.argv

    if not CONTENT.exists():
        CONTENT.mkdir()
        print(f"created {CONTENT.relative_to(ROOT)}/ — add .md files and re-run")
        return 0

    sources = sorted(CONTENT.glob("*.md"))
    if not sources:
        print("no .md files in content/ — nothing to build")
        return 0

    parsed = []
    for src in sources:
        meta, body = parse_front_matter(src.read_text(encoding="utf-8"), src)
        parsed.append((meta, body, src.name))

    slugs = [m["slug"] for m, _, _ in parsed]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        raise ValueError(f"duplicate slugs: {sorted(dupes)}")

    index = {m["slug"]: m for m, _, _ in parsed}
    posts = sorted((m for m, _, _ in parsed), key=lambda m: m["date"], reverse=True)

    if not check_only:
        OUT.mkdir(exist_ok=True)

    for meta, body, name in parsed:
        page = render_page(meta, body, index, name)
        words = word_count(body)
        flag = "   <-- THIN, under 900 words" if words < 900 else ""
        if not check_only:
            (OUT / f"{meta['slug']}.html").write_text(page, encoding="utf-8")
        print(f"  {meta['slug']:<52} {words:>5} words  {meta['template']}{flag}")

    if not check_only:
        (OUT / "index.html").write_text(render_index(posts), encoding="utf-8")
        (ROOT / "sitemap.xml").write_text(render_sitemap(posts), encoding="utf-8")

    verb = "checked" if check_only else "built"
    print(f"\n{verb} {len(parsed)} page(s)"
          + ("" if check_only else f", blog/index.html and sitemap.xml "
                                   f"({len(posts) + 4} URLs)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
