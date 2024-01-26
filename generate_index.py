import os
import sys

INDEX_TEXT_START = """<!DOCTYPE html>
<html>
<head><title>Index of {folderPath}</title></head>
<body>
    <h2>Index of {folderPath}</h2>
    <hr>
    <ul>
        <li>
            <a href='../'>../</a>
        </li>
"""
INDEX_TEXT_END = """
    </ul>
</body>
</html>
"""


def index_folder(path_):
    print("Indexing: " + path_ + '/')
    # Getting the content of the folder
    files = os.listdir(folder_path)
    # If Root folder, correcting folder name
    root = path_
    if path_.startswith('public'):
        root = path_.replace('public', 'gitlab-allure-history')
    index_text = INDEX_TEXT_START.format(folderPath=root)
    for file in sorted(files):
        # Avoiding index.html files
        if file != 'index.html':
            index_text += "\t\t<li>\n\t\t\t<a href='" + file + "'>" \
                + file \
                + "</a>\n\t\t</li>\n"
        # Recursive call to continue indexing
        # if os.path.isdir(folder_path + '/' + file):
        #     index_folder(folder_path + '/' + file)
    index_text += INDEX_TEXT_END
    # Create or override previous index.html
    # Save indexed content to file
    with open(path_ + '/index.html', "w") as index:
        index.write(index_text)


folder_path = sys.argv[1]


# Indexing root directory (Script position)
index_folder(folder_path)
