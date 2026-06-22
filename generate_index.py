from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import quote


INDEX_FILENAME = "index.html"
JOB_PREFIX = "job_"
MODIFIED_AT_FILENAME = ".modified_at"
SUMMARY_FILENAME = "widgets/summary.json"
HISTORY_DIRNAME = "history"
LATEST_DIRNAME = "latest"
HIDDEN_INDEX_ENTRIES = {INDEX_FILENAME, MODIFIED_AT_FILENAME, HISTORY_DIRNAME, LATEST_DIRNAME}

ROOT_INDEX_DIR = "public"
PUBLIC_TITLE = "gitlab-allure-history"
PINNED_ENTRY_NAMES = {"master"}
DESKTOP_LIST_BATCH_SIZE_ENV = "ALLURE_HISTORY_INDEX_DESKTOP_BATCH_SIZE"
MOBILE_LIST_BATCH_SIZE_ENV = "ALLURE_HISTORY_INDEX_MOBILE_BATCH_SIZE"
DESKTOP_LIST_BATCH_SIZE = 25
MOBILE_LIST_BATCH_SIZE = 12
SHOW_FOOTER_ENV = "ALLURE_HISTORY_SHOW_FOOTER"
VERSION_ENV = "GITLAB_ALLURE_HISTORY_VERSION"
GENERATOR_URL = "https://gitlab.com/aleksandr-kotlyar/gitlab-allure-history"
MOVING_REF_VERSIONS = {"latest", "master", "main"}

