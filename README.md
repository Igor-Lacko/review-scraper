# Booking.com review scraper

Scraper of Slovak reviews for hotels taken from Booking.com for my bachelor's thesis. Scrapes Slovak reviews from Booking.com from a base list url, filtering out hotels that have already been scraped (from a text file). Uses Playwright for scraping and BeautifulSoup4 for HTML parsing. The structure of this repository is:

```
.
├── pyproject.toml                          # TOML file with dependencies
├── README.md                               # This README
├── src                                     # Source code
│   ├── main.py                                 # - Scraper entry point
│   ├── models                                  # - Dataclasses representing one review and statistics
│   │   ├── hotel.py
│   │   └── statistics.py
│   ├── review_cleaner.py                       # - Base cleaning of data, also builds statistics and dataframes
│   ├── review_parser.py                        # - Beautifulsoup HTML review parser
│   ├── review_scraper.py                       # - Playwright scraper
│   ├── shared.py                               # - Rich console
│   ├── url_filter.py                           # - Filters already scraped URL
│   └── utils.py                                # - Other utilities (url shorten, convert name to save csv)
└── uv.lock                                 # uv lock file
```

## Disclaimer

Scraping Booking.com is not legal without their permission. Use this at your own risk.
