import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

url = "https://pkgd.racket-lang.org/pkgn/search?q=+&tags="
page = requests.get(url)

# Get all the rows of the table
soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find('table')
rows = table.find_all('tr')

count = 0
data = []
total_rows = len(rows)
start_time = time.time()
next_print = 1

for i, row in enumerate(rows):
    h2 = row.find('h2')
    if h2 is None:
        continue
    name = row.find('h2').text
    build = row.find('td', class_='build_green')
    if build is not None:
        build = build.text
    else:
        continue
    if build == 'succeeds':
        count += 1
        # Grab the href of the a tag
        link = h2.find('a')['href']
        # Go to the link and grab the info
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        primary_table = soup.find('table')
        rows = primary_table.find_all('tr')
        info_row = rows[9]
        nested_table = info_row.find('table')
        source_row = nested_table.find_all('tr')[1]
        # Source link is in second cell
        source_link = source_row.find_all('td')[1].text
        data.append([name, build, source_link])
        print(name, build, source_link)
    
    # Print time estimate after processing an increasing number of rows
    if count >= next_print:
        elapsed_time = time.time() - start_time
        remaining_rows = total_rows - i - 1
        estimated_total_time = (elapsed_time / (i + 1)) * total_rows
        estimated_remaining_time = estimated_total_time - elapsed_time
        print(f"Processed {i+1} rows. Estimated time remaining: {estimated_remaining_time:.2f} seconds.")
        next_print *= 2

# Print the total count of rows processed
print(f"Total count of rows processed: {count}")

# Save the data to a CSV file
df = pd.DataFrame(data, columns=['name', 'builds?', 'source_link'])
df.to_csv('racket_packages.csv', index=False)
