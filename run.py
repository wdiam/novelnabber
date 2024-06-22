from scrapeit.scraper import ParsedChapterWebpage
from epubit.epubber import create_epub_book
from utils.common import random_sleep, sanitize_no_specialchars
from glob import glob
import argparse

def parse_and_collate_chapters(initial_url, out_dir):
    parsed_first_chapter = False
    parsed_page = None


    while (not parsed_page is None) or (not parsed_first_chapter):
        parsed_first_chapter = True
        if parsed_page is None:
            # parsing first chapter if first time        
            parsed_page = ParsedChapterWebpage(initial_url)
        else:
            # otherwise, get the next chapter        
            parsed_page = parsed_page.get_next()

        # checking if we're at the end, in which case, break
        if parsed_page is None:
            break

        print("Parsed ChapNo: %s ChapTitle: %s" % (parsed_page.get_chapter_number(), parsed_page.get_chapter_title()))

        # saving it as both html and epub
        parsed_page.save_chapter_as_text(out_dir)
        parsed_page.save_chapter_as_epub_ready(out_dir)

        random_sleep(min_seconds=0.5, max_seconds=1.5)


def generate_epub(chapters,
                  out_dir,
                  identifier=None,
                  title=None,
                  language="en",
                  author=None):
    
    create_epub_book(chapters,
                     out_dir,
                     "blank" if identifier is None else identifier,
                     "blank" if title is None else title,
                     "en" if language is None else language,
                     "blank" if author is None else author)


def main(args):
    # parsing and collating chapters
    parse_and_collate_chapters(args.starting_url, args.out_dir_chapters)

    # generating EPUB
    html_files = sorted(glob(f"{args.out_dir_chapters}/*.html"))
    generate_epub(html_files, args.out_dir_chapters, title=args.title, author=args.author,
                  identifier=args.identifier, language=args.language)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an EPUB from a web-novel.")
    parser.add_argument("starting_url", type=str, help="URL of the first chapter of the novel.")
    parser.add_argument("out_dir_chapters", type=str, help="Directory to save the scraped chapters.")
    parser.add_argument("--title", type=str, default=None, help="Title of the book.")
    parser.add_argument("--author", type=str, default=None, help="Author of the book.")
    parser.add_argument("--identifier", type=str, default=None, help="Identifier of the book.")
    parser.add_argument("--language", type=str, default="en", help="Language of the book. Defaults to 'en'.")

    args = parser.parse_args()

    main(args)

    # python run.py "<link_to_first_chapter>" "./temp" --title "<title>" --author "<author>"
