from finance_buddy_backend.agent.state import AgentState


def validate_answer_policy(state: AgentState) -> dict[str, object]:
    answer = state.get("answer")
    answer_status = state.get("answer_status")
    final_sources = state.get("final_sources", [])
    web_sources = state.get("web_sources", [])
    trace_events = state.get("trace_events", [])
    answer_policy_flags = list(state.get("answer_policy_flags", []))
    requires_disclaimer = False

    if not isinstance(answer, str) or not answer.strip():
        answer_policy_flags.append("empty_answer")
        answer = (
            "I could not generate a grounded answer that passed policy validation. "
            "Please try again in a moment."
        )
        answer_status = "agent_failed"

    if answer_status == "answered_mixed_sources":
        requires_disclaimer = True
        if not web_sources:
            answer_policy_flags.append("mixed_answer_without_web_sources")
            answer_status = "generation_failed"
            answer = (
                "I could not complete a validated mixed-source answer because the public-source "
                "evidence was missing from the final response."
            )
        elif "approved public sources were used" not in answer.lower():
            answer = (
                f"{answer.rstrip()}\n\n"
                "Note: approved public web sources were used as supplemental evidence after "
                "internal retrieval was insufficient."
            )

    if answer_status in {"answered_internal", "answered_mixed_sources"} and not final_sources:
        answer_policy_flags.append("answer_without_sources")

    trace_event = {
        "node_name": "validate_answer_policy",
        "status": "completed",
        "summary": "Validated the final answer against the current Agent V1 policy rules.",
        "answer_status": answer_status,
        "source_count": len(final_sources),
        "requires_disclaimer": requires_disclaimer,
    }

    return {
        "answer": answer,
        "answer_status": answer_status,
        "answer_policy_flags": answer_policy_flags,
        "requires_disclaimer": requires_disclaimer,
        "trace_events": trace_events + [trace_event],
    }
