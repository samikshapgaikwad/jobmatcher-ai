from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from db.db_connection import supabase
import os

router = APIRouter()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    api_key=os.getenv("GROQ_API_KEY")
)

CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert AI career advisor helping a candidate evaluate a specific job opportunity.

CANDIDATE PROFILE:
Name: {name}
Skills: {skills}
Experience: {experience}
Education: {education}

JOB DETAILS:
Title: {job_title}
Company: {company}
Location: {location}
Description: {description}

Current match score: {match_score}%
Missing skills: {missing_skills}

You have deep knowledge of both the candidate's profile and this specific job.
Be specific, honest, and actionable. Reference actual skills and requirements.
Keep responses concise — 2-4 sentences max unless asked for more.
"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{message}")
])


class ChatMessage(BaseModel):
    role: str    # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    user_id: str
    job_id: int
    message: str
    match_score: int = 0
    missing_skills: List[str] = []
    history: List[ChatMessage] = []


@router.post("/chat/{job_id}")
async def chat_about_job(job_id: int, request: ChatRequest):
    """
    Conversational AI endpoint about a specific job.
    Maintains history client-side — stateless on server.
    Each message has full context of candidate + job + conversation so far.
    """
    # 1. Fetch resume
    resume_result = supabase.table("resumes")\
        .select("name, skills_text, experience_text, education_text")\
        .eq("user_id", request.user_id)\
        .single()\
        .execute()

    if not resume_result.data:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = resume_result.data

    # 2. Fetch job
    job_result = supabase.table("jobs")\
        .select("title, company, location, description")\
        .eq("id", job_id)\
        .single()\
        .execute()

    if not job_result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_result.data

    # 3. Convert history to LangChain messages
    history_messages = []
    for msg in request.history:
        if msg.role == "user":
            history_messages.append(HumanMessage(content=msg.content))
        else:
            history_messages.append(AIMessage(content=msg.content))

    # 4. Run chain
    chain = CHAT_PROMPT | llm

    response = chain.invoke({
        "name": resume.get("name", "Candidate"),
        "skills": resume.get("skills_text", ""),
        "experience": resume.get("experience_text", ""),
        "education": resume.get("education_text", ""),
        "job_title": job.get("title", ""),
        "company": job.get("company", ""),
        "location": job.get("location", ""),
        "description": job.get("description", "")[:800],
        "match_score": request.match_score,
        "missing_skills": ", ".join(request.missing_skills) or "none",
        "history": history_messages,
        "message": request.message
    })

    return {
        "reply": response.content,
        "job_id": job_id
    }