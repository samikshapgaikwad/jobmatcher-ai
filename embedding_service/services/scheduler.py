import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
# No need to import the Class here since we pass the instance in

class EmbeddingScheduler:
    # 1. Update __init__ to accept your initialized service instance
    def __init__(self, job_embedding_service, interval_minutes: int = 5):
        self.interval_minutes = interval_minutes
        self.scheduler = BackgroundScheduler()
        self.job_service = job_embedding_service # Store the instance

    # ---------- Startup batch execution ----------
    def run_once(self):
        logging.info("Running embedding batch once...")
        # 2. Use the instance (self.job_service) and the correct method name
        self.job_service.process_unembedded_jobs()

    # ---------- Scheduler starter ----------
    def start(self):
        logging.info("Starting embedding scheduler...")

        # 3. Schedule the instance method
        self.scheduler.add_job(
            self.job_service.process_unembedded_jobs,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id="job_embedding_batch",
            replace_existing=True
        )

        self.scheduler.start()

        logging.info(
            f"Scheduler started. Running every {self.interval_minutes} minutes."
        )

    # ---------- Graceful shutdown ----------
    def shutdown(self):
        logging.info("Shutting down scheduler...")
        if self.scheduler.running:
            self.scheduler.shutdown()