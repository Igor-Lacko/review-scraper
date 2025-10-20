"""
scraper.py

Module simulating a web browser with playwright for scraping purposes.

Author: Igor Lacko
"""

from playwright.sync_api import sync_playwright


class Scraper:
    """Class simulating a web browser for scraping purposes."""

    def __init__(self, urls: list[str], **kwargs: str) -> None:
        """Class constructor.

        Args:
            urls (list[str]): List of URLs to scrape.
        kwargs: Additional keyword arguments for future extensions.
        """
        self.urls = urls
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)

        # Check for review selector
        self.review_selector = kwargs.get('review_selector', 'a[rel="reviews"]')

        # And for language!
        self.language = kwargs.get('language', 'slovak')

        # Initialize page
        self.page = self.browser.new_page()

    def __safe_click(self, selector: str) -> None:
        """Safely clicks on an element specified by the selector.

        Args:
            selector (str): The CSS/Other selector of the element to click.
        """
        if not hasattr(self, 'page'):
            raise RuntimeError("No page is currently open.")

        self.page.wait_for_selector(selector, timeout=5000)
        self.page.click(selector)

    def close(self) -> None:
        """Closes the browser and playwright instance."""
        self.browser.close()
        self.playwright.stop()

    def open_reviews(self) -> None:
        """Opens the reviews section on the current page."""
        if not hasattr(self, 'page'):
            raise RuntimeError("No page is currently open.")

        self.__safe_click(self.review_selector)


    def scrape_next(self) -> str | None:
        """Scrapes the next URL in the list.

        Returns:
            str | None: The HTML of the page or None if no URLs left.
        """
        if not self.urls:
            return None

        url = self.urls.pop(0)
        self.page.goto(url)
        html = self.page.content()
        return html
