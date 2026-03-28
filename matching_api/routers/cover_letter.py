from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from db.db_connection import supabase
import os

router = APIRouter()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY")
)

COVER_LETTER_PROMPT = ChatPromptTemplate.from_template("""
You are an expert career coach writing a personalized cover letter.

CANDIDATE PROFILE:
Name: {name}
Skills: {skills}
Experience: {experience}

JOB DETAILS:
Title: {job_title}
Company: {company}
Job Description: {description}

Write a compelling, specific, 3-paragraph cover letter.
- Paragraph 1: Strong opening that mentions the role and a key strength
- Paragraph 2: Match 2-3 specific skills/experiences to job requirements
- Paragraph 3: Closing with enthusiasm and call to action

Tone: Professional but human. No generic phrases like "I am writing to apply".
Only return the cover letter text, no extra explanation.
""")


class CoverLetterRequest(BaseModel):
    user_id: str


@router.post("/cover-letter/{job_id}")
async def generate_cover_letter(job_id: int, request: CoverLetterRequest):
    """
    Generates a personalized cover letter for a specific job
    using the candidate's resume data. Pure GenAI showcase endpoint.
    """
    # 1. Fetch resume
    resume_result = supabase.table("resumes")\
        .select("name, skills_text, experience_text")\
        .eq("user_id", request.user_id)\
        .single()\
        .execute()

    if not resume_result.data:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = resume_result.data

    # 2. Fetch job
    job_result = supabase.table("jobs")\
        .select("id, title, company, location, description, link")\
        .eq("id", job_id)\
        .single()\
        .execute()

    if not job_result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_result.data

    # 3. Generate cover letter
    chain = COVER_LETTER_PROMPT | llm

    result = chain.invoke({
        "name": resume.get("name", "Candidate"),
        "skills": resume.get("skills_text", ""),
        "experience": resume.get("experience_text", ""),
        "job_title": job.get("title", ""),
        "company": job.get("company", ""),
        "description": job.get("description", "")[:1000]
    })

    return {
        "cover_letter": result.content,
        "job_title": job["title"],
        "company": job["company"],
        "location": job.get("location", ""),
        "link": job.get("link", "")
    }