from finance_buddy_backend.agent.state import AgentState
from finance_buddy_backend.services.retrieval_service import RetrievalService


def _build_trace_event(
    state: AgentState,
    status: str,
    retrieval_status: str,
    summary: str,
    retrieval_query: str,
    chunk_count: int,
) -> dict[str, object]:
    return {
        "node_name": "internal_retrieve",
        "status": status,
        "summary": summary,
        "retrieval_status": retrieval_status,
        "retrieval_query": retrieval_query,
        "chunk_count": chunk_count,
        "source_count": len(state.get("internal_sources", [])),
    }


def build_internal_retrieve_node(retrieval_service: RetrievalService):
    def internal_retrieve(state: AgentState) -> dict[str, object]:
        question = state.get("question", "").strip()
        trace_events = state.get("trace_events", [])

        if not question:
            return {
                "retrieval_query": "",
                "internal_retrieval_status": "empty",
                "internal_chunks": [],
                "internal_sources": [],
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        state=state,
                        status="completed",
                        retrieval_status="empty",
                        summary="No question was provided, so retrieval was skipped.",
                        retrieval_query="",
                        chunk_count=0,
                    )
                ],
            }

        try:
            retrieval_results = retrieval_service.retrieve_relevant_chunks(
                question,
                top_k=5,
            )

            if retrieval_results:
                sources_by_id: dict[object, dict[str, object]] = {}
                for chunk in retrieval_results:
                    source_id = chunk.get("source_id")
                    if source_id not in sources_by_id:
                        sources_by_id[source_id] = {
                            "source_id": source_id,
                            "title": chunk.get("source_title"),
                            "url": chunk.get("source_url"),
                            "publisher": chunk.get("source_publisher"),
                        }

                return {
                    "retrieval_query": question,
                    "internal_retrieval_status": "ok",
                    "internal_chunks": retrieval_results,
                    "internal_sources": list(sources_by_id.values()),
                    "trace_events": trace_events
                    + [
                        _build_trace_event(
                            state=state,
                            status="completed",
                            retrieval_status="ok",
                            summary="Retrieved internal evidence candidates successfully.",
                            retrieval_query=question,
                            chunk_count=len(retrieval_results),
                        )
                    ],
                }

            return {
                "retrieval_query": question,
                "internal_retrieval_status": "empty",
                "internal_chunks": [],
                "internal_sources": [],
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        state=state,
                        status="completed",
                        retrieval_status="empty",
                        summary="Internal retrieval completed but returned no chunks.",
                        retrieval_query=question,
                        chunk_count=0,
                    )
                ],
            }
        except Exception as exc:
            return {
                "retrieval_query": question,
                "internal_retrieval_status": "failed",
                "internal_chunks": [],
                "internal_sources": [],
                "errors": state.get("errors", [])
                + [f"Internal retrieval failed with exception: {exc}"],
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        state=state,
                        status="failed",
                        retrieval_status="failed",
                        summary="Internal retrieval raised an exception.",
                        retrieval_query=question,
                        chunk_count=0,
                    )
                ],
            }

    return internal_retrieve