STYLE = """
        :root {
            color-scheme: light dark;
            --bg: #f6f8fa;
            --panel: #ffffff;
            --text: #24292f;
            --muted: #57606a;
            --border: #d0d7de;
            --row: #f6f8fa;
            --link: #0969da;
            --latest-bg: #d9f1ff;
            --latest-border: #a6ddff;
            --latest-text: #075985;
            --allure-passed: #97cc64;
            --allure-failed: #fd5a3e;
            --allure-broken: #ffd050;
            --allure-skipped: #aaaaaa;
            --allure-unknown: #d35ebe;
        }

        :root[data-theme="dark"] {
            color-scheme: dark;
            --bg: #0d1117;
            --panel: #161b22;
            --text: #e6edf3;
            --muted: #8b949e;
            --border: #30363d;
            --row: #21262d;
            --link: #58a6ff;
            --latest-bg: #102a3a;
            --latest-border: #1f5f7a;
            --latest-text: #8bd7ff;
        }

        :root[data-theme="dark"] .summary-compact.issue {
            color: #e5534b;
        }

        :root[data-theme="dark"] .summary-compact.passed {
            color: #3fb950;
        }

        :root[data-theme="dark"] .summary-compact.skipped {
            color: #aaaaaa;
        }

        :root[data-theme="light"] {
            color-scheme: light;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.5;
        }

        main {
            width: min(960px, calc(100% - 32px));
            margin: 32px auto;
        }

        .page-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            position: sticky;
            top: 0;
            z-index: 2;
            margin: -8px 0 12px;
            padding: 8px 0 12px;
            background: var(--bg);
        }

        h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 650;
            overflow-wrap: anywhere;
        }

        .hero {
            margin: 0 0 24px;
            padding: 16px 20px;
            border: 1px solid var(--border);
            border-radius: 12px;
            background: var(--panel);
        }

        .hero h2 {
            margin: 0 0 6px;
            font-size: 1.35rem;
            line-height: 1.2;
        }

        .hero p {
            max-width: 760px;
            margin: 0;
            color: #4a5568;
            line-height: 1.5;
        }

        :root[data-theme="dark"] .hero p {
            color: #adbac7;
        }

        .breadcrumbs {
            display: flex;
            flex-wrap: wrap;
            align-items: baseline;
            min-width: 0;
        }

        .breadcrumb-separator {
            margin: 0 4px;
            color: var(--muted);
            font-weight: 500;
        }

        .theme-toggle {
            min-width: 68px;
            min-height: 32px;
            flex: 0 0 auto;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--panel);
            color: var(--muted);
            cursor: pointer;
            font: inherit;
            font-size: 12px;
            font-weight: 500;
            transition: background-color 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
        }

        .theme-toggle:hover,
        .theme-toggle:focus-visible {
            border-color: var(--link);
            box-shadow: 0 0 0 3px color-mix(in srgb, var(--link) 22%, transparent);
        }

        .theme-toggle:hover {
            background: color-mix(in srgb, var(--link) 10%, var(--panel));
        }

        .theme-toggle:focus-visible {
            outline: none;
        }

        table {
            width: 100%;
            overflow: hidden;
            border: 1px solid var(--border);
            border-radius: 8px;
            border-spacing: 0;
            background: var(--panel);
            box-shadow: 0 1px 2px rgba(27, 31, 36, 0.04);
        }

        th,
        td {
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
            text-align: left;
            vertical-align: middle;
        }

        th {
            background: var(--row);
            color: var(--muted);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        tr:last-child td {
            border-bottom: 0;
        }

        tr:hover td {
            background: var(--row);
        }

        [hidden] {
            display: none !important;
        }

        .name-cell,
        .latest-report-cell {
            width: auto;
        }

        .history-cell {
            width: 86px;
            text-align: center;
            white-space: nowrap;
        }

        .result-cell {
            width: 220px;
            white-space: nowrap;
        }

        .duration-cell {
            width: 110px;
            white-space: nowrap;
        }

        .entry-title {
            display: flex;
            min-width: 0;
            align-items: baseline;
            gap: 6px;
            line-height: 1.4;
        }

        .entry-link {
            min-width: 0;
            overflow-wrap: anywhere;
        }

        .entry-name-text {
            color: var(--text);
        }

        .latest-badge {
            display: inline-flex;
            min-height: 20px;
            flex: 0 0 auto;
            align-items: center;
            border: 1px solid var(--latest-border);
            border-radius: 999px;
            padding: 1px 8px 2px;
            background: var(--latest-bg);
            color: var(--latest-text);
            font-size: 11px;
            font-weight: 700;
            line-height: 1.3;
            text-transform: lowercase;
        }

        .history-link {
            display: inline-flex;
            width: 32px;
            height: 32px;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            color: var(--link);
            vertical-align: middle;
        }

        .history-link:hover {
            background: color-mix(in srgb, var(--link) 10%, transparent);
            text-decoration: none;
        }

        .history-link:focus-visible {
            outline: 2px solid var(--link);
            outline-offset: 2px;
        }

        .history-icon {
            width: 18px;
            height: 18px;
            fill: none;
            stroke: currentColor;
            stroke-linecap: round;
            stroke-linejoin: round;
            stroke-width: 2;
        }

        .modified-cell {
            width: 190px;
            color: var(--muted);
            font-variant-numeric: tabular-nums;
            text-align: right;
            white-space: nowrap;
        }

        .directory-index .modified-cell {
            width: 220px;
        }

        .result-cell,
        .duration-cell {
            color: var(--muted);
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
        }

        .summary-compact {
            display: inline-block;
            padding: 1px 8px;
            font-size: 12px;
            line-height: 1.5;
            white-space: nowrap;
        }

        .result-cell a,
        .duration-cell a {
            color: inherit;
            text-decoration: none;
        }

        .summary-compact.issue {
            color: #d93025;
            font-weight: 600;
            text-decoration: underline;
            text-decoration-style: dotted;
            text-underline-offset: 3px;
        }

        .summary-compact.passed {
            color: #2f9e44;
            font-weight: 500;
        }

        .summary-compact.skipped {
            color: #aaaaaa;
            font-weight: 500;
        }

        a {
            color: var(--link);
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        .list-controls {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-top: 12px;
            color: var(--muted);
            font-size: 13px;
        }

        .show-more {
            min-width: 104px;
            min-height: 34px;
            flex: 0 0 auto;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--panel);
            color: var(--text);
            cursor: pointer;
            font: inherit;
            font-size: 13px;
            font-weight: 600;
        }

        .show-more:hover {
            background: var(--row);
        }

        .show-more:focus-visible {
            outline: 2px solid var(--link);
            outline-offset: 2px;
        }

        @media (max-width: 640px) {
            main {
                width: min(100% - 20px, 960px);
                margin: 16px auto;
            }

            h1 {
                font-size: 20px;
            }

            .page-header {
                align-items: flex-start;
                flex-direction: column;
            }

            .theme-toggle {
                min-width: 64px;
                min-height: 30px;
            }

            .hero {
                padding: 14px 16px;
            }

            .hero h2 {
                margin-bottom: 6px;
                font-size: 1.12rem;
                font-weight: 650;
                line-height: 1.25;
            }

            .hero p {
                font-size: 0.88rem;
                font-weight: 400;
                line-height: 1.45;
            }

            th {
                display: none;
            }

            td {
                display: block;
                border-bottom: 0;
            }

            tr {
                display: block;
                border-bottom: 1px solid var(--border);
            }

            tr:last-child {
                border-bottom: 0;
            }

            .name-cell,
            .latest-report-cell {
                width: 100%;
                padding-bottom: 2px;
            }

            .history-cell {
                width: 100%;
                padding-top: 0;
                padding-bottom: 2px;
                text-align: left;
            }

            .entry-meta,
            .entry-meta-label,
            .entry-meta-link {
                color: var(--muted);
                font-size: 0.82rem;
                font-weight: 500;
                line-height: 1.35;
            }

            .modified-cell {
                padding-top: 0;
                color: var(--muted);
                font-size: 12px;
                font-weight: 400;
                line-height: 1.3;
                font-variant-numeric: tabular-nums;
                text-align: left;
            }

            td[data-label] {
                display: flex;
                align-items: baseline;
                justify-content: space-between;
                column-gap: 8px;
                color: var(--muted);
                font-size: 0.82rem;
                font-weight: 500;
                line-height: 1.35;
            }

            td[data-label]::before {
                content: attr(data-label);
                flex: 0 0 auto;
                color: inherit;
                font: inherit;
                letter-spacing: 0;
                text-transform: none;
            }

            .modified-cell[data-label]::before {
                content: attr(data-label) ":";
                color: var(--muted);
                font-size: 10px;
                font-weight: 400;
                letter-spacing: normal;
                margin-right: 4px;
                opacity: 0.65;
                text-transform: none;
            }

            .modified-cell[data-label] {
                display: block;
            }

            .list-controls {
                align-items: stretch;
                flex-direction: column;
            }

            .show-more {
                width: 100%;
            }
        }

        .generator-footer {
            margin-top: 24px;
            padding: 8px 0;
            color: var(--muted);
            font-size: 12px;
            text-align: center;
        }

        .generator-footer-content {
            display: inline-flex;
            align-items: baseline;
            gap: 4px;
            line-height: 1.5;
        }

        .generator-footer a {
            color: var(--muted);
        }

        .generator-footer a:hover {
            color: var(--link);
            text-decoration: underline;
        }

        .generator-footer .dot-separator {
            line-height: inherit;
        }

        @media (prefers-color-scheme: dark) {
            :root:not([data-theme]) {
                --bg: #0d1117;
                --panel: #161b22;
                --text: #e6edf3;
                --muted: #8b949e;
                --border: #30363d;
                --row: #21262d;
                --link: #58a6ff;
            }

            :root:not([data-theme]) .summary-compact.issue {
                color: #e5534b;
            }

            :root:not([data-theme]) .summary-compact.passed {
                color: #3fb950;
            }
        }
"""

