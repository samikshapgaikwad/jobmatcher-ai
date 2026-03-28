import os
import psycopg2
import hashlib
from dotenv import load_dotenv
from datetime import date

load_dotenv()
DB_URL = os.getenv("SUPABASE_DB_URL")

def job_hash(job):
    """
    Generate a unique hash for deduplication.
    """
    key = f"{job.get('title')}-{job.get('company')}-{job.get('location')}-{job.get('source')}"
    return hashlib.sha256(key.encode()).hexdigest()

def insert_jobs(jobs):
    """
    Insert jobs into PostgreSQL with deduplication.
    """
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    for job in jobs:
        h = job_hash(job)
        cur.execute("""
            INSERT INTO jobs (run_date, title, company, location, description, link, source, created, closing_date, hash)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (hash) DO NOTHING;
        """, (
            date.today(),
            job.get("title"),
            job.get("company"),
            job.get("location"),
            job.get("description"),
            job.get("link"),
            job.get("source"),
            job.get("created"),
            job.get("closing_date"),
            h
        ))

    conn.commit()
    cur.close()
    conn.close()

def cleanup_expired_jobs():
    """
    Delete jobs past their closing date.
    """
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("DELETE FROM jobs WHERE closing_date < %s", (date.today(),))
    conn.commit()
    cur.close()
    conn.close()
