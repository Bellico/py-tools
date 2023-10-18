import os
import shutil
import logging
import time
from datetime import datetime as date
from tqdm import tqdm
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
EC = '\033[0m'
BLUE = '\033[34m'
DARK = '\033[40m'
BG = '\033[35m'

# Paths
SOURCE_FOLDER = r"D:\\Downloads\\source\\"
DESTINATION_FOLDER = r"D:\Downloads\target\\"
LOG_FILE = r"log.txt"
DIRECTORIES_FILE = r"directories.txt"
# Options
RETRY_DELAY = [5, 10, 15, 30, 60]
GLOBAL_RETRY_COUNT = 5
WITH_DELETE = False
SEARCH_ONLY = True
# Scope in Ko
MIN_SIZE = 0.001
MAX_SIZE = 1_000_000

# Configure logging
LOG_FILE = r"log.txt"
logging.basicConfig(filename=LOG_FILE, format='%(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()

# Check if the directories file exist
if not os.path.exists(DIRECTORIES_FILE):
    print(RED + DIRECTORIES_FILE, "is not found. Please verify path or create it", EC)
    exit(0)

# Check if the directories file is not empty
if os.stat(DIRECTORIES_FILE).st_size == 0:
    print(DIRECTORIES_FILE, "is empty, no file to process")
    exit(0)

# Check if the source folder exist
if not os.path.exists(SOURCE_FOLDER):
    print(RED + SOURCE_FOLDER, "source folder not found", EC)
    exit(0)

# Check if the destination folder exist
if not os.path.exists(DESTINATION_FOLDER):
    print(RED + DESTINATION_FOLDER, "destination folder not found", EC)
    exit(0)


# Function to check the file size scope
def is_file_in_scope(file_path: str):
    size = os.path.getsize(file_path)
    return True if MIN_SIZE <= size / 1024 <= MAX_SIZE else False


# Function to count recursively files in a folder
def count_folder_files(folder_path: str) -> int:
    count = 0
    for path in os.listdir(folder_path):
        file_source_path = os.path.join(folder_path, path)
        if os.path.isfile(file_source_path):
            # Check the file size scope to count it
            if is_file_in_scope(file_source_path):
                count += 1
        elif os.path.isdir(file_source_path):
            count = count + count_folder_files(file_source_path)

    return count


# Function to copy file with progress bar
def progress_copy(file_source_path: str, file_destination_path: str):
    size = os.path.getsize(file_source_path)
    basename = os.path.basename(file_source_path)

    # Keep shutil copy method for small files
    if size < 4096:  # 4ko
        shutil.copy2(file_source_path, file_destination_path)
    else:
        with open(file_source_path, 'rb') as source, open(file_destination_path, 'ab') as target:
            with tqdm(ncols=150, total=size, unit='B', unit_scale=True, unit_divisor=1024, leave=False) as pbar:
                pbar.set_description(basename, refresh=True)
                while True:
                    buf = source.read(4096)  # 4ko
                    if len(buf) == 0:
                        print(end="\r")
                        break
                    target.write(buf)
                    pbar.update(len(buf))

        # Keep metadata
        shutil.copystat(file_source_path, file_destination_path)


# Function to copy file with error handling and retry
def try_copy(file_source_path: str, file_destination_path: str, retry_count=0) -> int:
    try:
        progress_copy(file_source_path, file_destination_path)
        # shutil.copy2(file_source_path, file_destination_path)
        print(date.now().strftime("%H:%M:%S"), "|", file_source_path, GREEN + "Copied!", EC)
        return 0
    except Exception as inst:
        # Delete for clean retry
        if os.path.exists(file_destination_path):
            os.remove(file_destination_path)

        if retry_count == len(RETRY_DELAY):
            logger.error("ERROR during the copy for :" + file_destination_path + " => " + str(inst))
            print(RED + "Failed to copy", file_destination_path, EC)
            return 1
        else:
            print(YELLOW + "ERROR... new attempt of", file_source_path, "in", RETRY_DELAY[retry_count], "seconds", EC)
            time.sleep(RETRY_DELAY[retry_count])
            return try_copy(file_source_path, file_destination_path, retry_count + 1)


# Function to copy recursively an entire folder
def copy_folder(folder_source_path: str, folder_destination_path: str) -> int:
    error_count = 0

    for path in os.listdir(folder_source_path):
        file_source_path = os.path.join(folder_source_path, path)
        file_destination_path = os.path.join(folder_destination_path, path)

        # Handle file
        if os.path.isfile(file_source_path):
            # Check the valid scope
            if not is_file_in_scope(file_source_path):
                continue

            # If the file already exist but has wrong size an error must have occurred, remove to undo the copy
            if os.path.exists(file_destination_path) and os.path.getsize(file_destination_path) < os.path.getsize(file_source_path):
                os.remove(file_destination_path)

            # Check if the file does not already exist
            if not os.path.exists(file_destination_path):
                # Copy file in the destination with an equivalent path
                result = try_copy(file_source_path, file_destination_path)
                if result == 1:
                    error_count += 1

                # Remove the file if the copy was successful
                if WITH_DELETE and result == 0:
                    try:
                        os.remove(file_source_path)
                        print(file_source_path, YELLOW + "removed!", EC)
                    except:
                        print(RED + "Failed to remove", file_source_path, EC)

        # Handle folder as recursively
        elif os.path.isdir(file_source_path):
            if not os.path.exists(file_destination_path):
                os.mkdir(file_destination_path)

            error_count += copy_folder(file_source_path, file_destination_path)

    # Try deleting the folder if it is empty
    if WITH_DELETE:
        try:
            os.rmdir(folder_source_path)
        except:
            pass

    return error_count


# Function to loop on each directory and make the copy
# Return the error count
def copy_directories(matching_directories: list[str]) -> int:
    total_error_count = 0

    for directory_source_path in matching_directories:
        # Count files before copy
        files_count = count_folder_files(directory_source_path)
        directory = os.path.basename(directory_source_path)
        print(f"[{directory}] with {files_count} file(s) processing :")

        # Create the directory in the destination if not exist
        directory_destination_path = DESTINATION_FOLDER + directory
        if not os.path.exists(directory_destination_path):
            os.mkdir(directory_destination_path)

        # Copy the entire directory
        error_count = copy_folder(directory_source_path, directory_destination_path)
        success_count = files_count - error_count
        total_error_count += error_count
        print(BLUE + "Processing", success_count, "/", files_count, "Files done" + ("!" if success_count == files_count else RED + " with error(s)"), EC)

    return total_error_count


# Function to retrieve the list of desired directory names in the directories file
def read_directory_names():
    with open(DIRECTORIES_FILE) as f:
        names = [folder_name.strip() for folder_name in f.readlines()]
        f.close()

    return names


# Function to search in sources folder for the corresponding directories on the 2 first level
def find_directories_to_copy(directories_to_find):
    matching_directories = []
    level2_to_look = []

    # Scan level 1
    for folder in os.listdir(SOURCE_FOLDER):
        path_to_look = os.path.join(SOURCE_FOLDER, folder)
        if not os.path.isdir(path_to_look):
            continue

        if any(x.lower() in folder.lower() for x in directories_to_find):
            matching_directories.append(os.path.join(SOURCE_FOLDER, folder))
           # print(YELLOW + '\r' + "Searching directories", len(matching_directories), "/", len(directories_to_find), EC, end="")
            if len(matching_directories) == len(directories_to_find):
                return matching_directories
        else:
            level2_to_look.append(path_to_look)

        print('\r' + "Searching directories", len(matching_directories), "/", len(directories_to_find), path_to_look, end="")

    # Scan level 2
    for path in level2_to_look:
        for sub_folder in os.listdir(path):
            if any(x.lower() in sub_folder.lower() for x in directories_to_find):
                matching_directories.append(os.path.join(path, sub_folder))
                # print(YELLOW + '\r' + "Searching directories", len(matching_directories), "/", len(directories_to_find), EC, end="")
                if len(matching_directories) == len(directories_to_find):
                    return matching_directories

            print('\r' + "Searching directories", len(matching_directories), "/", len(directories_to_find), os.path.join(path, sub_folder), end="")

    return matching_directories


# Function to check and compare the matching directories to the desired directories
def check_matching_result(matching_directories, directories_to_find):
    # Check if there are directories found
    if len(matching_directories) == 0:
        print(YELLOW + "No matching directories found", EC)
        exit()

    # Check if there are any directories not found
    if len(matching_directories) < len(directories_to_find):
        for x in directories_to_find:
            if not any(x.lower() in element.lower() for element in matching_directories):
                print(YELLOW + f"\"{x}\" not found, it will be skipped", EC)

    [print(GREEN + date.now().strftime("%H:%M:%S"), "|", "Found", x, EC) for x in matching_directories]


# 1. Read the directory file
directories_to_find = read_directory_names()

# 2. Search in source folder
print(BLUE + "Please wait... Starting for", len(directories_to_find), "files", EC, end="")
start = time.perf_counter()
matching_directories = find_directories_to_copy(directories_to_find)
print(end="\r")

# 3. Check the result found
check_matching_result(matching_directories, directories_to_find)
print(RED, time.perf_counter() - start, EC)

if SEARCH_ONLY:
    logging.shutdown()
    os.remove(LOG_FILE)
    print(BLUE + "No processing file to do")
    exit(0)

# 4. Copy the matching directories
error_count = 999
global_retry = 1
while error_count > 0 and global_retry <= GLOBAL_RETRY_COUNT:
    print(BG + "Start of processing...try", global_retry, "at:", date.now().strftime("%d/%m/%Y %H:%M:%S"), EC)
    error_count = copy_directories(matching_directories)

    print((GREEN if error_count == 0 else RED) + f"{error_count} error(s)", EC)
    print(BG + "End of try", global_retry, "at:", date.now().strftime("%d/%m/%Y %H:%M:%S"))
    global_retry += 1

# 5. If no errors remove the log file
if error_count == 0:
    logging.shutdown()
    os.remove(LOG_FILE)
