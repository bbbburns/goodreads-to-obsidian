# Author: Jason Burns
# Purpose: Take a Goodreads CSV and format each row as a separate Markdown file for use in Obsidian

''' 
 Steps
 Read in the CSV file to a data structure
 Read in a template (Template is easier for me than Jinja2 for now)
 Pull out the important pieces we need for each row
  Into some dictionary
  cleanup the data (ugh - so much cleanup)
 Output each row as a new file using the desired structure
  Substite the data in the template with the book data
  write out the file (more cleanup needed again)
 Place the resulting files somewhere safe - user specified
   Consider placing them straight into your vault if you feel lucky
   Probably don't do this.
'''

import argparse
import csv
from string import Template
import datetime
import re
from pathlib import Path

def remove_key_space(spaced_dict):
    # Handle keys in the mapping to remove spaces
    # 'Exclusive Shelf': 'read', 'My Review': 'Sample Text'
    # do some fixing courtesy of https://stackoverflow.com/questions/35758566/remove-space-from-dictionary-keys#35758583
    unspaced_dict = {k.translate({32: None}): v for k, v in spaced_dict.items()}
    return unspaced_dict

def format_dates(slash_dict):
    format = '%Y/%m/%d'

    date_read = slash_dict['DateRead']
    date_added = slash_dict['DateAdded']

    #TODO - just two repeated statements - could be a function or loop through values
    # It seems like a dictionary translate or some other pythonic way exists to do this
    # but I don't know it right now.
    # ALSO - I could just replace slash with dash but using datetime seems fun
    if date_read:
      #print("Date read was present. Fixing it.")
      datetime_read = datetime.datetime.strptime(date_read, format)
      slash_dict['DateRead'] = datetime_read.date()
      #print(datetime_read.date())

    if date_added:
      #print("Date added was present. Fixing it.")
      datetime_added = datetime.datetime.strptime(date_added, format)
      slash_dict['DateAdded'] = datetime_added.date()
      #print(datetime_added.date())

    return slash_dict

def fix_isbn(isbn_dict):
    # Strip out any non-digit values from the ISBN numbers
    # I could validate the count or checksum, but assume goodreads does
    # TODO same problem as above - doing the same thing twice
    if isbn_dict['ISBN']:
      # print("ISBN 10 value found " + isbn_dict['ISBN'])
      # Join all the digit values. Ignore spaces, dashes, whatever
      isbn10 = ''.join(filter(str.isdigit, isbn_dict['ISBN']))
      # print("Digits in ISBN10 " + isbn10)
      isbn_dict['ISBN'] = isbn10

    if isbn_dict['ISBN13']:
      # print("ISBN 13 value found " + isbn_dict['ISBN13'])
      # Join all the digit values. Ignore spaces, dashes, whatever
      isbn13 = ''.join(filter(str.isdigit, isbn_dict['ISBN13']))
      # print("Digits in ISBN13 " + isbn13)
      isbn_dict['ISBN13'] = isbn13
    return isbn_dict

# Replace the text in template with Template safe_substitute
def format_note(book_dict, template_string):
    template = Template(template_string)
    book_md = template.safe_substitute(**book_dict)
    print("This is what your Markdown will look like")
    print(book_md)
    return book_md

