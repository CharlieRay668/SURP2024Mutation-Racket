import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import linregress

df = pd.read_csv("mutation_report3.csv")
green_projects = pd.read_csv("green_projects.csv")["project"].tolist()
stars_df = pd.read_csv("stars.csv")

df["project"] = df["file"].apply(lambda x: x.split("/")[2])

data = []
unfinished_projects = []
for project in green_projects:
    subset = df[df["project"] == project]
    if len(subset) == 0:
        unfinished_projects.append(project)
        continue
    mutation_score = len(subset[subset["Result"] == "killed"]) / len(subset)
    stars = stars_df[stars_df["project"] == project]["stars"].values[0]
    data.append({"project": project, "mutation_score": mutation_score, "stars": stars})


df = pd.DataFrame(data)
df = df.sort_values("stars")
plt.scatter(df["stars"], df["mutation_score"])
# line of best fit
# m, b = np.polyfit(df["stars"], df["mutation_score"], 1)
# plt.plot(df["stars"], m*df["stars"] + b, color='red')
# show equation
# print(f"y = {m}x + {b}")
# calculate p value

# slope, intercept, r_value, p_value, std_err = linregress(df["stars"], df["mutation_score"])
# print(f"p value: {p_value}")
# print("unifinished projects:" + str(len(unfinished_projects)))
plt.xlabel("Stars")
plt.ylabel("Mutation Score")
plt.title("Mutation Score vs Stars")
plt.show()