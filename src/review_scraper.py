"""
review_scraper.py

Module simulating a web browser with playwright for scraping purposes.

Author: Igor Lacko
"""

from review_parser import ReviewParser
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from review_cleaner import ReviewCleaner


class ReviewScraper:
    """Class simulating a web browser for scraping purposes."""

    def __init__(self, urls: list[str], parser: ReviewParser, **kwargs: str) -> None:
        """Class constructor.

        Args:
            urls (list[str]): List of URLs to scrape.
            parser (ReviewParser): The parser instance to use.
        kwargs: Additional keyword arguments for future extensions.
        """
        self.urls = urls
        self.parser = parser
        self.playwright = sync_playwright().start()
        self.debug = kwargs.get("debug", False)
        self.statistics_mode = kwargs.get("statistics", "none")
        self.browser = self.playwright.chromium.launch(
            headless=not self.debug,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--single-process",
                "--disable-gpu",
            ],
        )

        # Make it behave as headful
        self.context = (
            self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                device_scale_factor=1,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US",
                extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
            )
            if not self.debug
            else self.browser.new_context()
        )

        # Review exporter
        self.exporter = ReviewCleaner(
            dataframe_folder=kwargs.get("dataframe_folder", "csvs/"),
            statistics=kwargs.get("statistics", "none"),
        )

        # Check for review selector
        self.review_selector = kwargs.get("review_selector", 'a[rel="reviews"]')

        # And for container selector
        self.container_selector = kwargs.get(
            "container_selector", 'div[data-testid="review-list-container"]'
        )

        # And for language selector
        self.language_selector = kwargs.get(
            "language_selector", 'select[name="languages"][data-testid="languages"]'
        )

        # And language itself!
        self.language = self.__map_language(kwargs.get("language", "slovak"))

        # Initialize page
        self.page = self.context.new_page()

    def __call__(self):
        """Scrapes all URLs in the list."""
        while self.urls:
            self.scrape_next_page()

        if self.statistics_mode in ("summary", "all"):
            self.exporter.compute_summary()

    def __map_language(self, language: str) -> str:
        """Maps a language name to its code used in the website.

        Args:
            language (str): The language name.

        Returns:
            str: The corresponding language code.
        """
        language_map = {
            "slovak": "sk",
            "english": "en",
            "german": "de",
            "french": "fr",
            "spanish": "es",
            "italian": "it",
        }

        if (lower := language.lower()) in language_map.values():
            return lower

        return language_map.get(lower, "sk")

    def __safe_click(self, selector: str) -> None:
        """Safely clicks on an element specified by the selector.

        Args:
            selector (str): The CSS/Other selector of the element to click.
        """
        if not hasattr(self, "page"):
            raise RuntimeError("No page is currently open.")

        self.page.wait_for_selector(selector, timeout=5000)
        self.page.click(selector)

    def __close_cookies_if_needed(self) -> None:
        """Closes the cookies banner if it is present."""
        cookies_selector = 'button[id="onetrust-reject-all-handler"]'
        if self.page.query_selector(
            cookies_selector
        ) is not None and not self.__is_disabled(cookies_selector):
            self.__safe_click(cookies_selector)
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(1000)
            print("Closed cookies banner.")

    def __get_hotel_name(self):
        """Scrapes the hotel name from the page URL."""
        url = self.page.url
        # Between the last / and .html
        start = url.rfind("/") + 1
        end = url.rfind(".html")
        self.hotel_name = url[start:end].replace("-", " ").title()

    @staticmethod
    def url_to_csv(url: str) -> str:
        """Converts a hotel URL to a CSV filename.
        Args:
            url (str): The hotel URL.
        Returns:
            str: The corresponding CSV filename.
        """
        start = url.rfind("/") + 1
        end = url.rfind(".html")
        hotel_name = url[start:end]
        return f"{hotel_name.lower().replace('-', '_')}.csv"

    def __is_disabled(self, selector: str) -> bool:
        """Checks if an element specified by the selector is disabled.

        Args:
            selector (str): The CSS/Other selector of the element to check.
        Returns:
            bool: True if the element is disabled, False otherwise.
        """
        locator = self.page.locator(selector)
        return locator.is_disabled()

    def close(self) -> None:
        """Closes the browser and playwright instance."""
        self.browser.close()
        self.playwright.stop()

    def __select_language(self) -> None:
        """Selects the desired language for reviews."""
        # Wait for the selector to be available
        self.page.wait_for_selector(
            self.language_selector, timeout=5000, state="attached"
        )
        self.page.select_option(self.language_selector, self.language)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def scrape_next_page(self) -> str | None:
        """Scrapes the next URL in the list.

        Returns:
            str | None: The HTML of the page or None if no URLs left.
        """
        if not self.urls:
            return None

        # Switch to the reviews
        url = self.urls.pop(0)
        print(f"Loading {url} ...")
        self.page.goto(url, wait_until="networkidle")
        print("Page loaded.")
        self.__close_cookies_if_needed()
        self.__get_hotel_name()
        print(f"Scraping reviews for hotel: {self.hotel_name} ...")
        self.__safe_click(self.review_selector)
        self.page.wait_for_load_state("networkidle")
        self.__select_language()

        scraped_reviews = []

        # Parse the current tab while the next buton
        while not self.__is_disabled('button[aria-label="Next page"]'):
            html = self.page.content()
            reviews = self.parser.parse_current(html)
            for review in reviews:
                scraped_reviews.append(review)

            self.__safe_click('button[aria-label="Next page"]')
            self.page.wait_for_load_state("networkidle")

        # Last page
        html = self.page.content()
        reviews = self.parser.parse_current(html)
        for review in reviews:
            scraped_reviews.append(review)

        # Create dataframe
        self.exporter.create_dataframe(self.hotel_name, scraped_reviews)
