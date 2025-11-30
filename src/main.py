"""
main.py

Entry point to the Booking.com scraper for slovak hotel reviews.

Author: Igor Lacko
"""

from review_scraper import ReviewScraper
from review_parser import ReviewParser
from sys import argv

def init_parser() -> ReviewParser:
    """Initializes the review parser with default selectors. If any will be changed, 
    here is the place to do it.

    Returns:
        ReviewParser: The initialized review parser.
    """
    parser = ReviewParser()
    return parser

def init_scraper(urls: list[str], parser: ReviewParser) -> ReviewScraper:
    """Initializes the review scraper with default settings. If any will be changed,
    here is the place to do it.

    Args:
        urls (list[str]): List of URLs to scrape.
        parser (ReviewParser): The parser instance to use.

    Returns:
        ReviewScraper: The initialized review scraper.
    """
    scraper = ReviewScraper(urls, parser)
    return scraper

def help() -> None:
    """Prints help message for using the scraper."""
    print("Usage: python main.py <url1> <url2> ...")
    print("Example: python main.py https://www.booking.com/hotel/sk/example1 https://www.booking.com/hotel/sk/example2")

if __name__ == "__main__":
    if ("-h" in argv) or ("--help" in argv) or (len(argv) == 1):
        help()
        exit(0)

    urls = argv[1:]
    parser = init_parser()
    scraper = init_scraper(urls, parser)
    scraper.scrape_next_page()