import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from scheduler import run_pipeline, start_scheduler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = FastAPI(title="JobMatch AI — Scraper Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    logging.info("Booting scraper service...")
    run_pipeline()
    scheduler = start_scheduler()
    app.state.scheduler = scheduler
    logging.info("Scraper service ready.")


@app.on_event("shutdown")
def shutdown():
    if hasattr(app.state, "scheduler"):
        app.state.scheduler.shutdown()


@app.get("/health")
def health():
    return {"status": "ok", "service": "scraper"}


@app.post("/run-now")
def run_now():
    run_pipeline()
    return {"status": "pipeline triggered"}