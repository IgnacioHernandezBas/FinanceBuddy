import re

def chunk_text(text: str, max_chunk_size: int = 1000, overlap: int = 0) -> list[str]:
  """
  Split by paragraphs first
  Accumulate into chunks up to a max character length
  Include overlap option to repeat some content between chunks for context
  """
  paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
  chunks: list[str] = []
  current_chunk = ""

  for paragraph in paragraphs:
      if len(current_chunk) + len(paragraph) + 1 <= max_chunk_size:
          current_chunk += paragraph + "\n"
      else:
          if current_chunk:
              chunks.append(current_chunk.strip())

          current_chunk = paragraph + "\n"

          if overlap > 0 and chunks:
              overlap_text = chunks[-1][-overlap:]
              current_chunk = overlap_text + current_chunk

  if current_chunk.strip():
      chunks.append(current_chunk.strip())

  return chunks