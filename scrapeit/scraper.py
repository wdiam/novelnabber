import os
import requests
import re
from bs4 import BeautifulSoup
from utils.common import create_safe_filename, ensure_directory

class ParsedChapterWebpage:
    def __init__(self, url_str):
        self.url = url_str
        self.soup = None
        self.load_page()

    def load_page(self):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }

            response = requests.get(self.url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            self.soup = BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            raise ValueError(f"Failed to load the page: {self.url}") from e

    def get_novel_name(self):
        title_tag = self.soup.find('title')
        if title_tag:
            # Split using " - Read " and take the first part, then split by '#' and take the first part again
            novel_name = title_tag.text.split(' - Read ')[0].split('#')[0].strip()
            return novel_name
        return 'Unknown Novel Name'

    def get_chapter_number(self):
        title_tag = self.soup.find('title')
        if title_tag:
            # Find pattern "#Chapter " followed by one or more digits
            match = re.search(r'#Chapter (\d+)', title_tag.text)
            if match:
                return match.group(1)
        return 'Unknown Chapter Number'
    
    def get_chapter_title(self):
        title_tag = self.soup.find('title')
        if title_tag:
            # Define a regex pattern to capture text after "Chapter ddd" and before " - Read"
            pattern = r'Chapter \d+[:\-]?\s*(.*?)\s*- Read'
            match = re.search(pattern, title_tag.text)
            
            if match:
                # Clean the captured title by removing leading non-alphanumeric characters
                title = re.sub(r'^[^a-zA-Z0-9]+', '', match.group(1).strip())
                return title if title else 'No Title'
        return 'No Title'    

    def get_chapter_text(self):
        # Find the main container div by its id
        content_div = self.soup.find('div', id='chr-content')
        if content_div:
            # Find all paragraph tags within the content div, ignoring any nested divs initially
            paragraphs = content_div.find_all('p', recursive=False)  # Adjust based on actual content structure
            
            # Filter out any paragraphs within unwanted nested divs if necessary
            # Here, we gather text from <p> tags that are direct children of the content_div
            chapter_text = []
            for p in paragraphs:
                if p.parent == content_div:
                    chapter_text.append(str(p))
            
            # Concatenate all paragraphs into a single string with HTML tags preserved
            return ''.join(chapter_text)
        return 'No content found'

    def get_prev(self):
        # Find the 'prev_chap' link by its ID
        prev_link = self.soup.find('a', id='prev_chap')
        # Check if the href attribute is present and not empty
        if prev_link and prev_link.get('href', '').strip():
            return ParsedChapterWebpage(prev_link['href'])
        return None

    def get_next(self):
        # Find the 'next_chap' link by its ID
        next_link = self.soup.find('a', id='next_chap')
        # Check if the href attribute is present and not empty
        if next_link and next_link.get('href', '').strip():
            return ParsedChapterWebpage(next_link['href'])
        return None

    def save_chapter_as_epub_ready(self, dir):
        ensure_directory(dir)

        content = self.get_chapter_text()
        chapter_number = self.get_chapter_number()
        chapter_title = self.get_chapter_title()
        header = f"<h4>Chapter {chapter_number}: {chapter_title}</h4>\n\n" if chapter_title != 'None' else ""
        full_content = f"{header}{content}"
        
        safe_title = create_safe_filename(chapter_title if chapter_title != 'None' else 'Untitled')        
        filename = f"{int(chapter_number):07}-{safe_title if chapter_title != 'None' else 'Untitled'}.html"
        with open(f"{dir}/{filename}", 'w', encoding='utf-8') as file:
            file.write(full_content)

    def save_chapter_as_text(self, dir):
        ensure_directory(dir)

        content = self.get_chapter_text()
        chapter_number = self.get_chapter_number()
        chapter_title = self.get_chapter_title()
        header = f"Chapter {chapter_number}: {chapter_title}\n\n" if chapter_title != 'None' else ""
        full_content = f"{header}{content.replace('<p>', '').replace('</p>', '\n')}"

        safe_title = create_safe_filename(chapter_title if chapter_title != 'None' else 'Untitled')
        filename = f"{int(chapter_number):07}-{safe_title if chapter_title != 'None' else 'Untitled'}.txt"
        with open(f"{dir}/{filename}", 'w', encoding='utf-8') as file:
            file.write(full_content)


# Usage example:
# chapter_page = ParsedChapterWebpage("http://example.com/chapter1")
# chapter_page.save_chapter_as_epub_ready('/path/to/save/epub')
# chapter_page.save_chapter_as_text('/path/to/save/text')
