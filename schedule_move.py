import os
from collections import deque
import shutil
import time
import re
import logging
import subprocess
import schedule
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
EC = '\033[0m'

SOURCE_FOLDER = r"C:\Users\Franck\Downloads\source"
DUPLICATE_FOLDER = r"C:\Users\Franck\Downloads\dupl"
DESTINATION_FOLDER = r"C:\Users\Franck\Downloads\dest"
ERROR_FOLDER = r"C:\Users\Franck\Downloads\error"
LOG_FILE = r"log.txt"
RETRY = '/r:3 /w:10'
TIME = 5  # Démarrer le décompte de 1 minutes (60 secondes)
SUB_LEVEL_MANDATORY_DEPTH = 5
MANDATORY_MOVE_ERROR = True

MANDATORY_FILES_1 = [
    '*.ppt',
]

MANDATORY_FILES_2 = [
]

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', filemode='a')
logger = logging.getLogger()


def printlog(messagelog, color=""):
    print(color + messagelog + EC)
    if color == RED:
        logger.error(messagelog)
    else:
        logger.info(messagelog)


def copy_folder(file_source_path, file_destination_path) -> int:
    command = f'robocopy "{file_source_path}" "{file_destination_path}" /e /njh /njs /ndl /nc /ns /log+:log.txt {RETRY}'
    result = subprocess.run(command, shell=True, text=True)

    return result.returncode


def move_safe_folder(folder_source_path: str, folder_destination_path: str) -> int:
    result = copy_folder(folder_source_path, folder_destination_path)
    if result == 1:
        return try_delete(folder_source_path)
    else:
        shutil.rmtree(folder_destination_path)


def try_delete(path: str) -> int:
    try:
        shutil.rmtree(path)
        return 0
    except Exception as inst:
        logger.error("ERROR during delete of :" + path + " => " + str(inst))
        print(RED + "Failed to delete", path, EC)
        return 1


def match_a_file(entry_name: str, mandatories: []) -> []:
    reasons = []
    for exp in mandatories:
        regex = exp.replace('*', '.*')
        if re.fullmatch(regex, entry_name, re.IGNORECASE) is not None:
            reasons.append(exp)

    return reasons


def get_item_excluded(origin: [], element: []) -> []:
    return [i for i in origin if i not in element]


def find_matching_pattern(folder_path: str, mandatory_files: []) -> []:
    sublevel_to_look = [folder_path]
    matching_pattern = []
    targeted_files = mandatory_files

    # Scan level
    depth = 0
    while any(sublevel_to_look) and depth <= SUB_LEVEL_MANDATORY_DEPTH:
        temp_to_look = deque()

        for path in sublevel_to_look:
            for entry in os.scandir(path):
                matches = match_a_file(entry.name, targeted_files)

                if any(matches):
                    matching_pattern.extend(matches)
                    targeted_files = get_item_excluded(
                        targeted_files, matching_pattern)

                if len(matching_pattern) == len(mandatory_files):
                    return matching_pattern

                if entry.is_dir():
                    temp_to_look.append(entry.path)

        depth = depth + 1
        sublevel_to_look.clear()
        sublevel_to_look.extend(temp_to_look)

    return matching_pattern


def search_missing_patterns(source_path: str):
    matching_pattern1 = find_matching_pattern(source_path, MANDATORY_FILES_1)
    if len(matching_pattern1) == len(MANDATORY_FILES_1):
        return None

    matching_pattern2 = find_matching_pattern(source_path, MANDATORY_FILES_2)
    if len(matching_pattern2) == len(MANDATORY_FILES_2):
        return None

    return str(get_item_excluded(MANDATORY_FILES_1, matching_pattern1)) + str(get_item_excluded(MANDATORY_FILES_2, matching_pattern2))


def dispatch(file_name: str):
    source_path = os.path.join(SOURCE_FOLDER, file_name)
    destination_path = os.path.join(DESTINATION_FOLDER, file_name)
    error_path = os.path.join(ERROR_FOLDER, file_name)
    is_dir = os.path.isdir(source_path)

    if not is_dir:
        return

    printlog("Start process for: " + file_name, GREEN)

    # Error (existing)
    if os.path.exists(destination_path):
        move_safe_folder(source_path, error_path)
        printlog("Moved Folder in error: " + file_name + " => Already in destination", RED)
        return

    # Error (missing patterns)
    missings = search_missing_patterns(source_path)
    if missings is not None:
        if MANDATORY_MOVE_ERROR:
            move_safe_folder(source_path, error_path)
            printlog("Moved Folder in error: " + file_name + " => Missings : " + missings, RED)
        else:
            printlog("Folder incomplete: " + file_name + " => Missings : " + missings, RED)

    # Copy
    if DUPLICATE_FOLDER:
        duplicate_path = os.path.join(DUPLICATE_FOLDER, file_name)
        copy_folder(source_path, duplicate_path)
        printlog("Copied Folder in duplicate : " + file_name, YELLOW)

    # Move
    move_safe_folder(source_path, destination_path)
    printlog("Moved Folder in destination: " + file_name, YELLOW)


def move_files():
    file_list = os.listdir(SOURCE_FOLDER)
    if not any(file_list):
        print("Nothing to move")
        return

    printlog("Processing start:")

    for file_name in file_list:
        try:
            dispatch(file_name)
        except Exception as inst:
            printlog("Folder in error: " + file_name + " => " + str(inst), RED)

    printlog("Process Done.")


t = TIME


def countdown():
    global t

    if t > 0:
        print("Next run in", t, "seconds.", end="")
        t -= 1
    else:
        print(end="\n")
        move_files()
        t = TIME


schedule.every(1).seconds.do(countdown)

while True:
    schedule.run_pending()
    time.sleep(1)
