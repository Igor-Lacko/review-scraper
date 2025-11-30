"""
review_cleaner.py

Exports the parsed Review classes into a pandas DataFrame and saves it as a CSV file, or cleans existing CSV files.

Author: Igor Lacko
"""

import pandas as pd
import os
from models.review import Review


class ReviewCleaner:
    """Class for cleaning and exporting reviews into CSV format."""

    def __init__(self, **kwargs: str):
        """Class constructor.

        Args:
            kwargs: Additional keyword arguments, such as export folder.
        """
        self.dataframe_folder = kwargs.get("dataframe_folder", "csvs/")
        os.makedirs(self.dataframe_folder, exist_ok=True)

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

        df = self.__clean(df)

        df.to_csv(
            f"{self.dataframe_folder}{hotel_name.lower().replace(' ', '_')}.csv",
            index=False,
        )

    def __clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans the DataFrame before exporting. Removes empty reviews and duplicates.

        Args:
            df (pd.DataFrame): Input DataFrame.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        df = df.dropna(how="all", subset=["content_good", "content_bad"])
        df = df.drop_duplicates()
        return df

    def clean_one_csv(self, filepath: str):
        """Cleans an existing CSV file by removing empty reviews and duplicates.

        Args:
            filepath (str): Path to the CSV file.
        """
        df = pd.read_csv(filepath)
        df = self.__clean(df)
        df.to_csv(filepath, index=False)

    def clean_folder(self):
        """Cleans all CSV files in the dataframe folder."""
        for filename in os.listdir(self.dataframe_folder):
            if filename.endswith(".csv"):
                self.clean_one_csv(os.path.join(self.dataframe_folder, filename))