THEME_INIT_SCRIPT = """
        (function () {
            var storedTheme = null;
            try {
                storedTheme = localStorage.getItem("gah-index-theme");
            } catch (error) {
                storedTheme = null;
            }

            var prefersDark = window.matchMedia &&
                window.matchMedia("(prefers-color-scheme: dark)").matches;
            var theme = storedTheme || (prefersDark ? "dark" : "light");

            document.documentElement.dataset.theme = theme;
        })();
"""

THEME_TOGGLE_SCRIPT = """
        (function () {
            var storageKey = "gah-index-theme";
            var button = document.querySelector(".theme-toggle");

            function setTheme(theme, persist) {
                document.documentElement.dataset.theme = theme;

                if (persist) {
                    try {
                        localStorage.setItem(storageKey, theme);
                    } catch (error) {
                        // Continue with the in-page theme even when storage is blocked.
                    }
                }

                button.textContent = theme === "dark" ? "Light" : "Dark";
            }

            setTheme(document.documentElement.dataset.theme || "light", false);

            button.addEventListener("click", function () {
                var currentTheme = document.documentElement.dataset.theme;
                setTheme(currentTheme === "dark" ? "light" : "dark", true);
            });
        })();
"""

LIST_REVEAL_SCRIPT_TEMPLATE = """
        (function () {
            var table = document.querySelector("[data-progressive-list]");

            if (!table) {
                return;
            }

            var rows = Array.prototype.slice.call(
                table.querySelectorAll("tbody tr[data-list-row]")
            );
            var controls = document.querySelector(".list-controls");
            var button = document.querySelector(".show-more");
            var count = document.querySelector(".list-count");

            if (!rows.length || !controls || !button || !count) {
                return;
            }

            var media = window.matchMedia("(max-width: 640px)");
            var visibleRows = 0;

            function batchSize() {
                return media.matches ? __MOBILE_BATCH_SIZE__ : __DESKTOP_BATCH_SIZE__;
            }

            function updateRows(nextVisibleRows) {
                var currentBatchSize = batchSize();
                visibleRows = currentBatchSize <= 0 ?
                    rows.length :
                    Math.min(nextVisibleRows, rows.length);

                rows.forEach(function (row, index) {
                    row.hidden = index >= visibleRows;
                });

                count.textContent = "Showing " + visibleRows + " of " + rows.length;
                controls.hidden = currentBatchSize <= 0 || rows.length <= currentBatchSize;
                button.hidden = currentBatchSize <= 0 || visibleRows >= rows.length;
            }

            button.addEventListener("click", function () {
                updateRows(visibleRows + batchSize());
            });

            function fitViewportBatch() {
                updateRows(Math.max(visibleRows, batchSize()));
            }

            updateRows(batchSize());

            if (media.addEventListener) {
                media.addEventListener("change", fitViewportBatch);
            } else if (media.addListener) {
                media.addListener(fitViewportBatch);
            }
        })();
"""


