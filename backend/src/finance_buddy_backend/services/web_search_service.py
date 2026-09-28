from urllib.parse import urlparse

import httpx
from google import genai
from google.genai import types

from finance_buddy_backend.core.config import settings

GEMINI_SEARCH_TIMEOUT_MS = 60_000


class WebSearchService:
    def __init__(self) -> None:
        self.provider = settings.agent_web_search_provider
        self.api_key = (
            settings.agent_web_search_api_key
            or settings.langsearch_api_key
        )
        self.max_results = settings.agent_web_search_max_results

    def search(
        self,
        query: str,
        allowed_domains: list[str],
    ) -> list[dict[str, object]]:
        if not query.strip() or not allowed_domains:
            return []

        if self.provider == "gemini_google_search":
            return self._search_with_gemini(query, allowed_domains)

        if self.provider != "langsearch":
            raise ValueError(
                f"Unsupported web search provider configured: {self.provider}"
            )

        return self._search_with_langsearch(query, allowed_domains)

    def _search_with_gemini(
        self,
        query: str,
        allowed_domains: list[str],
    ) -> list[dict[str, object]]:
        client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=GEMINI_SEARCH_TIMEOUT_MS),
        )
        prompt = (
            f"{query}\n\n"
            f"Use only official sources from these domains: {', '.join(allowed_domains)}."
        )
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )

        candidates = response.candidates or []
        metadata = candidates[0].grounding_metadata if candidates else None
        if metadata is None:
            return []

        # Gemini API leaves web.domain empty and puts the domain in web.title; uri is a Google redirect.
        snippets_by_chunk: dict[int, list[str]] = {}
        for support in metadata.grounding_supports or []:
            text = support.segment.text if support.segment else None
            if not text:
                continue
            for index in support.grounding_chunk_indices or []:
                snippets_by_chunk.setdefault(index, []).append(text.strip())

        results: list[dict[str, object]] = []
        for index, chunk in enumerate(metadata.grounding_chunks or []):
            web = chunk.web
            if web is None or not web.uri or index not in snippets_by_chunk:
                continue

            domain = (web.domain or web.title or "").lower()
            if not self._is_allowed_domain(domain, allowed_domains):
                continue

            results.append(
                {
                    "title": web.title,
                    "url": web.uri,
                    "snippet": " ".join(snippets_by_chunk[index]),
                    "publisher": domain,
                }
            )

            if len(results) >= self.max_results:
                break

        return results

    def _search_with_langsearch(
        self,
        query: str,
        allowed_domains: list[str],
    ) -> list[dict[str, object]]:
        if not self.api_key:
            raise RuntimeError(
                "Web search is enabled but no agent web search API key is configured."
            )

        site_filters = " OR ".join(f"site:{domain}" for domain in allowed_domains)
        scoped_query = f"{query} ({site_filters})"

        response = httpx.post(
            "https://api.langsearch.com/v1/web-search",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "query": scoped_query,
                "count": self.max_results,
                "summary": True,
            },
            timeout=15.0,
        )
        payload = response.json()

        if response.status_code != 200:
            raise RuntimeError(
                f"LangSearch HTTP {response.status_code}: "
                f"{self._truncate_text(response.text)}"
            )

        if payload.get("code") != 200:
            raise RuntimeError(
                f"LangSearch API error {payload.get('code')}: "
                f"{payload.get('msg') or 'Unknown error'}"
            )

        results: list[dict[str, object]] = []
        data = payload.get("data") or {}
        web_pages = (data.get("webPages") or {}).get("value") or []
        for item in web_pages:
            url = item.get("url")
            if not isinstance(url, str) or not url:
                continue

            domain = self._extract_domain(url)
            if not self._is_allowed_domain(domain, allowed_domains):
                continue

            results.append(
                {
                    "title": item.get("name") or item.get("title"),
                    "url": url,
                    "snippet": item.get("summary") or item.get("snippet"),
                    "publisher": domain,
                }
            )

            if len(results) >= self.max_results:
                break

        return results

    def _extract_domain(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc.lower()

    def _is_allowed_domain(self, domain: str, allowed_domains: list[str]) -> bool:
        normalized_domain = domain.removeprefix("www.")
        return any(
            normalized_domain == allowed or normalized_domain.endswith(f".{allowed}")
            for allowed in allowed_domains
        )

    def _truncate_text(self, text: str, max_length: int = 300) -> str:
        stripped = text.strip()
        if len(stripped) <= max_length:
            return stripped
        return stripped[:max_length] + "..."
