from finance_buddy_backend.agent.state import AgentState


MIN_RELEVANT_SCORE = 0.35
STRONG_TOP_SCORE = 0.70
STRONG_SECOND_SCORE = 0.50


def _build_trace_event(
    state: AgentState,
    decision: str,
    retrieval_status: str | None,
    scores: list[float],
    summary: str,
) -> dict[str, object]:
    return {
        "node_name": "assess_internal_evidence",
        "status": "completed",
        "summary": summary,
        "retrieval_status": retrieval_status,
        "scores": scores,
        "decision": decision,
        "chunk_count": len(state.get("internal_chunks", [])),
    }


def assess_internal_evidence(state: AgentState) -> dict[str, object]:
    retrieval_status = state.get("internal_retrieval_status")
    trace_events = state.get("trace_events", [])

    if retrieval_status == "failed":
        return {
            "internal_evidence_status": "none",
            "errors": state.get("errors", [])
            + ["Internal retrieval failed, cannot assess evidence."],
            "trace_events": trace_events
            + [
                _build_trace_event(
                    state=state,
                    decision="none",
                    retrieval_status=retrieval_status,
                    scores=[],
                    summary="Internal retrieval failed before evidence assessment.",
                )
            ],
        }

    if retrieval_status == "empty":
        return {
            "internal_evidence_status": "none",
            "trace_events": trace_events
            + [
                _build_trace_event(
                    state=state,
                    decision="none",
                    retrieval_status=retrieval_status,
                    scores=[],
                    summary="No internal chunks were retrieved.",
                )
            ],
        }

    chunks = state.get("internal_chunks", [])
    if not chunks:
        return {
            "internal_evidence_status": "none",
            "trace_events": trace_events
            + [
                _build_trace_event(
                    state=state,
                    decision="none",
                    retrieval_status=retrieval_status,
                    scores=[],
                    summary="Retrieval status was non-empty, but no chunks were present.",
                )
            ],
        }

    scored_chunks = [
        chunk for chunk in chunks
        if isinstance(chunk.get("similarity_score"), (int, float))
    ]
    scored_chunks.sort(key=lambda chunk: float(chunk["similarity_score"]), reverse=True)
    scores = [float(chunk["similarity_score"]) for chunk in scored_chunks]

    if not scored_chunks:
        return {
            "internal_evidence_status": "insufficient",
            "errors": state.get("errors", [])
            + ["Retrieved chunks had no usable similarity scores."],
            "trace_events": trace_events
            + [
                _build_trace_event(
                    state=state,
                    decision="insufficient",
                    retrieval_status=retrieval_status,
                    scores=[],
                    summary="Retrieved chunks existed, but none had usable scores.",
                )
            ],
        }

    top_score = float(scored_chunks[0]["similarity_score"])
    second_score = (
        float(scored_chunks[1]["similarity_score"])
        if len(scored_chunks) > 1
        else 0.0
    )

    if top_score < MIN_RELEVANT_SCORE:
        return {
            "internal_evidence_status": "none",
            "trace_events": trace_events
            + [
                _build_trace_event(
                    state=state,
                    decision="none",
                    retrieval_status=retrieval_status,
                    scores=scores,
                    summary="Top retrieval score was below the minimum relevant threshold.",
                )
            ],
        }
    if top_score >= STRONG_TOP_SCORE:
        return {
            "internal_evidence_status": "sufficient",
            "trace_events": trace_events
            + [
                _build_trace_event(
                    state=state,
                    decision="sufficient",
                    retrieval_status=retrieval_status,
                    scores=scores,
                    summary="Top retrieval score was strong enough to answer internally.",
                )
            ],
        }

    if top_score < STRONG_TOP_SCORE and second_score >= STRONG_SECOND_SCORE:
        return {
            "internal_evidence_status": "sufficient",
            "trace_events": trace_events
            + [
                _build_trace_event(
                    state=state,
                    decision="sufficient",
                    retrieval_status=retrieval_status,
                    scores=scores,
                    summary="Multiple moderately strong chunks made internal evidence sufficient.",
                )
            ],
        }

    return {
        "internal_evidence_status": "insufficient",
        "trace_events": trace_events
        + [
            _build_trace_event(
                state=state,
                decision="insufficient",
                retrieval_status=retrieval_status,
                scores=scores,
                summary="Retrieved evidence was relevant but not strong enough to answer confidently.",
            )
        ],
    }
