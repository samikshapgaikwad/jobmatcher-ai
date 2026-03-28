# services/resume_embedding_service.py
from resume_pipeline.resume_parser import parse_resume_metadata
from db.resume_repository import ResumeRepository


class ResumeEmbeddingService:
    def __init__(self, model):
        self.model = model

    def process_resume(self, file_path: str, user_id: str):
        metadata = parse_resume_metadata(file_path)

        payload = {**metadata}

        text_to_vector_map = {
            "education_text": "education_embedding",
            "experience_text": "experience_embedding",
            "skills_text": "skills_embedding",
            "achievements_text": "achievements_embedding",
            "raw_text": "full_resume_embedding"
        }

        for text_field, vector_field in text_to_vector_map.items():
            content = metadata.get(text_field, "")
            if content:
                encoded = self.model.encode(content)
                payload[vector_field] = encoded.tolist() if hasattr(encoded, "tolist") else list(encoded)
            else:
                payload[vector_field] = None

        return ResumeRepository.store_resume(user_id, payload)