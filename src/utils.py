"""
utils.py

Shared utility functions that don't fit anywhere else.

Author: Igor Lacko
"""


def url_to_csv(url: str) -> str:
    """Converts a hotel URL to a CSV filename.
    Args:
        url (str): The hotel URL.
    Returns:
        str: The corresponding CSV filename.
    """
    start = url.rfind("/") + 1
    end = url.rfind(".html")
    hotel_name = url[start:end]
    return f"{hotel_name.lower().replace('-', '_')}.csv"

def shorten_url(url: str) -> str:
    """Shortens a Booking.com hotel URL so that it is only hotel-name.html and nothing past that.
    Args:
        url (str): The full hotel URL.
    Returns:
        str: The shortened URL.
    """
    end = url.find(".html") + len(".html")
    return url[:end]