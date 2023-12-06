import os
import shutil
import time
import re
import logging
import schedule
from datetime import datetime as date
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

MANDATORY_FILES = [
    'fichierrequis.xml',
    '*.ppt',
]

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s', filemode='a')
logger = logging.getLogger()


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


def copy_folder(folder_source_path: str, folder_destination_path: str) -> int:
    error_count = 0

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
                try_copy(file_source_path, file_destination_path)
                print(date.now().strftime("%H:%M:%S"), "|",
                      file_source_path, GREEN + "Copied!", EC)

        # Handle folder as recursively
        elif os.path.isdir(file_source_path):
            if not os.path.exists(file_destination_path):
                os.mkdir(file_destination_path)

            error_count += copy_folder(file_source_path, file_destination_path)

    return error_count


def is_file_match(entry_name: str) -> bool:
    reasons = []
    for exp in MANDATORY_FILES:
        regex = exp.replace('*', '.*')
        if re.fullmatch(regex, entry_name, re.IGNORECASE) is not None:
            reasons.append(exp)

    return True if len(reasons) > 0 else False


def have_all_mandatory_file(folder_path: str) -> bool:
    match_count = 0
    for entry in os.scandir(folder_path):
        if is_file_match(entry.name):
            match_count += 1

    return True if match_count == len(MANDATORY_FILES) else False


def move_files():
    file_list = os.listdir(SOURCE_FOLDER)
    if len(file_list) == 0:
        print("Nothing to move")
        return

    print("Processing start...")
    logger.info("Processing start")

    for file_name in file_list:
        source_path = os.path.join(SOURCE_FOLDER, file_name)
        destination_path = os.path.join(DESTINATION_FOLDER, file_name)
        error_path = os.path.join(ERROR_FOLDER, file_name)

        if os.path.isdir(source_path) and os.path.exists(destination_path):
            shutil.move(source_path, error_path)
            print(RED + "Folder already in destination: " + file_name + EC)
            logger.info("Folder already in destination: " + file_name)
            continue

        if os.path.isdir(source_path) and not have_all_mandatory_file(source_path):
            shutil.move(source_path, error_path)
            print(RED + "Folder with errors: " + file_name + EC)
            logger.info("Folder with errors: " + file_name)
            continue

        if DUPLICATE_FOLDER:
            duplicate_path = os.path.join(DUPLICATE_FOLDER, file_name)

            if os.path.isfile(source_path):
                try_copy(source_path, duplicate_path)
            elif os.path.isdir(source_path):
                if not os.path.exists(duplicate_path):
                    os.mkdir(duplicate_path)

                print(YELLOW + f"[{file_name}] Copy start :" + EC)
                copy_folder(source_path, duplicate_path)
                print(YELLOW + "Copied folder : " + file_name + EC)
                logger.info("Copied folder : " + file_name)

        typefile = 'File' if os.path.isfile(source_path) else 'Folder'
        shutil.move(source_path, destination_path)
        print(YELLOW + "Moved " + typefile + " : " + file_name + EC)
        logger.info("Moved " + typefile + " : " + file_name)

    print("Process Done.")
    logger.info("Process end")


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
