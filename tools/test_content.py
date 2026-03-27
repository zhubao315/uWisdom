#!/usr/bin/env python3
"""
uWisdom TDD 测试框架

基于 Superpowers test-driven-development 方法论：
1. RED - 写一个会失败的测试
2. GREEN - 写最小代码让测试通过
3. REFACTOR - 重构代码
4. REPEAT - 重复

用法:
    python3 tools/test_content.py              # 运行所有测试
    python3 tools/test_content.py --tdd       # TDD 模式 (先运行失败测试)
    python3 tools/test_content.py --coverage  # 覆盖率报告
    python3 tools/test_content.py --verbose  # 详细输出
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class TestStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


class TestSeverity(Enum):
    CRITICAL = "CRITICAL"   # 必须修复
    HIGH = "HIGH"           # 应该修复
    MEDIUM = "MEDIUM"       # 建议修复
    LOW = "LOW"             # 可以忽略


@dataclass
class TestResult:
    name: str
    status: TestStatus
    message: str = ""
    severity: TestSeverity = TestSeverity.HIGH
    file_path: Optional[str] = None
    line_number: Optional[int] = None

    def __str__(self):
        icon = "✓" if self.status == TestStatus.PASSED else "✗"
        loc = f" [{self.file_path}:{self.line_number}]" if self.file_path else ""
        return f"  {icon} {self.name}{loc}: {self.message}"


@dataclass
class TestSuite:
    name: str
    results: list[TestResult] = field(default_factory=list)

    def add(self, result: TestResult):
        self.results.append(result)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.PASSED)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.FAILED)

    @property
    def errors(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.ERROR)

    def summary(self) -> str:
        total = len(self.results)
        return f"{self.name}: {self.passed}/{total} passed, {self.failed} failed, {self.errors} errors"


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

VALID_TYPES = {"principle", "method", "glossary", "decision", "area", "project", "task-pattern", "case", "opportunity", "agent-card"}
VALID_IDENTITIES = {"architect", "investor", "lifelong-learner", "life-artist"}
VALID_CONFIDENCE = {"high", "medium", "low"}

REQUIRED_FIELDS = {"title", "summary"}


class ContentTester:
    """uWisdom 内容测试基类"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.pages: list[tuple[Path, dict, str]] = []
        self.all_urls: dict[str, str] = {}
        self.all_titles: dict[str, Path] = {}
        self._load_pages()

    def _load_pages(self):
        """加载所有页面"""
        for path in sorted(DOCS.rglob("*.md")):
            rel_path = path.relative_to(DOCS)
            if rel_path.as_posix().startswith("_"):
                continue
            try:
                raw = path.read_text(encoding="utf-8")
                front, body = self._parse_front_matter(raw)
                self.pages.append((rel_path, front, body))
                self._register_url(rel_path, front)
            except Exception as e:
                print(f"Warning: Cannot read {rel_path}: {e}", file=sys.stderr)

    def _parse_front_matter(self, text: str) -> tuple[dict, str]:
        """解析 YAML front matter"""
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
                if isinstance(data, dict):
                    return data, body
            except yaml.YAMLError:
                pass
        return {}, text

    def _register_url(self, rel_path: Path, front: dict):
        """注册 URL"""
        permalink = front.get("permalink")
        if permalink:
            url = str(permalink).rstrip("/")
            self.all_urls[url] = str(rel_path)
            if not url.endswith("/"):
                self.all_urls[url + "/"] = str(rel_path)
        url = rel_path.with_suffix(".html").as_posix()
        self.all_urls[url] = str(rel_path)
        
        title = front.get("title")
        if title:
            self.all_titles[str(title).strip()] = rel_path


