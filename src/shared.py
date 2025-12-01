"""
shared.py

Shared resources for the application (so far only the rich Console). This file exists because:
    - Circular imports exist, and
    - I didn't like creating Console() in each file

Author: Igor Lacko
"""

from rich.console import Console

console = Console()
