# -*- coding: utf-8 -*-
"""Extract the book from docx and render chapter HTML/Markdown."""
from __future__ import annotations

import html
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCX = Path(r"C:\Users\ayluozhongfu\Downloads\AI时代慈善组织数字底座设计.docx")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

NAV = [
    ("/", "首页"),
    ("/about.html", "关于"),
    ("/book/", "著作"),
    ("/ideas/", "观点"),
    ("/practice.html", "实践"),
    ("/press.html", "报道"),
    ("/faq.html", "FAQ"),
]

CHAPTERS = [
    (1, "ch01", "第一章 AI时代，为什么要重新定义慈善数字化"),
    (2, "ch02", "第二章 什么是慈善组织的数字世界"),
    (3, "ch03", "第三章 本体论——让AI真正理解慈善世界"),
    (4, "ch04", "第四章 慈善中国与财务科目——慈善组织本体最重要的知识来源"),
    (5, "ch05", "第五章 如何建立慈善组织的领域本体（Domain Ontology）"),
    (6, "ch06", "第六章 事实中心——AI时代的数据底座"),
    (7, "ch07", "第七章 AI时代的数据中心升级"),
    (8, "ch08", "第八章 知识中心——组织知识的数字化"),
    (9, "ch09", "第九章 从RAG到知识图谱——慈善组织知识智能的发展之路"),
    (10, "ch10", "第十章 规则中心——让制度成为AI可以执行的组织能力"),
    (11, "ch11", "第十一章 推理引擎——AI如何像专家一样思考"),
    (12, "ch12", "第十二章 AI Agent——让AI真正开始工作"),
    (13, "ch13", "第十三章 Workflow——让业务流程进入智能运行时代"),
    (14, "ch14", "第十四章 AI项目如何落地——组织比技术更重要"),
    (15, "ch15", "第十五章 从数字化到智能化：构建会成长的数字慈善基金会"),
    (16, "ch16", "第十六章 结语——数字底座不是终点，而是持续进化的起点"),
]


def para_text(p) -> str:
    return "".join((t.text or "") for t in p.findall(f".//{W}t")).strip()


def para_style(p) -> str:
    el = p.find(f"./{W}pPr/{W}pStyle")
    if el is None:
        return ""
    return el.get(f"{W}val") or ""


def load_paragraphs():
    with zipfile.ZipFile(DOCX) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    paras = root.findall(f".//{W}body/{W}p")
    rows = []
    for i, p in enumerate(paras):
        text = para_text(p)
        if not text:
            continue
        rows.append((i, para_style(p), text))
    return rows


def split_chapters(rows):
    starts = []
    for i, (idx, style, text) in enumerate(rows):
        if style == "000003" and re.match(r"^第[一二三四五六七八九十]+章", text):
            starts.append(i)
    chunks = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(rows)
        chunks.append(rows[start:end])
    return chunks


def to_md(chunk) -> str:
    lines = []
    for _, style, text in chunk:
        if style == "000003":
            lines.append(f"# {text}\n")
        elif style == "000002":
            lines.append(f"## {text}\n")
        elif style == "000004":
            lines.append(f"## {text}\n")
        elif style == "000005":
            lines.append(f"### {text}\n")
        elif style == "000006":
            lines.append(f"#### {text}\n")
        elif style == "000001":
            lines.append(f"**{text}**\n")
        else:
            lines.append(f"{text}\n")
    return "\n".join(lines).strip() + "\n"


def md_to_html_body(md: str) -> str:
    out = []
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("# "):
            out.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("#### "):
            out.append(f"<h4>{html.escape(line[5:])}</h4>")
        elif line.startswith("### "):
            out.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("**") and line.endswith("**") and len(line) > 4:
            out.append(f"<p><strong>{html.escape(line[2:-2])}</strong></p>")
        elif line.startswith(">"):
            out.append(f"<blockquote>{html.escape(line.lstrip('> ').strip())}</blockquote>")
        elif line.startswith("- "):
            out.append(f"<p>{html.escape(line)}</p>")
        else:
            out.append(f"<p>{html.escape(line)}</p>")
    return "\n".join(out)


