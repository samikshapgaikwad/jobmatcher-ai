import requests
import time
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client
import hashlib

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive"
}

def clean_text(text):
    return text.strip() if text else None

def generate_hash(title, company, location, link):
    raw = f"{title}|{company}|{location}|{link}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def save_jobs(jobs):
    if not jobs:
        print("No jobs to save.")
        return
    try:
        response = supabase.table("jobs").upsert(jobs, on_conflict=["hash"]).execute()
        print(f"Upserted {len(jobs)} jobs into Supabase")
    except Exception as e:
        print(f"Error inserting jobs: {e}")

def extract_page(url, params):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def scrape_unstop(max_pages=50, jobs_per_page=30):
    base_url = "https://unstop.com/api/public/opportunity/search-result"
    oppstatus = "open"   # focus on currently open jobs
    all_jobs = []
    page = 1

    while page <= max_pages:
        print(f"Scraping page {page} for status='{oppstatus}'...")
        params = {
            "opportunity": "jobs",
            "oppstatus": oppstatus,
            "page": page,
            "size": jobs_per_page
        }
        headers["Referer"] = f"https://unstop.com/api/public/opportunity/search-result?opportunity=jobs&oppstatus={oppstatus}"

        data = extract_page(base_url, params)
        if not data or "data" not in data or "data" not in data["data"]:
            print("Invalid response or no jobs found.")
            break

        jobs = data["data"]["data"]
        if not jobs:
            print("No more jobs.")
            break

        jobs_this_page = []
        for job in jobs:
            try:
                title = clean_text(job.get("title"))
                company = clean_text(job.get("organisation", {}).get("name"))
                locations = job.get("jobDetail", {}).get("locations", [])
                location_str = ", ".join(locations) if isinstance(locations, list) else None
                description = clean_text(job.get("description", ""))
                link = f"https://unstop.com/{job.get('public_url', '')}"
                start_date = job.get("start_date")
                run_date = start_date if start_date else date.today().isoformat()
                closing_date = (datetime.fromisoformat(run_date) + timedelta(days=30)).date().isoformat()
                job_hash = generate_hash(title, company, location_str, link)

                if not title:
                    continue

                jobs_this_page.append({
                    "title": title,
                    "company": company,
                    "location": location_str,
                    "description": description,
                    "link": link,
                    "source": "Unstop",
                    "created_at": datetime.today().isoformat(),
                    "run_date": run_date,
                    "closing_date": closing_date,
                    "hash": job_hash
                })
            except Exception as e:
                print(f"Error parsing job: {e}")
                continue

        save_jobs(jobs_this_page)
        all_jobs.extend(jobs_this_page)

        page += 1
        time.sleep(1)  # polite delay

    print(f"Scraped {len(all_jobs)} jobs across pages")
    return all_jobs

if __name__ == "__main__":
    results = scrape_unstop(max_pages=20, jobs_per_page=30)
    print(f"Final total: {len(results)} jobs scraped and upserted")
