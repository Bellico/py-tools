import os
import re
import sys
import shutil
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
EC = '\033[0m'

SOURCE_FOLDER = r"D:\\Downloads\\source\\"
WITH_DELETE = False
FILE_TO_KEEP = [
    '*.xml',
    'un_nom_precis',
    'commence_par*',
    '*fini_par',
    '*commence_et_fini_par*',
    'quelque_chose*au_milieu',
    'plusieur*chose*au_milieu',
]

FOLDER_TO_DELETE = [
    'figures',
]

if not os.path.exists(SOURCE_FOLDER):
    print(SOURCE_FOLDER, "not found")
    sys.exit()


def delete_or_not(file_name: str, file_path: str) -> int:
    reasons = []
    for exp in FILE_TO_KEEP:
        regex = exp.replace('*', '.*')
        if re.fullmatch(regex, file_name, re.IGNORECASE) is not None:
            reasons.append(exp)

    if len(reasons) == 0:
        if WITH_DELETE:
            os.remove(file_path)
        print(RED + file_path, 'removed' + EC)
        return 1
    else:
        return 0


def delete_or_not_folder(folder_name: str, folder_path: str) -> int:
    reasons = []
    for exp in FOLDER_TO_DELETE:
        regex = exp.replace('*', '.*')
        if re.fullmatch(regex, folder_name, re.IGNORECASE) is not None:
            reasons.append(exp)

    if len(reasons) > 0:
        if WITH_DELETE:
            shutil.rmtree(folder_path)
        print(RED + folder_path, 'removed' + EC)
        return 1
    else:
        return 0


def clean_deep_folder(folder_path: str):
    count_deleted = 0

    for entry in os.scandir(folder_path):
        if entry.is_file():
            count_deleted += delete_or_not(entry.name, entry.path)
        elif entry.is_dir():
            is_delete = delete_or_not_folder(entry.name, entry.path)
            if is_delete == 0:
                count_deleted += clean_deep_folder(entry.path)

    return count_deleted


count = clean_deep_folder(SOURCE_FOLDER)
print(GREEN + f"[{SOURCE_FOLDER}]", 'was cleaned of', count, 'file(s)', EC)
