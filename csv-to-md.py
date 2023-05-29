# Author: Jason Burns
# Purpose: Take a Goodreads CSV and format each row as a separate Markdown file for use in Obsidian
# Probably should make the template extensible at some point later.

''' 
 Steps
 Read in the CSV file to a data structure
 Read in a template (Template is easier than Jinja2 for my money)
 Pull out the important pieces we need for each row
  Into some dictionary
 Output each row as a new file using the desired structure
  Substite the data in the template with the book data
  write out the file
 Place the resulting files somewhere safe - make user copy them?
   Consider placing them straight into a vault folder?
'''

# TODO Read in template
# Have a draft template. Need to make sure it matches with future Obsidian Book Search files.

csv_rel_path = "example/goodreads_export_example.csv"

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
        # I think it's better to write one file at a time. See progress.
        # TODO Call file write operation with this row

# TODO handle the called row - replacing the text in template with Template safe_substitute

# TODO write out the replaced text into a .md file