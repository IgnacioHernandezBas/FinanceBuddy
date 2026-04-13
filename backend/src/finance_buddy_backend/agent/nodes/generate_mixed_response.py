from finance_buddy_backend.agent.state import AgentState
from finance_buddy_backend.services.generation_service import GenerationService


def _build_trace_event(
    answer_status: str,
    summary: str,
    internal_source_count: int,
    web_source_count: int,
) -> dict[str, object]:
    return {
        "node_name": "generate_mixed_response",
        "status": "completed",
        "summary": summary,
        "answer_status": answer_status,
        "source_count": internal_source_count + web_source_count,
        "web_source_count": web_source_count,
    }


def build_generate_mixed_response_node(
    generation_service: GenerationService,
):
    def generate_mixed_response(state: AgentState) -> dict[str, object]:
        question = state.get("question", "").strip()
        explanation_level = state.get("explanation_level", "basic")
        internal_chunks = state.get("internal_chunks", [])
        internal_sources = state.get("internal_sources", [])
        web_results = state.get("web_results", [])
        web_sources = state.get("web_sources", [])
        trace_events = state.get("trace_events", [])

        if not web_results:
            return {
                "answer": (
                    "I could not find enough supporting evidence in the trusted internal "
                    "sources, and no approved public web results were available to improve the answer."
                ),
                "answer_status": "insufficient_internal_only",
                "final_sources": internal_sources,
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        answer_status="insufficient_internal_only",
                        summary="Mixed-source generation fell back because no web results were available.",
                        internal_source_count=len(internal_sources),
                        web_source_count=0,
                    )
                ],
            }

        try:
            answer = generation_service.generate_mixed_response(
                question=question,
                explanation_level=explanation_level,
                internal_chunks=internal_chunks,
                web_results=web_results,
            )
        except Exception as exc:
            return {
                "answer": (
                    "I could not generate a mixed-source answer at this time. "
                    "Please try again in a moment."
                ),
                "answer_status": "generation_failed",
                "final_sources": internal_sources + web_sources,
                "errors": state.get("errors", [])
                + [f"Mixed response generation failed with exception: {exc}"],
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        answer_status="generation_failed",
                        summary="Mixed-source generation raised an exception.",
                        internal_source_count=len(internal_sources),
                        web_source_count=len(web_sources),
                    )
                ],
            }

        if not answer or not answer.strip():
            return {
                "answer": (
                    "I could not generate a mixed-source answer at this time. "
                    "Please try again in a moment."
                ),
                "answer_status": "generation_failed",
                "final_sources": internal_sources + web_sources,
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        answer_status="generation_failed",
                        summary="Mixed-source generation returned an empty answer.",
                        internal_source_count=len(internal_sources),
                        web_source_count=len(web_sources),
                    )
                ],
            }

        return {
            "answer": answer,
            "answer_status": "answered_mixed_sources",
            "final_sources": internal_sources + web_sources,
            "trace_events": trace_events
            + [
                _build_trace_event(
                    answer_status="answered_mixed_sources",
                    summary="Generated a mixed-source answer using internal and approved public evidence.",
                    internal_source_count=len(internal_sources),
                    web_source_count=len(web_sources),
                )
            ],
        }

    return generate_mixed_response
