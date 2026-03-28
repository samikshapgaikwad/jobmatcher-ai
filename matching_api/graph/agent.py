from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import retrieve_jobs, rerank_jobs, analyze_gaps, format_output
from .edges import route_after_rerank, increment_retry

def build_agent() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("retrieve", retrieve_jobs)
    graph.add_node("rerank", rerank_jobs)
    graph.add_node("increment_retry", increment_retry)  # bumps retry count
    graph.add_node("analyze_gaps", analyze_gaps)
    graph.add_node("output", format_output)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "rerank")

    graph.add_conditional_edges(
        "rerank",
        route_after_rerank,
        {
            "retry": "increment_retry",
            "continue": "analyze_gaps"
        }
    )

    # After incrementing, loop back to retrieve with broader top_k
    graph.add_edge("increment_retry", "retrieve")
    graph.add_edge("analyze_gaps", "output")
    graph.add_edge("output", END)

    return graph.compile()

matching_agent = build_agent()