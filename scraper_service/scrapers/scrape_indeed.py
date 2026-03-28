from playwright.sync_api import sync_playwright
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

def clean_text(text):
    if not text: return None
    return " ".join(text.split())

def generate_hash(title, company, location, link):
    raw = f"{title}|{company}|{location}|{link}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def save_jobs(jobs):
    if not jobs:
        print("No jobs in this batch to save.")
        return
    try:
        # Batch upsert to Supabase
        supabase.table("jobs").upsert(jobs, on_conflict=["hash"]).execute()
        print(f"✅ Successfully upserted {len(jobs)} jobs into Supabase.")
    except Exception as e:
        print(f"❌ Database Error: {e}")

def scrape_indeed(query="data scientist", location="India", headless=False, max_pages=5):
    base_url = "https://www.indeed.com"
    all_jobs = []
    start = 0
    page_num = 1

    with sync_playwright() as p:
        # Launch browser with slow_mo to avoid bot detection
        browser = p.chromium.launch(headless=headless, slow_mo=1000)
        # Set a realistic user agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        while page_num <= max_pages:
            url = f"{base_url}/jobs?q={query.replace(' ', '+')}&l={location}&start={start}"
            print(f"\n--- Scraping Page {page_num} (start={start}) ---")
            
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector(".job_seen_beacon", timeout=15000)
            except Exception as e:
                print(f"Page load failed or timed out: {e}")
                break

            cards = page.query_selector_all(".job_seen_beacon")
            jobs_this_page = []

            for card in cards:
                try:
                    # 1. Basic Metadata Extraction
                    title_el = card.query_selector("h2.jobTitle span")
                    comp_el = card.query_selector("[data-testid='company-name']")
                    loc_el = card.query_selector("[data-testid='text-location']")
                    link_el = card.query_selector("a.jcs-JobTitle")

                    title = clean_text(title_el.inner_text() if title_el else None)
                    company = clean_text(comp_el.inner_text() if comp_el else None)
                    location = clean_text(loc_el.inner_text() if loc_el else None)
                    link = link_el.get_attribute("href") if link_el else None
                    
                    if not title: continue

                    # 2. THE CLICK: Load full description in side pane
                    card.scroll_into_view_if_needed()
                    card.click(force=True) 
                    time.sleep(2) # Vital: Give the side pane time to fetch content
                    
                    # 3. Target the FULL description container
                    full_desc_el = page.query_selector("#jobDescriptionText")
                    if full_desc_el:
                        full_description = full_desc_el.inner_text()
                    else:
                        # Fallback to snippet if description pane fails
                        snippet_el = card.query_selector(".job-snippet")
                        full_description = snippet_el.inner_text() if snippet_el else "No description available"

                    # 4. FIXED DATES: Prevent Not-Null Violation
                    today_str = date.today().isoformat()
                    # If closing_date is mandatory, we default to 30 days from now
                    future_closing = (date.today() + timedelta(days=30)).isoformat()

                    job_hash = generate_hash(title, company, location, link)
                    
                    jobs_this_page.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": full_description,
                        "link": f"{base_url}{link}" if link and link.startswith("/") else link,
                        "source": "Indeed",
                        "run_date": today_str,
                        "closing_date": future_closing, # FIX: Ensures this is NEVER null
                        "hash": job_hash,
                        "created_at": datetime.utcnow().isoformat()
                    })
                    print(f"Captured: {title} @ {company} ({len(full_description)} chars)")

                except Exception as e:
                    print(f"Skipping a job due to error: {e}")
                    continue

            # Save the current page batch
            save_jobs(jobs_this_page)
            all_jobs.extend(jobs_this_page)

            # Move to next page (Indeed uses 10-job increments)
            start += 10
            page_num += 1
            time.sleep(5) # Delay to avoid being blocked

        browser.close()
    return all_jobs

if __name__ == "__main__":
    scrape_indeed("data scientist", "India", headless=False)