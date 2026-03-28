import logging
import time
import os
import sys
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

# Make sure scraper_service root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.scrape_unstop import scrape_unstop
from data_pipeline.fetch_jobs import fetch_and_save
from data_pipeline.db_utils import cleanup_expired_jobs

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def run_pipeline():
    """
    Production-safe pipeline — API sources only.
    Playwright scrapers skipped — no display server on Railway.
    """
    logging.info("=" * 50)
    logging.info(f"Pipeline started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total = 0

    # 1. Unstop — JSON API, no browser needed
    try:
        logging.info("Scraping Unstop...")
        unstop_jobs = scrape_unstop(max_pages=20, jobs_per_page=30)
        logging.info(f"✅ Unstop: {len(unstop_jobs)} jobs scraped")
        total += len(unstop_jobs)
    except Exception as e:
        logging.error(f"❌ Unstop failed: {e}")

    # 2. Adzuna — REST API, no browser needed
    try:
        logging.info("Fetching Adzuna jobs...")
        queries = [
            "software engineer",
            "data scientist",
            "machine learning engineer",
            "backend developer",
            "frontend developer",
            "python developer",
            "AI engineer",
            "full stack developer"
        ]
        for query in queries:
            jobs = fetch_and_save(query=query, location="India", max_results=50)
            logging.info(f"✅ Adzuna '{query}': {len(jobs)} jobs")
            total += len(jobs)
    except Exception as e:
        logging.error(f"❌ Adzuna failed: {e}")

    # 3. Cleanup expired jobs
    try:
        logging.info("Cleaning up expired jobs...")
        cleanup_expired_jobs()
        logging.info("✅ Expired jobs removed.")
    except Exception as e:
        logging.error(f"❌ Cleanup failed: {e}")

    logging.info(f"Pipeline complete. Total jobs processed: {total}")
    logging.info("=" * 50)


def start_scheduler():
    """
    Starts the background scheduler.
    Reads run time from PIPELINE_RUN_TIME env var (default 02:00).
    """
    run_time = os.getenv("PIPELINE_RUN_TIME", "02:00")
    hour, minute = run_time.split(":")

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_pipeline,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        id="daily_pipeline",
        replace_existing=True
    )
    scheduler.start()
    logging.info(f"✅ Scraper scheduler started. Running daily at {run_time}.")
    return scheduler


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the scraper pipeline.")
    parser.add_argument("--now", action="store_true", help="Run pipeline immediately")
    args = parser.parse_args()

    if args.now:
        logging.info("Running pipeline immediately...")
        run_pipeline()
    else:
        scheduler = start_scheduler()
        logging.info("Scheduler running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            logging.info("Scheduler stopped cleanly.")