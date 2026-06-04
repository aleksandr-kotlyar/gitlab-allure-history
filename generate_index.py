from __future__ import annotations

import sys
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import quote


STYLE = """
        body {
            color: #222;
            font-family: Arial, Helvetica, sans-serif;
            margin: 2rem;
        }
        h1 {
            font-size: 1.4rem;
            margin-bottom: 1rem;
        }
        table {
            border-collapse: collapse;
            min-width: 32rem;
        }
        th, td {
            border-bottom: 1px solid #ddd;
            padding: 0.45rem 0.75rem;
            text-align: left;
        }
        th {
            color: #555;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        a {
            color: #0645ad;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
"""


def entry_sort_key(path: Path) -> tuple[bool, str, str]:
    """Sort directories first, then names case-insensitively and stably."""
    return (not path.is_dir(), path.name.casefold(), path.name)


def iter_entries(folder: Path) -> list[Path]:
    return sorted(
        (entry for entry in folder.iterdir() if entry.name != "index.html"),
        key=entry_sort_key,
    )


def format_modified_at(path: Path) -> str:
    modified_ts = path.stat().st_mtime
    return datetime.fromtimestamp(modified_ts).strftime("%d-%b-%Y %H:%M")


def link_for(entry: Path) -> str:
    suffix = "/" if entry.is_dir() else ""
    return quote(entry.name, safe="") + suffix


def label_for(entry: Path) -> str:
    suffix = "/" if entry.is_dir() else ""
    return entry.name + suffix


def display_path(folder: Path) -> str:
    parts = folder.as_posix().split("/")
    if "public" in parts:
        return "/".join(parts[parts.index("public") :])
    return folder.as_posix()


def build_index_html(folder: Path, entries: list[Path]) -> str:
    title = f"Index of {display_path(folder)}"
    rows = [
        "            <tr>",
        '                <td><a href="../">../</a></td>',
        "                <td></td>",
        "            </tr>",
    ]

    if entries:
        for entry in entries:
            rows.extend(
                [
                    "            <tr>",
                    '                <td><a href="{href}">{label}</a></td>'.format(
                        href=escape(link_for(entry), quote=True),
                        label=escape(label_for(entry)),
                    ),
                    f"                <td>{format_modified_at(entry)}</td>",
                    "            </tr>",
                ]
            )
    else:
        rows.extend(
            [
                "            <tr>",
                '                <td colspan="2">No reports yet.</td>',
                "            </tr>",
            ]
        )

    body = "\n".join(rows)

    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{escape(title)}</title>
    <style>
{STYLE.rstrip()}
    </style>
</head>
<body>
    <h1>{escape(title)}</h1>
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
</body>
</html>
"""


def index_folder(folder: str | Path) -> Path:
    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)

    print(f"Indexing: {path.as_posix()}/")
    index_path = path / "index.html"
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
