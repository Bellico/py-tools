import os
import shutil
import time
import logging
import schedule
from tqdm import tqdm

SOURCE_FOLDER = r"D:\Downloads\source"
DUPLICATE_FOLDER = r"D:\Downloads\second"
DESTINATION_FOLDER = r"D:\Downloads\dest"
LOG_FILE = r"log.txt"
TIME = 5  # Démarrer le décompte de 1 minutes (60 secondes)

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


def move_files():
    file_list = os.listdir(SOURCE_FOLDER)
    if len(file_list) == 0:
        print("Nothing to move")
        return

    print("Processing in progress...")
    logger.info("Processing start")

    for file_name in file_list:
        source_path = os.path.join(SOURCE_FOLDER, file_name)
        duplicate_path = os.path.join(DUPLICATE_FOLDER, file_name)
        destination_path = os.path.join(DESTINATION_FOLDER, file_name)
        progress_copy(source_path, duplicate_path)
        shutil.move(source_path, destination_path)
        print("Moved file :", file_name)
        logger.info("Moved file : " + file_name)

    print("Process Done.")
    logger.info("Processing end")


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
