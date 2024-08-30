import pandas as pd
import os 
import matplotlib.pyplot as plt


overall_coverage = pd.read_csv('overall_coverage.csv')

# convert coverage row into real between 0 and 1

# scatter plot of coverage vs project size
# to get size open the repo with the title in the repos directory, look for all .rkt files and count the lines
for row in overall_coverage.iterrows():
    repo = row[1]['project']
    coverage = row[1]['coverage']
    size = 0
    for root, dirs, files in os.walk(f'repos/{repo}'):
        for file in files:
            if file.endswith('.rkt'):
                with open(f'{root}/{file}', 'r') as f:
                    size += len(f.readlines())
    # print(repo, coverage, size)
    overall_coverage.loc[overall_coverage['project'] == repo, 'size'] = size

# Color points based on size and coverage
# make points that are at least 1000 lines of code and have at least 90% coverage green
# make points that are at least 1000 lines of code and have less than 90% coverage yellow
# make points that are less than 1000 lines of code red
overall_coverage['color'] = 'red'
overall_coverage.loc[(overall_coverage['size'] >= 1000) & (overall_coverage['coverage'] >= 90), 'color'] = 'green'
overall_coverage.loc[(overall_coverage['size'] >= 1000) & (overall_coverage['coverage'] < 90), 'color'] = 'yellow'
# plot
# plt.scatter(overall_coverage['size'], overall_coverage['coverage'], c=overall_coverage['color'])
# plt.xlabel('Size')
# plt.ylabel('Coverage')
# plt.title('Coverage vs Size')
# plt.show()
# count total number of green projects
green_projects = overall_coverage[overall_coverage['color'] == 'green']
print(f'Total number of green projects: {len(green_projects)}')

# Create new plot but remove extreme size outliers
overall_coverage = overall_coverage[overall_coverage['size'] < 20000]
# plt.scatter(overall_coverage['size'], overall_coverage['coverage'], c=overall_coverage['color'])
# plt.xlabel('Size')
# plt.ylabel('Coverage')
# plt.title('Coverage vs Size')
# plt.show()

# count total number of green projects
green_projects = overall_coverage[overall_coverage['color'] == 'green']
print(f'Total number of green projects: {len(green_projects)}')

# save the dataframe to a csv
green_projects.to_csv('green_projects.csv', index=False)