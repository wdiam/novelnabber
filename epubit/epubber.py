import os
from ebooklib import epub
from bs4 import BeautifulSoup
from utils.common import sanitize_no_specialchars

def create_epub_book(file_paths, 
                     out_dir,
                     identifier,
                     title,
                     language,
                     author):
    # Initialize a new EPUB book
    book = epub.EpubBook()

    # Set the book title, author and other metadata
    book.set_identifier(identifier)
    book.set_title(title)
    book.set_language(language)
    book.add_author(author)

    # Prepare a list to collect chapters for the TOC
    all_chapters = []

    # Process each HTML file
    for file_path in file_paths:
        if os.path.isfile(file_path) and file_path.endswith('.html'):
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('h4')
            chapter_title = title_tag.text if title_tag else 'No Title'

            chapter = epub.EpubHtml(title=chapter_title, file_name=os.path.basename(file_path), lang='en')
            chapter.content = html_content
            book.add_item(chapter)
            all_chapters.append(chapter)

    # Setting the Table of Contents
    book.toc = tuple(epub.Link(ch.file_name, ch.title, ch.id) for ch in all_chapters)

    # Add navigation files and define spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + all_chapters

    # Define CSS (optional)
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/style.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Write the EPUB file
    clean_title = sanitize_no_specialchars(title)
    clean_author = sanitize_no_specialchars(author)
    output_filename = f"{out_dir}/{clean_title} - {clean_author}.epub"

    os.makedirs(out_dir, exist_ok=True)
    epub.write_epub(output_filename, book, {})


# Example usage:
# file_paths = [
#     'path/to/html_files/chapter1.html',
#     'path/to/html_files/chapter2.html',
#     'path/to/html_files/chapter3.html'
# ]
# create_epub_book(file_paths, 'out_dir')