class FrontMatterTester(ContentTester):
    """Front Matter 字段测试"""

    def run(self) -> TestSuite:
        suite = TestSuite("Front Matter 字段测试")

        for rel_path, front, _ in self.pages:
            self._test_required_fields(suite, rel_path, front)
            self._test_title_format(suite, rel_path, front)
            self._test_summary_format(suite, rel_path, front)
            self._test_type_field(suite, rel_path, front)
            self._test_identity_field(suite, rel_path, front)
            self._test_confidence_field(suite, rel_path, front)
            self._test_version_format(suite, rel_path, front)
            self._test_permalink_format(suite, rel_path, front)
            self._test_tags_format(suite, rel_path, front)

        return suite

    def _test_required_fields(self, suite: TestSuite, rel_path: Path, front: dict):
        for field in REQUIRED_FIELDS:
            if not front.get(field):
                suite.add(TestResult(
                    name=f"必填字段 '{field}'",
                    status=TestStatus.FAILED,
                    message=f"缺少必填字段 '{field}'",
                    severity=TestSeverity.CRITICAL,
                    file_path=str(rel_path)
                ))

    def _test_title_format(self, suite: TestSuite, rel_path: Path, front: dict):
        title = str(front.get("title", ""))
        if len(title) > 50:
            suite.add(TestResult(
                name="标题长度",
                status=TestStatus.FAILED,
                message=f"标题过长 ({len(title)} 字符)，应 ≤50",
                severity=TestSeverity.HIGH,
                file_path=str(rel_path)
            ))
        elif len(title) == 0:
            pass  # 已在 required_fields 测试
        elif self.verbose:
            suite.add(TestResult(
                name="标题格式",
                status=TestStatus.PASSED,
                message=f"格式正确",
                file_path=str(rel_path)
            ))

    def _test_summary_format(self, suite: TestSuite, rel_path: Path, front: dict):
        summary = str(front.get("summary", ""))
        if summary and len(summary) < 10:
            suite.add(TestResult(
                name="摘要长度",
                status=TestStatus.FAILED,
                message=f"摘要过短 ({len(summary)} 字符)，应 ≥10",
                severity=TestSeverity.MEDIUM,
                file_path=str(rel_path)
            ))
        elif summary and len(summary) > 200:
            suite.add(TestResult(
                name="摘要长度",
                status=TestStatus.FAILED,
                message=f"摘要过长 ({len(summary)} 字符)，应 ≤200",
                severity=TestSeverity.MEDIUM,
                file_path=str(rel_path)
            ))

    def _test_type_field(self, suite: TestSuite, rel_path: Path, front: dict):
        ktype = front.get("type", "")
        if ktype and ktype not in VALID_TYPES:
            suite.add(TestResult(
                name="type 字段",
                status=TestStatus.FAILED,
                message=f"无效的 type 值 '{ktype}'，有效值: {', '.join(VALID_TYPES)}",
                severity=TestSeverity.HIGH,
                file_path=str(rel_path)
            ))
        elif ktype and self.verbose:
            suite.add(TestResult(
                name="type 字段",
                status=TestStatus.PASSED,
                message=f"有效值: {ktype}",
                file_path=str(rel_path)
            ))

    def _test_identity_field(self, suite: TestSuite, rel_path: Path, front: dict):
        identity = front.get("identity", "")
        if identity and identity not in VALID_IDENTITIES:
            suite.add(TestResult(
                name="identity 字段",
                status=TestStatus.FAILED,
                message=f"无效的 identity 值 '{identity}'，有效值: {', '.join(VALID_IDENTITIES)}",
                severity=TestSeverity.HIGH,
                file_path=str(rel_path)
            ))

    def _test_confidence_field(self, suite: TestSuite, rel_path: Path, front: dict):
        confidence = front.get("confidence", "")
        if confidence and confidence not in VALID_CONFIDENCE:
            suite.add(TestResult(
                name="confidence 字段",
                status=TestStatus.FAILED,
                message=f"无效的 confidence 值 '{confidence}'，有效值: {', '.join(VALID_CONFIDENCE)}",
                severity=TestSeverity.MEDIUM,
                file_path=str(rel_path)
            ))

    def _test_version_format(self, suite: TestSuite, rel_path: Path, front: dict):
        version = str(front.get("version", ""))
        if version and not re.match(r'^v?\d+\.\d+\.\d+$', version):
            suite.add(TestResult(
                name="version 格式",
                status=TestStatus.FAILED,
                message=f"无效的 version 格式 '{version}'，应符合 semver (如 v1.0.0)",
                severity=TestSeverity.MEDIUM,
                file_path=str(rel_path)
            ))

    def _test_permalink_format(self, suite: TestSuite, rel_path: Path, front: dict):
        permalink = front.get("permalink", "")
        if not permalink:
            suite.add(TestResult(
                name="permalink 字段",
                status=TestStatus.FAILED,
                message="缺少 permalink 字段",
                severity=TestSeverity.HIGH,
                file_path=str(rel_path)
            ))
        elif not permalink.startswith("/"):
            suite.add(TestResult(
                name="permalink 格式",
                status=TestStatus.FAILED,
                message=f"permalink 必须以 / 开头，当前: {permalink}",
                severity=TestSeverity.HIGH,
                file_path=str(rel_path)
            ))

    def _test_tags_format(self, suite: TestSuite, rel_path: Path, front: dict):
        tags = front.get("tags", [])
        if tags and not isinstance(tags, list):
            suite.add(TestResult(
                name="tags 格式",
                status=TestStatus.FAILED,
                message="tags 必须是数组格式",
                severity=TestSeverity.HIGH,
                file_path=str(rel_path)
            ))


