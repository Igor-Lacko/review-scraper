"""
url_filter.py

Utility module for filtering out urls (from list or txt file) that have already been scraped.

Author: Igor Lacko
"""

import os
from shared import console
from utils import url_to_csv


class URLFilter:
    """Class for filtering URLs based on existing CSV files."""

    def __init__(self, dataframe_folder: str):
        """Class constructor.

        Args:
            dataframe_folder (str): Path to the folder containing existing CSV files.
        """
        self.existing_files = (
            os.listdir(dataframe_folder) if os.path.exists(dataframe_folder) else []
        )

    def filter_existing_urls(self, urls: list[str]) -> list[str]:
        """Filters out URLs for which CSV files already exist in the specified folder.

        Args:
            urls (list[str]): List of URLs to filter.

        Returns:
            list[str]: List of URLs that do not have corresponding CSV files in the folder.
        """
        files_to_add = [url_to_csv(url) for url in urls]
        # For loop to print out skipped files
        filtered_urls = []
        for url, file in zip(urls, files_to_add):
            if file in self.existing_files:
                console.print(
                    f"[yellow]Skipping URL (CSV already exists): {url} -> {file}[/yellow]"
                )
            else:
                filtered_urls.append(url)
        return filtered_urls

    def filter_one_url(self, url: str) -> bool:
        """Checks if a single URL has a corresponding CSV file in the folder.

        Args:
            url (str): The URL to check.
        Returns:
            bool: True if the URL does not have a corresponding CSV file, False otherwise.
        """
        file = url_to_csv(url)
        if file in self.existing_files:
            console.print(
                f"[yellow]Skipping URL (CSV already exists): {url} -> {file}[/yellow]"
            )
            return False
        return True
