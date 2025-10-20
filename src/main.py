"""
main.py

Entry point to the Booking.com scraper for slovak hotel reviews.

Author: Igor Lacko
"""

from sys import argv
from models.scraper import Scraper

if __name__ == "__main__":
    print("This is the main module.")
    if len(argv) > 1:
        urls = argv[1:]
        scraper = Scraper(urls)
        for _ in urls:
            html = scraper.scrape_next()
            print(f"Scraped HTML length: {len(html) if html else 'No HTML'}")
            print(html)
        scraper.close()