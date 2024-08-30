# Start python code
import os
import sys
import json
import time
import pandas as pd

def mutate_file(file_path, racket_output_file):
    # use raco to test and get the time taken
    start_time = time.time()
    os.system("raco test " + file_path)
    end_time = time.time()
    time_taken_to_test = end_time - start_time
    timout_time = time_taken_to_test * 3
    # round to nearest second
    timout_time = round(timout_time)
    # use python to parse the coverage
    coverage_out = "report/coverage.csv"
    html_path = file_path.replace(".rkt", ".html")
    html_path = "/".join(html_path.split("/")[:3]) + "/coverage/" + "/".join(html_path.split("/")[3:])
    print("Parsing coverage from: " + html_path)
    os.system("python3 parse_covered_lines.py " + html_path + " " + coverage_out)

    # use racket to mutate the file
    os.system("racket mutation-tester.rkt " + file_path + " " + str(timout_time) + " " + racket_output_file + " " + coverage_out)
    # parse the output
    # Grab the 3 last directories, and join by -, this feels poor.
    file_name_with_path = "-".join(file_path.split("/")[-3:]).split(".")[0] + ".json"
    os.system("python3 parse-output.py " + file_path  + " " + "report/" + file_name_with_path + " " + racket_output_file)

green_repos = pd.read_csv("green_projects.csv")
desired_projects = green_repos["project"].tolist()
file_count = 0
rkt_files = []

def check_if_already_processed(file_path):
    file_name_with_path = "-".join(file_path.split("/")[-3:]).split(".")[0] + ".json"
    return os.path.exists("report/" + file_name_with_path)

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
# print(rkt_files)
# files = ["./repos/generic-flonum/private/mpfr.rkt"]
# files = ["./repos/1d6/expander.rkt"]
for i, file in enumerate(rkt_files):
    print(f"Mutating file: {file} {i}/{file_count}")
    # mutate_file(file, "report/test.txt")
    if not check_if_already_processed(file):
        print("Mutating file: " + file)
        mutate_file(file, "report/test.txt")
    else:
        print("File already processed: " + file)
    