from __future__ import annotations

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
            margin: 0 0 16px;
        }

        h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 650;
            overflow-wrap: anywhere;
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

        .name-cell {
            width: 70%;
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

    if parsed_modified_at is not None:
        return (0, -parsed_modified_at.timestamp(), -(entry_job_id or 0), entry.name)

    if entry_job_id is not None:
        return (1, -entry_job_id, entry.name)

    return (2, not entry.is_dir(), entry.name.casefold(), entry.name)


def iter_entries(folder: Path) -> list[Path]:
    return sorted(
        (entry for entry in folder.iterdir() if entry.name not in HIDDEN_INDEX_ENTRIES),
        key=entry_sort_key,
    )


def link_for(entry: Path) -> str:
    suffix = "/" if entry.is_dir() else ""
    return quote(entry.name, safe="") + suffix


def label_for(entry: Path) -> str:
    suffix = "/" if entry.is_dir() else ""
    return entry.name + suffix


def display_path(folder: Path) -> str:
    parts = folder.as_posix().split("/")

    if ROOT_INDEX_DIR not in parts:
        return folder.as_posix()

    public_index = len(parts) - 1 - parts[::-1].index(ROOT_INDEX_DIR)
    suffix_parts = parts[public_index + 1 :]

    return "/".join([PUBLIC_TITLE, *suffix_parts])


def show_parent_link(folder: Path) -> bool:
    return folder.name != ROOT_INDEX_DIR


def parent_row() -> list[str]:
    return [
        "            <tr>",
        '                <td class="name-cell"><a href="../">../</a></td>',
        '                <td class="modified-cell"></td>',
        "            </tr>",
    ]


def entry_row(entry: Path) -> list[str]:
    return [
        "            <tr>",
        '                <td class="name-cell"><a href="{href}">{label}</a></td>'.format(
            href=escape(link_for(entry), quote=True),
            label=escape(label_for(entry)),
        ),
        f'                <td class="modified-cell">{escape(format_entry_modified_at(entry))}</td>',
        "            </tr>",
    ]


def empty_row() -> list[str]:
    return [
        "            <tr>",
        '                <td class="name-cell" colspan="2">No reports yet.</td>',
        "            </tr>",
    ]


def build_index_html(folder: Path, entries: list[Path]) -> str:
    title = display_path(folder)
    rows: list[str] = []

    if show_parent_link(folder):
        rows.extend(parent_row())

    if entries:
        for entry in entries:
            rows.extend(entry_row(entry))
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
            <h1>{escape(title)}</h1>
            <button class="theme-toggle" type="button" aria-label="Switch theme" title="Switch theme">Theme</button>
        </div>
        <table>
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
    </main>
    <script>
{THEME_TOGGLE_SCRIPT.rstrip()}
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


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python3 generate_index.py <folder>", file=sys.stderr)
        return 2

    index_folder(argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
