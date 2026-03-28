from typing import TypedDict, Optional
from langgraph.graph import add_messages

class AgentState(TypedDict):
    user_id: str
    resume: dict              # raw resume data from Supabase
    retrieved_jobs: list      # top-K from pgvector
    scored_jobs: list         # after LLM reranking
    final_jobs: list          # after gap analysis, ready for API response
    confidence: float         # agent self-assessed confidence 0-1
    retry_count: int          # how many times retrieval was broadened
    error: Optional[str]