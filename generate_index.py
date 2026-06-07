from __future__ import annotations

import os
import sys
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import quote


INDEX_FILENAME = "index.html"
JOB_PREFIX = "job_"
MODIFIED_AT_FILENAME = ".modified_at"
HISTORY_DIRNAME = "history"
HIDDEN_INDEX_ENTRIES = {INDEX_FILENAME, MODIFIED_AT_FILENAME, HISTORY_DIRNAME}

ROOT_INDEX_DIR = "public"
PUBLIC_TITLE = "gitlab-allure-history"
PINNED_ENTRY_NAMES = {"master"}
DESKTOP_LIST_BATCH_SIZE_ENV = "ALLURE_HISTORY_INDEX_DESKTOP_BATCH_SIZE"
MOBILE_LIST_BATCH_SIZE_ENV = "ALLURE_HISTORY_INDEX_MOBILE_BATCH_SIZE"
DESKTOP_LIST_BATCH_SIZE = 25
MOBILE_LIST_BATCH_SIZE = 12

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
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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
            min-width: 72px;
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

        .theme-toggle:hover {
            background: var(--row);
        }

        .theme-toggle:focus-visible {
            outline: 2px solid var(--link);
            outline-offset: 2px;
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

        .name-cell {
            width: 70%;
        }

        .entry-title {
            display: flex;
            min-width: 0;
            align-items: center;
            gap: 8px;
        }

        .entry-link {
            min-width: 0;
            overflow-wrap: anywhere;
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

        .entry-meta {
            display: flex;
            min-width: 0;
            align-items: baseline;
            gap: 5px;
            margin-top: 1px;
            color: var(--muted);
            font-size: 12px;
            line-height: 1.25;
            overflow-wrap: anywhere;
        }

        .entry-meta-label {
            flex: 0 0 auto;
            color: var(--muted);
            font-weight: 500;
        }

        .entry-meta-link {
            min-width: 0;
            color: var(--muted);
            overflow-wrap: anywhere;
        }

        .entry-meta-link:hover {
            color: var(--link);
        }

        .modified-cell {
            color: var(--muted);
            font-variant-numeric: tabular-nums;
            text-align: right;
            white-space: nowrap;
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
                min-width: 68px;
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

            .name-cell {
                width: 100%;
                padding-bottom: 2px;
            }

            .modified-cell {
                padding-top: 0;
                text-align: left;
            }

            .list-controls {
                align-items: stretch;
                flex-direction: column;
            }

            .show-more {
                width: 100%;
            }
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


def latest_report_meta_html(folder: Path, entry: Path) -> str:
    if not entry.is_dir() or is_report_folder(entry):
        return ""

    latest_report = latest_report_for(entry)

    if latest_report is None:
        return ""

    return (
        '<div class="entry-meta">'
        '<span class="entry-meta-label">latest:</span>'
        '<a class="entry-meta-link" href="{href}" title="{title}">{label}</a>'
        "</div>"
    ).format(
        href=escape(latest_report_link(folder, latest_report), quote=True),
        title=escape(latest_report_label(latest_report), quote=True),
        label=escape(latest_report_context_label(entry, latest_report)),
    )


def entry_row(folder: Path, entry: Path, latest_report: Path | None) -> list[str]:
    title = entry_title_html(entry, latest_report == entry)
    meta = latest_report_meta_html(folder, entry)

    return [
        '            <tr data-list-row>',
        f'                <td class="name-cell">{title}{meta}</td>',
        f'                <td class="modified-cell">{escape(format_entry_modified_at(entry))}</td>',
        "            </tr>",
    ]


def empty_row() -> list[str]:
    return [
        "            <tr>",
        '                <td class="name-cell" colspan="2">No reports yet.</td>',
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


def build_index_html(folder: Path, entries: list[Path]) -> str:
    title = display_path(folder)
    desktop_batch_size, mobile_batch_size = configured_list_batch_sizes()
    latest_report = latest_report_for(folder)
    rows: list[str] = []

    if entries:
        for entry in entries:
            rows.extend(entry_row(folder, entry, latest_report))
    else:
        rows.extend(empty_row())

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
        <table data-progressive-list>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Modified</th>
                </tr>
            </thead>
            <tbody>
{body}
            </tbody>
        </table>
{list_controls_html(entries, desktop_batch_size, mobile_batch_size)}
    </main>
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
        print("Usage: python3 generate_index.py [--recursive] <folder>", file=sys.stderr)
        return 2

    index_folder(argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
