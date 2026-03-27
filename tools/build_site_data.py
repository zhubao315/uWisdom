#!/usr/bin/env python3
"""Build search index, knowledge graph data, and daily highlights for uWisdom site."""
from __future__ import annotations

import json
import re
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Parse YAML front matter, with fallback to regex if pyyaml unavailable."""
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return {}, text
    header_raw = parts[0].split("---\n", 1)[1]
    body = parts[1]

    if HAS_YAML:
        try:
            data = yaml.safe_load(header_raw) or {}
            if not isinstance(data, dict):
                data = {}
            return data, body
        except yaml.YAMLError:
            pass

    # Fallback: regex-based parsing
    data: dict = {}
    current_key: str | None = None
    for line in header_raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line[4:].strip().strip('"').strip("'"))
            continue
        if re.match(r"^-\s+", line) and current_key:
            data.setdefault(current_key, []).append(line[2:].strip().strip('"').strip("'"))
            continue
        if ":" in line and not line.startswith(" "):
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


def extract_title(front: dict, body: str, fallback: str) -> str:
    if front.get("title"):
        return str(front["title"])
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def strip_markdown(text: str) -> str:
    text = re.sub(r"\{\{.*?\}\}", "", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_>\-]", " ", text)
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate_by_sentence(text: str, max_len: int = 2500) -> str:
    """Truncate text at sentence boundary instead of hard cutoff."""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    # Find last sentence-ending punctuation
    for sep in ["。", "！", "？", ".", "!", "?", "\n"]:
        idx = truncated.rfind(sep)
        if idx > max_len * 0.6:
            return truncated[: idx + 1]
    return truncated


def build_url(rel_path: Path, front: dict) -> str:
    permalink = front.get("permalink")
    if permalink:
        return str(permalink).rstrip("/") or "/"
    rel = "/" + rel_path.with_suffix(".html").as_posix()
    rel = rel.replace("/index.html", "/")
    return rel


def section_for_path(rel_path: Path) -> str:
    value = rel_path.as_posix()
    section_map = [
        ("knowledge-base/domains/", "知识百科 / 领域"),
        ("knowledge-base/themes/", "知识百科 / 主题"),
        ("knowledge-base/glossary/", "知识百科 / 术语"),
        ("knowledge-base/principles/", "知识百科 / 原则"),
        ("knowledge-base/methods/", "知识百科 / 方法"),
        ("knowledge-base/cases/", "知识百科 / 案例"),
        ("topic-research/", "主题研究"),
        ("figures/", "人物志"),
        ("tools-agent/", "工具 & Agent"),
        ("identities/", "角色地图"),
        ("today/", "今日知识精华"),
        ("search/", "搜索"),
        ("encyclopedia/", "知识百科"),
    ]
    for prefix, section in section_map:
        if value.startswith(prefix):
            return section
    return "页面"


def domain_for_path(rel_path: Path, title: str) -> str:
    value = rel_path.as_posix()
    if value.startswith("knowledge-base/domains/"):
        return title
    if value.startswith("knowledge-base/themes/"):
        return ""
    if value.startswith("figures/"):
        return "人物志"
    if value.startswith("topic-research/"):
        return "主题研究"
    return ""


def linked_domain(body: str) -> str:
    match = re.search(r"所属第二层领域：\[([^\]]+)\]", body)
    return match.group(1).strip() if match else ""


def infer_tags(rel_path: Path, title: str) -> list[str]:
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
    type_markers = {
        "domains/": "domain",
        "themes/": "theme",
        "figures/": "figure",
        "topic-research/": "research",
    }
    for marker, tag in type_markers.items():
        if marker in value:
            tags.add(tag)
    for key, values in mapping.items():
        if any(token in title for token in values):
            tags.add(key)
    return sorted(tags)


def internal_links(body: str) -> list[tuple[str, str]]:
    # Support both [label]({{ 'path' | relative_url }}) and [[WikiLink]]
    md_links = re.findall(r"\[([^\]]+)\]\(\{\{\s*'([^']+)'", body)
    wiki_links = re.findall(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", body)
    results = []
    for label, path in md_links:
        results.append((label, path))
    for target, label in wiki_links:
        results.append((label or target, target))
    return results


def extract_chunks(body: str) -> list[dict]:
    """Split body into chunks by H2/H3 for semantic indexing."""
    chunks = []
    current_heading = "Introduction"
    current_content = []
    
    lines = body.splitlines()
    for line in lines:
        if line.startswith(("## ", "### ")):
            if current_content:
                chunks.append({"heading": current_heading, "text": "\n".join(current_content).strip()})
            current_heading = line.lstrip("#").strip()
            current_content = []
        else:
            current_content.append(line)
    
    if current_content:
        chunks.append({"heading": current_heading, "text": "\n".join(current_content).strip()})
    return chunks


def git_date(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "log", "-1", "--format=%cs", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or date.today().isoformat()


def ensure_list(value) -> list:
    """Ensure a value is a list (handle string or list from YAML)."""
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return []


def main():
    pages: list[dict] = []
    url_to_page: dict[str, dict] = {}

    for path in sorted(DOCS.rglob("*.md")):
        rel_path = path.relative_to(DOCS)
        if rel_path.as_posix().startswith("_"):
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            print(f"  skip: {rel_path}")
            continue

        front, body = parse_front_matter(raw)
        title = extract_title(front, body, path.stem)
        url = build_url(rel_path, front)
        tags = front.get("tags") or infer_tags(rel_path, title)
        tags = ensure_list(tags)

        is_glossary = "knowledge-base/glossary/" in rel_path.as_posix()
        
        page = {
            "path": rel_path.as_posix(),
            "url": url,
            "title": title,
            "summary": str(front.get("summary", "")),
            "section": section_for_path(rel_path),
            "domain": str(front.get("domain", "") or linked_domain(body) or domain_for_path(rel_path, title)),
            "tags": tags,
            "version": str(front.get("version", "v1.0.0")),
            "author": str(front.get("author", "")),
            "book": str(front.get("book", "")),
            "updated": str(front.get("updated", "") or git_date(path)),
            "content": truncate_by_sentence(strip_markdown(body)) if not is_glossary else "",
            "links": internal_links(body) if not is_glossary else [],
        }
        pages.append(page)
        url_to_page[url] = page

    title_to_url = {page["title"]: page["url"] for page in pages}
    edges: set[tuple[str, str]] = set()

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

    incoming: dict[str, list[str]] = defaultdict(list)
    outgoing: dict[str, list[str]] = defaultdict(list)
    for source, target in sorted(edges):
        outgoing[source].append(target)
        incoming[target].append(source)

    graph_pages: dict[str, dict] = {}
    for page in pages:
        related = []
        for url in outgoing.get(page["url"], [])[:3]:
            if url in url_to_page:
                related.append(("out", url_to_page[url]["title"], url))
        for url in incoming.get(page["url"], [])[:3]:
            if url in url_to_page:
                related.append(("in", url_to_page[url]["title"], url))

        if related:
            lines = ["graph LR"]
            safe_page_title = page["title"].replace('"', "'")
            lines.append(f'A["{safe_page_title}"]')
            for index, (direction, title, url) in enumerate(related, start=1):
                node = f"N{index}"
                safe_title = title.replace('"', "'")
                if direction == "out":
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

    skip_sections = {"页面", "搜索"}
    search_entries = []
    for page in pages:
        if page["section"] in skip_sections:
            continue
        search_entries.append(
            {key: page[key] for key in ("url", "title", "summary", "section", "domain", "tags", "version", "author", "book", "content")}
        )

    search_payload = {"entries": search_entries, "filters": filters}
    graph_payload = {"pages": graph_pages}

    # Calculate statistics
    stats = {
        "total": len(pages),
        "by_section": defaultdict(int),
        "by_domain": defaultdict(int),
    }
    for page in pages:
        stats["by_section"][page["section"]] += 1
        if page["domain"]:
            stats["by_domain"][page["domain"]] += 1
    
    # Convert defaultdict to regular dict for JSON serialization
    stats["by_section"] = dict(stats["by_section"])
    stats["by_domain"] = dict(stats["by_domain"])

    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "search-index.json").write_text(
        json.dumps(search_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (ASSETS / "graph.json").write_text(
        json.dumps(graph_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (ASSETS / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Daily highlights: rotate across domains, prefer recently updated
    highlight_sections = {"知识百科 / 领域", "知识百科 / 主题", "主题研究", "人物志", "工具 & Agent"}
    candidates = [p for p in pages if p["section"] in highlight_sections]
    # Sort by updated date descending, then by title for stability
    candidates.sort(key=lambda item: (item["updated"], item["title"]), reverse=True)
    # Pick up to 8, ensuring domain diversity
    highlights: list[dict] = []
    seen_domains: set[str] = set()
    for item in candidates:
        if len(highlights) >= 8:
            break
        domain = item["domain"] or item["section"]
        # Allow max 2 from same domain
        domain_count = sum(1 for h in highlights if (h["domain"] or h["section"]) == domain)
        if domain_count < 2:
            highlights.append(item)
            seen_domains.add(domain)
    # Fill remaining slots
    for item in candidates:
        if len(highlights) >= 8:
            break
        if item not in highlights:
            highlights.append(item)

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
        summary_text = item["summary"] or "暂无摘要"
        today_md.extend(
            [
                f"## [{item['title']}]({item['url']})",
                "",
                f"- 分类：{item['section']}",
                f"- 领域：{item['domain'] or '—'}",
                f"- 更新：{item['updated']}",
                f"- 标签：{', '.join(item['tags']) or '—'}",
                f"- 摘要：{summary_text}",
                "",
            ]
        )
    today_dir = DOCS / "today"
    today_dir.mkdir(exist_ok=True)
    (today_dir / "index.md").write_text("\n".join(today_md), encoding="utf-8")

    print(f"Built: {len(search_entries)} search entries, {len(graph_pages)} graph pages, {len(highlights)} highlights")


if __name__ == "__main__":
    main()
