from urllib.parse import urlparse

import httpx

from finance_buddy_backend.core.config import settings


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

        if self.provider != "langsearch":
            raise ValueError(
                f"Unsupported web search provider configured: {self.provider}"
            )

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
