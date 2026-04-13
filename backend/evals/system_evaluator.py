from time import perf_counter, sleep

from sqlalchemy.orm import Session

from finance_buddy_backend.services.agent_chat_service import AgentChatService
from finance_buddy_backend.services.chat_service import ChatService

from .models import (
    EvaluationExample,
    EvaluationManifest,
    SystemAggregateEvaluationResult,
    SystemPerExampleResult,
    SystemSourceResult,
)


class SystemEvaluator:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.chat_service = ChatService(db)
        self.agent_chat_service = AgentChatService(db)

    def evaluate_system(
        self,
        *,
        system_name: str,
        dataset: list[EvaluationExample],
        manifest: EvaluationManifest,
        explanation_level: str = "basic",
        allow_web_search: bool = False,
        sleep_seconds: float = 0.0,
    ) -> SystemAggregateEvaluationResult:
        per_example_results: list[SystemPerExampleResult] = []

        for index, example in enumerate(dataset):
            per_example_results.append(
                self._evaluate_example(
                    system_name=system_name,
                    example=example,
                    explanation_level=explanation_level,
                    allow_web_search=allow_web_search,
                )
            )

            if sleep_seconds > 0 and index < len(dataset) - 1:
                sleep(sleep_seconds)

        return SystemAggregateEvaluationResult(
            dataset_name=manifest.dataset_name,
            dataset_version=manifest.dataset_version,
            system_name=system_name,
            total_examples=len(dataset),
            aggregate_metrics=self._aggregate_metrics(per_example_results),
            per_example_results=per_example_results,
        )

    def _evaluate_example(
        self,
        *,
        system_name: str,
        example: EvaluationExample,
        explanation_level: str,
        allow_web_search: bool,
    ) -> SystemPerExampleResult:
        started_at = perf_counter()

        if system_name == "baseline_rag":
            response = self.chat_service.create_chat_response(
                message=example.question,
                explanation_level=explanation_level,
            )
            answer_status = None
            trace_events: list[dict[str, object]] = []
        elif system_name == "agentic_v1":
            response = self.agent_chat_service.create_chat_response(
                message=example.question,
                explanation_level=explanation_level,
                allow_web_search=allow_web_search,
            )
            answer_status = getattr(response, "message_id", None)
            trace_events = [
                event.model_dump() if hasattr(event, "model_dump") else event
                for event in getattr(response, "trace_events", [])
            ]
            answer_status = None
            if getattr(response, "trace_events", None):
                final_trace = response.trace_events[-1]
                answer_status = final_trace.answer_status
        else:
            raise ValueError(f"Unsupported system_name: {system_name}")

        latency_ms = (perf_counter() - started_at) * 1000.0
        sources = [
            SystemSourceResult(
                title=source.title,
                url=source.url,
                publisher=source.publisher,
            )
            for source in response.sources
        ]
        expected_titles = set(example.expected_source_titles)
        matched_expected_source_count = sum(
            1 for source in sources if source.title in expected_titles
        )
        used_web_search = any(
            event.get("node_name") == "web_search" and event.get("status") == "completed"
            for event in trace_events
            if isinstance(event, dict)
        )

        return SystemPerExampleResult(
            question_id=example.question_id,
            question=example.question,
            system_name=system_name,
            answer=response.answer,
            answer_status=answer_status,
            latency_ms=latency_ms,
            source_count=len(sources),
            sources=sources,
            matched_expected_source_count=matched_expected_source_count,
            used_web_search=used_web_search,
            trace_event_count=len(trace_events),
            expected_source_titles=example.expected_source_titles,
            expected_answer_points=example.expected_answer_points,
        )

    def _aggregate_metrics(
        self,
        per_example_results: list[SystemPerExampleResult],
    ) -> dict[str, float]:
        if not per_example_results:
            return {
                "avg_latency_ms": 0.0,
                "source_hit_rate": 0.0,
                "avg_source_count": 0.0,
                "web_usage_rate": 0.0,
            }

        total_examples = len(per_example_results)
        source_hit_count = sum(
            1 for result in per_example_results if result.matched_expected_source_count > 0
        )
        total_latency_ms = sum(result.latency_ms for result in per_example_results)
        total_source_count = sum(result.source_count for result in per_example_results)
        web_usage_count = sum(
            1 for result in per_example_results if result.used_web_search
        )

        return {
            "avg_latency_ms": total_latency_ms / total_examples,
            "source_hit_rate": source_hit_count / total_examples,
            "avg_source_count": total_source_count / total_examples,
            "web_usage_rate": web_usage_count / total_examples,
        }
