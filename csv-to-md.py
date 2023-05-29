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

import csv
from string import Template

# handle the called row - replacing the text in template with Template safe_substitute
def format_note(book_dict, template_string):
    print("In format_note")
    print(book_dict)
    print(template_string)

    template = Template(template_string)

    # this is broken because the keys in the mapping have spaces
    # 'Exclusive Shelf': 'read', 'My Review': 'Sample Text'
    # Should consider removing spaces from keys like ExclusiveShelf
    # https://stackoverflow.com/questions/35758566/remove-space-from-dictionary-keys
    # or maybe someone knows how to make keys with spaces work in Templates
    book_md = template.safe_substitute(**book_dict)
    print("This is what your Markdown will look like")
    print(book_md)

# TODO Read in template
# Have a draft template. Need to make sure it matches with future Obsidian Book Search files.

template_path = "book.md.Template"
csv_path = "example/goodreads_export_example.csv"

with open (template_path, newline='') as template_file:
    template_string = template_file.read()
    print(template_string)

# Yeah - csv.DictReader is really what I'm after
# https://docs.python.org/3/library/csv.html

import csv
with open(csv_path, newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        print(row['Author'], row['Title'], row['My Rating'])
        # Now I'm looping through EVERY row
        # Is it better to write my .md file out from within this loop
        # or should I build a data structure up, then do the writing later?
        # I think it's better to write one file at a time. See progress.

        # I could build a dictionary RIGHT HERE that doesn't have spaces and pass it
        format_note(row, template_string)



# TODO write out the replaced text into a .md file
