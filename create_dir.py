import os
import uuid

# Directory

# Parent Directory path
parent_dir = "D:\\Downloads\\source\\"

for x in range(2018, 2024):
    for y in range(1, 13):
        month = str(y) if y > 9 else "0" + str(y)
        directory = str(x) + "-" + str(month)
        path = os.path.join(parent_dir, directory)
        # os.mkdir(path)

for folder_name in os.listdir(parent_dir):
    path = os.path.join(parent_dir, folder_name)
    for y in range(1, 300):
        final = os.path.join(path, str(y))
        # os.mkdir(final)

# print(uuid.uuid4())

for folder_name in os.listdir(parent_dir):
    path = os.path.join(parent_dir, folder_name)

    for sub_folder_name in os.listdir(path):
        sub_path = os.path.join(path, sub_folder_name)
        new_sub_path = os.path.join(path, str(uuid.uuid4()))
        print(sub_path, new_sub_path)
        os.rename(sub_path, new_sub_path)
