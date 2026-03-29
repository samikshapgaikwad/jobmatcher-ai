from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import match, cover_letter, explain, chat

load_dotenv()

app = FastAPI(title="JobMatch AI — Matching API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match.router, prefix="/api")
app.include_router(cover_letter.router, prefix="/api")
app.include_router(explain.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "agent": "LangGraph",
        "llm": "Groq llama-3.3-70b-versatile"
    }