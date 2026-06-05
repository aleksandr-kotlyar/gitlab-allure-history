import os
import sys
from datetime import datetime

INDEX_FILENAME = "index.html"
JOB_PREFIX = "job_"
MODIFIED_AT_FILENAME = ".modified_at"

INDEX_TEXT_START = """<!DOCTYPE html>
<html>
<head><title>Index of {folderPath}</title></head>
<body>
    <h2>Index of {folderPath}</h2>
    <hr>
    <table>
        <tbody>
        <tr>
            <td><a href='../'>../</a></td>
            <td></td>
        </tr>
"""
INDEX_TEXT_END = """
        </tbody>
    </table>
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
        return (1, parsed_modified_at.timestamp(), file_job_id or -1, file_name)

    if file_job_id is not None:
        return (0, file_job_id, file_name)

    return (2, file_name)


def index_folder(folder_path):
    folder_path = os.fspath(folder_path)
    print("Indexing: " + folder_path + '/')
    # Getting the content of the folder
    files = [
        file_
        for file_ in os.listdir(folder_path)
        if file_ not in {INDEX_FILENAME, MODIFIED_AT_FILENAME}
    ]
    # If Root folder, correcting folder name
    root = folder_path
    if folder_path.startswith('public'):
        root = folder_path.replace('public', 'gitlab-allure-history')
    index_text = INDEX_TEXT_START.format(folderPath=root)
    files.sort(key=lambda file_: index_sort_key(folder_path, file_))
    for file in files:
        modified_at = format_modified_at(read_modified_at(folder_path, file))
        index_text += (
            "\t\t<tr>\n"
            "\t\t\t<td><a href='" + file + "'>" + file + "</a></td>\n"
            "\t\t\t<td>" + modified_at + "</td>\n"
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
