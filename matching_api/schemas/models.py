from pydantic import BaseModel
from typing import List, Optional

class MatchRequest(BaseModel):
    user_id: str
    top_k: int = 30

class JobMatch(BaseModel):
    id: int
    title: str
    company: str
    location: str
    link: str
    match_score: int           # 0-100
    skills_match_pct: int
    experience_match_pct: int
    strengths: List[str]       # "Why You Match" bullets
    weaknesses: List[str]      # "Areas to Improve" bullets
    missing_skills: List[str]  # skill gap list

class MatchResponse(BaseModel):
    jobs: List[JobMatch]
    resume_name: str
    total_found: int