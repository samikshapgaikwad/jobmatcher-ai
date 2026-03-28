import sys
import uuid
from data_pipeline.scheduler import pipeline_job
from resume_pipeline.resume_parser import parse_resume
from resume_pipeline.store_resume import store_resume

def run_job_pipeline():
    pipeline_job()

def run_resume_pipeline(file_path: str, user_id: str = None):
    # Generate a temporary UUID if none is provided (for testing)
    if user_id is None:
        user_id = str(uuid.uuid4())

    # Parse the resume
    resume_data = parse_resume(file_path)
    print("Extracted Skills:", resume_data.get("skills", []))

    # Store resume in Supabase
    store_resume(user_id=user_id, resume_data=resume_data)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "resume":
        # Example: python main.py resume dataset/I2K23178_SamikshaGaikwad_Resume.pdf
        file_path = sys.argv[2]
        run_resume_pipeline(file_path)
    else:
        run_job_pipeline()
