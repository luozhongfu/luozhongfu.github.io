from datetime import date
from pathlib import Path

root = Path(__file__).resolve().parents[1]
pages = []
for p in sorted(root.rglob("*")):
    if ".git" in p.parts or "tools" in p.parts:
        continue
    if p.suffix.lower() not in {".html", ".md", ".txt", ".json", ".xml"}:
        continue
    rel = p.relative_to(root).as_posix()
    if rel == "index.html":
        url = "https://luozhongfu.github.io/"
    elif rel.endswith("/index.html"):
        url = "https://luozhongfu.github.io/" + rel[: -len("index.html")]
    else:
        url = "https://luozhongfu.github.io/" + rel
    pages.append(url)

today = date.today().isoformat()
lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
]
for u in pages:
    pri = "1.0" if u == "https://luozhongfu.github.io/" else "0.7"
    lines += [
        "  <url>",
        f"    <loc>{u}</loc>",
        f"    <lastmod>{today}</lastmod>",
        "    <changefreq>weekly</changefreq>",
        f"    <priority>{pri}</priority>",
        "  </url>",
    ]
lines.append("</urlset>")
(root / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("urls", len(pages))
