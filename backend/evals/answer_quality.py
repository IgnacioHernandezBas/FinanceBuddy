import re
import unicodedata

from google.genai.types import GenerateContentConfig
from pydantic import BaseModel

from finance_buddy_backend.services.generation_service import GenerationService

SUCCESS_ANSWER_STATUSES = {"answered_internal", "answered_mixed_sources", "generated"}


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", without_accents)


def match_facts(answer: str, expected_facts: list[str]) -> list[str]:
    normalized_answer = _normalize(answer)
    matched: list[str] = []
    for fact in expected_facts:
        alternatives = [_normalize(option.strip()) for option in fact.split("|") if option.strip()]
        # Whole-word matching so "app" does not match "approved" and "directo" not "indirecto".
        if any(
            re.search(rf"(?<!\w){re.escape(option)}(?!\w)", normalized_answer)
            for option in alternatives
        ):
            matched.append(fact)
    return matched


class _PointVerdict(BaseModel):
    point_index: int
    covered: bool


class _JudgeOutput(BaseModel):
    verdicts: list[_PointVerdict]


class AnswerJudge:
    def __init__(self, generation_service: GenerationService) -> None:
        self.generation_service = generation_service

    def judge_points(
        self,
        question: str,
        answer: str,
        expected_points: list[str],
    ) -> list[bool]:
        points_text = "\n".join(
            f"{index}. {point}" for index, point in enumerate(expected_points)
        )
        prompt = (
            "You are grading an answer from a Spanish tax education assistant.\n"
            "For each expected point, decide whether the answer explicitly conveys it. "
            "Paraphrases count. A point is NOT covered if the answer says the information "
            "is unavailable, gives a different value (date, figure, deadline), or only "
            "mentions the topic without the stated fact. Points that describe how the "
            "answer should be framed (for example, attributing it to the Agencia Tributaria) "
            "are covered if the answer does so.\n\n"
            f"Question:\n{question}\n\n"
            f"Answer:\n{answer}\n\n"
            f"Expected points:\n{points_text}\n\n"
            "Return one verdict per expected point, using its index."
        )
        response = self.generation_service.generate_content_with_retry(
            prompt,
            config=GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=_JudgeOutput,
            ),
        )
        output = _JudgeOutput.model_validate_json(response.text or "")
        covered_by_index = {verdict.point_index: verdict.covered for verdict in output.verdicts}
        return [covered_by_index.get(index, False) for index in range(len(expected_points))]
