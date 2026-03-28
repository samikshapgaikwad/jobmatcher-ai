from playwright.sync_api import sync_playwright
import time
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client
import re
import hashlib

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # ✅ use service role key

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def clean_text(text):
    return text.strip() if text else None

def parse_posted_date(text):
    """Convert Naukri's 'Posted today / 2 days ago' into a proper date."""
    if not text:
        return None
    text = text.lower()
    if "today" in text:
        return date.today().isoformat()
    elif "yesterday" in text:
        return (date.today() - timedelta(days=1)).isoformat()
    else:
        match = re.search(r"(\d+)\s+day", text)
        if match:
            days = int(match.group(1))
            return (date.today() - timedelta(days=days)).isoformat()
    return None

def generate_hash(title, company, location, link):
    """Generate a unique SHA256 hash for each job."""
    raw = f"{title}|{company}|{location}|{link}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def save_jobs(jobs):
    if not jobs:
        print("No jobs to save.")
        return
    try:
        # ✅ Upsert instead of insert, skip duplicates based on hash
        response = supabase.table("jobs").upsert(jobs, on_conflict=["hash"]).execute()
        print(f"Upserted {len(jobs)} jobs into Supabase")
    except Exception as e:
        print(f"Error inserting jobs: {e}")

def scrape_naukri(query="data scientist", location="India", headless=False):
    base_url = "https://www.naukri.com"
    search_url = f"{base_url}/{query.replace(' ', '-')}-jobs-in-{location}"

    jobs = []
    page_num = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=50)
        page = browser.new_page()
        page.goto(search_url, timeout=60000)

        while True:
            print(f"Scraping page {page_num}...")

            try:
                page.wait_for_selector(".srp-jobtuple-wrapper", timeout=15000)
            except Exception as e:
                print(f"No job cards found: {e}")
                break

            cards = page.query_selector_all(".srp-jobtuple-wrapper")
            print(f"Found {len(cards)} job cards on this page")

            for card in cards:
                try:
                    title_el = card.query_selector(".title")
                    company_el = card.query_selector(".comp-name")
                    location_el = card.query_selector(".locWdth")
                    link_el = card.query_selector("a.title")
                    desc_el = card.query_selector(".job-description, .job-desc")
                    posted_el = card.query_selector(".job-post-day, .job-posted, .jobTupleFooter .type")

                    title = clean_text(title_el.inner_text() if title_el else None)
                    company = clean_text(company_el.inner_text() if company_el else None)
                    location = clean_text(location_el.inner_text() if location_el else None)
                    description = clean_text(desc_el.inner_text() if desc_el else None)
                    link = link_el.get_attribute("href") if link_el else None
                    posted_text = clean_text(posted_el.inner_text() if posted_el else None)
                    run_date = parse_posted_date(posted_text)

                    # ✅ Fallbacks for NOT NULL columns
                    run_date = run_date if run_date else date.today().isoformat()
                    closing_date = (datetime.fromisoformat(run_date) + timedelta(days=30)).date().isoformat()
                    job_hash = generate_hash(title, company, location, link)

                    if not title:
                        continue

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": description,
                        "link": link,
                        "source": "Naukri",
                        "created_at": datetime.today().isoformat(),
                        "run_date": run_date,
                        "closing_date": closing_date,
                        "hash": job_hash
                    })

                except Exception as e:
                    print(f"Error parsing card: {e}")
                    continue

            # ✅ Robust pagination
           # Robust pagination
            # Robust pagination using text match
            try:
                next_button = page.get_by_text("Next")
                if next_button:
                    print("Next button found, going to next page...")
                    next_button.scroll_into_view_if_needed()
                    next_button.click()
                    page.wait_for_load_state("networkidle")
                    time.sleep(3)
                    page_num += 1
                else:
                    print("No more pages.")
                    break
            except Exception as e:
                print(f"Pagination failed: {e}")
                break




        browser.close()

    return jobs

if __name__ == "__main__":
    results = scrape_naukri("data scientist", "India", headless=False)
    print(f"Scraped {len(results)} jobs across pages")
    save_jobs(results)
