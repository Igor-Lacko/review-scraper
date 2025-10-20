"""
scraper.py

Module simulating a web browser with playwright for scraping purposes.

Author: Igor Lacko
"""

from playwright.sync_api import sync_playwright


class Scraper:
    """Class simulating a web browser for scraping purposes."""

    def __init__(self, urls: list[str]) -> None:
        """Class constructor.

        Args:
            urls (list[str]): List of URLs to scrape.
        """
        self.urls = urls
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)

    def close(self) -> None:
        """Closes the browser and playwright instance."""
        self.browser.close()
        self.playwright.stop()

    def scrape_next(self) -> str | None:
        """Scrapes the next URL in the list.

        Returns:
            str | None: The HTML of the page or None if no URLs left.
        """
        if not self.urls:
            return None

        url = self.urls.pop(0)
        page = self.browser.new_page()
        page.goto(url)
        html = page.content()
        page.close()
        return html
