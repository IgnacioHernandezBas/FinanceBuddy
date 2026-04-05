import re


class QueryNormalizationService:
    """Expand multilingual tax queries into retrieval-friendly Spanish phrasing."""

    _ENGLISH_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
        (re.compile(r"\bwhat is\b", re.IGNORECASE), "que es"),
        (re.compile(r"\bhow does\b", re.IGNORECASE), "como funciona"),
        (re.compile(r"\bhow do\b", re.IGNORECASE), "como"),
        (re.compile(r"\btax(es)?\b", re.IGNORECASE), "impuesto"),
        (re.compile(r"\bincome\b", re.IGNORECASE), "renta"),
        (re.compile(r"\breturn\b", re.IGNORECASE), "declaracion"),
        (re.compile(r"\bdeduction(s)?\b", re.IGNORECASE), "deduccion"),
        (re.compile(r"\bvat\b", re.IGNORECASE), "IVA impuesto sobre el valor anadido"),
    )

    _DOMAIN_EXPANSIONS: dict[str, str] = {
        "irpf": "IRPF impuesto sobre la renta de las personas fisicas impuesto sobre la renta renta",
        "iva": "IVA impuesto sobre el valor anadido vat impuesto indirecto",
        "aeat": "AEAT agencia tributaria agencia estatal de administracion tributaria",
        "hacienda": "hacienda agencia tributaria impuestos",
        "declaracion": "declaracion de la renta declaracion del impuesto sobre la renta",
    }

    def normalize_for_retrieval(self, query: str) -> str:
        """Keep the original query but append Spanish expansions for retrieval."""
        normalized_query = query.strip()
        if not normalized_query:
            return normalized_query

        lowered_query = normalized_query.lower()
        expansions: list[str] = []

        translated_query = normalized_query
        for pattern, replacement in self._ENGLISH_PATTERNS:
            translated_query = pattern.sub(replacement, translated_query)

        translated_query = self._normalize_spaces(translated_query)
        if translated_query.lower() != lowered_query:
            expansions.append(translated_query)

        for keyword, expansion in self._DOMAIN_EXPANSIONS.items():
            if keyword in lowered_query:
                expansions.append(expansion)

        if not expansions:
            return normalized_query

        unique_expansions: list[str] = []
        seen_values = {lowered_query}
        for expansion in expansions:
            cleaned_expansion = self._normalize_spaces(expansion)
            lowered_expansion = cleaned_expansion.lower()
            if cleaned_expansion and lowered_expansion not in seen_values:
                unique_expansions.append(cleaned_expansion)
                seen_values.add(lowered_expansion)

        if not unique_expansions:
            return normalized_query

        return f"{normalized_query}\n{'\n'.join(unique_expansions)}"

    def _normalize_spaces(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
