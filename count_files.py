import os
import pandas as pd

green_repos = pd.read_csv("green_projects.csv")
desired_projects = green_repos["project"].tolist()
file_count = 0
rkt_files = []

for root, dirs, files in os.walk("./repos"):
    for directory in dirs:
        if directory in desired_projects:
            print("Processing: " + directory)
            subdir_path = os.path.join(root, directory)
            for sub_root, sub_dirs, sub_files in os.walk(subdir_path):
                print("Root: " + sub_root)
                for file in sub_files:
                    print("File: " + file)
                    if file.endswith(".rkt"):
                        rkt_files.append(os.path.join(sub_root, file))
                        file_count += 1

print(f"Total Racket files found: {file_count}")

# count the number of .json files in the report directory
json_file_count = 0
for file in os.listdir('report'):
    if file.endswith('.json'):
        json_file_count += 1

print(f"Total JSON files found: {json_file_count}")