"""
main.py

Entry point to the Booking.com scraper for slovak hotel reviews.

Author: Igor Lacko
"""

import argparse
from shared import console
from review_scraper import ReviewScraper
from review_parser import ReviewParser
from review_cleaner import ReviewCleaner
from url_filter import URLFilter

parser = argparse.ArgumentParser(description="Booking.com Hotel Review Scraper")
parser.add_argument("urls", nargs="*", help="List of URLs to scrape")
parser.add_argument(
    "--from-txt",
    type=str,
    help="Path to a .txt file containing URLs (one per line) to scrape. Cannot be used with manual URLs. If the corresponding csv file exists (URL-based name), it will be skipped.",
)
parser.add_argument(
    "--urls-from-list",
    nargs=3,
    metavar=("URL", "LIMIT", "OUTPUT_FILE"),
    help="Scrape hotel URLs from a search result page and append them to a file. Does not scrape reviews, only the URLS to later be scraped with --from-txt.",
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
    console.print("[bold yellow]Usage:[/bold yellow] python main.py <url1> <url2> ...")
    console.print(
        "[bold yellow]Example:[/bold yellow] python main.py https://www.booking.com/hotel/sk/example1 https://www.booking.com/hotel/sk/example2"
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

    elif (
        args.statistics != "none"
        and not args.urls
        and not args.from_txt
        and not args.urls_from_list
    ):
        cleaner = ReviewCleaner(
            dataframe_folder=args.dataframe_folder, statistics=args.statistics
        )
        cleaner.show_stored_statistics()
        exit(0)

    # Enforce that --from-txt, --urls-from-list and manual URLs cannot be used together
    if sum([bool(args.from_txt), bool(args.urls), bool(args.urls_from_list)]) > 1:
        console.print(
            "[bold red]Error: You can only use one of manual URLs, --from-txt, or --urls-from-list.[/bold red]"
        )
        exit(1)

    # If --from-txt is used, read URLs from the file
    if args.from_txt:
        try:
            with open(args.from_txt, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
                # Filter out duplicate URLs
                url_filter = URLFilter(dataframe_folder=args.dataframe_folder)
                urls = url_filter.filter_existing_urls(urls)

                if not urls:
                    console.print(
                        "[bold green]No new URLs to scrape after filtering existing CSV files.[/bold green]"
                    )
                    exit(0)

        except Exception as e:
            console.print(
                f"[bold red]Error reading URLs from {args.from_txt}: {e}[/bold red]"
            )
            exit(1)
    elif args.urls_from_list:
        parser = init_parser()
        scraper = init_scraper(
            [],
            parser,
            base_list_url=args.urls_from_list[0],
            limit=int(args.urls_from_list[1]),
            output_file=args.urls_from_list[2],
            debug=args.debug,
            statistics=args.statistics,
            dataframe_folder=args.dataframe_folder,
        )
        scraper()
        exit(0)

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
