from finance_buddy_backend.agent.state import AgentState


def load_request(state: AgentState) -> dict[str, object]:
    return {
        "conversation_id": state.get("conversation_id"),
        "user_message_id": state.get("user_message_id"),
        "question": state.get("question", "").strip(),
        "explanation_level": state.get("explanation_level", "basic"),
        "user_allows_web_search": state.get("user_allows_web_search", False),
        "web_access_mode": state.get("web_access_mode", "disabled"),
        "allowed_web_domains": state.get("allowed_web_domains", []),
        "request_type": None,
        "request_type_confidence": None,
        "web_search_policy_reason": None,
        "retrieval_query": None,
        "internal_retrieval_status": None,
        "internal_chunks": [],
        "internal_sources": [],
        "internal_evidence_status": None,
        "web_search_decision": None,
        "web_search_query": None,
        "web_results": [],
        "web_sources": [],
        "final_sources": [],
        "answer": None,
        "answer_status": None,
        "answer_policy_flags": [],
        "requires_disclaimer": False,
        "trace_events": [],
        "errors": state.get("errors", []),
    }
