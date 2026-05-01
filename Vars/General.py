from enum import IntEnum, auto

import cloudscraper

from rich.console import Console

console = Console()
scrapper = cloudscraper.create_scraper()

default_error_result_text = "thing went boom :("
default_result_text = "thing happen here when you press the button :3"

catagories = {}

class Errors(IntEnum):
    GENERAL = auto()
    BOT_DETECTION = auto()
    RATE_LIMIT = auto()
    UNAUTHORIZED = auto()
    TIMEOUT = auto()