@dataclass(frozen=True)
class SummaryCount:
    status: str
    count: int


@dataclass(frozen=True)
class ReportSummary:
    status: str
    counts: tuple[SummaryCount, ...]
    total: int
    duration: str


def configured_list_batch_size(env_name: str, default: int) -> int:
    raw_value = os.environ.get(env_name)

    if raw_value is None:
        return default

    try:
        return int(raw_value.strip())
    except ValueError:
        return default


def configured_list_batch_sizes() -> tuple[int, int]:
    return (
        configured_list_batch_size(DESKTOP_LIST_BATCH_SIZE_ENV, DESKTOP_LIST_BATCH_SIZE),
        configured_list_batch_size(MOBILE_LIST_BATCH_SIZE_ENV, MOBILE_LIST_BATCH_SIZE),
    )


def list_reveal_script(desktop_batch_size: int, mobile_batch_size: int) -> str:
    return LIST_REVEAL_SCRIPT_TEMPLATE.replace(
        "__DESKTOP_BATCH_SIZE__", str(desktop_batch_size)
    ).replace(
        "__MOBILE_BATCH_SIZE__", str(mobile_batch_size)
    )


def job_id(entry: Path) -> int | None:
    if not entry.name.startswith(JOB_PREFIX):
        return None

    try:
        return int(entry.name.removeprefix(JOB_PREFIX))
    except ValueError:
        return None


def read_modified_at(entry: Path) -> str:
    modified_at_path = entry / MODIFIED_AT_FILENAME
    if not modified_at_path.is_file():
        return ""

    lines = modified_at_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return ""

    return lines[0].strip()


def parse_modified_at(modified_at: str) -> datetime | None:
    if not modified_at:
        return None

    try:
        return datetime.fromisoformat(modified_at.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_datetime(value: datetime) -> str:
    return value.strftime("%d-%b-%Y %H:%M")


def format_entry_modified_at(entry: Path) -> str:
    modified_at = read_modified_at(entry)
    parsed_modified_at = parse_modified_at(modified_at)

    if parsed_modified_at is not None:
        return format_datetime(parsed_modified_at)

    if modified_at:
        return modified_at

    return format_datetime(datetime.fromtimestamp(entry.stat().st_mtime))


def numeric_value(value: object) -> float | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None

    return None


def integer_value(value: object) -> int:
    parsed_value = numeric_value(value)

    if parsed_value is None or parsed_value < 0:
        return 0

    return int(parsed_value)


def format_duration(duration_ms: object) -> str:
    parsed_duration = numeric_value(duration_ms)

    if parsed_duration is None or parsed_duration < 0:
        return "n/a"

    total_seconds = int(round(parsed_duration / 1000))

    if total_seconds < 1:
        return f"{int(parsed_duration)} ms"

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}h {minutes:02d}m {seconds:02d}s"

    if minutes:
        return f"{minutes}m {seconds:02d}s"

    return f"{seconds}s"


