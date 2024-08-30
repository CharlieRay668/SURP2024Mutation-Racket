import json
import pandas as pd
import os


def parse_report(project):
    # open mutants.json
    with open('mutants.json') as f:
        data = json.load(f)["files"]
        try:
            project_data = data[project]
        except:
            print(f"Failed to grab project data for {project}")
            return False, None
        mutants = project_data["mutants"]
        processed_mutants = []
        for mutant in mutants:
            mutator_type = mutant["mutatorName"]
            result = mutant["status"]
            replacement = mutant["replacement"]
            mutant_source_file = project
            mutant_start_line = mutant["location"]["start"]["line"]
            mutant_start_col = mutant["location"]["start"]["column"]
            mutant_end_line = mutant["location"]["end"]["line"]
            mutant_end_col = mutant["location"]["end"]["column"]
            processed_mutants.append({
                "MutatorType": mutator_type,
                "Result": result,
                "MutantSourceFile": mutant_source_file,
                "Replacement": replacement,
                "MutantSourceLine": mutant_start_line,
                "MutantSourceColumn": mutant_start_col,
                "MutantDestinationLine": mutant_end_line,
                "MutantDestinationColumn": mutant_end_col,
            })
        df = pd.DataFrame(processed_mutants)
        return True, df
    
def alter_mutation_commands(project):
    script_path = "mutation_commands.sh"
    
    # Read the content of the script
    with open(script_path, 'r') as file:
        script_content = file.readlines()

    # Update the projectDir line
    for i, line in enumerate(script_content):
        if line.startswith('projectDir='):
            script_content[i] = f'projectDir="{project}"\n'
            break

    # Write the modified content back to the script
    with open(script_path, 'w') as file:
        file.writelines(script_content)


def check_if_already_processed(file):
    with open("macket_logs.txt") as f:
        lines = f.readlines()
        for line in lines:
            if file in line:
                return True

def get_racket_files():
    green_repos = pd.read_csv("green_projects.csv")
    desired_projects = green_repos["project"].tolist()
    file_count = 0
    rkt_files = []
    for root, dirs, files in os.walk("repos"):
        for directory in dirs:
            if directory in desired_projects:
                # print("Processing: " + directory)
                subdir_path = os.path.join(root, directory)
                for sub_root, sub_dirs, sub_files in os.walk(subdir_path):
                    # print("Root: " + sub_root)
                    for file in sub_files:
                        # print("File: " + file)
                        if file.endswith(".rkt"):
                            rkt_files.append(os.path.join(sub_root, file))
                            file_count += 1

    print(f"Total Racket files found: {file_count}")
    return rkt_files

def generate_mutants(project):
    result = os.system(f"generate-mutants {project} output.yml")
    return result

def run_mutants():
    result = os.system("run-mutants --run_tests_in_one_batch output.yml")
    return result

def mutate_file(file):
    alter_mutation_commands(file)
    with open("macket_logs.txt", "a") as f:
        f.write(file + "\n")

    generated = generate_mutants(file)
    if generated != 0:
        print(f"Failed to generate mutants for {file}")
        return 1
    
    ran = run_mutants()

    csv_name = file.replace("/", "-").replace(".rkt", ".csv")
    good, csv_file = parse_report(file)
    if good:
        csv_file.to_csv(f"macket_report/{csv_name}", index=False)
    print(f"Processed file: {file}")
    return 0


if __name__ == "__main__":
    rkt_files = get_racket_files()
    for i, file in enumerate(rkt_files):
        print(f"Mutating file: {file} {i}/{len(rkt_files)}")
        if not check_if_already_processed(file):
            print("Mutating file: " + file)
            mutate_file(file)
        else:
            print("File already processed: " + file)