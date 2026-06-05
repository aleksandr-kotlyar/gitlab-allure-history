import os
import sys
from datetime import datetime

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


def index_folder(folder_path):
    print("Indexing: " + folder_path + '/')
    # Getting the content of the folder
    files = [file_ for file_ in os.listdir(folder_path) if file_ != 'index.html']
    # If Root folder, correcting folder name
    root = folder_path
    if folder_path.startswith('public'):
        root = folder_path.replace('public', 'gitlab-allure-history')
    index_text = INDEX_TEXT_START.format(folderPath=root)
    for file in sorted(files):
        modified_ts = os.path.getmtime(os.path.join(folder_path, file))
        modified_at = datetime.fromtimestamp(modified_ts).strftime("%d-%b-%Y %H:%M")
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


folder_path = sys.argv[1]

# Indexing root directory (Script position)
index_folder(folder_path)
