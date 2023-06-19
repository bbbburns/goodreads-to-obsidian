# Author: Jason Burns
# Purpose: Take a Goodreads CSV and format each row as a separate Markdown file for use in Obsidian

''' 
 Steps
 Read in the CSV file to a data structure
 Read in a template (Template is easier for me than Jinja2 for now)
 Pull out the important pieces we need for each row / book
  Into some dictionary
  cleanup the data (ugh - so much cleanup)
  EVEN MORE CLEANUP
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

def return_sub_words(sub_title, my_sub_len):
  new_sub = ""
  sub_words = re.findall(r'\w+', sub_title)
  sub_words_len = len(sub_words)

  #print(f"sub words length {sub_words_len}")
  for count, word in enumerate(sub_words):
      #print(f"Count is {count} and word is {word}")
      if count < int(my_sub_len):
        new_sub += word
        #print(f"Adding word {count + 1} to make '{new_sub}'")
        if count < int(my_sub_len) - 1 and count < sub_words_len - 1:
          # Add spaces to all but the final word
          new_sub += " "
          #print(f"Adding space {count + 1} to make '{new_sub}'")
      elif count >= int(my_sub_len):
        #print(f"Count {count} must be higher than sub length {int(my_sub_len)}, so breaking")
        break
  return new_sub

def get_custom_sub(base_title, full_sub):
   # Take in the base title and full_sub and request custom_sub_len from user
   # return the desired sub_len
   print(f"Current File Name (Title - [Subtitle]): ({base_title} - [{full_sub}])")

   input_success = False

   while not input_success:
      custom_sub_len = input("Enter desired subtitle length: [0] (drop sub), [1-n] (1-n words), [a] all.\n")
      # validate the input and perhaps preview result.
      if custom_sub_len.isdigit() or custom_sub_len == "a":
         input_success = True
         print(f"Thanks for entering valid input {custom_sub_len}")
      else:
         print("Invalid input. Try again.")

   return custom_sub_len

def parse_title(full_title):
    # take in a full title string, which might include a subtitle separated by :
    # return the stripped down base title
    # return the short subtitle for use in the .md file title name
    # short subtitle length is 0 if no subtitle present
    # otherwise short subtitle length is set by global sub_len
    
    my_sub_len = "0"
    title_tuple = full_title.partition(":")

    #if we didn't find a subtitle, stop processing
    if not title_tuple[1]:
       #no subtitle - just return the base
       #print("No subtitle found. Continuing.")
       return full_title, ""
    
    #print("We found a subtitle and have to handle it.")

    # There must be a subtitle - so strip out the base title for alias
    base_title = title_tuple[0]

    # we're getting the full sub - might be useful later if sub_len is ALL
    full_sub = title_tuple[2].lstrip()

    # If the global sub_len is set to custom, get the action to take
    # otherwise take the global action
    if sub_len == "c":
       my_sub_len = get_custom_sub(base_title, full_sub)
    else:
       my_sub_len = sub_len

    # need to handle sub_len value parsing here
    if my_sub_len == "a":
       # just set the short sub to the full sub
       #print("We want all of the subtitle")
       short_sub = full_sub
    elif my_sub_len.isdigit() and int(my_sub_len) > 0:
       # We want a positive number of subtitle words
       #print(f"We want {my_sub_len} words of the subtitle")
       short_sub = return_sub_words(full_sub, my_sub_len)
    elif my_sub_len.isdigit() and int(my_sub_len) == 0:
       # We want to drop the subtitle text
       #print("We want to drop the subtitle")
       short_sub = ""

    return base_title, short_sub

def write_book_md(title, author, book_md):
    # handle special characters in title. Replace with "" 
    # following are invalid chars in obsidian files
    # []:\/^|# and windows <>?"*
    # : for subtitle should have been handled already, so ditch any new :
    book_file_name = title + " - " + author + ".md"

    invalid_name = re.search(r"[]\\\/\^\|#\[\?\*\<\>\":]", book_file_name)
    if invalid_name:
       print(f"Rewriting invalid {book_file_name} | {len(book_file_name)} | it has invalid characters")
       book_file_name = re.sub(r"[]\\\/\^\|#\[\?\*\<\>\":]", "", book_file_name)
       print(f"new non-invalid name is {book_file_name}")
       return
    
    print(f"Book file name is: {book_file_name}")
    book_path = Path(output_path, book_file_name)
    print("Book md file path: " + str(book_path))

    # before we write the file, let's check to make sure we don't overwrite something
    if book_path.is_file():
       print(f"Skipping duplicate {book_path} because file already exists.")
    elif dry_run == False:
       with open(book_path, "w") as book_file:
          book_file.writelines(book_md)

def main():
    global template_path 
    template_path = "book.md.Template"
    #csv_path = "example/goodreads_export_example.csv"
    global output_path 
    output_path = ""
    global sub_len 
    sub_len = "0"
    global dry_run
    dry_run = False
    global alias
    alias = False

    parser = argparse.ArgumentParser()
    parser.add_argument("csv",
                        help="Goodreads CSV export file to import")
    parser.add_argument("--template",
                        help="Book Markdown template file with $variables. Uses book.md.Template by default.")
    parser.add_argument("--out",
                        help="Output directory. Uses current dir as default.")
    parser.add_argument("--sub_len",
                        help="Subtitle length for file name. 0 = none (default). a = ALL subtitle words. 1+ = num words long. c = custom")
    parser.add_argument("--dry", action="store_true",
                        help="If passed, perform a dry run and skip the file write steps.")
    parser.add_argument("--alias", action="store_true",
                        help="Add the base title as frontmatter alias when subtitle exists.")
    args = parser.parse_args()

    csv_path = args.csv

    if args.template:
      print(f"template was specified: {args.template}")
      template_path = args.template

    if args.out:
      print(f"output was specified: {args.out}")
      output_path = args.out

    if args.sub_len:
       print(f"Subtitle length {args.sub_len} was passed.")
       sub_len = args.sub_len
       if sub_len.isdigit() and int(sub_len) >= 0:
          print(f"Sub length set to valid numeric value {sub_len}")
       elif sub_len == "a":
          print("Sub length set to a for ALL")
       elif sub_len == "c":
          print("We're going to prompt you for the length whenever a sub is found.")
       else:
          print(f"Invalid sub_len {sub_len}")
          # do I mean system exit here? How do I do that again?
          return 1

    if args.dry:
       print("Dry Run. Skipping write!")
       dry_run = True

    if args.alias:
       print("Alias set to true. Adding frontmatter alias if a subtitle exists.")
       alias = True

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
                print(f"Something went wrong with the column count: Got {len(row)}, expected 24. We should skip {row['Title']}.")
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
            #print(series_tuple)
            date_dict['Title'] = series_tuple[0]
            date_dict['Series'] = series_tuple[1]
            date_dict['SeriesNum'] = series_tuple[2]

            # TODO - convert <br/> to \n in the MyReview text
            review_text = date_dict['MyReview']
            if review_text and re.search(r"<br/>", review_text):
               print(f"The text matched <br/> \n {review_text}")
               fixed_text = re.sub(r"<br/>", "\n", review_text)
               print(f"The new fixed review is:\n {fixed_text}")
               date_dict['MyReview'] = fixed_text
            
            # handle creating an alias if the title has a subtitle and alias is true
            # Pass the full title to some function
            # get back: the base title, and the short subtitle
            # based on this - check if subtitle is present
            # pass the title and shortsubtitle (if present) as the file name

            full_title = date_dict['Title']
            base_title, short_sub = parse_title(full_title)

            # for the ALIAS - we want an alias if:
            # 1. The alias flag is true
            # 2. The full title is longer than the base title
            if alias and len(base_title) < len(full_title): 
               print(f"Alias is true and base_title is shorter, setting alias to {base_title}")
               date_dict['BaseTitle'] = base_title
            else:
               date_dict['BaseTitle'] = ""

            book_md = format_note(date_dict, template_string)

            # Write out the replaced text into a $Title - $Author.md file to path
            # use the subtitle if this book has one and we set it to something
            if short_sub:
               title = base_title + " - " + short_sub
            else:
               title = base_title

            author = date_dict['Author']
            write_book_md(title, author, book_md)
            print(f'We have written {count + 1} books.')

if __name__ == '__main__':
    main()
