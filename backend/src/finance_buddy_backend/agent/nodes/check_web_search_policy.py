from finance_buddy_backend.agent.state import AgentState
from finance_buddy_backend.core.config import settings


def _build_trace_event(
    decision: str,
    summary: str,
    reason: str,
    allowed_domain_count: int,
) -> dict[str, object]:
    return {
        "node_name": "check_web_search_policy",
        "status": "completed",
        "summary": summary,
        "decision": decision,
        "source_count": allowed_domain_count,
        "policy_reason": reason,
    }


def check_web_search_policy(state: AgentState) -> dict[str, object]:
    trace_events = state.get("trace_events", [])
    request_type = state.get("request_type")
    internal_evidence_status = state.get("internal_evidence_status")
    web_access_mode = state.get("web_access_mode", "disabled")
    user_allows_web_search = state.get("user_allows_web_search", False)
    allowed_domains = state.get("allowed_web_domains", [])
    question = state.get("question", "").strip()

    if request_type != "knowledge_qa":
        reason = "Web search is only available for knowledge questions in Agent V1."
        return {
            "web_search_decision": "not_allowed",
            "web_search_policy_reason": reason,
            "trace_events": trace_events
            + [
                _build_trace_event(
                    decision="not_allowed",
                    summary="Web search was blocked because the request type is not eligible.",
                    reason=reason,
                    allowed_domain_count=len(allowed_domains),
                )
            ],
        }

    if internal_evidence_status == "sufficient":
        reason = "Internal evidence is already sufficient, so web search is not needed."
        return {
            "web_search_decision": "not_needed",
            "web_search_policy_reason": reason,
            "trace_events": trace_events
            + [
                _build_trace_event(
                    decision="not_needed",
                    summary="Web search was skipped because internal evidence was sufficient.",
                    reason=reason,
                    allowed_domain_count=len(allowed_domains),
                )
            ],
        }

    if not question:
        reason = "No question was provided for web search."
        return {
            "web_search_decision": "not_allowed",
            "web_search_policy_reason": reason,
            "trace_events": trace_events
            + [
                _build_trace_event(
                    decision="not_allowed",
                    summary="Web search was blocked because the question was empty.",
                    reason=reason,
                    allowed_domain_count=len(allowed_domains),
                )
            ],
        }

    if web_access_mode == "disabled":
        reason = "Web access is disabled by agent policy."
        return {
            "web_search_decision": "not_allowed",
            "web_search_policy_reason": reason,
            "trace_events": trace_events
            + [
                _build_trace_event(
                    decision="not_allowed",
                    summary="Web search was blocked by the configured agent web access mode.",
                    reason=reason,
                    allowed_domain_count=len(allowed_domains),
                )
            ],
        }

    if settings.agent_require_web_search_consent and not user_allows_web_search:
        reason = "The request did not authorize web search."
        return {
            "web_search_decision": "not_allowed",
            "web_search_policy_reason": reason,
            "trace_events": trace_events
            + [
                _build_trace_event(
                    decision="not_allowed",
                    summary="Web search was blocked because the user did not authorize it.",
                    reason=reason,
                    allowed_domain_count=len(allowed_domains),
                )
            ],
        }

    if not allowed_domains:
        reason = "No approved public domains are configured for web search."
        return {
            "web_search_decision": "not_allowed",
            "web_search_policy_reason": reason,
            "trace_events": trace_events
            + [
                _build_trace_event(
                    decision="not_allowed",
                    summary="Web search was blocked because no approved domains are configured.",
                    reason=reason,
                    allowed_domain_count=0,
                )
            ],
        }

    reason = "Web search is allowed as a fallback because internal evidence was insufficient."
    return {
        "web_search_decision": "allowed",
        "web_search_policy_reason": reason,
        "web_search_query": question,
        "trace_events": trace_events
        + [
            _build_trace_event(
                decision="allowed",
                summary="Web search was approved as a constrained fallback step.",
                reason=reason,
                allowed_domain_count=len(allowed_domains),
            )
        ],
    }