class LinkTester(ContentTester):
    """链接测试"""

    def run(self) -> TestSuite:
        suite = TestSuite("链接测试")

        for rel_path, front, body in self.pages:
            body_no_code = self._strip_code_blocks(body)
            self._test_wiki_links(suite, rel_path, body_no_code)
            self._test_markdown_links(suite, rel_path, body_no_code)

        return suite

    def _strip_code_blocks(self, text: str) -> str:
        """移除代码块"""
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        return text

    def _test_wiki_links(self, suite: TestSuite, rel_path: Path, body: str):
        wiki_links = re.findall(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", body)
        for target, _ in wiki_links:
            target_clean = target.strip()
            if target_clean in {"WikiLink", "Link", "链接"}:
                continue
            if target_clean not in self.all_titles:
                target_path = DOCS / f"{target_clean}.md"
                if not target_path.exists():
                    suite.add(TestResult(
                        name=f"WikiLink [[{target_clean}]]",
                        status=TestStatus.FAILED,
                        message=f"死链接：目标不存在",
                        severity=TestSeverity.CRITICAL,
                        file_path=str(rel_path)
                    ))

    def _test_markdown_links(self, suite: TestSuite, rel_path: Path, body: str):
        md_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body)
        for label, url in md_links:
            # Skip external links
            if url.startswith("http"):
                continue
            # Skip anchor links
            if url.startswith("#"):
                continue
            # Skip Jekyll relative_url links
            if "relative_url" in url:
                match = re.search(r"'([^']+)'", url)
                if match:
                    url = match.group(1)
                    if url.endswith("/"):
                        url = url + "index.html"
                    elif not url.endswith(".html"):
                        url = url + ".html"
            # Skip relative paths (files outside docs)
            if url.startswith("../"):
                continue
            # Skip non-markdown files
            if url.endswith(".json") or url.endswith(".yaml") or url.endswith(".yml"):
                continue
            # Skip inline code-like patterns (Python/JavaScript style)
            # Pattern like ["key"](value) or similar code syntax
            if re.match(r'^["\'].*["\']\)$', f'{label}]({url}'):
                continue
            if '=' in label and '(' in url:
                continue
            if label.startswith('"') or label.startswith("'"):
                continue
            
            clean_url = url.lstrip("/")
            if clean_url not in self.all_urls and clean_url.rstrip("/") not in self.all_urls:
                suite.add(TestResult(
                    name=f"Markdown Link [{label}]({url})",
                    status=TestStatus.FAILED,
                    message=f"死链接：目标不存在",
                    severity=TestSeverity.HIGH,
                    file_path=str(rel_path)
                ))


