"""
review_exporter.py

Exports the parsed Review classes into a pandas DataFrame and saves it as a CSV file.

Author: Igor Lacko
"""

import pandas as pd
from models.review import Review


class ReviewExporter:
    """Class for exporting reviews into CSV format."""

    def __init__(self):
        """Class constructor."""
        self.dataframe_folder = "csvs/"

    def create_dataframe(self, hotel_name: str, reviews: list[Review]):
        """Creates a pandas DataFrame from the list of reviews.

        Args:
            hotel_name (str): Name of the hotel.
            reviews (list[Review]): List of Review objects to be included in the DataFrame.
        """
        df = pd.DataFrame(
            [
                {
                    "rating": review.rating,
                    "content_good": review.content_good,
                    "content_bad": review.content_bad,
                }
                for review in reviews
            ]
        )

        df.to_csv(f"{self.dataframe_folder}{hotel_name}.csv", index=False)
