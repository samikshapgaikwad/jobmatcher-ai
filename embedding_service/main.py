import os
import shutil
import logging
import time
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from services.resume_embedding_service import ResumeEmbeddingService
from services.job_embedding_service import JobEmbeddingService
from services.scheduler import EmbeddingScheduler
from db.job_repository import JobRepository
from models.embedding_model import get_embedding_model

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="JobMatch AI — Embedding Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jobmatcher-ai.onrender.com",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup: boot scheduler for job embeddings ────────────────────────────────
@app.on_event("startup")
def startup():
    logging.info("Booting embedding service...")
    model = get_embedding_model()
    repository = JobRepository()
    job_service = JobEmbeddingService(model, repository)

    interval = int(os.getenv("BATCH_INTERVAL_MINUTES", 5))
    scheduler = EmbeddingScheduler(job_embedding_service=job_service, interval_minutes=interval)
    scheduler.run_once()
    scheduler.start()

    # Store on app state so shutdown can access it
    app.state.scheduler = scheduler
    logging.info("Embedding service ready.")


@app.on_event("shutdown")
def shutdown():
    if hasattr(app.state, "scheduler"):
        app.state.scheduler.shutdown()
        logging.info("Scheduler shut down cleanly.")


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "embedding"}


# ── Resume Upload Endpoint ────────────────────────────────────────────────────
UPLOAD_DIR = Path("tmp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    """
    Accepts a resume PDF or DOCX from the frontend.
    Saves it temporarily, runs the full embedding pipeline,
    stores result in Supabase, then cleans up the temp file.
    """
    # 1. Validate file type
    filename = file.filename or ""
    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF and DOCX are accepted."
        )

    # 2. Save to temp path — use user_id to avoid collisions
    suffix = ".pdf" if filename.endswith(".pdf") else ".docx"
    temp_path = UPLOAD_DIR / f"{user_id}{suffix}"

    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logging.info(f"Saved resume for user {user_id} → {temp_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # 3. Run embedding pipeline
    try:
        model = get_embedding_model()
        service = ResumeEmbeddingService(model)
        service.process_resume(str(temp_path), user_id)
        logging.info(f"Resume pipeline complete for user {user_id}")
    except ValueError as e:
        # Text extraction failed — bad file
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logging.error(f"Resume pipeline failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding pipeline failed: {e}")
    finally:
        # 4. Always clean up temp file
        if temp_path.exists():
            temp_path.unlink()
            logging.info(f"Cleaned up temp file: {temp_path}")

    return {
        "status": "success",
        "message": "Resume processed and stored successfully.",
        "user_id": user_id
    }

