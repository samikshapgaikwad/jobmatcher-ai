import os
import re
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Adzuna API credentials
# ---------------------------------------------------------------------------
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
    raise ValueError(
        "Missing Adzuna API credentials. "
        "Set ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env file."
    )

# ---------------------------------------------------------------------------
# Pipeline settings
# ---------------------------------------------------------------------------
DEFAULT_QUERY = os.getenv("DEFAULT_QUERY", "software engineer")
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "India")

# Max results to fetch per source
MAX_RESULTS_ADZUNA = int(os.getenv("MAX_RESULTS_ADZUNA", 50))
MAX_SCRAPER_PAGES = int(os.getenv("MAX_SCRAPER_PAGES", 2))

# ---------------------------------------------------------------------------
# Schedule time — validated at startup
# ---------------------------------------------------------------------------
PIPELINE_RUN_TIME = os.getenv("PIPELINE_RUN_TIME", "02:00")

_TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
if not _TIME_PATTERN.match(PIPELINE_RUN_TIME):
    raise ValueError(
        f"Invalid PIPELINE_RUN_TIME: '{PIPELINE_RUN_TIME}'. "
        "Expected format HH:MM in 24-hour time e.g. '02:00'."
    )