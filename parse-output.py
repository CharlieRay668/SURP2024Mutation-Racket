import json
import re
import sys

def process_mutation_output(file_path, test_file):
    with open(file_path, 'r') as file:
        content = file.read()

    # Regular expressions to match lines in the output file
    num_mutant_pattern = re.compile(r'/#:NUM MUTANT: (\d+):#/')
    mutator_pattern = re.compile(r'/#:MUTANT USED: (.+?):#/')
    result_pattern = re.compile(r'MUTANT_RESULT: (survived|killed|not_covered)')
    mutant_source_file_pattern = re.compile(r'/#:MUTANT SOURCE FILE: (.+?):#/')
    mutant_line_pattern = re.compile(r'/#:MUTANT SOURCE LINE: (\d+):#/')
    mutant_col_pattern = re.compile(r'/#:MUTANT SOURCE COLUMN: (\d+):#/')
    mutant_source_pattern = re.compile(r'"/#:MUTANT SOURCE: (.+?):#/"')
    mutant_destination_pattern = re.compile(r'"/#:MUTANT DESTINATION: (.+?):#/"')
    score_pattern = re.compile(r'Mutation score: (\d+\.\d+)')

    # Split the content by the custom delimiter
    entries = content.split('//##::##//')
    
    mutation_results = []
    mutation_score = None
    print(len(entries))
    for entry in entries:
        num_mutant_match = num_mutant_pattern.search(entry)
        mutator_match = mutator_pattern.search(entry)
        result_match = result_pattern.search(entry)
        mutant_source_file_match = mutant_source_file_pattern.search(entry)
        mutant_line_match = mutant_line_pattern.search(entry)
        mutant_col_match = mutant_col_pattern.search(entry)
        mutant_source_match = mutant_source_pattern.search(entry)
        mutant_destination_match = mutant_destination_pattern.search(entry)
        score_match = score_pattern.search(entry)
        # print(entry)
        # print(num_mutant_match, "num")
        # print(mutator_match, "mutator")
        # print(result_match, "result")
        # print(mutant_source_match, "source")
        # print(mutant_destination_match, "destination")
        # print(num_mutant_match and mutator_match and result_match and mutant_source_match and mutant_destination_match, "all")

        if num_mutant_match and mutator_match and result_match and mutant_source_file_match and mutant_source_match and mutant_destination_match and mutant_line_match and mutant_col_match:
            mutation_results.append({
                "NumMutant": int(num_mutant_match.group(1)),
                "MutatorType": mutator_match.group(1),
                "Result": result_match.group(1),
                "MutantSourceFile": mutant_source_file_match.group(1),
                "MutantSource": mutant_source_match.group(1),
                "MutantDestination": mutant_destination_match.group(1),
                "MutantSourceLine": int(mutant_line_match.group(1)),
                "MutantSourceColumn": int(mutant_col_match.group(1))
            })
        if score_match:
            mutation_score = float(score_match.group(1))

    # Prepare the final JSON structure
    json_data = {
        "MutationResults": mutation_results,
        "MutationScore": mutation_score,
        "TestFile": test_file
    }

    return json_data

def write_to_json(data, output_file):
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    # Read command line arguments
    command_line_args = sys.argv
    if len(command_line_args) != 4:
        print("Usage: python parse-output.py <tested-file> <output-file> <racket-output-file>")
        sys.exit(1)
    else:
        test_file = command_line_args[1]
        output_file_path = command_line_args[2]
        racket_output_file = command_line_args[3]

    input_file_path = racket_output_file  # Path to the output file
    
    mutation_data = process_mutation_output(input_file_path, test_file)
    write_to_json(mutation_data, output_file_path)

    print(f"Mutation results have been written to {output_file_path}")
