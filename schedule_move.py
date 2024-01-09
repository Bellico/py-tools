import os
from collections import deque
import shutil
import time
import re
import logging
from datetime import datetime as date
import schedule
from tqdm import tqdm
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
EC = '\033[0m'

SOURCE_FOLDER = r"C:\Users\franc\Downloads\source"
DUPLICATE_FOLDER = r"C:\Users\franc\Downloads\second"
DESTINATION_FOLDER = r"C:\Users\franc\Downloads\dest"
ERROR_FOLDER = r"C:\Users\franc\Downloads\error"
LOG_FILE = r"log.txt"
TIME = 5  # Démarrer le décompte de 1 minutes (60 secondes)
RETRY_DELAY = [5, 10, 15, 30, 60]
SUB_LEVEL_MANDATORY_DEPTH = 5

MANDATORY_FILES_1 = [
    'fichierrequis.xml',
    '*.ppt',
]

MANDATORY_FILES_2 = [
]

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s', filemode='a')
logger = logging.getLogger()


def printlog(messagelog, color=""):
    print(color + messagelog + EC)
    if color == RED:
        logger.error(messagelog)
    else:
        logger.info(messagelog)


def progress_copy(file_source_path: str, file_destination_path: str):
    size = os.path.getsize(file_source_path)
    basename = os.path.basename(file_source_path)

    # Keep shutil copy method for small files
    if size < 52_428_800:
        shutil.copy2(file_source_path, file_destination_path)
    else:
        with open(file_source_path, 'rb') as source, open(file_destination_path, 'ab') as target:
            with tqdm(ncols=150, total=size, unit='B', unit_scale=True, unit_divisor=1024, leave=False) as pbar:
                pbar.set_description(basename, refresh=True)
                while True:
                    buf = source.read(104_8576)
                    if len(buf) == 0:
                        print(end="\r")
                        break
                    target.write(buf)
                    pbar.update(len(buf))

        # Keep metadata
        shutil.copystat(file_source_path, file_destination_path)


def try_copy(file_source_path: str, file_destination_path: str, retry_count=0) -> int:
    try:
        progress_copy(file_source_path, file_destination_path)
        print(date.now().strftime("%H:%M:%S"), "|",
              file_source_path, GREEN + "Copied!", EC)
        return 0
    except Exception as inst:
        # Delete for clean retry
        if os.path.exists(file_destination_path):
            os.remove(file_destination_path)

        if retry_count == len(RETRY_DELAY):
            logger.error("ERROR during the copy for :" +
                         file_destination_path + " => " + str(inst))
            print(RED + "Failed to copy", file_destination_path, EC)
            return 1
        else:
            print(YELLOW + "ERROR... new attempt of", file_source_path,
                  "in", RETRY_DELAY[retry_count], "seconds", EC)
            time.sleep(RETRY_DELAY[retry_count])
            return try_copy(file_source_path, file_destination_path, retry_count + 1)


def try_move(source_path: str, destination_path: str, retry_count=0) -> int:
    try:
        shutil.move(source_path, destination_path)
        return 0
    except Exception as inst:
        # Delete for clean retry
        if os.path.exists(destination_path):
            shutil.rmtree(destination_path)

        if retry_count == len(RETRY_DELAY):
            logger.error("ERROR during move for :" +
                         destination_path + " => " + str(inst))
            print(RED + "Failed to move", destination_path, EC)
            return 1
        else:
            print(YELLOW + "ERROR MOVE... new attempt of", source_path,
                  "in", RETRY_DELAY[retry_count], "seconds", EC)
            time.sleep(RETRY_DELAY[retry_count])
            return try_move(source_path, destination_path, retry_count + 1)


def copy_folder(folder_source_path: str, folder_destination_path: str) -> int:
    error_count = 0

    if not os.path.exists(folder_destination_path):
        os.mkdir(folder_destination_path)

    for path in os.listdir(folder_source_path):
        file_source_path = os.path.join(folder_source_path, path)
        file_destination_path = os.path.join(folder_destination_path, path)

        # Handle file
        if os.path.isfile(file_source_path):
            # Check the valid scope
            # If the file already exist but has wrong size an error must have occurred, remove to undo the copy
            if os.path.exists(file_destination_path) and os.path.getsize(file_destination_path) < os.path.getsize(file_source_path):
                os.remove(file_destination_path)

            # Check if the file does not already exist
            if not os.path.exists(file_destination_path):
                # Copy file in the destination with an equivalent path
                error_count += try_copy(file_source_path,
                                        file_destination_path)

        # Handle folder as recursively
        elif os.path.isdir(file_source_path):
            error_count += copy_folder(file_source_path, file_destination_path)

    return error_count


def copydelete_folder(folder_source_path: str, folder_destination_path: str):
    error_count = copy_folder(folder_source_path, folder_destination_path)
    if error_count == 0:
        shutil.rmtree(folder_source_path)
    else:
        shutil.rmtree(folder_destination_path)


def copydelete_file(file_source_path: str, file_destination_path: str):
    error_count = try_copy(file_source_path, file_destination_path)
    if error_count == 0:
        os.remove(file_source_path)
    else:
        shutil.rmtree(file_destination_path)


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


def move_files():
    file_list = os.listdir(SOURCE_FOLDER)
    if not any(file_list):
        print("Nothing to move")
        return

    printlog("Processing start:")

    for file_name in file_list:
        source_path = os.path.join(SOURCE_FOLDER, file_name)
        destination_path = os.path.join(DESTINATION_FOLDER, file_name)
        error_path = os.path.join(ERROR_FOLDER, file_name)
        is_dir = os.path.isdir(source_path)

        # Error (existing)
        if is_dir and os.path.exists(destination_path):
            result = try_move(source_path, error_path)
            if result == 0:
                printlog("Folder already in destination: " + file_name, RED)
            continue

        # Error (missing patterns)
        if is_dir:
            missings = search_missing_patterns(source_path)
            if missings is not None:
                result = try_move(source_path, error_path)
                if result == 0:
                    printlog("Moved Folder in error: " + file_name +
                             " => Missings : " + missings, RED)
                continue

        # Copy
        if DUPLICATE_FOLDER:
            duplicate_path = os.path.join(DUPLICATE_FOLDER, file_name)

            if is_dir:
                copy_folder(source_path, duplicate_path)
                printlog("Copied folder : " + file_name, YELLOW)
            else:
                try_copy(source_path, duplicate_path)
                printlog("Copied file : " + file_name, YELLOW)

        # Move
        if is_dir:
            copydelete_folder(source_path, destination_path)
            printlog("Moved folder: " + file_name, YELLOW)
        else:
            copydelete_file(source_path, destination_path)
            printlog("Moved file: " + file_name, YELLOW)

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
