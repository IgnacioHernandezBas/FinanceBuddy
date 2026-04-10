from finance_buddy_backend.agent.state import AgentState
from finance_buddy_backend.services.generation_service import GenerationService


def _build_trace_event(
    answer_status: str,
    summary: str,
    request_type: str | None,
    internal_evidence_status: str | None,
    source_count: int,
) -> dict[str, object]:
    return {
        "node_name": "generate_internal_only_response",
        "status": "completed",
        "summary": summary,
        "answer_status": answer_status,
        "request_type": request_type,
        "internal_evidence_status": internal_evidence_status,
        "source_count": source_count,
    }


def build_generate_internal_only_response_node(
    generation_service: GenerationService,
):
    def generate_internal_only_response(state: AgentState) -> dict[str, object]:
        request_type = state.get("request_type")
        internal_evidence_status = state.get("internal_evidence_status")
        internal_chunks = state.get("internal_chunks", [])
        internal_sources = state.get("internal_sources", [])
        question = state.get("question", "").strip()
        explanation_level = state.get("explanation_level", "basic")
        trace_events = state.get("trace_events", [])

        if request_type == "document_analysis":
            return {
                "answer": (
                    "Document analysis is not implemented in this agent version yet. "
                    "Please use the grounded chat flow for supported knowledge questions."
                ),
                "answer_status": "insufficient_internal_only",
                "final_sources": [],
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        answer_status="insufficient_internal_only",
                        summary="Document analysis requests are not implemented in Agent V1.",
                        request_type=request_type,
                        internal_evidence_status=internal_evidence_status,
                        source_count=0,
                    )
                ],
            }

        if request_type == "unsupported":
            return {
                "answer": (
                    "This request is outside the currently supported FinanceBuddy scope. "
                    "Please ask a financial education question grounded in the trusted sources."
                ),
                "answer_status": "insufficient_internal_only",
                "final_sources": [],
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        answer_status="insufficient_internal_only",
                        summary="The request was outside the supported FinanceBuddy scope.",
                        request_type=request_type,
                        internal_evidence_status=internal_evidence_status,
                        source_count=0,
                    )
                ],
            }

        if internal_evidence_status != "sufficient" or not internal_chunks:
            return {
                "answer": (
                    "I could not find enough supporting evidence in the trusted internal "
                    "sources to answer confidently."
                ),
                "answer_status": "insufficient_internal_only",
                "final_sources": internal_sources,
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        answer_status="insufficient_internal_only",
                        summary="Internal evidence was not strong enough to generate a confident answer.",
                        request_type=request_type,
                        internal_evidence_status=internal_evidence_status,
                        source_count=len(internal_sources),
                    )
                ],
            }

        try:
            answer = generation_service.generate_response(
                question=question,
                explanation_level=explanation_level,
                retrieved_chunks=internal_chunks,
            )
        except Exception as exc:
            return {
                "answer": (
                    "I could not generate a grounded answer at this time. "
                    "Please try again in a moment."
                ),
                "answer_status": "generation_failed",
                "final_sources": internal_sources,
                "errors": state.get("errors", [])
                + [f"Internal-only response generation failed with exception: {exc}"],
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        answer_status="generation_failed",
                        summary="Grounded generation raised an exception.",
                        request_type=request_type,
                        internal_evidence_status=internal_evidence_status,
                        source_count=len(internal_sources),
                    )
                ],
            }

        if not answer or not answer.strip():
            return {
                "answer": (
                    "I could not generate a grounded answer at this time. "
                    "Please try again in a moment."
                ),
                "answer_status": "generation_failed",
                "final_sources": internal_sources,
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        answer_status="generation_failed",
                        summary="Grounded generation returned an empty answer.",
                        request_type=request_type,
                        internal_evidence_status=internal_evidence_status,
                        source_count=len(internal_sources),
                    )
                ],
            }

        return {
            "answer": answer,
            "answer_status": "answered_internal",
            "final_sources": internal_sources,
            "trace_events": trace_events
            + [
                _build_trace_event(
                    answer_status="answered_internal",
                    summary="Generated an internal-only grounded answer successfully.",
                    request_type=request_type,
                    internal_evidence_status=internal_evidence_status,
                    source_count=len(internal_sources),
                )
            ],
        }

    return generate_internal_only_response
