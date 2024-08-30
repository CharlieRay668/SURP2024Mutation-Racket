import pandas as pd
import requests
from bs4 import BeautifulSoup

green_projects = pd.read_csv("green_projects.csv")["project"].tolist()
racket_packages = pd.read_csv("racket_packages.csv")

def get_stars(project):
    # grab the row in the racket_packages dataframe
    row = racket_packages.loc[racket_packages["name"] == project]
    url = row["source_link"].values[0]
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    stars = soup.find_all("a", class_="Link Link--muted")
    for star in stars:
        strong_tags = star.find_all("strong")
        for strong_tag in strong_tags:
            if "stars" in star.text:
                return strong_tag.text
data = []
for project in green_projects:
    stars = get_stars(project)
    if stars is not None:
        print(f"Project: {project} Stars: {stars}")
    else:
        print(f"Project: {project} Stars: None")
    data.append({"project": project, "stars": stars})

df = pd.DataFrame(data)
df.to_csv("stars.csv", index=False)