class ContentQualityTester(ContentTester):
    """内容质量测试"""

    def run(self) -> TestSuite:
        suite = TestSuite("内容质量测试")

        for rel_path, front, body in self.pages:
            self._test_body_length(suite, rel_path, front, body)
            self._test_heading_structure(suite, rel_path, body)
            self._test_no_placeholder(suite, rel_path, body)
            self._test_incoming_outgoing_balance(suite, rel_path, body)

        return suite

    def _test_body_length(self, suite: TestSuite, rel_path: Path, front: dict, body: str):
        lines = [l for l in body.splitlines() if l.strip()]
        if len(lines) < 5:
            suite.add(TestResult(
                name="内容长度",
                status=TestStatus.FAILED,
                message=f"内容过短 ({len(lines)} 行)，应 ≥5 行",
                severity=TestSeverity.MEDIUM,
                file_path=str(rel_path)
            ))

    def _test_heading_structure(self, suite: TestSuite, rel_path: Path, body: str):
        headings = re.findall(r"^(#{1,6})\s+(.+)$", body, re.MULTILINE)
        if not headings:
            suite.add(TestResult(
                name="标题结构",
                status=TestStatus.FAILED,
                message="缺少标题结构",
                severity=TestSeverity.MEDIUM,
                file_path=str(rel_path)
            ))

    def _test_no_placeholder(self, suite: TestSuite, rel_path: Path, body: str):
        placeholders = [
            (r"TODO", "TODO 占位符"),
            (r"FIXME", "FIXME 占位符"),
            (r"XXX", "XXX 占位符"),
            (r"占位", "中文占位符"),
            (r"待写", "待写占位符"),
            (r"补充中", "补充中占位符"),
        ]
        body_no_code = re.sub(r'```[\s\S]*?```', '', body)
        body_no_code = re.sub(r'`[^`]+`', '', body_no_code)
        for pattern, msg in placeholders:
            matches = list(re.finditer(pattern, body_no_code, re.IGNORECASE))
            for match in matches:
                suite.add(TestResult(
                    name="占位符检测",
                    status=TestStatus.FAILED,
                    message=f"发现 {msg}",
                    severity=TestSeverity.MEDIUM,
                    file_path=str(rel_path)
                ))

    def _test_incoming_outgoing_balance(self, suite: TestSuite, rel_path: Path, body: str):
        wiki_links = re.findall(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", body)
        if len(wiki_links) > 50:
            suite.add(TestResult(
                name="链接数量",
                status=TestStatus.FAILED,
                message=f"链接过多 ({len(wiki_links)} 个)，考虑拆分",
                severity=TestSeverity.LOW,
                file_path=str(rel_path)
            ))


class SchemaTester(ContentTester):
    """增强 Schema 测试"""

    def run(self) -> TestSuite:
        suite = TestSuite("Schema 增强测试")

        for rel_path, front, body in self.pages:
            self._test_applicability_fields(suite, rel_path, front)
            self._test_skill_ref(suite, rel_path, front)
            self._test_knowledge_id(suite, rel_path, front)

        return suite

    def _test_applicability_fields(self, suite: TestSuite, rel_path: Path, front: dict):
        ktype = front.get("type", "")
        if ktype in {"principle", "method"}:
            applicability = front.get("applicability", [])
            non_applicability = front.get("non_applicability", [])
            if not applicability:
                suite.add(TestResult(
                    name="applicability 字段",
                    status=TestStatus.FAILED,
                    message="principle/method 类型应包含 applicability 字段",
                    severity=TestSeverity.HIGH,
                    file_path=str(rel_path)
                ))

    def _test_skill_ref(self, suite: TestSuite, rel_path: Path, front: dict):
        skill_ref = front.get("skill_ref", "")
        if skill_ref and not re.match(r"^uskill-[a-z0-9-]+$", skill_ref):
            suite.add(TestResult(
                name="skill_ref 格式",
                status=TestStatus.FAILED,
                message=f"无效的 skill_ref 格式 '{skill_ref}'，应符合 uskill-xxx 格式",
                severity=TestSeverity.MEDIUM,
                file_path=str(rel_path)
            ))

    def _test_knowledge_id(self, suite: TestSuite, rel_path: Path, front: dict):
        kid = front.get("id", "")
        if kid and not re.match(r"^kw-[a-z0-9]+-[a-z0-9-]+$", kid):
            suite.add(TestResult(
                name="id 格式",
                status=TestStatus.FAILED,
                message=f"无效的 id 格式 '{kid}'，应符合 kw-xxx-xxx 格式",
                severity=TestSeverity.MEDIUM,
                file_path=str(rel_path)
            ))


def run_all_tests(verbose: bool = False) -> tuple[int, int, int]:
    """运行所有测试套件"""
    suites = [
        FrontMatterTester(verbose),
        LinkTester(verbose),
        ContentQualityTester(verbose),
        SchemaTester(verbose),
    ]

    total_passed = 0
    total_failed = 0
    total_errors = 0

    for suite in suites:
        results = suite.run()
        total_passed += results.passed
        total_failed += results.failed
        total_errors += results.errors

        print(f"\n{results.summary()}")
        for result in results.results:
            if result.status != TestStatus.PASSED or verbose:
                print(result)

    return total_passed, total_failed, total_errors


def main():
    parser = argparse.ArgumentParser(description="uWisdom TDD 测试框架")
    parser.add_argument("--tdd", action="store_true", help="TDD 模式：先运行失败测试")
    parser.add_argument("--coverage", action="store_true", help="生成覆盖率报告")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    print("=" * 60)
    print("uWisdom TDD 测试框架")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    passed, failed, errors = run_all_tests(verbose=args.verbose)

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败, {errors} 错误")
    print("=" * 60)

    if failed > 0 or errors > 0:
        print("\n⚠️  测试未全部通过，请修复后重试")
        sys.exit(1)
    else:
        print("\n✅ 所有测试通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()
