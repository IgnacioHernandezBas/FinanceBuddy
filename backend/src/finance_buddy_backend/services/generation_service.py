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