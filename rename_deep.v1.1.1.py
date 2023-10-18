import os
import re
import sys

FOLDER = r"D:\Downloads\works\target\dossier"
NEW_NAME = "nouveau_nom"
EXTENSIONS = ['.xml', '.pca', '.pcp', '.pcr', '.vgi']

XML_INFO_FILE = '_jobinfo.xml'
TAGS = {
    'name': 'Ranaivo',
    'firstName': 'Rado',
    'machineLocation': 'Commercy',
    'machineType': 'Malgache',
    'machineSN': 'Masculin',
    'partSerialNumber': '030483904',
    'acquisitionWi': 'FR3FDF'
}

if not os.path.exists(FOLDER):
    print(FOLDER, "not found")
    sys.exit()

EXTENSIONS = [x.lower() for x in EXTENSIONS]
old_name = os.path.basename(FOLDER)
compiled = re.compile(re.escape(old_name), re.IGNORECASE)


def replace_lines_in_file(file_path: str):
    if not file_path.lower().endswith(tuple(EXTENSIONS)):
        return
    with open(file_path, 'r') as file:
        data = file.read()
        data = compiled.sub(NEW_NAME, data)
        if file_path.lower().endswith(XML_INFO_FILE):
            for key, value in TAGS.items():
                pattern = re.compile(rf'<{key}>(.*)</{key}>')
                data = pattern.sub(f'<{key}>{value}</{key}>', data)

    with open(file_path, 'w') as file:
        file.write(data)


def rename_deep_folder(folder_path: str) -> str:
    for file in os.listdir(folder_path):
        file_source_path = os.path.join(folder_path, file)

        if os.path.isfile(file_source_path):
            replace_lines_in_file(file_source_path)

            if not file.lower().startswith(old_name.lower()):
                continue

            new_file_name = compiled.sub(NEW_NAME, file)
            os.rename(file_source_path, os.path.join(
                folder_path, new_file_name))

        elif os.path.isdir(file_source_path):
            rename_deep_folder(file_source_path)

    [base_folder, old_folder_name] = os.path.split(folder_path)
    new_folder_name = compiled.sub(NEW_NAME, old_folder_name)
    new_folder_path = os.path.join(base_folder, new_folder_name)
    os.rename(folder_path, new_folder_path)

    return new_folder_path


newname = rename_deep_folder(FOLDER)
print(FOLDER, 'was deeply renamed to', newname)
