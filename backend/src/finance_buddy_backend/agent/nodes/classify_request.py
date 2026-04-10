from finance_buddy_backend.agent.state import AgentState


def classify_request(state: AgentState) -> dict[str, object]:
    question = state.get("question", "").strip()

    if not question:
        return {
            "request_type": "unsupported",
            "request_type_confidence": 1.0,
            "errors": state.get("errors", []) + ["No question provided."],
        }

    # V1 uses simple heuristics so routing stays explicit and easy to debug.
    document_keywords = [
        "invoice",
        "bill",
        "receipt",
        "factura",
        "pdf",
        "document",
        "file",
        "upload",
    ]
    lowered_question = question.lower()

    if any(keyword in lowered_question for keyword in document_keywords):
        return {
            "request_type": "document_analysis",
            "request_type_confidence": 0.9,
        }

    return {
        "request_type": "knowledge_qa",
        "request_type_confidence": 0.8,
    }
