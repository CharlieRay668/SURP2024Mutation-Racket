# Start python code
import os
import sys
import json
import time

def mutate_file(file_path, racket_output_file):
    # use raco to test and get the time taken
    start_time = time.time()
    os.system("raco test " + file_path)
    end_time = time.time()
    time_taken_to_test = end_time - start_time
    timout_time = time_taken_to_test * 3
    # round to nearest second
    timout_time = round(timout_time)
    # use racket to mutate the file
    os.system("racket mutation-tester-assignments.rkt " + file_path + " " + str(timout_time) + " " + racket_output_file)
    # parse the output
    # Grab the 3 last directories, and join by -
    file_name_with_path = "-".join(file_path.split("/")[-3:]).split(".")[0] + ".json"
    os.system("python3 parse-output.py " + file_path  + " " + "report/" + file_name_with_path + " " + racket_output_file)

file_count = 0
# get the total number of files
for root, dirs, files in os.walk("./2234-grading"):
    for directory in dirs:
        if "shuffled" in directory:
            file_count += 1

print("Total files: " + str(file_count))
# start_time = time.time()
# finished_files = 0
# # walkthough the directories
# one_file= False
# for root, dirs, files in os.walk("./2234-grading"):
#     for directory in dirs:
#         if "shuffled" in directory and not one_file:
#             # one_file = True
#             file_path = os.path.join(root, directory, "text.rkt")
#             mutate_file(file_path)
#             finished_files += 1
#             elasped_time = time.time() - start_time
#             estimated_remaining_time = (elasped_time / finished_files) * (file_count - finished_files)
#             print("Mutated file: " + file_path, "Finished files: " + str(finished_files) + "/" + str(file_count), "Estimated remaining time: " + str(estimated_remaining_time) + " seconds")
#         break
    

# the above but multithreaded
import threading
import queue

def worker():
    while True:
        item = q.get()
        if item is None:
            break
        target_file = item[0]
        output_file = item[1]
        mutate_file(target_file, output_file)
        q.task_done()


q = queue.Queue()
threads = []
for i in range(8):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

start_time = time.time()
finished_files = 0
for root, dirs, files in os.walk("./2234-grading"):
    for directory in dirs:
        if "shuffled" in directory:
            file_path = os.path.join(root, directory, "text.rkt")
            output_file = os.path.join("report", "-".join(file_path.split("/")[-3:]).split(".")[0] + ".txt")
            q.put([file_path, output_file])
            finished_files += 1
            elasped_time = time.time() - start_time
            estimated_remaining_time = (elasped_time / finished_files) * (file_count - finished_files)
            print("Mutated file: " + file_path, "Finished files: " + str(finished_files) + "/" + str(file_count), "Estimated remaining time: " + str(estimated_remaining_time) + " seconds")

q.join()
