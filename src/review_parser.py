"""
review_parser.py

Parses HTML content using BeautifulSoup4 to extract hotel reviews.

Author: Igor Lacko
"""

from bs4 import BeautifulSoup, Tag
from models.review import Review

class ReviewParser:
    """Class for parsing hotel reviews from HTML content."""

    def __init__(self, **kwargs: str) -> None:
        """Class constructor.

        Args:
            kwargs: Additional keyword arguments, such as selectors.
        """
        self.soup = None

        # Individual review card
        self.card_selector = kwargs.get('card_selector', 'div[data-testid="review-card"]')

        # Review itself inside the card
        self.review_selector = kwargs.get('review_selector', 'div[aria-label="Review"]')

        # Review title
        self.title_selector = kwargs.get('title_selector', 'div[data-testid="review-title"]')

        # Review rating
        self.rating_selector = kwargs.get('rating_selector', 'div[data-testid="review-score"]')

        # Positive content
        self.positive_selector = kwargs.get('positive_selector', 'div[data-testid="review-positive-text"]')

        # Negative content
        self.negative_selector = kwargs.get('negative_selector', 'div[data-testid="review-negative-text"]')


    def parse_current(self, html: str) -> list[Review]:
        """Parses the currently selected/scraped review tab

        Args:
            html (str): The page's HTML.

        Returns:
            list[Review]: Parsed list of review objects.
        """
        self.soup = BeautifulSoup(html, 'html.parser')
        cards = self.soup.select(self.card_selector)
        results : list[Review] = []

        for card in cards:
            if (review := self.__parse_one(card)) is not None:
                results.append(review)

        return results

    def __parse_one(self, card: Tag) -> Review | None:
        """Parses one review card.

        Args:
            card (Tag): The BeautifulSoup Tag representing the review card.

        Returns:
            Review: The parsed review object.
        """
        # Rating
        rating_tag = card.select_one(self.rating_selector)
        if rating_tag is None:
            return None
        
        rating_strings = rating_tag.stripped_strings
        rating_str = next(rating_strings, None)
        if rating_str is None:
            return None

        rating_str = rating_str.replace("Scored ", "").replace(",", ".")
        rating = float(rating_str)

        # Positive content
        positive_tag = card.select_one(self.positive_selector)
        content_good = positive_tag.get_text(strip=True) if positive_tag else None

        # Negative content
        negative_tag = card.select_one(self.negative_selector)
        content_bad = negative_tag.get_text(strip=True) if negative_tag else None

        return Review( 
            rating=rating,
            content_good=content_good,
            content_bad=content_bad
        )