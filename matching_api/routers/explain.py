from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from db.db_connection import supabase
import os

router = APIRouter()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

EXPLAIN_PROMPT = ChatPromptTemplate.from_template("""
You are an expert AI career advisor explaining a job match to a candidate.

CANDIDATE PROFILE:
Name: {name}
Skills: {skills}
Experience: {experience}
Education: {education}

JOB DETAILS:
Title: {job_title}
Company: {company}
Location: {location}
Job Description: {description}

Give a deep, honest analysis of this match. Structure your response as JSON:
{{
    "overall_summary": "2-3 sentence honest overview of this match",
    "match_score": <0-100 integer>,
    "skills_match_pct": <0-100 integer>,
    "experience_match_pct": <0-100 integer>,
    "strengths": [
        "Specific strength 1 referencing actual skills/experience",
        "Specific strength 2",
        "Specific strength 3"
    ],
    "weaknesses": [
        "Honest gap 1 with context",
        "Honest gap 2"
    ],
    "missing_skills": ["skill1", "skill2"],
    "recommendation": "Should they apply? What should they do first?"
}}

Be specific — reference actual skills and job requirements. No generic advice.
Only return the JSON object, nothing else.
""")


class ExplainRequest(BaseModel):
    user_id: str


@router.post("/explain/{job_id}")
async def explain_match(job_id: int, request: ExplainRequest):
    """
    Deep-dive explanation of why a specific job matches (or doesn't)
    a candidate's resume. Powers the AIInsightsPanel in the frontend.
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
        .select("id, title, company, location, description, link")\
        .eq("id", job_id)\
        .single()\
        .execute()

    if not job_result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_result.data

    # 3. Run LLM explanation
    chain = EXPLAIN_PROMPT | llm | JsonOutputParser()

    analysis = chain.invoke({
        "name": resume.get("name", "Candidate"),
        "skills": resume.get("skills_text", ""),
        "experience": resume.get("experience_text", ""),
        "education": resume.get("education_text", ""),
        "job_title": job.get("title", ""),
        "company": job.get("company", ""),
        "location": job.get("location", ""),
        "description": job.get("description", "")[:1000]
    })

    return {
        "job_id": job_id,
        "job_title": job["title"],
        "company": job["company"],
        **analysis
    }