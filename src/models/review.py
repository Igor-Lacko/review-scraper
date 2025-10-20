"""
review.py

Data model for hotel reviews.

Author: Igor Lacko
"""

from dataclasses import dataclass


@dataclass
class Review:
    """Class modelling one hotel review."""

    rating: float
    content_good: str
    content_bad: str
