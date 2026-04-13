from google import genai
from finance_buddy_backend.core.config import settings

class GenerationService:
    def __init__(self)->None:
         self.gemini_client = genai.Client(api_key=settings.gemini_api_key)

    def generate_response(
            self,
            question: str,
            explanation_level: str,
            retrieved_chunks: list[dict[str, int | float | str | None]],
        ) -> str:
            if not retrieved_chunks:
                return "I could not find enough supporting evidence in the trusted sources to answer confidently."

            prompt = self._build_prompt(
                question=question,
                explanation_level=explanation_level,
                retrieved_chunks=retrieved_chunks,
            )

            response = self.gemini_client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt
                
            )

            return response.text

    def generate_mixed_response(
            self,
            question: str,
            explanation_level: str,
            internal_chunks: list[dict[str, int | float | str | None]],
            web_results: list[dict[str, object]],
        ) -> str:
            if not internal_chunks and not web_results:
                return (
                    "I could not find enough internal or approved public evidence "
                    "to answer confidently."
                )

            prompt = self._build_mixed_prompt(
                question=question,
                explanation_level=explanation_level,
                internal_chunks=internal_chunks,
                web_results=web_results,
            )

            response = self.gemini_client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt
            )

            return response.text
    
    def _build_prompt(self,question: str,explanation_level: str,
                      retrieved_chunks: list[dict[str, int | float | str | None]],) -> str:
        prompt = (
          "You are FinanceBuddy, a financial education assistant. "
          "Answer the user's question using only the retrieved evidence below. "
          "Do not invent facts or rely on outside knowledge. "
          "If the evidence is incomplete or does not answer the question, say so clearly. "
          "Adjust the answer depth to the requested explanation level.\n\n"
          )
        prompt += f"Explanation level: {explanation_level}\n\n"


        for index, chunk in enumerate(retrieved_chunks, start=1):
            url_text = chunk["source_url"] or "N/A"
            prompt += (
                f"Source {index} (Title: {chunk['source_title']}, URL: {url_text}):\n"
                f"{chunk['text']}\n\n"
            )

        prompt += f"Question: {question}\n"
        prompt += ("Write a grounded answer. ""If the evidence is insufficient, explicitly state the limitation.")

        return prompt

    def _build_mixed_prompt(
        self,
        question: str,
        explanation_level: str,
        internal_chunks: list[dict[str, int | float | str | None]],
        web_results: list[dict[str, object]],
    ) -> str:
        prompt = (
          "You are FinanceBuddy, a financial education assistant. "
          "Answer the user's question using the supplied evidence only. "
          "Treat internal FinanceBuddy evidence as primary and approved public web evidence as secondary support. "
          "Do not invent facts or rely on outside knowledge. "
          "If public web evidence contributes materially, say that approved public sources were used. "
          "If the evidence remains incomplete, say so clearly.\n\n"
          )
        prompt += f"Explanation level: {explanation_level}\n\n"

        prompt += "Internal evidence:\n"
        if not internal_chunks:
            prompt += "None\n\n"
        else:
            for index, chunk in enumerate(internal_chunks, start=1):
                url_text = chunk["source_url"] or "N/A"
                prompt += (
                    f"Internal Source {index} (Title: {chunk['source_title']}, URL: {url_text}):\n"
                    f"{chunk['text']}\n\n"
                )

        prompt += "Approved public web evidence:\n"
        if not web_results:
            prompt += "None\n\n"
        else:
            for index, result in enumerate(web_results, start=1):
                prompt += (
                    f"Web Source {index} (Title: {result.get('title')}, URL: {result.get('url')}, "
                    f"Publisher: {result.get('publisher', 'Unknown')}):\n"
                    f"{result.get('snippet', '')}\n\n"
                )

        prompt += f"Question: {question}\n"
        prompt += (
            "Write a grounded answer. Prefer internal evidence when available and use public web evidence only to supplement it."
        )

        return prompt
