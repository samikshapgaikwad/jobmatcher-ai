import os
import re
from dotenv import load_dotenv

load_dotenv()

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase config. Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")

# ── Groq ──────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "Missing GROQ_API_KEY. Get a free key at https://console.groq.com"
    )

# ── Agent Settings ────────────────────────────────────────────────────────────
# How many jobs to retrieve from pgvector initially
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", 20))

# Confidence threshold below which the agent retries with broader search
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.5))

# Max retry attempts before agent accepts results regardless of confidence
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))

# ── API Settings ──────────────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8080,http://localhost:3000").split(",")


# ── Validation ────────────────────────────────────────────────────────────────
if not (0.0 <= CONFIDENCE_THRESHOLD <= 1.0):
    raise ValueError(f"CONFIDENCE_THRESHOLD must be between 0 and 1, got: {CONFIDENCE_THRESHOLD}")

if MAX_RETRIES < 0:
    raise ValueError(f"MAX_RETRIES must be >= 0, got: {MAX_RETRIES}")