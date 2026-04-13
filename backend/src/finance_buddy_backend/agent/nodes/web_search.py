from finance_buddy_backend.agent.state import AgentState
from finance_buddy_backend.services.web_search_service import WebSearchService


def _build_trace_event(
    status: str,
    summary: str,
    result_count: int,
    query: str | None,
) -> dict[str, object]:
    return {
        "node_name": "web_search",
        "status": status,
        "summary": summary,
        "chunk_count": result_count,
        "retrieval_query": query,
    }


def build_web_search_node(web_search_service: WebSearchService):
    def web_search(state: AgentState) -> dict[str, object]:
        trace_events = state.get("trace_events", [])
        query = state.get("web_search_query") or state.get("question", "").strip()
        allowed_domains = state.get("allowed_web_domains", [])

        if state.get("web_search_decision") != "allowed":
            return {
                "web_results": [],
                "web_sources": [],
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        status="skipped",
                        summary="Web search node was skipped because policy did not allow it.",
                        result_count=0,
                        query=query,
                    )
                ],
            }

        try:
            web_results = web_search_service.search(
                query=query,
                allowed_domains=allowed_domains,
            )
        except Exception as exc:
            return {
                "web_results": [],
                "web_sources": [],
                "errors": state.get("errors", [])
                + [f"Web search failed with exception: {exc}"],
                "trace_events": trace_events
                + [
                    _build_trace_event(
                        status="failed",
                        summary=f"Approved public web search raised an exception: {exc}",
                        result_count=0,
                        query=query,
                    )
                ],
            }

        web_sources = [
            {
                "title": result.get("title"),
                "url": result.get("url"),
                "publisher": result.get("publisher"),
            }
            for result in web_results
        ]

        return {
            "web_results": web_results,
            "web_sources": web_sources,
            "trace_events": trace_events
            + [
                _build_trace_event(
                    status="completed",
                    summary="Approved public web search completed successfully.",
                    result_count=len(web_results),
                    query=query,
                )
            ],
        }

    return web_search
