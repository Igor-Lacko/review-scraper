"""
statistics.py

Data model for storing statistics about hotel reviews.

Author: Igor Lacko
"""

from dataclasses import dataclass
from rich.table import Table
from shared import console


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
        table = Table(
            title=f"{self.name.upper()} STATISTICS",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")

        table.add_row("Total reviews", str(self.total_reviews))
        table.add_row("Mean rating", f"{self.mean_rating:.2f}")
        table.add_row("Mean review length", f"{self.mean_length:.2f}")
        table.add_row("Max review length", str(self.max_length))
        table.add_row("Min review length", str(self.min_length))
        table.add_row("Positive empty", str(self.with_positive_empty))
        table.add_row("Negative empty", str(self.with_negative_empty))
        table.add_row("Both present", str(self.with_both_sentiments))

        console.print(table)
