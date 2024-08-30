import pandas as pd
import os
import time
import subprocess

# Read the CSV file
df = pd.read_csv('racket_packages.csv')

# Get the total number of rows
total_rows = len(df)

# Start the timer
start_time = time.time()
next_print = 1

# Clone the source code into the "repos" directory
for i, row in df.iterrows():
    name = row['name']
    source_link = row['source_link']
    
    # Use subprocess to suppress output
    subprocess.run(f'git clone {source_link} repos/{name}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Print time estimate after processing an increasing number of rows
    if i + 1 >= next_print:
        elapsed_time = time.time() - start_time
        remaining_rows = total_rows - (i + 1)
        estimated_total_time = (elapsed_time / (i + 1)) * total_rows
        estimated_remaining_time = estimated_total_time - elapsed_time
        print(f"Processed {i+1} rows. Estimated time remaining: {estimated_remaining_time:.2f} seconds.")
        next_print *= 2

# Print the total time taken
total_time = time.time() - start_time
print(f"All repositories cloned. Total time taken: {total_time:.2f} seconds.")
