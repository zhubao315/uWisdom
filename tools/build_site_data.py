#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"


def parse_front_matter(text: str):
    if not text.startswith("---\n"):
      return {}, text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
      return {}, text
    header = parts[0].splitlines()[1:]
    body = parts[1]
    data = {}
    current_key = None
    for line in header:
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line[4:].strip())
            continue
        if re.match(r"^-\s+", line) and current_key:
            data.setdefault(current_key, []).append(line[2:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value == "":
                data[key] = []
                current_key = key
            else:
                data[key] = value
                current_key = key
    return data, body


def extract_title(front, body, fallback):
    if front.get("title"):
        return front["title"]
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def strip_markdown(text: str):
    text = re.sub(r"\{\{.*?\}\}", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = re.sub(r"[*_>\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_url(rel_path: Path, front) -> str:
    permalink = front.get("permalink")
    if permalink:
        return permalink.rstrip("/") or "/"
    rel = "/" + rel_path.with_suffix(".html").as_posix()
    rel = rel.replace("/index.html", "/")
    return rel


def section_for_path(rel_path: Path) -> str:
    value = rel_path.as_posix()
    if value.startswith("knowledge-base/domains/"):
        return "知识百科 / 领域"
    if value.startswith("knowledge-base/themes/"):
        return "知识百科 / 主题"
    if value.startswith("topic-research/"):
        return "主题研究"
    if value.startswith("figures/"):
        return "人物志"
    if value.startswith("tools-agent/"):
        return "工具 & Agent"
    if value.startswith("identities/"):
        return "角色地图"
    if value.startswith("today/"):
        return "今日知识精华"
    if value.startswith("search/"):
        return "搜索"
    if value.startswith("encyclopedia/"):
        return "知识百科"
    return "页面"


def domain_for_path(rel_path: Path, title: str) -> str:
    if rel_path.as_posix().startswith("knowledge-base/domains/"):
        return title
    if rel_path.as_posix().startswith("knowledge-base/themes/"):
        return ""
    if rel_path.as_posix().startswith("figures/"):
        return "人物志"
    if rel_path.as_posix().startswith("topic-research/"):
        return "主题研究"
    return ""


def linked_domain(body: str) -> str:
    match = re.search(r"所属第二层领域：\[([^\]]+)\]", body)
    return match.group(1).strip() if match else ""


def infer_tags(rel_path: Path, title: str):
    tags = set()
    value = rel_path.as_posix()
    mapping = {
        "ai": ["AI", "LLM", "Agent", "人工智能"],
        "agent": ["Agent"],
        "architecture": ["架构", "云原生", "平台"],
        "investment": ["投资", "市场", "交易"],
        "learning": ["学习", "国学", "心理"],
        "lifestyle": ["生活", "摄影", "户外", "葡萄酒", "跑步", "健身"],
        "culture": ["北京", "文化", "人物志", "苏轼", "蒙田", "王阳明"],
        "digital-life": ["数字"],
    }
    if "domains/" in value:
        tags.add("domain")
    if "themes/" in value:
        tags.add("theme")
    if "figures/" in value:
        tags.add("figure")
    if "topic-research/" in value:
        tags.add("research")
    for key, values in mapping.items():
        if any(token in title for token in values):
            tags.add(key)
    return sorted(tags)


def internal_links(body: str):
    return re.findall(r"\[([^\]]+)\]\(\{\{\s*'([^']+)'", body)


def git_date(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "log", "-1", "--format=%cs", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "2026-03-25"


def main():
    pages = []
    path_to_title = {}
    url_to_page = {}

    for path in sorted(DOCS.rglob("*.md")):
        rel_path = path.relative_to(DOCS)
        if rel_path.as_posix().startswith("_"):
            continue
        raw = path.read_text(encoding="utf-8")
        front, body = parse_front_matter(raw)
        title = extract_title(front, body, path.stem)
        url = build_url(rel_path, front)
        page = {
            "path": rel_path.as_posix(),
            "url": url,
            "title": title,
            "summary": front.get("summary", ""),
            "section": section_for_path(rel_path),
            "domain": front.get("domain", "") or linked_domain(body) or domain_for_path(rel_path, title),
            "tags": front.get("tags", []) or infer_tags(rel_path, title),
            "version": front.get("version", "v1.0.0"),
            "author": front.get("author", ""),
            "book": front.get("book", ""),
            "updated": front.get("updated", "") or git_date(path),
            "content": strip_markdown(body)[:2500],
            "links": internal_links(body),
        }
        pages.append(page)
        path_to_title[rel_path.as_posix()] = title
        url_to_page[url] = page

    title_to_url = {page["title"]: page["url"] for page in pages}
    edges = set()

    for page in pages:
        for label, href in page["links"]:
            clean_href = href.replace(".html", "")
            if clean_href.endswith("/"):
                target = clean_href.rstrip("/") or "/"
            else:
                target = clean_href
            if target in url_to_page:
                edges.add((page["url"], target))
            elif target + ".html" in url_to_page:
                edges.add((page["url"], target + ".html"))
            elif label in title_to_url:
                edges.add((page["url"], title_to_url[label]))

    incoming = defaultdict(list)
    outgoing = defaultdict(list)
    for source, target in sorted(edges):
        outgoing[source].append(target)
        incoming[target].append(source)

    graph_pages = {}
    for page in pages:
        related = []
        for url in outgoing.get(page["url"], [])[:3]:
            related.append(("out", url_to_page[url]["title"], url))
        for url in incoming.get(page["url"], [])[:3]:
            related.append(("in", url_to_page[url]["title"], url))
        if related:
            lines = ["graph LR"]
            lines.append(f'A["{page["title"]}"]')
            for index, (_, title, url) in enumerate(related, start=1):
                node = f"N{index}"
                safe_title = title.replace('"', "'")
                if url in outgoing.get(page["url"], []):
                    lines.append(f'A --> {node}["{safe_title}"]')
                else:
                    lines.append(f'{node}["{safe_title}"] --> A')
            mermaid = "\n".join(lines)
        else:
            mermaid = ""
        graph_pages[page["url"]] = {"mermaid": mermaid}

    filters = {
        "domain": sorted({page["domain"] for page in pages if page["domain"]}),
        "tag": sorted({tag for page in pages for tag in page["tags"]}),
        "version": sorted({page["version"] for page in pages if page["version"]}),
        "book": sorted({page["book"] for page in pages if page["book"]}),
        "author": sorted({page["author"] for page in pages if page["author"]}),
    }

    search_entries = []
    for page in pages:
        if page["section"] in {"页面"}:
            continue
        search_entries.append(
            {key: page[key] for key in ("url", "title", "summary", "section", "domain", "tags", "version", "author", "book", "content")}
        )

    search_payload = {"entries": search_entries, "filters": filters}
    graph_payload = {"pages": graph_pages}

    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "search-index.json").write_text(
        json.dumps(search_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (ASSETS / "graph.json").write_text(
        json.dumps(graph_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    highlights = sorted(
        [page for page in pages if page["section"] not in {"页面", "搜索", "知识百科", "角色地图"}],
        key=lambda item: (item["updated"], item["title"]),
        reverse=True,
    )[:8]
    today_md = [
        "---",
        "title: 今日知识精华",
        "summary: 自动生成的每日精选知识页",
        "permalink: /today/",
        "---",
        "",
        "# 今日知识精华",
        "",
        "以下内容由站点构建脚本自动挑选，优先展示最近更新且可复用度高的条目。",
        "",
    ]
    for item in highlights:
        today_md.extend(
            [
                f"## [{item['title']}]({item['url']})",
                "",
                f"- 分类：{item['section']}",
                f"- 更新：{item['updated']}",
                f"- 摘要：{item['summary'] or '暂无摘要'}",
                "",
            ]
        )
    today_dir = DOCS / "today"
    today_dir.mkdir(exist_ok=True)
    (today_dir / "index.md").write_text("\n".join(today_md), encoding="utf-8")


if __name__ == "__main__":
    main()
