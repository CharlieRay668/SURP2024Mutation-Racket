import os
import subprocess
import time
from bs4 import BeautifulSoup
import pandas as pd

def extract_coverage(project_path):
    coverage_files = os.listdir(f'{project_path}/coverage')
    coverage_report = None
    for file in coverage_files:
        if file == 'index.html':
            with open(f'{project_path}/coverage/index.html', 'r') as f:
                coverage_report = f.read()
                soup = BeautifulSoup(coverage_report, 'html.parser')
                coverage_percentage = soup.find('div', class_='total-coverage').text
                file_data = []
                file_coverage = soup.find('table', class_='file-list')
                rows = file_coverage.find_all('tr')
                for row in rows[1:]:
                    file_name = row.find('td', class_='file-name').text
                    coverage_percentage = row.find('td', class_='coverage-percentage').text
                    file_data.append([file_name, coverage_percentage])
    return coverage_percentage, file_data

# Get the list of directories in the "repos" directory
repos = os.listdir('repos')

# Start the timer
start_time = time.time()
total_repos = len(repos)
next_print = 1

# For each directory, run the bash file and extract the coverage report
overall_data = []
for i, repo in enumerate(repos):
    # Start a timer for the subprocess
    repo_start_time = time.time()
    
    # Run the bash file with a timeout of 300 seconds (5 minutes)
    try:
        subprocess.run(f'bash setup_and_cover.sh repos/{repo}', shell=True, timeout=300)
    except subprocess.TimeoutExpired:
        print(f'Skipping {repo} due to timeout.')
        continue
    
    # Check if the repo took too long and skip it if necessary
    repo_elapsed_time = time.time() - repo_start_time
    if repo_elapsed_time > 300:
        print(f'Skipping {repo} due to taking too long ({repo_elapsed_time:.2f} seconds).')
        continue
    
    try: 
        coverage_percentage, file_data = extract_coverage(f'repos/{repo}')
        file_data_df = pd.DataFrame(file_data, columns=['file', 'coverage'])
        os.makedirs('coverage_data', exist_ok=True)
        file_data_df.to_csv(f'coverage_data/{repo}_report.csv', index=False)
        overall_data.append([repo, coverage_percentage])
    except Exception as e:
        print(f'Error processing {repo}: {e}')

    # Print time estimate after processing an increasing number of repos
    if i + 1 >= next_print:
        elapsed_time = time.time() - start_time
        remaining_repos = total_repos - (i + 1)
        estimated_total_time = (elapsed_time / (i + 1)) * total_repos
        estimated_remaining_time = estimated_total_time - elapsed_time
        print(f"Processed {i+1} repos. Estimated time remaining: {estimated_remaining_time:.2f} seconds.")
        next_print *= 2

# Save overall coverage data to CSV
overall_df = pd.DataFrame(overall_data, columns=['project', 'coverage'])
overall_df.to_csv('overall_coverage.csv', index=False)

# Print the total time taken
total_time = time.time() - start_time
print(f"All projects processed. Total time taken: {total_time:.2f} seconds.")
