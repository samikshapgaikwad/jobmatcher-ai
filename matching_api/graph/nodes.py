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
    """
    Queries pgvector with resume embeddings.
    Broadens search on retry (increases top_k).
    """
    top_k = 20 + (state["retry_count"] * 10)  # 20 → 30 → 40 on retries
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

For each job, return a JSON array with this exact structure:
[
  {{
    "id": <job_id>,
    "match_score": <0-100>,
    "skills_match_pct": <0-100>,
    "experience_match_pct": <0-100>,
    "confidence": <0.0-1.0>,
    "strengths": ["reason1", "reason2", "reason3"],
    "weaknesses": ["gap1", "gap2"]
  }}
]

Be precise. Only return the JSON array, no explanation.
""")

def rerank_jobs(state: AgentState) -> AgentState:
    resume = state["resume"]
    jobs_summary = [
        {"id": j["id"], "title": j["title"], "company": j["company"],
         "requirements": j.get("requirements", "")[:800]}
        for j in state["retrieved_jobs"]
    ]
    chain = RERANK_PROMPT | llm | JsonOutputParser()
    scored = chain.invoke({
        "skills": resume.get("skills_text", ""),
        "experience": resume.get("experience_text", ""),
        "education": resume.get("education_text", ""),
        "jobs": str(jobs_summary)
    })
    avg_confidence = sum(j.get("confidence", 0) for j in scored) / max(len(scored), 1)
    return {**state, "scored_jobs": scored, "confidence": avg_confidence}


# ── Node 3: Gap Analyzer ──────────────────────────────────────────────────────
GAP_PROMPT = ChatPromptTemplate.from_template("""
You are a technical skills gap analyzer.

Resume skills: {resume_skills}
Job title: {job_title}
Job requirements: {job_requirements}

Return ONLY a JSON array of missing skill strings (max 5):
["skill1", "skill2", "skill3"]

If no gaps, return: []
""")

def analyze_gaps(state: AgentState) -> AgentState:
    resume = state["resume"]
    job_lookup = {j["id"]: j for j in state["retrieved_jobs"]}
    gap_chain = GAP_PROMPT | llm | JsonOutputParser()

    final_jobs = []
    for scored_job in state["scored_jobs"]:
        job_id = scored_job["id"]
        raw_job = job_lookup.get(job_id, {})
        missing = gap_chain.invoke({
            "resume_skills": resume.get("skills_text", ""),
            "job_title": raw_job.get("title", ""),
            "job_requirements": raw_job.get("requirements", "")[:600]
        })
        final_jobs.append({
            **raw_job,
            **scored_job,
            "missing_skills": missing if isinstance(missing, list) else []
        })

    # Sort by match_score descending
    final_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return {**state, "final_jobs": final_jobs[:10]}


# ── Node 4: Router (conditional) ─────────────────────────────────────────────
def should_retry(state: AgentState) -> str:
    """
    Conditional edge: retry retrieval if confidence is low
    and we haven't exceeded max retries.
    """
    if state["confidence"] < 0.5 and state["retry_count"] < 2:
        return "retry"
    return "continue"


# ── Node 5: Format Output ─────────────────────────────────────────────────────
def format_output(state: AgentState) -> AgentState:
    """Final node — state is already clean, just passes through."""
    return state