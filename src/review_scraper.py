"""
review_scraper.py

Module simulating a web browser with playwright for scraping purposes.

Author: Igor Lacko
"""

from review_parser import ReviewParser
from playwright.sync_api import sync_playwright
from review_cleaner import ReviewCleaner
from url_filter import URLFilter
from shared import console
from utils import shorten_url


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
        self.base_list_url = kwargs.get("base_list_url", None)
        self.limit = int(kwargs.get("limit", 100))
        self.output_file = kwargs.get("output_file", None)
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

        # URL filter
        self.filter = URLFilter(
            dataframe_folder=kwargs.get("dataframe_folder", "csvs/")
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

        # And for link title selector
        self.link_title_selector = kwargs.get(
            "link_title_selector", 'a[data-testid="title-link"]'
        )

        # And language itself!
        self.language = self.__map_language(kwargs.get("language", "slovak"))

        # Initialize page
        self.page = self.context.new_page()

    def __call__(self):
        """Scrapes all URLs in the list."""
        if self.base_list_url is not None:
            if self.output_file is None:
                console.print(
                    "[bold red]Error: Output file must be specified when scraping URLs from a list.[/bold red]"
                )
                return

            self.__scrape_urls_from_list()
            return

        while self.urls:
            self.scrape_next_page()

        if self.statistics_mode in ("summary", "all"):
            self.exporter.compute_summary()

    def __scrape_urls_from_list(self):
        """Scrapes hotel URLs from a search result page."""
        if self.base_list_url is None:
            raise ValueError("Base list URL is not set.")
        elif self.limit <= 0:
            raise ValueError("Limit must be a positive integer.")

        with console.status("[bold blue]Loading list page...[/bold blue]") as status:
            self.page.goto(self.base_list_url, wait_until="networkidle")
            status.update("[bold blue]Page loaded. Handling cookies...[/bold blue]")
            self.__close_cookies_if_needed()
            status.update("[bold blue]Scraping hotel URLs...[/bold blue]")

            # Avoid duplicate URLs
            scraped_urls = set()

            # Wait for at least one link to be present
            self.page.wait_for_selector(
                self.link_title_selector, timeout=10000, state="attached"
            )

            while True:
                previous_count = len(scraped_urls)

                # Get all title links
                anchors = self.page.locator(self.link_title_selector).all()

                for anchor in anchors:
                    href = anchor.get_attribute("href")
                    link = shorten_url(href) if href is not None else None
                    if (
                        link is not None
                        and link not in scraped_urls
                        and self.filter.filter_one_url(link)
                    ):
                        scraped_urls.add(link)
                        if len(scraped_urls) >= self.limit:
                            break

                status.update(
                    f"[bold blue]Scraping hotel URLs... ({len(scraped_urls)} found)[/bold blue]"
                )

                if len(scraped_urls) >= self.limit:
                    break

                # Scroll down to the bottom to trigger fetching more hotels
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self.page.wait_for_timeout(2000)

                # Scraped all links, have to load more
                if len(scraped_urls) == previous_count:
                    load_more_button = self.page.locator(
                        'button:has(span:text("Load more results"))'
                    )
                    if load_more_button.count() > 0:
                        status.update("[bold blue]Loading more results ...[/bold blue]")
                        load_more_button.click()
                        self.page.wait_for_load_state("networkidle")
                        # I love random "just in case" timeouts
                        self.page.wait_for_timeout(2000)
                    else:
                        # If no button and no new links, we might be at the end
                        console.print(
                            "[bold yellow]No more results to load.[/bold yellow]"
                        )
                        break

            self.urls = list(scraped_urls)
            console.print(f"[bold green]Found {len(self.urls)} links.[/bold green]")

            if self.output_file is None:
                raise ValueError("Output file must be specified to save scraped URLs.")

            with open(self.output_file, "a") as f:
                for url in self.urls:
                    f.write(f"{url}\n")
            console.print(
                f"[bold green]Saved {len(self.urls)} URLs to {self.output_file}[/bold green]"
            )

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

    def __get_hotel_name(self):
        """Scrapes the hotel name from the page content or URL."""
        url = self.page.url
        # Between the last / and .html
        start = url.rfind("/") + 1
        end = url.rfind(".html")
        self.hotel_name = url[start:end].replace("-", " ").title()
        console.print(f"[bold blue]Hotel name detected: {self.hotel_name}[/bold blue]")

    def __is_disabled(self, selector: str) -> bool:
        """Checks if an element specified by the selector is disabled.

        Args:
            selector (str): The CSS/Other selector of the element to check.
        Returns:
            bool: True if the element is disabled, False otherwise.
        """
        element = self.page.query_selector(selector)
        if not element:
            return True
        return element.is_disabled()

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

        with console.status(f"[bold blue]Loading {url} ...[/bold blue]") as status:
            self.page.goto(url, wait_until="networkidle")
            status.update(f"[bold blue]Page loaded. Handling cookies...[/bold blue]")
            self.__close_cookies_if_needed()
            self.__get_hotel_name()
            status.update(
                f"[bold blue]Scraping reviews for hotel: {self.hotel_name} ...[/bold blue]"
            )
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

                status.update(
                    f"[bold blue]Scraping reviews for hotel: {self.hotel_name} ... ({len(scraped_reviews)} scraped)[/bold blue]"
                )

                self.__safe_click('button[aria-label="Next page"]')
                self.page.wait_for_load_state("networkidle")

            # Last page
            html = self.page.content()
            reviews = self.parser.parse_current(html)
            for review in reviews:
                scraped_reviews.append(review)

        console.print(
            f"[bold green]Successfully scraped {len(scraped_reviews)} reviews for {self.hotel_name}![/bold green]"
        )

        # Create dataframe
        self.exporter.create_dataframe(self.hotel_name, scraped_reviews)
