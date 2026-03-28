from db.db_connection import supabase


class ResumeRepository:

    @staticmethod
    def store_resume(user_id: str, resume_data: dict):
        """
        Upserts a resume record into Supabase.
        If a resume already exists for user_id, it gets updated.
        Raises RuntimeError if the operation fails.
        """
        response = supabase.table("resumes").upsert({
            "user_id": user_id,
            "name": resume_data.get("name"),
            "email": resume_data.get("email"),
            "phone": resume_data.get("phone"),
            "raw_text": resume_data.get("raw_text"),

            # Text sections
            "skills_text": resume_data.get("skills_text"),
            "experience_text": resume_data.get("experience_text"),
            "education_text": resume_data.get("education_text"),
            "achievements_text": resume_data.get("achievements_text"),
            "extracurricular_text": resume_data.get("extracurricular_text"),

            # 384-dimension vectors
            "skills_embedding": resume_data.get("skills_embedding"),
            "experience_embedding": resume_data.get("experience_embedding"),
            "education_embedding": resume_data.get("education_embedding"),
            "achievements_embedding": resume_data.get("achievements_embedding"),
            "full_resume_embedding": resume_data.get("full_resume_embedding")

        }, on_conflict="user_id").execute()

        if not response.data:
            raise RuntimeError(f"Failed to store resume for user_id: {user_id}")

        return response