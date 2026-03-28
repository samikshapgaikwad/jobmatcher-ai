import logging
import argparse
from dotenv import load_dotenv
from services.resume_embedding_service import ResumeEmbeddingService
from models.embedding_model import get_embedding_model

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def run_resume_import(file_path: str, user_id: str):
    """
    Processes a single resume file and stores it in Supabase.
    Run from the embedding_service/ directory:
        python run_resume_pipeline.py --file path/to/resume.pdf --user-id <uuid>
    """
    logging.info(f"Processing resume: {file_path}")

    try:
        model = get_embedding_model()
        service = ResumeEmbeddingService(model)
        service.process_resume(file_path, user_id)
        logging.info("Resume successfully vectorized and stored in Supabase.")

    except FileNotFoundError:
        logging.error(f"Resume file not found: {file_path}")
        raise

    except Exception as e:
        logging.error(f"Resume pipeline failed: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the resume embedding pipeline.")
    parser.add_argument("--file", required=True, help="Path to the resume PDF or DOCX file.")
    parser.add_argument("--user-id", required=True, help="Supabase user UUID for this resume.")
    args = parser.parse_args()

    run_resume_import(file_path=args.file, user_id=args.user_id)