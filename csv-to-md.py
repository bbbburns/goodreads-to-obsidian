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
import datetime

def remove_key_space(spaced_dict):
    # print("We got in this spaced dict")
    # print(spaced_dict)
    # do some fixing courtesy of https://stackoverflow.com/questions/35758566/remove-space-from-dictionary-keys#35758583
    unspaced_dict = {k.translate({32: None}): v for k, v in spaced_dict.items()}
    # print("Here is the dict after a fix")
    # print(unspaced_dict)
    return unspaced_dict

def format_dates(slash_dict):
    format = '%Y/%m/%d'

    date_read = slash_dict['DateRead']
    date_added = slash_dict['DateAdded']
    print('This is the date read string')
    print(date_read)
    print('This is the date added string')
    print(date_added)

    #TODO - just two repeated statements - could be a function or loop through values
    if date_read:
      print("Date read was present. Fixing it.")
      datetime_read = datetime.datetime.strptime(date_read, format)
      slash_dict['DateRead'] = datetime_read.date()
      #print(datetime_read.date())
    else:
      print("Date read was false - just leaving it alone")


    if date_added:
      print("Date added was present. Fixing it.")
      datetime_added = datetime.datetime.strptime(date_added, format)
      slash_dict['DateAdded'] = datetime_added.date()
      #print(datetime_added.date())
    else:
      print("Date added was false - just leaving it alone")
    
    return slash_dict

# handle the called row - replacing the text in template with Template safe_substitute
def format_note(book_dict, template_string):
    print("In format_note")
    print(book_dict)
    # print(template_string)

    template = Template(template_string)

    # this is broken because the keys in the mapping have spaces
    # 'Exclusive Shelf': 'read', 'My Review': 'Sample Text'
    # Should consider removing spaces from keys like ExclusiveShelf
    # https://stackoverflow.com/questions/35758566/remove-space-from-dictionary-keys
    # or maybe someone knows how to make keys with spaces work in Templates
    book_md = template.safe_substitute(**book_dict)
    print("This is what your Markdown will look like")
    print(book_md)
    return book_md


def main():
    template_path = "book.md.Template"
    csv_path = "example/goodreads_export_example.csv"

    # probably make a parse template function
    with open (template_path, newline='') as template_file:
        template_string = template_file.read()
        print(template_string)

    # Yeah - csv.DictReader is really what I'm after
    # https://docs.python.org/3/library/csv.html

    with open(csv_path, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            # print(row['Author'], row['Title'], row['My Rating'])
            # Now I'm looping through EVERY row, where each row is a book
            # Is it better to write my .md file out from within this loop
            # or should I build a data structure up, then do the writing later?
            # I think it's better to write one file at a time. See progress.

            # Build a dictionary RIGHT HERE that doesn't have spaces and pass it
            unspaced_dict = remove_key_space(row)

            # TODO handle the formatting of ISBN somehow
            
            # handle the formatting of dates
            date_dict = format_dates(unspaced_dict)

            book_md = format_note(date_dict, template_string)
            
            # TODO write out the replaced text into a .md file

if __name__ == '__main__':
    main()
