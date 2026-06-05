import os
import sys
from datetime import datetime

INDEX_FILENAME = "index.html"
JOB_PREFIX = "job_"
MODIFIED_AT_FILENAME = ".modified_at"
HISTORY_DIRNAME = "history"
HIDDEN_INDEX_ENTRIES = {INDEX_FILENAME, MODIFIED_AT_FILENAME, HISTORY_DIRNAME}
ROOT_INDEX_DIR = "public"

INDEX_TEXT_START = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{folderPath}</title>
    <style>
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

        h2 {
            margin: 0 0 16px;
            font-size: 24px;
            font-weight: 650;
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

            h2 {
                font-size: 20px;
                overflow-wrap: anywhere;
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
            :root {
                --bg: #0d1117;
                --panel: #161b22;
                --text: #e6edf3;
                --muted: #8b949e;
                --border: #30363d;
                --row: #21262d;
                --link: #58a6ff;
            }
        }
    </style>
</head>
<body>
    <main>
    <h2>{folderPath}</h2>
    <table>
        <thead>
        <tr>
            <th>Name</th>
            <th>Modified</th>
        </tr>
        </thead>
        <tbody>
"""
PARENT_ROW = """        <tr>
            <td class="name-cell"><a href='../'>../</a></td>
            <td class="modified-cell"></td>
        </tr>
"""
INDEX_TEXT_END = """
        </tbody>
    </table>
    </main>
</body>
</html>
"""


def job_id(file_name):
    if not file_name.startswith(JOB_PREFIX):
        return None

    try:
        return int(file_name.removeprefix(JOB_PREFIX))
    except ValueError:
        return None


def read_modified_at(folder_path, file_name):
    modified_at_path = os.path.join(folder_path, file_name, MODIFIED_AT_FILENAME)
    if not os.path.isfile(modified_at_path):
        return ""

    with open(modified_at_path, encoding="utf-8") as modified_at_file:
        return modified_at_file.readline().strip()


def parse_modified_at(modified_at):
    if not modified_at:
        return None

    try:
        return datetime.fromisoformat(modified_at.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_modified_at(modified_at):
    parsed_modified_at = parse_modified_at(modified_at)
    if parsed_modified_at is None:
        return modified_at

    return parsed_modified_at.strftime("%d-%b-%Y %H:%M")


def index_sort_key(folder_path, file_name):
    file_job_id = job_id(file_name)
    modified_at = read_modified_at(folder_path, file_name)
    parsed_modified_at = parse_modified_at(modified_at)

    if parsed_modified_at is not None:
        return (0, -parsed_modified_at.timestamp(), -(file_job_id or 0), file_name)

    if file_job_id is not None:
        return (1, -file_job_id, file_name)

    return (2, file_name)


def show_parent_link(folder_path):
    return os.path.normpath(folder_path) != ROOT_INDEX_DIR


def index_folder(folder_path):
    folder_path = os.fspath(folder_path)
    print("Indexing: " + folder_path + '/')
    # Getting the content of the folder
    files = [
        file_
        for file_ in os.listdir(folder_path)
        if file_ not in HIDDEN_INDEX_ENTRIES
    ]
    # If Root folder, correcting folder name
    root = folder_path
    if folder_path.startswith('public'):
        root = folder_path.replace('public', 'gitlab-allure-history')
    index_text = INDEX_TEXT_START.replace("{folderPath}", root)
    if show_parent_link(folder_path):
        index_text += PARENT_ROW
    files.sort(key=lambda file_: index_sort_key(folder_path, file_))
    for file in files:
        modified_at = format_modified_at(read_modified_at(folder_path, file))
        index_text += (
            "\t\t<tr>\n"
            "\t\t\t<td class=\"name-cell\"><a href='" + file + "'>" + file + "</a></td>\n"
            "\t\t\t<td class=\"modified-cell\">" + modified_at + "</td>\n"
            "\t\t</tr>\n"
        )
        # Recursive call to continue indexing
        # if os.path.isdir(folder_path + '/' + file):
        #     index_folder(folder_path + '/' + file)
    index_text += INDEX_TEXT_END
    # Create or override previous index.html
    # Save indexed content to file
    with open(folder_path + '/index.html', "w", encoding="utf-8") as index:
        index.write(index_text)


if __name__ == "__main__":
    folder_path = sys.argv[1]

    # Indexing root directory (Script position)
    index_folder(folder_path)
