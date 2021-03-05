import os
import sys

indexTextStart = """<!DOCTYPE html>
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
indexTextEnd = """
    </ul>
</body>
</html>
"""


def index_folder(folder_path):
    print("Indexing: " + folder_path + '/')
    # Getting the content of the folder
    files = os.listdir(folder_path)
    # If Root folder, correcting folder name
    root = folder_path
    if folder_path.startswith('public'):
        root = folder_path.replace('public', 'gitlab-allure-history')
    index_text = indexTextStart.format(folderPath=root)
    for file in sorted(files):
        # Avoiding index.html files
        if file != 'index.html':
            index_text += "\t\t<li>\n\t\t\t<a href='" + file + "'>" + file + "</a>\n\t\t</li>\n"
        # Recursive call to continue indexing
        # if os.path.isdir(folder_path + '/' + file):
        #     index_folder(folder_path + '/' + file)
    index_text += indexTextEnd
    # Create or override previous index.html
    index = open(folder_path + '/index.html', "w")
    # Save indexed content to file
    index.write(index_text)


folder_path = sys.argv[1]


# Indexing root directory (Script position)
index_folder(folder_path)
