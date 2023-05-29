# Author: Jason Burns
# Purpose: Take a Goodreads CSV and format each row as a separate Markdown file for use in Obsidian
# Probably should make the template extensible at some point later.

''' 
 Steps
 Read in the CSV file to a data structure
 Pull out the important pieces we need for each row
 Output each row as a new file using the desired structure
 Place the resulting files somewhere safe - make user copy them?
   Consider placing them straight into a vault folder?
'''

# import pandas as pd

# Turns out vscode and environments are hard for my brain
# no idea why the above pandas import gives me a Pylance error - but the code runs
# disabled this print which proved that pandas was imported
# print(pd.__version__)

csv_rel_path = "example/goodreads_export_example.csv"

# data = pd.read_csv( csv_rel_path, sep=',', engine='python', encoding="utf-8").fillna('')

# books = data.values.tolist()

# print(books)

# The original author created a list, then looped through getting the index by number
# That seems less than ideal when you know the data structure has named columns
# maybe I should ditch pandas and just use the python CSV reader
# I remember this being better.


# Yeah - csv.DictReader is really what I'm after
# https://docs.python.org/3/library/csv.html

import csv
with open(csv_rel_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row['Author'], row['Title'], row['My Rating'])
        # Now I'm looping through EVERY row
        # Is it better to write my .md file out from within this loop
        # or should I build a data structure up, then do the writing later?