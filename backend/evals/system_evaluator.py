from time import perf_counter, sleep

from sqlalchemy.orm import Session

from finance_buddy_backend.services.agent_chat_service import AgentChatService
from finance_buddy_backend.services.chat_service import ChatService

from .answer_quality import SUCCESS_ANSWER_STATUSES, AnswerJudge, match_facts
from .models import (
    EvaluationExample,
    EvaluationManifest,
    SystemAggregateEvaluationResult,
    SystemPerExampleResult,
    SystemSourceResult,
)

REVIEW_DISAGREEMENT_THRESHOLD = 0.5


class SystemEvaluator:
    def __init__(self, db: Session, judge: AnswerJudge | None = None) -> None:
        self.db = db
        self.chat_service = ChatService(db)
        self.agent_chat_service = AgentChatService(db)
        self.judge = judge

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
            stored_message = self.chat_service.conversation_repository.get_message_by_id(
                response.message_id
            )
            answer_status = stored_message.answer_status if stored_message else None
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

        answer_success = answer_status in SUCCESS_ANSWER_STATUSES
        matched_facts = match_facts(response.answer, example.expected_facts)
        fact_recall = (
            len(matched_facts) / len(example.expected_facts)
            if example.expected_facts
            else None
        )

        judge_point_verdicts: list[bool] = []
        judge_point_coverage: float | None = None
        judge_error: str | None = None
        if self.judge is not None and example.expected_answer_points:
            if answer_success:
                try:
                    judge_point_verdicts = self.judge.judge_points(
                        question=example.question,
                        answer=response.answer,
                        expected_points=example.expected_answer_points,
                    )
                except Exception as exc:
                    judge_error = f"{type(exc).__name__}: {exc}"
            else:
                judge_point_verdicts = [False] * len(example.expected_answer_points)
            if judge_point_verdicts:
                judge_point_coverage = sum(judge_point_verdicts) / len(judge_point_verdicts)

        needs_review = (
            fact_recall is not None
            and judge_point_coverage is not None
            and abs(fact_recall - judge_point_coverage) >= REVIEW_DISAGREEMENT_THRESHOLD
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
            answer_success=answer_success,
            expected_facts=example.expected_facts,
            matched_facts=matched_facts,
            fact_recall=fact_recall,
            judge_point_verdicts=judge_point_verdicts,
            judge_point_coverage=judge_point_coverage,
            judge_error=judge_error,
            needs_review=needs_review,
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
                "answer_success_rate": 0.0,
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

        metrics = {
            "avg_latency_ms": total_latency_ms / total_examples,
            "source_hit_rate": source_hit_count / total_examples,
            "avg_source_count": total_source_count / total_examples,
            "web_usage_rate": web_usage_count / total_examples,
            "answer_success_rate": sum(
                1 for result in per_example_results if result.answer_success
            ) / total_examples,
        }

        fact_recalls = [
            result.fact_recall for result in per_example_results if result.fact_recall is not None
        ]
        if fact_recalls:
            metrics["fact_recall"] = sum(fact_recalls) / len(fact_recalls)

        if self.judge is not None:
            coverages = [
                result.judge_point_coverage
                for result in per_example_results
                if result.judge_point_coverage is not None
            ]
            if coverages:
                metrics["judge_point_coverage"] = sum(coverages) / len(coverages)
            metrics["judge_error_count"] = float(
                sum(1 for result in per_example_results if result.judge_error)
            )
            metrics["needs_review_count"] = float(
                sum(1 for result in per_example_results if result.needs_review)
            )

        return metrics
