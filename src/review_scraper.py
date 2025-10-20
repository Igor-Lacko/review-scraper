"""
review_scraper.py

Module simulating a web browser with playwright for scraping purposes.

Author: Igor Lacko
"""

from review_parser import ReviewParser
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


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
        self.browser = self.playwright.chromium.launch(headless=True)

        # Make it behave as headful
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )

        # Check for review selector
        self.review_selector = kwargs.get("review_selector", 'a[rel="reviews"]')

        # And for container selector
        self.container_selector = kwargs.get("container_selector", 'div[data-testid="review-list-container"]')

        # And for language selector
        self.language_selector = kwargs.get(
            "language_selector", 'select[name="languages"][data-testid="languages"]'
        )

        # And language itself!
        self.language = self.__map_language(kwargs.get("language", "slovak"))

        # Initialize page
        self.page = self.context.new_page()

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
        if not self.__is_disabled(cookies_selector):
            self.__safe_click(cookies_selector)

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

    def scrape_next_page(self) -> str | None:
        """Scrapes the next URL in the list.

        Returns:
            str | None: The HTML of the page or None if no URLs left.
        """
        if not self.urls:
            return None

        # Switch to the reviews
        url = self.urls.pop(0)
        self.page.goto(url, wait_until="networkidle")
        self.__close_cookies_if_needed()
        self.__safe_click(self.review_selector)
        self.page.wait_for_load_state("networkidle")
        self.__select_language()

        # Parse the current tab while the next buton
        soup = BeautifulSoup(self.page.inner_html(self.container_selector), 'html.parser')
        print(soup.prettify())