def summary_counts(
    statistic: dict[str, object],
) -> tuple[int, tuple[SummaryCount, ...]]:
    status_names = ("failed", "broken", "skipped", "passed", "unknown")
    counts = {name: integer_value(statistic.get(name)) for name in status_names}
    total = integer_value(statistic.get("total"))

    if total == 0:
        total = sum(counts.values())

    nonzero_counts = tuple(
        SummaryCount(status=name, count=count)
        for name, count in counts.items()
        if count > 0
    )

    return total, nonzero_counts


def summary_status(statistic: dict[str, object], total: int) -> str:
    if total == 0:
        return "no tests"

    for status in ("failed", "broken", "unknown"):
        if integer_value(statistic.get(status)) > 0:
            return status

    if integer_value(statistic.get("passed")) == total:
        return "passed"

    if integer_value(statistic.get("skipped")) == total:
        return "skipped"

    return "mixed"


def read_report_summary(report: Path) -> ReportSummary | None:
    summary_path = report / SUMMARY_FILENAME

    if not summary_path.is_file():
        return None

    try:
        raw_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None

    if not isinstance(raw_summary, dict):
        return None

    raw_statistic = raw_summary.get("statistic")
    statistic = raw_statistic if isinstance(raw_statistic, dict) else {}
    total, count_parts = summary_counts(statistic)

    raw_time = raw_summary.get("time")
    time = raw_time if isinstance(raw_time, dict) else {}

    return ReportSummary(
        status=summary_status(statistic, total),
        counts=count_parts,
        total=total,
        duration=format_duration(time.get("duration")),
    )


def entry_sort_key(entry: Path) -> tuple[object, ...]:
    entry_job_id = job_id(entry)
    modified_at = read_modified_at(entry)
    parsed_modified_at = parse_modified_at(modified_at)
    pinned_rank = 0 if entry.name in PINNED_ENTRY_NAMES else 1

    if parsed_modified_at is not None:
        return (
            pinned_rank,
            0,
            -parsed_modified_at.timestamp(),
            -(entry_job_id or 0),
            entry.name,
        )

    if entry_job_id is not None:
        return (pinned_rank, 1, -entry_job_id, entry.name)

    return (pinned_rank, 2, not entry.is_dir(), entry.name.casefold(), entry.name)


def iter_entries(folder: Path) -> list[Path]:
    return sorted(
        (entry for entry in folder.iterdir() if entry.name not in HIDDEN_INDEX_ENTRIES),
        key=entry_sort_key,
    )


def is_report_folder(folder: Path) -> bool:
    return folder.is_dir() and job_id(folder) is not None





REDIRECT_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url={href}">
    <title>Redirecting to latest report...</title>
    <link rel="canonical" href="{href}">
</head>
<body>
    <p>Redirecting to <a href="{href}">latest report</a>...</p>
