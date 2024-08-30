import pandas as pd
import os

# Combine all CSv files in ./macket_report folder
path = './macket_report/'
files = [file for file in os.listdir(path) if file.endswith('.csv')]

all_data = pd.DataFrame()
all_data = pd.concat([pd.read_csv(path + file) for file in files])
all_data.to_csv("macket_mutations.csv", index=False)
