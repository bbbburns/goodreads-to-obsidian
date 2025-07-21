# Author: Jason Burns
# Purpose: Flatten nested YAML frontmatter (Obsidian Properties)
 
"""
Given a folder of markdown files with YAML frontmatter in this format:
---
series:
   series_name: "Name Value"
   series_num: 1
---

Modify the folder of files in place so the frontmatter is flattened to:

---
series_name: "Name Value 1"
series_num: 1
---
 
Retain series_name and series_num values.

BIG WARNING!!

This will modify all of your markdown files in the folder.
Please make sure all the book files are in a single folder, with no other files in that folder.

This will rewrite all of the frontmatter in every book note with the python-frontmatter module.

Any string values will have their quotes removed.
Any single-line lists in [] will be converted to multi-line with -
Any empty values will be written as null.

"""

import os
import frontmatter

def load_markdown_file(file_path):
    """Load a markdown file and return its frontmatter and content."""
    print(f'Working on file {file_path}')
    if (frontmatter.check(file_path)):
        post = frontmatter.load(file_path)
        print('Grabbing Metadata')
        print(post.metadata)
    else:
        print(f'Skipping. No frontmatter in {file_path}.')
        post = False
    return post

def flatten_series(post):
    """Flatten the series structure in the frontmatter."""
    if 'series' in post:
        series = post['series']
        post['series_name'] = series.get('series_name')
        post['series_num'] = series.get('series_num')
        del post['series']  # Remove the original series key

def save_markdown_file(file_path, post):
    """Save the modified frontmatter back to the markdown file."""
    with open(file_path, 'wb') as f:
        frontmatter.dump(post, f, sort_keys=False)

def process_markdown_files(directory):
    """Process all markdown files in the specified directory."""
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            file_path = os.path.join(directory, filename)
            post = load_markdown_file(file_path)
            if (post):
                print(f'Post before flattening is:')
                print(frontmatter.dumps(post, sort_keys=False))
                flatten_series(post)
                print(f'Post after flattening is:')
                print(frontmatter.dumps(post, sort_keys=False))
                save_markdown_file(file_path, post)

if __name__ == "__main__":
    # Specify the directory containing markdown files
    directory_path = input("Enter the directory path containing markdown files: ")
    process_markdown_files(directory_path)