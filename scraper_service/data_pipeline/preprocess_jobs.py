def normalize_jobs(raw_jobs):

    processed = []

    for job in raw_jobs:

        processed.append({
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "description": job.get("description"),
            "created": job.get("created")
        })

    return processed