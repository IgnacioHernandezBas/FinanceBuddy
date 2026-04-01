import re

def normalize_text(text: str) -> str:
    """
    Normalize the input text by:
    - Normalizing line endings
    - Collapsing excessive blank lines
    - Trimming surrounding whitespace
    - Normalizing repeated spaces
    """
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.strip()
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    return normalized