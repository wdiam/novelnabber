import os
from ebooklib import epub
from lxml import etree, html
from bs4 import BeautifulSoup
from utils.common import sanitize_no_specialchars

# Function to remove parent <p> tags containing nested <p> tags
def remove_nested_p_tags(html_content):
    document_root = html.fromstring(html_content)
    p_elements = document_root.xpath('//p')
    for p in p_elements:
        if p.xpath('.//p'):
            p.getparent().remove(p)
    return etree.tostring(document_root, pretty_print=True, method="html", encoding="unicode")


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

            # Remove nested <p> tags
            html_content = remove_nested_p_tags(html_content)                

            # Parse HTML and convert to XHTML using lxml
            document_root = html.fromstring(html_content)
            etree.strip_elements(document_root, 'script', 'view', 'check', 'svg') # Remove sketchy tags
            xhtml_content = etree.tostring(document_root, pretty_print=True, method="xml", encoding="unicode")
            
            # Find title for the chapter
            title_element = document_root.xpath('//h4')[0] if document_root.xpath('//h4') else None
            chapter_title = title_element.text if title_element is not None else 'No Title'

            chapter = epub.EpubHtml(title=chapter_title, file_name=os.path.basename(file_path), lang='en')
            chapter.content = xhtml_content  # Use the XHTML content
            chapter.media_type = 'application/xhtml+xml'  # Set correct media type
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