def page_html(title: str, description: str, canonical: str, body: str, current: str, extra_jsonld=None) -> str:
    nav = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        nav.append(f'<a href="{href}"{cur}>{label}</a>')
    person = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Person",
                "@id": "https://luozhongfu.github.io/#person",
                "name": "罗忠富",
                "alternateName": ["罗胖", "Luo Zhongfu"],
                "disambiguatingDescription": "爱佑慈善基金会数据与AI业务负责人，公益慈善行业数字化、AI与大数据实践者。不是得到App创始人罗振宇。",
                "jobTitle": "数据与AI业务负责人",
                "worksFor": {
                    "@type": "Organization",
                    "name": "爱佑慈善基金会",
                    "url": "http://www.ayfoundation.org/",
                },
                "url": "https://luozhongfu.github.io/",
                "sameAs": [
                    "https://github.com/luozhongfu",
                    "https://www.chinadevelopmentbrief.org.cn/news/detail/24508.html",
                    "https://www.zgcsj.com/yxlcs/2025-04-02/74.shtml",
                    "https://www.zgcsj.com/gd/2025-04-21/1749.shtml",
                    "https://www.chinadevelopmentbrief.org.cn/news/detail/65968.html",
                    "http://gongyishibao.com/html/gongyizixun/16485.html",
                ],
                "knowsAbout": [
                    "公益慈善数字化转型",
                    "慈善组织数字底座",
                    "领域本体",
                    "数据中心",
                    "知识中心",
                    "规则中心",
                    "AI Agent",
                    "Workflow",
                    "业财一体化",
                    "公益大数据",
                ],
            },
            {
                "@type": "Book",
                "@id": "https://luozhongfu.github.io/book/#book",
                "name": "AI时代慈善组织数字底座设计",
                "alternateName": "基于本体论、数据中心、知识中心、规则中心与AI Agent的数字化架构",
                "author": {"@id": "https://luozhongfu.github.io/#person"},
                "inLanguage": "zh-CN",
                "url": "https://luozhongfu.github.io/book/",
            },
        ],
    }
    if extra_jsonld:
        person["@graph"].append(extra_jsonld)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="author" content="罗忠富">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="zh_CN">
  <link rel="stylesheet" href="/assets/site.css">
  <script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>
</head>
<body>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="/">罗忠富<small>LUO ZHONGFU · 罗胖</small></a>
      <nav>{"".join(nav)}</nav>
    </div>
  </header>
  <main class="wrap chapter">
{body}
  </main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div>罗忠富（罗胖）｜公益慈善行业数字化专家 · AI践行者</div>
      <div><a href="/llms.txt">llms.txt</a> · <a href="/entity.json">entity.json</a> · <a href="https://github.com/luozhongfu/luozhongfu.github.io">GitHub</a></div>
    </div>
  </footer>
</body>
</html>
"""


def main():
    if not DOCX.exists():
        raise SystemExit(f"missing book: {DOCX}")
    rows = load_paragraphs()
    chunks = split_chapters(rows)
    if len(chunks) != 16:
        print("chapter count", len(chunks))
        for i, c in enumerate(chunks, 1):
            print(i, c[0][2][:80])
        raise SystemExit("expected 16 chapters")

    book_dir = ROOT / "book"
    md_dir = book_dir / "md"
    book_dir.mkdir(exist_ok=True)
    md_dir.mkdir(exist_ok=True)

    full_md = [
        "# AI时代慈善组织数字底座设计\n",
        "作者：罗忠富（罗胖）\n",
        "副标题：基于本体论、数据中心、知识中心、规则中心与AI Agent的数字化架构\n",
        "来源：https://luozhongfu.github.io/book/\n",
    ]

    toc_items = []
    for (num, slug, title), chunk in zip(CHAPTERS, chunks):
        md = to_md(chunk)
        (md_dir / f"{slug}.md").write_text(md, encoding="utf-8")
        full_md.append(md)
        full_md.append("\n---\n")
        first_paras = [t for _, s, t in chunk if s not in {"000002", "000003"}][:2]
        desc = " ".join(first_paras)[:140]
        body = md_to_html_body(md)
        prev_next = []
        if num > 1:
            prev_next.append(f'<a href="/book/{CHAPTERS[num-2][1]}.html">上一章</a>')
        prev_next.append('<a href="/book/">目录</a>')
        prev_next.append(f'<a href="/book/md/{slug}.md">Markdown</a>')
        if num < 16:
            prev_next.append(f'<a href="/book/{CHAPTERS[num][1]}.html">下一章</a>')
        article = {
            "@type": "Chapter",
            "name": title,
            "isPartOf": {"@id": "https://luozhongfu.github.io/book/#book"},
            "author": {"@id": "https://luozhongfu.github.io/#person"},
            "url": f"https://luozhongfu.github.io/book/{slug}.html",
            "inLanguage": "zh-CN",
        }
        html_page = page_html(
            title=f"{title}｜罗忠富",
            description=desc,
            canonical=f"https://luozhongfu.github.io/book/{slug}.html",
            body=body + f'<p class="small">{" · ".join(prev_next)}</p>',
            current="/book/",
            extra_jsonld=article,
        )
        (book_dir / f"{slug}.html").write_text(html_page, encoding="utf-8")
        toc_items.append(f'<li><a href="/book/{slug}.html">{html.escape(title)}</a> · <a href="/book/md/{slug}.md">md</a></li>')
        print("wrote", slug)

    (book_dir / "book.md").write_text("\n".join(full_md), encoding="utf-8")
    print("done", book_dir)


if __name__ == "__main__":
    main()
