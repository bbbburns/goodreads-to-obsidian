# goodreads-to-obsidian
Take a Goodreads CSV export and convert that into a series of markdown notes for Obsidian.

## Is it done?
This works for me. I think it's ready to use. You can find my [blog post about it for some more background](https://bbbburns.com/blog/2023/06/converting-from-goodreads-to-obsidian/).

## Who is this for?
For those who want to migrate all of their existing Goodreads book data to individual markdown files in Obsidian. Then you plan to stop adding new books to Goodreads.

## How do I do this?
1. Optionally, prepare your Vault with a book template See the code snippet below for `Obsidian Book Template`
2. Optionally, build a books dashboard with dataview. See the code snippet below for `Obsidian Library Dashboard`
3. Login to Goodreads.
4. Export your books to CSV under My Books (think of sample book format)
6. Run `csv-to-md.py` 
7. Take all of these .md files and copy them to your Obsidian vault. :tada:
8. Add new books with this other great plugin [Obsidian Book Search](https://github.com/anpigon/obsidian-book-search-plugin)

### Running the python file

I wrote this with python 3.10. You will have better results if you use a similar version.

Usage:

```bash
user@host$ python3 csv-to-md.py -h
usage: csv-to-md.py [-h] [--template TEMPLATE] [--out OUT] [--sub_len SUB_LEN] [--dry] [--alias] csv

positional arguments:
  csv                  Goodreads CSV export file to import

options:
  -h, --help           show this help message and exit
  --template TEMPLATE  Book Markdown template file with $variables. Uses book.md.Template by default.
  --out OUT            Output directory. Uses current dir as default.
  --sub_len SUB_LEN    Subtitle length for file name. 0 = none (default). a = ALL subtitle words. 1+ = num words long. c = custom
  --dry                If passed, perform a dry run and skip the file write steps.
  --alias              Add the base title as frontmatter alias when subtitle exists.
```

Here's an example of how I use this to do a dry run, looking at the output to make sure it's correct before writing a file:

```bash
python3 csv-to-md.py /home/user/Downloads/goodreads_library_export.csv --template book.md.Template --out /tmp/books --sub_len c --alias --dry
```

That allows me to take in the CSV export file from a Downloads folder, use the specified template that's in this repo, and place the files into /tmp/books.

The option for `--sub_len c` lets me take very long subtitles and decide which ones should be dropped from the output file names or included. You can also decide this with other values of sub_len.

The option to `--alias` populates the value of the frontmatter `aliases:` key with the short title name. This is great for Obsidian if you want the book to have the full title, but link to it by the short name.

The final option is `--dry` which turns off the file write operations and just dumps output to the console.

### Obsidian Book Template

This is a helpful template for your Obsidian if you are using Templater and want to merge what I have here with the Obsidian Book Search plugin. I copy this to my Templates directory as a file called BookTemplate.md. Then I setup Templater and the Obsidian Book Search plugin to use this template. NOTE: This template is DIFFERENT than the one the python script uses. This template here is for Obsidian.

```
---
tags: book, media
publish: false
title: "{{title}}"
aliases:
series_name: 
series_num: 
author: [{{author}}]
status: 
isbn: {{isbn10}}
isbn13: {{isbn13}}
category: [{{category}}]
rating:
read_count:
binding:
num_pages: {{totalPage}}
pub_date: {{publishDate}}
cover: {{coverURL}}
date_start:
date_end:
created: <% tp.file.creation_date() %>
modified:
---
# {{title}}

## Description

{{description}}

## Review
```

Note: I have changed this to flatten series_name and series_num to top-level keys. They're no longer nested under the now-deleted seres. If you've used a version of this prior to July 2025, you may have the old style nested property.

Old:

```
series:
  series_name:
  series_num:
```

New:

```
series_name:
series_num:
```

### Obsidian Library Dashboard

The dataview is where all of this comes together. Here's where you can see all of your shelves and the list of all your books. This is entirely inspired by the Obsidan Book Search plugin and I've modified it some. I copy this to my _dataview folder as a file called Library.md

````
# 📚 Library

## Currently Reading

```dataview
TABLE WITHOUT ID
	file.link as Book,
	date_start as Started
FROM  #book
WHERE 
	status = "currently-reading" 
	AND !contains(file.path, "Templates")
SORT date_start DESC
```

## To Read

```dataview
TABLE WITHOUT ID
	file.link as Book,
	date_add as Added
FROM  #book
WHERE 
	status = "to-read" 
	AND !contains(file.path, "Templates")
SORT date_add DESC
```

## All Books

```dataview
TABLE WITHOUT ID
	status as Status,
	"![|60](" + cover + ")" as Cover,
	link(file.link, title) as Title,
	author as Author,
	series.series_name + " " + series.series_num as Series
FROM #book
WHERE !contains(file.path, "Templates")
SORT status ASC, file.ctime DESC
```
````

Note: If you use nested properties for series, the All Books query would be as follows for series:

```
series.series_name + " " + series.series_num as Series
```

## Why would I want this?
If you're planning to do all future book reviews in a private Obsidian vault, but have a bunch of book `read` data that you want to bring with you.

## What happens to my data in Goodreads?
Nothing, unless you choose to take some action. This is just a simple data converter.

## What about new books that I read?
You could use another great plugin [Goodsidian](https://github.com/selfire1/goodsidian) to add new books directly to Obsidian. This script won't do that.

## What if I want to keep using Goodreads?
Then this probably is not for you. However, there are some solutions that do that! Like [Goodsidian](https://github.com/selfire1/goodsidian) - which takes updates from your feeds of active Goodreads use and puts those into Obsidian. That wasn't what I wanted!
