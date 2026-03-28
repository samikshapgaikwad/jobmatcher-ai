import requests
import os
import hashlib
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def generate_hash(title, company, location, link):
    raw = f"{title}|{company}|{location}|{link}"
    return hashlib.sha256(raw.encode()).hexdigest()


def fetch_and_save(query="software engineer", location="India", max_results=50):
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": max_results,
        "what": query,
        "where": location
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"API Error for '{query}':", response.text)
        return []

    raw_jobs = response.json().get("results", [])
    jobs = []

    for job in raw_jobs:
        title = job.get("title", "")
        company = job.get("company", {}).get("display_name", "")
        location_str = job.get("location", {}).get("display_name", "")
        description = job.get("description", "")
        link = job.get("redirect_url", "")
        run_date = date.today().isoformat()
        closing_date = (date.today() + timedelta(days=30)).isoformat()

        if not title:
            continue

        jobs.append({
            "title": title,
            "company": company,
            "location": location_str,
            "description": description,
            "link": link,
            "source": "Adzuna",
            "run_date": run_date,
            "closing_date": closing_date,
            "created_at": datetime.utcnow().isoformat(),
            "hash": generate_hash(title, company, location_str, link)
        })

    if jobs:
        supabase.table("jobs").upsert(jobs, on_conflict=["hash"]).execute()
        print(f"✅ Upserted {len(jobs)} Adzuna jobs for query: '{query}'")

    return jobs


if __name__ == "__main__":
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

    total = 0
    for query in queries:
        jobs = fetch_and_save(query=query, location="India", max_results=50)
        total += len(jobs)

    print(f"\nTotal Adzuna jobs upserted: {total}")