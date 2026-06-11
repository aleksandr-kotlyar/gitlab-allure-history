import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from generate_index import index_tree


class HrefParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name.casefold() == "href" and value is not None:
                self.hrefs.append(value)


def write_report(report_dir, modified_at, failed=0):
    assets_dir = report_dir / "assets"
    attachments_dir = report_dir / "attachments"
    widgets_dir = report_dir / "widgets"
    assets_dir.mkdir(parents=True)
    attachments_dir.mkdir()
    widgets_dir.mkdir()

    (report_dir / "index.html").write_text(
        """<!doctype html>
<html lang="en">
<head>
    <link rel="stylesheet" href="assets/report.css">
</head>
<body>
    <section id="categories">Categories</section>
    <a href="#categories">Categories</a>
    <a href="attachments/result%20log.txt?download=1#output">Result log</a>
</body>
</html>
""",
        encoding="utf-8",
    )
    (assets_dir / "report.css").write_text("body { color: black; }\n", encoding="utf-8")
    (attachments_dir / "result log.txt").write_text("test output\n", encoding="utf-8")
    (widgets_dir / "summary.json").write_text(
        json.dumps(
            {
                "statistic": {
                    "failed": failed,
                    "broken": 0,
                    "skipped": 0,
                    "passed": 1,
                    "unknown": 0,
                    "total": failed + 1,
                },
                "time": {"duration": 1_000},
            }
        ),
        encoding="utf-8",
    )
    (report_dir / ".modified_at").write_text(f"{modified_at}\n", encoding="utf-8")


def local_href_target(public_dir, source_html, href):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        return None

    href_path = unquote(parsed.path)
    if not href_path:
        target = source_html
    elif href_path.startswith("/"):
        target = public_dir / href_path.lstrip("/")
    else:
        target = source_html.parent / href_path

    target = target.resolve()
    try:
        target.relative_to(public_dir.resolve())
    except ValueError:
        return target

    if href_path.endswith("/") or target.is_dir():
        target /= "index.html"

    return target


def find_local_href_targets(public_dir):
    references = []

    for source_html in sorted(public_dir.rglob("*.html")):
        parser = HrefParser()
        parser.feed(source_html.read_text(encoding="utf-8"))

        for href in parser.hrefs:
            target = local_href_target(public_dir, source_html, href)
            if target is not None:
                references.append((source_html, href, target))

    return references


def target_exists_in_public_tree(public_dir, target):
    try:
        target.relative_to(public_dir.resolve())
    except ValueError:
        return False

    return target.exists()


@pytest.mark.regression
class TestPublicTreeLinkIntegrity:
    def test_every_local_href_resolves_to_an_existing_target(self, tmp_path):
        public_dir = tmp_path / "public"
        write_report(
            public_dir / "dev" / "master" / "job_101",
            "2026-06-05T22:15:00Z",
        )
        write_report(
            public_dir / "dev" / "feature login" / "job_102",
            "2026-06-06T08:00:00Z",
            failed=1,
        )
        write_report(
            public_dir / "staging" / "release" / "job_103",
            "2026-06-07T09:30:00Z",
        )

        generated_indexes = index_tree(public_dir)
        references = find_local_href_targets(public_dir)
        broken_references = [
            (
                source.relative_to(public_dir).as_posix(),
                href,
                target.as_posix(),
            )
            for source, href, target in references
            if not target_exists_in_public_tree(public_dir, target)
        ]
        hrefs = [href for _, href, _ in references]

        assert generated_indexes
        assert references
        assert any("%20" in href for href in hrefs)
        assert any("?download=1#output" in href for href in hrefs)
        assert any(href.startswith("../job_") for href in hrefs)
        assert broken_references == []
