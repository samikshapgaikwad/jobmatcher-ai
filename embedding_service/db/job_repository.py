import os
from dotenv import load_dotenv
from supabase import create_client
from typing import List, Dict

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase configuration. Check your .env file.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class JobRepository:
    def __init__(self):
        self.client = supabase

    def get_unembedded_jobs(self, limit: int = 100) -> List[Dict]:
        """
        Fetch jobs where any embedding field is NULL.
        Only selects text columns — avoids pulling heavy embedding vectors.
        """
        response = (
            self.client
            .table("jobs")
            .select("id, title, company, location, description")
            .or_(
                "requirements_embedding.is.null,"
                "responsibilities_embedding.is.null,"
                "qualifications_embedding.is.null,"
                "title_embedding.is.null,"
                "description_embedding.is.null"
            )
            .limit(limit)
            .execute()
        )

        return response.data or []

    def update_job_embeddings(self, job_id: int, embeddings_dict: Dict[str, List[float]]):
        """
        Update multiple embedding columns for a specific job.
        Raises RuntimeError if the update fails silently.
        """
        response = (
            self.client
            .table("jobs")
            .update(embeddings_dict)
            .eq("id", job_id)
            .execute()
        )

        if not response.data:
            raise RuntimeError(f"Failed to update embeddings for job_id: {job_id}")

        return response