</body>
</html>
"""


def generate_latest_alias(folder: Path) -> Path | None:
    latest_report = latest_report_for(folder)
    if latest_report is None or latest_report.parent != folder:
        return None

    latest_dir = folder / LATEST_DIRNAME
    latest_dir.mkdir(exist_ok=True)
    relative_path = "../" + quote(latest_report.name, safe="") + "/"

    index_path = latest_dir / INDEX_FILENAME
    index_path.write_text(
        REDIRECT_HTML_TEMPLATE.format(href=relative_path),
        encoding="utf-8",
    )
    return index_path


def iter_report_folders(folder: Path) -> list[Path]:
    reports: list[Path] = []

    if not folder.is_dir():
        return reports

    if is_report_folder(folder):
        return [folder]

    for entry in folder.iterdir():
        if entry.name in HIDDEN_INDEX_ENTRIES or not entry.is_dir():
            continue

        reports.extend(iter_report_folders(entry))

    return reports


def latest_report_for(folder: Path) -> Path | None:
    reports = iter_report_folders(folder)

    if not reports:
        return None

    return sorted(reports, key=entry_sort_key)[0]


def is_indexable_folder(folder: Path) -> bool:
    return folder.is_dir() and folder.name not in HIDDEN_INDEX_ENTRIES and job_id(folder) is None


def iter_index_folders(root: Path) -> list[Path]:
    folders: list[Path] = []

    def collect(folder: Path) -> None:
        folders.append(folder)

        children = sorted(
            (entry for entry in folder.iterdir() if is_indexable_folder(entry)),
            key=lambda entry: (entry.name.casefold(), entry.name),
        )

        for child in children:
            collect(child)

    collect(root)
    return folders


def link_for(entry: Path) -> str:
    suffix = "/" if entry.is_dir() else ""
    return quote(entry.name, safe="") + suffix


def label_for(entry: Path) -> str:
    suffix = "/" if entry.is_dir() else ""
    return entry.name + suffix


def link_for_path(path: Path) -> str:
    return "/".join(quote(part, safe="") for part in path.parts) + "/"


def latest_report_link(folder: Path, report: Path) -> str:
    return link_for_path(report.relative_to(folder))


def latest_report_label(report: Path) -> str:
    suffix_parts = public_suffix_parts(report)

    if suffix_parts is not None:
        return "/".join([*suffix_parts, ""])

    return report.as_posix() + "/"


def latest_report_context_label(entry: Path, report: Path) -> str:
    try:
        suffix = report.relative_to(entry)
    except ValueError:
        return latest_report_label(report)

    return suffix.as_posix() + "/"


def display_path(folder: Path) -> str:
    parts = folder.as_posix().split("/")

    if ROOT_INDEX_DIR not in parts:
        return folder.as_posix()

    public_index = len(parts) - 1 - parts[::-1].index(ROOT_INDEX_DIR)
    suffix_parts = parts[public_index + 1 :]

    return "/".join([PUBLIC_TITLE, *suffix_parts])


def public_suffix_parts(folder: Path) -> list[str] | None:
    parts = folder.as_posix().split("/")

    if ROOT_INDEX_DIR not in parts:
        return None

    public_index = len(parts) - 1 - parts[::-1].index(ROOT_INDEX_DIR)
    return parts[public_index + 1 :]


def breadcrumb_html(folder: Path) -> str:
    suffix_parts = public_suffix_parts(folder)

    if suffix_parts is None:
        return f"<h1>{escape(folder.as_posix())}</h1>"

    crumbs = [PUBLIC_TITLE, *suffix_parts]
    last_index = len(crumbs) - 1
    html_parts: list[str] = ['<h1 class="breadcrumbs" aria-label="Current location">']

    for index, crumb in enumerate(crumbs):
        if index:
            html_parts.append('<span class="breadcrumb-separator">/</span>')

        levels_up = last_index - index

        if levels_up:
            href = "../" * levels_up
            html_parts.append(
                '<a href="{href}">{label}</a>'.format(
                    href=escape(href, quote=True),
                    label=escape(crumb),
                )
            )
        else:
            html_parts.append(f'<span aria-current="page">{escape(crumb)}</span>')

    html_parts.append("</h1>")
    return "".join(html_parts)


def root_intro_html(folder: Path) -> str:
    if public_suffix_parts(folder) != []:
        return ""

    return """
        <section class="hero" aria-label="Project summary">
            <h2>GitLab Allure History Publisher</h2>
            <p>
                Branch-based Allure report history on GitLab Pages.
                No server. No database. No external storage.
            </p>
        </section>""".rstrip()


def entry_title_html(entry: Path, is_latest: bool) -> str:
    badge = ' <span class="latest-badge">latest</span>' if is_latest else ""

    return (
        '<div class="entry-title">'
        '<a class="entry-link" href="{href}">{label}</a>'
        "{badge}"
        "</div>"
    ).format(
        href=escape(link_for(entry), quote=True),
        label=escape(label_for(entry)),
        badge=badge,
    )


def folder_icon_html() -> str:
    return (
        '<svg class="history-icon" viewBox="0 0 24 24" aria-hidden="true">'
        '<path d="M3 6.5A2.5 2.5 0 0 1 5.5 4h4l2 2h7A2.5 2.5 0 0 1 21 8.5v9A2.5 2.5 0 0 1 18.5 20h-13A2.5 2.5 0 0 1 3 17.5z"/>'
        "</svg>"
    )


def latest_alias_href(folder: Path, latest_report: Path | None) -> str | None:
    if latest_report is None:
        return None

    alias_path = latest_report.parent / LATEST_DIRNAME
    return escape(link_for_path(alias_path.relative_to(folder)), quote=True)


def latest_report_link_label(entry: Path, latest_report: Path | None) -> str:
    if latest_report is None:
        return entry.name

    return latest_report.parent.name


def branch_entry_cells(folder: Path, entry: Path) -> list[str]:
    latest_report = (
        latest_report_for(entry)
        if entry.is_dir() and not is_report_folder(entry)
        else None
    )
    latest_href = latest_alias_href(folder, latest_report)

    if latest_href:
        latest_content = (
            '<div class="entry-title">'
            '<a class="entry-link latest-report-link" href="{href}">{label}</a>'
            "</div>"
        ).format(
            href=latest_href,
            label=escape(latest_report_link_label(entry, latest_report)),
        )
    elif entry.is_dir():
        latest_content = (
            '<div class="entry-title">'
            '<span class="entry-link entry-name-text">{label}</span>'
            "</div>"
        ).format(label=escape(label_for(entry)))
    else:
        latest_content = (
            '<div class="entry-title">'
            '<a class="entry-link" href="{href}">{label}</a>'
            "</div>"
        ).format(
            href=escape(link_for(entry), quote=True),
            label=escape(label_for(entry)),
        )

    if entry.is_dir():
        history_content = (
            '<a class="history-link" href="{href}" '
            'aria-label="Open {label} history" title="Open history">'
            "{icon}</a>"
        ).format(
            href=escape(link_for(entry), quote=True),
            label=escape(entry.name, quote=True),
            icon=folder_icon_html(),
        )
    else:
        history_content = ""

    return [
        f'                <td class="latest-report-cell">{latest_content}</td>',
        (
            '                <td class="history-cell" data-label="History">'
            f"{history_content}</td>"
        ),
    ]


def include_report_summary(entries: list[Path]) -> bool:
    return any(is_report_folder(entry) for entry in entries)


def is_branch_index(folder: Path) -> bool:
    suffix_parts = public_suffix_parts(folder)
    return suffix_parts is not None and len(suffix_parts) == 1


def summary_compact_html(summary: ReportSummary) -> str:
    if not summary.counts:
        return ""

    counts_dict = {c.status: c.count for c in summary.counts}
    failed = counts_dict.get("failed", 0)
    broken = counts_dict.get("broken", 0)
    skipped = counts_dict.get("skipped", 0)
    passed = counts_dict.get("passed", 0)
    unknown = counts_dict.get("unknown", 0)

    issues = failed + broken + unknown

    tooltip_parts = []
    for s in ("failed", "broken", "skipped", "passed", "unknown"):
        c = counts_dict.get(s, 0)
        if c > 0:
            tooltip_parts.append(f"{s.capitalize()}: {c}")
    tooltip = " \u00b7 ".join(tooltip_parts)

    if issues > 0:
        label = f"{issues} issue"
        if issues != 1:
            label += "s"
        label += f" \u00b7 {summary.total} total"
        css_class = "issue"
    elif passed > 0:
        label = f"{passed} passed"
        css_class = "passed"
    else:
        label = f"{skipped} skipped"
        css_class = "skipped"

    return (
        '<span class="summary-compact {css_class}" '
        'title="{tooltip}">{label}</span>'
    ).format(
        css_class=escape(css_class),
        tooltip=escape(tooltip, quote=True),
        label=escape(label),
    )


def report_summary_cells(entry: Path) -> list[str]:
    summary = read_report_summary(entry) if is_report_folder(entry) else None

    if summary is None:
        counts = "n/a"
        duration = "n/a"
    else:
        issues = summary.status in ("failed", "broken", "unknown")
        inner = summary_compact_html(summary)
        if issues:
            suffix = "#categories"
            counts = '<a href="{href}">{inner}</a>'.format(
                href=escape(link_for(entry) + suffix, quote=True),
                inner=inner,
            )
        else:
            counts = inner
        duration = summary.duration

    return [
        (
            '                <td class="result-cell" '
            'data-label="Result">{counts}</td>'
        ).format(counts=counts if summary is not None else escape(counts)),
        (
            '                <td class="duration-cell" data-label="Duration">'
            "{duration}</td>"
        ).format(duration=escape(duration)),
    ]


def entry_row(
    folder: Path,
    entry: Path,
    latest_report: Path | None,
    show_report_summary: bool,
    show_branch_navigation: bool,
) -> list[str]:
    title = entry_title_html(entry, latest_report == entry)
    summary_cells = report_summary_cells(entry) if show_report_summary else []
    primary_cells = (
        branch_entry_cells(folder, entry)
        if show_branch_navigation
        else [f'                <td class="name-cell">{title}</td>']
    )

    return [
        '            <tr data-list-row>',
        *primary_cells,
        *summary_cells,
        (
            '                <td class="modified-cell" data-label="Modified">'
            f"{escape(format_entry_modified_at(entry))}</td>"
        ),
        "            </tr>",
    ]


def empty_row(column_count: int) -> list[str]:
    return [
        "            <tr>",
        f'                <td class="name-cell" colspan="{column_count}">No reports yet.</td>',
        "            </tr>",
    ]


def list_controls_html(
    entries: list[Path],
    desktop_batch_size: int,
    mobile_batch_size: int,
) -> str:
    if not entries or (desktop_batch_size <= 0 and mobile_batch_size <= 0):
        return ""

    return """
        <div class="list-controls" hidden>
            <span class="list-count" aria-live="polite"></span>
            <button class="show-more" type="button">Show more...</button>
        </div>""".rstrip()


def generator_footer_html() -> str:
    show_footer = os.environ.get(SHOW_FOOTER_ENV, "true").strip().lower()
    if show_footer not in ("true", "1", "yes"):
        return ""

    version = os.environ.get(VERSION_ENV, "").strip()
    if version in MOVING_REF_VERSIONS:
        version = ""

    parts = [
        '<span>Generated by <a href="{url}">gitlab-allure-history</a></span>'.format(
            url=escape(GENERATOR_URL, quote=True),
        )
    ]
    if version:
        parts.append('<span class="dot-separator">\u00b7</span>')
        parts.append(f'<span class="generator-version">{escape(version)}</span>')

    return (
        '<footer class="generator-footer">'
        '<span class="generator-footer-content">{text}</span>'
        '</footer>'
    ).format(text=" ".join(parts))


def build_index_html(folder: Path, entries: list[Path]) -> str:
    title = display_path(folder)
    desktop_batch_size, mobile_batch_size = configured_list_batch_sizes()
    latest_report = latest_report_for(folder)
    show_report_summary = include_report_summary(entries)
    show_branch_navigation = not show_report_summary and is_branch_index(folder)
    column_count = 4 if show_report_summary else 3 if show_branch_navigation else 2
    table_mode_class = "has-summary" if show_report_summary else "directory-index"
    table_headers = (
        """
                    <th class="name-cell">Name</th>
                    <th class="result-cell">Result</th>
                    <th class="duration-cell">Duration</th>""".rstrip()
        if show_report_summary
        else """
                    <th class="latest-report-cell">Latest report</th>
                    <th class="history-cell">History</th>""".rstrip()
        if show_branch_navigation
        else """
                    <th class="name-cell">Name</th>""".rstrip()
    )
    rows: list[str] = []

    if entries:
        for entry in entries:
            rows.extend(
                entry_row(
                    folder,
                    entry,
                    latest_report,
                    show_report_summary,
                    show_branch_navigation,
                )
            )
    else:
        rows.extend(empty_row(column_count))

    body = "\n".join(rows)

    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <script>
{THEME_INIT_SCRIPT.rstrip()}
    </script>
    <style>
{STYLE.rstrip()}
    </style>
</head>
<body>
    <main>
        <div class="page-header">
            {breadcrumb_html(folder)}
            <button class="theme-toggle" type="button" aria-label="Switch theme" title="Switch theme">Theme</button>
        </div>
{root_intro_html(folder)}
        <table class="index-table {table_mode_class}" data-progressive-list>
            <thead>
                <tr>
{table_headers}
                    <th class="modified-cell">Modified</th>
                </tr>
            </thead>
            <tbody>
{body}
            </tbody>
        </table>
{list_controls_html(entries, desktop_batch_size, mobile_batch_size)}
    </main>
    {generator_footer_html()}
    <script>
{THEME_TOGGLE_SCRIPT.rstrip()}
    </script>
    <script>
{list_reveal_script(desktop_batch_size, mobile_batch_size).rstrip()}
    </script>
</body>
</html>
"""


def index_folder(folder: str | Path) -> Path:
    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)

    print(f"Indexing: {path.as_posix()}/")

    index_path = path / INDEX_FILENAME
    index_path.write_text(build_index_html(path, iter_entries(path)), encoding="utf-8")

    generate_latest_alias(path)

    return index_path


def index_tree(root: str | Path) -> list[Path]:
    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)

    return [index_folder(folder) for folder in iter_index_folders(path)]


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--recursive":
        index_tree(argv[2])
        return 0

    if len(argv) != 2:
        print("Usage: python3 _generate_index.py [--recursive] <folder>", file=sys.stderr)
        return 2

    index_folder(argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
