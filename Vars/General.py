from enum import IntEnum, auto

import cloudscraper

from rich.console import Console

console = Console()
scrapper = cloudscraper.create_scraper()

class Errors(IntEnum):
    GENERAL = auto()
    BOT_DETECTION = auto()
    RATE_LIMIT = auto()
    UNAUTHORIZED = auto()
    TIMEOUT = auto()