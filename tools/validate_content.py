#!/usr/bin/env python3
"""Validate content integrity: check required front matter fields and find broken links."""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

REQUIRED_FIELDS = {"title", "summary"}
VALID_SECTIONS = {
    "知识百科 / 领域", "知识百科 / 主题", "主题研究", "人物志",
    "工具 & Agent", "角色地图", "搜索", "知识百科", "今日知识精华",
}


def parse_front_matter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return {}
    header_raw = parts[0].split("---\n", 1)[1]
    if HAS_YAML:
        try:
            data = yaml.safe_load(header_raw) or {}
            return data if isinstance(data, dict) else {}
        except yaml.YAMLError:
            return {}
    return {}


def main():
    errors: list[str] = []
    all_urls: set[str] = set()
    page_data: list[tuple[Path, dict, str]] = []

    for path in sorted(DOCS.rglob("*.md")):
        rel_path = path.relative_to(DOCS)
        if rel_path.as_posix().startswith("_"):
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            errors.append(f"Cannot read: {rel_path}")
            continue

        front = parse_front_matter(raw)
        page_data.append((rel_path, front, raw))

        # Check required fields
        for field in REQUIRED_FIELDS:
            value = front.get(field, "")
            if not value:
                errors.append(f"Missing '{field}' in {rel_path}")

        # Check title length
        title = str(front.get("title", ""))
        if len(title) > 50:
            errors.append(f"Title too long ({len(title)} chars) in {rel_path}: '{title[:30]}...'")

        # Check summary exists and is meaningful
        summary = str(front.get("summary", ""))
        if summary and len(summary) < 3:
            errors.append(f"Summary too short in {rel_path}: '{summary}'")

        # Collect URL
        permalink = front.get("permalink")
        if permalink:
            all_urls.add(str(permalink).rstrip("/"))
        else:
            url = "/" + rel_path.with_suffix(".html").as_posix()
            url = url.replace("/index.html", "/")
            all_urls.add(url)

    all_titles = {str(f.get("title")).strip(): p for p, f, _ in page_data if f.get("title")}

    # Validate links
    for rel_path, front, body in page_data:
        # Remove code blocks
        body_no_code = re.sub(r'```[\s\S]*?```', '', body)
        body_no_code = re.sub(r'`[^`]+`', '', body_no_code)
        
        # Check [[WikiLinks]]
        wiki_links = re.findall(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", body_no_code)
        for target, _ in wiki_links:
            target_clean = target.strip()
            if target_clean in {"WikiLink", "Link", "链接"}:
                continue
            # Try by title or by path
            if target_clean not in all_titles:
                # Try finding as path
                target_path = DOCS / f"{target_clean}.md"
                if not target_path.exists():
                    errors.append(f"Broken WikiLink: [[{target_clean}]] in {rel_path}")

    # Report
    if errors:
        print(f"Found {len(errors)} issue(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"Validated {len(page_data)} pages, all OK")


if __name__ == "__main__":
    main()
