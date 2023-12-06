import os
import re
import datetime
import sys
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
EC = '\033[0m'

SOURCE_FOLDER = r"C:\\Users\\franc\\Downloads\\source"
MIN_DATE = datetime.date(2023, 10, 1)

FILE_TO_WATCH = [
    '*jobinfo.xml',
]

FOLDER_TO_IGNORE = [
    'figures',
]

if not os.path.exists(SOURCE_FOLDER):
    print(SOURCE_FOLDER, "not found")
    sys.exit()


def is_greather_min_date(file_path: str) -> bool:
    mtime = datetime.date.fromtimestamp(os.path.getmtime(file_path))
    return mtime >= MIN_DATE


def is_watched_file(file_name: str) -> bool:
    reasons = []
    for exp in FILE_TO_WATCH:
        regex = exp.replace('*', '.*')
        if re.fullmatch(regex, file_name, re.IGNORECASE) is not None:
            reasons.append(exp)

    if len(reasons) > 0:
        return True
    else:
        return False


def is_ignored_folder(folder_name: str) -> bool:
    reasons = []
    for exp in FOLDER_TO_IGNORE:
        regex = exp.replace('*', '.*')
        if re.fullmatch(regex, folder_name, re.IGNORECASE) is not None:
            reasons.append(exp)

    if len(reasons) > 0:
        return True
    else:
        return False


def find_watched_paths(folder_path: str):
    for entry in os.scandir(folder_path):
        if entry.is_file():
            if is_watched_file(entry.name) and is_greather_min_date(entry.path):
                print(GREEN + 'Found:', entry.path, EC)
        elif entry.is_dir() and not is_ignored_folder(entry.name):
            find_watched_paths(entry.path)


find_watched_paths(SOURCE_FOLDER)
