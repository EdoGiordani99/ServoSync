import os
from scripts.utils import *

def get_file_paths(folder_path):
    file_paths = []
    
    # Get all files in the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    
    return file_paths

# Replace 'your_folder_path' with the path to the folder you want to scan
folder_path = 'projects'
a = []
if os.path.exists(folder_path):
    files_list = get_file_paths(folder_path)
    print("File Paths:")
    for file_path in files_list:
        a.append(file_path)
else:
    print(f"The folder '{folder_path}' does not exist.")

write_on_pickle(a, "cache/recent_projects.pkl")