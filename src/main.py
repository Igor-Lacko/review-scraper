"""
main.py

Entry point to the Booking.com scraper for slovak hotel reviews.

Author: Igor Lacko
"""

import argparse
import os
from review_scraper import ReviewScraper
from review_parser import ReviewParser
from review_cleaner import ReviewCleaner

parser = argparse.ArgumentParser(description="Booking.com Hotel Review Scraper")
parser.add_argument("urls", nargs="*", help="List of URLs to scrape")
parser.add_argument(
    "--from-txt",
    type=str,
    help="Path to a .txt file containing URLs (one per line) to scrape. Cannot be used with manual URLs. If the corresponding csv file exists (URL-based name), it will be skipped.",
)
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
parser.add_argument(
    "-s",
    "--statistics",
    choices=["none", "for-each", "summary", "all"],
    default="none",
    help="Statistics mode: none, for-each, summary, all",
)
parser.add_argument(
    "-c", "--clean", type=str, help="Clean the given CSV file or folder"
)
parser.add_argument(
    "--clean-all",
    action="store_true",
    help="Clean all CSV files in the dataframe folder",
)
parser.add_argument(
    "--dataframe-folder",
    type=str,
    default="csvs/",
    help="Folder to store CSV dataframes",
)


def init_parser(**kwargs) -> ReviewParser:
    """Initializes the review parser with default selectors. If any will be changed,
    here is the place to do it.

    Args:
        kwargs: Additional keyword arguments for future extensions.

    Returns:
        ReviewParser: The initialized review parser.
    """
    parser = ReviewParser(**kwargs)
    return parser


def init_scraper(urls: list[str], parser: ReviewParser, **kwargs) -> ReviewScraper:
    """Initializes the review scraper with default settings. If any will be changed,
    here is the place to do it.

    Args:
        urls (list[str]): List of URLs to scrape.
        parser (ReviewParser): The parser instance to use.
        kwargs: Additional keyword arguments for future extensions.

    Returns:
        ReviewScraper: The initialized review scraper.
    """
    scraper = ReviewScraper(urls, parser, **kwargs)
    return scraper


def help() -> None:
    """Prints help message for using the scraper."""
    print("Usage: python main.py <url1> <url2> ...")
    print(
        "Example: python main.py https://www.booking.com/hotel/sk/example1 https://www.booking.com/hotel/sk/example2"
    )


if __name__ == "__main__":
    args = parser.parse_args()

    if args.clean or args.clean_all:
        cleaner = ReviewCleaner(dataframe_folder=args.dataframe_folder)
        if args.clean:
            cleaner.clean_one_csv(args.clean)
        if args.clean_all:
            cleaner.clean_folder()
        exit(0)

    elif args.statistics != "none" and not args.urls and not args.from_txt:
        cleaner = ReviewCleaner(
            dataframe_folder=args.dataframe_folder, statistics=args.statistics
        )
        cleaner.show_stored_statistics()
        exit(0)

    # Enforce that --from-txt and manual URLs cannot be used together
    if args.from_txt and args.urls:
        print("Error: --from-txt cannot be used together with manual URLs.")
        exit(1)

    # If --from-txt is used, read URLs from the file
    if args.from_txt:
        try:
            with open(args.from_txt, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
                # Filter out duplicate URLs
                existing_files = (
                    os.listdir(args.dataframe_folder)
                    if os.path.exists(args.dataframe_folder)
                    else []
                )
                files_to_add = [ReviewScraper.url_to_csv(url) for url in urls]
                # For loop to print out skipped files
                filtered_urls = []
                for url, file in zip(urls, files_to_add):
                    if file in existing_files:
                        print(f"Skipping URL (CSV already exists): {url} -> {file}")
                    else:
                        filtered_urls.append(url)
                urls = filtered_urls

                if not urls:
                    print("No new URLs to scrape after filtering existing CSV files.")
                    exit(0)

        except Exception as e:
            print(f"Error reading URLs from {args.from_txt}: {e}")
            exit(1)
    else:
        urls = args.urls

    if not urls:
        help()
        exit(0)

    kwargs = {
        "debug": args.debug,
        "statistics": args.statistics,
        "dataframe_folder": args.dataframe_folder,
    }

    parser = init_parser()
    scraper = init_scraper(urls, parser, **kwargs)
    scraper()
