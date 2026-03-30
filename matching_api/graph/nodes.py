from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .state import AgentState
from services.retriever import retrieve_matching_jobs
import os
import logging

logger = logging.getLogger(__name__)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)


def retrieve_jobs(state: AgentState) -> AgentState:
    top_k = 20 + (state["retry_count"] * 10)
    try:
        jobs = retrieve_matching_jobs(
            user_id=state["user_id"],
            resume=state["resume"],
            top_k=top_k
        )
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        jobs = []
    return {**state, "retrieved_jobs": jobs}


RERANK_PROMPT = ChatPromptTemplate.from_template("""
You are an expert technical recruiter AI. Score each job against this resume.

RESUME SUMMARY:
- Skills: {skills}
- Experience: {experience}
- Education: {education}

JOBS TO SCORE:
{jobs}

Return ONLY a valid JSON array. No markdown, no code blocks, no explanation.
One object per job with this exact structure:
[
  {{
    "id": <job_id as integer>,
    "match_score": <0-100 integer>,
    "skills_match_pct": <0-100 integer>,
    "experience_match_pct": <0-100 integer>,
    "confidence": <0.0-1.0 float>,
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2"],
    "missing_skills": ["skill1", "skill2", "skill3"]
  }}
]
""")


def rerank_jobs(state: AgentState) -> AgentState:
    resume = state["resume"]

    if not state["retrieved_jobs"]:
        return {**state, "scored_jobs": [], "confidence": 0.0}

    jobs_summary = [
        {
            "id": j["id"],
            "title": j["title"],
            "company": j["company"],
            "description": (j.get("description") or "")[:400]
        }
        for j in state["retrieved_jobs"]
    ]

    try:
        chain = RERANK_PROMPT | llm | JsonOutputParser()
        scored = chain.invoke({
            "skills": (resume.get("skills_text") or "")[:400],
            "experience": (resume.get("experience_text") or "")[:400],
            "education": (resume.get("education_text") or "")[:200],
            "jobs": str(jobs_summary)
        })

        if not isinstance(scored, list):
            logger.warning(f"LLM returned non-list: {type(scored)}")
            scored = []

        avg_confidence = sum(
            j.get("confidence", 0.5) for j in scored
        ) / max(len(scored), 1)

    except Exception as e:
        logger.error(f"Rerank LLM call failed: {e}")
        scored = []
        avg_confidence = 0.0

    return {**state, "scored_jobs": scored, "confidence": avg_confidence}


def analyze_gaps(state: AgentState) -> AgentState:
    if not state["scored_jobs"]:
        return {**state, "final_jobs": []}

    job_lookup = {j["id"]: j for j in state["retrieved_jobs"]}

    final_jobs = []
    for scored_job in state["scored_jobs"]:
        try:
            job_id = scored_job.get("id")
            if job_id is None:
                continue
            raw_job = job_lookup.get(job_id, {})
            if not raw_job:
                continue
            final_jobs.append({
                **raw_job,
                **scored_job,
                "missing_skills": scored_job.get("missing_skills", [])
            })
        except Exception as e:
            logger.error(f"Gap merge failed for job: {e}")
            continue

    final_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return {**state, "final_jobs": final_jobs[:30]}


def should_retry(state: AgentState) -> str:
    if state["confidence"] < 0.5 and state["retry_count"] < 2:
        return "retry"
    return "continue"


def format_output(state: AgentState) -> AgentState:
    return state