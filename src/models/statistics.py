"""
statistics.py

Data model for storing statistics about hotel reviews.

Author: Igor Lacko
"""

from dataclasses import dataclass


@dataclass
class Statistics:
    """Class modelling statistics about hotel reviews."""

    name: str
    total_reviews: int
    mean_rating: float
    mean_length: float
    max_length: int
    min_length: int
    with_positive_empty: int
    with_negative_empty: int

    def __post_init__(self):
        """Post init call to compute some derived statistics."""
        self.with_both_sentiments = self.total_reviews - (
            self.with_positive_empty + self.with_negative_empty
        )

    def print_summary(self) -> None:
        """Prints a summary of the statistics."""
        print(f"---------- {self.name.upper()} STATISTICS ----------")
        print(f"Total reviews: {self.total_reviews}")
        print(f"Mean rating: {self.mean_rating:.2f}")
        print(f"Mean review length: {self.mean_length:.2f} characters")
        print(f"Max review length: {self.max_length} characters")
        print(f"Min review length: {self.min_length} characters")
        print(f"Reviews with positive sentiment empty: {self.with_positive_empty}")
        print(f"Reviews with negative sentiment empty: {self.with_negative_empty}")
        print(f"Reviews with both sentiments present: {self.with_both_sentiments}")
        print("---------------------------------------------")
