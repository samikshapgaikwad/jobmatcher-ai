from fastapi import APIRouter, HTTPException
from schemas.models import MatchRequest, MatchResponse, JobMatch
from graph.agent import matching_agent
from db.db_connection import supabase

router = APIRouter()

@router.post("/match", response_model=MatchResponse)
async def match_jobs(request: MatchRequest):
    # 1. Fetch resume from Supabase
    result = supabase.table("resumes")\
        .select("*")\
        .eq("user_id", request.user_id)\
        .single()\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Resume not found for this user_id")

    resume = result.data

    # 2. Run LangGraph agent
    final_state = matching_agent.invoke({
        "user_id": request.user_id,
        "resume": resume,
        "retrieved_jobs": [],
        "scored_jobs": [],
        "final_jobs": [],
        "confidence": 0.0,
        "retry_count": 0,
        "error": None
    })

    # 3. Shape response to match frontend Job type exactly
    jobs = [
        JobMatch(
            id=j["id"],
            title=j["title"],
            company=j["company"],
            location=j.get("location", ""),
            link=j.get("link", ""),
            match_score=j.get("match_score", 0),
            skills_match_pct=j.get("skills_match_pct", 0),
            experience_match_pct=j.get("experience_match_pct", 0),
            strengths=j.get("strengths", []),
            weaknesses=j.get("weaknesses", []),
            missing_skills=j.get("missing_skills", [])
        )
        for j in final_state["final_jobs"]
    ]

    return MatchResponse(
        jobs=jobs,
        resume_name=resume.get("name", "Your Resume"),
        total_found=len(jobs)
    )