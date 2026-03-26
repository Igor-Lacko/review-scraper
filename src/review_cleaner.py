"""
review_cleaner.py

Exports the parsed Review classes into a pandas DataFrame and saves it as a CSV file, or cleans existing CSV files.

Author: Igor Lacko
"""

import pandas as pd
import os
import sys
from models.review import Review
from models.statistics import Statistics
from shared import console


class ReviewCleaner:
    """Class for cleaning and exporting reviews into CSV format."""

    # Array to hold statistics about processed hotels
    statistics: list[Statistics] = []

    def __init__(self, **kwargs: str):
        """Class constructor.

        Args:
            kwargs: Additional keyword arguments, such as export folder.
        """
        self.dataframe_folder = kwargs.get("dataframe_folder", "csvs/")
        self.statistics_mode = kwargs.get("statistics", "none")
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

        if self.statistics_mode in ("for-each", "all"):
            self.compute_statistics(hotel_name, df)

    def __clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans the DataFrame before exporting. Removes empty reviews, reviews shorter than 100 chars and duplicates.

        Args:
            df (pd.DataFrame): Input DataFrame.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        # Remove surrounding quotes from content columns
        for col in ["content_good", "content_bad"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip('"')

        df = df.dropna(how="all", subset=["content_good", "content_bad"])
        mask = (
            df["content_good"].fillna("").apply(len)
            + df["content_bad"].fillna("").apply(len)
            >= 100
        )
        df = df[mask].drop_duplicates()

        return df

    def compute_statistics(self, name: str, df: pd.DataFrame):
        """Computes statistics for the given DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame.
        """
        total_reviews = df.shape[0]
        mean_rating = df["rating"].mean()
        mean_length = (
            df["content_good"].fillna("").apply(len).mean()
            + df["content_bad"].fillna("").apply(len).mean()
        )
        max_length = (
            df["content_good"].fillna("").apply(len).max()
            + df["content_bad"].fillna("").apply(len).max()
        )

        # Calculate length for each row
        review_lengths = df["content_good"].fillna("").apply(len) + df[
            "content_bad"
        ].fillna("").apply(len)
        min_length = review_lengths.min() if not review_lengths.empty else 0

        with_positive_empty = df["content_good"].isna().sum()
        with_negative_empty = df["content_bad"].isna().sum()

        stats = Statistics(
            name=name,
            total_reviews=total_reviews,
            mean_rating=mean_rating,
            mean_length=mean_length,
            max_length=max_length,
            min_length=min_length,
            with_positive_empty=with_positive_empty,
            with_negative_empty=with_negative_empty,
        )

        if self.statistics_mode in ("summary", "all"):
            self.statistics.append(stats)

        if self.statistics_mode in ("for-each", "all"):
            stats.print_summary()

    def compute_summary(self):
        """Computes and prints summary statistics for all processed hotels."""
        if not self.statistics:
            console.print("[bold red]No statistics to summarize.[/bold red]")
            return

        total_reviews = 0
        total_mean_rating = 0.0
        total_mean_length = 0.0
        total_max_length = 0
        total_min_length = sys.maxsize
        total_with_positive_empty = 0
        total_with_negative_empty = 0

        valid_ratings_count = 0
        valid_lengths_count = 0

        for stats in self.statistics:
            total_reviews += stats.total_reviews

            if stats.mean_rating is not None and not pd.isna(stats.mean_rating):
                total_mean_rating += stats.mean_rating
                valid_ratings_count += 1

            if stats.mean_length is not None and not pd.isna(stats.mean_length):
                total_mean_length += stats.mean_length
                valid_lengths_count += 1

            total_max_length = max(
                total_max_length,
                (stats.max_length if stats.max_length is not None else 0),
            )
            total_min_length = min(
                total_min_length,
                (stats.min_length if stats.min_length is not None else sys.maxsize),
            )
            total_with_positive_empty += (
                stats.with_positive_empty
                if stats.with_positive_empty is not None
                else 0
            )
            total_with_negative_empty += (
                stats.with_negative_empty
                if stats.with_negative_empty is not None
                else 0
            )

        summary = Statistics(
            name="SUMMARY",
            total_reviews=total_reviews,
            mean_rating=(
                total_mean_rating / valid_ratings_count
                if valid_ratings_count > 0
                else 0.0
            ),
            mean_length=(
                total_mean_length / valid_lengths_count
                if valid_lengths_count > 0
                else 0.0
            ),
            max_length=total_max_length,
            min_length=total_min_length if total_min_length != sys.maxsize else 0,
            with_positive_empty=total_with_positive_empty,
            with_negative_empty=total_with_negative_empty,
        )

        summary.print_summary()

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

    def show_stored_statistics(self):
        """Prints stored statistics for all stored csv files."""
        for csv_file in os.listdir(self.dataframe_folder):
            if csv_file.endswith(".csv"):
                filepath = os.path.join(self.dataframe_folder, csv_file)
                df = pd.read_csv(filepath)
                hotel_name = csv_file[:-4].replace("_", " ").title()
                self.compute_statistics(hotel_name, df)

        if self.statistics_mode in ("summary", "all"):
            self.compute_summary()

    def combine_csvs(self):
        """Combines all cleaned CSV files in the dataframe folder into a single CSV file."""
        console.print("[bold green]Combining CSV files...[/bold green]")
        dataframes = []

        for filename in os.listdir(self.dataframe_folder):
            if filename.endswith(".csv") and filename != "dataset.csv":
                filepath = os.path.join(self.dataframe_folder, filename)
                console.print(f"[blue]Processing file: {filename}[/blue]")
                df = pd.read_csv(filepath)
                if not df.empty:
                    dataframes.append(df)
                else:
                    console.print(f"[yellow]Skipping empty file: {filename}[/yellow]")

        if dataframes:
            df: pd.DataFrame = pd.concat(dataframes, ignore_index=True)
            # Still not sure whether to use them separately or unified
            df["unified"] = (
                df["content_good"].fillna("") + " " + df["content_bad"].fillna("")
            ).str.strip()
            df = df.drop_duplicates(subset=["unified"])
            df.to_csv(os.path.join(self.dataframe_folder, "dataset.csv"), index=False)

        console.print("[bold green]CSV files combined into 'dataset.csv'.[/bold green]")
