import pandas as pd
from bs4 import BeautifulSoup
import sys

def parsed_covered_lines(file_coverage_path):
    with open(file_coverage_path, "r") as file:
        soup = BeautifulSoup(file, "html.parser")
        # return an array with all the covered lines
        covered_lines = []
        for line in soup.find_all("div", class_="line"):
            try:
                if "covered" in line.span["class"]:
                    covered_lines.append(int(line["id"]))
            except:
                pass
        return covered_lines
    
if __name__ == "__main__":
    # read path from command line
    file_coverage_path = sys.argv[1]
    output_csv_path = sys.argv[2]
    print("Parsing covered lines from: " + file_coverage_path)
    print("Outputting to: " + output_csv_path)
    covered_lines = parsed_covered_lines(file_coverage_path)
    covered_lines_df = pd.DataFrame(covered_lines, columns=["Line"])
    covered_lines_df.to_csv(output_csv_path, index=False)
    print("Done")