def parse_series(title):
    # convert series title to vals
    # Book Title (Series Name, #1)
    # this might be harder than I thought: 
    # Guards! Guards! (Discworld, #8; City Watch, #1)
    # Auberon (The Expanse, #8.5)
    # Edgedancer (The Stormlight Archive #2.5)
    # Remembrance of Earth's Past: The Three-Body Trilogy (Remembrance of Earth's Past #1-3)
    # The System of the World (The Baroque Cycle, Vol. 3, Book 3)
    
    # Assume these are blank in case they don't get set later on
    series = ""
    series_num = ""

    # normal: Title (Name, #1)
    match_normal = re.search(r"(.*) \((.*),.*#(.*)\)", title)

    # space: Title (Name #1)
    match_space = re.search(r"(.*) \((.*) #(.*)\)", title)

    # vol: Title (Series, Vol. 1)
    match_vol = re.search(r"(.*) \((.*),.*Vol. (.*),", title)

    # comp:  Title (Name1, #1; Name 2, #2) - but take name1 only
    match_comp = re.search(r"(.*) \((.*),.*#(.*);", title)

    if match_comp:
      # Have to match this first, because it's a subset of normal
      #print(f"COMPLEX TITLE FOUND: {title}")
      title = match_comp.group(1)
      series = match_comp.group(2)
      series_num = match_comp.group(3)
    elif match_normal:
      # have to match this AFTER comp
      #print("This title is a normal series in book")
      title = match_normal.group(1)
      series = match_normal.group(2)
      series_num = match_normal.group(3)
    elif match_space:
      #print("This title is a spaced series")
      title = match_space.group(1)
      series = match_space.group(2)
      series_num = match_space.group(3)
    elif match_vol:
      #print("This title is a vol series")
      title = match_vol.group(1)
      series = match_vol.group(2)
      series_num = match_vol.group(3)
    #else:
      #print("I don't think this is a series")

    # Return the Title, Series, and Num
    # Series and num could be blank
    return title, series, series_num

def write_book_md(title, book_md, file_path):
    #TODO Need to handle special characters in title. Replace with - 
    # following are invalid chars in obsidian files
    # []:\/^|#
    # oh.. 30% of my book titles contain invalid characters.. mostly colons
    invalid_name = re.search(r"[]\\\/\^\|#\[:]", title)
    if invalid_name:
       print(f"{title} has invalid characters")
    book_file_name = title + ".md"
    print(f"Book file name is: {book_file_name}")
    book_path = Path(file_path, book_file_name)
    print("Book md file path: " + str(book_path))
    #with open(book_path, "w") as book_file:
      #book_file.writelines(book_md)

def main():
    template_path = "book.md.Template"
    #csv_path = "example/goodreads_export_example.csv"
    output_path = ""

    parser = argparse.ArgumentParser()
    parser.add_argument("csv",
                        help="Goodreads CSV export file to import")
    parser.add_argument("--template",
                        help="Book Markdown template file with $variables. Uses book.md.Template by default.")
    parser.add_argument("--out",
                        help="Output directory. Uses current dir as default.")
    args = parser.parse_args()

    csv_path = args.csv

    if args.template:
      print(f"template was specified: {args.template}")
      template_path = args.template

    if args.out:
      print(f"output was specified: {args.out}")
      output_path = args.out

    # read in the default or specified template
    with open (template_path, newline='') as template_file:
        template_string = template_file.read()
        #print(template_string)

    with open(csv_path, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for count, row in enumerate(reader):
            #check count of columns in this row just to be SURE. 24?
            # had one row of bad data from goodreads
            if len(row) != 24:
                print("Something went wrong. We should skip this book.")
                print("Error was in " + row['Title'])
                continue

            # Build a dictionary RIGHT HERE that doesn't have spaces and pass it
            unspaced_dict = remove_key_space(row)

            # handle the formatting of ISBN to mangle to digit only
            # ="0553213105" and ="9780553213102" instead of just numbers
            isbn_dict = fix_isbn(unspaced_dict)

            # handle the formatting of dates from 2020/02/27 to 2020-02-27
            date_dict = format_dates(isbn_dict)

            # convert series title to vals
            series_tuple = parse_series(date_dict['Title'])
            #print("Series Tuple Follows")
            print(series_tuple)
            date_dict['Title'] = series_tuple[0]
            date_dict['Series'] = series_tuple[1]
            date_dict['SeriesNum'] = series_tuple[2]

            book_md = format_note(date_dict, template_string)

            # Write out the replaced text into a $Title.md file to path
            title = date_dict['Title']
            write_book_md(title, book_md, output_path)
            print(f'We have written {count + 1} books.')

if __name__ == '__main__':
    main()
