import os
from gui import create_gui


def add_line_to_csv(file_path, line):
    with open(file_path, "a") as file:
        file.write(line + "\n")


def create_csv_file(name, folder, prefix="", postfix=""):
    file_path = os.path.join(folder, prefix + name + postfix)
    with open(file_path, "w") as file:
        file.write("")
    return file_path


tools = {
    "Create CSV File": {
        "description": "Creates a new empty CSV file.",
        "function": create_csv_file,
        "parameters": [
            {
                "name": {
                    "display_name": "File Name",
                    "type": "string",
                    "default": "",
                    "tooltip": "The name of the csv file to create.",
                }
            },
            {
                "out_folder": {
                    "display_name": "Out Folder",
                    "type": "folder_open",
                    "tooltip": "The path to folder to save the CSV file.",
                }
            },
            {
                "prefix": {
                    "display_name": "Prefix",
                    "type": "string",
                    "default": "",
                    "tooltip": "Prefix to add to the file name.",
                    "keyword": True,
                }
            },
            {
                "postfix": {
                    "display_name": "Postfix",
                    "type": "string",
                    "default": "",
                    "tooltip": "Postfix to add to the file name.",
                    "keyword": True,
                }
            },
        ],
    },
}

create_gui(tools)