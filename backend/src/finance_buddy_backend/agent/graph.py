from langgraph.graph import StateGraph, END, START  

from finance_buddy_backend.services.generation_service import GenerationService
from finance_buddy_backend.services.retrieval_service import RetrievalService

from .nodes.assess_internal_evidence import assess_internal_evidence
from .nodes.classify_request import classify_request
from .nodes.generate_internal_only_response import (
    build_generate_internal_only_response_node,
)
from .nodes.internal_retrieve import build_internal_retrieve_node
from .nodes.load_request import load_request
from .state import AgentState


def route_after_classify_request(state: AgentState) -> str:
    return state.get("request_type", "unsupported")


def route_after_assess_internal_evidence(state: AgentState) -> str:
    return state.get("internal_evidence_status", "none")


def build_agent_graph(retrieval_service: RetrievalService, generation_service: GenerationService):

    graph = StateGraph(AgentState)
    internal_retrieve_node = build_internal_retrieve_node(retrieval_service)
    generate_internal_only_response_node = (
        build_generate_internal_only_response_node(generation_service)
    )

    # Define the nodes.
    graph.add_node("load_request", load_request)
    graph.add_node("classify_request", classify_request)
    graph.add_node("internal_retrieve", internal_retrieve_node)
    graph.add_node("assess_internal_evidence", assess_internal_evidence)
    graph.add_node(
        "generate_internal_only_response",
        generate_internal_only_response_node,
    )

    # Define the edges.
    graph.add_edge(START, "load_request")
    graph.add_edge("load_request", "classify_request")
    graph.add_conditional_edges(
        "classify_request",
        route_after_classify_request,
        {
            "knowledge_qa": "internal_retrieve",
            "document_analysis": "generate_internal_only_response",
            "unsupported": "generate_internal_only_response",
        },
    )
    graph.add_edge("internal_retrieve", "assess_internal_evidence")
    graph.add_conditional_edges(
        "assess_internal_evidence",
        route_after_assess_internal_evidence,
        {
            "sufficient": "generate_internal_only_response",
            "insufficient": "generate_internal_only_response",
            "none": "generate_internal_only_response",
        },
    )
    graph.add_edge("generate_internal_only_response", END)

    return graph.compile()
