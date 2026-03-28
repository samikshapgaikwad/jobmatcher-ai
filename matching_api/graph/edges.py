from .state import AgentState

def route_after_rerank(state: AgentState) -> str:
    """
    Conditional routing logic after reranking.
    
    - If average confidence is too low AND we haven't retried twice → go back to retrieve with broader search
    - Otherwise → proceed to gap analysis
    
    This is what makes the agent 'agentic' — it self-evaluates
    and decides whether its results are good enough.
    """
    confidence = state.get("confidence", 0.0)
    retry_count = state.get("retry_count", 0)

    if confidence < 0.5 and retry_count < 2:
        print(f"[Router] Low confidence ({confidence:.2f}), retrying... (attempt {retry_count + 1})")
        # Increment retry count so retriever broadens the search
        return "retry"

    print(f"[Router] Confidence OK ({confidence:.2f}), proceeding to gap analysis.")
    return "continue"


def increment_retry(state: AgentState) -> AgentState:
    """
    Called when routing back to retrieve.
    Increments retry_count so the retriever knows to broaden top_k.
    """
    return {
        **state,
        "retry_count": state.get("retry_count", 0) + 1
    }