from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .state import AgentState
from services.retriever import retrieve_matching_jobs
import os

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)

# ── Node 1: Vector Retrieval ──────────────────────────────────────────────────
def retrieve_jobs(state: AgentState) -> AgentState:
    top_k = 20 + (state["retry_count"] * 10)
    jobs = retrieve_matching_jobs(
        user_id=state["user_id"],
        resume=state["resume"],
        top_k=top_k
    )
    return {**state, "retrieved_jobs": jobs}


# ── Node 2: LLM Reranker ─────────────────────────────────────────────────────
RERANK_PROMPT = ChatPromptTemplate.from_template("""
You are an expert technical recruiter AI. Score each job against this resume.

RESUME SUMMARY:
- Skills: {skills}
- Experience: {experience}
- Education: {education}

JOBS TO SCORE (JSON array):
{jobs}

Return a JSON array with this exact structure — one object per job:
[
  {{
    "id": <job_id>,
    "match_score": <0-100>,
    "skills_match_pct": <0-100>,
    "experience_match_pct": <0-100>,
    "confidence": <0.0-1.0>,
    "strengths": ["reason1", "reason2", "reason3"],
    "weaknesses": ["gap1", "gap2"],
    "missing_skills": ["skill1", "skill2"]
  }}
]

Include missing_skills directly here — max 4 skills per job.
Only return the JSON array, no explanation.
""")

def rerank_jobs(state: AgentState) -> AgentState:
    """
    Single LLM call scores AND extracts gaps for all jobs at once.
    This replaces the separate gap_analyzer node — much faster.
    """
    resume = state["resume"]
    jobs_summary = [
        {
            "id": j["id"],
            "title": j["title"],
            "company": j["company"],
            "description": (j.get("description") or "")[:500]
        }
        for j in state["retrieved_jobs"]
    ]

    chain = RERANK_PROMPT | llm | JsonOutputParser()
    scored = chain.invoke({
        "skills": resume.get("skills_text", "")[:500],
        "experience": resume.get("experience_text", "")[:500],
        "education": resume.get("education_text", "")[:300],
        "jobs": str(jobs_summary)
    })

    avg_confidence = sum(
        j.get("confidence", 0) for j in scored
    ) / max(len(scored), 1)

    return {**state, "scored_jobs": scored, "confidence": avg_confidence}


# ── Node 3: Gap Analyzer (now just merges data) ───────────────────────────────
def analyze_gaps(state: AgentState) -> AgentState:
    """
    No more individual LLM calls — gaps already included in rerank step.
    Just merges scored data with raw job data.
    """
    job_lookup = {j["id"]: j for j in state["retrieved_jobs"]}

    final_jobs = []
    for scored_job in state["scored_jobs"]:
        job_id = scored_job["id"]
        raw_job = job_lookup.get(job_id, {})
        final_jobs.append({
            **raw_job,
            **scored_job,
            "missing_skills": scored_job.get("missing_skills", [])
        })

    final_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return {**state, "final_jobs": final_jobs[:10]}


# ── Node 4: Router ────────────────────────────────────────────────────────────
def should_retry(state: AgentState) -> str:
    if state["confidence"] < 0.5 and state["retry_count"] < 2:
        return "retry"
    return "continue"


# ── Node 5: Format Output ─────────────────────────────────────────────────────
def format_output(state: AgentState) -> AgentState:
    return state