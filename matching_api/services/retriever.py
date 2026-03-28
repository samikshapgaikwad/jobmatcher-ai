from db.db_connection import supabase
from typing import List, Dict


def retrieve_matching_jobs(
    user_id: str,
    resume: dict,
    top_k: int = 20,
    threshold: float = 0.3
) -> List[Dict]:
    seen_ids = set()
    all_jobs = []

    # Use resume embeddings to query against job description_embedding
    embedding_fields = [
        "skills_embedding",
        "experience_embedding",
        "full_resume_embedding",
    ]

    for field in embedding_fields:
        embedding = resume.get(field)
        if not embedding:
            continue

        try:
            result = supabase.rpc(
                "match_jobs",
                {
                    "query_embedding": embedding,
                    "match_count": top_k,
                    "match_threshold": threshold
                }
            ).execute()

            for job in (result.data or []):
                if job["id"] not in seen_ids:
                    seen_ids.add(job["id"])
                    all_jobs.append(job)

        except Exception as e:
            print(f"[Retriever] RPC failed for field '{field}': {e}")
            continue

    print(f"[Retriever] Retrieved {len(all_jobs)} unique jobs")
    return all_jobs